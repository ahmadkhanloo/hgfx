"""Binary Volatile Kalman Filter after Piray & Daw, plus dual-stream wrapper."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.math.logistic import sigmoid


def _ignored(n: int, ignored_trials: Sequence[int] | None) -> np.ndarray:
    mask = np.zeros(n, dtype=bool)
    if ignored_trials is None:
        return mask
    for index in ignored_trials:
        if index < 0 or index >= n:
            raise IndexError(f"ignored trial index out of range: {index}")
        mask[index] = True
    return mask


def vkf_native_parameters(parameters, *, transformed: bool) -> np.ndarray:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    if p.size % 3:
        raise ValueError("VKF parameters come in (lambda, v0, omega) blocks")
    if transformed:
        for start in range(0, p.size, 3):
            p[start] = float(sigmoid(p[start], 1.0))
            p[start + 1] = float(np.exp(p[start + 1]))
            p[start + 2] = float(np.exp(p[start + 2]))
    return p


def vkf_binary(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Single-stream binary VKF (`vkf_bin`)."""

    p = vkf_native_parameters(parameters, transformed=transformed)
    if p.size != 3:
        raise ValueError("vkf_binary expects [lambda, v0, omega]")
    lam, v0, omega = p
    o = np.asarray(inputs, dtype=np.float64)
    if o.ndim == 2:
        o = o[:, 0]
    if o.ndim != 1:
        raise ValueError("vkf_binary inputs must be 1D or a matrix")
    ignored = _ignored(o.size, ignored_trials)

    m = 0.0
    w = float(omega)
    v = float(v0)
    n = o.size
    muhat = np.full(n, np.nan, dtype=np.float64)
    mu = np.full(n, np.nan, dtype=np.float64)
    vol = np.full(n, np.nan, dtype=np.float64)
    alpha = np.full(n, np.nan, dtype=np.float64)
    da = np.full(n, np.nan, dtype=np.float64)

    for t in range(n):
        belief = float(sigmoid(m, 1.0))
        muhat[t] = belief
        vol[t] = v
        if ignored[t] or np.isnan(o[t]):
            alpha[t] = 0.0
            da[t] = 0.0
        else:
            m_pre, w_pre = m, w
            delta = float(o[t]) - belief
            k = (w + v) / (w + v + omega)
            a = np.sqrt(w + v)
            m = m + a * delta
            w = (1.0 - k) * (w + v)
            wcov = (1.0 - k) * w_pre
            delta_v = (m - m_pre) ** 2 + w + w_pre - 2.0 * wcov - v
            v = v + lam * delta_v
            alpha[t] = a
            da[t] = delta
        mu[t] = float(sigmoid(m, 1.0))

    traj = {"muhat": muhat, "mu": mu, "vol": vol, "al": alpha, "da": da}
    inf = np.stack((muhat, mu), axis=1)
    return traj, inf


def vkf_reward_social(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Dual-stream binary VKF used by the social-gaze pipeline."""

    u = np.asarray(inputs, dtype=np.float64)
    if u.ndim != 2 or u.shape[1] < 2:
        raise ValueError("vkf_reward_social expects u with at least two columns")
    p = vkf_native_parameters(parameters, transformed=transformed)
    if p.size != 6:
        raise ValueError("vkf_reward_social expects 6 parameters")

    traj_r, _ = vkf_binary(u[:, 0], p[:3], ignored_trials=ignored_trials)
    traj_a, _ = vkf_binary(u[:, 1], p[3:], ignored_trials=ignored_trials)
    traj = {
        "muhat_r": traj_r["muhat"],
        "mu_r": traj_r["mu"],
        "vol_r": traj_r["vol"],
        "al_r": traj_r["al"],
        "da_r": traj_r["da"],
        "muhat_a": traj_a["muhat"],
        "mu_a": traj_a["mu"],
        "vol_a": traj_a["vol"],
        "al_a": traj_a["al"],
        "da_a": traj_a["da"],
    }
    n = u.shape[0]
    inf = np.full((n, 1, 3), np.nan, dtype=np.float64)
    inf[:, 0, 0] = traj_r["muhat"]
    inf[:, 0, 1] = traj_r["mu"]
    inf[:, 0, 2] = traj_a["muhat"]
    return traj, inf
