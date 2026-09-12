#!/usr/bin/env python3
"""Paired official workflow gate; all preregistered rows required, failures retained."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array

import hgfx
from hgfx.compat.workflows import resolve_config

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
        row = {"id": c["id"], "classification": "INSUFFICIENT_REFERENCE_EVIDENCE", "mismatches": []}
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
                    seed=c["seed"],
                    **kw,
                )
                err = compare("sim.y", sim.y, c["sim"]["y"], 5e-11, 5e-13)
                if err:
                    row["mismatches"].append(err)
                for key, value in c["sim"]["traj"].items():
                    err = compare("sim.traj." + key, sim.traj[key], value, 5e-11, 5e-13)
                    if err:
                        row["mismatches"].append(err)
            est = hgfx.fit_model(_array(c["responses"]).reshape(-1), u, prc, obs)
            expected = c["fit"]
            for name, actual in [
                ("prc_priormus", est.c_prc.priormus),
                ("prc_priorsas", est.c_prc.priorsas),
                ("obs_priormus", est.c_obs.priormus),
                ("obs_priorsas", est.c_obs.priorsas),
            ]:
                err = compare(name, actual, expected[name], 0, 0)
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
            row["classification"] = "PASS" if not row["mismatches"] else "OPTIMIZER_MISMATCH"
        except Exception as exc:
            row["classification"] = "IMPLEMENTATION_MISMATCH"
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
        print(json.dumps(row), flush=True)
    return {
        "protocol": meta["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "cases": rows,
        "gate_pass": len(rows) == len(IDS) and all(r["classification"] == "PASS" for r in rows),
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
