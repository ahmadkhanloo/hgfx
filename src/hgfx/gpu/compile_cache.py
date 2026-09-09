"""Explicit compile-signature cache for the JAX fast path."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from typing import Any


@dataclass(frozen=True, slots=True)
class CompileSignature:
    """Static compilation identity required by the GPU architecture."""

    model: str
    levels: int
    observation_model: str | None
    dtype: str
    trial_length_bucket: int
    static_options: tuple[tuple[str, Any], ...] = ()


class CompilationCache:
    """Small process-local cache around jitted callables."""

    def __init__(self) -> None:
        self._items: dict[CompileSignature, Callable[..., Any]] = {}
        self._hits = 0
        self._misses = 0
        self._lock = RLock()

    def get_or_create(
        self,
        signature: CompileSignature,
        factory: Callable[[], Callable[..., Any]],
    ) -> Callable[..., Any]:
        with self._lock:
            existing = self._items.get(signature)
            if existing is not None:
                self._hits += 1
                return existing
            compiled = factory()
            self._items[signature] = compiled
            self._misses += 1
            return compiled

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._hits = 0
            self._misses = 0

    def info(self) -> dict[str, int]:
        with self._lock:
            return {
                "size": len(self._items),
                "hits": self._hits,
                "misses": self._misses,
            }


GLOBAL_COMPILE_CACHE = CompilationCache()


__all__ = ["CompileSignature", "CompilationCache", "GLOBAL_COMPILE_CACHE"]
