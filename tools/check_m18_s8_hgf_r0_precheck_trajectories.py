#!/usr/bin/env python3
"""Compare frozen MATLAB/HGFX raw HGF trajectories before the terminal validity gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.models.hgf_binary import hgf_binary

PROTOCOL = "m18-s8-hgf-r0-precheck-trajectory-1"
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CASE_ID = "PR-hgf_binary-T256-S0.35-R0"
CASE_SHA = "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5"
JUMP_TOL = np.float64(16.0)
FIELDS = ("muhat", "pihat", "v", "w", "da", "mu", "pi", "psi", "epsi")


def _normalise(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def _array(value: Any) -> np.ndarray:
    if isinstance(value, dict) and value.get("hgfx_numeric") == "ieee-strings-v1":
        return np.asarray(_normalise(value["data"]), dtype=np.float64).reshape(
            value["shape"], order="F"
        )
    return np.asarray(_normalise(value), dtype=np.float64)


def _scalar(value: Any) -> float:
    return float(_array(value).reshape(-1)[0])


def _summary(actual: np.ndarray, expected: np.ndarray) -> dict[str, Any]:
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    if a.shape != e.shape:
        return {"shape_match": False, "hgfx_shape": list(a.shape), "matlab_shape": list(e.shape)}
    same = (a == e) | (np.isnan(a) & np.isnan(e))
    finite = np.isfinite(a) & np.isfinite(e)
    diff = np.abs(a - e)
    first = None
    if not np.all(same):
        idx = tuple(int(i) for i in np.argwhere(~same)[0])
        first = {
            "index_zero_based": list(idx),
            "hgfx": float(a[idx]),
            "matlab": float(e[idx]),
            "abs_diff": float(diff[idx]),
        }
    if np.any(finite):
        finite_diff = diff[finite]
        max_abs = float(np.max(finite_diff))
        scale = np.maximum(np.abs(e[finite]), np.float64(1.0))
        max_scaled = float(np.max(finite_diff / scale))
    else:
        max_abs = float("nan")
        max_scaled = float("nan")
    return {
        "shape_match": True,
        "exact": bool(np.all(same)),
        "different_count": int(same.size - np.count_nonzero(same)),
        "first_difference": first,
        "max_abs": max_abs,
        "max_scaled_abs": max_scaled,
    }


def _validity(mu: np.ndarray, pi: np.ndarray) -> dict[str, Any]:
    selected_mu = np.asarray(mu, dtype=np.float64)[:, 1:]
    selected_pi = np.asarray(pi, dtype=np.float64)[:, 1:]
    dmu = np.diff(selected_mu, axis=0)
    dpi = np.diff(selected_pi, axis=0)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        rmdmu = np.sqrt(np.mean(dmu**2, axis=0))
        rmdpi = np.sqrt(np.mean(dpi**2, axis=0))
        ratio_mu = np.abs(dmu) / rmdmu
        ratio_pi = np.abs(dpi) / rmdpi
    bad = bool(
        np.any(np.isnan(mu))
        or np.any(np.isnan(pi))
        or np.any(ratio_mu > JUMP_TOL)
        or np.any(ratio_pi > JUMP_TOL)
    )
    return {
        "invalid": bad,
        "rmdmu": rmdmu.tolist(),
        "rmdpi": rmdpi.tolist(),
        "max_mu_ratio": float(np.nanmax(ratio_mu)),
        "max_pi_ratio": float(np.nanmax(ratio_pi)),
        "max_mu_ratio_index_zero_based": [int(i) for i in np.unravel_index(np.nanargmax(ratio_mu), ratio_mu.shape)],
        "max_pi_ratio_index_zero_based": [int(i) for i in np.unravel_index(np.nanargmax(ratio_pi), ratio_pi.shape)],
    }


def _hgfx_raw(case: dict[str, Any], free: np.ndarray) -> dict[str, np.ndarray]:
    u = np.asarray(case["u"], dtype=np.float64)
    prc = hgf_binary_config().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    idx = np.asarray(case["free_indices_zero_based"], dtype=np.int64)
    full[idx] = np.asarray(free, dtype=np.float64).reshape(-1)
    traj, _ = hgf_binary(u, full[: len(prc.parameters)], transformed=True, validate=False)
    pi = np.float64(1.0) / np.asarray(traj["sa"], dtype=np.float64)
    pihat = np.float64(1.0) / np.asarray(traj["sahat"], dtype=np.float64)
    return {
        "mu": np.asarray(traj["mu"], dtype=np.float64),
        "pi": pi,
        "muhat": np.asarray(traj["muhat"], dtype=np.float64),
        "pihat": pihat,
        "v": np.asarray(traj["v"], dtype=np.float64),
        "w": np.asarray(traj["w"], dtype=np.float64),
        "da": np.asarray(traj["da"], dtype=np.float64),
        "psi": np.asarray(traj["psi"], dtype=np.float64),
        "epsi": np.asarray(traj["epsi"], dtype=np.float64),
    }


def main(fixture_path: Path, matlab_path: Path, output_path: Path) -> int:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    ref = json.loads(matlab_path.read_text(encoding="utf-8"))
    if ref.get("protocol") != PROTOCOL or ref.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Frozen precheck protocol/reference mismatch")
    if ref.get("case_id") != CASE_ID or ref.get("case_sha256") != CASE_SHA:
        raise ValueError("Frozen R0 case mismatch")
    cases = [c for c in fixture.get("cases", []) if c.get("case_id") == CASE_ID]
    if len(cases) != 1 or cases[0].get("case_sha256") != CASE_SHA:
        raise ValueError("Immutable R0 fixture missing or changed")
    case = cases[0]

    rows: list[dict[str, Any]] = []
    global_first: dict[str, Any] | None = None
    all_matlab_invalid = True
    all_hgfx_invalid = True
    for point in ref.get("points", []):
        free = _array(point["free"]).reshape(-1)
        actual = _hgfx_raw(case, free)
        expected = {field: _array(point[field]) for field in FIELDS}
        comparisons = {field: _summary(actual[field], expected[field]) for field in FIELDS}
        matlab_validity = {
            "invalid": bool(point["invalid_by_formula"]),
            "rmdmu": _array(point["rmdmu"]).reshape(-1).tolist(),
            "rmdpi": _array(point["rmdpi"]).reshape(-1).tolist(),
            "max_mu_ratio": _scalar(point["max_mu_ratio"]),
            "max_pi_ratio": _scalar(point["max_pi_ratio"]),
            "max_mu_ratio_index_1based": _array(point["max_mu_ratio_index_1based"]).reshape(-1).astype(int).tolist(),
            "max_pi_ratio_index_1based": _array(point["max_pi_ratio_index_1based"]).reshape(-1).astype(int).tolist(),
        }
        hgfx_validity = _validity(actual["mu"], actual["pi"])
        all_matlab_invalid &= matlab_validity["invalid"]
        all_hgfx_invalid &= hgfx_validity["invalid"]

        point_first = None
        for field in FIELDS:
            first = comparisons[field].get("first_difference")
            if first is None:
                continue
            candidate = {
                "field": field,
                **first,
            }
            trial = first["index_zero_based"][0] if first["index_zero_based"] else 10**9
            priority = FIELDS.index(field)
            key = (trial, priority)
            if point_first is None or key < point_first[0]:
                point_first = (key, candidate)
        point_first_payload = None if point_first is None else point_first[1]
        if point_first_payload is not None:
            tag = {
                "step_1based": int(round(_scalar(point["step_1based"]))),
                "h": _scalar(point["h"]),
                "side": point.get("side", "plus"),
                **point_first_payload,
            }
            trial = point_first_payload["index_zero_based"][0]
            priority = FIELDS.index(point_first_payload["field"])
            if global_first is None or (trial, priority) < global_first[0]:
                global_first = ((trial, priority), tag)

        rows.append({
            "step_1based": int(round(_scalar(point["step_1based"]))),
            "h": _scalar(point["h"]),
            "side": point.get("side", "plus"),
            "matlab_validity": matlab_validity,
            "hgfx_validity": hgfx_validity,
            "validity_match": bool(matlab_validity["invalid"] == hgfx_validity["invalid"]),
            "first_core_difference": point_first_payload,
            "fields": comparisons,
        })

    if global_first is None:
        classification = "PRECHECK_TRAJECTORIES_EXACT"
        first_payload = None
    else:
        classification = "PRECHECK_TRAJECTORY_NUMERICS_DIVERGE"
        first_payload = global_first[1]

    payload = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": CASE_ID,
        "case_sha256": CASE_SHA,
        "classification": classification,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "all_three_matlab_invalid": bool(all_matlab_invalid),
        "all_three_hgfx_invalid": bool(all_hgfx_invalid),
        "first_core_difference": first_payload,
        "points": rows,
        "note": "Diagnostic only. Raw MATLAB states come from the frozen hgf_binary implementation with only its terminal hgf_check_trajectories call temporarily shadowed after the official fit; no scientific input, threshold, optimizer, or acceptance criterion is changed.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": classification,
        "all_three_matlab_invalid": payload["all_three_matlab_invalid"],
        "all_three_hgfx_invalid": payload["all_three_hgfx_invalid"],
        "first_core_difference": first_payload,
        "validity_matches": [row["validity_match"] for row in rows],
        "matlab_max_ratios": [[row["matlab_validity"]["max_mu_ratio"], row["matlab_validity"]["max_pi_ratio"]] for row in rows],
        "hgfx_max_ratios": [[row["hgfx_validity"]["max_mu_ratio"], row["hgfx_validity"]["max_pi_ratio"]] for row in rows],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("matlab", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.fixture, args.matlab, args.output))
