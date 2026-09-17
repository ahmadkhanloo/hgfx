"""Three-choice softmax used by the 3PLR card-volatility response model."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .base import ignored_mask, output_arrays, response_vector


def _card_predictions(inf_states: np.ndarray, predorpost: int) -> tuple[np.ndarray, np.ndarray]:
    states = np.asarray(inf_states, dtype=np.float64)
    pop = 0 if predorpost == 1 else 2
    if states.ndim == 4:
        values = states[:, 0, :, pop]
        log_vol = states[:, 2, :, 0]
    elif states.ndim == 3:
        if states.shape[2] == 3:
            values = states[:, 0, :]
            log_vol = states[:, min(2, states.shape[1] - 1), :]
        elif states.shape[2] >= 6:
            values = states[:, 0, [0, 2, 4]]
            log_vol = states[:, min(2, states.shape[1] - 1), [0, 2, 4]]
        else:
            raise ValueError("could not identify three card prediction trajectories")
    else:
        raise ValueError("unsupported inferred-state layout")
    if values.shape[1] != 3 or log_vol.shape[1] != 3:
        raise ValueError("expected exactly three card trajectories")
    return values, log_vol


def softmax_mab3_card_volatility(
    responses,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
    predorpost: int = 1,
):
    """gamma_i(t) = beta * exp(-muhat_3_i(t))."""

    values, log_vol = _card_predictions(inf_states, predorpost)
    log_vol = np.clip(log_vol, -20.0, 20.0)
    beta = float(np.exp(np.asarray(ptrans, dtype=np.float64).reshape(-1)[0]))
    logits = beta * np.exp(-log_vol) * values
    n = logits.shape[0]
    y = response_vector(responses, n)
    regular = ~ignored_mask(n, irregular_trials)
    yr = y[regular]
    if np.any(yr < 1) or np.any(yr > 3) or np.any(yr != np.floor(yr)):
        raise ValueError("regular choices must be integers in {1,2,3}")
    loc = logits[regular] - np.max(logits[regular], axis=1, keepdims=True)
    log_norm = np.log(np.sum(np.exp(loc), axis=1))
    chosen = loc[np.arange(yr.size), yr.astype(np.int64) - 1] - log_norm
    logp, yhat, res = output_arrays(n)
    logp[regular] = chosen
    yhat[regular] = np.exp(chosen)
    res[regular] = -chosen
    return logp, yhat, res
