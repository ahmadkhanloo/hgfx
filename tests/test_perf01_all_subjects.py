"""PERF-01 prefreeze all-64 comparison accounting and fail-closed status tests."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))

from compare_all_subjects import analyze, MODELS, HORIZONS, SUBJECTS


def fixtures():
    hs,ms=[],[]
    for model in MODELS:
        for n in HORIZONS:
            for subject in range(SUBJECTS):
                base={"model":model,"trials":n,"subject_index_zero_based":subject,
                      "config_matches_snapshot":True,"forward_status":"COMPLETE",
                      "objective_status":"COMPLETE","negative_log_joint":100.0,
                      "negative_log_likelihood":90.0,"valid_likelihood_trials":n}
                hs.append(dict(base))
                ms.append(dict(base))
    h={"protocol_id":"hgfx-matlab-runtime-1",
       "source_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
       "versions":{"hgfx":"1.0.0"},"cases":hs}
    m={"protocol_id":"hgfx-matlab-runtime-1",
       "oracle_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
       "matlab_release":"2026a","cases":ms}
    return h,m


class TestPerf01AllSubjects(unittest.TestCase):
    def test_complete_576_rows_and_27_nested_strata(self):
        h,m=fixtures()
        report=analyze(h,m)
        self.assertEqual(len(report["rows"]),576)
        self.assertEqual(len(report["strata"]),27)
        self.assertEqual(report["classification_counts"],
            {"COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE":576})
        s=next(x for x in report["strata"] if x["model"]=="hgf_binary"
            and x["trials"]==512 and x["submitted_subjects"]==64)
        self.assertEqual(s["completed_scalar_pairs"],64)

    def test_one_numeric_mismatch_is_retained_not_hidden(self):
        h,m=fixtures()
        m["cases"][0]["negative_log_joint"]=101.0
        report=analyze(h,m)
        self.assertEqual(report["classification_counts"]["SCALAR_MISMATCH"],1)
        self.assertEqual(report["classification_counts"]["COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"],575)

    def test_reference_invalid_counts_not_scientific_pass(self):
        h,m=fixtures()
        h["cases"][0].update(forward_status="INVALID_OR_ERROR",objective_status="INVALID_OR_ERROR",
            forward_error="ValueError: Variational approximation invalid. Parameters are in a region where model assumptions are violated.")
        m["cases"][0].update(forward_status="INVALID_OR_ERROR",objective_status="INVALID_OR_ERROR",
            error_identifier="tapas:hgf:VarApproxInvalid")
        report=analyze(h,m)
        self.assertEqual(report["classification_counts"]["BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC"],1)
        self.assertEqual(report["status"],"DIAGNOSTIC_ONLY_NO_TIMING_NO_SCIENTIFIC_PASS")

    def test_bad_matlab_error_does_not_get_reference_match(self):
        h,m=fixtures()
        h["cases"][0].update(forward_status="INVALID_OR_ERROR",objective_status="INVALID_OR_ERROR",
            forward_error="ValueError: Variational approximation invalid.")
        m["cases"][0].update(forward_status="INVALID_OR_ERROR",objective_status="INVALID_OR_ERROR",
            error_identifier="some:UnrelatedFailure")
        report=analyze(h,m)
        self.assertEqual(report["classification_counts"]["BOTH_INVALID_MECHANISM_UNVERIFIED"],1)

    def test_duplicate_or_missing_subject_rejected(self):
        h,m=fixtures()
        m["cases"][-1]=m["cases"][-2]
        with self.assertRaisesRegex(ValueError,"missing/duplicated"):
            analyze(h,m)
        h,m=fixtures()
        h["cases"].pop()
        with self.assertRaisesRegex(ValueError,"missing/duplicated"):
            analyze(h,m)

    def test_different_product_version_rejected(self):
        h,m=fixtures()
        h["versions"]["hgfx"]="1.1.0b1"
        with self.assertRaisesRegex(ValueError,"Frozen comparator"):
            analyze(h,m)

    def test_one_bad_snapshot_is_blocked(self):
        h,m=fixtures()
        m["cases"][0]["config_matches_snapshot"]=False
        report=analyze(h,m)
        self.assertEqual(report["classification_counts"]["BLOCKED_CONFIG_MISMATCH"],1)


if __name__=="__main__":
    unittest.main()
