"""REV-1.2 targeted statistical tests; historical fits are never rerun."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "rev12", ROOT/"tools/compute_compstat_recovery_uncertainty.py")
assert SPEC and SPEC.loader
REV12 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REV12)


def test_exact_clopper_pearson():
    assert REV12.exact_ci(0, 12)[0] == 0
    assert REV12.exact_ci(12, 12)[1] == 1
    lo, hi = REV12.exact_ci(4, 12)
    assert lo == pytest.approx(0.09924609114958331, abs=1e-12)
    assert hi == pytest.approx(0.6511244935811844, abs=1e-12)


def test_cluster_bootstrap_preserves_pairs():
    truth = np.tile(np.arange(12, dtype=float).reshape(12,1,1), (1,2,3))
    fitted = truth+0.1
    idx = np.tile(np.arange(12)[::-1], (REV12.N_BOOT,1))
    corr, rmse = REV12.bootstats(truth.reshape(24,3), fitted.reshape(24,3), idx)
    assert corr.shape == rmse.shape == (REV12.N_BOOT,3)
    assert np.allclose(corr,1)
    assert np.all(rmse > 0)


def test_nonfinite_does_not_produce_interval():
    draws = np.full(REV12.N_BOOT, np.nan)
    draws[:REV12.VALID_MIN-1] = 1.
    result = REV12.ci_from_bootstrap(draws)
    assert result["ci95"] is None
    assert not result["quality_ok"]


def test_missing_original_archive_is_error(tmp_path):
    with pytest.raises(ValueError, match="missing, extra or renamed"):
        REV12.read_archives(tmp_path, {"raw_artifacts":[]})


def test_reference_formula():
    truth = np.array([[1,2,3],[2,3,4],[3,4,5]], dtype=float)
    r, srmse = REV12.summaries(truth, truth.copy())
    assert np.allclose(r, 1)
    assert np.allclose(srmse, 0)
