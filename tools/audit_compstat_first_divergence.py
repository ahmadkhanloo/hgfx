#!/usr/bin/env python3
"""REV-1.4: SHA-guarded source-only audit; not objective or first-cause parity."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

PROTOCOL = "compstat-rev-1.4-source-audit-v1"
P3_PROTOCOL = "m18c2-trial-horizon-identifiability-1"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
ATOL, RTOL = 3e-10, 3e-8
ARCHIVES = {
    "p3_512": ("35effd1aa5f46afa874042d0df9b15389ae5eb2fa0294482d7ffc52223c1d940", "hgf-t512-s035"),
    "p3_1024": ("e6f6e05417f3fc7ec1f0fc2907ff026a704aebeff59651402adbb050ddc24e66", "hgf-t1024-s035"),
    "fullfit": ("45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587", ""),
}
FIT_MEMBERS = {
    "comparison.json": "97877d64f609a62b3ca10674809907ae18562321c170f9b47aebaf672f3fcede",
    "hgfx_raw.json": "6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb",
    "matlab_raw.json": "2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98",
}
FIRST_CELLS = {
    "mu": [[83, 1], [108, 1], [116, 1], [126, 1]],
    "muhat": [[84, 1], [109, 1], [117, 1], [127, 1]],
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def canonical_hash(doc: dict, excluded: tuple[str, ...] = ()) -> str:
    filtered = {k: v for k, v in doc.items() if k not in excluded}
    return sha256(json.dumps(filtered, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())

def archive_files(path: Path, expected_sha: str) -> tuple[dict[str, bytes], dict[str, str]]:
    require(path.is_file(), f"Missing original artifact ZIP: {path}")
    require(sha256(path.read_bytes()) == expected_sha, f"Original artifact ZIP SHA-256 mismatch: {path}")
    with ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate archive entries")
        require(all(name and not name.startswith("/") and ".." not in Path(name).parts for name in names),
                "Unsafe original archive member name")
        basenames = [Path(name).name for name in names]
        require(len(basenames) == len(set(basenames)), "Duplicate archive member basename")
        data = {Path(name).name: archive.read(name) for name in names if not name.endswith("/")}
    return data, {name: sha256(value) for name, value in data.items()}

def decode_ieee(value):
    """MATLAB numeric scalars may be encoded in hgfx_json_ieee wrappers."""
    if isinstance(value, dict) and value.get("hgfx_numeric") == "ieee-strings-v1":
        value = value.get("data", [])
    while isinstance(value, list) and len(value) == 1:
        value = value[0]
    if isinstance(value, (list, dict)) or value is None:
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return float(x) if math.isfinite(x) else ("-Inf" if x < 0 else "+Inf" if x > 0 else "NaN")

def audit_p3(path: Path, horizon: int) -> dict:
    label = f"p3_{horizon}"
    digest, stem = ARCHIVES[label]
    members, member_sha = archive_files(path, digest)
    expected = {f"{stem}-{suffix}.json" for suffix in ("manifest", "matlab", "comparison")}
    require(set(members) == expected, f"Original {label} members incomplete or unexpected")
    manifest = json.loads(members[f"{stem}-manifest.json"])
    matlab = json.loads(members[f"{stem}-matlab.json"])
    paired = json.loads(members[f"{stem}-comparison.json"])
    require(manifest.get("protocol") == matlab.get("protocol") == paired.get("protocol") == P3_PROTOCOL,
            "Original P3 protocol drift")
    require(manifest.get("reference_commit") == matlab.get("reference_commit") == MATLAB_SHA,
            "Original MATLAB source mismatch")
    require(manifest.get("shard", {}).get("model") == "hgf_binary" and
            manifest["shard"]["trial_count"] == horizon and
            manifest["shard"]["truth_scale"] == 0.35, "Original P3 wrong stratum")
    require(canonical_hash(manifest, ("shard_sha256",)) == manifest["shard_sha256"],
            "Original P3 shard content/hash mismatch")
    require(matlab.get("input_shard_sha256") == paired.get("input_shard_sha256") == manifest["shard_sha256"],
            "Original paired P3 shard hash mismatch")
    case_map = {c["case_id"]: c for c in manifest["parameter_cases"]}
    m_map = {c["case_id"]: c for c in matlab["parameter_results"]}
    c_map = {c["case_id"]: c for c in paired["parameter_results"]}
    require(len(case_map) == len(manifest["parameter_cases"]) and
            len(m_map) == len(matlab["parameter_results"]) and
            len(c_map) == len(paired["parameter_results"]), "Duplicated original P3 case")
    rows = []
    for rep in (0, 4):
        case_id = f"PR-hgf_binary-T{horizon}-S0.35-R{rep}"
        require(case_id in case_map and case_id in m_map and case_id in c_map,
                f"Missing original preregistered case: {case_id}")
        case, ref, hgfx = case_map[case_id], m_map[case_id], c_map[case_id]
        seed = 18018 + 3500 + 100 * horizon + rep
        require(case["model"] == "hgf_binary" and case["seed"] == seed and
                case["replicate"] == rep and case["trial_count"] == horizon and
                case["truth_scale"] == 0.35, f"Case identity changed: {case_id}")
        require(canonical_hash(case, ("case_id", "case_sha256")) == case["case_sha256"],
                f"Original case SHA-256 invalid: {case_id}")
        require(ref.get("case_sha256") == hgfx.get("case_sha256") == case["case_sha256"],
                f"MATLAB/HGFX original case digest mismatch: {case_id}")
        valid_sim = bool(case["simulation_success"])
        require((len(case["y"]) == horizon) if valid_sim else len(case["y"]) == 0,
                f"Simulation payload does not match original status: {case_id}")
        ref_fit = hgfx["matlab"]
        target_fit = hgfx["hgfx"]
        require(bool(ref_fit.get("success")) == bool(ref.get("success")), "Original MATLAB status disagrees")
        rows.append({
            "case_id": case_id, "seed": seed, "case_sha256": case["case_sha256"],
            "simulation_success_original": valid_sim, "responses_present": bool(case["y"]),
            "matlab_fit_success_original": bool(ref.get("success")),
            "hgfx_fit_success_original": bool(target_fit.get("success")),
            "matlab_negLj_original": decode_ieee(ref.get("negLj")),
            "hgfx_negLj_original": decode_ieee(target_fit.get("negLj")),
            "initial_free_same_vector_verified": (
                ref_fit.get("initial_free") == target_fit.get("initial_free")
                and bool(ref_fit.get("initial_free"))),
            "same_vector_matlab_hgfx_objective_replay": "NOT_EXECUTED_SOURCE_ONLY",
            "first_divergent_trial_level_intermediate": "NOT_IN_ARCHIVED_P3_FIT_SUMMARY",
        })
    return {
        "archive_zip_sha256": digest, "member_sha256": member_sha,
        "input_shard_sha256": manifest["shard_sha256"],
        "historical_P3_gate": "FAIL_INSUFFICIENT_REFERENCE_EVIDENCE_UNCHANGED",
        "cases": rows,
    }

def mismatches(hgfx: list, matlab: list) -> dict:
    require(len(hgfx) == len(matlab) == 128, "Subject-7 original horizon is not 128")
    failures = []
    first_nonzero = None
    max_delta = 0.0
    for trial, (a_row, b_row) in enumerate(zip(hgfx, matlab)):
        require(len(a_row) == len(b_row) == 3, "Subject-7 wrong level count")
        for level, (a, b) in enumerate(zip(a_row, b_row)):
            require(isinstance(a, (int, float)) and isinstance(b, (int, float)) and
                    math.isfinite(a) and math.isfinite(b), "Nonfinite original subject-7 trajectory")
            delta, allowed = abs(a-b), ATOL + RTOL * abs(b)
            max_delta = max(delta, max_delta)
            if delta != 0 and first_nonzero is None:
                first_nonzero = {"trial_zero_based": trial, "level_zero_based": level,
                                 "hgfx": a, "matlab": b, "abs_diff": delta, "allowed": allowed}
            if delta > allowed:
                failures.append({"trial_zero_based": trial, "level_zero_based": level,
                                 "hgfx": a, "matlab": b, "abs_diff": delta, "allowed": allowed})
    return {
        "first_nonzero_difference": first_nonzero,
        "first_outside_existing_gate": failures[0] if failures else None,
        "outside_gate_count": len(failures),
        "outside_gate_cells_zero_based": [[f["trial_zero_based"], f["level_zero_based"]] for f in failures],
        "max_abs_diff": max_delta,
    }

def audit_fullfit(path: Path) -> dict:
    expected_sha, _ = ARCHIVES["fullfit"]
    members, digests = archive_files(path, expected_sha)
    require(set(members) == set(FIT_MEMBERS), "Original full-64 archive members changed")
    require(digests == FIT_MEMBERS, "Original original full-fit member SHA-256 mismatch")
    hgfx, matlab, comparison = (json.loads(members[n]) for n in
                                ("hgfx_raw.json", "matlab_raw.json", "comparison.json"))
    require(hgfx.get("model") == matlab.get("model") == "hgf_binary" and
            hgfx.get("observation_model") == matlab.get("observation_model") == "unitsq_sgm" and
            hgfx.get("subjects") == matlab.get("subjects") == 64 and
            hgfx.get("trials") == matlab.get("trials") == 128, "Original full-fit contract drift")
    require(len(hgfx["cases"]) == len(matlab["cases"]) == 64, "Original full fit missing subjects")
    require(comparison["classification_counts"] == {
        "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
        "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1,
    }, "Historical 63/64 result altered")
    require(comparison["cases"][7]["subject_index_zero_based"] == 7 and
            set(comparison["cases"][7]["mismatched_fields"]) == {"traj.mu", "traj.muhat"},
            "Original failing subject changed")
    require(matlab.get("fitModel_path", "").replace(chr(92), "/").endswith(
        "/reference_toolbox/core/fitModel.m"), "Wrong original MATLAB fitModel source")
    require(matlab.get("hgf_binary_path", "").replace(chr(92), "/").endswith(
        "/reference_toolbox/_original_models/hgf_binary.m"), "Wrong original MATLAB HGF source")
    fields = {}
    for field in ("mu", "muhat"):
        row = mismatches(hgfx["cases"][7]["traj"][field], matlab["cases"][7]["traj"][field])
        require(row["outside_gate_cells_zero_based"] == FIRST_CELLS[field],
                f"Original subject-7 failure cells changed in {field}")
        require(row["outside_gate_count"] == 4, "Subject-7 mismatch count drift")
        fields["traj." + field] = row
    return {
        "archive_zip_sha256": expected_sha, "member_sha256": digests,
        "original_subject_count": 64, "subject_index_zero_based": 7,
        "existing_gate": {"atol": ATOL, "rtol": RTOL},
        "level_zero_based": 1, "first_observed_exceedance_field": "traj.mu",
        "fields": fields, "first_causal_intermediate": "UNAVAILABLE_IN_ORIGINAL_ARCHIVE",
        "original_scientific_result": "NONPASS_63_OF_64_UNCHANGED",
    }

def run(p3_512: Path, p3_1024: Path, fullfit: Path) -> dict:
    p3_a, p3_b, subject = audit_p3(p3_512, 512), audit_p3(p3_1024, 1024), audit_fullfit(fullfit)
    require(len(p3_a["cases"]) + len(p3_b["cases"]) == 4, "Unexpected P3 case count")
    return {
        "protocol": PROTOCOL, "reference_commit": MATLAB_SHA, "released_hgfx_sha": HGFX_SHA,
        "scope": "FOUR_P3_CASES_AND_SUBJECT_7_ONLY",
        "original_p3_artifacts": [10519038480, 10519860062],
        "original_subject7_artifact": 13341288055,
        "p3": [p3_a, p3_b], "subject7": subject,
        "audit_class": "ORIGINAL_SOURCE_INTEGRITY_AND_FIRST_OBSERVED_OUTPUT_EXCEEDANCE_ONLY",
        "rev14_status": "IN_PROGRESS_NOT_TERMINAL",
        "unresolved": [
            "Four P3 cases still need same-vector MATLAB/HGFX objective and intermediate-state comparison",
            "Subject 7 first causal intermediate and same-start objective comparison not proved",
        ],
        "historical_m18_and_p3_fail_preserved": True,
        "perf01c_gate": "BLOCK_FREEZE_NOT_FROZEN",
    }

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--p3-512", type=Path, required=True)
    p.add_argument("--p3-1024", type=Path, required=True)
    p.add_argument("--fullfit", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.p3_512, args.p3_1024, args.fullfit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "rev14_status": result["rev14_status"],
        "p3_case_ids": [v["case_id"] for group in result["p3"] for v in group["cases"]],
        "subject7_first_mu_gate_failure": result["subject7"]["fields"]["traj.mu"]["first_outside_existing_gate"],
        "source_digest": sha256(args.output.read_bytes()),
    }, sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
