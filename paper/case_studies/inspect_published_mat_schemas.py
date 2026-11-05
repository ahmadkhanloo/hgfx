"""Schema-only inventory for two previously published behavioral datasets.

No person-level values, labels or observations are printed, checked in or uploaded.
This is a feasibility operation; not a fitting, parity or reproduction experiment.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.io import loadmat, whosmat

SOURCES = {
    "suthaharan_2021": {
        "doi": "10.1038/s41562-021-01176-8",
        "source_repository": "psuthaharan/covid19paranoia",
        "source_commit": "c618e032228fb4ed03821f11bdc57af608695631",
        "path": "data/hgfPRL/pandemic_prelockdown_TP117_TP261_130.mat",
        "model_family_claimed_by_paper": "hgf_ar1_binary_mab + softmax_mu03",
    },
    "reed_2020": {
        "doi": "10.7554/eLife.56345",
        "source_repository": "ModelDBRepository/258631",
        "source_commit": "39ccaca508b81ca610e7666a613e061c801faaf9",
        "path": "IRL_Data.mat",
        "model_family_claimed_by_paper": "three-level HGF + volatility-dependent softmax; original config not pinned here",
    },
}


def describe(value, depth=0):
    arr = np.asarray(value)
    result = {"dtype": str(arr.dtype), "shape": list(arr.shape)}
    if depth >= 3:
        return result
    if arr.dtype.names:
        result["fields"] = {
            key: describe(arr[key], depth + 1)
            for key in arr.dtype.names[:30]
        }
    elif arr.dtype.kind in "O":
        # Describe the first element's structure without exposing its content.
        if arr.size:
            result["first_structure"] = describe(arr.flat[0], depth + 1)
    return result


def inspect(name, source, cache):
    repo, path, revision = source["source_repository"], source["path"], source["source_commit"]
    url = f"https://raw.githubusercontent.com/{repo}/{revision}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "HGFX-public-source-schema-audit/1.0"})
    with urllib.request.urlopen(request, timeout=30) as res:
        data = res.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise RuntimeError("Refuse file larger than 8MiB in metadata workflow")
    file_path = cache / (name + ".mat")
    file_path.write_bytes(data)
    result = {**source, "bytes": len(data), "input_sha256": hashlib.sha256(data).hexdigest()}
    result["mat_variables"] = [
        {"variable": key, "shape": list(shape), "class": klass}
        for key, shape, klass in whosmat(file_path)
        if not key.startswith("__")
    ]
    loaded = loadmat(file_path, squeeze_me=False, struct_as_record=True)
    result["schema"] = {
        key: describe(value)
        for key, value in loaded.items() if not key.startswith("__")
    }
    # Remove downloaded data in the runner after extracting schema.
    file_path.unlink()
    return result


def main():
    destination = Path(sys.argv[1] if len(sys.argv)>1 else "published_study_schema.json")
    import tempfile
    report = {
        "status": "STRUCTURE_INVENTORY_NOT_A_REPLICATION",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "workflow_run": os.environ.get("GITHUB_RUN_ID"),
        "source_commit": os.environ.get("GITHUB_SHA"),
        "cases": {},
    }
    with tempfile.TemporaryDirectory(prefix="hgfx_schema_") as tmp:
        for name, source in SOURCES.items():
            try:
                report["cases"][name] = inspect(name, source, Path(tmp))
            except Exception as ex:
                report["cases"][name] = {
                    "status": "ERROR_NOT_ELIGIBLE_YET",
                    "error": type(ex).__name__,
                    "message": str(ex)[:300],
                    **source,
                }
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
