#!/usr/bin/env python3
"""Localize D02 likelihood mismatch to forward states or observation arithmetic."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks

THRESHOLDS = (0.0, 1e-16, 1e-15, 1e-14, 1e-13)


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


def focus(actual, expected, trial_1based):
    index = trial_1based - 1
    actual = np.asarray(actual, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if actual.ndim == 1:
        return {
            "hgfx": float(actual[index]),
            "matlab": float(expected[index]),
            "abs_diff": float(abs(actual[index] - expected[index])),
        }
    diff = np.abs(actual[index] - expected[index])
    return {
        "hgfx": actual[index].tolist(),
        "matlab": expected[index].tolist(),
        "max_abs": float(np.nanmax(diff)),
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d02-likelihood-primitive-1":
        raise ValueError("Diagnostic protocol mismatch")
    if reference["case_id"] != "D02_fit":
        raise ValueError("Unexpected case")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("ehgf_binary")
    obs = resolve_config("unitsq_sgm")
    obs = replace(
        obs,
        parameters=(
            replace(
                obs.parameters[0],
                prior_variance=float(reference["obs_prior_variance"]),
            ),
        ),
    )
    problem = WorkflowFitProblem(
        y, u, prc.resolve_placeholders(u), obs.resolve_placeholders(u)
    )
    sample_free = _array(reference["sample_free"]).reshape(-1)
    full = problem.expand(sample_free)
    masks = build_trial_masks(y, u)
    ignored = tuple(int(i) for i in np.flatnonzero(masks.ignored))
    irregular = tuple(int(i) for i in np.flatnonzero(masks.irregular))
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
    pop = 0 if int(problem.obs.options.get("predorpost", 1)) == 1 else 2
    observation_x = states[:, 0, pop]
    ze = float(np.exp(full[problem.n_perceptual]))

    expected_states = _array(reference["inf_states"])
    expected_x = _array(reference["observation_x"]).reshape(-1)
    expected_logp = _array(reference["trial_log_likelihoods"]).reshape(-1)
    expected_yhat = _array(reference["yhat"]).reshape(-1)
    expected_res = _array(reference["res"]).reshape(-1)
    trial = int(reference["trial_focus_1based"])

    comparisons = {
        "sample_free": stats(sample_free, _array(reference["sample_free"]).reshape(-1)),
        "full_transformed": stats(full, _array(reference["full_transformed"]).reshape(-1)),
        "inf_states": stats(states, expected_states),
        "observation_x": stats(observation_x, expected_x),
        "ze": stats([ze], [float(reference["ze"])]),
        "trial_log_likelihoods": stats(logp, expected_logp),
        "yhat": stats(yhat, expected_yhat),
        "res": stats(res, expected_res),
    }

    state_max = comparisons["inf_states"].get("max_abs", float("nan"))
    logp_max = comparisons["trial_log_likelihoods"].get("max_abs", float("nan"))
    if np.isfinite(state_max) and state_max > 0.0:
        classification = "FORWARD_NUMERICAL_DIVERGENCE"
    elif np.isfinite(logp_max) and logp_max > 0.0:
        classification = "OBSERVATION_NUMERICAL_DIVERGENCE"
    else:
        classification = "NO_PRIMITIVE_DIVERGENCE_AT_SELECTED_SAMPLE"

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "sample": reference["sample"],
        "classification": classification,
        "note": (
            "Diagnostic only. This exact Ridders sample is upstream of optimizer path drift; "
            "no M18 threshold or acceptance criterion is changed."
        ),
        "comparisons": comparisons,
        "focus_trial_1based": trial,
        "focus": {
            "observation_x": focus(observation_x, expected_x, trial),
            "trial_log_likelihood": focus(logp, expected_logp, trial),
            "yhat": focus(yhat, expected_yhat, trial),
            "res": focus(res, expected_res, trial),
            "inf_states": focus(states, expected_states, trial),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")

    print(
        json.dumps(
            {
                "classification": classification,
                "inf_states_max_abs": comparisons["inf_states"].get("max_abs"),
                "observation_x_max_abs": comparisons["observation_x"].get("max_abs"),
                "ze_max_abs": comparisons["ze"].get("max_abs"),
                "logp_max_abs": comparisons["trial_log_likelihoods"].get("max_abs"),
                "focus_trial": trial,
                "focus_logp_abs_diff": result["focus"]["trial_log_likelihood"]["abs_diff"],
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
