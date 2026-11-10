#!/usr/bin/env python3
"""REV-2.4 Panel E: private original-endpoint input package, NOT science.

Read SHA-verified historical files only. The private output contains original
trial-level data and both original transformed endpoint vectors; NEVER upload
or commit it. The separate audit is sanitized, suitable for CI artifact upload.
No new fit, parameter substitution, or objective evaluation is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from tools.compstat_rev24_endpoint_coverage import (
    COHORT_INPUT_SHA256, audit_coverage, read_zip_json,
)
from tools.compstat_rev24_endpoint_sources import SOURCES, require

PROTOCOL = "compstat-rev2-4-objective-cross-eval-v1"


def safe(value):
    """Encode IEEE nonfinite scalars without silently replacing their meaning."""
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("+Inf" if value > 0 else "-Inf")
    if isinstance(value, list):
        return [safe(x) for x in value]
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    return value


def _full_endpoint(value, count, identity):
    require(isinstance(value, list) and len(value) == count,
            f"{identity}: missing original {count}-component transformed endpoint")
    out = safe(value)
    for v in out:
        require(v is None or (isinstance(v, (int, float)) and not isinstance(v, bool))
                or v in ("NaN", "+Inf", "-Inf"),
                f"{identity}: unsupported endpoint scalar")
    return out


def _case(case_id, model, observation, inputs, responses, matlab, hgfx, source, *, obs_prior_variance, source_prior_variances=None):
    require(isinstance(inputs, list) and isinstance(responses, list)
            and len(inputs) == len(responses) and len(inputs) > 0,
            f"{case_id}: invalid original input/response pairing")
    require(isinstance(source, str) and source,
            f"{case_id}: missing archival source reference")
    n = len(matlab)
    require(hgfx is None or len(hgfx) == n, f"{case_id}: endpoint length mismatch")
    return {
        "case_id": case_id, "perceptual_model": model,
        "observation_model": observation, "source": source,
        "trials": len(inputs), "inputs": safe(inputs), "responses": safe(responses),
        "obs_prior_variance": obs_prior_variance,
        "source_prior_variances": safe(source_prior_variances),
        "endpoints": {
            "matlab": matlab,
            "hgfx": hgfx,
        },
        "endpoint_status": {
            "matlab": "ORIGINAL_SOURCE_PRESENT",
            "hgfx": ("ORIGINAL_SOURCE_PRESENT" if hgfx is not None
                     else "INSUFFICIENT_REFERENCE_EVIDENCE"),
        },
        "objective_cross_evaluation": "NOT_RUN",
    }


def build_private_inputs(d02_data, d08_data, d08_comparison,
                         hgfx_raw, matlab_raw, cohort_data):
    """Construct 66 original rows. Pure function; use only after SHA checks."""
    d02_list = [r for r in d02_data["cases"] if r.get("id") == "D02_fit"]
    require(len(d02_list) == 1, "D02 source identity not unique")
    d02 = d02_list[0]
    require(d02["model"] == "ehgf_binary"
            and d02["observation"] == "unitsq_sgm"
            and d02["seed"] == 123456789, "D02 original identity changed")
    original_matlab = d02["fit"]["final"]
    require(original_matlab["shape"] == [1, 15],
            "D02 original MATLAB endpoint shape changed")
    cases = [_case(
        "D02_fit", "ehgf_binary", "unitsq_sgm",
        d02["inputs"], d02["responses"],
        _full_endpoint(original_matlab["data"], 15, "D02 MATLAB"),
        None, "d02:m18_workflows.json",
        obs_prior_variance=d02["obs_prior_variance"],
        source_prior_variances={"perceptual": d02["fit"]["prc_priorsas"],
                                "observation": d02["fit"]["obs_priorsas"]},
    )]
    require(cases[0]["trials"] == 320, "D02 original trial length changed")

    require(d08_data["case_id"] == "D08_fit"
            and d08_data["model"] == "uhgf"
            and d08_data["observation"] == "gaussian_obs",
            "D08 model family/observation identity changed")
    d08_rows = d08_comparison["endpoint_parameters"]
    require(len(d08_rows) == 11 and
            [r["index"] for r in d08_rows] == list(range(11)),
            "D08 archived full endpoint record changed")
    d08_matlab = _full_endpoint(d08_data["final"], 11, "D08 MATLAB")
    require([r["matlab"] for r in d08_rows] == d08_matlab,
            "D08 independent MATLAB source endpoints differ")
    d08_hgfx = _full_endpoint([r["hgfx"] for r in d08_rows], 11, "D08 HGFX")
    cases.append(_case(
        "D08_fit", "uhgf", "gaussian_obs",
        d08_data["inputs"], d08_data["responses"],
        d08_matlab, d08_hgfx,
        "d08:m18_d08_endpoint.json+m18_d08_endpoint_comparison.json",
        obs_prior_variance=d08_data["obs_priorsas"],
        source_prior_variances={"perceptual": d08_data["prc_priorsas"],
                                "observation": [d08_data["obs_priorsas"]]},
    ))
    require(cases[1]["trials"] == 614, "D08 original trial length changed")

    require(cohort_data.get("subject_indices_zero_based") == list(range(64))
            and cohort_data.get("subject_count") == 64
            and cohort_data.get("trial_count") == 128,
            "Cohort input grid changed")
    for side, raw in (("hgfx", hgfx_raw), ("matlab", matlab_raw)):
        require(raw["model"] == "hgf_binary"
                and raw["observation_model"] == "unitsq_sgm",
                f"{side}: cohort model/observation changed")
        require(raw.get("subjects") == 64 and raw.get("trials") == 128,
                f"{side}: cohort size changed")
        require([r["subject_index_zero_based"] for r in raw["cases"]] ==
                list(range(64)), f"{side}: subject order changed")
    require(hgfx_raw["input_sha256"] == COHORT_INPUT_SHA256,
            "Cohort HGFX input hash does not match original fixture")

    for idx in range(64):
        for side in ("u", "y"):
            require(len(cohort_data[side][idx]) == 128,
                    f"subject {idx}: original {side} trial count wrong")
        cases.append(_case(
            f"cohort64_subject_{idx:02d}", "hgf_binary", "unitsq_sgm",
            cohort_data["u"][idx], cohort_data["y"][idx],
            _full_endpoint(matlab_raw["cases"][idx]["optim"]["final"], 15,
                           f"cohort64 subject {idx} MATLAB"),
            _full_endpoint(hgfx_raw["cases"][idx]["optim"]["final"], 15,
                           f"cohort64 subject {idx} HGFX"),
            "cohort64:matlab_raw.json+hgfx_raw.json+binary_128_s64.json",
            obs_prior_variance=1.0,
        ))
    require(cases[0]["obs_prior_variance"] == 0.5 and
            cases[1]["obs_prior_variance"] == 0.1,
            "Original D02/D08 observation-prior variances changed")
    require(len(cases) == 66 and len({c["case_id"] for c in cases}) == 66,
            "Panel E cannot omit or duplicate an original case")
    require(sum(c["endpoints"]["hgfx"] is None for c in cases) == 1,
            "Panel E missing original D02 HGFX endpoint is a required blocker")
    payload = {
        "protocol": PROTOCOL,
        "panel": "E",
        "source_status": "ORIGINAL_ARCHIVE_BYTES_VERIFIED_EXTERNALLY",
        "science_status": "NOT_EXECUTED",
        "source_sha256": {k: v["zip_sha256"] for k, v in SOURCES.items()},
        "original_cohort_inputs_sha256": COHORT_INPUT_SHA256,
        "data_policy": "PRIVATE_RUNNER_ONLY_NEVER_UPLOAD_OR_COMMIT",
        "expected_cases": 66,
        "cases": cases,
    }
    return payload


def digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def sanitized_audit(payload):
    cases = payload["cases"]
    require(len(cases) == 66 and cases[0]["case_id"] == "D02_fit"
            and cases[1]["case_id"] == "D08_fit", "Panel E row identity drift")
    return {
        "protocol": PROTOCOL,
        "panel": "E",
        "stage": "PRIVATE_INPUT_PREPARATION_ONLY",
        "science_gate": "NOT_ASSESSED",
        "original_cases": len(cases),
        "original_matlab_endpoints": sum(c["endpoints"]["matlab"] is not None
                                         for c in cases),
        "original_hgfx_endpoints": sum(c["endpoints"]["hgfx"] is not None
                                       for c in cases),
        "insufficient_reference_evidence": [
            c["case_id"] for c in cases if c["endpoints"]["hgfx"] is None
        ],
        "d02": {"trials": 320, "matlab": True, "hgfx": False},
        "d08": {"trials": 614, "matlab": True, "hgfx": True},
        "cohort64": {"subjects": 64, "trials_per_subject": 128,
                     "matlab_endpoints": 64, "hgfx_endpoints": 64},
        "private_input_sha256": digest(payload),
        "source_sha256": payload["source_sha256"],
        "cohort_input_sha256": payload["original_cohort_inputs_sha256"],
        "objective_evaluations": 0,
        "includes_trial_data_or_endpoints": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("d02", "d08", "cohort64", "cohort_input", "private_output",
                 "audit_output"):
        p.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = p.parse_args()
    require(not args.private_output.exists() and not args.audit_output.exists(),
            "Original Panel E inputs/audit must not be overwritten")
    audit_coverage(args.d02, args.d08, args.cohort64, args.cohort_input)
    data = build_private_inputs(
        read_zip_json(args.d02, "m18_workflows.json"),
        read_zip_json(args.d08, "m18_d08_endpoint.json"),
        read_zip_json(args.d08, "m18_d08_endpoint_comparison.json"),
        read_zip_json(args.cohort64, "hgfx_raw.json"),
        read_zip_json(args.cohort64, "matlab_raw.json"),
        json.loads(args.cohort_input.read_text(encoding="utf-8")),
    )
    summary = sanitized_audit(data)
    args.private_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.private_output.write_text(json.dumps(data, indent=2, sort_keys=True,
                                              allow_nan=False) + "\n", encoding="utf-8")
    args.audit_output.write_text(json.dumps(summary, indent=2, sort_keys=True,
                                            allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"stage": summary["stage"], "cases": summary["original_cases"],
                      "matlab_endpoints": summary["original_matlab_endpoints"],
                      "hgfx_endpoints": summary["original_hgfx_endpoints"],
                      "science_gate": summary["science_gate"]}, sort_keys=True))


if __name__ == "__main__":
    main()
