#!/usr/bin/env python3
"""Post-result exploratory Ridders stencil trace; NEVER a scientific gate.

Target is explicitly selected after the preserved 50-row gradient observation.
All original failed science and its immutable raw hashes remain binding.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import struct
from hashlib import sha256

import numpy as np

SOURCE_RUN = "42305573614"
SOURCE_SHA = "b9ff63685aac7ecd10a7cc4d1c33a4dc28699a62"
PRESPEC_SHA = "e1c3e2e83045896195701926a5f94fa361b0f091"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
TARGET = [-1.1621811570388512, -6.37816839506084, -0.23738383160834042]
SOURCE_HASH = {
    "locked-50-bfgs-anchors.json": "d92690111b2fa128c045f29b39aa95110b5e5cd838f90c48a733400a3e537913",
    "real-private-matlab-ridders.json": "90de6c75c13736fae95bc0645950ac0352546fd7262c4d5f70d97f8b9b14e978",
    "paired-direct-private-gradient-bfgs-margins.json": "2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d",
}
ORIGINAL_HASH = {
    "hgfx_raw.json": "060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce",
    "matlab_raw.json": "4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a",
}


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def bits(value):
    return struct.pack(">d", float(value))


def ulp(a, b):
    require(math.isfinite(float(a)) and math.isfinite(float(b)), "Nonfinite ULP")
    def order(n):
        raw = struct.unpack(">Q", bits(n))[0]
        return ((~raw) & ((1 << 64) - 1)) if raw & (1 << 63) else raw | (1 << 63)
    return abs(order(a) - order(b))


def same_coord(a, b):
    return len(a) == len(b) == 3 and all(bits(x) == bits(y) for x, y in zip(a, b))


def source_check(archive: Path, original: Path):
    for name, expected in SOURCE_HASH.items():
        require(digest(archive / name) == expected, "Prior 50-case raw evidence tampered: " + name)
    for name, expected in ORIGINAL_HASH.items():
        require(digest(original / name) == expected, "Original BFGS source raw altered: " + name)
    prev = json.loads((archive / "paired-direct-private-gradient-bfgs-margins.json").read_bytes())
    anchors = json.loads((archive / "locked-50-bfgs-anchors.json").read_bytes())
    mat = json.loads((archive / "real-private-matlab-ridders.json").read_bytes())
    require(len(anchors["cases"]) == len(prev["all_50_original_same_x_paired_gradient_records"])
            == len(mat["cases"]) == 50, "Original 50 gradients must be preserved")
    require(prev["status"] == "AUTHOR_SIDE_50_DIRECT_PRIVATE_RIDDERS_DIAGNOSTIC_REVIEW_PENDING"
            and prev["source_original_64_full_fit"] == "63/64 SCIENTIFIC NONPASS"
            and prev["perf01c"] == "NOT_FROZEN"
            and prev["independent_scientific_review"] == "NOT_RECEIVED"
            and prev["instrumentation_neutral"] is True
            and mat["same_session_28_fields_isequaln"] is True
            and mat["github_run_id"] == SOURCE_RUN
            and mat["github_sha"] == SOURCE_SHA
            and mat["frozen_matlab_sha"] == MATLAB_SHA
            and mat["frozen_hgfx_sha"] == HGFX_SHA,
            "Preserved 50-case and original failure metadata has changed")
    s = anchors["cases"][6]
    observed = prev["all_50_original_same_x_paired_gradient_records"][6]
    require(s["anchor_origin"] == "hgfx"
            and s["record_index_zero_based"] == 6
            and same_coord(s["free_parameters"], TARGET)
            and same_coord(observed["free_parameters"], TARGET)
            and observed["matlab_status"] == "EVALUATED"
            and observed["same_x_max_abs_gradient_component_difference"]
                == 6.884955006114524e-08
            and observed["same_x_abs_objective_difference"] == 0
            and observed["hgfx"]["gradient"][0] == 5.046862798072859
            and observed["matlab"]["gradient"][0] == 5.046862866922409,
            "Post-result target does not match the original observed counterexample")
    require(anchors["original_hgfx_raw_sha256"] == ORIGINAL_HASH["hgfx_raw.json"]
            and anchors["original_matlab_raw_sha256"] == ORIGINAL_HASH["matlab_raw.json"],
            "Original optimizer source-hash provenance changed")
    return anchors, observed


def make_manifest(archive, original):
    anchors, observed = source_check(archive, original)
    return {
        "schema": "perf01d-posthoc-ridders-trace-manifest-v1",
        "status": "POST_RESULT_SELECTION_NOT_A_SCIENTIFIC_GATE",
        "protocol_commit_before_new_stencil_samples": PRESPEC_SHA,
        "original_frozen_hgfx_sha": HGFX_SHA,
        "original_frozen_matlab_sha": MATLAB_SHA,
        "original_50_probe_run_id": SOURCE_RUN,
        "original_50_probe_executed_sha": SOURCE_SHA,
        "source_50_sha256": SOURCE_HASH,
        "source_original_bfgs_sha256": ORIGINAL_HASH,
        "source_input_sha256": anchors["source_input_sha256"],
        "source_config_sha256": anchors["source_config_sha256"],
        "original_full_scientific_fits": "63/64 NONPASS",
        "target_origin": "hgfx",
        "target_record_index_zero_based": 6,
        "target_free_parameters": TARGET,
        "observed_first_coordinate_gradient_hgfx": observed["hgfx"]["gradient"][0],
        "observed_first_coordinate_gradient_matlab": observed["matlab"]["gradient"][0],
        "observed_same_x_gradient_component_delta": observed["same_x_max_abs_gradient_component_difference"],
        "observed_base_objective_exact": True,
        "ridders_min_steps": 10,
        "trace_every_actual_evaluation_in_all_3_coordinates": True,
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "no_timing": True,
    }


def validate_stream(stream, target, label):
    require(isinstance(stream, list) and len(stream) >= 7 and len(stream) <= 601,
            label + " Ridders call inventory missing or >100 steps*2*3+center")
    require(same_coord(stream[0]["free_parameters"], target), label + " first call not f(x)")
    for i, row in enumerate(stream):
        x = row["free_parameters"]
        require(len(x) == 3 and all(math.isfinite(float(v)) for v in x)
                and math.isfinite(float(row["objective"])),
                label + " nonfinite or malformed objective call at " + str(i))
        if i:
            require(sum(bits(x[j]) != bits(target[j]) for j in range(3)) == 1,
                    label + " Ridders perturbation must change exactly one free coordinate")


def pair_streams(a, b):
    """Pair chronological calls ONLY if all binary64 coordinates agree."""
    require(len(a) >= 7 and len(b) >= 7, "Both real call streams must exist")
    merged = []
    for i in range(max(len(a), len(b))):
        left = a[i] if i < len(a) else None
        right = b[i] if i < len(b) else None
        coord_match = bool(left is not None and right is not None
                           and same_coord(left["free_parameters"], right["free_parameters"]))
        rec = {"call_index_zero_based": i,
               "both_present": left is not None and right is not None,
               "same_binary64_coordinates": coord_match}
        if coord_match:
            obj_a, obj_b = float(left["objective"]), float(right["objective"])
            rec.update({"absolute_objective_difference": abs(obj_a - obj_b),
                        "objective_ulp_distance": ulp(obj_a, obj_b)})
        else:
            rec.update({"hgfx_free_parameters": left["free_parameters"] if left else None,
                        "matlab_free_parameters": right["free_parameters"] if right else None})
        merged.append(rec)
    matched = [x for x in merged if x["same_binary64_coordinates"]]
    differing = [x for x in matched if x["objective_ulp_distance"] != 0]
    unmapped = [x for x in merged if not x["same_binary64_coordinates"]]
    return {
        "hgfx_call_count": len(a), "matlab_call_count": len(b),
        "index_aligned_exact_coordinate_pairs": len(matched),
        "index_aligned_exact_coordinate_objective_differences": len(differing),
        "first_coord_mismatch_index": unmapped[0]["call_index_zero_based"] if unmapped else None,
        "first_objective_mismatch_index": differing[0]["call_index_zero_based"] if differing else None,
        "max_matched_objective_ulp": max((x["objective_ulp_distance"] for x in matched), default=None),
        "max_matched_objective_abs_difference": max((x["absolute_objective_difference"] for x in matched), default=None),
        "all_calls_by_original_index_with_unpaired_coordinates_explicit": merged,
        "no_attempt_to_pair_different_coordinates": True,
    }


def run_compare(root, archive, original, manifest_path, matlab_path):
    from importlib import metadata
    from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
    from hgfx.optim.ridders import RiddersOptions, ridders_gradient
    from compare_subject7_same_host_repeatability_v2 import strict_pair
    require(metadata.version("hgfx") == "1.0.0", "Only frozen HGFX v1.0.0 is admissible")
    manifest = make_manifest(archive, original)
    require(json.loads(Path(manifest_path).read_bytes()) == manifest,
            "Prospective selected-target manifest differs")
    m = json.loads(Path(matlab_path).read_bytes())
    require(m.get("schema") == "perf01d-posthoc-ridders-matlab-trace-v1"
            and m.get("status") == "POST_RESULT_STENCIL_TRACE_NOT_A_SCIENTIFIC_PASS"
            and m.get("protocol_commit_before_new_stencil_samples") == PRESPEC_SHA
            and m.get("original_50_probe_run_id") == SOURCE_RUN
            and m.get("original_frozen_hgfx_sha") == HGFX_SHA
            and m.get("original_frozen_matlab_sha") == MATLAB_SHA
            and m.get("source_50_anchor_sha256") == SOURCE_HASH["locked-50-bfgs-anchors.json"]
            and m.get("source_50_matlab_sha256") == SOURCE_HASH["real-private-matlab-ridders.json"]
            and m.get("source_50_paired_sha256") == SOURCE_HASH["paired-direct-private-gradient-bfgs-margins.json"]
            and m.get("source_original_bfgs_hgfx_sha256") == ORIGINAL_HASH["hgfx_raw.json"]
            and m.get("source_original_bfgs_matlab_sha256") == ORIGINAL_HASH["matlab_raw.json"]
            and m.get("source_input_sha256") == manifest["source_input_sha256"]
            and m.get("source_config_sha256") == manifest["source_config_sha256"]
            and m.get("hook_count") == 1
            and m.get("original_optimizer_delegated") is True
            and m.get("n_trials") == 128
            and m.get("subject_index_zero_based") == 7
            and m.get("no_timing") is True
            and m.get("original_full_scientific_fits") == "63/64 NONPASS"
            and m.get("independent_scientific_review") == "NOT_RECEIVED"
            and m.get("perf01c") == "NOT_FROZEN"
            and same_coord(m.get("target_free_parameters", []), TARGET),
            "MATLAB private objective trace lost source provenance")
    neutral = strict_pair(m["native_fit"], m["instrumented_fit"])
    require(neutral["field_count"] == 28
            and neutral["all_serialized_binary64_equal"] is m["same_session_28_fields_isequaln"],
            "MATLAB strict 28-field binary64 neutrality contradiction")
    source = json.loads((root / "inputs" / "binary_128_s64.json").read_bytes())
    require(digest(root / "inputs" / "binary_128_s64.json") == manifest["source_input_sha256"]
            and digest(root / "configs" / "hgf_binary_128.json") == manifest["source_config_sha256"],
            "Canonical original dataset/config bytes changed")
    problem = hgf_binary_unitsq_fit_problem(
        np.asarray(source["y"][7], float), np.asarray(source["u"][7], float))
    require(list(problem.free_indices) == [12, 13, 14]
            and np.array_equal(problem.initial_free, np.asarray([-3., -6., 3.871201010907891], float)),
            "Original frozen free start/config changed")
    trace = []
    def observe(x):
        xx = np.asarray(x, np.float64).reshape(-1)
        value = float(problem.evaluate_free(xx))
        trace.append({"free_parameters": xx.tolist(), "objective": value})
        return value
    grad, err = ridders_gradient(observe, np.asarray(TARGET, np.float64),
                                 RiddersOptions(min_steps=10))
    mat_trace = m["actual_private_objective_evaluation_calls"]
    validate_stream(trace, TARGET, "HGFX")
    validate_stream(mat_trace, TARGET, "MATLAB")
    require(len(grad) == len(err) == 3
            and np.isfinite(grad).all() and np.isfinite(err).all(),
            "Original HGFX Ridders did not produce three finite components")
    mg = np.asarray(m["actual_matlab_ridders_gradient"], float).reshape(-1)
    me = np.asarray(m["actual_matlab_ridders_error"], float).reshape(-1)
    require(mg.shape == me.shape == (3,) and np.isfinite(mg).all()
            and np.isfinite(me).all(), "Original MATLAB Ridders did not produce finite components")
    _, old = source_check(archive, original)
    return {
        "schema": "perf01d-exploratory-original-ridders-stencil-paired-v1",
        "status": "AUTHOR_SIDE_POST_RESULT_STENCIL_DIAGNOSTIC_NOT_SCIENTIFIC_PASS"
                  if neutral["all_serialized_binary64_equal"] else "AUTHOR_SIDE_NONNEUTRAL_INSTRUMENTATION",
        "source_protocol_sha": PRESPEC_SHA,
        "source_50_run_id": SOURCE_RUN,
        "source_50_hashes": SOURCE_HASH,
        "source_original_bfgs_hashes": ORIGINAL_HASH,
        "new_matlab_trace_sha256": digest(matlab_path),
        "target_post_result_selected_from_original_50": manifest,
        "same_session_matlab_28_field_neutrality": neutral,
        "matlab_runner": m.get("runner_name"),
        "matlab_version": m.get("matlab_version"),
        "hgfx_version": metadata.version("hgfx"),
        "hgfx_trace_full_all_actual_calls": trace,
        "matlab_trace_full_all_actual_calls": mat_trace,
        "objective_call_pairing": pair_streams(trace, mat_trace),
        "new_matlab_gradient": mg.tolist(),
        "new_hgfx_gradient": grad.tolist(),
        "new_matlab_ridders_internal_error_estimate": me.tolist(),
        "new_hgfx_ridders_internal_error_estimate": err.tolist(),
        "old_matlab_gradient": old["matlab"]["gradient"],
        "old_hgfx_gradient": old["hgfx"]["gradient"],
        "old_matlab_ridders_internal_error_estimate": old["matlab"]["ridders_error"],
        "old_hgfx_ridders_internal_error_estimate": old["hgfx"]["ridders_error"],
        "gradient_same_x_component_abs_difference": np.abs(grad-mg).tolist(),
        "original_scientific_full_fit": "63/64 NONPASS",
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "timing": "NOT_RUN",
        "limitations": [
            "Target was selected after observing 50 original direct-private gradients; this exploratory sample is not prospective scientific validation.",
            "Complete actual objective call streams are retained; index-aligned pairs only compare bitwise-identical x coordinates.",
            "A single stencil difference alone does not establish causal source, optimizer branch history or scientific fit parity.",
            "Original 63/64 scientific NONPASS and all original failed source runs remain binding.",
            "No gradient acceptance threshold, benchmark timing or external scientific-review sign-off was introduced.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("prepare", "compare"), required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--matlab", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.stage == "prepare":
        data = make_manifest(args.archive, args.original)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"post_result_exploratory": True, "original_record": 6,
                          "old_science": data["original_full_scientific_fits"]}, sort_keys=True))
        return
    require(args.matlab is not None and args.output is not None, "Missing comparison paths")
    result = run_compare(args.root, args.archive, args.original, args.manifest, args.matlab)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    summary = result["objective_call_pairing"]
    print(json.dumps({"status": result["status"],
                      "hgfx_calls": summary["hgfx_call_count"],
                      "matlab_calls": summary["matlab_call_count"],
                      "identical_x_pairs": summary["index_aligned_exact_coordinate_pairs"],
                      "different_objectives_same_x": summary["index_aligned_exact_coordinate_objective_differences"],
                      "original_full_fit": result["original_scientific_full_fit"]}, sort_keys=True))
    require(result["status"] == "AUTHOR_SIDE_POST_RESULT_STENCIL_DIAGNOSTIC_NOT_SCIENTIFIC_PASS",
            "Original reference MATLAB fit outputs altered by tracing")


if __name__ == "__main__":
    main()
