"""Fail-closed raw SHA, complete 20-field, 71x128x2 original unitsq archive replay controls."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import replay_original_x0_unitsq_arithmetic_archive as replay
from replay_original_x0_infstates_observation_archive import first_difference
from compare_original_x0_unitsq_arithmetic import STAGE_NAMES,finite_vector,ACTIVE_STAGES


class UnitsqSourceArchiveReplayControls(unittest.TestCase):
    def test_sha_pin_exact_original_new_true_source(self):
        self.assertEqual(replay.ORIGINAL_RUN,"42408646109")
        self.assertEqual(replay.ORIGINAL_SHA,"8e9a21e62efc5099e7e519bbf13b44f505cd1ad8")
        self.assertEqual(len(replay.SOURCE_SHA),3)
        self.assertEqual(replay.SOURCE_SHA["independent-original-71x128x2-unitsq-first-arithmetic-stage.json"],
                         "9a65d743a13f1da62e6751e4636605d9c712b6bb1575debfae515006fb2abb7c")

    def test_source_sha_tampering_fails_before_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"source.json"
            path.write_text('{"original_scientific_fitting":"64/64 PASS"}')
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                replay.load_sha(path,"0"*64)

    def test_missing_true_source_file_fails(self):
        with self.assertRaises(FileNotFoundError):
            replay.load_sha(Path("/absent-original-unitsq-71x128x2-source.json"),"0"*64)

    def test_signed_zero_exact_difference(self):
        self.assertIn("binary64",first_difference({"v":[0.]},{"v":[-0.]}))

    def test_one_ulp_exact_difference(self):
        self.assertIn("binary64",first_difference({"v":[1.]},{"v":[math.nextafter(1.,math.inf)]}))

    def test_original_71_node_denominator_changed(self):
        self.assertIn("length",first_difference({"nodes":[0]*71},{"nodes":[0]*70}))

    def test_original_two_predictor_cases_changed(self):
        self.assertIn("length",first_difference({"cases":["hgfx_predictor","matlab_predictor"]},
                                                 {"cases":["hgfx_predictor"]}))

    def test_missing_original_numerical_stage(self):
        self.assertIn("key sets",first_difference(
            {"stage_arrays":{"logx_selected":1.,"pow_x":2.}},
            {"stage_arrays":{"logx_selected":1.}}))

    def test_original_scientific_nonpass_forgery(self):
        self.assertIn("differs",first_difference(
            {"original_fitting":"63/64 SCIENTIFIC NONPASS"},
            {"original_fitting":"64/64 PASS"}))

    def test_independent_reviewer_forgery(self):
        self.assertIn("differs",first_difference(
            {"external_independent_scientific_review":"NOT_RECEIVED"},
            {"external_independent_scientific_review":"APPROVE_PROSPECTIVE_FREEZE"}))

    def test_raw_stage_count_complete_and_source_mask(self):
        self.assertEqual(len(STAGE_NAMES),20)
        self.assertTrue(set(ACTIVE_STAGES).issubset(set(STAGE_NAMES)))
        self.assertEqual(len(set(STAGE_NAMES)),20)

    def test_short_original_trial_vector_rejected(self):
        with self.assertRaisesRegex(ValueError,"128"):
            finite_vector([1.]*127,"authentic original missing")

    def test_original_nonfinite_intermediate_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            finite_vector([1.]*127+[float("nan")],"original corrupted")

    def test_binary64_report_type_forgery_rejected(self):
        self.assertIn("types",first_difference({"native_source_status":True},
                                                {"native_source_status":1}))


if __name__=="__main__":
    unittest.main()
