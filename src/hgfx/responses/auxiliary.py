"""Auxiliary perceptual/response families from frozen HGF Toolbox 8.2.0."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.math.logistic import sigmoid

from .base import first_input_column, ignored_mask, output_arrays, response_vector


def _regular(n: int, irregular_trials: Sequence[int] | None) -> np.ndarray:
    return ~ignored_mask(n, irregular_trials)


def bayes_optimal(
    inputs,
    inf_states,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    muhat = s[reg, 0, 0]
    sahat = s[reg, 0, 1]
    ur = u[reg]
    logp[reg] = -0.5 * np.log(8.0 * np.arctan(1.0) * sahat) - (ur - muhat) ** 2 / (2.0 * sahat)
    yhat[reg] = muhat
    res[reg] = ur - muhat
    return logp, yhat, res


def bayes_optimal_binary(
    inputs,
    inf_states,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    x = s[reg, 0, 0]
    ur = u[reg]
    logp[reg] = ur * np.log(x) + (1.0 - ur) * np.log(1.0 - x)
    yhat[reg] = x
    res[reg] = (ur - x) / np.sqrt(x * (1.0 - x))
    return logp, yhat, res


def bayes_optimal_categorical(
    inputs,
    inf_states,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    pred = np.asarray(s[reg, 0, :, 0], dtype=np.float64)
    choices = u[reg].astype(np.int64) - 1
    if np.any(choices < 0) or np.any(choices >= pred.shape[1]):
        raise ValueError("categorical inputs must be MATLAB-style 1..N")
    p = pred[np.arange(pred.shape[0]), choices]
    logp[reg] = np.log(p)
    yhat[reg] = p
    res[reg] = -np.log(p)
    return logp, yhat, res


def bayes_optimal_whichworld(
    inputs,
    inf_states,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)

    # Frozen layout: infStates(:,1,:,1,1)
    pred = np.asarray(s[reg, 0, :, 0, 0], dtype=np.float64)
    ur = u[reg]
    bp = np.asarray([0.85, 0.65, 0.35, 0.15], dtype=np.float64)
    llh = bp[None, :] ** ur[:, None] * (1.0 - bp[None, :]) ** (1.0 - ur[:, None])
    marginal = np.sum(llh * pred, axis=1)
    logp[reg] = np.log(marginal)
    yhat[reg] = marginal
    res[reg] = -np.log(marginal)
    return logp, yhat, res


def bayes_optimal_whatworld(
    inputs,
    inf_states,
    *,
    n_states: int,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)

    # Frozen layout: infStates(:,1,:,:,1,1)
    pred = np.asarray(s[:, 0, :, :, 0, 0], dtype=np.float64)
    if pred.shape[1] != n_states or pred.shape[2] != n_states:
        raise ValueError("WhatWorld inferred-state tensor does not match n_states")
    to_state = u.astype(np.int64) - 1
    from_state = np.concatenate(([0], to_state[:-1]))
    valid = np.flatnonzero(reg)
    if np.any(to_state[valid] < 0) or np.any(to_state[valid] >= n_states):
        raise ValueError("WhatWorld inputs must be MATLAB-style state indices")
    p = pred[valid, to_state[valid], from_state[valid]]
    logp[reg] = np.log(p)
    yhat[reg] = p
    res[reg] = -np.log(p)
    return logp, yhat, res


def squared_pe(
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    sqpe, yhat, res = output_arrays(n)
    ze = np.exp(np.asarray(ptrans, dtype=np.float64).reshape(-1)[0])
    muhat = s[reg, 0, 0]
    ur = u[reg]
    sqpe[reg] = -0.5 * np.log(8.0 * np.arctan(1.0) * ze) - (ur - muhat) ** 2 / (2.0 * ze)
    yhat[reg] = muhat
    res[reg] = ur - muhat
    return sqpe, yhat, res


def _rs_gaussian(
    responses,
    prediction,
    variance: float,
    *,
    irregular_trials: Sequence[int] | None,
):
    pred = np.asarray(prediction, dtype=np.float64).reshape(-1)
    n = pred.size
    y = response_vector(responses, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    yr = y[reg]
    pr = pred[reg]
    logp[reg] = -0.5 * np.log(8.0 * np.arctan(1.0) * variance) - (yr - pr) ** 2 / (2.0 * variance)
    yhat[reg] = pr
    res[reg] = yr - pr
    return logp, yhat, res


def _rs_params(ptrans) -> tuple[float, float, float, float]:
    p = np.exp(np.asarray(ptrans, dtype=np.float64).reshape(-1))
    if p.size != 4:
        raise ValueError("response-speed model expects four transformed parameters")
    return tuple(float(x) for x in p)


def rs_belief(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    ze1v, ze1i, ze2, ze3 = _rs_params(ptrans)
    alpha = s[:, 0, 0]
    rs = u * (ze1v + ze2 * alpha) + (1.0 - u) * (ze1i + ze2 * (1.0 - alpha))
    return _rs_gaussian(responses, rs, ze3, irregular_trials=irregular_trials)


def rs_precision(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    ze1v, ze1i, ze2, ze3 = _rs_params(ptrans)
    mu2hat = s[:, 1, 0]
    pi1hat = 1.0 / s[:, 0, 1]
    alpha = np.asarray(sigmoid(np.sign(mu2hat) * (pi1hat - 4.0), 1.0), dtype=np.float64)
    rs = u * (ze1v + ze2 * alpha) + (1.0 - u) * (ze1i + ze2 * (1.0 - alpha))
    return _rs_gaussian(responses, rs, ze3, irregular_trials=irregular_trials)


def rs_surprise(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    ze1v, ze1i, ze2, ze3 = _rs_params(ptrans)
    mu1hat = s[:, 0, 0]
    alpha = 1.0 / (1.0 - np.log2(mu1hat))
    rs = u * (ze1v + ze2 * alpha) + (1.0 - u) * (ze1i + ze2 * (1.0 - alpha))
    return _rs_gaussian(responses, rs, ze3, irregular_trials=irregular_trials)


def rs_precision_whatworld(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    n_states: int,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    u, _ = first_input_column(inputs, n)
    p = np.exp(np.asarray(ptrans, dtype=np.float64).reshape(-1))
    if p.size != 3:
        raise ValueError("WhatWorld precision response-speed model expects three parameters")
    ze1, ze2, ze3 = (float(x) for x in p)

    to_state = u.astype(np.int64) - 1
    from_state = np.concatenate(([0], to_state[:-1]))
    if np.any((to_state < 0) | (to_state >= n_states)):
        raise ValueError("WhatWorld inputs must be MATLAB-style state indices")

    mu2hat_tensor = np.asarray(s[:, 1, :, :, 0, 0], dtype=np.float64)
    sa1hat_tensor = np.asarray(s[:, 0, :, :, 0, 1], dtype=np.float64)
    idx = np.arange(n)
    mu2hat = mu2hat_tensor[idx, to_state, from_state]
    pi1hat = 1.0 / sa1hat_tensor[idx, to_state, from_state]
    alpha = np.asarray(sigmoid(np.sign(mu2hat) * (pi1hat - 4.0), 1.0), dtype=np.float64)
    rs = ze1 + ze2 * alpha
    return _rs_gaussian(responses, rs, ze3, irregular_trials=irregular_trials)
