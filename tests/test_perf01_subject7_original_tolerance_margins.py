"""Fail-closed synthetic tampering checks for original threshold exceedance evidence."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
from derive_subject7_original_tolerance_margins import (
    analyze, check_pair, SOURCE, SOURCE_SHA256, STATUS,
)
class ArchivedToleranceMargins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/SOURCE).read_bytes())

    def expect_tamper(self,edit,pattern):
        case=deepcopy(self.original)
        edit(case)
        with self.assertRaisesRegex(ValueError,pattern):
            analyze(case,SOURCE_SHA256)

    def test_true_archived_original_all_four_and_six_contrasts(self):
        report=analyze(self.original,SOURCE_SHA256)
        self.assertEqual(report["status"],STATUS)
        self.assertEqual(report["perf01c"],"NOT_FROZEN")
        self.assertEqual(report["original_fit"],
                         "63/64 SCIENTIFIC NONPASS; original subject index 7")
        self.assertEqual(report["performance_timing"],"NOT_RUN")
        self.assertEqual(len(report["same_runner_blas_cross_mode"]),6)
        self.assertEqual(len(report["cross_run_original_matlab"]),4)
        for name,record in report["cross_run_original_matlab"].items():
            n=4 if name.startswith("SkylakeX") else 14
            self.assertEqual(record["traj.mu"]["failed_cells"],n)
            self.assertEqual(record["traj.muhat"]["failed_cells"],n)
            self.assertTrue(all(x["exceedance_ratio"]>1
                 for x in record["traj.mu"]["cells"]))
        for name,record in report["same_runner_blas_cross_mode"].items():
            n=0 if "within_mode" in name else 4
            self.assertEqual(record["traj.mu"]["failed_cells"],n)

    def test_wrong_immutable_source_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            analyze(self.original,"0"*64)

    def test_fabricated_64_of_64_science_pass_rejected(self):
        self.expect_tamper(lambda r:r.update(original_science="64/64 PASS"),
                           "scientific")

    def test_historical_trajectory_atol_mutation_rejected(self):
        self.expect_tamper(
            lambda r:r["vs_original"]["SkylakeX_1"]["vs_original_matlab"]["fields"]["traj.mu"].update(atol=1e-8),
            "tolerance")

    def test_historical_trajectory_rtol_mutation_rejected(self):
        self.expect_tamper(
            lambda r:r["pairwise"]["cross_mode_first"]["original_numeric_tolerances"]["fields"]["traj.muhat"].update(rtol=1e-4),
            "tolerance")

    def test_deleted_failed_trial_rejected(self):
        self.expect_tamper(
            lambda r:r["vs_original"]["Haswell_1"]["vs_original_matlab"]["critical_field_mismatch_details"]["traj.mu"].pop(),
            "failed trialwise")

    def test_deleted_comparison_rejected(self):
        self.expect_tamper(lambda r:r["pairwise"].pop("cross_mode_second"),
                           "comparisons missing")

    def test_false_binary64_exactness_rejected(self):
        self.expect_tamper(lambda r:r["pairwise"]["cross_mode_first"]["strict_serialized_binary64"].update(
                           all_serialized_binary64_equal=True),
                           "binary equality")

    def test_falsified_original_numeric_bound_rejected(self):
        self.expect_tamper(lambda r:r["vs_original"]["SkylakeX_1"]["vs_original_matlab"]["critical_field_mismatch_details"]["traj.mu"][0].update(
                           unchanged_tolerance_bound_at_reference=7.0e-9),
                           "tolerance-bound")

    def test_falsified_original_delta_rejected(self):
        self.expect_tamper(lambda r:r["vs_original"]["SkylakeX_1"]["vs_original_matlab"]["critical_field_mismatch_details"]["traj.mu"][0].update(
                           abs_difference=9e-6),
                           "residual")

    def test_falsified_lagged_mu_hat_index_rejected(self):
        def tamper(r):
            item=r["vs_original"]["SkylakeX_1"]["vs_original_matlab"][
                "critical_field_mismatch_details"]["traj.muhat"][1]
            item["index_zero_based"]=[108,1]
            item["trial_one_based"]=109
        self.expect_tamper(tamper,"one-trial")

    def test_falsified_first_mismatch_index_rejected(self):
        self.expect_tamper(lambda r:r["vs_original"]["SkylakeX_1"]["vs_original_matlab"]["critical_field_mismatch_details"]["traj.muhat"][0].update(
                           index_zero_based=[83,1]),
                           "first mismatch")

    def test_mismatched_mu_muhat_source_values_rejected(self):
        self.expect_tamper(lambda r:r["pairwise"]["cross_mode_first"]["original_numeric_tolerances"]["critical_field_mismatch_details"]["traj.muhat"][0].update(
                           hgfx_value=0.5),
                           "one-trial|residual")

    def test_preserved_same_blas_has_no_failed_cells(self):
        d=self.original["pairwise"]["Haswell_within_mode"]["original_numeric_tolerances"]
        report=check_pair(d,[])
        self.assertEqual(report["traj.mu"]["failed_cells"],0)
        self.assertEqual(report["traj.muhat"]["failed_cells"],0)

if __name__=="__main__":
    unittest.main()
