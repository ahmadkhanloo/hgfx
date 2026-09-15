#!/usr/bin/env python3
"""Localize the first D02 optimizer-source objective residual inside likelihood evaluation."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks
from hgfx.math.matlab_exp import matlab_exp_scalar
from hgfx.responses.unitsq_sigmoid import _core as unitsq_core, _scalar_log

PROTOCOL = "m18-d02-source-likelihood-probe-1"
THRESHOLDS = (0.0, 1e-16, 1e-15, 1e-14, 1e-13)


def scalar(value) -> np.float64:
    return np.float64(_array(value).reshape(-1)[0])


def stats(actual, expected):
    actual = np.asarray(actual, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if actual.shape != expected.shape:
        return {"shape_mismatch": [list(actual.shape), list(expected.shape)]}
    diff = np.abs(actual - expected)
    both_nan = np.isnan(actual) & np.isnan(expected)
    diff[both_nan] = 0.0
    finite = np.isfinite(diff)
    out = {"max_abs": float(np.max(diff[finite])) if np.any(finite) else float("nan")}
    for threshold in THRESHOLDS:
        mask = finite & (diff > threshold)
        key = f"first_gt_{threshold:.0e}"
        if np.any(mask):
            idx = tuple(int(i) for i in np.argwhere(mask)[0])
            out[key] = {
                "index": list(idx),
                "hgfx": float(actual[idx]),
                "matlab": float(expected[idx]),
                "abs_diff": float(diff[idx]),
            }
        else:
            out[key] = None
    return out


def scalar_cmp(actual, expected):
    a = np.float64(actual)
    e = np.float64(expected)
    return {"hgfx": float(a), "matlab": float(e), "abs_diff": float(abs(a-e)), "exact": bool(a == e)}


def scalar_loop_sum(values) -> np.float64:
    total = np.float64(0.0)
    for value in np.asarray(values, dtype=np.float64).reshape(-1):
        total = np.float64(total + np.float64(value))
    return total


def production_primitives(x, y, ze):
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    z = np.float64(ze)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        logx_raw = _scalar_log(x)
        log1pxm1 = np.log1p(x - np.float64(1.0))
        use_log1pxm1 = (np.float64(1.0) - x) < np.float64(1e-4)
        logx_used = logx_raw.copy()
        logx_used[use_log1pxm1] = log1pxm1[use_log1pxm1]

        log1mx_raw = _scalar_log(np.float64(1.0) - x)
        log1pmx = np.log1p(-x)
        use_log1pmx = x < np.float64(1e-4)
        log1mx_used = log1mx_raw.copy()
        log1mx_used[use_log1pmx] = log1pmx[use_log1pmx]

        pow1mx = (np.float64(1.0) - x) ** z
        powx = x ** z
        denom = pow1mx + powx
        logdenom = np.log(denom)
        term1 = y * z * (logx_used - log1mx_used)
        term2 = z * log1mx_used
        logp_formula = term1 + term2 - logdenom
    return {
        "logx_raw": logx_raw,
        "log1pxm1": log1pxm1,
        "use_log1pxm1": use_log1pxm1.astype(np.float64),
        "logx_used": logx_used,
        "log1mx_raw": log1mx_raw,
        "log1pmx": log1pmx,
        "use_log1pmx": use_log1pmx.astype(np.float64),
        "log1mx_used": log1mx_used,
        "pow1mx": pow1mx,
        "powx": powx,
        "denom": denom,
        "logdenom": logdenom,
        "term1": term1,
        "term2": term2,
        "logp_formula": logp_formula,
    }


def make_problem(reference):
    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("ehgf_binary")
    obs = resolve_config("unitsq_sgm")
    obs = replace(obs, parameters=(replace(obs.parameters[0], prior_variance=float(reference["obs_prior_variance"])),))
    prc = prc.resolve_placeholders(u)
    obs = obs.resolve_placeholders(u)
    return WorkflowFitProblem(y, u, prc, obs), u, y


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference.get("protocol") != PROTOCOL:
        raise ValueError("Diagnostic protocol mismatch")
    if reference.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference.get("case_id") != "D02_fit" or int(reference.get("seed")) != 123456789:
        raise ValueError("Frozen D02 contract mismatch")
    if int(reference.get("source_trace_row_1based")) != 7:
        raise ValueError("Frozen source row mismatch")
    if int(reference.get("component_free_index_1based")) != 1:
        raise ValueError("Frozen free component mismatch")
    if int(reference.get("component_full_index_1based")) != 13:
        raise ValueError("Frozen full transformed component mismatch")
    if int(reference.get("ridders_step_1based")) != 2 or reference.get("side") != "plus":
        raise ValueError("Frozen Ridders sample mismatch")
    expected_h = np.float64(1.0) / np.float64(1.2)
    if scalar(reference["h"]) != expected_h:
        raise ValueError("Frozen Ridders h mismatch")

    problem, u, y = make_problem(reference)
    sample_free = _array(reference["sample_free"]).reshape(-1)
    full = problem.expand(sample_free)
    masks = build_trial_masks(y, u)
    ignored = tuple(int(i) for i in np.flatnonzero(masks.ignored))
    irregular = tuple(int(i) for i in np.flatnonzero(masks.irregular))
    regular = ~masks.irregular

    _, states = problem.forward(
        u,
        full[: problem.n_perceptual],
        transformed=True,
        irregular_intervals=bool(problem.prc.options.get("irregular_intervals", False)),
        ignored_trials=ignored,
    )
    logp, yhat, res = problem.observation(
        y,
        states,
        full[problem.n_perceptual :],
        irregular_trials=irregular,
    )
    evaluated = problem.evaluate_full(full)

    pop = 0 if int(problem.obs.options.get("predorpost", 1)) == 1 else 2
    actual_x = states[:, 0, pop]
    actual_ze = matlab_exp_scalar(float(full[problem.n_perceptual]))

    expected_states = _array(reference["inf_states"])
    expected_x = _array(reference["observation_x"]).reshape(-1)
    expected_ze = scalar(reference["ze"])
    expected_logp = _array(reference["trial_log_likelihoods"]).reshape(-1)
    expected_regular_y = _array(reference["regular_y"]).reshape(-1)
    expected_primitives = {key: _array(value).reshape(-1) for key, value in reference["primitives"].items()}

    actual_primitives = production_primitives(actual_x[regular], y[regular], actual_ze)
    replay_primitives = production_primitives(expected_x[regular], expected_regular_y, expected_ze)
    replay_logp, _, _ = unitsq_core(y, expected_x, expected_ze, irregular_trials=irregular)

    comparisons = {
        "sample_free": stats(sample_free, _array(reference["sample_free"]).reshape(-1)),
        "full_transformed": stats(full, _array(reference["full_transformed"]).reshape(-1)),
        "inf_states": stats(states, expected_states),
        "observation_x": stats(actual_x, expected_x),
        "ze": stats([actual_ze], [expected_ze]),
        "trial_log_likelihoods": stats(logp, expected_logp),
        "exact_matlab_state_observation_replay": stats(replay_logp, expected_logp),
        "primitives": {},
        "exact_matlab_state_primitives": {},
    }
    for key, expected in expected_primitives.items():
        comparisons["primitives"][key] = stats(actual_primitives[key], expected)
        comparisons["exact_matlab_state_primitives"][key] = stats(replay_primitives[key], expected)

    reductions = {
        "workflow_log_likelihood": scalar_cmp(evaluated.log_likelihood, scalar(reference["log_likelihood_sum"])),
        "actual_trial_np_sum": scalar_cmp(np.sum(logp[regular], dtype=np.float64), scalar(reference["log_likelihood_sum"])),
        "actual_trial_scalar_loop": scalar_cmp(scalar_loop_sum(logp[regular]), scalar(reference["log_likelihood_scalar_loop"])),
        "matlab_trials_python_np_sum": scalar_cmp(np.sum(expected_logp[regular], dtype=np.float64), scalar(reference["log_likelihood_sum"])),
        "matlab_trials_python_scalar_loop": scalar_cmp(scalar_loop_sum(expected_logp[regular]), scalar(reference["log_likelihood_scalar_loop"])),
        "matlab_sum_vs_scalar_loop": scalar_cmp(scalar(reference["log_likelihood_sum"]), scalar(reference["log_likelihood_scalar_loop"])),
    }

    state_max = comparisons["inf_states"].get("max_abs", math.nan)
    trial_max = comparisons["trial_log_likelihoods"].get("max_abs", math.nan)
    workflow_exact = reductions["workflow_log_likelihood"]["exact"]
    if np.isfinite(state_max) and state_max > 0.0:
        classification = "FORWARD_NUMERICAL_DIVERGENCE"
    elif np.isfinite(trial_max) and trial_max > 0.0:
        classification = "OBSERVATION_PRIMITIVE_DIVERGENCE"
    elif not workflow_exact:
        classification = "LIKELIHOOD_REDUCTION_DIVERGENCE"
    else:
        classification = "NO_LIKELIHOOD_DIVERGENCE_AT_SELECTED_SAMPLE"

    first_trial = comparisons["trial_log_likelihoods"].get("first_gt_0e+00")
    focus = None
    if first_trial is not None:
        trial_zero = int(first_trial["index"][0])
        regular_indices = np.flatnonzero(regular)
        positions = np.flatnonzero(regular_indices == trial_zero)
        if positions.size:
            regular_index = int(positions[0])
            focus = {
                "trial_zero_based": trial_zero,
                "trial_one_based": trial_zero + 1,
                "trial_log_likelihood": first_trial,
                "primitives": {
                    key: {
                        "hgfx": float(actual_primitives[key][regular_index]),
                        "matlab": float(expected[regular_index]),
                        "abs_diff": float(abs(actual_primitives[key][regular_index] - expected[regular_index])),
                    }
                    for key, expected in expected_primitives.items()
                },
                "exact_matlab_state_primitives": {
                    key: {
                        "hgfx": float(replay_primitives[key][regular_index]),
                        "matlab": float(expected[regular_index]),
                        "abs_diff": float(abs(replay_primitives[key][regular_index] - expected[regular_index])),
                    }
                    for key, expected in expected_primitives.items()
                },
            }

    first_replay_primitive = None
    for key in ("logx_raw", "log1pxm1", "logx_used", "log1mx_raw", "log1pmx", "log1mx_used", "pow1mx", "powx", "denom", "logdenom", "term1", "term2", "logp_formula"):
        value = comparisons["exact_matlab_state_primitives"][key].get("max_abs")
        if value is not None and np.isfinite(value) and value > 0.0:
            first_replay_primitive = {"name": key, "max_abs": value, "detail": comparisons["exact_matlab_state_primitives"][key].get("first_gt_0e+00")}
            break

    result = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "classification": classification,
        "frozen_sample": {
            "source_trace_row_zero_based": 6,
            "component_free_index_zero_based": 0,
            "component_full_index_zero_based": 12,
            "ridders_step_zero_based": 1,
            "side": "plus",
            "h": float(expected_h),
        },
        "comparisons": comparisons,
        "reductions": reductions,
        "first_differing_trial": focus,
        "first_exact_state_replay_primitive_difference": first_replay_primitive,
        "decision_note": "Diagnostic only; no acceptance rule, tolerance, seed, data, model, start, or optimizer is changed and D02 remains BLOCKED.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")
    print(json.dumps({"classification": classification, "workflow_log_likelihood": reductions["workflow_log_likelihood"], "first_differing_trial": None if focus is None else focus["trial_one_based"], "first_replay_primitive": first_replay_primitive}), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
