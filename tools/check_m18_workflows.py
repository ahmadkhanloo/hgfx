#!/usr/bin/env python3
"""Paired official workflow gate; all preregistered rows required, failures retained."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array

import hgfx
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks
from hgfx.optim.ridders import RiddersOptions, ridders_gradient

IDS = (
    "D01_bayes",
    "D01_fit",
    "D02_fit",
    "D03_fit",
    "D05_fit",
    "D06_bayes",
    "D06_fit",
    "D07_fit",
    "D08_fit",
)


def _seed(value):
    """MATLAB jsonencode emits integer seeds as doubles."""
    if value is None:
        return None
    if isinstance(value, dict):
        value = _array(value).reshape(-1)[0]
    return int(np.asarray(value, dtype=np.int64).reshape(-1)[0])


def compare(label, a, e, rtol=3e-8, atol=3e-10):
    a = np.asarray(a, dtype=np.float64)
    e = _array(e)
    a = np.squeeze(a)
    e = np.squeeze(e)
    if a.shape != e.shape:
        return f"{label}: shape {a.shape} != {e.shape}"
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return None
    idx = tuple(np.argwhere(~close)[0]) if np.ndim(close) else ()
    return f"{label}: first divergence index={idx} HGFX={a[idx]} MATLAB={e[idx]}"


def _problem(case, u, prc, obs):
    y = _array(case["responses"]).reshape(-1)
    return WorkflowFitProblem(
        y,
        u,
        prc.resolve_placeholders(u),
        obs.resolve_placeholders(u),
    )


def reference_point_diagnostics(case, u, prc, obs):
    """Evaluate HGFX at MATLAB's fitted point without changing the release gate."""
    expected = case["fit"]
    final = _array(expected["final"]).reshape(-1)
    y = _array(case["responses"]).reshape(-1)
    prc_resolved = prc.resolve_placeholders(u)
    obs_resolved = obs.resolve_placeholders(u)
    problem = WorkflowFitProblem(y, u, prc_resolved, obs_resolved)
    if final.size != problem.initial_full.size:
        return {
            "classification": "IMPLEMENTATION_MISMATCH",
            "mismatches": [
                f"reference.final: size {final.size} != expected {problem.initial_full.size}"
            ],
        }

    mismatches = []
    objective = problem.evaluate_full(final)
    for name, actual in (
        ("reference.negLl", objective.neg_log_likelihood),
        ("reference.negLj", objective.neg_log_joint),
    ):
        expected_name = name.split(".", 1)[1]
        err = compare(name, actual, expected[expected_name])
        if err:
            mismatches.append(err)

    masks = build_trial_masks(y, u)
    ignored = tuple(int(index) for index in np.flatnonzero(masks.ignored))
    irregular = tuple(int(index) for index in np.flatnonzero(masks.irregular))
    n = problem.n_perceptual
    traj, states = problem.forward(
        u,
        final[:n],
        transformed=True,
        irregular_intervals=bool(prc_resolved.options.get("irregular_intervals", False)),
        ignored_trials=ignored,
    )
    for key, value in expected["traj"].items():
        err = compare("reference.traj." + key, traj[key], value)
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
        for name, actual in (("reference.yhat", yhat), ("reference.res", res)):
            expected_name = name.split(".", 1)[1]
            err = compare(name, actual, expected[expected_name])
            if err:
                mismatches.append(err)

    return {
        "classification": "PASS" if not mismatches else "IMPLEMENTATION_MISMATCH",
        "mismatches": mismatches,
    }


def initial_ridders_diagnostics(case, u, prc, obs):
    """Compare the exact initial objective and Ridders gradient used by BFGS."""
    expected = case["fit"].get("initial_ridders")
    if not isinstance(expected, dict):
        return {"classification": "INSUFFICIENT_REFERENCE_EVIDENCE"}

    problem = _problem(case, u, prc, obs)
    gradient, errors = ridders_gradient(
        problem.evaluate_free,
        problem.initial_free,
        RiddersOptions(min_steps=10),
    )
    mismatches = []
    for label, actual, key in (
        ("initial_ridders.x", problem.initial_free, "x"),
        ("initial_ridders.val", problem.evaluate_free(problem.initial_free), "val"),
        ("initial_ridders.grad", gradient, "grad"),
        ("initial_ridders.grad_err", errors, "grad_err"),
    ):
        err = compare(label, actual, expected[key])
        if err:
            mismatches.append(err)
    return {
        "classification": "PASS" if not mismatches else "DIVERGED",
        "mismatches": mismatches,
    }


def optimizer_trace_diagnostics(case, u, prc, obs, est):
    """Compare BFGS traces without making them part of the frozen release gate.

    For the two currently divergent workflows, also replay HGFX's objective at
    every finite MATLAB iteration point. If those objective values agree while
    the optimizer traces diverge, the evidence isolates an optimizer/numerical
    path mismatch rather than a model/objective mismatch.
    """
    expected_iter = case["fit"].get("iter")
    if not isinstance(expected_iter, dict):
        return {"classification": "INSUFFICIENT_REFERENCE_EVIDENCE"}
    actual_iter = est.optim.iter
    if not hasattr(actual_iter, "x"):
        return {
            "classification": "IMPLEMENTATION_MISMATCH",
            "mismatches": ["HGFX optim.iter trace is absent"],
        }

    mismatches = []
    for name, actual in (
        ("optimizer.iter.x", actual_iter.x),
        ("optimizer.iter.val", actual_iter.val),
        ("optimizer.iter.rst", actual_iter.rst),
    ):
        expected_name = name.rsplit(".", 1)[1]
        err = compare(name, actual, expected_iter[expected_name])
        if err:
            mismatches.append(err)

    result = {
        "classification": "PASS" if not mismatches else "DIVERGED",
        "mismatches": mismatches,
    }

    if case["id"] not in {"D02_fit", "D08_fit"}:
        return result

    problem = _problem(case, u, prc, obs)
    matlab_x = _array(expected_iter["x"])
    matlab_val = _array(expected_iter["val"]).reshape(-1)
    if matlab_x.ndim == 1:
        matlab_x = matlab_x.reshape(-1, len(problem.free_indices))
    objective_mismatches = []
    checked = 0
    for index, point in enumerate(matlab_x):
        if index >= matlab_val.size or not np.all(np.isfinite(point)):
            continue
        expected_value = matlab_val[index]
        if not np.isfinite(expected_value):
            continue
        checked += 1
        actual_value = problem.evaluate_free(point)
        err = compare(
            f"matlab_path_objective[{index}]",
            actual_value,
            expected_value,
        )
        if err:
            objective_mismatches.append(err)
            break
    result["matlab_path_objective"] = {
        "classification": "PASS" if not objective_mismatches else "IMPLEMENTATION_MISMATCH",
        "points_checked": checked,
        "mismatches": objective_mismatches,
    }
    return result


def validate(reference):
    meta = reference["metadata"]
    if (
        meta["reference_commit"] != REFERENCE_COMMIT
        or meta["numeric_encoding"] != "ieee-strings-v1"
        or meta["protocol"] != "official-demo-workflows-1"
    ):
        raise ValueError("Reference/protocol mismatch")
    cases = reference["cases"]
    if [c["id"] for c in cases] != list(IDS):
        raise ValueError("Incomplete, reordered or duplicate case coverage")
    rows = []
    for c in cases:
        row = {
            "id": c["id"],
            "classification": "INSUFFICIENT_REFERENCE_EVIDENCE",
            "mismatches": [],
        }
        try:
            if not c["success"]:
                row["matlab_failure"] = {
                    k: c[k] for k in ("stage", "error_identifier", "error_message")
                }
                rows.append(row)
                continue
            u = _array(c["inputs"]).reshape(-1)
            prc = resolve_config(c["model"])
            obs = resolve_config(c["observation"])
            if c["observation"] == "unitsq_sgm":
                obs = replace(
                    obs,
                    parameters=(
                        replace(obs.parameters[0], prior_variance=c["obs_prior_variance"]),
                    ),
                )
            native = _array(c["native"]).reshape(-1)
            if native.size:
                model = "hgf_binary" if c["id"] == "D05_fit" else c["model"]
                kw = (
                    {"response_normals": _array(c["driver"]).reshape(-1)}
                    if c["observation"] == "gaussian_obs"
                    else {"response_uniforms": _array(c["driver"]).reshape(-1)}
                )
                sim = hgfx.sim_model(
                    u,
                    model,
                    native,
                    c["observation"],
                    _array(c["obs_native"]),
                    seed=_seed(c["seed"]),
                    **kw,
                )
                err = compare("sim.y", sim.y, c["sim"]["y"], 5e-11, 5e-13)
                if err:
                    row["mismatches"].append(err)
                for key, value in c["sim"]["traj"].items():
                    err = compare(
                        "sim.traj." + key,
                        sim.traj[key],
                        value,
                        5e-11,
                        5e-13,
                    )
                    if err:
                        row["mismatches"].append(err)

            row["reference_point"] = reference_point_diagnostics(c, u, prc, obs)
            row["initial_ridders"] = initial_ridders_diagnostics(c, u, prc, obs)
            est = hgfx.fit_model(_array(c["responses"]).reshape(-1), u, prc, obs)
            expected = c["fit"]
            row["optimizer_trace"] = optimizer_trace_diagnostics(c, u, prc, obs, est)
            for name, actual in [
                ("prc_priormus", est.c_prc.priormus),
                ("prc_priorsas", est.c_prc.priorsas),
                ("obs_priormus", est.c_obs.priormus),
                ("obs_priorsas", est.c_obs.priorsas),
            ]:
                err = compare(name, actual, expected[name], 0, 1e-18)
                if err:
                    row["mismatches"].append(err)
            for name in (
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
            ):
                tol = (
                    (5e-6, 5e-8)
                    if name in ("Sigma", "Corr")
                    else (2e-6, 2e-8)
                    if name in ("H", "LME")
                    else (3e-8, 3e-10)
                )
                err = compare(name, est.optim[name], expected[name], *tol)
                if err:
                    row["mismatches"].append(err)
            for key, value in expected["traj"].items():
                err = compare("fit.traj." + key, est.traj[key], value)
                if err:
                    row["mismatches"].append(err)

            implementation_evidence = (
                row["reference_point"]["classification"] == "IMPLEMENTATION_MISMATCH"
                or any(item.startswith("sim.") for item in row["mismatches"])
                or row["optimizer_trace"].get("classification") == "IMPLEMENTATION_MISMATCH"
                or row["optimizer_trace"].get("matlab_path_objective", {}).get("classification")
                == "IMPLEMENTATION_MISMATCH"
            )
            if not row["mismatches"]:
                row["classification"] = "PASS"
            elif implementation_evidence:
                row["classification"] = "IMPLEMENTATION_MISMATCH"
            else:
                row["classification"] = "OPTIMIZER_MISMATCH"
        except Exception as exc:
            row["classification"] = "IMPLEMENTATION_MISMATCH"
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
        print(json.dumps(row), flush=True)
    return {
        "protocol": meta["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "cases": rows,
        "gate_pass": len(rows) == len(IDS)
        and all(r["classification"] == "PASS" for r in rows),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("reference", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = validate(json.loads(a.reference.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    raise SystemExit(0 if result["gate_pass"] else 2)
