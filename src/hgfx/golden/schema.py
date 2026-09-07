"""Schema objects for frozen MATLAB golden fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

FIXTURE_SCHEMA_VERSION = 1

REQUIRED_METADATA_FIELDS = (
    "hgf_version",
    "hgf_commit_sha",
    "matlab_version",
    "fixture_schema_version",
    "model_name",
    "response_model_name",
    "optimizer_name",
    "rng_seed",
)


class FixtureValidationError(ValueError):
    """Raised when a golden fixture violates the HGFX fixture schema."""


@dataclass(frozen=True)
class GoldenFixture:
    path: Path
    metadata: dict[str, Any]
    config: dict[str, Any]
    inputs: dict[str, np.ndarray]
    expected: dict[str, np.ndarray]


def validate_metadata(metadata: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_METADATA_FIELDS if field not in metadata]
    if missing:
        raise FixtureValidationError(
            "Fixture metadata missing required fields: " + ", ".join(missing)
        )
    if metadata["fixture_schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise FixtureValidationError(
            f"Unsupported fixture schema version {metadata['fixture_schema_version']!r}; "
            f"expected {FIXTURE_SCHEMA_VERSION}"
        )
