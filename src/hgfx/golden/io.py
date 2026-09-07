"""Import and load MATLAB golden fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .schema import GoldenFixture, FixtureValidationError, validate_metadata


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FixtureValidationError(f"Missing fixture file: {path}") from exc
    if not isinstance(value, dict):
        raise FixtureValidationError(f"Expected a JSON object in {path}")
    return value


def _flatten_numeric(value: Any, prefix: str = "") -> dict[str, np.ndarray]:
    if isinstance(value, dict):
        out: dict[str, np.ndarray] = {}
        for key in sorted(value):
            child = f"{prefix}/{key}" if prefix else str(key)
            out.update(_flatten_numeric(value[key], child))
        return out
    if not prefix:
        raise FixtureValidationError("Numeric fixture payload must have named fields")
    arr = np.asarray(value)
    if arr.dtype.kind not in "biufc":
        raise FixtureValidationError(f"Fixture field {prefix!r} is not numeric")
    return {prefix: arr}


def _load_npz(path: Path) -> dict[str, np.ndarray]:
    try:
        with np.load(path, allow_pickle=False) as archive:
            return {key: np.asarray(archive[key]) for key in archive.files}
    except FileNotFoundError as exc:
        raise FixtureValidationError(f"Missing fixture file: {path}") from exc


def import_matlab_json_fixture(raw_dir: Path, output_dir: Path) -> GoldenFixture:
    raw_dir = Path(raw_dir)
    output_dir = Path(output_dir)
    metadata = _read_json_object(raw_dir / "metadata.json")
    config = _read_json_object(raw_dir / "config.json")
    inputs = _flatten_numeric(_read_json_object(raw_dir / "input.json"))
    expected = _flatten_numeric(_read_json_object(raw_dir / "expected.json"))
    validate_metadata(metadata)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    np.savez_compressed(output_dir / "input.npz", **inputs)
    np.savez_compressed(output_dir / "expected.npz", **expected)
    return GoldenFixture(output_dir, metadata, config, inputs, expected)


def load_fixture(path: Path) -> GoldenFixture:
    path = Path(path)
    metadata = _read_json_object(path / "metadata.json")
    config = _read_json_object(path / "config.json")
    validate_metadata(metadata)
    return GoldenFixture(
        path,
        metadata,
        config,
        _load_npz(path / "input.npz"),
        _load_npz(path / "expected.npz"),
    )


def load_npz_mapping(path: Path) -> dict[str, np.ndarray]:
    return _load_npz(Path(path))
