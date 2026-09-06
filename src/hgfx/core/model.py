from __future__ import annotations
from typing import Protocol, Any


class PerceptualModel(Protocol):
    def init_state(self, config: Any) -> Any: ...
    def step(self, state: Any, input_t: Any, params: Any) -> tuple[Any, Any]: ...


class ResponseModel(Protocol):
    def log_prob(self, response: Any, inf_state: Any, params: Any) -> Any: ...
