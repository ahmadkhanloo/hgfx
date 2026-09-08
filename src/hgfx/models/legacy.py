"""Legacy/specialized perceptual models from frozen HGF Toolbox 8.2.0."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.math.logistic import sigmoid


def _values(inputs) -> np.ndarray:
    array = np.asarray(inputs, dtype=np.float64)
    if array.ndim == 1:
        return array
    if array.ndim == 2 and array.shape[1] >= 1:
        return array[:, 0]
    raise ValueError("inputs must be 1D or a matrix with at least one column")


def _ignored(values: np.ndarray, ignored_trials: Sequence[int] | None) -> np.ndarray:
    mask = np.isnan(values)
    if ignored_trials is not None:
        mask = mask.copy()
        for index in ignored_trials:
            if index < 0 or index >= values.size:
                raise IndexError(f"ignored trial index out of range: {index}")
            mask[index] = True
    return mask


def rw_binary(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    if p.size != 2:
        raise ValueError("rw_binary expects [v_0, alpha]")
    if transformed:
        p = np.asarray(sigmoid(p, 1.0), dtype=np.float64)

    values = _values(inputs)
    ignored = _ignored(values, ignored_trials)
    v0, alpha = p
    u = np.concatenate(([0.0], values))
    n = u.size
    v = np.full(n, np.nan, dtype=np.float64)
    da = np.full(n, np.nan, dtype=np.float64)
    v[0] = v0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            da[k] = 0.0
            v[k] = v[k - 1]
        else:
            da[k] = u[k] - v[k - 1]
            v[k] = v[k - 1] + alpha * da[k]

    vhat = v[:-1].copy()
    traj = {"v": v[1:], "vhat": vhat, "da": da[1:]}
    return traj, vhat.copy()


def rw_binary_dual(
    inputs,
    responses,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    if p.size != 4:
        raise ValueError("rw_binary_dual expects [v0_1, v0_2, alpha, kappa]")
    if transformed:
        p = np.asarray(sigmoid(p, 1.0), dtype=np.float64)

    values = _values(inputs)
    y = np.asarray(responses, dtype=np.float64).reshape(-1)
    if y.size != values.size:
        raise ValueError("responses and inputs must have the same length")
    ignored = _ignored(values, ignored_trials)

    v0 = p[:2]
    alpha, kappa = p[2], p[3]
    u = np.concatenate(([0.0], values))
    yy = np.concatenate(([0.0], y))
    n = u.size
    v = np.full((n, 2), np.nan, dtype=np.float64)
    da = np.full((n, 2), np.nan, dtype=np.float64)
    v[0] = v0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            da[k] = 0.0
            v[k] = v[k - 1]
            continue
        choice = int(yy[k])
        if choice not in {1, 2}:
            raise ValueError("rw_binary_dual responses must be coded as 1 or 2")
        chosen = choice - 1
        other = 1 - chosen
        if u[k] == 1:
            da[k, chosen] = 1.0 - v[k - 1, chosen]
            da[k, other] = 0.0 - v[k - 1, other]
        elif u[k] == 0:
            da[k, chosen] = 0.0 - v[k - 1, chosen]
            da[k, other] = 1.0 - v[k - 1, other]
        else:
            raise ValueError("rw_binary_dual inputs must be binary")
        v[k, chosen] = v[k - 1, chosen] + alpha * da[k, chosen]
        v[k, other] = v[k - 1, other] + kappa * alpha * da[k, other]

    vhat = v[:-1].copy()
    traj = {"v": v[1:], "vhat": vhat, "da": da[1:]}
    inf_states = np.full((n - 1, 1, 2, 1, 1), np.nan, dtype=np.float64)
    inf_states[:, 0, 0, 0, 0] = vhat[:, 0]
    inf_states[:, 0, 1, 0, 0] = vhat[:, 1]
    return traj, inf_states


def pearce_hall_binary(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    if p.size != 3:
        raise ValueError("pearce_hall_binary expects [v_0, alpha_0, S]")
    if transformed:
        p[:2] = np.asarray(sigmoid(p[:2], 1.0), dtype=np.float64)
        p[2] = np.exp(p[2])

    values = _values(inputs)
    ignored = _ignored(values, ignored_trials)
    v0, alpha0, strength = p
    u = np.concatenate(([0.0], values))
    n = u.size
    v = np.full(n, np.nan, dtype=np.float64)
    alpha = np.full(n, np.nan, dtype=np.float64)
    da = np.full(n, np.nan, dtype=np.float64)
    v[0], alpha[0], da[0] = v0, alpha0, alpha0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            da[k] = 0.0
            alpha[k] = alpha[k - 1]
            v[k] = v[k - 1]
        else:
            da[k] = u[k] - v[k - 1]
            alpha[k] = abs(da[k - 1])
            v[k] = v[k - 1] + strength * alpha[k] * da[k]

    vhat = v[:-1].copy()
    traj = {
        "v": v[1:],
        "vhat": vhat,
        "al": alpha[1:],
        "da": da[1:],
    }
    inf_states = np.column_stack((vhat, v[1:], alpha[1:]))
    return traj, inf_states


def sutton_k1_binary(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    if p.size != 4:
        raise ValueError("sutton_k1_binary expects [mu, Rhat, vhat_1, h_1]")
    if transformed:
        p[0] = np.exp(p[0])
        p[1] = np.exp(p[1])
        p[2] = sigmoid(p[2], 1.0)
        p[3] = np.exp(p[3])

    mu, rhat, vhat1, h1 = p
    values = _values(inputs)
    ignored = _ignored(values, ignored_trials)
    n = values.size

    da = np.full(n, np.nan, dtype=np.float64)
    beta = np.full(n + 1, np.nan, dtype=np.float64)
    alpha = np.full(n, np.nan, dtype=np.float64)
    h = np.full(n + 1, np.nan, dtype=np.float64)
    vhat = np.full(n + 1, np.nan, dtype=np.float64)
    vhat[0], beta[0], h[0] = vhat1, np.log(rhat), h1

    for k in range(n):
        if ignored[k]:
            da[k] = 0.0
            beta[k + 1] = beta[k]
            alpha[k] = alpha[k - 1] if k > 0 else np.nan
            h[k + 1] = h[k]
            vhat[k + 1] = vhat[k]
            continue
        da[k] = values[k] - vhat[k]
        beta[k + 1] = beta[k] + mu * da[k] * h[k]
        alpha[k] = np.exp(beta[k + 1]) / (rhat + np.exp(beta[k + 1]))
        h[k + 1] = (h[k] + alpha[k] * da[k]) * max(1.0 - alpha[k], 0.0)
        vhat[k + 1] = vhat[k] + alpha[k] * da[k]

    posterior = vhat[1:].copy()
    # Frozen source removes the final entries from beta/h and prediction.
    traj = {
        "da": da,
        "be": beta[:-2],
        "al": alpha,
        "h": h[:-1],
        "v": posterior,
        "vhat": vhat[:-1],
    }
    return traj, traj["vhat"].copy()


def kalman_filter(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    if p.size != 4:
        raise ValueError("kalman_filter expects [g_0, mu_0, om, pi_u]")
    if transformed:
        p[0] = np.exp(p[0])
        p[3] = np.exp(p[3])

    g0, mu0, omega, pi_u = p
    process_variance = np.exp(omega)
    values = _values(inputs)
    ignored = _ignored(values, ignored_trials)
    u = np.concatenate(([0.0], values))
    n = u.size

    da = np.full(n, np.nan, dtype=np.float64)
    gain = np.full(n, np.nan, dtype=np.float64)
    mu = np.full(n, np.nan, dtype=np.float64)
    gain[0], mu[0] = g0, mu0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            da[k] = 0.0
            gain[k] = gain[k - 1]
            mu[k] = mu[k - 1]
        else:
            da[k] = u[k] - mu[k - 1]
            gain[k] = (
                gain[k - 1] + pi_u * process_variance
            ) / (
                gain[k - 1] + pi_u * process_variance + 1.0
            )
            mu[k] = mu[k - 1] + gain[k] * da[k]

    muhat = mu[:-1].copy()
    traj = {
        "g": gain[1:],
        "muhat": muhat,
        "mu": mu[1:],
        "da": da[1:],
    }
    return traj, np.column_stack((muhat, mu[1:]))


def hidden_markov_model(
    inputs,
    parameters,
    *,
    outcome_matrix,
    n_states: int,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Mirror tapas_hmm.m for a fixed outcome matrix B.

    Inputs are MATLAB-style 1-based outcome indices.
    """

    p = np.asarray(parameters, dtype=np.float64).reshape(-1)
    d = int(n_states)
    expected = d - 1 + d * (d - 1)
    if p.size != expected:
        raise ValueError(f"HMM expects {expected} reduced probability parameters")

    b = np.asarray(outcome_matrix, dtype=np.float64)
    if b.ndim != 2 or b.shape[1] != d:
        raise ValueError("outcome_matrix must have shape (n_outcomes, n_states)")
    if not np.allclose(np.sum(b, axis=0), 1.0):
        raise ValueError("each state column of outcome_matrix must sum to 1")

    prior_reduced = p[: d - 1]
    prior_last = 1.0 - np.sum(prior_reduced)
    if prior_last < 0:
        raise ValueError("illegal HMM state prior")
    prior = np.concatenate((prior_reduced, [prior_last]))

    reduced = np.reshape(p[d - 1 :], (d, d - 1), order="F")
    last_column = 1.0 - np.sum(reduced, axis=1)
    if np.any(last_column < 0):
        raise ValueError("illegal HMM transition matrix")
    transition = np.column_stack((reduced, last_column))

    values = _values(inputs)
    ignored = _ignored(values, ignored_trials)
    outcomes = values.astype(np.int64)
    if np.any((outcomes[~ignored] < 1) | (outcomes[~ignored] > b.shape[0])):
        raise ValueError("HMM outcomes must be 1..n_outcomes")

    n = values.size
    alpha = np.full((n, d), np.nan, dtype=np.float64)
    first_likelihood = prior * b[outcomes[0] - 1]
    alpha[0] = first_likelihood / np.sum(first_likelihood)

    for k in range(1, n):
        if ignored[k]:
            alpha[k] = alpha[k - 1]
            continue
        tmp = b[outcomes[k] - 1] * (alpha[k - 1] @ transition)
        alpha[k] = tmp / np.sum(tmp)

    alpha_hat = np.vstack((prior, alpha))[:-1]
    traj = {"alpr": alpha, "alprhat": alpha_hat}
    return traj, alpha.copy()
