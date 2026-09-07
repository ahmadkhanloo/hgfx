"""Parameter/config schemas preserving frozen MATLAB HGF semantics."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from .placeholders import compute_placeholder_values, resolve_placeholder_value
from .priors import PriorStatus, indices_with_status, prior_status
from .transforms import IDENTITY, TransformSpec


@dataclass(frozen=True)
class ParameterSpec:
    """One element of the flat MATLAB parameter vector.

    name identifies the transformed-space parameter, while native_name
    identifies the field produced by the MATLAB transformation function.
    matlab_index is deliberately 1-based.
    """

    name: str
    native_name: str
    matlab_index: int
    prior_mean: float
    prior_variance: float
    transform: TransformSpec = IDENTITY
    component: int | None = None

    @property
    def status(self) -> PriorStatus:
        return prior_status(self.prior_variance)

    @property
    def fixed(self) -> bool:
        return self.status is PriorStatus.FIXED

    @property
    def free(self) -> bool:
        return self.status is PriorStatus.FREE

    @property
    def undefined(self) -> bool:
        return self.status is PriorStatus.UNDEFINED


@dataclass(frozen=True)
class ModelConfig:
    """Immutable compatibility representation of a MATLAB model config."""

    model: str
    parameters: tuple[ParameterSpec, ...]
    options: Mapping[str, Any] = field(default_factory=dict)
    source_files: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        expected = tuple(range(1, len(self.parameters) + 1))
        actual = tuple(parameter.matlab_index for parameter in self.parameters)
        if actual != expected:
            raise ValueError(
                f"MATLAB parameter indices must be contiguous and ordered: {actual!r}"
            )
        names = tuple(parameter.name for parameter in self.parameters)
        if len(set(names)) != len(names):
            raise ValueError("Parameter names must be unique")
        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))

    @property
    def priormus(self) -> np.ndarray:
        return np.asarray(
            [parameter.prior_mean for parameter in self.parameters],
            dtype=np.float64,
        )

    @property
    def priorsas(self) -> np.ndarray:
        return np.asarray(
            [parameter.prior_variance for parameter in self.parameters],
            dtype=np.float64,
        )

    @property
    def free_indices(self) -> tuple[int, ...]:
        return indices_with_status(self.priorsas, PriorStatus.FREE)

    @property
    def fixed_indices(self) -> tuple[int, ...]:
        return indices_with_status(self.priorsas, PriorStatus.FIXED)

    @property
    def undefined_indices(self) -> tuple[int, ...]:
        return indices_with_status(self.priorsas, PriorStatus.UNDEFINED)

    @property
    def matlab_free_indices(self) -> tuple[int, ...]:
        return indices_with_status(
            self.priorsas, PriorStatus.FREE, matlab_one_based=True
        )

    @property
    def matlab_fixed_indices(self) -> tuple[int, ...]:
        return indices_with_status(
            self.priorsas, PriorStatus.FIXED, matlab_one_based=True
        )

    @property
    def matlab_undefined_indices(self) -> tuple[int, ...]:
        return indices_with_status(
            self.priorsas, PriorStatus.UNDEFINED, matlab_one_based=True
        )

    def resolve_placeholders(
        self,
        inputs: np.ndarray | list[float],
    ) -> "ModelConfig":
        placeholders = compute_placeholder_values(inputs)
        resolved = tuple(
            replace(
                parameter,
                prior_mean=resolve_placeholder_value(
                    parameter.prior_mean, placeholders
                ),
                prior_variance=resolve_placeholder_value(
                    parameter.prior_variance, placeholders
                ),
            )
            for parameter in self.parameters
        )
        return replace(self, parameters=resolved)

    def transformed_to_native(
        self,
        transformed: Sequence[float] | np.ndarray,
    ) -> np.ndarray:
        vector = np.asarray(transformed, dtype=np.float64).reshape(-1)
        if vector.size != len(self.parameters):
            raise ValueError(
                f"Expected {len(self.parameters)} parameters, got {vector.size}"
            )
        return np.asarray(
            [
                parameter.transform.forward_scalar(float(value))
                for parameter, value in zip(self.parameters, vector, strict=True)
            ],
            dtype=np.float64,
        )

    def structure_vector(
        self,
        vector: Sequence[float] | np.ndarray,
    ) -> dict[str, float | np.ndarray]:
        values = np.asarray(vector, dtype=np.float64).reshape(-1)
        if values.size != len(self.parameters):
            raise ValueError(
                f"Expected {len(self.parameters)} parameters, got {values.size}"
            )

        grouped: dict[str, list[tuple[int | None, float]]] = {}
        for parameter, value in zip(self.parameters, values, strict=True):
            grouped.setdefault(parameter.native_name, []).append(
                (parameter.component, float(value))
            )

        output: dict[str, float | np.ndarray] = {}
        for name, items in grouped.items():
            if len(items) == 1 and items[0][0] is None:
                output[name] = items[0][1]
                continue
            ordered = sorted(
                items,
                key=lambda item: -1 if item[0] is None else item[0],
            )
            output[name] = np.asarray(
                [value for _, value in ordered],
                dtype=np.float64,
            )
        return output

    def transformed_to_native_structure(
        self,
        transformed: Sequence[float] | np.ndarray,
    ) -> dict[str, float | np.ndarray]:
        return self.structure_vector(self.transformed_to_native(transformed))
