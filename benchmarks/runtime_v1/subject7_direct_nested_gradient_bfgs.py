#!/usr/bin/env python3
"""PERF-01D: direct *private frozen MATLAB* Ridders gradient, BFGS margins.

Strict precommitted 50 original BFGS occurrences, not 50 posthoc 'best' points.
No original fitting gate, tolerance, benchmark or publication claim is altered.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

import numpy as np

RUN = "42187240378"
SOURCE_SHA = "5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d"
REF = "2437f4dc241541072722a2695ddeca7b44d83dd3"
HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
HASHES = {
    "hgfx_raw.json": "060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce",
    "matlab_raw.json": "4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a",
}
START = [-3., -6., 3.871201010907891]
ORIG = ("hgfx", "matlab")
SCHEMA = "perf01d-original-bfgs-50-gradient-anchors-v1"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(path: Path):
    return sha256(path.read_bytes()).hexdigest()


def original_inventory(root: Path, archived: Path):
    from compare_subject7_bfgs_state import inspect_one

    report = json.loads((archived / "summary.json").read_bytes())
    require(str(report.get("github_run_id")) == RUN
            and report.get("candidate_sha") == SOURCE_SHA
            and report.get("status") == "AUTHOR_SIDE_BFGS_STATE_RECONSTRUCTION_NOT_SCIENTIFIC_PASS_NOT_TIMED"
            and report.get("raw_evidence_sha256") == HASHES
            and report.get("source_run_id") == "41863441006",
            "Original real public-fit BFGS evidence metadata changed")
    original_fit = json.loads((root / "fit_cohort_results" / "summary-41863441006.json").read_bytes())
    require(original_fit.get("subject_count") == 64
            and original_fit.get("classification_counts") == {
                "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
                "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1,
            }
            and original_fit["cases"][7]["mismatched_fields"] == ["traj.mu", "traj.muhat"]
            and original_fit["cases"][7]["fields"]["traj.mu"]["mismatch_count"] == 4
            and original_fit["cases"][7]["fields"]["traj.muhat"]["mismatch_count"] == 4,
            "Original 63/64 and subject-7 four-plus-four scientific failures changed")
    raw = {}
    shapes = {}
    for name in ORIG:
        fn = name + "_raw.json"
        require(digest(archived / fn) == HASHES[fn],
                "Exact original real BFGS raw SHA-256 changed: " + fn)
        raw[name] = json.loads((archived / fn).read_bytes())
        shapes[name] = inspect_one(raw[name], name)
        require(raw[name]["source_input_sha256"] == digest(root / "inputs" / "binary_128_s64.json")
                and raw[name]["source_config_sha256"] == digest(root / "configs" / "hgf_binary_128.json"),
                "Original canonical input/config bytes changed")
    require(raw["hgfx"]["source_input_sha256"] == raw["matlab"]["source_input_sha256"]
            and raw["hgfx"]["source_config_sha256"] == raw["matlab"]["source_config_sha256"],
            "Different physical canonical sources")
    return raw, shapes


def build_anchors(root: Path, archived: Path):
    raw, _ = original_inventory(root, archived)
    rows = []
    for origin in ORIG:
        x = np.asarray(raw[origin]["iter_x"], np.float64)
        values = np.asarray(raw[origin]["iter_val"], np.float64)
        for index in range(25):
            rows.append({
                "anchor_origin": origin,
                "record_index_zero_based": index,
                "free_parameters": x[index].tolist(),
                "original_public_iter_val": float(values[index]),
            })
    require(len(rows) == 50 and
            [x["anchor_origin"] for x in rows] == ["hgfx"] * 25 + ["matlab"] * 25
            and [x["record_index_zero_based"] for x in rows] == list(range(25)) * 2,
            "All 50 frozen original history occurrences required")
    return {
        "schema": SCHEMA, "status": "PRESPECIFIED_50_ORIGINAL_BFGS_ANCHORS",
        "original_bfgs_source_run": RUN,
        "original_bfgs_source_sha": SOURCE_SHA,
        "original_hgfx_raw_sha256": HASHES["hgfx_raw.json"],
        "original_matlab_raw_sha256": HASHES["matlab_raw.json"],
        "frozen_hgfx_sha": HGFX, "frozen_matlab_sha": REF,
        "original_science": "63/64 NONPASS",
        "subject_index_zero_based": 7, "trials": 128,
        "model": "hgf_binary", "observation": "unitsq_sgm",
        "free_indices_zero_based": [12, 13, 14], "start_free": START,
        "source_input_sha256": raw["hgfx"]["source_input_sha256"],
        "source_config_sha256": raw["hgfx"]["source_config_sha256"],
        "cases": rows, "no_timing": True,
        "independent_review": "NOT_RECEIVED", "perf01c": "NOT_FROZEN",
    }


def ordered_uint64(value):
    """Monotone binary64 encoding, including sign; exact ULP distance."""
    bits = struct.unpack(">Q", struct.pack(">d", float(value)))[0]
    return (~bits & ((1 << 64) - 1)) if bits & (1 << 63) else bits | (1 << 63)


def ulp_distance(a, b):
    require(math.isfinite(float(a)) and math.isfinite(float(b)),
            "ULP distance requires finite objective values")
    return abs(ordered_uint64(a) - ordered_uint64(b))


def stop_margin(x, grad, val):
    x, grad = np.asarray(x, float), np.asarray(grad, float)
    require(x.shape == grad.shape == (3,) and np.isfinite(x).all()
            and np.isfinite(grad).all() and math.isfinite(float(val)),
            "Original gradient stop scalars must be finite")
    score = float(np.max(np.abs(grad) * np.maximum(np.abs(x), 1.)
                         / max(abs(float(val)), 1.)))
    return {"score": score, "original_tol_grad": 1e-3,
            "signed_margin_tol_minus_score": 1e-3 - score,
            "condition_converges_if_tested": bool(score < 1e-3)}


def bfgs_margins(raw, own_rows, origin):
    """Retrospective MATLAB-source formulas, not internal optimizer event logs."""
    require(len(own_rows) == 25, "Original own history denominator changed")
    x = np.asarray(raw["iter_x"], float)
    values = np.asarray([r[origin]["objective"] for r in own_rows], float)
    grad = np.asarray([r[origin]["gradient"] for r in own_rows], float)
    t = np.asarray(raw["iter_inverse_hessian"], float)
    require(x.shape == (101, 3) and grad.shape == (25, 3)
            and values.shape == (25,) and t.ndim == 3 and
            t.shape[1:] == (3, 3) and len(t) >= 23
            and np.isfinite(grad).all() and np.isfinite(values).all(),
            "BFGS own history or complete private gradient missing")
    stops = [dict(record_index_zero_based=i, **stop_margin(x[i], grad[i], values[i]))
             for i in range(25)]
    curvature = []
    for i in range(1, 23):
        dx = x[i] - x[i-1]
        dg = grad[i] - grad[i-1]
        lhs = float(dg @ dx)
        rhs = float(np.sqrt(np.finfo(np.float64).eps
                            * float(dg @ dg) * float(dx @ dx)))
        stored_change = bool(np.any(t[i] != t[i-1]))
        curvature.append({
            "record_index_zero_based": i,
            "lhs_dgrad_dot_dx": lhs, "rhs_sqrt_eps_norm_products": rhs,
            "signed_margin_lhs_minus_rhs": lhs-rhs,
            "reconstructed_update_condition": bool(lhs > rhs),
            "original_saved_inverse_hessian_changed": stored_change,
            "reconstructed_condition_matches_saved_state": bool((lhs > rhs) == stored_change),
        })
    line = []
    for i in range(22):
        raw_dir = -(t[i] @ grad[i])
        size = float(np.linalg.norm(raw_dir))
        require(math.isfinite(size), "Original saved BFGS direction norm is nonfinite")
        clipped = raw_dir if size <= 1. else raw_dir / size
        predicted = x[i] + clipped
        residual = float(np.max(np.abs(predicted - x[i+1])))
        slope = float(grad[i] @ raw_dir)  # Original MATLAB slope before clipping.
        lhs = float(values[i+1] - values[i])
        rhs = float(1e-4 * slope)
        line.append({
            "from_record_zero_based": i,
            "source_unclipped_direction_norm": size,
            "source_step_clipped": bool(size > 1.),
            "unclipped_gradient_dot_direction": slope,
            "original_recorded_next_x_full_step_residual_max_abs": residual,
            "armijo_lhs_next_minus_current": lhs,
            "armijo_rhs_original_1e_minus_4_slope": rhs,
            "signed_armijo_margin_rhs_minus_lhs": rhs - lhs,
            "armijo_condition_if_tested": bool(lhs < rhs),
            "full_step_compatible_with_recorded_transition": bool(residual < 1e-11),
        })
    return {
        "gradient_stop_descriptive_all_25": stops,
        "curvature_safe_original_slots_1_to_22": curvature,
        "line_search_safe_original_transitions_0_to_21": line,
        "terminal_ambiguous_transition_indices_excluded": [22, 23],
        "source_reconstruction_not_instrumented_optimizer_branch": True,
    }


def compare(root: Path, archive: Path, anchor_path: Path, matlab_path: Path):
    from importlib import metadata
    from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
    from hgfx.optim.ridders import RiddersOptions, ridders_gradient
    from compare_subject7_same_host_repeatability_v2 import strict_pair
    from compare_subject7_full_fit_trajectories import compare_pair

    require(metadata.version("hgfx") == "1.0.0",
            "Only exact frozen HGFX v1.0.0 release is admissible")
    expected = build_anchors(root, archive)
    require(json.loads(anchor_path.read_bytes()) == expected,
            "Original source-locked 50 anchor prespec differs")
    raw, _ = original_inventory(root, archive)
    mat = json.loads(matlab_path.read_bytes())
    require(mat.get("schema") == "perf01d-direct-private-nested-bfgs-gradient-matlab-v1"
            and mat.get("status") == "AUTHOR_SIDE_EXACT_NESTED_RIDDERS_NO_SCIENTIFIC_PASS"
            and mat.get("original_bfgs_source_run") == RUN
            and mat.get("original_hgfx_raw_sha256") == HASHES["hgfx_raw.json"]
            and mat.get("original_matlab_raw_sha256") == HASHES["matlab_raw.json"]
            and mat.get("frozen_matlab_sha") == REF
            and mat.get("frozen_hgfx_sha") == HGFX
            and mat.get("source_input_sha256") == expected["source_input_sha256"]
            and mat.get("source_config_sha256") == expected["source_config_sha256"]
            and mat.get("subject_index_zero_based") == 7
            and mat.get("n_trials") == 128
            and mat.get("matlab_release") == "2026a"
            and mat.get("hook_count") == 1
            and mat.get("original_optimizer_delegated") is True
            and mat.get("no_timing") is True
            and mat.get("original_science") == "63/64 NONPASS"
            and mat.get("independent_review") == "NOT_RECEIVED"
            and mat.get("perf01c") == "NOT_FROZEN",
            "Captured MATLAB function is not original frozen private fitModel objective")
    neutrality = strict_pair(mat["native_fit"], mat["instrumented_fit"])
    neutral = neutrality["field_count"] == 28 and neutrality["all_serialized_binary64_equal"]
    require(mat["same_session_28_fields_isequaln"] is neutral,
            "MATLAB internal and Python binary64 instrumentation checks disagree")
    source = json.loads((root / "inputs" / "binary_128_s64.json").read_bytes())
    u = np.asarray(source["u"][7], float)
    y = np.asarray(source["y"][7], float)
    problem = hgf_binary_unitsq_fit_problem(y, u)
    require(list(problem.free_indices) == [12, 13, 14]
            and np.array_equal(problem.initial_free, np.asarray(START, float)),
            "Frozen original HGFX free-transform/start changed")
    probes = mat.get("cases")
    require(isinstance(probes, list) and len(probes) == 50,
            "Original 50 real private MATLAB gradient rows missing")
    result = []
    for fixed, record in zip(expected["cases"], probes):
        require(record.get("anchor_origin") == fixed["anchor_origin"]
                and record.get("record_index_zero_based") == fixed["record_index_zero_based"]
                and np.array_equal(np.asarray(record.get("free_parameters"), float),
                                   np.asarray(fixed["free_parameters"], float)),
                "Missing, changed or reordered original 50-case real MATLAB gradient anchor")
        x = np.asarray(fixed["free_parameters"], float)
        val_h = float(problem.evaluate_free(x))
        g_h, e_h = ridders_gradient(problem.evaluate_free, x, RiddersOptions(min_steps=10))
        matlab_ok = record.get("status") == "EVALUATED"
        if matlab_ok:
            val_m = float(record["objective"])
            g_m = np.asarray(record["ridders_gradient"], float).reshape(-1)
            e_m = np.asarray(record["ridders_error"], float).reshape(-1)
            require(g_m.shape == e_m.shape == (3,) and np.isfinite(g_m).all()
                    and np.isfinite(e_m).all() and math.isfinite(val_m),
                    "Nonfinite MATLAB direct-private Ridders output")
            point = {
                "objective": val_m, "gradient": g_m.tolist(),
                "ridders_error": e_m.tolist(),
            }
            maxd = float(np.max(np.abs(g_h - g_m)))
            objdiff = abs(val_h - val_m)
            ulp = ulp_distance(val_h, val_m)
        else:
            point = {"status": record.get("status"), "error_identifier": record.get("error_identifier"),
                     "error_message": record.get("error_message")}
            maxd = objdiff = ulp = None
        require(np.isfinite(g_h).all() and np.isfinite(e_h).all() and math.isfinite(val_h),
                "Frozen original HGFX Ridders output is not finite")
        result.append({
            **fixed,
            "matlab_status": record.get("status"),
            "matlab": point,
            "hgfx": {"objective": val_h, "gradient": g_h.tolist(),
                     "ridders_error": e_h.tolist()},
            "same_x_max_abs_gradient_component_difference": maxd,
            "same_x_abs_objective_difference": objdiff,
            "same_x_objective_ulp_distance": ulp,
            "original_history_objective_minus_direct_matlab":
                (val_m - fixed["original_public_iter_val"] if matlab_ok else None),
        })
    failures = [i for i, r in enumerate(result) if r["matlab_status"] != "EVALUATED"]
    states = {}
    if not failures:
        for label in ORIG:
            own = [r for r in result if r["anchor_origin"] == label]
            states[label] = bfgs_margins(raw[label], own, label)
    # All 50 original cases, and every original failed gate, are preserved.
    return {
        "schema": "perf01d-direct-private-nested-ridders-bfgs-margins-v1",
        "status": ("AUTHOR_SIDE_50_DIRECT_PRIVATE_RIDDERS_DIAGNOSTIC_REVIEW_PENDING"
                   if neutral and not failures else "AUTHOR_SIDE_DIAGNOSTIC_NONNEUTRAL_OR_INCOMPLETE"),
        "source_original_64_full_fit": "63/64 SCIENTIFIC NONPASS",
        "source_original_zero_based_subject_7_failure": {
            "traj.mu": 4, "traj.muhat": 4,
        },
        "original_bfgs_run_id": RUN,
        "original_bfgs_raw_sha256": HASHES,
        "new_matlab_raw_sha256": digest(matlab_path),
        "new_anchor_sha256": digest(anchor_path),
        "frozen_matlab_sha": REF, "frozen_hgfx_sha": HGFX,
        "full_original_50_anchor_occurrences": 50,
        "fully_evaluated_matlab_private_gradients": 50 - len(failures),
        "failed_anchor_positions": failures,
        "same_session_matlab_28_field_unchanged_tolerances": compare_pair(
            mat["instrumented_fit"], mat["native_fit"]),
        "same_session_matlab_28_field_strict_binary64": neutrality,
        "instrumentation_neutral": neutral,
        "all_50_original_same_x_paired_gradient_records": result,
        "original_BFGS_decision_margin_reconstructions": states,
        "scientific_acceptance_tolerances": "UNCHANGED original fitting; none defined for Ridders gradients",
        "source_gradstop_tol": 1e-3,
        "source_armijo_constant": 1e-4,
        "original_sixteen_and_sixty_four_subjects": "15/16, 63/64 NONPASS",
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN", "performance_timing": "NOT_RUN",
        "limitations": [
            "This captures actual private MATLAB objective and Ridders at original fixed points; not its internal gradient operation log.",
            "Curvature/Armijo/stop margins are retrospective source-formula reconstructions, NOT internally instrumented decisions.",
            "MATLAB-own vs HGFX-own gradients are at different optimizer x after divergence; no causal attribution.",
            "Terminal history 22-23 transitions excluded from acceptance-event conclusions.",
            "No source or scientific acceptance threshold changes; existing 63/64 and all eight fresh same-runner NONPASS remain.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("prepare", "compare"), required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--matlab", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.stage == "prepare":
        data = build_anchors(args.root, args.archive)
        args.anchors.parent.mkdir(parents=True, exist_ok=True)
        args.anchors.write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"original_bfgs_source": RUN, "anchors_prespecified": len(data["cases"]),
                          "original_scientific": data["original_science"]}, sort_keys=True))
        return
    require(args.matlab is not None and args.output is not None, "Missing compare paths")
    data = compare(args.root, args.archive, args.anchors, args.matlab)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "anchors": data["full_original_50_anchor_occurrences"],
        "evaluated": data["fully_evaluated_matlab_private_gradients"],
        "matlab_neutral": data["instrumentation_neutral"],
        "status": data["status"], "perf01c": data["perf01c"],
    }, sort_keys=True))
    require(data["status"] == "AUTHOR_SIDE_50_DIRECT_PRIVATE_RIDDERS_DIAGNOSTIC_REVIEW_PENDING",
            "New private MATLAB gradient evidence incomplete or instrument changed scientific fit")


if __name__ == "__main__":
    main()
