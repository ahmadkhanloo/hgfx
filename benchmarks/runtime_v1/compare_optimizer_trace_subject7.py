#!/usr/bin/env python3
"""PERF-01D: compare original subject-7 public-fit optimizer traces, UNTIMED.

The original source preallocates 101 slots; length(iter.val)==101 is not
the number of executed iterations. MATLAB does not return a termination code.
No numerical threshold, original fit result, or scientific gate is changed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from compare_fits import TOLS, numeric

HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
SOURCE_RUN = "41863441006"
SLOTS = 101


def validated(record: dict, product: str):
    if (record.get("schema") != f"perf01-subject7-optimizer-trace-{product}-v1"
            or record.get("subject_index_zero_based") != 7
            or record.get("trials") != 128
            or record.get("model") != "hgf_binary"
            or record.get("source_run_id") != SOURCE_RUN
            or record.get("frozen_hgfx_sha") != HGFX
            or record.get("frozen_matlab_sha") != MATLAB
            or record.get("status") != "FULL_PUBLIC_FIT_TRACE_EXPORTED"
            or record.get("frozen_start_matches") is not True
            or record.get("original_raw_fits_verified") is not True
            or record.get("n_rand_init") != 0):
        raise ValueError(f"Incorrect or incomplete {product} source/fit identity")
    x = np.asarray(record["iter_x"], dtype=np.float64)
    values = np.asarray(record["iter_val"], dtype=np.float64)
    if x.shape != (SLOTS, 3) or values.shape != (SLOTS,):
        raise ValueError(f"{product}: expected original maxIter+1 = 101 x 3 history")
    if not np.all(np.isfinite(x[0])) or not np.isfinite(values[0]):
        raise ValueError(f"{product}: no original finite initial record")
    finite_x = np.all(np.isfinite(x), axis=1)
    finite_val = np.isfinite(values)
    if not np.array_equal(finite_x, finite_val):
        raise ValueError(f"{product}: inconsistent trace x/val finite masks")
    valid_indices = np.flatnonzero(finite_val)
    if not np.array_equal(valid_indices, np.arange(len(valid_indices))):
        raise ValueError(f"{product}: noncontiguous recorded trace; cannot infer executed iterations")
    return x, values, finite_val


def compare(hgfx: dict, matlab: dict) -> dict:
    hx, hv, hm = validated(hgfx, "hgfx")
    mx, mv, mm = validated(matlab, "matlab")
    filled_h, filled_m = int(hm.sum()), int(mm.sum())
    shared = int(np.sum(hm & mm))
    atol, rtol = TOLS["final"][1], TOLS["final"][0]
    discrepancies = []
    first_any_numerical_difference = None
    for i in range(shared):
        exact_dx = float(np.max(np.abs(hx[i] - mx[i])))
        exact_dv = float(abs(hv[i] - mv[i]))
        if first_any_numerical_difference is None and (exact_dx != 0 or exact_dv != 0):
            first_any_numerical_difference = {
                "record_index_zero_based": i,
                "parameter_max_abs_delta": exact_dx,
                "objective_abs_delta": exact_dv,
                "note": "Exact/nonzero double differences, not a separate scientific gate.",
            }
        mismatch_x = np.any(np.abs(hx[i] - mx[i]) > atol + rtol * np.abs(mx[i]))
        mismatch_v = abs(hv[i] - mv[i]) > atol + rtol * abs(mv[i])
        if mismatch_x or mismatch_v:
            discrepancies.append({
                "record_index_zero_based": i,
                "model_iteration_index_if_no_restart": (0 if i == 0 else i),
                "free_parameter_difference_max_abs": float(np.max(np.abs(hx[i] - mx[i]))),
                "objective_difference_abs": float(abs(hv[i] - mv[i])),
                "free_parameters_outside_existing_final_tolerance": bool(mismatch_x),
                "objective_outside_existing_final_tolerance": bool(mismatch_v),
            })
    fit_delta = numeric(hgfx["final_full"], matlab["final_full"], rtol, atol)
    hgfx_orig = numeric(hgfx["final_full"], hgfx["original_final_full"], rtol, atol)
    matlab_orig = numeric(matlab["final_full"], matlab["original_final_full"], rtol, atol)
    if (hgfx.get("source_config_sha256") != matlab.get("source_config_sha256")
            or hgfx.get("source_input_sha256") != matlab.get("source_input_sha256")):
        raise ValueError("Mismatch in original dataset/config provenance")
    if (hgfx.get("fit_neg_lj") is None or matlab.get("fit_neg_lj") is None):
        raise ValueError("Missing original objective/end-of-fitting evidence")
    if not np.isclose(hv[0], mv[0], rtol=rtol, atol=atol):
        raise ValueError("Initial objective already differs; cannot attribute fit drift to optimizer")
    return {
        "schema": "perf01-subject7-optimizer-trace-comparison-v1",
        "status": "AUTHOR_SIDE_TRACE_DIAGNOSTIC_NOT_INDEPENDENTLY_REVIEWED_NOT_TIMED",
        "source_run_id": SOURCE_RUN,
        "frozen_hgfx_sha": HGFX,
        "frozen_matlab_sha": MATLAB,
        "subject_index_zero_based": 7,
        "max_iter": 100,
        "allocated_slots_per_implementation": SLOTS,
        "recorded_finite_slots": {"hgfx": filled_h, "matlab": filled_m},
        "shared_finite_slot_count": shared,
        "first_any_nonzero_double_difference": first_any_numerical_difference,
        "terminal_duplicate_finite_slots": {
            "hgfx": bool(filled_h >= 2
                     and bool(np.array_equal(hx[filled_h-1], hx[filled_h-2]))
                     and bool(hv[filled_h-1] == hv[filled_h-2])),
            "matlab": bool(filled_m >= 2
                       and bool(np.array_equal(mx[filled_m-1], mx[filled_m-2]))
                       and bool(mv[filled_m-1] == mv[filled_m-2])),
        },
        "first_different_record": discrepancies[0] if discrepancies else None,
        "all_different_record_count": len(discrepancies),
        "slot_mismatch_count": abs(filled_h-filled_m),
        "final_fitted_vector": fit_delta,
        "hgfx_fresh_vs_original_fit": hgfx_orig,
        "matlab_fresh_vs_original_fit": matlab_orig,
        "original_fit_neg_lj": {"hgfx": hgfx["fit_neg_lj"], "matlab": matlab["fit_neg_lj"]},
        "termination_reason": {
            "matlab": "NOT_EXPOSED_BY_UNMODIFIED_PUBLIC_FITMODEL",
            "hgfx": "NOT_INFERRED_FROM_PREALLOCATED_PUBLIC_ITER_ARRAY",
        },
        "classification": "OPTIMIZER_PATH_DIAGNOSTIC_ONLY_FULL_FIT_PARITY_NOT_PROMOTED",
        "interpretation": (
            "Finite recorded slots are not guaranteed to equal the number of actual optimizer "
            "iterations because the frozen MATLAB implementation overwrites index i at stopping. "
            "A 101-slot buffer alone is never evidence of 100 completed iterations. "
            "Different fitted endpoints and the original subject-7 63/64 mismatch remain preserved."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    for name in ("hgfx", "matlab", "output"):
        parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    report = compare(json.loads(args.hgfx.read_bytes()), json.loads(args.matlab.read_bytes()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+"\n")
    print(json.dumps({
        "classification": report["classification"],
        "recorded_finite_slots": report["recorded_finite_slots"],
        "first_different_record": report["first_different_record"],
        "fresh_hgfx_compatible_with_original": report["hgfx_fresh_vs_original_fit"]["status"],
        "fresh_matlab_compatible_with_original": report["matlab_fresh_vs_original_fit"]["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
