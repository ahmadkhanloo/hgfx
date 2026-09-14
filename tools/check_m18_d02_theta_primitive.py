#!/usr/bin/env python3
"""Localize D02 top-level theta/predicted-precision binary64 divergence."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks
from hgfx.math.matlab_exp import matlab_exp_scalar, matlab_theta_exp_scalar

ORDER = (
    "logsa0_last",
    "sa0_last",
    "pi_prev_last",
    "logtheta",
    "theta",
    "t_first",
    "reciprocal_pi_prev",
    "t_theta",
    "inner",
    "pihat_first",
    "sahat_first",
    "traj_sahat_first",
    "inf_sahat_first",
)


def scalar(value) -> np.float64:
    return np.float64(_array(value).reshape(-1)[0])


def compare(actual, expected):
    a = np.float64(actual)
    e = np.float64(expected)
    return {
        "hgfx": float(a),
        "matlab": float(e),
        "abs_diff": float(abs(a - e)),
        "exact": bool(a == e),
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d02-theta-primitive-1":
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

    expected_full = _array(reference["full_transformed"]).reshape(-1)
    if not np.array_equal(full, expected_full, equal_nan=True):
        raise ValueError("Expanded transformed vector does not match MATLAB payload")

    l = int(reference["n_levels"])
    if l != 3:
        raise ValueError(f"Unexpected D02 level count: {l}")

    logsa0_last = np.float64(full[2 * l - 1])
    sa0_last = matlab_exp_scalar(logsa0_last)
    pi_prev_last = np.float64(1.0) / sa0_last
    logtheta = np.float64(full[5 * l - 2])
    theta = matlab_theta_exp_scalar(logtheta)

    t_first = np.float64(1.0)
    reciprocal_pi_prev = np.float64(1.0) / pi_prev_last
    t_theta = t_first * theta
    inner = reciprocal_pi_prev + t_theta
    pihat_first = np.float64(1.0) / inner
    sahat_first = np.float64(1.0) / pihat_first

    masks = build_trial_masks(y, u)
    ignored = tuple(int(i) for i in np.flatnonzero(masks.ignored))
    traj, states = problem.forward(
        u,
        full[: problem.n_perceptual],
        transformed=True,
        irregular_intervals=bool(problem.prc.options.get("irregular_intervals", False)),
        ignored_trials=ignored,
    )
    actual = {
        "logsa0_last": logsa0_last,
        "sa0_last": sa0_last,
        "pi_prev_last": pi_prev_last,
        "logtheta": logtheta,
        "theta": theta,
        "t_first": t_first,
        "reciprocal_pi_prev": reciprocal_pi_prev,
        "t_theta": t_theta,
        "inner": inner,
        "pihat_first": pihat_first,
        "sahat_first": sahat_first,
        "traj_sahat_first": np.float64(traj["sahat"][0, l - 1]),
        "inf_sahat_first": np.float64(states[0, l - 1, 1]),
    }
    expected = {key: scalar(reference["primitives"][key]) for key in ORDER}
    comparisons = {key: compare(actual[key], expected[key]) for key in ORDER}
    first_difference = next(
        (key for key in ORDER if not comparisons[key]["exact"]),
        None,
    )

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "sample": reference["sample"],
        "classification": (
            "NO_THETA_PRIMITIVE_DIVERGENCE"
            if first_difference is None
            else "THETA_PRIMITIVE_DIVERGENCE"
        ),
        "first_difference": first_difference,
        "comparisons": comparisons,
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
