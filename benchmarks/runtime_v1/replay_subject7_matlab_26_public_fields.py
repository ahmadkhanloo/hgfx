#!/usr/bin/env python3
"""Archive-only SciPy verification of ALL 26 native/intercepted MATLAB fields.

This separately implemented parser inspects archived MATLAB -v7 field values;
it does NOT delegate to the MATLAB producer's aggregate isequaln boolean.
It is author-side evidence and cannot sign any scientific performance gate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab import mat_struct

OPT = ("init", "final", "H", "Sigma", "Corr", "trialLogLlsplit",
       "negLl", "negLj", "LME", "decompLME", "AIC", "BIC", "yhat", "res", "resAC")
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CANDIDATE_SHA = "b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144"
SCHEMA = "perf01d-26-matlab-public-stable-fields-raw-v1"


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def matlab_text(value):
    """Decode a MATLAB -v7 character array or a scalar Python string."""
    if isinstance(value, str):
        return value
    if isinstance(value, np.ndarray) and value.dtype.kind in "US":
        return "".join(str(s) for s in value.flat)
    if isinstance(value, np.ndarray) and value.size == 1:
        return matlab_text(value.item())
    raise ValueError("Not a MATLAB scalar string/character array")


def matlab_strings(value):
    if isinstance(value, np.ndarray):
        return [matlab_text(x) for x in value.flat]
    raise ValueError("MATLAB cell string field list must be an array")


def only_struct(array):
    require(isinstance(array, np.ndarray) and array.shape == (1, 1)
            and array.dtype.kind == "O" and isinstance(array[0, 0], mat_struct),
            "Expected exact 1x1 MATLAB v7 struct")
    return array[0, 0]


def scalar(value):
    require(isinstance(value, np.ndarray) and value.size == 1,
            "Expected scalar MATLAB numeric/logical field")
    return value.item()


def compare_exact(a, b, path="field"):
    """First pairwise mismatch, recursively; shape/dtype and NaN parity strict.

    Numeric values use exact equality with NaNs at corresponding positions,
    as MATLAB's isequaln. No atol/rtol or mask. Integral/logical equality
    includes dtype and dimensions. MATLAB struct field names must match.
    """
    if isinstance(a, mat_struct) or isinstance(b, mat_struct):
        if not isinstance(a, mat_struct) or not isinstance(b, mat_struct):
            return path + ": MATLAB struct type mismatch"
        na, nb = list(a._fieldnames), list(b._fieldnames)
        if na != nb:
            return path + ": nested MATLAB struct keys mismatch"
        for k in na:
            problem = compare_exact(getattr(a, k), getattr(b, k), path + "." + k)
            if problem:
                return problem
        return None

    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            return path + ": MATLAB array type mismatch"
        if a.shape != b.shape:
            return path + ": MATLAB array shape mismatch"
        if a.dtype != b.dtype:
            return path + ": MATLAB array dtype mismatch"
        if a.dtype.kind == "O":
            for index in np.ndindex(a.shape):
                problem = compare_exact(a[index], b[index], path + str(index))
                if problem:
                    return problem
            return None
        if a.dtype.kind in "fc":
            same = np.array_equal(a, b, equal_nan=True)
        elif a.dtype.kind in "biuUS":
            same = np.array_equal(a, b)
        else:
            return path + ": unsupported MATLAB array dtype " + str(a.dtype)
        return None if same else path + ": exact value or NaN-position mismatch"

    if type(a) is not type(b):
        return path + ": Python scalar type mismatch"
    if isinstance(a, (int, bool, str, np.integer, np.bool_)):
        return None if a == b else path + ": scalar mismatch"
    if isinstance(a, (float, complex, np.floating, np.complexfloating)):
        if (math.isnan(a.real) and math.isnan(b.real)
                and math.isnan(a.imag) and math.isnan(b.imag)):
            return None
        try:
            if np.array_equal(np.asarray([a]), np.asarray([b]), equal_nan=True):
                return None
        except (ValueError, TypeError):
            pass
        return path + ": exact floating/NaN scalar mismatch"
    return path + ": unsupported MATLAB scalar type " + type(a).__name__


def read_public(path):
    raw_bytes = Path(path).read_bytes()
    data = loadmat(path, struct_as_record=False, squeeze_me=False,
                   chars_as_strings=True, mat_dtype=True)
    require(set(data).issuperset({"native_public", "instrumented_public", "metadata"}),
            "Incomplete MATLAB raw .mat member")
    return (only_struct(data["native_public"]),
            only_struct(data["instrumented_public"]),
            only_struct(data["metadata"]), sha256(raw_bytes).hexdigest())


def check_original_public_fit(original):
    require(original.get("subject_count") == 64
            and original.get("classification_counts") == {
                "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
                "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1}
            and original["cases"][7]["mismatched_fields"] == ["traj.mu", "traj.muhat"]
            and all(original["cases"][7]["fields"][k]["mismatch_count"] == 4
                    for k in ("traj.mu", "traj.muhat")),
            "Frozen original 63/64 public fitting NONPASS changed")


def replay(native, instrumented, metadata, private, original, raw_hash):
    """Fail closed on case/config/provenance; preserve all fieldwise results."""
    check_original_public_fit(original)
    m = metadata
    require(matlab_text(m.schema) == SCHEMA
            and matlab_text(m.frozen_hgfx_sha) == HGFX_SHA
            and matlab_text(m.frozen_matlab_sha) == MATLAB_SHA
            and matlab_text(m.original_source_candidate_sha256) == CANDIDATE_SHA
            and matlab_text(m.original_64_public_science) == "63/64 SCIENTIFIC NONPASS"
            and matlab_text(m.independent_scientific_review) == "NOT_RECEIVED"
            and matlab_text(m.perf01c) == "NOT_FROZEN"
            and matlab_text(m.performance_timing) == "NOT_RUN"
            and scalar(m.subject_index_zero_based) == 7
            and scalar(m.original_trial_count) == 128
            and scalar(m.field_count) == 26
            and scalar(m.hook_count) == 1
            and bool(scalar(m.original_optimizer_delegated)),
            "MATLAB raw archive case/commit/science metadata changed")
    run_id, commit = matlab_text(m.github_run_id), matlab_text(m.tested_sha)
    require(run_id and len(commit) == 40
            and private.get("tested_sha") == commit
            and str(private.get("github_run_id")) == run_id
            and private.get("frozen_hgfx_sha") == HGFX_SHA
            and private.get("frozen_matlab_sha") == MATLAB_SHA
            and private.get("source_original_candidate_sha256") == CANDIDATE_SHA
            and private.get("original_science") == "63/64 SCIENTIFIC NONPASS"
            and private.get("hook_count") == 1
            and private.get("original_optimizer_delegated") is True
            and private.get("compared_stable_field_count") == 26,
            "Paired real private MATLAB report/run mismatch")

    optim = matlab_strings(m.optim_fields)
    traj = matlab_strings(m.traj_fields)
    require(tuple(optim) == OPT and len(traj) == 11 and len(set(traj)) == 11,
            "Original 15+11 public stable field selection changed")
    per_field = []
    for category, fields in (("optim", OPT), ("traj", traj)):
        left_group = getattr(native, category)
        right_group = getattr(instrumented, category)
        require(isinstance(left_group, mat_struct) and isinstance(right_group, mat_struct),
                "Missing MATLAB raw " + category + " struct")
        require(set(left_group._fieldnames) == set(fields)
                and set(right_group._fieldnames) == set(fields),
                "A native/intercepted raw " + category + " field was omitted or added")
        for field in fields:
            lhs, rhs = getattr(left_group, field), getattr(right_group, field)
            issue = compare_exact(lhs, rhs, category + "." + field)
            per_field.append({
                "field": category + "." + field,
                "equal_nan_exact": issue is None,
                "first_difference": issue,
                "native_type": type(lhs).__name__,
                "intercepted_type": type(rhs).__name__,
                "native_shape": list(lhs.shape) if isinstance(lhs, np.ndarray) else None,
                "intercepted_shape": list(rhs.shape) if isinstance(rhs, np.ndarray) else None,
            })
    equal = len(per_field) == 26 and all(x["equal_nan_exact"] for x in per_field)
    producer = bool(scalar(m.native_instrumented_26_field_equality_producer))
    require(private.get("native_instrumented_stable_fields_identical") is producer,
            "Original MATLAB producer neutrality flag differs from raw archive")
    return {
        "schema": "perf01d-public-26-raw-field-archive-replay-v1",
        "status": ("AUTHOR_SIDE_PUBLIC_26_FIELD_RAW_REPLAY_IDENTICAL" if equal
                   else "AUTHOR_SIDE_PUBLIC_26_FIELD_RAW_REPLAY_NONIDENTICAL"),
        "raw_mat_sha256": raw_hash,
        "source_matlab_run_id": run_id,
        "source_matlab_commit": commit,
        "source_candidate_sha256": CANDIDATE_SHA,
        "original_scientific_fitting": "63/64 SCIENTIFIC NONPASS",
        "native_and_instrumented_fieldwise_exact": equal,
        "producer_neutrality_flag": producer,
        "compared_fields_count": len(per_field),
        "field_results": per_field,
        "real_private_objective_sample_count": len(private.get("calls", [])),
        "actual_private_x6_objective": private.get("calls", [{}])[0].get("private_objective"),
        "original_2026_11_07_private_x6_objective": 108.28848680066957,
        "private_x6_matches_historical_value": (
            private.get("calls", [{}])[0].get("private_objective")
            == 108.28848680066957),
        "matlab_release_version": matlab_text(m.matlab_version),
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "performance_timing": "NOT_RUN",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mat", type=Path, required=True)
    p.add_argument("--private", type=Path, required=True)
    p.add_argument("--original-fit", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    native, intercepted, metadata, digest = read_public(args.mat)
    private = json.loads(args.private.read_bytes())
    original = json.loads(args.original_fit.read_bytes())
    report = replay(native, intercepted, metadata, private, original, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "field_results"}, sort_keys=True))
    require(report["native_and_instrumented_fieldwise_exact"],
            "26-field archive independently disagrees with native fit")
    require(report["producer_neutrality_flag"],
            "Original MATLAB aggregate neutrality assertion did not hold")


if __name__ == "__main__":
    main()
