#!/usr/bin/env python3
"""Build the HGFX v1 evidence-freeze manifest without rewriting historical evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN_MATLAB_REFERENCE = "2437f4dc241541072722a2695ddeca7b44d83dd3"
INDEX_PATH = ROOT / "reference" / "validation" / "v1_release" / "evidence_index.json"
GPU_PATH = ROOT / "gpu_validation_results" / "m18_s9_physical_gpu_revalidation.json"

REQUIRED_FILES = (
    "docs/planning/MILESTONES.md",
    "docs/planning/V1_RELEASE_GATE.md",
    "docs/validation/V1_EVIDENCE_INDEX.md",
    "docs/validation/M18_S9_CPU_EVIDENCE.md",
    "docs/validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md",
    "reference/validation/v1_release/evidence_index.json",
    "reference/validation/m18_d02_reference_limitation/decision.json",
    "reference/validation/m18_d08_reference_limitation/decision.json",
    "reference/validation/m18_s7_reference_limitation/decision.json",
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CITATION.cff",
    "pyproject.toml",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def physical_gpu_state() -> dict:
    if not GPU_PATH.is_file():
        return {
            "present": False,
            "pass": False,
            "classification": "PHYSICAL_GPU_REVALIDATION_REQUIRED",
            "path": str(GPU_PATH.relative_to(ROOT)),
        }
    data = json.loads(GPU_PATH.read_text(encoding="utf-8"))
    physical = data.get("physical_gpu", {})
    provenance = data.get("physical_gpu_evidence", {})
    passed = bool(
        data.get("gate_pass") is True
        and data.get("classification") == "PASS_S9_ROBUSTNESS_BACKEND"
        and physical.get("classification") == "PASS_PHYSICAL_GPU_APPLICABILITY"
        and physical.get("pass") is True
        and provenance.get("hardware_eligibility_pass") is True
    )
    return {
        "present": True,
        "pass": passed,
        "classification": data.get("classification"),
        "physical_gpu_classification": physical.get("classification"),
        "hardware_requirement": provenance.get("hardware_requirement"),
        "hardware_eligibility_pass": provenance.get("hardware_eligibility_pass"),
        "nvidia_smi_list": provenance.get("nvidia_smi_list"),
        "source_commit": data.get("source_commit"),
        "sha256": sha256(GPU_PATH),
        "path": str(GPU_PATH.relative_to(ROOT)),
    }


def main(mode: str, output: str) -> int:
    if not INDEX_PATH.is_file():
        raise SystemExit("release evidence index is missing")

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    if index.get("frozen_matlab_reference") != FROZEN_MATLAB_REFERENCE:
        failures.append("wrong frozen MATLAB reference")

    evidence = {item.get("id"): item for item in index.get("evidence", [])}
    if evidence.get("S10_RELEASE_READINESS", {}).get("classification") != "PASS":
        failures.append("S10 release-readiness is not PASS")
    if evidence.get("S9_CPU_BACKEND", {}).get("classification") != "PASS_CPU_BACKEND_EQUIVALENCE":
        failures.append("S9 CPU backend evidence is not PASS_CPU_BACKEND_EQUIVALENCE")

    files: list[dict] = []
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing release evidence file: {relative}")
            continue
        files.append({"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size})

    gpu = physical_gpu_state()
    blockers = list(index.get("active_blockers", []))
    allowed_preflight = {
        "S9 physical NVIDIA GPU revalidation",
        "M19 evidence freeze",
        "M20 v1.0 candidate gate",
    }
    unexpected = sorted(set(blockers) - allowed_preflight)
    if unexpected:
        failures.append(f"unexpected active blockers: {unexpected}")

    if mode == "finalize":
        if not gpu["pass"]:
            failures.append("physical NVIDIA GPU S9 evidence has not passed")
        allowed_final = {"M19 evidence freeze", "M20 v1.0 candidate gate"}
        unexpected_final = sorted(set(blockers) - allowed_final)
        if unexpected_final:
            failures.append(f"pre-M19 blockers still active: {unexpected_final}")

    status = "FROZEN" if mode == "finalize" and not failures else (
        "PREPARED" if gpu["pass"] and not failures else "PREPARED_BLOCKED_GPU"
    )

    payload = {
        "schema_version": 1,
        "milestone": "M19",
        "mode": mode,
        "status": status,
        "source_commit": git_head(),
        "frozen_matlab_reference": FROZEN_MATLAB_REFERENCE,
        "release_branch": index.get("release_branch"),
        "numerical_source_commit": index.get("numerical_source_commit"),
        "files": sorted(files, key=lambda item: item["path"]),
        "external_evidence": index.get("evidence", []),
        "physical_gpu": gpu,
        "active_blockers_at_manifest_time": blockers,
        "failures": failures,
        "integrity": {
            "historical_failures_rewritten": False,
            "thresholds_changed_for_freeze": False,
            "seeds_or_datasets_changed_for_freeze": False,
            "validation_grid_changed_for_freeze": False,
            "gpu_model_constrained": False,
        },
    }

    output_path = Path(output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failures": failures, "output": str(output_path)}, indent=2))

    if failures:
        return 2
    if mode == "finalize" and status != "FROZEN":
        return 3
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "finalize"), default="preflight")
    parser.add_argument(
        "--output",
        default="reference/validation/v1_release/evidence_manifest.json",
    )
    args = parser.parse_args()
    raise SystemExit(main(args.mode, args.output))
