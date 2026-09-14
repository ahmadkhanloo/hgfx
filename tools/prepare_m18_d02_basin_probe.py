#!/usr/bin/env python3
"""Prepare the frozen D02 cross-endpoint same-vector objective grid."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

import hgfx
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config

PROTOCOL = "m18-d02-basin-probe-1"
ALPHAS = np.asarray([0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0])


def make_problem(reference):
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
    prc = prc.resolve_placeholders(u)
    obs = obs.resolve_placeholders(u)
    return u, y, prc, obs, WorkflowFitProblem(y, u, prc, obs)


def main(reference_path: Path, points_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    meta = reference["metadata"]
    if meta.get("protocol") != PROTOCOL:
        raise ValueError("Diagnostic protocol mismatch")
    if meta.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if meta.get("numeric_encoding") != "ieee-strings-v1":
        raise ValueError("Numeric encoding mismatch")
    if reference.get("case_id") != "D02_fit":
        raise ValueError("Unexpected case")
    if int(reference.get("seed")) != 123456789:
        raise ValueError("Frozen D02 seed mismatch")

    u, y, prc, obs, problem = make_problem(reference)
    estimate = hgfx.fit_model(y, u, prc, obs, "quasinewton_optim_config")

    matlab_final = _array(reference["matlab_final"]).reshape(-1).copy()
    prior_means = np.r_[
        _array(reference["prc_priormus"]).reshape(-1),
        _array(reference["obs_priormus"]).reshape(-1),
    ]
    if matlab_final.shape != prior_means.shape:
        raise ValueError("MATLAB endpoint/prior shape mismatch")

    hgfx_final = np.asarray(estimate.optim.final, dtype=np.float64).reshape(-1)
    if hgfx_final.shape != matlab_final.shape:
        raise ValueError("HGFX/MATLAB endpoint shape mismatch")

    # Structural NaNs are part of the MATLAB/HGFX parameter contract for
    # non-applicable fixed slots.  The first CI execution incorrectly used
    # np.array_equal without equal_nan=True, which rejected NaN-vs-NaN even
    # though the endpoints represented the same fixed structure.  Keep those
    # NaNs in the generated full vectors; interpolate only the free coordinates.
    free = np.asarray(problem.free_indices, dtype=np.int64)
    fixed_mask = np.ones(matlab_final.size, dtype=bool)
    fixed_mask[free] = False

    matlab_fixed = matlab_final[fixed_mask]
    hgfx_fixed = hgfx_final[fixed_mask]
    if not np.array_equal(matlab_fixed, hgfx_fixed, equal_nan=True):
        raise ValueError("Fixed transformed parameters differ between endpoints")

    points = np.repeat(matlab_final[None, :], len(ALPHAS), axis=0)
    points[:, free] = (
        (1.0 - ALPHAS[:, None]) * matlab_final[free][None, :]
        + ALPHAS[:, None] * hgfx_final[free][None, :]
    )

    hgfx_neg_lj = np.asarray(
        [problem.evaluate_full(point).neg_log_joint for point in points], dtype=np.float64
    )

    points_path.parent.mkdir(parents=True, exist_ok=True)
    # 17 significant digits round-trip binary64 through MATLAB str2double/readmatrix.
    np.savetxt(points_path, points, delimiter=",", fmt="%.17g")

    finite_endpoint = np.isfinite(matlab_final) & np.isfinite(hgfx_final)
    if not np.any(finite_endpoint):
        raise ValueError("No finite endpoint coordinates available")
    endpoint_max_abs_diff = float(
        np.max(np.abs(hgfx_final[finite_endpoint] - matlab_final[finite_endpoint]))
    )

    result = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "alphas": ALPHAS.tolist(),
        "free_indices_zero_based": free.tolist(),
        "structural_nan_indices_zero_based": np.flatnonzero(
            fixed_mask & ~np.isfinite(matlab_final)
        ).tolist(),
        "matlab_final_resolved": matlab_final.tolist(),
        "hgfx_final": hgfx_final.tolist(),
        "endpoint_max_abs_diff": endpoint_max_abs_diff,
        "hgfx_negLj": hgfx_neg_lj.tolist(),
        "matlab_reported_negLj": float(_array(reference["matlab_negLj"]).reshape(-1)[0]),
        "hgfx_reported_negLj": float(estimate.optim.negLj),
        "note": (
            "Diagnostic only; structural NaNs are preserved exactly and only frozen free "
            "coordinates are interpolated. Endpoints and alpha grid do not modify the "
            "release gate."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")
    print(
        json.dumps(
            {
                "endpoint_max_abs_diff": result["endpoint_max_abs_diff"],
                "structural_nan_indices_zero_based": result[
                    "structural_nan_indices_zero_based"
                ],
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.points, args.output))
