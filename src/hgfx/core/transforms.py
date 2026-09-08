"""Parameter transform specifications used by the MATLAB compatibility layer.

M2 defines transform semantics and parameter ordering. Scalar numerical parity
for the underlying utility functions is validated separately in M3.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

import numpy as np


class TransformKind(str, Enum):
    IDENTITY = "identity"
    EXPONENTIAL = "exponential"
    SIGMOID = "sigmoid"


@dataclass(frozen=True)
class TransformSpec:
    kind: TransformKind
    upper: float = 1.0

    def forward_scalar(self, value: float) -> float:
        if self.kind is TransformKind.IDENTITY:
            return float(value)
        if self.kind is TransformKind.EXPONENTIAL:
            return math.exp(float(value))
        if self.kind is TransformKind.SIGMOID:
            x = float(value)
            return float(self.upper) / (1.0 + math.exp(-x))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def inverse_scalar(self, value: float) -> float:
        if self.kind is TransformKind.IDENTITY:
            return float(value)
        if self.kind is TransformKind.EXPONENTIAL:
            return math.log(float(value))
        if self.kind is TransformKind.SIGMOID:
            x = float(value)
            upper = float(self.upper)
            if not 0.0 < x < upper:
                raise ValueError("Sigmoid inverse requires value in (0, upper)")
            return math.log(x / (upper - x))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def forward(self, values: np.ndarray | list[float]) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if self.kind is TransformKind.IDENTITY:
            return array.copy()
        if self.kind is TransformKind.EXPONENTIAL:
            return np.exp(array)
        if self.kind is TransformKind.SIGMOID:
            with np.errstate(over="ignore"):
                return np.float64(self.upper) / (1.0 + np.exp(-array))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def inverse(self, values: np.ndarray | list[float]) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if self.kind is TransformKind.IDENTITY:
            return array.copy()
        if self.kind is TransformKind.EXPONENTIAL:
            return np.log(array)
        if self.kind is TransformKind.SIGMOID:
            upper = np.float64(self.upper)
            if np.any((array <= 0.0) | (array >= upper)):
                raise ValueError("Sigmoid inverse requires values in (0, upper)")
            return np.log(array / (upper - array))
        raise ValueError(f"Unsupported transform: {self.kind}")


IDENTITY = TransformSpec(TransformKind.IDENTITY)
EXPONENTIAL = TransformSpec(TransformKind.EXPONENTIAL)
SIGMOID = TransformSpec(TransformKind.SIGMOID)


def bounded_sigmoid(upper: float) -> TransformSpec:
    return TransformSpec(TransformKind.SIGMOID, float(upper))
