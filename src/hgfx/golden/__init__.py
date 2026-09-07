"""Golden-reference fixture loading and numerical diff tools."""

from .diff import DiffReport, Divergence, compare_mappings
from .io import import_matlab_json_fixture, load_fixture, load_npz_mapping
from .schema import FIXTURE_SCHEMA_VERSION, GoldenFixture, FixtureValidationError

__all__ = [
    "DiffReport",
    "Divergence",
    "FIXTURE_SCHEMA_VERSION",
    "GoldenFixture",
    "FixtureValidationError",
    "compare_mappings",
    "import_matlab_json_fixture",
    "load_fixture",
    "load_npz_mapping",
]
