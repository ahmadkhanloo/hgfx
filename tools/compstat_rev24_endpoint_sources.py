#!/usr/bin/env python3
"""REV-2.4 Panel E original-archive SHA preflight, WITHOUT endpoint science.

Reads only archived ZIP identity and the two cohort raw-file hashes. Output
contains no raw participant records, endpoints, fitted values or model claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

SOURCES = {
    "d02": {
        "run_id": 34823572071,
        "artifact_id": 10339454535,
        "zip_sha256": "78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b",
        "expires_at": "2026-12-13T08:36:19Z",
        "model": "ehgf_binary + unitsq_sgm",
        "expected_files": {},
    },
    "d08": {
        "run_id": 34823572192,
        "artifact_id": 10339403480,
        "zip_sha256": "c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de",
        "expires_at": "2026-12-13T08:36:19Z",
        "model": "uhgf + gaussian_obs",
        "expected_files": {},
    },
    "cohort64": {
        "run_id": 41863441006,
        "artifact_id": 13341288055,
        "zip_sha256": "45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587",
        "expires_at": "2027-02-02T16:01:19Z",
        "model": "hgf_binary + unitsq_sgm",
        "expected_files": {
            "hgfx_raw.json": "6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb",
            "matlab_raw.json": "2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98",
        },
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit_archive(path: Path, name: str, source: dict) -> dict:
    """Verify bytes and required inner files; never expose their contents."""
    require(name in SOURCES, "Unknown original Panel E source identity")
    require(path.is_file(), f"Missing {name} original ZIP")
    data = path.read_bytes()
    require(sha256_bytes(data) == source["zip_sha256"],
            f"{name}: original archive SHA256 mismatch")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = [i for i in archive.infolist() if not i.is_dir()]
            require(bool(members), f"{name}: empty archived evidence")
            require(archive.testzip() is None, f"{name}: corrupt ZIP member")
            verified = {}
            for basename, expected in source["expected_files"].items():
                matching = [m for m in members
                            if Path(m.filename).name == basename]
                require(len(matching) == 1,
                        f"{name}: missing or duplicated {basename}")
                actual = sha256_bytes(archive.read(matching[0]))
                require(actual == expected, f"{name}: {basename} SHA256 mismatch")
                verified[basename] = actual
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError(f"{name}: invalid original ZIP") from exc
    return {
        "source": name,
        "run_id": source["run_id"],
        "artifact_id": source["artifact_id"],
        "zip_sha256": source["zip_sha256"],
        "expected_model": source["model"],
        "verified_inner_sha256": verified,
        "member_count": len(members),
        "archive_identity": "SHA256_VERIFIED",
        "endpoint_vector_coverage": "NOT_EVALUATED",
        "objective_cross_evaluation": "NOT_RUN",
    }


def audit_sources(paths: dict[str, Path]) -> dict:
    require(set(paths) == set(SOURCES),
            "Original D02, D08 and 64-cohort are all required")
    return {
        "protocol": "compstat-rev2-4-objective-cross-eval-v1",
        "panel": "E",
        "status": "ARCHIVE_IDENTITIES_ONLY_NOT_OBJECTIVE_PARITY",
        "sources": [audit_archive(paths[k], k, SOURCES[k]) for k in SOURCES],
        "original_endpoints_extracted": False,
        "cohort_64_subject_coverage_checked": False,
        "matlab_oracle_executed": False,
        "hgfx_v1_objective_executed": False,
        "scientific_gate": "NOT_ASSESSED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d02", type=Path, required=True)
    parser.add_argument("--d08", type=Path, required=True)
    parser.add_argument("--cohort64", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Refusing to overwrite original preflight")
    result = audit_sources({"d02": args.d02, "d08": args.d08,
                            "cohort64": args.cohort64})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "archive_count": len(result["sources"]),
                      "scientific_gate": result["scientific_gate"],
                      "output_sha256": sha256_bytes(args.output.read_bytes())},
                     sort_keys=True))


if __name__ == "__main__":
    main()
