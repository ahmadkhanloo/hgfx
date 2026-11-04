"""All 324 published-source blocks: MATLAB8.2 vs HGFX1.0 fixed-vector softmax.

This tests the published-family observation equation, not the original fitted model. This is not a replication of either article's model fitting or inferential results.
Only aggregate comparison metrics and case statuses are written, not raw data.
"""
from __future__ import annotations
import importlib.metadata
import json
import os
import sys
import warnings
from pathlib import Path

import jax
import numpy as np
from scipy.io import loadmat

from compare_realdata_pair import P, RTOL as FORWARD_RTOL, ATOL as FORWARD_ATOL
from hgfx.models import hgf_ar1_binary_mab
from hgfx.responses import softmax_mu3

OBS_RTOL = 2e-11
OBS_ATOL = 2e-13
EXPECTED_CASES = 324
EXPECTED_FIELDS = ("logp", "yhat", "res", "total_loglik")


def compare_field(name, got, expected):
    got = np.asarray(got, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    info = {"field": name, "actual_shape": list(got.shape),
            "matlab_shape": list(expected.shape)}
    # MATLAB sci.io.loadmat often preserves an N x 1 column for a 1D vector.
    if name != "total_loglik" and expected.shape == (got.size, 1):
        expected = expected.reshape(-1)
    if name == "total_loglik" and expected.size == got.size == 1:
        expected = expected.reshape(got.shape)
    if got.shape != expected.shape:
        return {**info, "status": "FAIL_SHAPE", "failing_elements": int(got.size)}
    agreement = np.isclose(got, expected, rtol=OBS_RTOL,
                           atol=OBS_ATOL, equal_nan=True)
    finite = np.isfinite(got) & np.isfinite(expected)
    diffs = np.abs(got[finite] - expected[finite])
    bad = np.argwhere(~agreement)
    info.update(
        status="PASS_NUMERIC_GATE" if not bad.size else "FAIL_NUMERIC_GATE",
        elements=int(got.size),
        finite_elements=int(finite.sum()),
        failing_elements=int(np.count_nonzero(~agreement)),
        max_abs_diff=float(diffs.max()) if diffs.size else None,
    )
    if bad.size:
        index = tuple(int(x) for x in bad[0])
        info["first_divergence_zero_based"] = list(index)
        info["first_divergence_trial_1_based"] = index[0] + 1 if index and name != "total_loglik" else None
    return info


def run_case(folder, entry):
    case_id = entry["id"]
    if entry["status"] != "INPUT_READY":
        return {"id": case_id, "study": entry["study"], "status": "BLOCKED_INPUT"}
    source = np.loadtxt(folder / f"{case_id}_input.txt", dtype=np.float64, ndmin=2)
    if source.shape != (80, 2):
        raise ValueError(f"Unexpected original source shape {source.shape}")
    u, y = source.T
    mask = np.isnan(u) | np.isnan(y)
    if not np.all(np.isin(u[np.isfinite(u)], [0, 1])) or not np.all(np.isin(y[np.isfinite(y)], [1, 2, 3])):
        raise ValueError("Unmapped source coding; no guessed recoding permitted")
    ref = loadmat(folder / f"{case_id}_matlab_mu3.mat")
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        _, states = hgf_ar1_binary_mab(
            u, P, choices=y, n_bandits=3, coupled=False,
            irregular_intervals=False, ignored_trials=np.flatnonzero(mask).tolist(),
            validate=False,
        )
        logp, yhat, residual = softmax_mu3(
            y, states, irregular_trials=np.flatnonzero(mask).tolist(), predorpost=1,
        )
    expected_nonfinite = np.isnan(logp)
    if not np.array_equal(expected_nonfinite, mask):
        raise ValueError("Softmax missingness differs from source mask")
    total = np.sum(logp[~expected_nonfinite], dtype=np.float64)
    data = {"logp": logp, "yhat": yhat, "res": residual,
            "total_loglik": np.asarray(total)}
    checked = [compare_field(name, data[name], ref[name]) for name in EXPECTED_FIELDS]
    success = all(c["status"] == "PASS_NUMERIC_GATE" for c in checked)
    return {
        "id": case_id, "study": entry["study"],
        "status": "PASS_BOUNDED_MU3" if success else "FAIL_BOUNDED_MU3",
        "ignored": int(mask.sum()), "comparisons": checked,
        "warning_types": sorted(set(type(w.message).__name__ for w in ws)),
        "warning_count": len(ws),
    }


def main():
    folder = Path(sys.argv[1]).resolve()
    destination = Path(sys.argv[2]).resolve()
    assert importlib.metadata.version("hgfx") == "1.0.0"
    assert jax.config.jax_enable_x64
    assert all(d.platform == "cpu" for d in jax.devices())
    manifest = json.loads((folder / "all_cohort_manifest.json").read_text())
    matlab = json.loads((folder / "matlab_mu3_status.json").read_text())
    assert manifest["expected_total_cases"] == manifest["actual_total_cases"] == EXPECTED_CASES
    states = {r["id"]: r for r in matlab["records"]}
    output = []
    for entry in manifest["cases"]:
        mid = entry["id"]
        if entry["status"] != "INPUT_READY":
            output.append({"id": mid, "study": entry["study"], "status": "BLOCKED_INPUT"})
        elif mid not in states or states[mid]["status"] != "MATLAB_RESPONSE_DONE":
            output.append({"id": mid, "study": entry["study"], "status": "MATLAB_RESPONSE_FAILED",
                           "reason": states.get(mid, {}).get("reason", "Missing reference output")[:180]})
        else:
            try:
                output.append(run_case(folder, entry))
            except Exception as exc:
                output.append({"id": mid, "study": entry["study"], "status": "HGFX_RESPONSE_FAILED",
                               "reason": f"{type(exc).__name__}: {exc}"[:180]})
    counts = {}
    for row in output:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    comparison = [v for row in output for v in row.get("comparisons", [])]
    deviations = [v["max_abs_diff"] for v in comparison if v.get("max_abs_diff") is not None]
    failed = [v for v in comparison if v["status"] != "PASS_NUMERIC_GATE"]
    summary = {
        "scope": "Two published-input datasets, matched fixed-vector MAB + volatility-dependent softmax_mu3; not the papers' actual fitted models",
        "reference": "MATLAB HGF 8.2.0 2437f4dc241541072722a2695ddeca7b44d83dd3",
        "hgfx": "stable PyPI 1.0.0",
        "jax_version": jax.__version__, "devices": [d.platform for d in jax.devices()],
        "github_sha": os.getenv("GITHUB_SHA"), "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "criteria": {"rtol": OBS_RTOL, "atol": OBS_ATOL, "from": "M7 frozen softmax_mu3 observation gate"},
        "cases_expected": EXPECTED_CASES, "cases_attempted": len(output),
        "case_status": counts, "comparisons": len(comparison),
        "elements_compared": sum(v.get("elements", 0) for v in comparison),
        "failed_fields": len(failed),
        "failed_elements": sum(v.get("failing_elements", 0) for v in comparison),
        "max_abs_diff": max(deviations, default=None),
        "cases_with_warnings": sum(row.get("warning_count", 0) > 0 for row in output),
        "warning_types": sorted({t for row in output for t in row.get("warning_types", [])}),
        "total_ignored_trials": sum(row.get("ignored", 0) for row in output),
        "historical_published_study_replication": "NOT_REPRODUCED",
        "status": ("PASS_BOUNDED_MU3_RESPONSE_PARITY"
                   if counts == {"PASS_BOUNDED_MU3": EXPECTED_CASES}
                   and len(comparison) == EXPECTED_CASES * 4
                   else "FAIL_OR_INCONCLUSIVE_RESPONSE_PARITY"),
        "cases": [
            {"study": row["study"], "id": row["id"], "status": row["status"],
             "warnings": row.get("warning_count"), "failed_quantities": [
                 c["field"] for c in row.get("comparisons", [])
                 if c["status"] != "PASS_NUMERIC_GATE"],
             "first_divergence": next((
                 c.get("first_divergence_trial_1_based") for c in row.get("comparisons", [])
                 if c["status"] != "PASS_NUMERIC_GATE"), None),
             "reason": row.get("reason")}
            for row in output
        ],
    }
    destination.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    if summary["status"] != "PASS_BOUNDED_MU3_RESPONSE_PARITY":
        raise SystemExit("Matched observation comparison NOT PASSED; inspect aggregate evidence")


if __name__ == "__main__":
    main()
