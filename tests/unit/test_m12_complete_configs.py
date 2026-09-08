from __future__ import annotations

import numpy as np

from hgfx.compat import (
    hgf_ar1_config,
    hgf_binary_mab_config,
    hgf_ar1_mab_config,
    hgf_ar1_binary_mab_config,
    ehgf_ar1_binary_mab_config,
    uhgf_ar1_binary_mab_config,
    hgf_jget_config,
    ehgf_jget_config,
    uhgf_jget_config,
    hgf_categorical_config,
    hgf_categorical_norm_config,
    hgf_whatworld_config,
    hgf_whichworld_config,
    bayes_optimal_config,
    bayes_optimal_binary_config,
    bayes_optimal_categorical_config,
    bayes_optimal_whatworld_config,
    bayes_optimal_whichworld_config,
    rs_belief_config,
    rs_precision_config,
    rs_surprise_config,
    rs_precision_whatworld_config,
    squared_pe_config,
    condhalluc_obs_config,
    condhalluc_obs2_config,
    condhalluc_obs3_config,
    softmax_wld_config,
    softmax_mu3_wld_config,
    logrt_linear_whatworld_config,
)


def test_all_m12_configs_are_public_and_transformable() -> None:
    configs = [
        hgf_ar1_config(),
        hgf_binary_mab_config(),
        hgf_ar1_mab_config(),
        hgf_ar1_binary_mab_config(),
        ehgf_ar1_binary_mab_config(),
        uhgf_ar1_binary_mab_config(),
        hgf_jget_config(),
        ehgf_jget_config(),
        uhgf_jget_config(),
        hgf_categorical_config(),
        hgf_categorical_norm_config(),
        hgf_whatworld_config(),
        hgf_whichworld_config(),
        bayes_optimal_config(),
        bayes_optimal_binary_config(),
        bayes_optimal_categorical_config(),
        bayes_optimal_whatworld_config(),
        bayes_optimal_whichworld_config(),
        rs_belief_config(),
        rs_precision_config(),
        rs_surprise_config(),
        rs_precision_whatworld_config(),
        squared_pe_config(),
        condhalluc_obs_config(),
        condhalluc_obs2_config(),
        condhalluc_obs3_config(),
        softmax_wld_config(),
        softmax_mu3_wld_config(),
        logrt_linear_whatworld_config(),
    ]
    for cfg in configs:
        assert len(cfg.parameters) == cfg.priormus.size == cfg.priorsas.size
        if cfg.parameters:
            vector = np.asarray(cfg.priormus, dtype=np.float64)
            finite = np.isfinite(vector)
            # Replace placeholder/nonfinite entries only for transform smoke testing.
            smoke = vector.copy()
            smoke[~finite] = 0.0
            native = cfg.transformed_to_native(smoke)
            assert native.shape == smoke.shape


def test_bounded_sigmoid_configs_match_frozen_upper_bounds() -> None:
    cat = hgf_categorical_config()
    native = cat.transformed_to_native(cat.priormus)
    assert np.isclose(native[-3], 1.0)   # kappa: 2/(1+exp(0))
    assert np.isclose(native[-1], 0.05)  # theta: .1/(1+exp(0))

    which = hgf_whichworld_config()
    native = which.transformed_to_native(which.priormus)
    assert np.isclose(native[-5], 1.0)
    assert np.isclose(native[-3], 1.0)


def test_bayes_optimal_configs_have_no_parameters() -> None:
    for cfg in (
        bayes_optimal_config(),
        bayes_optimal_binary_config(),
        bayes_optimal_categorical_config(),
        bayes_optimal_whatworld_config(),
        bayes_optimal_whichworld_config(),
    ):
        assert cfg.parameters == ()
        assert cfg.priormus.size == 0
        assert cfg.priorsas.size == 0
