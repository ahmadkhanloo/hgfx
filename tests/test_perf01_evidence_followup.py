"""Fail-closed regression tests for archived subject-7 reference sensitivity.

Synthetic test stubs use a committed diagnostic summary as test data.
These tests do not independently validate MATLAB optimizer scientific behavior.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks" / "runtime_v1"))
from verify_evidence_regression import verify_reference_sensitivity


def fixtures():
    recorded = json.loads((ROOT / "benchmarks" / "runtime_v1" /
        "matlab_sensitivity_results/summary-41870479069.json").read_text())
    recorded = {k: v for k, v in recorded.items()
                if k not in {"workflow_id", "raw_evidence_sha256", "original_artifact"}}
    initial = [None] * 12 + [-3, -6, 3.871201010907891]
    original = {"cases": [{} for _ in range(7)] + [{
        "optim": {
            "init": initial,
            "final": recorded["original_full_final"],
            "negLj": recorded["original_optimal_negative_log_joint"],
        },
    }]}
    return recorded, original


class TestPerf01ReferenceFollowup(unittest.TestCase):
    def test_six_archived_probe_rows_are_retained_without_scientific_pass(self):
        evidence, reference = fixtures()
        actual = verify_reference_sensitivity(evidence, reference)
        self.assertEqual(actual["original_probes"], 6)
        self.assertEqual(actual["out_of_tolerance_probe"], "free_coord_2_minus_eps")
        self.assertEqual(actual["scientific_disposition"],
                         "INDEPENDENT_REVIEW_REQUIRED_NOT_PASS")

    def test_deleted_sensitivity_probe_refuses_regression(self):
        evidence, reference = fixtures()
        evidence["perturbations"].pop()
        with self.assertRaisesRegex(AssertionError, "all six"):
            verify_reference_sensitivity(evidence, reference)

    def test_mismatched_reference_baseline_fails(self):
        evidence, reference = fixtures()
        evidence["reproduction"]["max_endpoint_shift"] = 1e-4
        with self.assertRaisesRegex(AssertionError, "exactly reproduce"):
            verify_reference_sensitivity(evidence, reference)

    def test_mutated_fitted_endpoint_is_detected(self):
        evidence, reference = fixtures()
        evidence["perturbations"][4]["optimized_full_final"][12] += 0.1
        with self.assertRaisesRegex(AssertionError, "differs from actual"):
            verify_reference_sensitivity(evidence, reference)

    def test_unreviewed_evidence_cannot_be_reclassified_as_pass(self):
        evidence, reference = fixtures()
        evidence["classification"] = "SCIENTIFIC_PASS"
        with self.assertRaisesRegex(AssertionError, "improperly|misclassified|hidden"):
            verify_reference_sensitivity(evidence, reference)

    def test_recorded_step_must_equal_ieee_ulp_of_original_start(self):
        evidence, reference = fixtures()
        probe = evidence["perturbations"][0]
        probe["step_size"] *= 2
        probe["signed_step"] *= 2
        with self.assertRaisesRegex(AssertionError, "one MATLAB eps"):
            verify_reference_sensitivity(evidence, reference)

    def test_tolerance_status_is_recomputed_not_trusted(self):
        evidence, reference = fixtures()
        evidence["perturbations"][4]["outside_old_v1_final_parameter_tolerance"] = False
        with self.assertRaisesRegex(AssertionError, "original numerical threshold"):
            verify_reference_sensitivity(evidence, reference)

    def test_duplicate_sign_and_missing_original_sign_fails(self):
        evidence, reference = fixtures()
        evidence["perturbations"][1] = deepcopy(evidence["perturbations"][0])
        with self.assertRaisesRegex(AssertionError, "Missing or duplicate"):
            verify_reference_sensitivity(evidence, reference)


if __name__ == "__main__":
    unittest.main()
