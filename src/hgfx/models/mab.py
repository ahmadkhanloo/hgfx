"""Multi-armed bandit HGF families from frozen HGF Toolbox 8.2.0."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.core.trials import build_time_axis
from hgfx.math.logistic import logit, sigmoid
from hgfx.updates.volatility import hgf_volatility_update
from hgfx.validation.trajectory_checks import check_hgf_trajectories


def _mab_inputs(inputs, choices, n_bandits: int):
    arr = np.asarray(inputs, dtype=np.float64)
    if arr.ndim == 1:
        values = arr
        matrix = arr[:, None]
    elif arr.ndim == 2 and arr.shape[1] >= 1:
        values = arr[:, 0]
        matrix = arr
    else:
        raise ValueError("MAB inputs must be 1D or a matrix")

    if choices is None:
        if matrix.shape[1] < 2:
            raise ValueError("choices are required unless input column 2 contains them")
        choice = matrix[:, 1]
    else:
        choice = np.asarray(choices, dtype=np.float64).reshape(-1)
    if choice.size != values.size:
        raise ValueError("choices and inputs must have equal trial counts")
    valid = ~np.isnan(choice)
    idx = choice[valid].astype(np.int64)
    if np.any((idx < 1) | (idx > n_bandits)):
        raise ValueError("MAB choices must be MATLAB-style 1..n_bandits")
    return values, matrix, choice


def _ignored(n: int, values, choices, ignored_trials):
    mask = np.isnan(np.asarray(values, dtype=np.float64)) | np.isnan(np.asarray(choices, dtype=np.float64))
    if ignored_trials is not None:
        for index in ignored_trials:
            if index < 0 or index >= n:
                raise IndexError(f"ignored trial index out of range: {index}")
            mask[index] = True
    return mask


def _selected(matrix: np.ndarray, choices_zero: np.ndarray, regular: np.ndarray) -> np.ndarray:
    out = np.full(matrix.shape[0], np.nan, dtype=np.float64)
    idx = np.flatnonzero(regular)
    out[idx] = matrix[idx, choices_zero[idx]]
    return out


def _mab_outputs(mu, pi, muhat, pihat, v, w, da, *, ka, choices_zero, regular, binary):
    n, l, _ = mu.shape
    traj = {
        "mu": mu,
        "sa": 1.0 / pi,
        "muhat": muhat,
        "sahat": 1.0 / pihat,
        "v": v,
        "w": w,
        "da": da,
        "ud": mu - muhat,
    }

    psi = np.full((n, l), np.nan, dtype=np.float64)
    selected_pi2 = _selected(pi[:, 1, :], choices_zero, regular)
    psi[regular, 1] = 1.0 / selected_pi2[regular]
    for level in range(2, l):
        selected_prev_pihat = _selected(pihat[:, level - 1, :], choices_zero, regular)
        selected_pi = _selected(pi[:, level, :], choices_zero, regular)
        psi[regular, level] = selected_prev_pihat[regular] / selected_pi[regular]
    traj["psi"] = psi

    epsi = np.full((n, l), np.nan, dtype=np.float64)
    epsi[:, 1:l] = psi[:, 1:l] * da[:, : l - 1]
    traj["epsi"] = epsi

    wt = np.full((n, l), np.nan, dtype=np.float64)
    if binary:
        selected_mu2 = _selected(mu[:, 1, :], choices_zero, regular)
        selected_mu1hat = _selected(muhat[:, 0, :], choices_zero, regular)
        upd1 = np.asarray(sigmoid(ka[0] * selected_mu2, 1.0), dtype=np.float64) - selected_mu1hat
        with np.errstate(divide="ignore", invalid="ignore"):
            wt[regular, 0] = upd1[regular] / da[regular, 0]
        wt[:, 1] = psi[:, 1]
        if l > 2:
            wt[:, 2:l] = 0.5 * (v[:, 1 : l - 1] * ka[1 : l - 1]) * psi[:, 2:l]
    traj["wt"] = wt

    inf_states = np.stack((muhat, 1.0 / pihat, mu, 1.0 / pi), axis=3)
    return traj, inf_states


def hgf_binary_mab(
    inputs,
    parameters,
    *,
    choices=None,
    n_bandits: int = 3,
    coupled: bool = False,
    transformed: bool = False,
    irregular_intervals: bool = False,
    ignored_trials: Sequence[int] | None = None,
    validate: bool = True,
):
    """Mirror frozen hgf_binary_mab.m."""

    values, input_matrix, choices_raw = _mab_inputs(inputs, choices, n_bandits)
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    levels = (p.size + 1) / 5
    if levels != int(levels) or levels < 3:
        raise ValueError("Cannot determine hgf_binary_mab levels")
    l = int(levels)
    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[3 * l : 4 * l - 1] = np.exp(p[3 * l : 4 * l - 1])

    if coupled and n_bandits != 2:
        raise ValueError("coupled binary MAB is only defined for two bandits")

    mu0 = p[:l]
    sa0 = p[l : 2 * l]
    rho = p[2 * l : 3 * l]
    ka = p[3 * l : 4 * l - 1]
    om = p[4 * l - 1 : 5 * l - 2]
    theta = np.exp(p[5 * l - 2])

    ignored = _ignored(values.size, values, choices_raw, ignored_trials)
    choices_zero = np.where(np.isnan(choices_raw), 0, choices_raw.astype(np.int64) - 1)
    u = np.concatenate(([0.0], values))
    y = np.concatenate(([0], choices_zero + 1))
    t = build_time_axis(input_matrix, irregular_intervals=irregular_intervals)
    n = values.size + 1

    mu = np.full((n, l, n_bandits), np.nan)
    pi = np.full_like(mu, np.nan)
    muhat = np.full_like(mu, np.nan)
    pihat = np.full_like(mu, np.nan)
    v = np.full((n, l), np.nan)
    w = np.full((n, l - 1), np.nan)
    da = np.full((n, l), np.nan)

    mu[0, 0, :] = sigmoid(mu0[1], 1.0)
    pi[0, 0, :] = np.inf
    mu[0, 1:, :] = mu0[1:, None]
    pi[0, 1:, :] = (1.0 / sa0[1:])[:, None]

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

        arm = choices_zero[trial]
        muhat[k, 1, :] = mu[k - 1, 1, :] + t[k] * rho[1]
        muhat[k, 0, :] = sigmoid(ka[0] * muhat[k, 1, :], 1.0)
        pihat[k, 0, :] = 1.0 / (muhat[k, 0, :] * (1.0 - muhat[k, 0, :]))

        pi[k, 0, :] = pihat[k, 0, :]
        pi[k, 0, arm] = np.inf
        mu[k, 0, :] = muhat[k, 0, :]
        mu[k, 0, arm] = u[k]
        da[k, 0] = mu[k, 0, arm] - muhat[k, 0, arm]

        pihat[k, 1, :] = 1.0 / (
            1.0 / pi[k - 1, 1, :]
            + np.exp(ka[1] * mu[k - 1, 2, :] + om[1])
        )
        pi[k, 1, :] = pihat[k, 1, :]
        pi[k, 1, arm] = pihat[k, 1, arm] + ka[0] ** 2 / pihat[k, 0, arm]
        mu[k, 1, :] = muhat[k, 1, :]
        mu[k, 1, arm] = muhat[k, 1, arm] + ka[0] / pi[k, 1, arm] * da[k, 0]
        da[k, 1] = (
            (1.0 / pi[k, 1, arm] + (mu[k, 1, arm] - muhat[k, 1, arm]) ** 2)
            * pihat[k, 1, arm]
            - 1.0
        )

        for j in range(2, l - 1):
            muhat[k, j, :] = mu[k - 1, j, :] + t[k] * rho[j]
            pihat[k, j, :] = 1.0 / (
                1.0 / pi[k - 1, j, :]
                + t[k] * np.exp(ka[j] * mu[k - 1, j + 1, :] + om[j])
            )
            v[k, j - 1] = t[k] * np.exp(ka[j - 1] * mu[k - 1, j, arm] + om[j - 1])
            w[k, j - 1] = v[k, j - 1] * pihat[k, j - 1, arm]
            correction = (
                0.5
                * ka[j - 1] ** 2
                * w[k, j - 1]
                * (w[k, j - 1] + (2.0 * w[k, j - 1] - 1.0) * da[k, j - 1])
            )
            pi[k, j, :] = pihat[k, j, :] + correction
            mu[k, j, :] = (
                muhat[k, j, :]
                + 0.5 / pi[k, j, :] * ka[j - 1] * w[k, j - 1] * da[k, j - 1]
            )
            da[k, j] = (
                (1.0 / pi[k, j, arm] + (mu[k, j, arm] - muhat[k, j, arm]) ** 2)
                * pihat[k, j, arm]
                - 1.0
            )

        last = l - 1
        muhat[k, last, :] = mu[k - 1, last, :] + t[k] * rho[last]
        pihat[k, last, :] = 1.0 / (1.0 / pi[k - 1, last, :] + t[k] * theta)
        v[k, last] = t[k] * theta
        v[k, last - 1] = t[k] * np.exp(ka[last - 1] * mu[k - 1, last, arm] + om[last - 1])
        w[k, last - 1] = v[k, last - 1] * pihat[k, last - 1, arm]
        correction = (
            0.5
            * ka[last - 1] ** 2
            * w[k, last - 1]
            * (w[k, last - 1] + (2.0 * w[k, last - 1] - 1.0) * da[k, last - 1])
        )
        pi[k, last, :] = pihat[k, last, :] + correction
        mu[k, last, :] = (
            muhat[k, last, :]
            + 0.5 / pi[k, last, :] * ka[last - 1] * w[k, last - 1] * da[k, last - 1]
        )
        da[k, last] = (
            (1.0 / pi[k, last, arm] + (mu[k, last, arm] - muhat[k, last, arm]) ** 2)
            * pihat[k, last, arm]
            - 1.0
        )

        if coupled:
            if arm == 0:
                mu[k, 0, 1] = 1.0 - mu[k, 0, 0]
                mu[k, 1, 1] = logit(1.0 - sigmoid(mu[k, 1, 0], 1.0), 1.0)
            else:
                mu[k, 0, 0] = 1.0 - mu[k, 0, 1]
                mu[k, 1, 0] = logit(1.0 - sigmoid(mu[k, 1, 1], 1.0), 1.0)

    mu = mu[1:]
    pi = pi[1:]
    muhat = muhat[1:]
    pihat = pihat[1:]
    v = v[1:]
    w = w[1:]
    da = da[1:]
    regular = ~ignored
    if validate:
        check_hgf_trajectories(mu[:, 1:, :], pi[:, 1:, :], 16.0, columns=None)
    return _mab_outputs(
        mu, pi, muhat, pihat, v, w, da,
        ka=ka, choices_zero=choices_zero, regular=regular, binary=True
    )


def hgf_ar1_mab(
    inputs,
    parameters,
    *,
    choices=None,
    n_bandits: int = 3,
    transformed: bool = False,
    irregular_intervals: bool = False,
    ignored_trials: Sequence[int] | None = None,
    validate: bool = True,
):
    """Mirror frozen hgf_ar1_mab.m."""

    values, input_matrix, choices_raw = _mab_inputs(inputs, choices, n_bandits)
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    levels = p.size / 6
    if levels != int(levels) or levels < 2:
        raise ValueError("Cannot determine hgf_ar1_mab levels")
    l = int(levels)
    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[2 * l : 3 * l] = sigmoid(p[2 * l : 3 * l], 1.0)
        p[4 * l : 5 * l - 1] = np.exp(p[4 * l : 5 * l - 1])
        p[6 * l - 1] = np.exp(p[6 * l - 1])

    mu0 = p[:l]
    sa0 = p[l : 2 * l]
    phi = p[2 * l : 3 * l]
    m = p[3 * l : 4 * l]
    ka = p[4 * l : 5 * l - 1]
    om = p[5 * l - 1 : 6 * l - 2]
    theta = np.exp(p[6 * l - 2])
    alpha = p[6 * l - 1]

    ignored = _ignored(values.size, values, choices_raw, ignored_trials)
    choices_zero = np.where(np.isnan(choices_raw), 0, choices_raw.astype(np.int64) - 1)
    u = np.concatenate(([0.0], values))
    t = build_time_axis(input_matrix, irregular_intervals=irregular_intervals)
    n = values.size + 1

    mu = np.full((n, l, n_bandits), np.nan)
    pi = np.full_like(mu, np.nan)
    muhat = np.full_like(mu, np.nan)
    pihat = np.full_like(mu, np.nan)
    v = np.full((n, l), np.nan)
    w = np.full((n, l - 1), np.nan)
    da = np.full((n, l), np.nan)
    dau = np.full(n, np.nan)

    mu[0, :, :] = mu0[:, None]
    pi[0, :, :] = (1.0 / sa0)[:, None]

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

        arm = choices_zero[trial]
        muhat[k, 0, :] = mu[k - 1, 0, :] + t[k] * phi[0] * (m[0] - mu[k - 1, 0, :])
        pihat[k, 0, :] = 1.0 / (
            1.0 / pi[k - 1, 0, :]
            + t[k] * np.exp(ka[0] * mu[k - 1, 1, :] + om[0])
        )
        dau[k] = u[k] - muhat[k, 0, arm]
        pi[k, 0, :] = pihat[k, 0, :]
        pi[k, 0, arm] += 1.0 / alpha
        mu[k, 0, :] = muhat[k, 0, :]
        mu[k, 0, arm] += (
            1.0 / pihat[k, 0, arm]
            * 1.0 / (1.0 / pihat[k, 0, arm] + alpha)
            * dau[k]
        )
        da[k, 0] = (
            (1.0 / pi[k, 0, arm] + (mu[k, 0, arm] - muhat[k, 0, arm]) ** 2)
            * pihat[k, 0, arm]
            - 1.0
        )

        for j in range(1, l - 1):
            muhat[k, j, :] = mu[k - 1, j, :] + t[k] * phi[j] * (m[j] - mu[k - 1, j, :])
            pihat[k, j, :] = 1.0 / (
                1.0 / pi[k - 1, j, :]
                + t[k] * np.exp(ka[j] * mu[k - 1, j + 1, :] + om[j])
            )
            v[k, j - 1] = t[k] * np.exp(ka[j - 1] * mu[k - 1, j, arm] + om[j - 1])
            w[k, j - 1] = v[k, j - 1] * pihat[k, j - 1, arm]
            correction = (
                0.5 * ka[j - 1] ** 2 * w[k, j - 1]
                * (w[k, j - 1] + (2.0 * w[k, j - 1] - 1.0) * da[k, j - 1])
            )
            pi[k, j, :] = pihat[k, j, :] + correction
            mu[k, j, :] = (
                muhat[k, j, :]
                + 0.5 / pi[k, j, :] * ka[j - 1] * w[k, j - 1] * da[k, j - 1]
            )
            da[k, j] = (
                (1.0 / pi[k, j, arm] + (mu[k, j, arm] - muhat[k, j, arm]) ** 2)
                * pihat[k, j, arm]
                - 1.0
            )

        last = l - 1
        muhat[k, last, :] = mu[k - 1, last, :] + t[k] * phi[last] * (m[last] - mu[k - 1, last, :])
        pihat[k, last, :] = 1.0 / (1.0 / pi[k - 1, last, :] + t[k] * theta)
        v[k, last] = t[k] * theta
        v[k, last - 1] = t[k] * np.exp(ka[last - 1] * mu[k - 1, last, arm] + om[last - 1])
        w[k, last - 1] = v[k, last - 1] * pihat[k, last - 1, arm]
        correction = (
            0.5 * ka[last - 1] ** 2 * w[k, last - 1]
            * (w[k, last - 1] + (2.0 * w[k, last - 1] - 1.0) * da[k, last - 1])
        )
        pi[k, last, :] = pihat[k, last, :] + correction
        mu[k, last, :] = (
            muhat[k, last, :]
            + 0.5 / pi[k, last, :] * ka[last - 1] * w[k, last - 1] * da[k, last - 1]
        )
        da[k, last] = (
            (1.0 / pi[k, last, arm] + (mu[k, last, arm] - muhat[k, last, arm]) ** 2)
            * pihat[k, last, arm]
            - 1.0
        )

    mu = mu[1:]
    pi = pi[1:]
    muhat = muhat[1:]
    pihat = pihat[1:]
    v = v[1:]
    w = w[1:]
    da = da[1:]
    dau = dau[1:]
    regular = ~ignored

    if validate:
        check_hgf_trajectories(mu, pi, 256.0, columns=None)

    traj, inf_states = _mab_outputs(
        mu, pi, muhat, pihat, v, w, da,
        ka=ka, choices_zero=choices_zero, regular=regular, binary=False
    )
    traj["dau"] = dau
    psi = np.full((values.size, l), np.nan)
    selected_pi1 = _selected(pi[:, 0, :], choices_zero, regular)
    psi[regular, 0] = 1.0 / (alpha * selected_pi1[regular])
    for level in range(1, l):
        prev = _selected(pihat[:, level - 1, :], choices_zero, regular)
        cur = _selected(pi[:, level, :], choices_zero, regular)
        psi[regular, level] = prev[regular] / cur[regular]
    traj["psi"] = psi
    epsi = np.full((values.size, l), np.nan)
    epsi[:, 0] = psi[:, 0] * dau
    epsi[:, 1:l] = psi[:, 1:l] * da[:, : l - 1]
    traj["epsi"] = epsi
    wt = np.full((values.size, l), np.nan)
    wt[:, 0] = psi[:, 0]
    wt[:, 1:l] = 0.5 * (v[:, : l - 1] * ka[: l - 1]) * psi[:, 1:l]
    traj["wt"] = wt
    return traj, inf_states
