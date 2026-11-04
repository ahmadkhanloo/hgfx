"""Unit regression for prospectively declared M7 likelihood comparison contract."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2] / "paper" / "case_studies"
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("published_softmax", HERE / "compare_fullcohort_softmax.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_frozen_observation_tolerances():
    assert module.OBS_RTOL == 2e-11
    assert module.OBS_ATOL == 2e-13
    assert module.EXPECTED_CASES == 324
    assert module.EXPECTED_FIELDS == ("logp", "yhat", "res", "total_loglik")


def test_missingness_and_nonfinite_sign_not_falsely_matched():
    actual = np.asarray([np.nan, -np.inf, 0.4])
    expected = np.asarray([np.nan, -np.inf, 0.4])
    assert module.compare_field("logp", actual, expected)["status"] == "PASS_NUMERIC_GATE"
    wrong_sign = np.asarray([np.nan, np.inf, 0.4])
    failed = module.compare_field("logp", actual, wrong_sign)
    assert failed["status"] == "FAIL_NUMERIC_GATE"
    assert failed["first_divergence_trial_1_based"] == 2


def test_perceptual_trial_alignment_and_scalar_likelihood():
    arr = np.asarray([-1.5, -0.7, -0.2])
    ref = arr.reshape(-1, 1)
    assert module.compare_field("logp", arr, ref)["status"] == "PASS_NUMERIC_GATE"
    assert module.compare_field("total_loglik", np.asarray(-2.4), np.asarray([[-2.4]]))["status"] == "PASS_NUMERIC_GATE"
    bad = module.compare_field("logp", arr, np.asarray([-1.5, -0.7]))
    assert bad["status"] == "FAIL_SHAPE"


def test_numeric_mismatch_fails_without_relaxing_gate():
    a = np.asarray([-0.1, -0.2, -0.3])
    e = np.asarray([-0.1, -0.20001, -0.3])
    result = module.compare_field("logp", a, e)
    assert result["status"] == "FAIL_NUMERIC_GATE"
    assert result["failing_elements"] == 1
    assert result["first_divergence_trial_1_based"] == 2
