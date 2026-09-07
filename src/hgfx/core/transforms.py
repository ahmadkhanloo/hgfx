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


@dataclass(frozen=True)
class TransformSpec:
    kind: TransformKind

    def forward_scalar(self, value: float) -> float:
        if self.kind is TransformKind.IDENTITY:
            return float(value)
        if self.kind is TransformKind.EXPONENTIAL:
            return math.exp(float(value))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def inverse_scalar(self, value: float) -> float:
        if self.kind is TransformKind.IDENTITY:
            return float(value)
        if self.kind is TransformKind.EXPONENTIAL:
            return math.log(float(value))
        raise ValueError(f"Unsupported transform: {self.kind}")

    def forward(self, values: np.ndarray | list[float]) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if self.kind is TransformKind.IDENTITY:
            return array.copy()
        if self.kind is TransformKind.EXPONENTIAL:
            return np.exp(array)
        raise ValueError(f"Unsupported transform: {self.kind}")

    def inverse(self, values: np.ndarray | list[float]) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if self.kind is TransformKind.IDENTITY:
            return array.copy()
        if self.kind is TransformKind.EXPONENTIAL:
            return np.log(array)
        raise ValueError(f"Unsupported transform: {self.kind}")


IDENTITY = TransformSpec(TransformKind.IDENTITY)
EXPONENTIAL = TransformSpec(TransformKind.EXPONENTIAL)
