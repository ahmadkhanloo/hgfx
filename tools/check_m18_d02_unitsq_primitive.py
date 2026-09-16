#!/usr/bin/env python3
"""Localize residual D02 mismatch inside the unit-square likelihood formula."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks
from hgfx.math.matlab_exp import matlab_exp_scalar

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


def unitsq_primitives(x, y, ze):
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    z = np.float64(ze)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        logx_raw = np.log(x)
        log1pxm1 = np.log1p(x - 1.0)
        use_log1pxm1 = (1.0 - x) < 1e-4
        logx_used = logx_raw.copy()
        logx_used[use_log1pxm1] = log1pxm1[use_log1pxm1]

        log1mx_raw = np.log(1.0 - x)
        log1pmx = np.log1p(-x)
        use_log1pmx = x < 1e-4
        log1mx_used = log1mx_raw.copy()
        log1mx_used[use_log1pmx] = log1pmx[use_log1pmx]

        pow1mx = (1.0 - x) ** z
        powx = x**z
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


def focus_stat(actual, expected, index):
    actual = np.asarray(actual, dtype=np.float64).reshape(-1)
    expected = np.asarray(expected, dtype=np.float64).reshape(-1)
    return {
        "hgfx": float(actual[index]),
        "matlab": float(expected[index]),
        "abs_diff": float(abs(actual[index] - expected[index])),
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d02-unitsq-primitive-1":
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
    actual_x = states[:, 0, pop]
    actual_ze = matlab_exp_scalar(float(full[problem.n_perceptual]))

    regular = ~masks.irregular
    actual_primitives = unitsq_primitives(actual_x[regular], y[regular], actual_ze)

    expected_states = _array(reference["inf_states"])
    expected_x = _array(reference["observation_x"]).reshape(-1)
    expected_ze = float(reference["ze"])
    expected_logp = _array(reference["trial_log_likelihoods"]).reshape(-1)
    expected_primitives = {
        key: _array(value).reshape(-1)
        for key, value in reference["primitives"].items()
    }
    expected_regular_y = _array(reference["regular_y"]).reshape(-1)
    replay_primitives = unitsq_primitives(
        expected_x[regular], expected_regular_y, expected_ze
    )

    comparisons = {
        "sample_free": stats(sample_free, _array(reference["sample_free"]).reshape(-1)),
        "full_transformed": stats(full, _array(reference["full_transformed"]).reshape(-1)),
        "inf_states": stats(states, expected_states),
        "observation_x": stats(actual_x, expected_x),
        "ze": stats([actual_ze], [expected_ze]),
        "trial_log_likelihoods": stats(logp, expected_logp),
        "actual_primitives": {},
        "exact_matlab_state_replay": {},
    }
    for key, expected in expected_primitives.items():
        comparisons["actual_primitives"][key] = stats(actual_primitives[key], expected)
        comparisons["exact_matlab_state_replay"][key] = stats(
            replay_primitives[key], expected
        )

    state_max = comparisons["inf_states"].get("max_abs", float("nan"))
    replay_logp_max = comparisons["exact_matlab_state_replay"]["logp_formula"].get(
        "max_abs", float("nan")
    )
    call_logp_max = comparisons["trial_log_likelihoods"].get("max_abs", float("nan"))
    state_diff = np.isfinite(state_max) and state_max > 0.0
    observation_diff = np.isfinite(replay_logp_max) and replay_logp_max > 0.0

    if state_diff and observation_diff:
        classification = "FORWARD_AND_OBSERVATION_NUMERICAL_DIVERGENCE"
    elif state_diff:
        classification = "FORWARD_NUMERICAL_DIVERGENCE"
    elif observation_diff:
        classification = "OBSERVATION_PRIMITIVE_DIVERGENCE"
    elif np.isfinite(call_logp_max) and call_logp_max > 0.0:
        classification = "OBSERVATION_CALL_DIVERGENCE"
    else:
        classification = "NO_RESIDUAL_PRIMITIVE_DIVERGENCE"

    trial = int(reference["trial_focus_1based"])
    if not regular[trial - 1]:
        raise ValueError("Focused D02 trial unexpectedly irregular")
    regular_indices = np.flatnonzero(regular)
    regular_index = int(np.flatnonzero(regular_indices == trial - 1)[0])
    focus = {
        "observation_x": focus_stat(actual_x, expected_x, trial - 1),
        "trial_log_likelihood": focus_stat(logp, expected_logp, trial - 1),
        "primitives": {},
        "exact_matlab_state_replay": {},
    }
    for key, expected in expected_primitives.items():
        focus["primitives"][key] = focus_stat(
            actual_primitives[key], expected, regular_index
        )
        focus["exact_matlab_state_replay"][key] = focus_stat(
            replay_primitives[key], expected, regular_index
        )

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "sample": reference["sample"],
        "classification": classification,
        "note": (
            "Diagnostic only. The sample/trial was selected from the unchanged "
            "post-fdlibm exact-coordinate decomposition; no acceptance criterion changed."
        ),
        "comparisons": comparisons,
        "focus_trial_1based": trial,
        "focus": focus,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")

    summary = {
        "classification": classification,
        "inf_states_max_abs": state_max,
        "observation_x_max_abs": comparisons["observation_x"].get("max_abs"),
        "ze_max_abs": comparisons["ze"].get("max_abs"),
        "logp_max_abs": call_logp_max,
        "replay_logp_max_abs": replay_logp_max,
        "focus_trial": trial,
        "focus_logp_abs_diff": focus["trial_log_likelihood"]["abs_diff"],
    }
    for key in (
        "logx_raw", "log1pxm1", "logx_used", "log1mx_raw", "log1pmx",
        "log1mx_used", "pow1mx", "powx", "denom", "logdenom",
        "term1", "term2", "logp_formula",
    ):
        value = comparisons["exact_matlab_state_replay"][key].get("max_abs")
        if value is not None and np.isfinite(value) and value > 0.0:
            summary["first_replay_primitive_with_difference"] = key
            summary["first_replay_primitive_max_abs"] = value
            break
    print(json.dumps(summary), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
