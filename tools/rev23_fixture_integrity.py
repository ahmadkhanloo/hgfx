#!/usr/bin/env python3
"""REV-2.3 prospective fixture integrity preflight (no model/timing execution).

Validate a candidate input manifest; this tool never generates, repairs,
resamples, selects, or rewrites scientific inputs. A successful exit does NOT
authorize measurement or establish scientific parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROWS = {
    "F128": (128, 1), "F1024": (1024, 1),
    "F8192": (8192, 1), "F65536": (65536, 1),
    "S128": (128, 1), "S512": (512, 1),
    "B1": (256, 1), "B32": (256, 32),
    "B256": (256, 256), "B1024": (256, 1024),
    "D08": (614, 1),
}
ARRAY_KEYS = ("inputs", "responses")
FILE_FIELDS = ("config", "start", "inputs", "responses")
EXPECTED_RELEASE = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
EXPECTED_ORACLE = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_file(root: Path, rel: object) -> Path:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError("file must have a nonempty relative path")
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f"file missing or escapes manifest directory: {rel}")
    return target


def check(manifest_file: Path) -> dict:
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    errors = []
    if manifest.get("protocol_id") != "compstat-rev23-performance-1":
        errors.append("wrong protocol_id")
    if manifest.get("hgfx_source_commit") != EXPECTED_RELEASE:
        errors.append("unverified released HGFX source commit")
    if manifest.get("matlab_source_commit") != EXPECTED_ORACLE:
        errors.append("wrong frozen MATLAB source commit")
    rows = manifest.get("workloads")
    if not isinstance(rows, dict):
        rows = {}
        errors.append("workloads must be an object keyed by the original 11 IDs")
    if set(rows) != set(ROWS):
        errors.append(f"workload IDs mismatch: missing={sorted(set(ROWS)-set(rows))}, "
                      f"extra={sorted(set(rows)-set(ROWS))}")
    root = manifest_file.resolve().parent
    for ident, (trials, subjects) in ROWS.items():
        w = rows.get(ident)
        if not isinstance(w, dict):
            continue
        if w.get("trials") != trials or w.get("subjects") != subjects:
            errors.append(f"{ident}: immutable dimensions changed")
        if not w.get("model") or not w.get("observation"):
            errors.append(f"{ident}: missing explicit model/observation")
        if ident.startswith("S") and (
            w.get("model") != "hgf_binary" or w.get("observation") != "unitsq_sgm"
        ):
            errors.append(f"{ident}: must use original binary HGF/unitsq fit scope")
        if ident == "D08" and (
            w.get("model") != "uhgf" or w.get("observation") != "gaussian_obs"
        ):
            errors.append("D08: original model/observation changed")
        if not w.get("provenance") or not w.get("selection_policy"):
            errors.append(f"{ident}: source provenance/selection policy missing")
        for field in FILE_FIELDS:
            item = w.get(field)
            if not isinstance(item, dict):
                errors.append(f"{ident}: missing {field} file and SHA256")
                continue
            try:
                source = safe_file(root, item.get("path"))
                actual = sha256(source)
                if item.get("sha256") != actual:
                    raise ValueError(f"sha256 mismatch, actual {actual}")
                if field in ARRAY_KEYS:
                    if source.suffix != ".npy":
                        raise ValueError("arrays must be serialized as .npy")
                    with source.open("rb") as stream:
                        arr = np.load(stream, allow_pickle=False)
                    shape = (trials,) if subjects == 1 else (subjects, trials)
                    # Explicit shape/dtype prevents silent flatten/recast/padding.
                    if not isinstance(arr, np.ndarray) or arr.shape != shape or arr.dtype != np.dtype("<f8"):
                        raise ValueError(f"array shape/dtype invalid; expected {shape}/float64")
                elif field == "config" and source.suffix != ".json":
                    raise ValueError("config must be a JSON file")
                elif field == "start" and source.suffix != ".npy":
                    raise ValueError("start must be an immutable .npy file")
            except (ValueError, OSError, TypeError, EOFError) as exc:
                errors.append(f"{ident}.{field}: {exc}")
    return {
        "schema": "rev23_fixture_integrity_preflight_v1",
        "status": "SOURCE_ONLY_CHECK_PASS" if not errors else "BLOCKED_FIXTURE_INTEGRITY",
        "rows_checked": len(ROWS),
        "errors": errors,
        "scientific_parity": "NOT_EVALUATED",
        "independent_review": "NOT_EVALUATED",
        "benchmark_authorized": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path, help="existing candidate manifest JSON")
    p.add_argument("--report", type=Path, help="optional JSON output path")
    args = p.parse_args()
    try:
        result = check(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"status": "BLOCKED_FIXTURE_INTEGRITY", "errors": [str(exc)],
                  "scientific_parity": "NOT_EVALUATED", "benchmark_authorized": False}
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["status"] == "SOURCE_ONLY_CHECK_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
