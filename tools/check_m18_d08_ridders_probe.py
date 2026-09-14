#!/usr/bin/env python3
"""Decompose the first D08 Ridders gradient mismatch into objective components."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config


def scalar(value) -> np.float64:
    return np.float64(_array(value).reshape(-1)[0])


def scalar_cmp(actual, expected):
    a = np.float64(actual)
    e = np.float64(expected)
    return {
        "hgfx": float(a),
        "matlab": float(e),
        "abs_diff": float(abs(a - e)),
        "exact": bool(a == e),
    }


def evaluate_decomposition(problem: WorkflowFitProblem, free: np.ndarray):
    out = problem.evaluate_full(problem.expand(free))
    return {
        "log_likelihood": np.float64(out.log_likelihood),
        "perceptual_prior": np.float64(out.perceptual_prior.total),
        "observation_prior": np.float64(out.observation_prior.total),
        "neg_log_joint": np.float64(out.neg_log_joint),
    }


def compare_decomposition(actual, expected):
    return {
        key: scalar_cmp(actual[key], scalar(expected[key]))
        for key in ("log_likelihood", "perceptual_prior", "observation_prior", "neg_log_joint")
    }


def ridders_replay(hvals, fplus, fminus):
    n = len(hvals)
    p = np.full((n, n), np.nan, dtype=np.float64)
    result = np.float64(np.nan)
    error = np.float64(np.finfo(np.float64).max)
    diagonal = np.full(n, np.nan, dtype=np.float64)
    for i in range(n):
        h = np.float64(hvals[i])
        p[i, 0] = np.float64(
            (np.float64(fplus[i]) - np.float64(fminus[i])) / (np.float64(2.0) * h)
        )
        if i > 0:
            divsq = np.float64(1.2) ** 2
            t = np.float64(divsq)
            for j in range(1, i + 1):
                p[i, j] = np.float64(
                    (t * p[i, j - 1] - p[i - 1, j - 1]) / (t - np.float64(1.0))
                )
                t = np.float64(t * divsq)
                currerr = np.float64(
                    max(
                        abs(p[i, j] - p[i, j - 1]),
                        abs(p[i, j] - p[i - 1, j - 1]),
                    )
                )
                if currerr < error:
                    error = currerr
                    result = p[i, j]
        diagonal[i] = p[i, i]
    return result, error, diagonal


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d08-ridders-probe-1":
        raise ValueError("Diagnostic protocol mismatch")
    if reference["case_id"] != "D08_fit":
        raise ValueError("Unexpected case")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("uhgf").resolve_placeholders(u)
    obs = resolve_config("gaussian_obs").resolve_placeholders(u)
    problem = WorkflowFitProblem(y, u, prc, obs)

    source_x = _array(reference["source_x"]).reshape(-1)
    component = int(reference["component_free_index_1based"]) - 1
    probe = reference["probe"]
    hvals = _array(probe["h"]).reshape(-1)
    xplus = _array(probe["x_plus"]).reshape(-1)
    xminus = _array(probe["x_minus"]).reshape(-1)
    matlab_fplus = _array(probe["f_plus"]).reshape(-1)
    matlab_fminus = _array(probe["f_minus"]).reshape(-1)

    sample_records = []
    first_objective_difference = None
    max_objective_difference = {"abs_diff": -1.0}
    hgfx_fplus = []
    hgfx_fminus = []

    for i in range(len(hvals)):
        plus = source_x.copy()
        minus = source_x.copy()
        plus[component] = xplus[i]
        minus[component] = xminus[i]
        plus_decomp = evaluate_decomposition(problem, plus)
        minus_decomp = evaluate_decomposition(problem, minus)
        plus_cmp = compare_decomposition(plus_decomp, probe["plus_decomposition"][i])
        minus_cmp = compare_decomposition(minus_decomp, probe["minus_decomposition"][i])
        fp = plus_decomp["neg_log_joint"]
        fm = minus_decomp["neg_log_joint"]
        hgfx_fplus.append(fp)
        hgfx_fminus.append(fm)
        fp_cmp = scalar_cmp(fp, matlab_fplus[i])
        fm_cmp = scalar_cmp(fm, matlab_fminus[i])
        record = {
            "step_zero_based": i,
            "h": float(hvals[i]),
            "plus": {"objective": fp_cmp, "decomposition": plus_cmp},
            "minus": {"objective": fm_cmp, "decomposition": minus_cmp},
        }
        sample_records.append(record)
        for side, cmp in (("plus", fp_cmp), ("minus", fm_cmp)):
            if not cmp["exact"] and first_objective_difference is None:
                components = plus_cmp if side == "plus" else minus_cmp
                first_component = next(
                    (name for name, value in components.items() if not value["exact"]), None
                )
                first_objective_difference = {
                    "step_zero_based": i,
                    "side": side,
                    "h": float(hvals[i]),
                    "abs_diff": cmp["abs_diff"],
                    "first_differing_component": first_component,
                    "components": components,
                }
            if cmp["abs_diff"] > max_objective_difference["abs_diff"]:
                max_objective_difference = {
                    "step_zero_based": i,
                    "side": side,
                    "h": float(hvals[i]),
                    "abs_diff": cmp["abs_diff"],
                }

    matlab_replay_derivative, matlab_replay_error, matlab_replay_diagonal = ridders_replay(
        hvals, matlab_fplus, matlab_fminus
    )
    hgfx_replay_derivative, hgfx_replay_error, hgfx_replay_diagonal = ridders_replay(
        hvals, hgfx_fplus, hgfx_fminus
    )
    expected_derivative = scalar(probe["selected_derivative"])
    expected_error = scalar(probe["selected_error"])

    matlab_replay_cmp = scalar_cmp(matlab_replay_derivative, expected_derivative)
    hgfx_replay_cmp = scalar_cmp(hgfx_replay_derivative, expected_derivative)

    if first_objective_difference is not None:
        classification = "OBJECTIVE_SAMPLE_DIVERGENCE"
    elif not matlab_replay_cmp["exact"]:
        classification = "RIDDERS_EXTRAPOLATION_ARITHMETIC_DIVERGENCE"
    elif not hgfx_replay_cmp["exact"]:
        classification = "RIDDERS_REPLAY_UNEXPLAINED_DIVERGENCE"
    else:
        classification = "NO_RIDDERS_DIVERGENCE"

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D08_fit",
        "classification": classification,
        "source_trace_row_zero_based": int(reference["source_trace_row_1based"]) - 1,
        "component_free_index_zero_based": component,
        "component_full_index_zero_based": int(
            _array(reference["free_full_indices_1based"]).reshape(-1)[component]
        ) - 1,
        "stop_step": int(scalar(probe["stop_step"])),
        "first_objective_difference": first_objective_difference,
        "max_objective_difference": max_objective_difference,
        "selected_derivative": {
            "matlab_reference": float(expected_derivative),
            "matlab_samples_python_replay": matlab_replay_cmp,
            "hgfx_samples_python_replay": hgfx_replay_cmp,
        },
        "selected_error": {
            "matlab_reference": float(expected_error),
            "matlab_samples_python_replay": scalar_cmp(matlab_replay_error, expected_error),
            "hgfx_samples_python_replay": scalar_cmp(hgfx_replay_error, expected_error),
        },
        "diagonal_replay": {
            "matlab_samples": {
                "max_abs_vs_exported": float(
                    np.max(np.abs(matlab_replay_diagonal - _array(probe["diagonal"]).reshape(-1)))
                )
            },
            "hgfx_samples_max_abs_vs_matlab_exported": float(
                np.max(np.abs(hgfx_replay_diagonal - _array(probe["diagonal"]).reshape(-1)))
            ),
        },
        "samples": sample_records,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
