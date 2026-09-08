"""Unified AR(1) binary HGF family from frozen HGF Toolbox 8.2.0."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.core.trials import build_time_axis
from hgfx.math.logistic import sigmoid
from hgfx.updates.binary_l1 import hgf_binary_level1
from hgfx.updates.binary_l2 import hgf_binary_level2
from hgfx.updates.precision_prediction import hgf_pihat, hgf_pihat_last
from hgfx.updates.prediction import hgf_prediction
from hgfx.updates.volatility import hgf_volatility_update
from hgfx.updates.volatility_pe import hgf_volatility_pe
from hgfx.validation.trajectory_checks import check_hgf_trajectories

from ._forward_common import first_input_column, ignored_mask


def _native_ar1_parameters(
    parameters,
    *,
    update_type: str,
    transformed: bool,
) -> tuple[np.ndarray, int]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    if update_type == "hgf":
        levels = (p.size + 1) / 6
    else:
        levels = (p.size + 1) / 7
    if levels != int(levels) or levels < 3:
        raise ValueError("Cannot determine number of AR1 binary HGF levels")
    l = int(levels)

    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[2 * l : 3 * l] = np.asarray(sigmoid(p[2 * l : 3 * l], 1.0))
        if update_type == "hgf":
            p[4 * l : 5 * l - 1] = np.exp(p[4 * l : 5 * l - 1])
        else:
            p[5 * l : 6 * l - 1] = np.exp(p[5 * l : 6 * l - 1])
    return p, l


def hgf_ar1_binary_unified(
    inputs,
    parameters,
    *,
    update_type: str,
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
    validate: bool = True,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Mirror frozen hgf_ar1_binary_unified.m."""

    if update_type not in {"hgf", "ehgf", "uhgf"}:
        raise ValueError("update_type must be 'hgf', 'ehgf', or 'uhgf'")

    values, input_array = first_input_column(inputs)
    p, l = _native_ar1_parameters(
        parameters,
        update_type=update_type,
        transformed=transformed,
    )
    ignored = ignored_mask(values, ignored_trials)

    if update_type == "hgf":
        mu_0 = p[:l]
        sa_0 = p[l : 2 * l]
        phi = p[2 * l : 3 * l]
        m = p[3 * l : 4 * l]
        rho = np.zeros(l, dtype=np.float64)
        ka = p[4 * l : 5 * l - 1]
        om = p[5 * l - 1 : 6 * l - 2]
        th = np.exp(np.float64(p[6 * l - 2]))
    else:
        mu_0 = p[:l]
        sa_0 = p[l : 2 * l]
        phi = p[2 * l : 3 * l]
        m = p[3 * l : 4 * l]
        rho = p[4 * l : 5 * l]
        ka = p[5 * l : 6 * l - 1]
        om = p[6 * l - 1 : 7 * l - 2]
        th = np.exp(np.float64(p[7 * l - 2]))

    u = np.concatenate(([0.0], values))
    n = u.size
    t = build_time_axis(input_array, irregular_intervals=irregular_intervals)

    mu = np.full((n, l), np.nan, dtype=np.float64)
    pi = np.full((n, l), np.nan, dtype=np.float64)
    muhat = np.full((n, l), np.nan, dtype=np.float64)
    pihat = np.full((n, l), np.nan, dtype=np.float64)
    v = np.full((n, l), np.nan, dtype=np.float64)
    w = np.full((n, l - 1), np.nan, dtype=np.float64)
    da = np.full((n, l), np.nan, dtype=np.float64)

    mu[0, 0] = sigmoid(mu_0[0], 1.0)
    pi[0, 0] = np.inf
    mu[0, 1:] = mu_0[1:]
    pi[0, 1:] = 1.0 / sa_0[1:]

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

        muhat[k, 1] = hgf_prediction(
            mu[k - 1, 1],
            t[k],
            rho=rho[1],
            phi=phi[1],
            m=m[1],
        )
        (
            mu[k, 0],
            pi[k, 0],
            muhat[k, 0],
            pihat[k, 0],
            da[k, 0],
        ) = hgf_binary_level1(u[k], ka[0], muhat[k, 1])

        pihat[k, 1] = hgf_pihat(
            pi[k - 1, 1],
            1.0,
            ka[1],
            mu[k - 1, 2],
            om[1],
        )
        pi[k, 1], mu[k, 1], da[k, 1] = hgf_binary_level2(
            muhat[k, 1],
            pihat[k, 1],
            ka[0],
            pihat[k, 0],
            da[k, 0],
        )

        for j in range(2, l - 1):
            muhat[k, j] = hgf_prediction(
                mu[k - 1, j],
                t[k],
                rho=rho[j],
                phi=phi[j],
                m=m[j],
            )
            pihat[k, j] = hgf_pihat(
                pi[k - 1, j],
                t[k],
                ka[j],
                mu[k - 1, j + 1],
                om[j],
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
                update_type,
            )
            da[k, j] = hgf_volatility_pe(
                pi[k, j], mu[k, j], muhat[k, j], pihat[k, j]
            )

        last = l - 1
        muhat[k, last] = hgf_prediction(
            mu[k - 1, last],
            t[k],
            rho=rho[last],
            phi=phi[last],
            m=m[last],
        )
        pihat[k, last] = hgf_pihat_last(pi[k - 1, last], t[k], th)
        v[k, last] = t[k] * th
        # Frozen AR1 source uses the previous posterior here for all update types.
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
            update_type,
        )
        da[k, last] = hgf_volatility_pe(
            pi[k, last], mu[k, last], muhat[k, last], pihat[k, last]
        )

    sgmmu2 = np.asarray(sigmoid(ka[0] * mu[:, 1], 1.0), dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr1 = np.diff(sgmmu2) / (u[1:] - sgmmu2[1:])
    lr1[da[1:, 0] == 0] = 0.0

    mu = mu[1:]
    pi = pi[1:]
    if update_type == "hgf" and validate:
        check_hgf_trajectories(mu, pi, 16.0, columns=range(1, l))
    muhat = muhat[1:]
    pihat = pihat[1:]
    v = v[1:]
    w = w[1:]
    da = da[1:]

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
        "ud": mu - muhat,
    }

    psi = np.full((n - 1, l), np.nan, dtype=np.float64)
    psi[:, 1] = 1.0 / pi[:, 1]
    psi[:, 2:l] = pihat[:, 1 : l - 1] / pi[:, 2:l]
    traj["psi"] = psi

    epsi = np.full((n - 1, l), np.nan, dtype=np.float64)
    epsi[:, 1:l] = psi[:, 1:l] * da[:, : l - 1]
    traj["epsi"] = epsi

    wt = np.full((n - 1, l), np.nan, dtype=np.float64)
    wt[:, 0] = lr1
    wt[:, 1] = psi[:, 1]
    wt[:, 2:l] = 0.5 * (v[:, 1 : l - 1] * ka[1 : l - 1]) * psi[:, 2:l]
    traj["wt"] = wt

    inf_states = np.stack((muhat, sahat, mu, sa), axis=2)
    return traj, inf_states


def hgf_ar1_binary(inputs, parameters, **kwargs):
    return hgf_ar1_binary_unified(inputs, parameters, update_type="hgf", **kwargs)


def ehgf_ar1_binary(inputs, parameters, **kwargs):
    return hgf_ar1_binary_unified(inputs, parameters, update_type="ehgf", **kwargs)


def uhgf_ar1_binary(inputs, parameters, **kwargs):
    return hgf_ar1_binary_unified(inputs, parameters, update_type="uhgf", **kwargs)
