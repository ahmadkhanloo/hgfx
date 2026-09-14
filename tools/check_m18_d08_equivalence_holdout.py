#!/usr/bin/env python3
"""Prospective D08 equivalence holdout.

The seeds and decision rule are frozen in MATLAB_EQUIVALENCE_POLICY.md.  This
checker deliberately reuses the official workflow tolerances instead of
loosening the pointwise trajectory gate after seeing D08's original failure.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import hgfx
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks

PROTOCOL = "m18-d08-equivalence-holdout-1"
FROZEN_SEEDS = (271828182, 314159265)
DEFAULT_RTOL = 3e-8
DEFAULT_ATOL = 3e-10


def compare(label, actual, expected, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
    a = np.squeeze(np.asarray(actual, dtype=np.float64))
    e = np.squeeze(_array(expected))
    if a.shape != e.shape:
        return f"{label}: shape {a.shape} != {e.shape}"
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return None
    idx = tuple(int(v) for v in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = a[idx] if idx else a.item()
    ev = e[idx] if idx else e.item()
    return f"{label}: first divergence index={idx} HGFX={av} MATLAB={ev}"


def field_tolerance(name):
    if name in ("Sigma", "Corr"):
        return 5e-6, 5e-8
    if name in ("H", "LME"):
        return 2e-6, 2e-8
    return DEFAULT_RTOL, DEFAULT_ATOL


def problem_for(y, u):
    prc = resolve_config("uhgf")
    obs = resolve_config("gaussian_obs")
    return WorkflowFitProblem(
        y,
        u,
        prc.resolve_placeholders(u),
        obs.resolve_placeholders(u),
    ), prc, obs


def same_endpoint_mismatches(problem, prc, obs, y, u, expected):
    final = _array(expected["final"]).reshape(-1)
    mismatches = []

    objective = problem.evaluate_full(final)
    for label, actual, key in (
        ("same_endpoint.negLl", objective.neg_log_likelihood, "negLl"),
        ("same_endpoint.negLj", objective.neg_log_joint, "negLj"),
    ):
        err = compare(label, actual, expected[key])
        if err:
            mismatches.append(err)

    masks = build_trial_masks(y, u)
    ignored = tuple(int(i) for i in np.flatnonzero(masks.ignored))
    irregular = tuple(int(i) for i in np.flatnonzero(masks.irregular))
    prc_resolved = prc.resolve_placeholders(u)
    n = problem.n_perceptual
    traj, states = problem.forward(
        u,
        final[:n],
        transformed=True,
        irregular_intervals=bool(prc_resolved.options.get("irregular_intervals", False)),
        ignored_trials=ignored,
    )
    for key, value in expected["traj"].items():
        if key not in traj:
            mismatches.append(f"same_endpoint.traj.{key}: missing HGFX field")
            continue
        err = compare(f"same_endpoint.traj.{key}", traj[key], value)
        if err:
            mismatches.append(err)

    obs_output = problem.observation(
        y,
        states,
        final[n:],
        irregular_trials=irregular,
    )
    if isinstance(obs_output, tuple) and len(obs_output) >= 3:
        _, yhat, res = obs_output[:3]
        for label, actual, key in (
            ("same_endpoint.yhat", yhat, "yhat"),
            ("same_endpoint.res", res, "res"),
        ):
            err = compare(label, actual, expected[key])
            if err:
                mismatches.append(err)
    else:
        mismatches.append("same_endpoint.observation: expected tuple with yhat/res")
    return mismatches


def trace_mismatches(actual_iter, expected_iter):
    if not isinstance(expected_iter, dict) or not hasattr(actual_iter, "x"):
        return ["optimizer.trace: missing trace"]
    mismatches = []
    for key, actual in (
        ("x", actual_iter.x),
        ("val", actual_iter.val),
        ("rst", actual_iter.rst),
    ):
        err = compare(f"optimizer.iter.{key}", actual, expected_iter[key])
        if err:
            mismatches.append(err)
    return mismatches


def validate_case(case, u):
    row = {
        "seed": int(np.asarray(case["seed"], dtype=np.int64).reshape(-1)[0]),
        "classification": "INSUFFICIENT_REFERENCE_EVIDENCE",
        "frozen_gate_mismatches": [],
        "core_inference_mismatches": [],
        "same_endpoint_mismatches": [],
        "optimizer_trace_mismatches": [],
    }
    if not case.get("success", False):
        row["classification"] = "MATLAB_REFERENCE_FAILURE"
        row["matlab_failure"] = {
            key: case.get(key, "")
            for key in ("stage", "error_identifier", "error_message")
        }
        return row

    y = _array(case["responses"]).reshape(-1)
    expected = case["fit"]
    problem, prc, obs = problem_for(y, u)
    est = hgfx.fit_model(y, u, prc, obs)

    # Level 0 configuration/prior contract: no tolerance broadening is allowed.
    for name, actual in (
        ("prc_priormus", est.c_prc.priormus),
        ("prc_priorsas", est.c_prc.priorsas),
        ("obs_priormus", est.c_obs.priormus),
        ("obs_priorsas", est.c_obs.priorsas),
    ):
        err = compare(name, actual, expected[name], 0.0, 1e-18)
        if err:
            row["core_inference_mismatches"].append(err)
            row["frozen_gate_mismatches"].append(err)

    core_fields = (
        "final",
        "H",
        "Sigma",
        "Corr",
        "negLl",
        "negLj",
        "LME",
        "AIC",
        "BIC",
        "yhat",
        "res",
        "resAC",
    )
    for name in core_fields:
        rtol, atol = field_tolerance(name)
        err = compare(name, est.optim[name], expected[name], rtol, atol)
        if err:
            row["core_inference_mismatches"].append(err)
            row["frozen_gate_mismatches"].append(err)

    for key, value in expected["traj"].items():
        if key not in est.traj:
            row["frozen_gate_mismatches"].append(f"fit.traj.{key}: missing HGFX field")
            continue
        err = compare(f"fit.traj.{key}", est.traj[key], value)
        if err:
            row["frozen_gate_mismatches"].append(err)

    row["same_endpoint_mismatches"] = same_endpoint_mismatches(
        problem, prc, obs, y, u, expected
    )
    row["optimizer_trace_mismatches"] = trace_mismatches(est.optim.iter, expected.get("iter"))

    if row["same_endpoint_mismatches"]:
        row["classification"] = "IMPLEMENTATION_MISMATCH"
    elif row["core_inference_mismatches"]:
        row["classification"] = "INFERENCE_EQUIVALENCE_FAIL"
    elif row["optimizer_trace_mismatches"]:
        row["classification"] = "OPTIMIZER_MISMATCH"
    elif not row["frozen_gate_mismatches"]:
        row["classification"] = "PASS"
    elif all(item.startswith("fit.traj.") for item in row["frozen_gate_mismatches"]):
        row["classification"] = "PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY"
    else:
        row["classification"] = "NUMERICAL_MISMATCH"
    return row


def validate(reference):
    meta = reference["metadata"]
    if meta.get("protocol") != PROTOCOL:
        raise ValueError("Holdout protocol mismatch")
    if meta.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if meta.get("numeric_encoding") != "ieee-strings-v1":
        raise ValueError("Numeric encoding mismatch")
    if meta.get("case_id") != "D08_fit":
        raise ValueError("Unexpected case ID")
    if reference.get("model") != "uhgf" or reference.get("observation") != "gaussian_obs":
        raise ValueError("Model/observation contract mismatch")

    seeds = tuple(int(v) for v in _array(reference["seeds"]).reshape(-1))
    if seeds != FROZEN_SEEDS:
        raise ValueError(f"Frozen seed mismatch: {seeds} != {FROZEN_SEEDS}")
    cases = reference.get("cases", [])
    if len(cases) != len(FROZEN_SEEDS):
        raise ValueError("Incomplete holdout case set")
    case_seeds = tuple(int(np.asarray(c["seed"], dtype=np.int64).reshape(-1)[0]) for c in cases)
    if case_seeds != FROZEN_SEEDS:
        raise ValueError("Holdout cases are reordered or have changed seeds")

    u = _array(reference["inputs"]).reshape(-1)
    rows = []
    for case in cases:
        row = validate_case(case, u)
        rows.append(row)
        print(json.dumps(row), flush=True)

    accepted = {"PASS", "PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY"}
    return {
        "protocol": PROTOCOL,
        "policy": "docs/validation/MATLAB_EQUIVALENCE_POLICY.md",
        "reference_commit": REFERENCE_COMMIT,
        "frozen_seeds": list(FROZEN_SEEDS),
        "cases": rows,
        "gate_pass": len(rows) == len(FROZEN_SEEDS)
        and all(row["classification"] in accepted for row in rows),
    }


def main(reference_path: Path, output_path: Path) -> int:
    result = validate(json.loads(reference_path.read_text()))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"gate_pass": result["gate_pass"]}), flush=True)
    return 0 if result["gate_pass"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))