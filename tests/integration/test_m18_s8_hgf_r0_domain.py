from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from hgfx.compat.configs import hgf_binary_config
from hgfx.models.hgf_binary import hgf_binary
from hgfx.updates.binary_l1 import hgf_binary_level1

CASE_ID = "PR-hgf_binary-T256-S0.35-R0"
CASE_SHA256 = "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5"
R0_RIDDERS_PLUS_FREE = (
    (-0.80072897574871538, -3.4696680688370498),
    (-1.0553586053783448, -3.4696680688370498),
    (-1.1518092226622956, -3.4696680688370498),
)


def _frozen_r0_inputs() -> np.ndarray:
    root = Path(__file__).resolve().parents[2]
    fixture_path = (
        root
        / "reference"
        / "validation"
        / "m18_s7_paired_recovery"
        / "hgf_anomaly_fixture.json"
    )
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    matches = [case for case in fixture["cases"] if case["case_id"] == CASE_ID]
    assert len(matches) == 1
    case = matches[0]
    assert case["case_sha256"] == CASE_SHA256
    return np.asarray(case["u"], dtype=np.float64)


def test_standard_hgf_level1_can_follow_unclamped_frozen_original() -> None:
    raw = hgf_binary_level1(
        0.0,
        1.0,
        20.0,
        clamp_prediction=False,
    )[2]
    clamped = hgf_binary_level1(0.0, 1.0, 20.0)[2]
    assert raw > 0.999
    assert raw != 0.999
    assert clamped == 0.999


@pytest.mark.parametrize("om2, log_theta", R0_RIDDERS_PLUS_FREE)
def test_standard_hgf_rejects_frozen_r0_negative_precision_points(
    om2: float,
    log_theta: float,
) -> None:
    inputs = _frozen_r0_inputs()
    parameters = hgf_binary_config().priormus.copy()
    # Frozen standard-HGF free perceptual coordinates are transformed indices
    # 12 and 13 (zero-based) in the 14-element perceptual vector.
    parameters[12] = om2
    parameters[13] = log_theta

    with pytest.raises(ValueError, match="Negative posterior precision"):
        hgf_binary(inputs, parameters, transformed=True)
