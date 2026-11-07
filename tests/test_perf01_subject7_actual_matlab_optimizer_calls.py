"""Fail-closed author-side checks for true source MATLAB-owned direct-call chronology."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "benchmarks" / "runtime_v1" / "replay_subject7_actual_matlab_optimizer_calls.py"
spec = importlib.util.spec_from_file_location("matlab_actual_calls", P)
import sys
sys.path.insert(0, str(P.parent))   # same-folder existing source-independent comparator
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
SOURCE = "val = f(x);\nnewval  = f(newx);\nval = f(x);\n"


def fixture():
    meta = {
        "schema": audit.SCHEMA,
        "frozen_matlab_sha": audit.MATLAB,
        "frozen_hgfx_sha": audit.HGFX,
        "original_science": "63/64 SCIENTIFIC NONPASS",
        "original_failure_mu": 4,
        "original_failure_muhat": 4,
        "subject_index_zero_based": 7,
        "original_trial_count": 128,
        "compared_26_fields": 26,
        "finite_native_history_count": 25,
        "hook_count": 1,
        "delegated": True,
        "native_instrumented_stable_identical": True,
        "native_instrumented_history_identical": True,
        "not_an_original_optimizer_source_patch": True,
        "not_a_source_if_branch_event_trace": True,
        "independent_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN", "timing": "NOT_RUN",
        "github_run_id": "12345", "tested_sha": "f"*40,
        "source_initial_line": 1,
        "source_linesearch_line": 2,
        "source_reset_line": 3,
        "direct_counts": [1,2,0,0],
        "direct_call_count": 3, "total_calls": 5, "indirect_calls": 2,
    }
    calls = [
        {"kind":"INITIAL","call_number":1,"direct_index_zero_based":0,
         "optimizer_name":"quasinewton_optim","source_line":1,
         "free_x":list(audit.START),"private_objective":10.,
         "finite":True,"realmax_sentinel":False},
        {"kind":"LINESEARCH","call_number":3,"direct_index_zero_based":1,
         "optimizer_name":"quasinewton_optim","source_line":2,
         "free_x":[1.,2.,3.],"private_objective":9.,
         "finite":True,"realmax_sentinel":False},
        {"kind":"LINESEARCH","call_number":5,"direct_index_zero_based":2,
         "optimizer_name":"quasinewton_optim","source_line":2,
         "free_x":[4.,5.,6.],"private_objective":8.,
         "finite":True,"realmax_sentinel":False},
    ]
    report = {"schema":audit.SCHEMA,"metadata":meta,
              "direct_calls":calls,"native_history_finite_zero_based":list(range(25)),
              "native_history_x":[list(audit.START)]+[[4.,5.,6.]]*24,
              "native_history_val":[10.]+[8.]*24,
              "original_science":"63/64 SCIENTIFIC NONPASS",
              "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN","timing":"NOT_RUN"}
    cases=[{} for _ in range(8)]
    cases[7]={"mismatched_fields":["traj.mu","traj.muhat"],
              "fields":{"traj.mu":{"mismatch_count":4},
                        "traj.muhat":{"mismatch_count":4}}}
    original={"subject_count":64,
              "classification_counts":{
                  "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
                  "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1},
              "cases":cases}
    return report,original


class NativeSourceCallTraceTests(unittest.TestCase):
    def test_valid_source_calltrace_and_ambiguous_terminal_caveat(self):
        report,original=fixture()
        got=audit.validate_trace(report,SOURCE,original)
        self.assertEqual(got["direct_source_call_count"],3)
        self.assertEqual(got["matching_source_direct_call_history_rows"],24)
        self.assertTrue(got["ambiguous_terminal_slots_not_labelled_as_branch_events"])
        self.assertEqual(got["original_scientific_fitting"],"63/64 SCIENTIFIC NONPASS")

    def test_frozen_source_line_number_mismatch_fails(self):
        report,original=fixture()
        report["direct_calls"][1]["source_line"]=3
        with self.assertRaisesRegex(ValueError,"source objective site"):
            audit.validate_trace(report,SOURCE,original)

    def test_missing_direct_candidate_fails(self):
        report,original=fixture()
        report["direct_calls"].pop()
        with self.assertRaisesRegex(ValueError,"inventory"):
            audit.validate_trace(report,SOURCE,original)

    def test_ordinal_swapped_fails(self):
        report,original=fixture()
        report["direct_calls"][1]["call_number"]=6
        with self.assertRaisesRegex(ValueError,"order"):
            audit.validate_trace(report,SOURCE,original)

    def test_original_failed_muhat_erased_fails(self):
        report,original=fixture()
        original["cases"][7]["fields"]["traj.muhat"]["mismatch_count"]=0
        with self.assertRaisesRegex(ValueError,"4\\+4"):
            audit.validate_trace(report,SOURCE,original)

    def test_unfrozen_review_status_forgery_fails(self):
        report,original=fixture()
        report["metadata"]["independent_review"]="APPROVED"
        with self.assertRaisesRegex(ValueError,"scientific status"):
            audit.validate_trace(report,SOURCE,original)

    def test_missing_nan_vector_coordinate_fails(self):
        report,original=fixture()
        report["direct_calls"][1]["free_x"][1]=float("nan")
        with self.assertRaisesRegex(ValueError,"missing/nonfinite"):
            audit.validate_trace(report,SOURCE,original)

    def test_false_native_instrumentation_neutrality_fails(self):
        report,original=fixture()
        report["metadata"]["native_instrumented_history_identical"]=False
        with self.assertRaisesRegex(ValueError,"scientific status"):
            audit.validate_trace(report,SOURCE,original)

    def test_unknown_frozen_source_callsite_fails(self):
        report,original=fixture()
        report["direct_calls"][2]["kind"]="UNRECOGNIZED"
        with self.assertRaisesRegex(ValueError,"source objective site"):
            audit.validate_trace(report,SOURCE,original)

    def test_source_revision_with_duplicate_line_fails(self):
        report,original=fixture()
        with self.assertRaisesRegex(ValueError,"source"):
            audit.validate_trace(report,SOURCE+"val=f(x);\n",original)

    def test_reject_changed_bfgs_bytes(self):
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            audit.verify_bfgs_source(b"fake",b"fake")


if __name__ == "__main__":
    unittest.main()
