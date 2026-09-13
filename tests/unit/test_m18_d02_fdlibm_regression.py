"""Regression fixtures for D02 cross-runtime numerical divergence."""

import numpy as np

from hgfx.core.transforms import EXPONENTIAL
from hgfx.math.logistic import sigmoid
from hgfx.models.hgf_binary import hgf_binary_unified


# Frozen MATLAB R2026a / HGF Toolbox v8.2.0 evidence from M18 artifacts.
# The first two scalar oracles are from artifact 10323083435 (run 34774452669).
# The theta-path state oracle is from artifact 10323968264 (run 34776952053),
# sample parameter_2_first_ridders_minus. No tolerance is used: these fixtures
# freeze exact binary64 values observed before optimizer-path amplification.


def test_d02_first_sigmoid_divergence_matches_matlab_oracle_exactly():
    muhat2 = np.float64(1.5490758290775484)
    expected_muhat1 = np.float64(0.8247802127606182)
    assert np.float64(sigmoid(muhat2, 1.0)) == expected_muhat1


def test_d02_observation_exponential_transform_matches_matlab_oracle_exactly():
    logze = np.float64(3.871201010907891)
    expected_ze = np.float64(48.000000000000014)
    assert np.float64(EXPONENTIAL.forward_scalar(logze)) == expected_ze


def test_d02_theta_path_matches_matlab_sahat_at_first_residual_divergence():
    # Exact D02 transformed perceptual vector at parameter 2, first Ridders-minus
    # sample. The first three official binary inputs are all one, so three trials
    # are sufficient to expose the first residual forward-state divergence.
    ptrans = np.asarray(
        [
            np.nan,
            0.0,
            1.0,
            np.nan,
            -2.3025850929940455,
            0.0,
            np.nan,
            0.0,
            0.0,
            0.0,
            0.0,
            np.nan,
            -3.0,
            1.0,
        ],
        dtype=np.float64,
    )
    _, inf_states = hgf_binary_unified(
        np.ones(3, dtype=np.float64),
        ptrans,
        update_type="ehgf",
        transformed=True,
        validate=False,
    )
    expected_sahat_trial3_level3 = np.float64(6.427379727890512)
    assert inf_states[2, 2, 1] == expected_sahat_trial3_level3
