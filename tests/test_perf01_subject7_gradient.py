"""PERF-01D frozen same-parameter gradient comparison fail-closed tests."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"))
from compare_subject7_gradient_probes import compare,ANCHORS,TRACE_HASHES,PRODUCT,REFERENCE


def record(engine):
    cases=[]
    for origin in ("hgfx","matlab"):
        for index in ANCHORS:
            cases.append({
                "anchor_origin":origin,"record_index_zero_based":index,
                "free_parameters":[-3.0,-6.0,3.871201010907891],
                "archived_iter_val":100.,
                "objective":100.0,
                "ridders_gradient":[0.1,0.2,0.3],
                "ridders_error":[0.001,0.002,0.003],
                "archived_objective_abs_diff":0.0,"status":"EVALUATED"})
    return {
        "schema":f"perf01d-subject7-{engine}-same-vector-gradient-v1",
        "status":"AUTHOR_SIDE_DIAGNOSTIC_UNTIMED_NO_FIT_NO_GATE_PASS",
        "frozen_hgfx_sha":PRODUCT,"frozen_matlab_sha":REFERENCE,
        "original_trace_run":"42115887599",
        "original_trace_sha":"b378fef6ff93f6efa041f4e8304dafba742ae4ab",
        "original_trace_raw_sha256":dict(TRACE_HASHES),
        "source_run_id":"41863441006",
        "subject_index_zero_based":7,"trials":128,"model":"hgf_binary",
        "observation":"unitsq_sgm","free_indices_zero_based":[12,13,14],
        "gradient_method":"frozen_Ridders_min_steps_10",
        "anchor_indices_zero_based":ANCHORS,"cases":cases,
    }


class TestGradientProbeParity(unittest.TestCase):
    def test_complete_identical_anchors_no_scientific_pass(self):
        out=compare(record("hgfx"),record("matlab"))
        self.assertEqual(out["anchor_count"],10)
        self.assertEqual(out["fully_evaluated_pairs"],10)
        self.assertIn("NO_SCIENTIFIC_PASS",out["status"])
        self.assertEqual(out["gradient_discrepancy_count_under_existing_final_tolerance_as_lens"],0)

    def test_missing_anchor_cannot_be_silently_excluded(self):
        a,b=record("hgfx"),record("matlab")
        a["cases"].pop()
        with self.assertRaisesRegex(ValueError,"retain all 10"):
            compare(a,b)

    def test_duplicate_anchor_rejected(self):
        a,b=record("hgfx"),record("matlab")
        a["cases"][3]=deepcopy(a["cases"][2])
        with self.assertRaisesRegex(ValueError,"incomplete or duplicate"):
            compare(a,b)

    def test_changed_frozen_matlab_source_rejected(self):
        a,b=record("hgfx"),record("matlab")
        b["frozen_matlab_sha"]="wrong"
        with self.assertRaisesRegex(ValueError,"frozen gradient source"):
            compare(a,b)

    def test_identical_parameter_vector_is_essential(self):
        a,b=record("hgfx"),record("matlab")
        b["cases"][3]["free_parameters"][0]+=1e-10
        out=compare(a,b)
        self.assertEqual(out["fully_evaluated_pairs"],9)
        self.assertEqual(out["cases"][3]["status"],"SAME_VECTOR_IDENTITY_VIOLATION")

    def test_gradient_difference_is_retained_as_diagnostic(self):
        a,b=record("hgfx"),record("matlab")
        a["cases"][0]["ridders_gradient"][1]+=0.1
        out=compare(a,b)
        self.assertEqual(out["gradient_discrepancy_count_under_existing_final_tolerance_as_lens"],1)
        self.assertEqual(out["cases"][0]["ridders_gradient"]["number_outside_existing_final_parameter_tolerance"],1)
        self.assertIn("NO_SCIENTIFIC_PASS",out["status"])

    def test_nonfinite_gradient_masks_are_reported(self):
        a,b=record("hgfx"),record("matlab")
        a["cases"][1]["ridders_gradient"][0]=None
        out=compare(a,b)
        self.assertFalse(out["cases"][1]["ridders_gradient"]["nonfinite_masks_match"])
        self.assertEqual(out["gradient_discrepancy_count_under_existing_final_tolerance_as_lens"],1)

    def test_probe_failure_not_disguised_as_full_evaluation(self):
        a,b=record("hgfx"),record("matlab")
        a["cases"][3]["status"]="ERROR"
        out=compare(a,b)
        self.assertEqual(out["fully_evaluated_pairs"],9)
        self.assertEqual(out["cases"][3]["status"],"PROBE_ERROR_OR_INCOMPLETE")

    def test_exact_source_hash_manifest_not_optional(self):
        a,b=record("hgfx"),record("matlab")
        a["original_trace_raw_sha256"]["hgfx_raw.json"]="spoofed"
        with self.assertRaisesRegex(ValueError,"frozen gradient source"):
            compare(a,b)


if __name__ == "__main__":
    unittest.main()
