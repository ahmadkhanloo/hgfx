"""Seventh original-source ABBA replay controls, without scientific sign-off."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
from verify_perf01_seven_source_handoff import (
    check_derived, decision_digest, TRACKED_ABBA_SHA256, EXPECTED_RAW, PAIRS,
    EXPECTED_ORIGINAL, STATUS,
)

def original():
    p=ROOT/"benchmarks"/"runtime_v1"/"issue90_results"/"derived-archived-v2-42250539438.json"
    return json.loads(p.read_bytes())

class SevenSourceHandoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=original()

    def test_original_abba_28_fields_and_six_pairs(self):
        r=self.source
        self.assertEqual(set(r["pairwise"]),set(PAIRS))
        self.assertEqual(set(r["vs_original"]),set(EXPECTED_RAW))
        self.assertEqual(r["fresh_raw_sha256"],EXPECTED_RAW)
        self.assertEqual(r["original_science"],"63/64 NONPASS; original subject zero-based 7")
        self.assertEqual(len(decision_digest(r)["pairwise"]),6)
        self.assertIn("NOT_INDEPENDENT_REVIEW",STATUS)
        self.assertEqual(check_derived(r,r)[
            "complete_derived_report_exact_except_analysis_provenance"],True)

    def test_description_only_float_drift_is_distinct_not_scientific_pass(self):
        r=deepcopy(self.source)
        r["pairwise"]["cross_mode_first"]["original_numeric_tolerances"][
            "fields"]["traj.mu"]["max_abs_delta"]+=1e-13
        result=check_derived(r,self.source)
        self.assertFalse(result["complete_derived_report_exact_except_analysis_provenance"])
        self.assertTrue(result[
            "all_six_pairwise_and_four_reference_28_field_decisions_match"])

    def test_missing_one_original_abba_pair_rejected(self):
        r=deepcopy(self.source)
        del r["pairwise"]["cross_mode_second"]
        with self.assertRaisesRegex(AssertionError,"six-pair"):
            check_derived(r,self.source)

    def test_false_same_dispatch_bitwise_equality_rejected(self):
        r=deepcopy(self.source)
        r["pairwise"]["SkylakeX_within_mode"]["strict_serialized_binary64"][
            "all_serialized_binary64_equal"]=False
        with self.assertRaisesRegex(AssertionError,"bitwise condition"):
            check_derived(r,self.source)

    def test_dropped_four_cross_mode_mismatches_rejected(self):
        r=deepcopy(self.source)
        r["pairwise"]["cross_mode_first"]["original_numeric_tolerances"][
            "critical_field_mismatch_details"]["traj.mu"]=[]
        with self.assertRaisesRegex(AssertionError,"critical trial count"):
            check_derived(r,self.source)

    def test_falsified_source_sha_rejected(self):
        r=deepcopy(self.source)
        r["fresh_raw_sha256"]["Haswell_1"]="0"*64
        with self.assertRaisesRegex(AssertionError,"provenance"):
            check_derived(r,self.source)

    def test_source_matlab_failure_hidden_rejected(self):
        r=deepcopy(self.source)
        r["vs_original"]["Haswell_1"]["vs_original_matlab"]["mismatched_fields"]=[]
        with self.assertRaisesRegex(AssertionError,"original MATLAB"):
            check_derived(r,self.source)

    def test_original_numeric_tolerance_change_rejected(self):
        r=deepcopy(self.source)
        r["pairwise"]["cross_mode_first"]["original_numeric_tolerances"][
            "fields"]["traj.mu"]["atol"]=3e-9
        with self.assertRaisesRegex(AssertionError,"DECISIONS"):
            check_derived(r,self.source)

    def test_original_binary64_field_count_mutation_rejected(self):
        r=deepcopy(self.source)
        del r["pairwise"]["cross_mode_first"]["strict_serialized_binary64"][
            "fields"]["traj.mu"]
        with self.assertRaisesRegex(AssertionError,"28 binary64"):
            check_derived(r,self.source)

    def test_failed_original_science_promotion_rejected(self):
        r=deepcopy(self.source)
        r["original_science"]="64/64 PASS"
        with self.assertRaisesRegex(AssertionError,"science status"):
            check_derived(r,self.source)

if __name__=="__main__":
    unittest.main()
