from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from hgfx.diagnostics.recovery import fit_binary_variant


CASE_ID = "PR-hgf_binary-T256-S0.35-R0"
CASE_SHA = "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5"
MATLAB_FINAL = np.array(
    [-1.681508358629877, -2.813834229811849, 4.040575231980671],
    dtype=np.float64,
)
MATLAB_NEG_LJ = 13.292404684084028
RTOL = 3e-8
ATOL = 3e-10


def _frozen_case() -> dict:
    root = Path(__file__).resolve().parents[2]
    fixture = json.loads(
        (root / "reference/validation/m18_s7_paired_recovery/hgf_anomaly_fixture.json")
        .read_text(encoding="utf-8")
    )
    matches = [case for case in fixture["cases"] if case["case_id"] == CASE_ID]
    assert len(matches) == 1
    case = matches[0]
    assert case["case_sha256"] == CASE_SHA
    return case


def test_s8_hgf_r0_reproduces_stable_matlab_optimizer_endpoint() -> None:
    """Regression for the S7 HGFX-only optimizer mismatch localized in S8.

    The immutable data are from the original S7 run 34856542785.  The MATLAB
    endpoint is stable under all six preregistered +/- one-local-spacing start
    perturbations in anomaly-review run 34883973822, so this is deliberately a
    product regression rather than a reference-limitation test.
    """

    case = _frozen_case()
    fit = fit_binary_variant(
        np.asarray(case["y"], dtype=np.float64),
        np.asarray(case["u"], dtype=np.float64),
        "hgf_binary",
    )

    assert fit.optimizer.termination in {"tol_arg", "tol_grad"}
    np.testing.assert_allclose(fit.final_free, MATLAB_FINAL, rtol=RTOL, atol=ATOL)
    np.testing.assert_allclose(
        fit.objective.neg_log_joint,
        MATLAB_NEG_LJ,
        rtol=RTOL,
        atol=ATOL,
    )
