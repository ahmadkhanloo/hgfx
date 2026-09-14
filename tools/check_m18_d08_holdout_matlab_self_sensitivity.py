#!/usr/bin/env python3
"""Classify frozen MATLAB start sensitivity for D08 failed holdout seed 314159265."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array

PROTOCOL = "m18-d08-holdout-matlab-self-sensitivity-1"
SEED = 314159265
RTOL = 3e-8
ATOL = 3e-10
EXPECTED_FREE_FULL_INDICES = [1, 3, 4, 8, 9, 10, 11]
EXPECTED_KEYS = {(k, direction) for k in range(1, 8) for direction in (-1, 1)}


def close_array(actual, expected):
    a = _array(actual).reshape(-1)
    e = _array(expected).reshape(-1)
    if a.shape != e.shape:
        return False, {"shape": [list(a.shape), list(e.shape)]}
    finite = np.isfinite(a) & np.isfinite(e)
    if not np.all(finite):
        return False, {"nonfinite": True}
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=False)
    diff = np.abs(a - e)
    scale = ATOL + RTOL * np.abs(e)
    ratio = np.divide(diff, scale, out=np.full_like(diff, np.inf), where=scale > 0)
    first = None
    if not np.all(close):
        i = int(np.flatnonzero(~close)[0])
        first = {
            "index_zero_based": i,
            "actual": float(a[i]),
            "baseline": float(e[i]),
            "abs_diff": float(diff[i]),
            "allowed": float(scale[i]),
            "gate_ratio": float(ratio[i]),
        }
    return bool(np.all(close)), {
        "max_abs_diff": float(np.max(diff)),
        "max_gate_ratio": float(np.max(ratio)),
        "first_outside_gate": first,
    }


def first_exact_path_difference(actual, baseline):
    a = _array(actual)
    b = _array(baseline)
    if a.shape != b.shape:
        return {"shape_mismatch": [list(a.shape), list(b.shape)]}
    both_nan = np.isnan(a) & np.isnan(b)
    equal = (a == b) | both_nan
    if np.all(equal):
        return None
    idx = tuple(int(x) for x in np.argwhere(~equal)[0])
    return {
        "index": list(idx),
        "variant": float(a[idx]),
        "baseline": float(b[idx]),
        "abs_diff": float(abs(a[idx] - b[idx])),
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference.get("protocol") != PROTOCOL or reference.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Frozen D08 holdout diagnostic protocol/reference mismatch")
    if reference.get("case_id") != "D08_fit_holdout" or int(reference.get("seed")) != SEED:
        raise ValueError("Frozen D08 holdout seed contract mismatch")
    if reference.get("model") != "uhgf" or reference.get("observation") != "gaussian_obs":
        raise ValueError("Frozen D08 holdout model contract mismatch")

    free_init = _array(reference["free_init"]).reshape(-1)
    free_indices = _array(reference["free_full_indices_1based"]).reshape(-1).astype(int)
    if free_init.size != 7 or free_indices.tolist() != EXPECTED_FREE_FULL_INDICES:
        raise ValueError("Frozen D08 holdout free-parameter contract mismatch")
    variants = reference.get("variants", [])
    if len(variants) != 14:
        raise ValueError("Frozen fourteen-variant perturbation set is incomplete")

    baseline_arg = _array(reference["baseline"]["argMin"]).reshape(-1)
    official_arg = _array(reference["official_free_final"]).reshape(-1)
    baseline_ok, baseline_cmp = close_array(baseline_arg, official_arg)

    results = []
    evidence_complete = baseline_arg.size == 7 and np.all(np.isfinite(baseline_arg))
    any_material = False
    seen = set()
    for item in variants:
        k = int(item["component_free_index_1based"])
        direction = int(item["direction"])
        seen.add((k, direction))
        start = _array(item["start"]).reshape(-1)
        arg = _array(item["argMin"]).reshape(-1)
        requested = float(np.asarray(item["requested_spacing"], dtype=np.float64).reshape(-1)[0])
        actual_delta = float(np.asarray(item["actual_delta"], dtype=np.float64).reshape(-1)[0])
        if start.size != 7 or arg.size != 7 or not np.all(np.isfinite(arg)) or requested <= 0 or actual_delta == 0:
            evidence_complete = False
        changed = np.flatnonzero(start != free_init)
        contract_ok = bool(changed.size == 1 and changed[0] == k - 1 and np.sign(actual_delta) == direction)
        if not contract_ok:
            evidence_complete = False
        final_ok, final_cmp = close_array(arg, baseline_arg)
        any_material |= not final_ok
        results.append(
            {
                "label": item["label"],
                "component_free_index_zero_based": k - 1,
                "component_full_index_zero_based": int(item["component_full_index_1based"]) - 1,
                "direction": direction,
                "requested_spacing": requested,
                "actual_delta": actual_delta,
                "start_contract_ok": contract_ok,
                "final_within_existing_gate": final_ok,
                "final_comparison": final_cmp,
                "valMin": float(np.asarray(item["valMin"], dtype=np.float64).reshape(-1)[0]),
                "first_exact_iter_x_difference": first_exact_path_difference(
                    item["iter_x"], reference["baseline"]["iter_x"]
                ),
            }
        )

    if seen != EXPECTED_KEYS:
        evidence_complete = False

    if not baseline_ok:
        classification = "INVALID_BASELINE_REPLAY"
    elif not evidence_complete:
        classification = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif any_material:
        classification = "MATLAB_START_ULP_BASIN_SENSITIVE"
    else:
        classification = "NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED"

    material = [item["label"] for item in results if not item["final_within_existing_gate"]]
    output = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D08_fit_holdout",
        "seed": SEED,
        "classification": classification,
        "existing_gate": {"rtol": RTOL, "atol": ATOL},
        "baseline_reproduces_reference_final": baseline_ok,
        "baseline_comparison": baseline_cmp,
        "material_variant_count": len(material),
        "material_variants": material,
        "variants": results,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "decision_note": (
            "This is reference-only evidence for the already-failed prospective holdout seed. "
            "A positive sensitivity result cannot rewrite that failure or independently confer PASS."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"classification": classification, "baseline_ok": baseline_ok, "material_variant_count": len(material), "material_variants": material}), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
