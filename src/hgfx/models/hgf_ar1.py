"""Continuous AR(1) HGF from frozen HGF Toolbox 8.2.0."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.core.trials import build_time_axis
from hgfx.math.logistic import sigmoid
from hgfx.updates.precision_prediction import hgf_pihat, hgf_pihat_last
from hgfx.updates.prediction import hgf_prediction
from hgfx.updates.volatility import hgf_volatility_update
from hgfx.updates.volatility_pe import hgf_volatility_pe
from hgfx.validation.trajectory_checks import check_hgf_trajectories

from ._forward_common import first_input_column, ignored_mask


def _native_ar1_parameters(parameters, *, transformed: bool) -> tuple[np.ndarray, int]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    levels = p.size / 6
    if levels != int(levels) or levels < 2:
        raise ValueError("Cannot determine number of continuous AR1 HGF levels")
    l = int(levels)
    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[2 * l : 3 * l] = np.asarray(sigmoid(p[2 * l : 3 * l], 1.0), dtype=np.float64)
        p[4 * l : 5 * l - 1] = np.exp(p[4 * l : 5 * l - 1])
        p[6 * l - 1] = np.exp(p[6 * l - 1])
    return p, l


def hgf_ar1(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
    validate: bool = True,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Mirror frozen hgf_ar1.m."""

    values, input_array = first_input_column(inputs)
    p, l = _native_ar1_parameters(parameters, transformed=transformed)
    ignored = ignored_mask(values, ignored_trials)

    mu_0 = p[:l]
    sa_0 = p[l : 2 * l]
    phi = p[2 * l : 3 * l]
    m = p[3 * l : 4 * l]
    ka = p[4 * l : 5 * l - 1]
    om = p[5 * l - 1 : 6 * l - 2]
    th = np.exp(np.float64(p[6 * l - 2]))
    al = np.float64(p[6 * l - 1])

    u = np.concatenate(([0.0], values))
    n = u.size
    # Frozen hgf_ar1.m reduces r.u to its first column before constructing
    # the time axis. With irregular_intervals=true the explicit error is
    # caught by its broad catch block, whose fallback sees the same
    # single-column u and therefore sets t=ones. Preserve that source quirk.
    t = np.ones(n, dtype=np.float64)

    mu = np.full((n, l), np.nan, dtype=np.float64)
    pi = np.full((n, l), np.nan, dtype=np.float64)
    muhat = np.full((n, l), np.nan, dtype=np.float64)
    pihat = np.full((n, l), np.nan, dtype=np.float64)
    v = np.full((n, l), np.nan, dtype=np.float64)
    w = np.full((n, l - 1), np.nan, dtype=np.float64)
    da = np.full((n, l), np.nan, dtype=np.float64)
    dau = np.full(n, np.nan, dtype=np.float64)

    mu[0] = mu_0
    pi[0] = 1.0 / sa_0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            mu[k] = mu[k - 1]
            pi[k] = pi[k - 1]
            muhat[k] = muhat[k - 1]
            pihat[k] = pihat[k - 1]
            v[k] = v[k - 1]
            w[k] = w[k - 1]
            da[k] = da[k - 1]
            continue

        muhat[k, 0] = hgf_prediction(
            mu[k - 1, 0], t[k], phi=phi[0], m=m[0]
        )
        pihat[k, 0] = hgf_pihat(
            pi[k - 1, 0], t[k], ka[0], mu[k - 1, 1], om[0]
        )
        dau[k] = u[k] - muhat[k, 0]
        pi[k, 0] = pihat[k, 0] + 1.0 / al
        mu[k, 0] = (
            muhat[k, 0]
            + (1.0 / pihat[k, 0])
            * (1.0 / (1.0 / pihat[k, 0] + al))
            * dau[k]
        )
        da[k, 0] = (
            (1.0 / pi[k, 0] + (mu[k, 0] - muhat[k, 0]) ** 2)
            * pihat[k, 0]
            - 1.0
        )

        if l > 2:
            for j in range(1, l - 1):
                muhat[k, j] = hgf_prediction(
                    mu[k - 1, j], t[k], phi=phi[j], m=m[j]
                )
                pihat[k, j] = hgf_pihat(
                    pi[k - 1, j], t[k], ka[j], mu[k - 1, j + 1], om[j]
                )
                pi[k, j], mu[k, j], v[k, j - 1], w[k, j - 1] = hgf_volatility_update(
                    muhat[k, j],
                    pihat[k, j],
                    ka[j - 1],
                    pihat[k, j - 1],
                    da[k, j - 1],
                    mu[k - 1, j],
                    om[j - 1],
                    pi[k - 1, j - 1],
                    pi[k, j - 1],
                    mu[k, j - 1],
                    muhat[k, j - 1],
                    t[k],
                    "hgf",
                )
                da[k, j] = hgf_volatility_pe(
                    pi[k, j], mu[k, j], muhat[k, j], pihat[k, j]
                )

        last = l - 1
        muhat[k, last] = hgf_prediction(
            mu[k - 1, last], t[k], phi=phi[last], m=m[last]
        )
        pihat[k, last] = hgf_pihat_last(pi[k - 1, last], t[k], th)
        v[k, last] = t[k] * th
        v[k, last - 1] = t[k] * np.exp(
            ka[last - 1] * mu[k - 1, last] + om[last - 1]
        )
        pi[k, last], mu[k, last], _, w[k, last - 1] = hgf_volatility_update(
            muhat[k, last],
            pihat[k, last],
            ka[last - 1],
            pihat[k, last - 1],
            da[k, last - 1],
            mu[k - 1, last],
            om[last - 1],
            pi[k - 1, last - 1],
            pi[k, last - 1],
            mu[k, last - 1],
            muhat[k, last - 1],
            t[k],
            "hgf",
        )
        da[k, last] = hgf_volatility_pe(
            pi[k, last], mu[k, last], muhat[k, last], pihat[k, last]
        )

    mu = mu[1:]
    pi = pi[1:]
    if validate:
        check_hgf_trajectories(mu, pi, 256.0, columns=None)
    muhat = muhat[1:]
    pihat = pihat[1:]
    v = v[1:]
    w = w[1:]
    da = da[1:]
    dau = dau[1:]

    sa = 1.0 / pi
    sahat = 1.0 / pihat
    traj = {
        "mu": mu,
        "sa": sa,
        "muhat": muhat,
        "sahat": sahat,
        "v": v,
        "w": w,
        "da": da,
        "dau": dau,
        "ud": mu - muhat,
    }

    psi = np.full((n - 1, l), np.nan, dtype=np.float64)
    psi[:, 0] = 1.0 / (al * pi[:, 0])
    psi[:, 1:l] = pihat[:, : l - 1] / pi[:, 1:l]
    traj["psi"] = psi

    epsi = np.full((n - 1, l), np.nan, dtype=np.float64)
    epsi[:, 0] = psi[:, 0] * dau
    epsi[:, 1:l] = psi[:, 1:l] * da[:, : l - 1]
    traj["epsi"] = epsi

    wt = np.full((n - 1, l), np.nan, dtype=np.float64)
    wt[:, 0] = psi[:, 0]
    wt[:, 1:l] = 0.5 * (v[:, : l - 1] * ka[: l - 1]) * psi[:, 1:l]
    traj["wt"] = wt

    inf_states = np.stack((muhat, sahat, mu, sa), axis=2)
    return traj, inf_states


forward = hgf_ar1
