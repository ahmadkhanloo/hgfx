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

    def forward_scalar(self, value: float) -> float:
        if self.kind is TransformKind.IDENTITY:
            return float(value)
        if self.kind is TransformKind.EXPONENTIAL:
            return math.exp(float(value))
        if self.kind is TransformKind.SIGMOID:
            x = float(value)
            return 1.0 / (1.0 + math.exp(-x))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def inverse_scalar(self, value: float) -> float:
        if self.kind is TransformKind.IDENTITY:
            return float(value)
        if self.kind is TransformKind.EXPONENTIAL:
            return math.log(float(value))
        if self.kind is TransformKind.SIGMOID:
            x = float(value)
            if not 0.0 < x < 1.0:
                raise ValueError("Sigmoid inverse requires value in (0, 1)")
            return math.log(x / (1.0 - x))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def forward(self, values: np.ndarray | list[float]) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if self.kind is TransformKind.IDENTITY:
            return array.copy()
        if self.kind is TransformKind.EXPONENTIAL:
            return np.exp(array)
        if self.kind is TransformKind.SIGMOID:
            with np.errstate(over="ignore"):
                return 1.0 / (1.0 + np.exp(-array))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def inverse(self, values: np.ndarray | list[float]) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if self.kind is TransformKind.IDENTITY:
            return array.copy()
        if self.kind is TransformKind.EXPONENTIAL:
            return np.log(array)
        if self.kind is TransformKind.SIGMOID:
            if np.any((array <= 0.0) | (array >= 1.0)):
                raise ValueError("Sigmoid inverse requires values in (0, 1)")
            return np.log(array / (1.0 - array))
        raise ValueError(f"Unsupported transform: {self.kind}")


IDENTITY = TransformSpec(TransformKind.IDENTITY)
EXPONENTIAL = TransformSpec(TransformKind.EXPONENTIAL)
SIGMOID = TransformSpec(TransformKind.SIGMOID)
