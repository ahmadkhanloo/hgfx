"""Regression fixtures for the first D02 cross-runtime numerical divergence."""

import numpy as np

from hgfx.core.transforms import EXPONENTIAL
from hgfx.math.logistic import sigmoid


# Frozen MATLAB R2026a / HGF Toolbox v8.2.0 evidence from M18 artifact
# 10323083435 (run 34774452669), before optimizer path divergence.

def test_d02_first_sigmoid_divergence_matches_matlab_oracle_exactly():
    muhat2 = np.float64(1.5490758290775484)
    expected_muhat1 = np.float64(0.8247802127606182)
    assert np.float64(sigmoid(muhat2, 1.0)) == expected_muhat1


def test_d02_observation_exponential_transform_matches_matlab_oracle_exactly():
    logze = np.float64(3.871201010907891)
    expected_ze = np.float64(48.000000000000014)
    assert np.float64(EXPONENTIAL.forward_scalar(logze)) == expected_ze
