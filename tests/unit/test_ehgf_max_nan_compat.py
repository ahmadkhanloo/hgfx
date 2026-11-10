"""Golden eHGF-019 MATLAB max-with-NaN compatibility regression.

Source: unmodified 2026-11-10 original fixed synthetic Panel G manifest,
authentic 128-trial MATLAB/HGFX trace (run 42797497943, artifact 13754932663).
This is a *single-step source-backed golden unit test* against development
1.1.0b1, NOT a rerun of original 600-case HGFX/MATLAB scientific evidence.
"""
from __future__ import annotations

import numpy as np
import pytest

from hgfx.updates.volatility import hgf_volatility_update


def original_trial8_level3_operands():
    """Exact original archived trial 8 (zero-based) scalar operands only."""
    return dict(
        muhat_j=5.381279434383974,
        pihat_j=1.0 / 8.209456713045242,
        ka_jm1=1.0,  # frozen transformed log(kappa_2)=0
        pihat_jm1=1.0 / 887.5497877367073,
        da_jm1=248.37874264484864,
        mu_prev_j=5.381279434383974,
        om_jm1=1.391502762318833,
        pi_prev_jm1=1.0 / 13.810357782664 ,
        pi_jm1=1.0 / 470.4338539693152,
        mu_jm1=459.7094265678726,
        muhat_jm1=-10.253993547473282,
        t_k=1.0,
    )


def test_ehgf019_original_trial8_max_nan_matches_matlab_frozen_precision():
    operands=original_trial8_level3_operands()
    predicted=operands["pihat_j"]
    pi,mu,v,w=hgf_volatility_update(**operands,update_type="ehgf")
    assert np.isfinite(mu) and mu==pytest.approx(1009.0446083588881,abs=1e-10)
    assert np.isfinite(v) and np.isfinite(w)
    assert np.isfinite(pi), "Old np.maximum(0, NaN) incorrectly creates NaN precision"
    assert pi==predicted, (
        "Frozen MATLAB max(0, NaN) keeps zero correction; source archive "
        "has sa3=sahat3=8.209456713045242"
    )


def test_ehgf_max_nan_semantics_are_not_numpy_maximum():
    assert np.isnan(np.maximum(np.float64(0.0),np.float64("nan")))
    assert np.fmax(np.float64(0.0),np.float64("nan"))==0.0


def test_ehgf_finite_precision_update_remains_finite():
    scalar=original_trial8_level3_operands()
    scalar["da_jm1"]=0.0
    pi,mu,v,w=hgf_volatility_update(**scalar,update_type="ehgf")
    assert np.isfinite(pi)
    assert pi>=scalar["pihat_j"]
