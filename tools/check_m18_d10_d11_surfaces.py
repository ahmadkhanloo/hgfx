#!/usr/bin/env python3
"""Validate D10 Corr/Sigma and D11 residual diagnostic surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.result import CompatibilityResult, MatlabStruct
from hgfx.plotting import prepare_fit_correlation_surface, prepare_residual_diagnostics

PROTOCOL = "m18-d10-d11-surfaces-2"
FIXTURE = "synthetic_fit_v2"
RTOL = 3e-8
ATOL = 3e-10


def decode_numeric_struct(value: dict[str, Any]) -> MatlabStruct:
    return MatlabStruct({key: _array(item) for key, item in value.items()})


def flatten_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        output: list[str] = []
        for item in value:
            output.extend(flatten_strings(item))
        return output
    raise TypeError(f"Unexpected label encoding: {type(value)!r}")


def compare(label: str, actual, expected) -> dict[str, Any]:
    a = np.asarray(actual, dtype=np.float64)
    e = _array(expected)
    if a.shape != e.shape:
        if a.size == e.size:
            e = e.reshape(a.shape)
        else:
            return {"label": label, "pass": False, "reason": "shape", "actual_shape": list(a.shape), "expected_shape": list(e.shape)}
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    diff = np.abs(a - e)
    finite = np.isfinite(diff)
    if np.all(close):
        return {"label": label, "pass": True, "max_abs": float(np.max(diff[finite])) if np.any(finite) else 0.0}
    idx = tuple(int(x) for x in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = a[idx] if idx else a
    ev = e[idx] if idx else e
    return {"label": label, "pass": False, "index": list(idx), "hgfx": float(av), "matlab": float(ev), "abs_diff": float(abs(av-ev))}


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference.get("protocol") != PROTOCOL or reference.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("D10/D11 frozen protocol/reference mismatch")
    if reference.get("case_id") != "D10_D11_surfaces" or reference.get("fixture_id") != FIXTURE:
        raise ValueError("D10/D11 frozen fixture mismatch")

    est = reference["est"]
    result = CompatibilityResult(
        kind="fit",
        u=_array(est["u"]),
        c_prc=MatlabStruct({"priorsas": _array(est["c_prc"]["priorsas"])}),
        c_obs=MatlabStruct({"priorsas": _array(est["c_obs"]["priorsas"])}),
        p_prc=decode_numeric_struct(est["p_prc"]),
        p_obs=decode_numeric_struct(est["p_obs"]),
        optim=MatlabStruct(
            {
                "Corr": _array(est["optim"]["Corr"]),
                "Sigma": _array(est["optim"]["Sigma"]),
                "res": _array(est["optim"]["res"]),
                "resAC": _array(est["optim"]["resAC"]),
                "yhat": _array(est["optim"]["yhat"]),
            }
        ),
    )

    d10 = prepare_fit_correlation_surface(result)
    d11 = prepare_residual_diagnostics(result)
    expected_labels = flatten_strings(reference["d10"]["labels"])
    label_pass = list(d10["labels"]) == expected_labels
    checks = [
        {"label": "d10.labels", "pass": label_pass, "hgfx": list(d10["labels"]), "matlab": expected_labels},
        compare("d10.Corr", d10["Corr"], reference["d10"]["Corr"]),
        compare("d10.Sigma", d10["Sigma"], reference["d10"]["Sigma"]),
        compare("d11.res", d11["res"], reference["d11"]["res"]),
        compare("d11.resAC_shifted", d11["resAC_shifted"], reference["d11"]["resAC_shifted"]),
        compare("d11.lags", d11["lags"], reference["d11"]["lags"]),
        compare("d11.yhat", d11["yhat"], reference["d11"]["yhat"]),
    ]
    failures = [item for item in checks if not item["pass"]]
    classification = "PASS" if not failures else "IMPLEMENTATION_MISMATCH"
    output = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D10_D11_surfaces",
        "fixture_id": FIXTURE,
        "classification": classification,
        "tolerance": {"rtol": RTOL, "atol": ATOL},
        "checks": checks,
        "failures": failures,
        "rendering_note": "Parity is gated on plotted data/labels, not backend-specific pixels or window geometry.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"classification": classification, "failures": failures[:3]}), flush=True)
    return 0 if classification == "PASS" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
