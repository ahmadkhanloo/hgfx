"""Pinned public study inputs for a prospective two-study fixed-vector pilot.

Downloaded participant-level values are retained ONLY inside the current runner
and are never printed or uploaded. This script does not fit any model.
"""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
import sys
import urllib.request
from pathlib import Path
import numpy as np
from scipy.io import loadmat

CASES = {
    "suthaharan_2021": {
        "repo": "psuthaharan/covid19paranoia",
        "commit": "c618e032228fb4ed03821f11bdc57af608695631",
        "path": "data/hgfPRL/pandemic_prelockdown_TP117_TP261_130.mat",
        "sha256": "9c3e81cc4533b49dfa993f1f885678f1a541dd2f31d6738e6e845bb2e7834428",
        "outcome": "TP117_V3_outcomes_1", "choice": "TP117_V3_choices_1",
    },
    "reed_2020": {
        "repo": "ModelDBRepository/258631",
        "commit": "39ccaca508b81ca610e7666a613e061c801faaf9",
        "path": "IRL_Data.mat",
        "sha256": "b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708",
        "outcome": "P01_outcomes_804020", "choice": "P01_choices_804020",
    },
}


def get_source(spec):
    url = f"https://raw.githubusercontent.com/{spec['repo']}/{spec['commit']}/{spec['path']}"
    req = urllib.request.Request(url, headers={"User-Agent": "HGFX-realdata-parity-pilot/1.0"})
    with urllib.request.urlopen(req, timeout=40) as res:
        raw = res.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError("Unexpected source size over 1MB")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != spec["sha256"]:
        raise ValueError(f"Source identity mismatch: {actual}")
    return raw


def extract_vectors(raw, spec):
    from io import BytesIO
    source = loadmat(BytesIO(raw), squeeze_me=False, struct_as_record=False)
    vectors = []
    for key in (spec["outcome"], spec["choice"]):
        if key not in source:
            raise ValueError(f"Missing preregistered variable {key}")
        arr = np.asarray(source[key], dtype=np.float64)
        if arr.shape != (80, 1):
            raise ValueError(f"Unexpected preregistered shape {key}: {arr.shape}")
        vectors.append(arr.reshape(-1))
    outcome, choice = vectors
    for values, expected, label in ((outcome, (0.0, 1.0), "outcomes"), (choice, (1.0, 2.0, 3.0), "choices")):
        present = values[np.isfinite(values)]
        if not np.all(np.isin(present, expected)):
            raise ValueError(f"BLOCKED_DATA_CODING_UNRESOLVED for {label}; no conversion permitted")
        if np.any(np.isinf(values)):
            raise ValueError(f"Nonfinite infinity in {label}")
    if len(outcome) != 80 or len(choice) != 80:
        raise ValueError("Trial count mismatch")
    return outcome, choice


def main():
    outdir = Path(sys.argv[1]).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    records = {}
    for case, spec in CASES.items():
        try:
            raw = get_source(spec)
            outcome, choice = extract_vectors(raw, spec)
            ignored = np.flatnonzero(np.isnan(outcome) | np.isnan(choice)).astype(int)
            # Data are kept outside any uploaded artifact directory.
            np.savetxt(outdir / f"{case}_input.txt", np.column_stack((outcome, choice)), fmt="%.17g", delimiter=" ")
            records[case] = {
                "status": "INPUT_READY_FOR_FORWARD_PAIR",
                "input_file_sha256": hashlib.sha256((outdir / f"{case}_input.txt").read_bytes()).hexdigest(),
                "source_sha256": spec["sha256"],
                "study": case,
                "selected_variables": [spec["outcome"], spec["choice"]],
                "n_trials": 80, "ignored_trials_1_based": (ignored + 1).tolist(),
                "outcome_domain_valid": True, "choice_domain_valid": True,
            }
        except Exception as exc:
            records[case] = {"status": "BLOCKED_BEFORE_MODEL", "reason": str(exc)[:250], "error_type": type(exc).__name__}
    (outdir / "input_manifest.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps(records, indent=2))
    if any(x["status"] != "INPUT_READY_FOR_FORWARD_PAIR" for x in records.values()):
        raise SystemExit("Input gate BLOCKED: no fitting is permitted for blocked case")


if __name__ == "__main__":
    main()
