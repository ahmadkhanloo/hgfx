"""Remaining frozen observation families required by complete M12 coverage."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.math.logistic import sigmoid

from .base import first_input_column, ignored_mask, output_arrays, response_vector


def _regular(n: int, irregular_trials: Sequence[int] | None) -> np.ndarray:
    return ~ignored_mask(n, irregular_trials)


def _condhalluc_common(
    responses,
    inputs,
    inf_states,
    *,
    belief: np.ndarray,
    beta: float,
    irregular_trials: Sequence[int] | None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    y = response_vector(responses, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    x = np.asarray(belief, dtype=np.float64)[reg]
    yr = y[reg]
    logp[reg] = -np.log(1.0 + np.exp(-beta * (2.0 * x - 1.0) * (2.0 * yr - 1.0)))
    yhat[reg] = x
    res[reg] = (yr - x) / np.sqrt(x * (1.0 - x))
    return logp, yhat, res


def condhalluc_obs(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    _, umat = first_input_column(inputs, n)
    if umat.shape[1] != 2:
        raise ValueError("condhalluc_obs requires exactly two input columns")
    mu1hat = s[:, 0, 0]
    tp = umat[:, 1]
    denominator = tp * mu1hat + (1.0 - mu1hat) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        x = tp * mu1hat / denominator
    x = np.asarray(x, dtype=np.float64)
    x[tp == 0.0] = mu1hat[tp == 0.0]
    beta = float(np.exp(np.asarray(ptrans, dtype=np.float64).reshape(-1)[0]))
    return _condhalluc_common(
        responses,
        inputs,
        inf_states,
        belief=x,
        beta=beta,
        irregular_trials=irregular_trials,
    )


def condhalluc_obs2(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    _, umat = first_input_column(inputs, n)
    if umat.shape[1] != 2:
        raise ValueError("condhalluc_obs2 requires exactly two input columns")
    p = np.asarray(ptrans, dtype=np.float64).reshape(-1)
    beta = float(np.exp(p[0]))
    nu = float(np.exp(p[1]))
    mu1hat = s[:, 0, 0]
    tp = umat[:, 1]
    x = mu1hat + (tp - mu1hat) / (1.0 + nu)
    return _condhalluc_common(
        responses,
        inputs,
        inf_states,
        belief=x,
        beta=beta,
        irregular_trials=irregular_trials,
    )


def condhalluc_obs3(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    _, umat = first_input_column(inputs, n)
    if umat.shape[1] != 2:
        raise ValueError("condhalluc_obs3 requires exactly two input columns")
    beta = float(np.exp(np.asarray(ptrans, dtype=np.float64).reshape(-1)[0]))
    mu1hat = s[:, 0, 0]
    mu3hat = s[:, 2, 0]
    nu = np.exp(mu3hat)
    tp = umat[:, 1]
    x = mu1hat + (tp - mu1hat) / (1.0 + nu)
    return _condhalluc_common(
        responses,
        inputs,
        inf_states,
        belief=x,
        beta=beta,
        irregular_trials=irregular_trials,
    )


def _choice_matrix(choices: np.ndarray, n_choices: int) -> np.ndarray:
    idx = choices.astype(np.int64) - 1
    if np.any(idx < 0) or np.any(idx >= n_choices):
        raise ValueError("choices must be MATLAB-style 1..N")
    matrix = np.zeros((choices.size, n_choices), dtype=np.float64)
    matrix[np.arange(choices.size), idx] = 1.0
    return matrix


def _win_loss_distort(
    states: np.ndarray,
    outcomes: np.ndarray,
    choices: np.ndarray,
    *,
    la_wd: float,
    la_ld: float,
) -> np.ndarray:
    ymat = _choice_matrix(choices, states.shape[1])
    yprev = np.vstack((np.zeros((1, states.shape[1])), ymat))[:-1]
    wprev = np.concatenate(([0.0], outcomes))[:-1]
    lprev = 1.0 - wprev
    lprev[0] = 0.0
    wmat = yprev.copy()
    wmat[lprev.astype(bool)] = 0.0
    lmat = yprev.copy()
    lmat[wprev.astype(bool)] = 0.0
    return states + la_wd * wmat + la_ld * lmat


def softmax_wld(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
    predorpost: int = 1,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    y = response_vector(responses, n)
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)

    pop = 0 if int(predorpost) == 1 else 2
    states = np.asarray(s[reg, 0, :, pop], dtype=np.float64)
    ur = u[reg]
    yr = y[reg]

    p = np.asarray(ptrans, dtype=np.float64).reshape(-1)
    # Frozen source quirk: ptrans(1) controls both beta and win distortion.
    beta = float(np.exp(p[0]))
    la_wd = float(p[0])
    la_ld = float(p[1])
    states = _win_loss_distort(states, ur, yr, la_wd=la_wd, la_ld=la_ld)

    exponent = np.exp(beta * states)
    prob = exponent / np.sum(exponent, axis=1, keepdims=True)
    idx = yr.astype(np.int64) - 1
    probc = prob[np.arange(prob.shape[0]), idx]
    logp[reg] = np.log(probc)
    yhat[reg] = probc
    res[reg] = -np.log(probc)
    return logp, yhat, res


def softmax_mu3_wld(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
    predorpost: int = 1,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    y = response_vector(responses, n)
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)

    pop = 0 if int(predorpost) == 1 else 2
    states = np.asarray(s[reg, 0, :, pop], dtype=np.float64)
    mu3 = np.asarray(s[reg, 2, 0, 2], dtype=np.float64)
    ur = u[reg]
    yr = y[reg]

    p = np.asarray(ptrans, dtype=np.float64).reshape(-1)
    la_wd, la_ld = float(p[0]), float(p[1])
    states = _win_loss_distort(states, ur, yr, la_wd=la_wd, la_ld=la_ld)

    beta = np.exp(-mu3)[:, None]
    exponent = np.exp(beta * states)
    prob = exponent / np.sum(exponent, axis=1, keepdims=True)
    idx = yr.astype(np.int64) - 1
    probc = prob[np.arange(prob.shape[0]), idx]
    logp[reg] = np.log(probc)
    yhat[reg] = probc
    res[reg] = -np.log(probc)
    return logp, yhat, res


def logrt_linear_whatworld(
    responses,
    inputs,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    n = s.shape[0]
    y = response_vector(responses, n)
    u, _ = first_input_column(inputs, n)
    reg = _regular(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    p = np.asarray(ptrans, dtype=np.float64).reshape(-1)
    be0, be1, be2, be3 = (float(x) for x in p[:4])
    ze = float(np.exp(p[4]))

    # Frozen WhatWorld tensor layout:
    # time, level, to-state, from-state, channel
    mu1hat = np.asarray(s[:, 0, :, :, 0], dtype=np.float64)
    mu1 = np.asarray(s[:, 0, :, :, 2], dtype=np.float64)
    mu2 = np.asarray(s[:, 1, :, :, 2], dtype=np.float64)
    sa2 = np.asarray(s[:, 1, :, :, 3], dtype=np.float64)
    mu3 = np.asarray(s[:, 2, 0, 0, 2], dtype=np.float64)

    otp = mu1 * mu1hat
    otps23 = np.nansum(np.nansum(otp, axis=2), axis=1)
    surprise = -np.log(otps23)

    euo = mu1 * sa2
    euos23 = np.nansum(np.nansum(euo, axis=2), axis=1)
    tendency = mu1 * mu2
    tos23 = np.nansum(np.nansum(tendency, axis=2), axis=1)
    prob = np.asarray(sigmoid(tos23, 1.0), dtype=np.float64)
    expected_uncertainty = prob * (1.0 - prob) * euos23
    unexpected_uncertainty = prob * (1.0 - prob) * np.exp(mu3)

    logrt = (
        be0
        + be1 * surprise
        + be2 * expected_uncertainty
        + be3 * unexpected_uncertainty
    )
    yr = y[reg]
    lr = logrt[reg]
    logp[reg] = -0.5 * np.log(8.0 * np.arctan(1.0) * ze) - (yr - lr) ** 2 / (2.0 * ze)
    yhat[reg] = lr
    res[reg] = yr - lr
    return logp, yhat, res



def _bernoulli_from_probability(probability, *, seed=None, uniform_draws=None):
    prob = np.asarray(probability, dtype=np.float64).reshape(-1)
    if uniform_draws is None:
        draws = np.random.default_rng(seed).random(prob.size)
    else:
        draws = np.asarray(uniform_draws, dtype=np.float64).reshape(-1)
        if draws.size != prob.size:
            raise ValueError("uniform_draws length must match trials")
    return (draws < prob).astype(np.float64), prob


def simulate_condhalluc_obs(
    inputs,
    inf_states,
    parameters,
    *,
    seed=None,
    uniform_draws=None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    arr = np.asarray(inputs, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] < 2:
        raise ValueError("conditioned-hallucination simulation requires input column 2")
    beta = float(np.asarray(parameters, dtype=np.float64).reshape(-1)[0])
    mu1hat = s[:, 0, 0]
    tp = arr[:, 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        x = tp * mu1hat / (tp * mu1hat + (1.0 - mu1hat) ** 2)
    x[tp == 0.0] = mu1hat[tp == 0.0]
    probability = np.asarray(sigmoid(beta * (2.0 * x - 1.0), 1.0), dtype=np.float64)
    return _bernoulli_from_probability(probability, seed=seed, uniform_draws=uniform_draws)


def simulate_condhalluc_obs2(
    inputs,
    inf_states,
    parameters,
    *,
    seed=None,
    uniform_draws=None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    arr = np.asarray(inputs, dtype=np.float64)
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    beta, nu = float(p[0]), float(p[1])
    mu1hat = s[:, 0, 0]
    tp = arr[:, 1]
    x = mu1hat + (tp - mu1hat) / (1.0 + nu)
    probability = np.asarray(sigmoid(beta * (2.0 * x - 1.0), 1.0), dtype=np.float64)
    return _bernoulli_from_probability(probability, seed=seed, uniform_draws=uniform_draws)


def simulate_condhalluc_obs3(
    inputs,
    inf_states,
    parameters,
    *,
    seed=None,
    uniform_draws=None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    arr = np.asarray(inputs, dtype=np.float64)
    beta = float(np.asarray(parameters, dtype=np.float64).reshape(-1)[0])
    mu1hat = s[:, 0, 0]
    mu3hat = s[:, 2, 0]
    nu = np.exp(mu3hat)
    tp = arr[:, 1]
    x = mu1hat + (tp - mu1hat) / (1.0 + nu)
    probability = np.asarray(sigmoid(beta * (2.0 * x - 1.0), 1.0), dtype=np.float64)
    return _bernoulli_from_probability(probability, seed=seed, uniform_draws=uniform_draws)


def _categorical_draw(probability, *, seed=None, uniform_draws=None):
    prob = np.asarray(probability, dtype=np.float64)
    if uniform_draws is None:
        draws = np.random.default_rng(seed).random(prob.shape[0])
    else:
        draws = np.asarray(uniform_draws, dtype=np.float64).reshape(-1)
        if draws.size != prob.shape[0]:
            raise ValueError("uniform_draws length must match trials")
    cumulative = np.cumsum(prob, axis=1)
    choices = np.sum(draws[:, None] >= cumulative, axis=1) + 1
    return choices.astype(np.float64), prob


def _world_distorted_states(inputs, inf_states, parameters, *, predorpost, mu3_temperature):
    s = np.asarray(inf_states, dtype=np.float64)
    arr = np.asarray(inputs, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] < 2:
        raise ValueError("world softmax simulation requires payout and true-choice columns")
    pop = 0 if int(predorpost) == 1 else 2
    states = np.asarray(s[:, 0, :, pop], dtype=np.float64).copy()
    outcomes = arr[:, 0]
    true_choices = arr[:, 1].astype(np.int64)
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    la_wd, la_ld = float(p[0]), float(p[1])
    dummy_choices = true_choices.astype(np.float64)
    states = _win_loss_distort(states, outcomes, dummy_choices, la_wd=la_wd, la_ld=la_ld)
    if mu3_temperature:
        beta = np.exp(-np.asarray(s[:, 2, 0, 2], dtype=np.float64))[:, None]
    else:
        # Frozen softmax_wld_sim.m sets be=p (the entire native vector).
        # MATLAB implicit expansion therefore requires p length == n_choices
        # (or scalar). Preserve this simulation-specific behavior.
        beta = p[None, :]
        if beta.shape[1] not in {1, states.shape[1]}:
            raise ValueError("frozen softmax_wld_sim requires parameter count equal to number of choices")
    exponent = np.exp(beta * states)
    probability = exponent / np.sum(exponent, axis=1, keepdims=True)
    return probability


def simulate_softmax_wld(
    inputs,
    inf_states,
    parameters,
    *,
    predorpost: int = 1,
    seed=None,
    uniform_draws=None,
):
    probability = _world_distorted_states(
        inputs, inf_states, parameters, predorpost=predorpost, mu3_temperature=False
    )
    return _categorical_draw(probability, seed=seed, uniform_draws=uniform_draws)


def simulate_softmax_mu3_wld(
    inputs,
    inf_states,
    parameters,
    *,
    predorpost: int = 1,
    seed=None,
    uniform_draws=None,
):
    probability = _world_distorted_states(
        inputs, inf_states, parameters, predorpost=predorpost, mu3_temperature=True
    )
    return _categorical_draw(probability, seed=seed, uniform_draws=uniform_draws)
