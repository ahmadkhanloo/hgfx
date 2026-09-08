"""Categorical and world-state HGF families from frozen toolbox 8.2.0."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.math.boltzmann import boltzmann
from hgfx.math.logistic import sigmoid


def _ignored(values: np.ndarray, ignored_trials: Sequence[int] | None) -> np.ndarray:
    mask = np.isnan(values)
    if ignored_trials is not None:
        mask = mask.copy()
        for index in ignored_trials:
            if index < 0 or index >= values.size:
                raise IndexError(f"ignored trial index out of range: {index}")
            mask[index] = True
    return mask


def _categorical_core(
    inputs,
    parameters,
    *,
    n_outcomes: int,
    normalized: bool,
    ignored_trials: Sequence[int] | None = None,
):
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    expected = 2 * n_outcomes + 5
    if p.size != expected:
        raise ValueError(f"categorical HGF expects {expected} native parameters")
    mu2_0 = p[:n_outcomes]
    sa2_0 = p[n_outcomes : 2 * n_outcomes]
    mu3_0, sa3_0, ka, om, th = p[2 * n_outcomes :]

    values = np.asarray(inputs, dtype=np.float64)
    if values.ndim == 2:
        values = values[:, 0]
    values = values.reshape(-1)
    ignored = _ignored(values, ignored_trials)
    outcomes = np.where(np.isnan(values), 1, values).astype(np.int64)
    valid = ~ignored
    if np.any((outcomes[valid] < 1) | (outcomes[valid] > n_outcomes)):
        raise ValueError("categorical outcomes must be MATLAB-style 1..n_outcomes")

    u = np.concatenate(([1], outcomes))
    n = u.size
    no = n_outcomes
    mu1 = np.full((n, no), np.nan)
    pi1 = np.full((n, no), np.nan)
    mu2 = np.full((n, no), np.nan)
    pi2 = np.full((n, no), np.nan)
    mu3 = np.full(n, np.nan)
    pi3 = np.full(n, np.nan)
    mu1hat = np.full((n, no), np.nan)
    pi1hat = np.full((n, no), np.nan)
    mu2hat = np.full((n, no), np.nan)
    pi2hat = np.full((n, no), np.nan)
    mu3hat = np.full(n, np.nan)
    pi3hat = np.full(n, np.nan)
    v2 = np.full(n, np.nan)
    w2 = np.full((n, no), np.nan)
    da1 = np.full((n, no), np.nan)
    da2 = np.full((n, no), np.nan)

    mu1[0] = sigmoid(mu2_0, 1.0)
    pi1[0] = 1.0 / (mu1[0] * (1.0 - mu1[0]))
    mu2[0] = mu2_0
    pi2[0] = 1.0 / sa2_0
    mu3[0] = mu3_0
    pi3[0] = 1.0 / sa3_0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            for a in (mu1, pi1, mu2, pi2, mu1hat, pi1hat, mu2hat, pi2hat, w2, da1, da2):
                a[k] = a[k - 1]
            for a in (mu3, pi3, mu3hat, pi3hat, v2):
                a[k] = a[k - 1]
            continue
        if normalized:
            mu1hat[k] = boltzmann(mu2[k - 1], 1.0)
        else:
            mu1hat[k] = sigmoid(mu2[k - 1], 1.0)
        pi1hat[k] = 1.0 / (mu1hat[k] * (1.0 - mu1hat[k]))
        mu1[k] = 0.0
        mu1[k, u[k] - 1] = 1.0
        pi1[k] = np.inf
        da1[k] = mu1[k] - mu1hat[k]

        mu2hat[k] = mu2[k - 1]
        pi2hat[k] = 1.0 / (1.0 / pi2[k - 1] + np.exp(ka * mu3[k - 1] + om))
        pi2[k] = pi2hat[k] + 1.0 / pi1hat[k]
        mu2[k] = mu2hat[k] + 1.0 / pi2[k] * da1[k]
        da2[k] = (1.0 / pi2[k] + (mu2[k] - mu2hat[k]) ** 2) * pi2hat[k] - 1.0

        mu3hat[k] = mu3[k - 1]
        pi3hat[k] = 1.0 / (1.0 / pi3[k - 1] + th)
        v2[k] = np.exp(ka * mu3[k - 1] + om)
        w2[k] = v2[k] * pi2hat[k]
        pi3[k] = pi3hat[k] + np.sum(
            0.5 * ka**2 * w2[k] * (w2[k] + (2.0 * w2[k] - 1.0) * da2[k])
        )
        if pi3[k] <= 0:
            raise ValueError("Negative posterior precision")
        mu3[k] = mu3hat[k] + np.sum(0.5 / pi3[k] * ka * w2[k] * da2[k])

    mu1, pi1, mu2, pi2, mu3, pi3 = mu1[1:], pi1[1:], mu2[1:], pi2[1:], mu3[1:], pi3[1:]
    mu1hat, pi1hat, mu2hat, pi2hat = mu1hat[1:], pi1hat[1:], mu2hat[1:], pi2hat[1:]
    mu3hat, pi3hat, v2, w2, da1, da2 = mu3hat[1:], pi3hat[1:], v2[1:], w2[1:], da1[1:], da2[1:]

    traj_mu = np.full((values.size, 3, no), np.nan)
    traj_sa = np.full_like(traj_mu, np.nan)
    traj_muhat = np.full_like(traj_mu, np.nan)
    traj_sahat = np.full_like(traj_mu, np.nan)
    traj_mu[:, 0, :] = mu1
    traj_mu[:, 1, :] = mu2
    traj_mu[:, 2, 0] = mu3
    traj_sa[:, 0, :] = 1.0 / pi1
    traj_sa[:, 1, :] = 1.0 / pi2
    traj_sa[:, 2, 0] = 1.0 / pi3
    traj_muhat[:, 0, :] = mu1hat
    traj_muhat[:, 1, :] = mu2hat
    traj_muhat[:, 2, 0] = mu3hat
    traj_sahat[:, 0, :] = 1.0 / pi1hat
    traj_sahat[:, 1, :] = 1.0 / pi2hat
    traj_sahat[:, 2, 0] = 1.0 / pi3hat
    da = np.full((values.size, 2, no), np.nan)
    da[:, 0, :] = da1
    da[:, 1, :] = da2
    psi = np.full((values.size, 3, no), np.nan)
    psi[:, 1, :] = 1.0 / pi2
    psi[:, 2, :] = pi2hat / pi3[:, None]
    epsi = np.full_like(psi, np.nan)
    epsi[:, 1, :] = psi[:, 1, :] * da1
    epsi[:, 2, :] = psi[:, 2, :] * da2
    with np.errstate(divide="ignore", invalid="ignore"):
        upd1 = sigmoid(mu2, 1.0) - mu1hat
        lr1 = upd1 / da1
    wt = np.full_like(psi, np.nan)
    wt[:, 0, :] = lr1
    wt[:, 1, :] = psi[:, 1, :]
    wt[:, 2, :] = 0.5 * ka * (v2[:, None] * psi[:, 2, :])
    traj = {
        "mu": traj_mu,
        "sa": traj_sa,
        "muhat": traj_muhat,
        "sahat": traj_sahat,
        "v": v2,
        "w": w2,
        "da": da,
        "ud": traj_mu - traj_muhat,
        "psi": psi,
        "epsi": epsi,
        "wt": wt,
    }
    inf_states = np.stack((traj_muhat, traj_sahat, traj_mu, traj_sa), axis=3)
    return traj, inf_states


def hgf_categorical(inputs, parameters, *, n_outcomes: int = 3, ignored_trials=None):
    return _categorical_core(
        inputs, parameters, n_outcomes=n_outcomes, normalized=False, ignored_trials=ignored_trials
    )


def hgf_categorical_norm(inputs, parameters, *, n_outcomes: int = 3, ignored_trials=None):
    return _categorical_core(
        inputs, parameters, n_outcomes=n_outcomes, normalized=True, ignored_trials=ignored_trials
    )


def hgf_whatworld(
    inputs,
    parameters,
    *,
    n_states: int = 4,
    ignored_trials: Sequence[int] | None = None,
):
    values = np.asarray(inputs, dtype=np.float64)
    if values.ndim == 2:
        values = values[:, 0]
    values = values.reshape(-1)
    ignored = _ignored(values, ignored_trials)
    ns = int(n_states)
    ntr = ns * ns
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    if p.size != 2 * ntr + 5:
        raise ValueError("WhatWorld parameter length does not match n_states")
    # MATLAB reshape fills columns first.
    mu2_0 = np.reshape(p[:ntr], (ns, ns), order="F")
    sa2_0 = np.reshape(p[ntr : 2 * ntr], (ns, ns), order="F")
    mu3_0, sa3_0, ka, om, th = p[2 * ntr :]
    state = np.where(np.isnan(values), 1, values).astype(np.int64)
    valid = ~ignored
    if np.any((state[valid] < 1) | (state[valid] > ns)):
        raise ValueError("WhatWorld states must be MATLAB-style 1..n_states")
    u = np.concatenate(([1], state))
    n = u.size

    shape = (n, ns, ns)
    mu1 = np.full(shape, np.nan)
    pi1 = np.full(shape, np.nan)
    mu2 = np.full(shape, np.nan)
    pi2 = np.full(shape, np.nan)
    mu1hat = np.full(shape, np.nan)
    pi1hat = np.full(shape, np.nan)
    mu2hat = np.full(shape, np.nan)
    pi2hat = np.full(shape, np.nan)
    w2 = np.full(shape, np.nan)
    da1 = np.full(shape, np.nan)
    da2 = np.full(shape, np.nan)
    mu3 = np.full(n, np.nan)
    pi3 = np.full(n, np.nan)
    mu3hat = np.full(n, np.nan)
    pi3hat = np.full(n, np.nan)
    v2 = np.full(n, np.nan)

    mu1[0] = sigmoid(mu2_0, 1.0)
    pi1[0] = 1.0 / (mu1[0] * (1.0 - mu1[0]))
    mu2[0] = mu2_0
    pi2[0] = 1.0 / sa2_0
    mu3[0], pi3[0] = mu3_0, 1.0 / sa3_0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            for a in (mu1, pi1, mu2, pi2, mu1hat, pi1hat, mu2hat, pi2hat, w2, da1, da2):
                a[k] = a[k - 1]
            for a in (mu3, pi3, mu3hat, pi3hat, v2):
                a[k] = a[k - 1]
            continue
        prev = u[k - 1] - 1
        cur = u[k] - 1
        mu1hat[k] = sigmoid(mu2[k - 1], 1.0)
        pi1hat[k] = 1.0 / (mu1hat[k] * (1.0 - mu1hat[k]))
        mu1[k, :, prev] = 0.0
        mu1[k, cur, prev] = 1.0
        pi1[k, :, prev] = np.inf
        da1[k, :, prev] = mu1[k, :, prev] - mu1hat[k, :, prev]
        mu2hat[k] = mu2[k - 1]
        pi2hat[k] = 1.0 / (1.0 / pi2[k - 1] + np.exp(ka * mu3[k - 1] + om))
        pi2[k] = pi2hat[k]
        pi2[k, :, prev] = pi2hat[k, :, prev] + 1.0 / pi1hat[k, :, prev]
        mu2[k] = mu2hat[k]
        mu2[k, :, prev] = mu2hat[k, :, prev] + 1.0 / pi2[k, :, prev] * da1[k, :, prev]
        da2[k, :, prev] = (
            (1.0 / pi2[k, :, prev] + (mu2[k, :, prev] - mu2hat[k, :, prev]) ** 2)
            * pi2hat[k, :, prev]
            - 1.0
        )
        mu3hat[k] = mu3[k - 1]
        pi3hat[k] = 1.0 / (1.0 / pi3[k - 1] + th)
        v2[k] = np.exp(ka * mu3[k - 1] + om)
        w2[k, :, prev] = v2[k] * pi2hat[k, :, prev]
        corr = 0.5 * ka**2 * w2[k, :, prev] * (
            w2[k, :, prev] + (2.0 * w2[k, :, prev] - 1.0) * da2[k, :, prev]
        )
        pi3[k] = pi3hat[k] + np.sum(corr)
        if pi3[k] <= 0:
            raise ValueError("Negative posterior precision")
        mu3[k] = mu3hat[k] + np.sum(
            0.5 / pi3[k] * ka * w2[k, :, prev] * da2[k, :, prev]
        )

    mu1, pi1, mu2, pi2, mu3, pi3 = mu1[1:], pi1[1:], mu2[1:], pi2[1:], mu3[1:], pi3[1:]
    mu1hat, pi1hat, mu2hat, pi2hat = mu1hat[1:], pi1hat[1:], mu2hat[1:], pi2hat[1:]
    mu3hat, pi3hat, v2, w2, da1, da2 = mu3hat[1:], pi3hat[1:], v2[1:], w2[1:], da1[1:], da2[1:]

    shp = (values.size, 3, ns, ns)
    tmu = np.full(shp, np.nan)
    tsa = np.full(shp, np.nan)
    tmh = np.full(shp, np.nan)
    tsh = np.full(shp, np.nan)
    tmu[:, 0] = mu1; tmu[:, 1] = mu2; tmu[:, 2, 0, 0] = mu3
    tsa[:, 0] = 1.0 / pi1; tsa[:, 1] = 1.0 / pi2; tsa[:, 2, 0, 0] = 1.0 / pi3
    tmh[:, 0] = mu1hat; tmh[:, 1] = mu2hat; tmh[:, 2, 0, 0] = mu3hat
    tsh[:, 0] = 1.0 / pi1hat; tsh[:, 1] = 1.0 / pi2hat; tsh[:, 2, 0, 0] = 1.0 / pi3hat
    da = np.full((values.size, 2, ns, ns), np.nan)
    da[:, 0] = da1; da[:, 1] = da2
    psi = np.full(shp, np.nan)
    psi[:, 1] = 1.0 / pi2
    psi[:, 2] = pi2hat / pi3[:, None, None]
    epsi = np.full(shp, np.nan)
    epsi[:, 1] = psi[:, 1] * da1
    epsi[:, 2] = psi[:, 2] * da2
    with np.errstate(divide="ignore", invalid="ignore"):
        lr1 = (sigmoid(mu2, 1.0) - mu1hat) / da1
    wt = np.full(shp, np.nan)
    wt[:, 0] = lr1
    wt[:, 1] = psi[:, 1]
    wt[:, 2] = 0.5 * ka * (v2[:, None, None] * psi[:, 2])
    traj = {
        "mu": tmu, "sa": tsa, "muhat": tmh, "sahat": tsh,
        "v": v2, "w": w2, "da": da, "ud": tmu - tmh,
        "psi": psi, "epsi": epsi, "wt": wt,
    }
    inf_states = np.stack((tmh, tsh, tmu, tsa), axis=4)
    return traj, inf_states


def hgf_whichworld(
    inputs,
    parameters,
    *,
    n_worlds: int = 2,
    ignored_trials: Sequence[int] | None = None,
):
    """Usable port of frozen hgf_whichworld with documented da->da1 defect repair."""

    values = np.asarray(inputs, dtype=np.float64)
    if values.ndim == 2:
        values = values[:, 0]
    values = values.reshape(-1)
    ignored = _ignored(values, ignored_trials)
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    nw = int(n_worlds)
    if nw != 2:
        raise ValueError("Frozen WhichWorld defines two Bernoulli worlds")
    if p.size != 2 * nw + 7:
        raise ValueError("WhichWorld parameter length mismatch")
    mu2_0 = p[:nw]
    sa2_0 = p[nw : 2 * nw]
    mu3_0, sa3_0, ka, om, th, m, phi = p[2 * nw :]
    uvals = np.where(np.isnan(values), 0.0, values)
    u = np.concatenate(([0.0], uvals))
    n = u.size
    bp = np.array([0.85, 0.15])

    mu1 = np.full((n, nw), np.nan); pi1 = np.full((n, nw), np.nan)
    mu2 = np.full((n, nw), np.nan); pi2 = np.full((n, nw), np.nan)
    mu3 = np.full(n, np.nan); pi3 = np.full(n, np.nan)
    mu1hat = np.full((n, nw), np.nan); pi1hat = np.full((n, nw), np.nan)
    mu2hat = np.full((n, nw), np.nan); pi2hat = np.full((n, nw), np.nan)
    mu3hat = np.full(n, np.nan); pi3hat = np.full(n, np.nan)
    v2 = np.full(n, np.nan); w2 = np.full((n, nw), np.nan)
    da1 = np.full((n, nw), np.nan); da2 = np.full((n, nw), np.nan)

    mu1[0] = sigmoid(mu2_0, 1.0)
    pi1[0] = 1.0 / (mu1[0] * (1.0 - mu1[0]))
    mu2[0] = mu2_0; pi2[0] = 1.0 / sa2_0
    mu3[0] = mu3_0; pi3[0] = 1.0 / sa3_0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            for a in (mu1, pi1, mu2, pi2, mu1hat, pi1hat, mu2hat, pi2hat, w2, da1, da2):
                a[k] = a[k - 1]
            for a in (mu3, pi3, mu3hat, pi3hat, v2):
                a[k] = a[k - 1]
            continue
        mu1hat[k] = sigmoid(mu2[k - 1], 1.0)
        pi1hat[k] = 1.0 / (mu1hat[k] * (1.0 - mu1hat[k]))
        llh = bp ** u[k] * (1.0 - bp) ** (1.0 - u[k])
        mllh = float(mu1hat[k] @ llh)
        mu1[k] = mu1hat[k] * llh / mllh
        pi1[k] = 1.0 / (mu1[k] * (1.0 - mu1[k]))
        da1[k] = mu1[k] - mu1hat[k]
        mu2hat[k] = mu2[k - 1]
        pi2hat[k] = 1.0 / (1.0 / pi2[k - 1] + np.exp(ka * mu3[k - 1] + om))
        pi2[k] = pi2hat[k] + 1.0 / pi1hat[k]
        mu2[k] = mu2hat[k] + 1.0 / pi2[k] * da1[k]
        da2[k] = (1.0 / pi2[k] + (mu2[k] - mu2hat[k]) ** 2) * pi2hat[k] - 1.0
        mu3hat[k] = mu3[k - 1] + phi * (m - mu3[k - 1])
        pi3hat[k] = 1.0 / (1.0 / pi3[k - 1] + th)
        v2[k] = np.exp(ka * mu3[k - 1] + om)
        w2[k] = v2[k] * pi2hat[k]
        pi3[k] = pi3hat[k] + (1.0 / nw) * np.sum(
            0.5 * ka**2 * w2[k] * (w2[k] + (2.0 * w2[k] - 1.0) * da2[k])
        )
        if pi3[k] <= 0:
            raise ValueError("Negative posterior precision")
        mu3[k] = mu3hat[k] + np.sum(0.5 / pi3[k] * ka * w2[k] * da2[k])

    with np.errstate(divide="ignore", invalid="ignore"):
        lr1 = np.diff(sigmoid(mu2, 1.0), axis=0) / da1[1:]
        lr1[da1[1:] == 0] = 0.0

    mu1, pi1, mu2, pi2, mu3, pi3 = mu1[1:], pi1[1:], mu2[1:], pi2[1:], mu3[1:], pi3[1:]
    mu1hat, pi1hat, mu2hat, pi2hat = mu1hat[1:], pi1hat[1:], mu2hat[1:], pi2hat[1:]
    mu3hat, pi3hat, v2, w2, da1, da2 = mu3hat[1:], pi3hat[1:], v2[1:], w2[1:], da1[1:], da2[1:]
    shp=(values.size,3,nw)
    tmu=np.full(shp,np.nan); tsa=np.full(shp,np.nan); tmh=np.full(shp,np.nan); tsh=np.full(shp,np.nan)
    tmu[:,0]=mu1;tmu[:,1]=mu2;tmu[:,2,0]=mu3
    tsa[:,0]=1/pi1;tsa[:,1]=1/pi2;tsa[:,2,0]=1/pi3
    tmh[:,0]=mu1hat;tmh[:,1]=mu2hat;tmh[:,2,0]=mu3hat
    tsh[:,0]=1/pi1hat;tsh[:,1]=1/pi2hat;tsh[:,2,0]=1/pi3hat
    da=np.full((values.size,2,nw),np.nan);da[:,0]=da1;da[:,1]=da2
    psi=np.full(shp,np.nan);psi[:,1]=1/pi2;psi[:,2]=pi2hat/pi3[:,None]
    epsi=np.full(shp,np.nan);epsi[:,1]=psi[:,1]*da1;epsi[:,2]=psi[:,2]*da2
    wt=np.full(shp,np.nan);wt[:,0]=lr1;wt[:,1]=psi[:,1];wt[:,2]=0.5*ka*(w2/pi3[:,None])
    traj={"mu":tmu,"sa":tsa,"muhat":tmh,"sahat":tsh,"v":v2,"w":w2,"da":da,"ud":tmu-tmh,"psi":psi,"epsi":epsi,"wt":wt}
    return traj,np.stack((tmh,tsh,tmu,tsa),axis=3)
