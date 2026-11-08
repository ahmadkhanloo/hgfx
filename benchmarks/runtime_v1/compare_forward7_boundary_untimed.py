#!/usr/bin/env python3
"""PERF-01C candidate forward-call boundary audit; NEVER times anything."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_forward7_untimed import compare as compare_complete_outputs

BOUNDARY = "PERCEPTUAL_FORWARD_FULL_OUTPUT_CALL_V1"
SCOPE = "FORWARD_ONLY_NO_OBSERVATION_NO_OBJECTIVE_NO_FIT"
BEFORE = "BEFORE_CALL_OUTSIDE_CANDIDATE_REGION"
AFTER = "AFTER_CALL_OUTSIDE_CANDIDATE_REGION"
SOURCES = {
    "hgfx": "perf01c-forward7-hgfx-boundary-untimed-v1",
    "matlab": "perf01c-forward7-matlab-boundary-untimed-v1",
}


def require_boundary(payload: dict, engine: str) -> None:
    if (payload.get("schema") != SOURCES[engine]
            or payload.get("candidate_boundary") != BOUNDARY
            or payload.get("input_preparation") != BEFORE
            or payload.get("output_shape_validation_and_serialization") != AFTER
            or payload.get("clock") != "ABSENT"):
        raise ValueError(engine + ": candidate boundary contract not established")
    for row in payload.get("cells", []):
        if (row.get("boundary_id") != BOUNDARY
                or row.get("boundary_scope") != SCOPE
                or row.get("clock") != "ABSENT"):
            raise ValueError(engine + ": case boundary not established")


def compare(root: Path, hgfx: dict, matlab: dict) -> dict:
    require_boundary(hgfx, "hgfx")
    require_boundary(matlab, "matlab")
    # Run the *unchanged* full, fieldwise historical diagnostic comparator:
    # existing case/file checks, axis semantics, numerical thresholds and
    # all 11 trajectory fields + original N x 3 x 4 inference states.
    # Only map a new wrapper schema to its original comparator input schema.
    h = dict(hgfx, schema="perf01c-forward7-hgfx-untimed-v1")
    m = dict(matlab, schema="perf01c-forward7-matlab-untimed-v1")
    result = compare_complete_outputs(root, h, m)
    result.update({
        "schema": "perf01c-forward7-proposed-boundary-untimed-compare-v1",
        "candidate_boundary": BOUNDARY,
        "input_preparation": BEFORE,
        "output_shape_validation_and_serialization": AFTER,
        "clock": "ABSENT",
        "benchmark": "NOT_RUN_NOT_AUTHORIZED",
        "external_independent_approval": "NOT_RECEIVED",
        "perf01c": "BLOCK_FREEZE_NOT_FROZEN",
    })
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--hgfx", type=Path, required=True)
    p.add_argument("--matlab", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = compare(a.input, json.loads(a.hgfx.read_bytes()),
                     json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(report["counts"], sort_keys=True))
    if report["counts"].get("FORWARD_CONTRACT_OR_NUMERICAL_MISMATCH"):
        raise SystemExit("Forward mismatch preserved: boundary still blocked")


if __name__ == "__main__":
    main()
