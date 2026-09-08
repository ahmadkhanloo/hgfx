"""Stable MATLAB-style result containers for the public compatibility API."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from hgfx.core.parameters import ModelConfig


def _wrap(value: Any) -> Any:
    if isinstance(value, MatlabStruct):
        return value
    if isinstance(value, Mapping):
        return MatlabStruct(value)
    if isinstance(value, tuple):
        return tuple(_wrap(item) for item in value)
    if isinstance(value, list):
        return [_wrap(item) for item in value]
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, MatlabStruct):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_plain(item) for item in value)
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.copy()
    return value


class MatlabStruct(Mapping[str, Any]):
    """Read-only mapping with MATLAB-struct-like attribute access."""

    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, Any] | None = None, **fields: Any) -> None:
        merged = dict(data or {})
        merged.update(fields)
        object.__setattr__(self, "_data", {key: _wrap(value) for key, value in merged.items()})

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __repr__(self) -> str:
        return f"MatlabStruct({self._data!r})"

    def to_dict(self) -> dict[str, Any]:
        """Return a recursively plain dictionary with copied NumPy arrays."""

        return {key: _plain(value) for key, value in self._data.items()}


@dataclass(frozen=True)
class CompatibilityResult:
    """Public result ergonomic in Python and stable for MATLAB-style consumers."""

    kind: Literal["fit", "sim", "sample"]
    u: np.ndarray
    y: np.ndarray | None = None
    irr: tuple[int, ...] = ()
    ign: tuple[int, ...] = ()
    c_prc: MatlabStruct | None = None
    c_obs: MatlabStruct | None = None
    c_opt: MatlabStruct | None = None
    c_sim: MatlabStruct | None = None
    p_prc: MatlabStruct | None = None
    p_obs: MatlabStruct | None = None
    traj: MatlabStruct | None = None
    optim: MatlabStruct | None = None
    yhat: np.ndarray | None = None
    res: np.ndarray | None = None

    @property
    def inputs(self) -> np.ndarray:
        return self.u

    @property
    def responses(self) -> np.ndarray | None:
        return self.y

    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style consumers without giving up attribute access."""

        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)

    def to_dict(self, matlab_style: bool = True) -> dict[str, Any]:
        """Export a stable result mapping.

        With matlab_style=True, fit predictions/residuals live under optim,
        while simModel probabilities may be top-level yhat. Python style
        additionally exposes direct yhat/res aliases.
        """

        if self.kind == "fit":
            names = (
                "u", "y", "irr", "ign", "c_prc", "c_obs", "c_opt", "optim",
                "p_prc", "p_obs", "traj",
            )
        elif self.kind == "sim":
            names = (
                "u", "ign", "c_sim", "p_prc", "c_prc", "p_obs", "c_obs",
                "traj", "y", "yhat",
            )
        else:
            names = (
                "u", "ign", "c_prc", "c_obs", "c_sim", "p_prc", "p_obs",
                "traj", "y",
            )

        output: dict[str, Any] = {}
        for name in names:
            value = getattr(self, name)
            if value is None:
                continue
            output[name] = _plain(value)

        if not matlab_style:
            output["kind"] = self.kind
            if self.yhat is not None:
                output["yhat"] = _plain(self.yhat)
            if self.res is not None:
                output["res"] = _plain(self.res)

        return output


FitResult = CompatibilityResult


def config_struct(config: ModelConfig) -> MatlabStruct:
    """Convert immutable HGFX config metadata to a downstream-friendly struct."""

    fields: dict[str, Any] = {
        "model": config.model,
        "priormus": config.priormus.copy(),
        "priorsas": config.priorsas.copy(),
    }
    fields.update(dict(config.options))
    return MatlabStruct(fields)


def parameter_struct(
    config: ModelConfig,
    native_parameters: np.ndarray,
    *,
    transformed_parameters: np.ndarray | None = None,
) -> MatlabStruct:
    """Create the frozen p_* shape: named native fields plus p/ptrans vectors."""

    native = np.asarray(native_parameters, dtype=np.float64).reshape(-1)
    fields = config.structure_vector(native)
    fields["p"] = native.copy()
    if transformed_parameters is not None:
        fields["ptrans"] = np.asarray(
            transformed_parameters, dtype=np.float64
        ).reshape(-1).copy()
    return MatlabStruct(fields)
