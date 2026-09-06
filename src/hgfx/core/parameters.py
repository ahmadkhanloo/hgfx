from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Transform(Protocol):
    def forward(self, x): ...
    def inverse(self, y): ...


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    prior_mean: float
    prior_variance: float
    fixed: bool = False
