"""Binary HGF level-1 update (B05)."""

from __future__ import annotations

import numpy as np

from hgfx.math.logistic import sigmoid


def hgf_binary_level1(
    u_k: float,
    ka_1: float,
    muhat_2: float,
    *,
    pu: tuple[float, float, float] | None = None,
    clamp_prediction: bool = True,
) -> tuple[float, float, float, float, float]:
    """Mirror the frozen binary-HGF level-1 update.

    ``pu`` is ``(alpha, eta0, eta1)`` and preserves the optional upstream
    perceptual-uncertainty branch.

    ``clamp_prediction`` defaults to the v8 unified/eHGF/uHGF behavior, which
    clips the Bernoulli prediction to ``[0.001, 0.999]``. The frozen v8.2.0
    documented ``setup.m`` uses ``addpath(genpath(...))`` and resolves the
    standard ``hgf_binary`` call to ``_original_models/hgf_binary.m``; that
    actual standard-HGF oracle does *not* apply this clamp. The standard model
    therefore passes ``False`` explicitly while eHGF/uHGF retain the clamp.
    """
    ka = np.float64(ka_1)
    muhat2 = np.float64(muhat_2)
    muhat1 = np.float64(sigmoid(ka * muhat2, 1.0))
    if clamp_prediction:
        muhat1 = np.maximum(muhat1, np.float64(0.001))
        muhat1 = np.minimum(muhat1, np.float64(0.999))
    with np.errstate(divide="ignore", invalid="ignore"):
        pihat1 = np.float64(1.0) / (muhat1 * (np.float64(1.0) - muhat1))

    u = np.float64(u_k)
    if pu is None:
        mu1 = u
    else:
        al, eta0, eta1 = (np.float64(value) for value in pu)
        with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
            und1 = np.exp(-((u - eta1) ** 2) / (np.float64(2.0) * al))
            und0 = np.exp(-((u - eta0) ** 2) / (np.float64(2.0) * al))
            mu1 = muhat1 * und1 / (
                muhat1 * und1 + (np.float64(1.0) - muhat1) * und0
            )

    pi1 = np.float64(np.inf)
    da1 = mu1 - muhat1
    return float(mu1), float(pi1), float(muhat1), float(pihat1), float(da1)
