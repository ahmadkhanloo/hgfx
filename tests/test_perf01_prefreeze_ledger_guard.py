"""Fail-closed derived-evidence cross-ledger controls, NOT independent scientific approval."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from verify_perf01_prefreeze_ledger import load, verify, RESULT_STATUS

class TestPrefreezeReviewerLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, cls.digests = load(Path(__file__).resolve().parents[1])

    def check_raises(self, key, update, pattern):
        d = deepcopy(self.original)
        update(d[key])
        with self.assertRaisesRegex(ValueError, pattern):
            verify(d)

    def test_real_derived_ledgers_consistent_but_not_approved(self):
        d=verify(self.original)
        self.assertEqual(d["status"],RESULT_STATUS)
        self.assertEqual(d["reviewer_independent_verdict"],"NOT_RECEIVED")
        self.assertEqual(d["performance_timing"],"NOT_RUN")
        self.assertEqual(d["cohort"],{"rows":576,"completed":448,"both_invalid":128})
        self.assertEqual(d["fit"]["fitting"],"63/64 NONPASS")
        self.assertEqual(d["eligibility"]["blocked"],12)
        self.assertEqual(d["abba"]["cross_dispatch_numeric_mismatch"],4)
        self.assertEqual(len(self.digests),5)

    def test_dropped_cohort_subject_rejected(self):
        self.check_raises("cohort",lambda d:d["rows"].pop(), "576-case")

    def test_rewritten_invalid_reference_as_complete_rejected(self):
        def tamper(d):
            row=next(x for x in d["rows"] if x["model"]=="hgf_binary" and x["trials"]==512)
            row["classification"]="COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"
        self.check_raises("cohort",tamper,"448/128")

    def test_source_sha_or_identity_changed_rejected(self):
        self.check_raises("cohort",lambda d:d.update(hgfx_source_sha="f"*40),"source/run identity")

    def test_fitted_one_bad_subject_hidden_rejected(self):
        def tamper(d):
            d["cases"][7]["classification"]="FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
        self.check_raises("fit",tamper,"63/64")

    def test_fitted_four_bad_mu_cells_hidden_rejected(self):
        def tamper(d): d["cases"][7]["fields"]["traj.mu"]["mismatch_count"]=0
        self.check_raises("fit",tamper,"mismatch count")

    def test_fitted_trajectory_acceptance_threshold_changed_rejected(self):
        def tamper(d): d["cases"][3]["fields"]["traj.mu"]["atol"]=3e-9
        self.check_raises("fit",tamper,"tolerance")

    def test_candidate_hidden_blocked_subcase_rejected(self):
        def tamper(d): d["cases"].pop()
        self.check_raises("candidate",tamper,"28-case")

    def test_candidate_false_independent_review_rejected(self):
        self.check_raises("candidate",lambda d:d.update(independent_review="APPROVED"),"review/timing")

    def test_candidate_posthoc_different_classification_rejected(self):
        def tamper(d): d["cases"][0]["classification"]="DIAGNOSTIC_PASS"
        self.check_raises("candidate",tamper,"classification changed")

    def test_abba_endpoint_source_run_changed_rejected(self):
        def tamper(d): d["analysis_provenance"]["archived_source_run_id"]="1"
        self.check_raises("abba",tamper,"source/analysis provenance")

    def test_abba_raw_checksum_tamper_rejected(self):
        def tamper(d): d["fresh_raw_sha256"]["SkylakeX_2"]="0"*64
        self.check_raises("abba",tamper,"raw hashes")

    def test_abba_within_mode_false_bitwise_claim_rejected(self):
        def tamper(d): d["pairwise"]["Haswell_within_mode"]["strict_serialized_binary64"]["all_serialized_binary64_equal"]=False
        self.check_raises("abba",tamper,"bitwise or cross-mode")

    def test_abba_cross_mode_mismatch_hidden_rejected(self):
        def tamper(d): d["pairwise"]["cross_mode_first"]["original_numeric_tolerances"]["mismatched_fields"]=[]
        self.check_raises("abba",tamper,"bitwise or cross-mode")

    def test_abba_historical_matlab_mismatch_hidden_rejected(self):
        def tamper(d): d["vs_original"]["SkylakeX_1"]["vs_original_matlab"]["mismatched_fields"]=[]
        self.check_raises("abba",tamper,"MATLAB old-tolerance")

if __name__ == "__main__":
    unittest.main()
