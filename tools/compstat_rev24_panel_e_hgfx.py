#!/usr/bin/env python3
"""REV-2.4 Panel E: ORIGINAL HGFX 1.0.0 fixed-endpoint evaluator.

No fitting, resampling, dropout or claim of parity. PRIVATE INPUT AND OUTPUT:
neither may be uploaded to a public repository or unrestricted CI artifact.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform

import numpy as np

from tools.compstat_rev24_manifest import (
    FROZEN_RELEASE, MATLAB_REFERENCE, NUMPY_VERSION, ieee,
    require_released_runtime,
)
from tools.compstat_rev24_panel_e_inputs import PROTOCOL, digest

EXPECTED = ("D02_fit", "D08_fit") + tuple(
    f"cohort64_subject_{i:02d}" for i in range(64)
)
N_ENDPOINTS = 132


def check(condition, message):
    if not condition:
        raise ValueError(message)


def number(value):
    if value is None or value == "NaN":
        return float("nan")
    if value == "+Inf":
        return float("inf")
    if value == "-Inf":
        return float("-inf")
    if isinstance(value, bool):
        raise ValueError("Boolean is not a numeric original source entry")
    return float(value)


def as_float_array(values):
    return np.asarray([number(x) for x in values], dtype=np.float64)


def priors_source_list(values):
    if values is None:
        return None
    if isinstance(values, dict):
        check(values.get("shape", [1, len(values.get("data", []))])
              == [1, len(values["data"])], "Archived prior-vector shape drift")
        values = values["data"]
    return as_float_array(values)


def assert_source_prior_identity(case, prc, obs):
    original = case.get("source_prior_variances")
    if original is None:
        return
    for side, config in (("perceptual", prc), ("observation", obs)):
        source = priors_source_list(original[side])
        actual = np.asarray(config.priorsas, dtype=np.float64)
        check(np.array_equal(source, actual, equal_nan=True),
              f'{case["case_id"]}: archived {side} variances differ from v1.0.0')


def validate_inputs(doc):
    check(doc.get("protocol") == PROTOCOL and doc.get("panel") == "E",
          "Wrong frozen Panel E protocol")
    check(doc.get("science_status") == "NOT_EXECUTED"
          and doc.get("expected_cases") == 66,
          "Input is not original source-only Panel E")
    cases = doc.get("cases")
    check(isinstance(cases, list) and len(cases) == 66,
          "Expected all 66 original case identities")
    check(tuple(c["case_id"] for c in cases) == EXPECTED,
          "Original case order/identity changed")
    for i, case in enumerate(cases):
        check(case["case_sha256"] == digest({k:v for k,v in case.items()
                                            if k != "case_sha256"}),
              f'Original case hash mismatch: {case["case_id"]}')
        model, obs, n = (
            ("ehgf_binary", "unitsq_sgm", 320) if i == 0 else
            ("uhgf", "gaussian_obs", 614) if i == 1 else
            ("hgf_binary", "unitsq_sgm", 128)
        )
        check(case["perceptual_model"] == model
              and case["observation_model"] == obs
              and case["trials"] == n
              and len(case["inputs"]) == n
              and len(case["responses"]) == n,
              f'Original frozen config/data changed: {case["case_id"]}')
        check(case["obs_prior_variance"] == (0.5 if i == 0 else
              0.1 if i == 1 else 1.0),
              f'Original observation prior mismatch: {case["case_id"]}')
        check(len(case["endpoints"]["matlab"]) == (11 if i == 1 else 15),
              "Original MATLAB endpoint dimensionality changed")
        check((case["endpoints"]["hgfx"] is None) == (i == 0),
              "Missing original HGFX endpoint changed")
        if i != 0:
            check(len(case["endpoints"]["hgfx"]) == (11 if i == 1 else 15),
                  "Original HGFX endpoint dimensionality changed")
    return cases


def evaluate_case(case, endpoint_name, objective_fn):
    source = case["endpoints"][endpoint_name]
    row = {
        "case_id": case["case_id"], "case_sha256": case["case_sha256"],
        "at_original_endpoint": endpoint_name, "source": "hgfx",
        "model": case["perceptual_model"], "observation_model": case["observation_model"],
        "valid": False, "rval": -1, "status": "NOT_EXECUTED",
        "log_likelihood": "NaN", "neg_log_likelihood": "NaN",
        "neg_log_joint": "NaN", "trial_log_likelihoods": [],
        "perceptual_prior_total": "NaN", "observation_prior_total": "NaN",
        "error_type": "", "error_message": "",
        "first_causal_state": "NOT_EXPORTED",
        "gradient": "NOT_AVAILABLE",
    }
    if source is None:
        row["status"] = "INSUFFICIENT_REFERENCE_EVIDENCE"
        return row
    try:
        full = as_float_array(source)
        check(len(full) in (11, 15), "Unexpected full vector length")
        objective = objective_fn(case, full)
        ll = np.asarray(objective.trial_log_likelihoods,
                        dtype=np.float64).reshape(-1)
        row["rval"] = int(objective.rval)
        row["log_likelihood"] = ieee(objective.log_likelihood)
        row["neg_log_likelihood"] = ieee(objective.neg_log_likelihood)
        row["neg_log_joint"] = ieee(objective.neg_log_joint)
        row["perceptual_prior_total"] = ieee(objective.perceptual_prior.total)
        row["observation_prior_total"] = ieee(objective.observation_prior.total)
        row["trial_log_likelihoods"] = [ieee(x) for x in ll]
        row["valid"] = bool(
            objective.rval == 0 and ll.size == case["trials"]
            and np.all(np.isfinite(ll))
            and np.isfinite(objective.log_likelihood)
            and np.isfinite(objective.neg_log_likelihood)
            and np.isfinite(objective.neg_log_joint)
        )
        row["status"] = "VALID" if row["valid"] else "INVALID_OBJECTIVE"
    except Exception as exc:
        row["status"] = "EVALUATION_ERROR"
        row["error_type"] = type(exc).__name__
        row["error_message"] = str(exc)[:750]
    return row


def evaluate(doc, objective_fn, *, wheel_sha256, runtime):
    cases = validate_inputs(doc)
    rows = [
        evaluate_case(case, side, objective_fn)
        for case in cases for side in ("matlab", "hgfx")
    ]
    check(len(rows) == N_ENDPOINTS, "Lost a Panel E endpoint slot")
    return {
        "protocol": PROTOCOL, "panel": "E",
        "source": "hgfx", "private_source_sha256": digest(doc),
        "release_source_commit": FROZEN_RELEASE,
        "matlab_reference_commit": MATLAB_REFERENCE,
        "release_wheel_sha256": wheel_sha256,
        "runtime": runtime,
        "cases": rows,
        "scientific_gate": "NOT_ASSESSED_NO_PAIRED_MATLAB",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-input",type=Path,required=True)
    p.add_argument("--release-wheel",type=Path,required=True)
    p.add_argument("--frozen-tag-source",type=Path,required=True)
    p.add_argument("--private-output",type=Path,required=True)
    args=p.parse_args()
    check(not args.private_output.exists(), "Refusing to overwrite original Panel E output")
    wheel_hash=require_released_runtime(args.release_wheel,args.frozen_tag_source)
    check(np.__version__ == NUMPY_VERSION, "NumPy frozen version mismatch")
    # Release imports only after source-byte verification; no development worktree.
    import hgfx
    import jax
    import jaxlib
    from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
    check(jax.config.read("jax_enable_x64") and jax.default_backend()=="cpu",
          "Expected pinned scientific CPU x64")
    check(Path(hgfx.__file__).resolve() ==
          Path(importlib.metadata.distribution("hgfx").locate_file(
              "hgfx/__init__.py")).resolve(),
          "HGFX imported from branch not installed frozen wheel")
    doc=json.loads(args.private_input.read_text(encoding="utf-8"))

    def objective_fn(case, full):
        u=as_float_array(case["inputs"])
        y=as_float_array(case["responses"])
        prc=resolve_config(case["perceptual_model"]).resolve_placeholders(u)
        obs=resolve_config(case["observation_model"]).resolve_placeholders(u)
        obs=replace(obs, parameters=tuple(
            replace(param, prior_variance=float(case["obs_prior_variance"]))
            for param in obs.parameters))
        assert_source_prior_identity(case,prc,obs)
        problem=WorkflowFitProblem(y,u,prc,obs)
        check(len(full) == len(problem.initial_full),
              "Original full endpoint parameter dimension mismatch")
        free=np.asarray(problem.free_indices,dtype=int)
        check(np.all(np.isfinite(full[free])),
              "Original free endpoint parameter nonfinite")
        fixed=np.setdiff1d(np.arange(len(full)),free)
        check(np.array_equal(full[fixed],problem.initial_full[fixed],
                             equal_nan=True), "Original fixed endpoint parameters differ")
        return problem.evaluate_full(full)

    result=evaluate(doc,objective_fn,wheel_sha256=wheel_hash,runtime={
        "python":platform.python_version(),"numpy":np.__version__,
        "jax":jax.__version__,"jaxlib":jaxlib.__version__,
        "platform":platform.platform(), "backend":jax.default_backend(),
        "hgfx_distribution":importlib.metadata.version("hgfx"),
        "hgfx_module_path":str(Path(hgfx.__file__).resolve()),
    })
    args.private_output.parent.mkdir(parents=True,exist_ok=True)
    args.private_output.write_text(json.dumps(result,indent=2,sort_keys=True,
                                              allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":"E","slots":len(result["cases"]),
        "evaluated":sum(row["status"]!="INSUFFICIENT_REFERENCE_EVIDENCE"
                        for row in result["cases"]),
        "valid":sum(row["valid"] for row in result["cases"]),
        "invalid":sum(row["status"] not in ("VALID","INSUFFICIENT_REFERENCE_EVIDENCE")
                      for row in result["cases"]),
        "output_sha256":hashlib.sha256(args.private_output.read_bytes()).hexdigest(),
        "scientific_gate":"NOT_ASSESSED_NO_PAIRED_MATLAB",
    },sort_keys=True))


if __name__=="__main__":main()
