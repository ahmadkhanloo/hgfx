"""Device discovery and placement helpers for fast-mode execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import jax

jax.config.update("jax_enable_x64", True)


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    id: int
    platform: str
    device_kind: str


def _devices(platform: str | None = None):
    try:
        return tuple(jax.devices(platform)) if platform is not None else tuple(jax.devices())
    except RuntimeError:
        return ()


def available_devices(platform: str | None = None) -> tuple[DeviceInfo, ...]:
    return tuple(
        DeviceInfo(
            id=int(device.id),
            platform=str(device.platform),
            device_kind=str(device.device_kind),
        )
        for device in _devices(platform)
    )


def has_gpu() -> bool:
    return bool(_devices("gpu"))


def select_device(
    prefer: Literal["auto", "cpu", "gpu"] = "auto",
    *,
    index: int = 0,
):
    """Select a JAX device without substituting for an explicit GPU request."""

    if index < 0:
        raise ValueError("device index must be non-negative")

    if prefer == "auto":
        candidates = _devices("gpu") or _devices("cpu") or _devices()
    elif prefer in {"cpu", "gpu"}:
        candidates = _devices(prefer)
    else:
        raise ValueError("prefer must be 'auto', 'cpu', or 'gpu'")

    if not candidates:
        raise RuntimeError(f"No JAX {prefer} device is available")
    if index >= len(candidates):
        raise IndexError(f"device index {index} out of range for {prefer}")
    return candidates[index]


def device_put(value, *, prefer: Literal["auto", "cpu", "gpu"] = "auto", index: int = 0):
    return jax.device_put(value, select_device(prefer, index=index))


__all__ = [
    "DeviceInfo",
    "available_devices",
    "has_gpu",
    "select_device",
    "device_put",
]
