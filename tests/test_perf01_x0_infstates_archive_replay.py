"""Fail-closed deep exact original 71-node source report archive replay controls."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import replay_original_x0_infstates_observation_archive as r


class FrozenStageArchiveDeepEqualityTests(unittest.TestCase):
    def test_equal_nested_actual_source_shape(self):
        self.assertIsNone(r.first_difference(
            {"x":[0.,{"a":[[1.,2.],None,True]}]},
            {"x":[0.,{"a":[[1.,2.],None,True]}]}))
    def test_signed_zero_is_not_exact_binary64(self):
        self.assertIn("exact binary64",r.first_difference([0.],[-0.]))
    def test_one_binary64_ulp_detected_without_tolerance(self):
        self.assertIn("exact binary64",
                      r.first_difference([1.],[math.nextafter(1.,math.inf)]))
    def test_missing_original_record_rejected(self):
        self.assertIn("length",r.first_difference([1,2],[1]))
    def test_forged_reviewer_field_detected(self):
        self.assertIn("differs",
                      r.first_difference({"independent_scientific_review":"NOT_RECEIVED"},
                                         {"independent_scientific_review":"APPROVED"}))
    def test_renamed_original_field_rejected(self):
        self.assertIn("key sets",r.first_difference({"zeta":0},{"zeta_new":0}))
    def test_boolean_and_integer_sources_are_not_interchangeable(self):
        self.assertIn("types",r.first_difference({"completed":True},{"completed":1}))
    def test_stringified_node_is_not_original_numeric_node(self):
        self.assertIn("types",r.first_difference([{"ordinal":0}],[{"ordinal":"0"}]))
    def test_source_version_and_sha_pins_are_not_derivative_archive(self):
        self.assertEqual(r.RUN,"42404444341")
        self.assertEqual(r.SHA,"a6168bb2b1be07a0f084abc07599e9ffda61b22b")
        self.assertEqual(len(r.SOURCE_FILES),3)
    def test_missing_file_fails_before_reconstruction(self):
        with self.assertRaises(FileNotFoundError):
            r.read_checked(Path("/does-not-exist-perf01d-x0-source-report.json"),
                           "0"*64)


if __name__=="__main__":unittest.main()
