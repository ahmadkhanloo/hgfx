#!/usr/bin/env python3
"""Classify exact-state D02 Ridders objective samples at the frozen source row."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config

PROTOCOL = "m18-d02-optimizer-source-probe-1"


def scalar(value) -> np.float64:
    return np.float64(_array(value).reshape(-1)[0])


def scalar_cmp(actual, expected):
    a = np.float64(actual)
    e = np.float64(expected)
    return {"hgfx": float(a), "matlab": float(e), "abs_diff": float(abs(a-e)), "exact": bool(a == e)}


def make_problem(reference):
    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("ehgf_binary")
    obs = resolve_config("unitsq_sgm")
    obs = replace(obs, parameters=(replace(obs.parameters[0], prior_variance=float(reference["obs_prior_variance"])),))
    prc = prc.resolve_placeholders(u)
    obs = obs.resolve_placeholders(u)
    return WorkflowFitProblem(y, u, prc, obs)


def decompose(problem, free):
    out = problem.evaluate_full(problem.expand(free))
    return {
        "log_likelihood": np.float64(out.log_likelihood),
        "perceptual_prior": np.float64(out.perceptual_prior.total),
        "observation_prior": np.float64(out.observation_prior.total),
        "neg_log_joint": np.float64(out.neg_log_joint),
    }


def compare_decomp(actual, expected):
    return {key: scalar_cmp(actual[key], scalar(expected[key])) for key in actual}


def ridders_replay(hvals, fplus, fminus):
    n = len(hvals)
    p = np.full((n, n), np.nan, dtype=np.float64)
    result = np.float64(np.nan)
    error = np.float64(np.finfo(np.float64).max)
    diagonal = np.full(n, np.nan, dtype=np.float64)
    for i in range(n):
        h = np.float64(hvals[i])
        p[i, 0] = np.float64((np.float64(fplus[i]) - np.float64(fminus[i])) / (np.float64(2.0) * h))
        if i > 0:
            divsq = np.float64(1.2) ** 2
            t = np.float64(divsq)
            for j in range(1, i + 1):
                p[i, j] = np.float64((t * p[i, j - 1] - p[i - 1, j - 1]) / (t - np.float64(1.0)))
                t = np.float64(t * divsq)
                currerr = np.float64(max(abs(p[i, j]-p[i, j-1]), abs(p[i, j]-p[i-1, j-1])))
                if currerr < error:
                    error = currerr
                    result = p[i, j]
        diagonal[i] = p[i, i]
    return result, error, diagonal


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference.get("protocol") != PROTOCOL:
        raise ValueError("Diagnostic protocol mismatch")
    if reference.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference.get("case_id") != "D02_fit" or int(reference.get("seed")) != 123456789:
        raise ValueError("Frozen D02 contract mismatch")
    if int(reference.get("source_trace_row_1based")) != 7:
        raise ValueError("Frozen D02 source row mismatch")

    problem = make_problem(reference)
    source_x = _array(reference["source_x"]).reshape(-1)
    if source_x.size != len(problem.free_indices):
        raise ValueError("Free-parameter shape mismatch")

    component_results = []
    first_objective_difference = None
    all_exact_samples = True
    all_matlab_replays_exact = True
    all_hgfx_replays_exact = True

    for component_zero, probe in enumerate(reference["probes"]):
        component_one = int(probe["component_free_index_1based"])
        if component_one != component_zero + 1:
            raise ValueError("Probe component ordering mismatch")
        hvals = _array(probe["h"]).reshape(-1)
        xplus = _array(probe["x_plus"]).reshape(-1)
        xminus = _array(probe["x_minus"]).reshape(-1)
        matlab_fplus = _array(probe["f_plus"]).reshape(-1)
        matlab_fminus = _array(probe["f_minus"]).reshape(-1)
        hgfx_fplus = []
        hgfx_fminus = []
        samples = []
        for i in range(len(hvals)):
            plus = source_x.copy(); plus[component_zero] = xplus[i]
            minus = source_x.copy(); minus[component_zero] = xminus[i]
            plus_d = decompose(problem, plus)
            minus_d = decompose(problem, minus)
            plus_cmp = scalar_cmp(plus_d["neg_log_joint"], matlab_fplus[i])
            minus_cmp = scalar_cmp(minus_d["neg_log_joint"], matlab_fminus[i])
            plus_parts = compare_decomp(plus_d, probe["plus_decomposition"][i])
            minus_parts = compare_decomp(minus_d, probe["minus_decomposition"][i])
            hgfx_fplus.append(plus_d["neg_log_joint"])
            hgfx_fminus.append(minus_d["neg_log_joint"])
            samples.append({
                "step_zero_based": i,
                "h": float(hvals[i]),
                "plus": {"objective": plus_cmp, "decomposition": plus_parts},
                "minus": {"objective": minus_cmp, "decomposition": minus_parts},
            })
            for side, cmp, parts in (("plus", plus_cmp, plus_parts), ("minus", minus_cmp, minus_parts)):
                if not cmp["exact"]:
                    all_exact_samples = False
                    if first_objective_difference is None:
                        first_component = next((name for name, value in parts.items() if not value["exact"]), None)
                        first_objective_difference = {
                            "component_free_index_zero_based": component_zero,
                            "step_zero_based": i,
                            "side": side,
                            "h": float(hvals[i]),
                            "objective_abs_diff": cmp["abs_diff"],
                            "first_differing_decomposition": first_component,
                            "decomposition": parts,
                        }

        matlab_deriv, matlab_err, matlab_diag = ridders_replay(hvals, matlab_fplus, matlab_fminus)
        hgfx_deriv, hgfx_err, hgfx_diag = ridders_replay(hvals, hgfx_fplus, hgfx_fminus)
        expected_deriv = scalar(probe["selected_derivative"])
        expected_err = scalar(probe["selected_error"])
        matlab_deriv_cmp = scalar_cmp(matlab_deriv, expected_deriv)
        matlab_err_cmp = scalar_cmp(matlab_err, expected_err)
        hgfx_deriv_cmp = scalar_cmp(hgfx_deriv, expected_deriv)
        hgfx_err_cmp = scalar_cmp(hgfx_err, expected_err)
        all_matlab_replays_exact &= matlab_deriv_cmp["exact"] and matlab_err_cmp["exact"]
        all_hgfx_replays_exact &= hgfx_deriv_cmp["exact"] and hgfx_err_cmp["exact"]
        exported_diag = _array(probe["diagonal"]).reshape(-1)
        component_results.append({
            "component_free_index_zero_based": component_zero,
            "component_full_index_zero_based": int(_array(reference["free_full_indices_1based"]).reshape(-1)[component_zero]) - 1,
            "stop_step": int(scalar(probe["stop_step"])),
            "matlab_samples_python_replay": {"derivative": matlab_deriv_cmp, "error": matlab_err_cmp, "diagonal_max_abs": float(np.max(np.abs(matlab_diag-exported_diag)))},
            "hgfx_samples_python_replay": {"derivative": hgfx_deriv_cmp, "error": hgfx_err_cmp, "diagonal_max_abs": float(np.max(np.abs(hgfx_diag-exported_diag)))},
            "samples": samples,
        })

    if not all_exact_samples:
        classification = "OBJECTIVE_SAMPLE_DIVERGENCE"
    elif not all_matlab_replays_exact:
        classification = "RIDDERS_EXTRAPOLATION_ARITHMETIC_DIVERGENCE"
    elif not all_hgfx_replays_exact:
        classification = "RIDDERS_REPLAY_UNEXPLAINED_DIVERGENCE"
    else:
        classification = "NO_RIDDERS_DIVERGENCE_AT_SOURCE"

    result = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "classification": classification,
        "source_trace_row_zero_based": 6,
        "source_objective_replay": scalar_cmp(problem.evaluate_free(source_x), scalar(reference["source_val"])),
        "first_objective_difference": first_objective_difference,
        "components": component_results,
        "decision_note": "Diagnostic only; no acceptance rule or tolerance is changed and D02 remains BLOCKED.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"classification": classification, "first_objective_difference": first_objective_difference}), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
