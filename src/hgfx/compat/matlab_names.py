"""Name and option adapters for frozen HGF Toolbox entry-point conventions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hgfx.core.parameters import ModelConfig
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


def strip_config_suffix(value: str) -> str:
    """Accept both model and model_config spellings."""

    return value[:-7] if value.endswith("_config") else value


def model_name(value: str | ModelConfig) -> str:
    if isinstance(value, ModelConfig):
        return value.model
    return strip_config_suffix(str(value))


def require_model(value: str | ModelConfig, expected: str, *, role: str) -> None:
    actual = model_name(value)
    if actual != expected:
        raise ValueError(
            f"M13 fit compatibility currently supports {role}={expected!r}; got {actual!r}"
        )


def coerce_quasinewton_options(
    value: str | Mapping[str, Any] | QuasiNewtonOptions | None,
) -> QuasiNewtonOptions:
    """Accept the frozen config name, a config-like mapping, or native options."""

    if value is None:
        return QuasiNewtonOptions()
    if isinstance(value, QuasiNewtonOptions):
        return value
    if isinstance(value, str):
        normalized = strip_config_suffix(value)
        if normalized != "quasinewton_optim":
            raise ValueError(f"Unsupported compatibility optimizer: {value}")
        return QuasiNewtonOptions()

    aliases = {
        "tolGrad": "tol_grad",
        "tolArg": "tol_arg",
        "maxStep": "max_step",
        "maxIter": "max_iter",
        "maxRegu": "max_regu",
        "maxRst": "max_rst",
        "verbose": "verbose",
        "optIter": "opt_iter",
        "tol_grad": "tol_grad",
        "tol_arg": "tol_arg",
        "max_step": "max_step",
        "max_iter": "max_iter",
        "max_regu": "max_regu",
        "max_rst": "max_rst",
        "opt_iter": "opt_iter",
    }
    translated: dict[str, Any] = {}
    unsupported: list[str] = []
    for key, item in value.items():
        if key in {"algorithm", "opt_algo"}:
            continue
        if key in {"nRandInit", "seedRandInit"}:
            unsupported.append(key)
            continue
        target = aliases.get(key)
        if target is None:
            unsupported.append(key)
        else:
            translated[target] = item
    if unsupported:
        raise ValueError(
            "Unsupported optimizer config fields in the M13 public wrapper: "
            + ", ".join(sorted(unsupported))
            + ". Use restart_free_parameters for deterministic multistart fitting."
        )
    return QuasiNewtonOptions(**translated)
