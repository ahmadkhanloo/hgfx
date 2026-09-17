"""Binary softmax that mixes reward and social beliefs in gaze space."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import numpy as np

from hgfx.math.logistic import sigmoid

from .base import ignored_mask, output_arrays, response_vector

Variant = Literal["mu3", "beta"]


def _gaze_and_rewards(inputs: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if inputs.ndim != 2 or inputs.shape[1] < 4:
        raise ValueError("socialreward softmax expects u with 4 columns")
    blue_correct = inputs[:, 0]
    advice_correct = inputs[:, 1]
    blue_value = inputs[:, 2]
    green_value = inputs[:, 3]
    gaze = (blue_correct == advice_correct).astype(np.float64)
    expr_gaze = np.where(gaze == 1.0, blue_value, green_value)
    expr_nogaze = np.where(gaze == 1.0, green_value, blue_value)
    return gaze, expr_gaze, expr_nogaze


def softmax_binary_socialreward(
    responses,
    inf_states,
    ptrans,
    *,
    inputs,
    irregular_trials: Sequence[int] | None = None,
    variant: Variant = "beta",
):
    """Port of tapas_softmax_binary_socialreward4 (beta) and variant 1 (mu3)."""

    states = np.asarray(inf_states, dtype=np.float64)
    u = np.asarray(inputs, dtype=np.float64)
    n = states.shape[0]
    y = response_vector(responses, n)
    p = np.asarray(ptrans, dtype=np.float64).reshape(-1)
    if p.size < 3:
        raise ValueError("socialreward softmax expects [zeta, beta, eta] in transformed space")
    zeta = float(np.exp(p[0]))
    beta0 = float(np.exp(p[1]))
    eta = float(sigmoid(p[2], 1.0))
    gaze, expr_gaze, expr_nogaze = _gaze_and_rewards(u)
    irregular = ignored_mask(n, irregular_trials)
    regular = ~irregular

    if states.ndim == 3:
        x_r = states[:, 0, 0].copy()
        x_a = states[:, 0, 2].copy()
        mu3_r = states[:, min(2, states.shape[1] - 1), 0] if variant == "mu3" else None
        mu3_a = states[:, min(2, states.shape[1] - 1), 2] if variant == "mu3" else None
    else:
        raise ValueError("inf_states must be (trials, levels, streams)")

    x_r = np.where(gaze == 0.0, 1.0 - x_r, x_r)
    px = 1.0 / (x_a * (1.0 - x_a))
    pc = 1.0 / (x_r * (1.0 - x_r))
    wx = zeta * px / (zeta * px + pc)
    wc = pc / (zeta * px + pc)
    belief = wx * x_a + wc * x_r
    beta = np.full(n, beta0, dtype=np.float64)
    if variant == "mu3":
        if mu3_r is None or mu3_a is None:
            raise ValueError("mu3 variant requires level-3 predictions")
        beta = beta0 * np.exp((-mu3_r) + (-mu3_a))

    linear = 1.0 / (
        1.0 + np.exp(-beta * (expr_gaze * belief - expr_nogaze * (1.0 - belief)) * (2.0 * y - 1.0))
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        logged = 1.0 / (
            1.0
            + np.exp(
                -beta
                * (np.log(expr_gaze) * belief - np.log(expr_nogaze) * (1.0 - belief))
                * (2.0 * y - 1.0)
            )
        )
    probc = eta * linear + (1.0 - eta) * logged
    logp, yhat, res = output_arrays(n)
    yr = y[regular]
    pr = probc[regular]
    logp[regular] = np.log(pr)
    yh = yr * pr + (1.0 - yr) * (1.0 - pr)
    yhat[regular] = yh
    res[regular] = (yr - yh) / np.sqrt(yh * (1.0 - yh))
    return logp, yhat, res
