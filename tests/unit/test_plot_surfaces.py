import matplotlib
import numpy as np

matplotlib.use("Agg")

from hgfx.compat.result import CompatibilityResult, MatlabStruct
from hgfx.plotting import (
    fit_plotCorr,
    fit_plotResidualDiagnostics,
    prepare_fit_correlation_surface,
    prepare_residual_diagnostics,
)


def _result():
    return CompatibilityResult(
        kind="fit",
        u=np.arange(4.0),
        c_prc=MatlabStruct({"priorsas": np.array([1.0, 0.0])}),
        c_obs=MatlabStruct({"priorsas": np.array([1.0])}),
        p_prc=MatlabStruct(
            {
                "alpha": 1.0,
                "beta": 2.0,
                "p": np.array([1.0, 2.0]),
                "ptrans": np.array([1.0, 2.0]),
            }
        ),
        p_obs=MatlabStruct(
            {
                "ze": 0.5,
                "p": np.array([0.5]),
                "ptrans": np.array([-0.7]),
            }
        ),
        optim=MatlabStruct(
            {
                "Corr": np.array([[1.0, 0.25], [0.25, 1.0]]),
                "Sigma": np.array([[2.0, 0.5], [0.5, 3.0]]),
                "res": np.array([0.1, -0.2, 0.3, -0.1]),
                "resAC": np.array([1.0, 0.5, 0.25, 0.5]),
                "yhat": np.array([0.2, 0.4, 0.6, 0.8]),
            }
        ),
    )


def test_correlation_surface_labels_follow_matlab_field_expansion():
    surface = prepare_fit_correlation_surface(_result())
    assert surface["labels"] == ("alpha", "ze")
    np.testing.assert_array_equal(surface["Corr"], np.array([[1.0, 0.25], [0.25, 1.0]]))


def test_residual_surface_matches_matlab_fftshift_and_lags():
    data = prepare_residual_diagnostics(_result())
    np.testing.assert_array_equal(data["resAC_shifted"], np.array([0.25, 0.5, 1.0, 0.5]))
    np.testing.assert_array_equal(data["lags"], np.array([-2, -1, 0, 1]))


def test_matlab_plot_aliases_smoke():
    import matplotlib.pyplot as plt

    fig1, _ = fit_plotCorr(_result())
    fig2, _ = fit_plotResidualDiagnostics(_result())
    plt.close(fig1)
    plt.close(fig2)
