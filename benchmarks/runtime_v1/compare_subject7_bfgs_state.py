#!/usr/bin/env python3
"""PERF-01D: source-anchored, UNTImed BFGS state/line-search trace forensic.

The frozen public HGFX/MATLAB fit models export their own original BFGS
inverse-Hessian matrices. This report reconstructs candidate half-step
fractions from recorded states. This is not instrumented acceptance evidence,
not a MATLAB termination reason, and NOT a parity or performance gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
SOURCE = "41863441006"
MAX_REGU = 16
MAX_STEP = 1.0
SLOTS = 101
FILLED = 25


def inspect_one(raw: dict, engine: str) -> dict:
    if (
        raw.get("schema") != f"perf01-subject7-bfgs-state-{engine}-v1"
        or raw.get("status") != "UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED"
        or raw.get("subject_index_zero_based") != 7
        or raw.get("source_run_id") != SOURCE
        or raw.get("model") != "hgf_binary" or raw.get("trials") != 128
        or raw.get("frozen_hgfx_sha") != HGFX
        or raw.get("frozen_matlab_sha") != MATLAB
        or raw.get("original_raw_fits_verified") is not True
        or raw.get("frozen_start_matches") is not True
        or raw.get("n_rand_init") != 0
        or raw.get("ridders_min_steps") != 10
        or raw.get("finite_slots") != FILLED
    ):
        raise ValueError(f"{engine}: unverified original full-public-fit identity")
    x = np.asarray(raw["iter_x"], dtype=np.float64)
    v = np.asarray(raw["iter_val"], dtype=np.float64)
    if x.shape != (SLOTS, 3) or v.shape != (SLOTS,):
        raise ValueError(f"{engine}: full original 101-slot x/val buffers must be retained")
    valid = np.all(np.isfinite(x), axis=1) & np.isfinite(v)
    if not np.array_equal(np.flatnonzero(valid), np.arange(FILLED)):
        raise ValueError(f"{engine}: finite optimizer history is incomplete or noncontiguous")
    if not np.array_equal(x[0], np.array([-3., -6., 3.871201010907891])):
        raise ValueError(f"{engine}: original unchanged optimizer start missing")

    t = np.asarray(raw["iter_inverse_hessian"], dtype=np.float64)
    if t.ndim != 3 or t.shape[1:] != (3, 3) or not (23 <= len(t) <= 25):
        raise ValueError(f"{engine}: expected 23-25 original 3x3 inverse-Hessian slots")
    rst = raw.get("iter_resets_one_based", [])
    if rst is None:
        rst = []
    reset_indices = np.asarray(rst, dtype=np.int64).reshape(-1).tolist()
    if len(set(reset_indices)) != len(reset_indices) or any(i < 1 or i > 100 for i in reset_indices):
        raise ValueError(f"{engine}: malformed original 1-based reset indices")
    if not np.array_equal(t[0], np.eye(3)):
        raise ValueError(f"{engine}: initial BFGS inverse-Hessian must be identity")
    if np.any(~np.isfinite(t)):
        raise ValueError(f"{engine}: nonfinite inverse-Hessian history requires explicit investigation")
    grad = raw.get("ridders_recomputed_history", [])
    if len(grad) != FILLED:
        raise ValueError(f"{engine}: must retain all 25 Ridders gradient evaluations")
    g = np.empty((FILLED, 3), dtype=np.float64)
    f = np.empty(FILLED, dtype=np.float64)
    grad_error = np.empty((FILLED, 3), dtype=np.float64)
    for i, rec in enumerate(grad):
        if rec.get("record_index_zero_based") != i:
            raise ValueError(f"{engine}: reordered or omitted gradient record {i}")
        if not np.array_equal(np.asarray(rec["free_parameters"], np.float64), x[i]):
            raise ValueError(f"{engine}: Ridders gradient was not evaluated at saved x[{i}]")
        g[i] = np.asarray(rec["grad"], np.float64)
        grad_error[i] = np.asarray(rec["ridders_error"], np.float64)
        f[i] = float(rec["objective_recomputed"])
    if np.any(~np.isfinite(g)) or np.any(~np.isfinite(f)):
        raise ValueError(f"{engine}: nonfinite Ridders objective/gradient must not be ignored")
    if not np.allclose(f, v[:FILLED], rtol=3e-8, atol=3e-10):
        raise ValueError(f"{engine}: independently recomputed objective disagrees with original history")

    transitions = []
    for i in range(FILLED - 1):
        row = {
            "from_record_zero_based": i,
            "to_record_zero_based": i+1,
            "status": "UNASSESSED_NOT_A_TERMINATION_VERDICT",
            "actual_step_max_abs": float(np.max(np.abs(x[i+1] - x[i]))),
            "inverse_hessian_available": i < len(t),
        }
        if i >= len(t):
            row["status"] = "INVERSE_HESSIAN_NOT_EXPORTED_FOR_TERMINAL_SLOT"
            transitions.append(row)
            continue
        raw_dir = -(t[i] @ g[i])
        gradient_dot_direction = float(g[i] @ raw_dir)
        norm = float(np.linalg.norm(raw_dir))
        clipped = raw_dir.copy()
        if norm > MAX_STEP:
            clipped *= MAX_STEP / norm
        candidates = []
        for j in range(MAX_REGU + 1):
            alpha = 2.0 ** -j
            predicted = x[i] + alpha * clipped
            err = float(np.max(np.abs(predicted - x[i+1])))
            candidates.append((err, j, alpha))
        best_err, j, alpha = min(candidates)
        row.update({
            "status": ("SAME_STORED_STATE_OR_TERMINAL_OVERWRITE"
                       if np.array_equal(x[i+1], x[i])
                       else "HALVING_CANDIDATE_ONLY_NOT_ACTUAL_ACCEPTANCE"),
            "matrix_frobenius_norm": float(np.linalg.norm(t[i])),
            "raw_direction_norm": norm,
            "gradient_dot_unclipped_direction": gradient_dot_direction,
            "max_step_clipping_applied": bool(norm > MAX_STEP),
            "best_half_step_exponent": j,
            "best_half_step_fraction": alpha,
            "candidate_reconstruction_max_abs_residual": best_err,
            "candidate_at_max_regu_is_not_accepted": bool(j == MAX_REGU),
            "candidate_armijo_rhs_using_unclipped_slope": float(
                f[i] + 1e-4 * alpha * gradient_dot_direction
            ),
            "candidate_armijo_test_from_stored_next_value": bool(
                f[i+1] < f[i] + 1e-4 * alpha * gradient_dot_direction
            ),
            "reset_was_reported_at_next_one_based_iteration": bool(i+1 in reset_indices),
        })
        transitions.append(row)
    return {
        "engine": engine,
        "input_sha256": raw["source_input_sha256"],
        "config_sha256": raw["source_config_sha256"],
        "preallocated_slots": SLOTS,
        "filled_history_slots": FILLED,
        "inverse_hessian_slots": len(t),
        "reset_indices_one_based": reset_indices,
        "terminal_history_duplicate": bool(np.array_equal(x[23], x[24]) and v[23] == v[24]),
        "transitions": transitions,
        "matrix": t,
        "grad": g,
        "x": x,
        "f": f,
    }


def compare(hgfx: dict, matlab: dict) -> dict:
    h = inspect_one(hgfx, "hgfx")
    m = inspect_one(matlab, "matlab")
    if h["input_sha256"] != m["input_sha256"] or h["config_sha256"] != m["config_sha256"]:
        raise ValueError("Cross-language original source input/config SHA256 differs")
    n = min(h["inverse_hessian_slots"], m["inverse_hessian_slots"])
    matrix_diffs = [
        {"record_index_zero_based": i,
         "matrix_max_abs_delta": float(np.max(np.abs(h["matrix"][i] - m["matrix"][i]))),
         "hgfx_matrix_frobenius_norm": float(np.linalg.norm(h["matrix"][i])),
         "matlab_matrix_frobenius_norm": float(np.linalg.norm(m["matrix"][i]))}
        for i in range(n)
    ]
    divergence = [r for r in matrix_diffs if r["matrix_max_abs_delta"] > 0]
    steps = []
    for a, b in zip(h["transitions"], m["transitions"]):
        if a["from_record_zero_based"] != b["from_record_zero_based"]:
            raise ValueError("Step-record indexing differs")
        i = a["from_record_zero_based"]
        steps.append({
            "record_zero_based": i,
            "hgfx": a,
            "matlab": b,
            "recorded_next_points_max_abs_delta": float(np.max(np.abs(h["x"][i+1] - m["x"][i+1]))),
            "raw_Ridders_gradient_max_abs_delta_at_different_own_points": float(np.max(np.abs(h["grad"][i] - m["grad"][i]))),
            "candidate_halving_exponent_same": (
                a.get("best_half_step_exponent") == b.get("best_half_step_exponent")
                if "best_half_step_exponent" in a and "best_half_step_exponent" in b
                else None
            )
        })
    return {
        "schema": "perf01d-subject7-bfgs-line-search-diagnostic-v1",
        "status": "AUTHOR_SIDE_BFGS_STATE_RECONSTRUCTION_NOT_SCIENTIFIC_PASS_NOT_TIMED",
        "frozen_hgfx_sha": HGFX,
        "frozen_matlab_sha": MATLAB,
        "source_run_id": SOURCE,
        "subject_index_zero_based": 7,
        "model": "hgf_binary",
        "trials": 128,
        "preallocated_history_slots": SLOTS,
        "filled_history_slots": FILLED,
        "hgfx_inverse_hessian_slots": h["inverse_hessian_slots"],
        "matlab_inverse_hessian_slots": m["inverse_hessian_slots"],
        "hgfx_one_based_reset_indices": h["reset_indices_one_based"],
        "matlab_one_based_reset_indices": m["reset_indices_one_based"],
        "both_terminal_history_duplicate": bool(h["terminal_history_duplicate"] and m["terminal_history_duplicate"]),
        "matrix_shared_slot_count": n,
        "first_nonzero_matrix_difference": divergence[0] if divergence else None,
        "maximum_matrix_component_difference": max(x["matrix_max_abs_delta"] for x in matrix_diffs),
        "matrix_differences": matrix_diffs,
        "line_search_candidates": steps,
        "important_limitations": [
            "Unmodified public MATLAB optimizer does not export an explicit termination reason.",
            "A reconstructed nearest power-of-two fraction is a mathematical candidate, not an instrumented line-search acceptance decision.",
            "The frozen MATLAB optimizer overwrites terminal history slots; a duplicated final x must not be interpreted as another actual iteration.",
            "The frozen MATLAB source uses gradient-dot-direction slope before step clipping; this is reflected in the candidate Armijo arithmetic.",
            "Ridders gradients are recalculated after the full public fit at the stored OWN-implementation points. They are not identical-parameter cross-tool gradient tests.",
            "Original 63/64 subject-7 complete fitting mismatch and scientific non-PASS remain unchanged.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("hgfx","matlab","output"):
        p.add_argument("--"+name, type=Path, required=True)
    a=p.parse_args()
    result=compare(json.loads(a.hgfx.read_bytes()),json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "matrix_slots":result["matrix_shared_slot_count"],
        "first_nonzero_T":result["first_nonzero_matrix_difference"],
        "max_T_delta":result["maximum_matrix_component_difference"],
        "n_line_search_steps":len(result["line_search_candidates"]),
        "final_duplicate":result["both_terminal_history_duplicate"],
        "status":result["status"],
    },sort_keys=True))


if __name__=="__main__":
    main()
