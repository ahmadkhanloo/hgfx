"""REV-2.4 archived endpoint source coverage fail-closed tests: no science."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.compstat_rev24_endpoint_coverage import (
    COHORT_INPUT_SHA256, COHORT_INPUT_GIT_BLOB, cohort_source, audit_coverage,
)


class OriginalEndpointCoverageTests(unittest.TestCase):
    def test_original_pins_have_full_digests(self):
        self.assertEqual(len(COHORT_INPUT_SHA256), 64)
        self.assertEqual(len(COHORT_INPUT_GIT_BLOB), 40)

    def test_noncanonical_source_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "binary_128_s64.json"
            path.write_text('{"subject_count":64}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Original cohort input SHA256 mismatch"):
                cohort_source(path)

    def test_required_archives_not_silently_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.zip"
            with self.assertRaisesRegex(ValueError, "Missing d02 original ZIP"):
                audit_coverage(path, path, path, path)

    def test_source_gate_does_not_expose_participant_values(self):
        source = Path(__file__).resolve().parents[2] / "tools" / "compstat_rev24_endpoint_coverage.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn('"participant_data_in_report": False', text)
        self.assertIn('"scientific_gate": "NOT_ASSESSED"', text)
        self.assertIn('"matlab_hgfx_paired_objective_executed": False', text)


if __name__ == "__main__":
    unittest.main()
