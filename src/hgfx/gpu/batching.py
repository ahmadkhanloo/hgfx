"""Shape bucketing and padding primitives for the JAX fast path."""

from __future__ import annotations

import math

import jax.numpy as jnp


def trial_length_bucket(length: int, *, minimum: int = 16) -> int:
    """Return a power-of-two bucket large enough for the trial count."""

    if length <= 0:
        raise ValueError("trial length must be positive")
    if minimum <= 0:
        raise ValueError("minimum bucket must be positive")
    target = max(int(length), int(minimum))
    return 1 << int(math.ceil(math.log2(target)))


def pad_trials(array, bucket: int, *, value: float = float("nan")):
    """Pad only the leading trial axis, preserving trailing dimensions."""

    x = jnp.asarray(array)
    if x.ndim == 0:
        raise ValueError("trial arrays must have at least one dimension")
    if bucket < x.shape[0]:
        raise ValueError("bucket cannot be shorter than the trial array")
    pad = bucket - x.shape[0]
    widths = ((0, pad),) + tuple((0, 0) for _ in range(x.ndim - 1))
    return jnp.pad(x, widths, constant_values=value)


def pad_mask(mask, bucket: int, *, value: bool = True):
    x = jnp.asarray(mask, dtype=jnp.bool_)
    if x.ndim != 1:
        raise ValueError("trial masks must be one-dimensional")
    if bucket < x.shape[0]:
        raise ValueError("bucket cannot be shorter than the trial mask")
    return jnp.pad(x, ((0, bucket - x.shape[0]),), constant_values=value)


__all__ = ["trial_length_bucket", "pad_trials", "pad_mask"]
