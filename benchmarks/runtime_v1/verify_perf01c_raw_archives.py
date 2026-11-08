#!/usr/bin/env python3
"""Recompute PERF-01C scientific diagnostics from original authenticated raw artifacts.

The output is an author-side evidence-integrity check, NOT a scientific PASS,
independent external peer review, or permission to time MATLAB/HGFX.
Every original failure and threshold is preserved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import zipfile

from compare_fit_cohort import compare as compare_original_fits
from compare_forward7_boundary_untimed import compare as compare_forward
from compare_forward7_untimed import EXPECTED as EXPECTED_FORWARD

FIT_ARCHIVE = {
    "artifact_id": 13341288055,
    "run_id": 41863441006,
    "sha256": "45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587",
    "members": {
        "comparison.json": "97877d64f609a62b3ca10674809907ae18562321c170f9b47aebaf672f3fcede",
        "hgfx_raw.json": "6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb",
        "matlab_raw.json": "2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98",
    },
}
FORWARD_ARCHIVE = {
    "artifact_id": 13617382986,
    "run_id": 42481218455,
    "sha256": "6928272eeab342df85a833fa2ce058d713202495fb2f666bb3c7b3307cd21a95",
    "members": {
        "forward7_boundary_comparison.json": "dc859460b2f61770e9ef8ef0e173776f21a054f0ce0195f41ab66757a7e8c61f",
        "hgfx_forward7_boundary.json": "8abf2b6de3ae805365d867ce6f9101022826733ebf949c389578c50b2a132ff3",
        "matlab_forward7_boundary.json": "d8d83ee30c935f17350d0934b4f92da2a930145f01eb60470640122fc7afa639",
    },
}
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
GOOD_FIT = "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
BAD_FIT = "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"
GOOD_FORWARD = "UNFROZEN_FORWARD_DIAGNOSTIC_CONCORDANCE"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def read_original_members(source: Path, archive: dict) -> tuple[dict, str]:
    names = archive["members"]
    if source.is_file() and source.suffix.lower() == ".zip":
        # Compare raw ZIP bytes, not only GitHub artifact metadata.
        checksum = sha256(source.read_bytes())
        require(checksum == archive["sha256"], "Original artifact ZIP SHA256 mismatch")
        with zipfile.ZipFile(source) as zipped:
            filenames = zipped.namelist()
            require(len(filenames) == len(set(filenames))
                    and set(filenames) == set(names),
                    "Original artifact missing, duplicate or extra ZIP member")
            raw = {name: zipped.read(name) for name in names}
        form = "EXACT_ZIP_AND_MEMBER_SHA256"
    elif source.is_dir():
        # gh run download extracts members. Validate all original member bytes,
        # but do NOT claim the unavailable original ZIP hash was re-verified.
        filenames = [x.name for x in source.iterdir()]
        require(set(filenames) == set(names) and len(filenames) == len(set(filenames)),
                "Original extracted artifact missing/extra member")
        raw = {}
        for name in names:
            p = source / name
            require(p.is_file() and not p.is_symlink(), "Artifact member not a regular file")
            raw[name] = p.read_bytes()
        form = "EXTRACTED_MEMBERS_SHA256_ONLY_NO_ZIP_CLAIM"
    else:
        raise ValueError("Provide an authenticated original ZIP or exact extracted folder")

    for name, expected in names.items():
        require(sha256(raw[name]) == expected,
                "Original raw artifact member SHA256 mismatch: " + name)
    return {name: json.loads(data) for name, data in raw.items()}, form


def first_json_difference(lhs, rhs, path: str = "$"):
    """Locate actual tracked-versus-original result divergence, no filtering."""
    if type(lhs) is not type(rhs):
        return (path, repr(lhs)[:240], repr(rhs)[:240])
    if isinstance(lhs, dict):
        if lhs.keys() != rhs.keys():
            return (path + ".keys", sorted(lhs.keys()), sorted(rhs.keys()))
        for k in sorted(lhs):
            failure = first_json_difference(lhs[k], rhs[k], path + "." + k)
            if failure is not None:
                return failure
    elif isinstance(lhs, list):
        if len(lhs) != len(rhs):
            return (path + ".length", len(lhs), len(rhs))
        for i, (a, b) in enumerate(zip(lhs, rhs)):
            failure = first_json_difference(a, b, path + "[" + str(i) + "]")
            if failure is not None:
                return failure
    elif lhs != rhs:
        return (path, repr(lhs)[:240], repr(rhs)[:240])
    return None


def independent_trajectory_failures(hgfx_subject: dict, matlab_subject: dict,
                                    field: str) -> dict:
    """Independent scalar arithmetic, not archived or project comparator labels."""
    lhs = hgfx_subject["traj"][field]
    rhs = matlab_subject["traj"][field]
    require(len(lhs) == len(rhs) == 128,
            "Original 128-trial subject-7 trajectory changed")
    mismatches = []
    max_delta = 0.0
    for trial, (left, right) in enumerate(zip(lhs, rhs)):
        require(isinstance(left, list) and isinstance(right, list)
                and len(left) == len(right) == 3,
                "Original 3-level trialwise trajectory shape mismatch")
        for level, (a, b) in enumerate(zip(left, right)):
            require(isinstance(a, (int, float)) and isinstance(b, (int, float))
                    and math.isfinite(a) and math.isfinite(b),
                    "Non-finite raw subject-7 trajectory value")
            delta = abs(a - b)
            max_delta = max(max_delta, delta)
            # Frozen original fieldwise tolerance, not altered for the replay.
            if delta > 3e-10 + 3e-8 * abs(b):
                mismatches.append([trial, level])
    return {
        "mismatch_count": len(mismatches),
        "mismatch_indices_zero_based": mismatches,
        "max_abs_delta": max_delta,
        "rtol": 3e-8, "atol": 3e-10,
    }


def verify(root: Path, fit_source: Path, forward_source: Path) -> dict:
    fit, fit_integrity = read_original_members(fit_source, FIT_ARCHIVE)
    forward, forward_integrity = read_original_members(
        forward_source, FORWARD_ARCHIVE)

    hfit, mfit, recorded_fit = (
        fit["hgfx_raw.json"], fit["matlab_raw.json"], fit["comparison.json"]
    )
    require(mfit.get("fitModel_path", "").replace("\\", "/").endswith(
        "/reference_toolbox/core/fitModel.m"),
        "Original MATLAB fitModel resolved unexpectedly")
    require(mfit.get("hgf_binary_path", "").replace("\\", "/").endswith(
        "/reference_toolbox/_original_models/hgf_binary.m"),
        "Original MATLAB HGF resolved to a different shadowed function")
    require(hfit.get("model") == mfit.get("model") == "hgf_binary"
            and hfit.get("observation_model") == mfit.get("observation_model") ==
            "unitsq_sgm"
            and hfit.get("subjects") == mfit.get("subjects") == 64
            and hfit.get("trials") == mfit.get("trials") == 128,
            "Original full-fit model, observation, horizon or subject count differs")
    require(hfit.get("input_sha256") ==
            "6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae"
            and hfit.get("config_sha256") ==
            "2523e0438fe28ca5f6e4bdf0c8b8530fb0b3cbe5cc50a87f5b5b55dbfd56c180",
            "Frozen HGF fit dataset/config bytes not pinned")

    # Re-execute the *original unmodified comparison function* on real raw
    # 64-subject arrays, not on a tracked/archived derived summary.
    recomputed_fit = compare_original_fits(hfit, mfit)
    require(recomputed_fit == recorded_fit,
            "Raw 64-fit comparator does not reproduce archived full comparison")
    tracked_path = root / "fit_cohort_results" / "summary-41863441006.json"
    tracked = json.loads(tracked_path.read_bytes())
    # Git's derived summary is the archived original comparator PLUS three
    # additional provenance fields. They are NOT scientific differences.
    expected_provenance = {
        "github_run_id": str(FIT_ARCHIVE["run_id"]),
        "raw_evidence_location": "GitHub Actions artifact perf01-64-full-fits-41863441006",
        "raw_evidence_sha256": {
            name: FIT_ARCHIVE["members"][name]
            for name in ("hgfx_raw.json", "matlab_raw.json")
        },
    }
    require(set(tracked) == set(recomputed_fit) | set(expected_provenance),
            "Git-tracked full-fit summary has missing/extra scientific or provenance keys")
    require(all(tracked[k] == v for k, v in expected_provenance.items()),
            "Git-tracked source archive provenance fields conflict with exact raw hashes")
    tracked_science = {k: tracked[k] for k in recomputed_fit}
    if recomputed_fit != tracked_science:
        diff = first_json_difference(recomputed_fit, tracked_science)
        raise ValueError("Original Git-tracked SCIENTIFIC fields differ from raw replay. "
                         "FIRST DIFF (raw_recomputed,git_tracked)=" + repr(diff))
    require(recomputed_fit["hgfx_sha"] == HGFX_SHA
            and recomputed_fit["matlab_sha"] == MATLAB_SHA
            and recomputed_fit["classification_counts"] ==
            {GOOD_FIT: 63, BAD_FIT: 1}
            and len(recomputed_fit["cases"]) == 64,
            "Historical original 63/64 NONPASS denominator changed")
    bad = [r for r in recomputed_fit["cases"]
           if r["classification"] != GOOD_FIT]
    require(len(bad) == 1
            and bad[0]["subject_index_zero_based"] == 7
            and sorted(bad[0]["mismatched_fields"]) ==
            ["traj.mu", "traj.muhat"],
            "Wrong raw original fitting failure identity")
    require(recomputed_fit["by_prefix"][1]["numerical_output_concordant"] == 15
            and recomputed_fit["by_prefix"][2]["numerical_output_concordant"] == 63,
            "Historical 1/16/64 denominator replay differs")

    actual_spot = {}
    for field in ("mu", "muhat"):
        item = independent_trajectory_failures(
            hfit["cases"][7], mfit["cases"][7], field)
        original = recomputed_fit["cases"][7]["fields"]["traj." + field]
        require(item["mismatch_count"] == original["mismatch_count"] == 4
                and item["mismatch_indices_zero_based"][0] ==
                original["first_mismatch_index_zero_based"]
                and abs(item["max_abs_delta"] - original["max_abs_delta"]) < 1e-20,
                "Direct independent subject-7 arithmetic conflicts with original report")
        actual_spot["traj." + field] = item

    hforward, mforward, recorded_forward = (
        forward["hgfx_forward7_boundary.json"],
        forward["matlab_forward7_boundary.json"],
        forward["forward7_boundary_comparison.json"],
    )
    # Recompute all seven original forward tasks and ALL 12 full-result fields
    # using the unchanged existing repo comparator and registry/hashes.
    recomputed_forward = compare_forward(root, hforward, mforward)
    require(recomputed_forward == recorded_forward,
            "Recomputed seven-forward full result differs from archived evidence")
    require(recomputed_forward["counts"] == {GOOD_FORWARD: 7}
            and recomputed_forward["old_denominator"] == 28
            and recomputed_forward["old_pending"] == 16
            and recomputed_forward["old_blocked"] == 12
            and len(recomputed_forward["rows"]) == 7,
            "Original seven-forward scope / 28-case ledger changed")
    source_paths = {}
    for row in recomputed_forward["rows"]:
        case_id = row["case_id"]
        expected = EXPECTED_FORWARD[case_id][0]
        subdir = "perceptual" if expected == "uhgf_binary" else "_original_models"
        path = row["source_path_observed"].replace("\\", "/")
        require(path.endswith(f"/reference_toolbox/{subdir}/{expected}.m"),
                "Original active MATLAB forward source path unexpectedly shadowed")
        require(set(row["fields"]) ==
                {"inf_states", "traj.mu", "traj.sa", "traj.muhat",
                 "traj.sahat", "traj.v", "traj.w", "traj.da", "traj.ud",
                 "traj.psi", "traj.epsi", "traj.wt"},
                "Original complete forward fields missing")
        source_paths[case_id] = path

    return {
        "schema": "perf01c-direct-raw-archive-replay-v1",
        "status": "AUTHOR_SIDE_RAW_EVIDENCE_REPLAY_SUCCESS_NOT_SCIENTIFIC_ACCEPTANCE",
        "original_full_fit_artifact": FIT_ARCHIVE["artifact_id"],
        "original_full_fit_integrity": fit_integrity,
        "original_full_fit_zip_sha256": (
            FIT_ARCHIVE["sha256"] if fit_integrity == "EXACT_ZIP_AND_MEMBER_SHA256"
            else "NOT_REVERIFIED_IN_THIS_RUN"),
        "original_full_fit_member_sha256": FIT_ARCHIVE["members"],
        "forward7_artifact": FORWARD_ARCHIVE["artifact_id"],
        "forward7_integrity": forward_integrity,
        "forward7_zip_sha256": (
            FORWARD_ARCHIVE["sha256"] if forward_integrity == "EXACT_ZIP_AND_MEMBER_SHA256"
            else "NOT_REVERIFIED_IN_THIS_RUN"),
        "forward7_member_sha256": FORWARD_ARCHIVE["members"],
        "original_full_fit_subject_count": 64,
        "original_full_fit_diagnostic_concordant": 63,
        "original_full_fit_scientific_gate": "NONPASS_63_OF_64",
        "original_failed_subject_index_zero_based": 7,
        "direct_independent_subject7_trajectory_arithmetic": actual_spot,
        "old_case_denominator": 28,
        "old_review_pending": 16,
        "old_blocked": 12,
        "forward_only_full_output_diagnostic_concordant": 7,
        "forward7_original_active_matlab_paths": source_paths,
        "same_source_hgfx_sha": HGFX_SHA,
        "same_source_matlab_sha": MATLAB_SHA,
        "matlab_active_blas_workers_proved": False,
        "original_cpu_env_gate": "BLOCKED_MATLAB_MKL_ENV",
        "benchmark_performed": False,
        "performance_claim": "NOT_AUTHORIZED",
        "external_independent_reviewer_signoff": "NOT_RECEIVED",
        "perf01c": "BLOCK_FREEZE_NOT_FROZEN",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--original-fit", type=Path, required=True)
    p.add_argument("--forward7", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = verify(a.root, a.original_fit, a.forward7)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("Original raw 64/64 inspected; 63/64 NONPASS retained; 7/7 forward diagnostic;"
          " archive replay verified; PERF-01C BLOCK_FREEZE")


if __name__ == "__main__":
    main()
