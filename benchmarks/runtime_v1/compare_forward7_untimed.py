#!/usr/bin/env python3
"""PERF-01C: fail-closed comparison of seven UNTIMED forward-only outputs.

This is not the independent PERF-01C freeze, benchmark timing or 64/64 fit gate.
No failed, invalid or otherwise blocked original matrix row is reclassified.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from compare_trialwise import compare_numeric, TRAJ

SOURCE = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
ORACLE = "2437f4dc241541072722a2695ddeca7b44d83dd3"
EXPECTED = {
    "primary_forward_128": ("hgf_binary", 128),
    **{f"secondary_{m}_forward_{n}": (m, n)
       for m in ("ehgf_binary", "uhgf_binary") for n in (128, 512, 1024)},
}
GOOD = "UNFROZEN_FORWARD_DIAGNOSTIC_CONCORDANCE"
BAD = "FORWARD_CONTRACT_OR_NUMERICAL_MISMATCH"


def index(cells: list, label: str) -> dict:
    ids = [r["case_id"] for r in cells]
    if len(ids) != 7 or len(set(ids)) != 7 or set(ids) != set(EXPECTED):
        raise ValueError(f"{label}: case denominator, duplicate, or selection mismatch")
    return {r["case_id"]: r for r in cells}


def verify_registry(root: Path) -> dict:
    input_manifest = json.loads((root / "inputs_manifest.json").read_bytes())
    config_manifest = json.loads((root / "resolved_configs_manifest.json").read_bytes())
    ledger = json.loads((root / "eligibility_candidates" /
                         "candidate_v2_fullfit41863441006.json").read_bytes())
    if (len(input_manifest["cases"]) != 28 or len(config_manifest["entries"]) != 9
            or len(ledger["cases"]) != 28
            or ledger["classification_counts"].get(
                "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING") != 16
            or sum(x["classification"] != "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
                   for x in ledger["cases"]) != 12):
        raise ValueError("Original 28-case historical matrix/ledger changed")
    candidates = {c["case_id"]: c for c in ledger["cases"]}
    originals = {c["id"]: c for c in input_manifest["cases"]}
    if len(candidates) != 28 or len(originals) != 28:
        raise ValueError("Duplicate original case ID")
    configs = {(c["model"], int(c["trial_count"])): c
               for c in config_manifest["entries"]}
    if len(configs) != 9:
        raise ValueError("Duplicate original resolved config")
    verified = {}
    for case_id, (model, n) in EXPECTED.items():
        c, o = candidates[case_id], originals[case_id]
        if (c["model"], c["trials"], c["stage"], c["subjects"], c["classification"]) != (
            model, n, "forward", 1, "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
        ) or (o["model"], o["n_trials"], o["stage"]) != (model, n, "forward"):
            raise ValueError("Original case status/model/horizon changed: " + case_id)
        source = root / o["source_file"]
        cfg = configs[model, n]
        for path, recorded in ((source, o["source_sha256"]),
                               (root / cfg["config_file"], cfg["config_sha256"])):
            if hashlib.sha256(path.read_bytes()).hexdigest() != recorded:
                raise ValueError("Original source/config byte digest changed: " + str(path))
        verified[case_id] = {
            "model": model, "trials": n, "source_sha256": o["source_sha256"],
            "config_sha256": cfg["config_sha256"],
        }
    return verified


def compare(root: Path, hgfx: dict, matlab: dict) -> dict:
    if (hgfx.get("schema") != "perf01c-forward7-hgfx-untimed-v1"
            or hgfx.get("hgfx_sha") != SOURCE
            or matlab.get("schema") != "perf01c-forward7-matlab-untimed-v1"
            or matlab.get("matlab_sha") != ORACLE
            or hgfx.get("forward_case_count") != 7
            or matlab.get("forward_case_count") != 7
            or hgfx.get("original_case_denominator") != 28
            or matlab.get("original_case_denominator") != 28):
        raise ValueError("Unfrozen or unexpected source/schema/denominator")
    verified = verify_registry(root)
    hs, ms = index(hgfx["cells"], "HGFX"), index(matlab["cells"], "MATLAB")
    rows = []
    for case_id, record in verified.items():
        h, m = hs[case_id], ms[case_id]
        path = m.get("resolved_function_path", "").replace("\\", "/")
        if not path.endswith("/" + record["model"] + ".m"):
            raise ValueError("MATLAB active forward function not resolved: " + case_id)
        for row in (h, m):
            if (row.get("model") != record["model"]
                    or row.get("trials") != record["trials"]
                    or row.get("subject_index") != 0
                    or row.get("source_sha256") != record["source_sha256"]):
                raise ValueError("Source/subject/model contract changed: " + case_id)
            if set(row.get("traj", {})) != set(TRAJ):
                raise ValueError("Missing or extra trajectory field: " + case_id)
        if h.get("config_sha256") != record["config_sha256"]:
            raise ValueError("HGFX config changed: " + case_id)
        if (h.get("status") != "HGFX_UNTIMED_FORWARD_COMPLETED_MATLAB_UNVERIFIED"
                or m.get("status") != "MATLAB_UNTIMED_FORWARD_COMPLETED_HGFX_UNVERIFIED"):
            raise ValueError("Missing genuine forward-only completion: " + case_id)
        stats = {"inf_states": compare_numeric(h["inf_states"], m["inf_states"])}
        stats.update({f"traj.{f}": compare_numeric(h["traj"][f], m["traj"][f])
                      for f in TRAJ})
        # Both sources must preserve the original leading trial axis.
        for field, rec in stats.items():
            shape = rec.get("shape")
            if (not shape or shape[0] != record["trials"]
                    or (field == "inf_states" and shape != [record["trials"], 3, 4])):
                raise ValueError("Axes/shape not preserved for " + case_id + "." + field)
        passed = all(rec["status"] == "WITHIN_DIAGNOSTIC_TOLERANCE"
                     for rec in stats.values())
        rows.append({
            "case_id": case_id, "source_path_observed": path,
            "classification": GOOD if passed else BAD,
            "fields": stats,
        })
    counts = Counter(r["classification"] for r in rows)
    return {
        "schema": "perf01c-forward7-untimed-compare-v1",
        "status": "DIAGNOSTIC_ONLY_NOT_SCIENTIFIC_ACCEPTANCE_OR_BENCHMARK",
        "old_denominator": 28,
        "old_pending": 16, "old_blocked": 12,
        "seven_forward_cases": 7,
        "counts": dict(counts), "rows": rows,
        "perf01c": "BLOCK_FREEZE_NOT_FROZEN",
        "performance": "NOT_MEASURED",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--hgfx", type=Path, required=True)
    p.add_argument("--matlab", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = compare(a.input, json.loads(a.hgfx.read_bytes()),
                     json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result["counts"], sort_keys=True))
    if result["counts"].get(BAD):
        raise SystemExit("Untimed forward-only numerical mismatch; raw evidence retained")


if __name__ == "__main__":
    main()
