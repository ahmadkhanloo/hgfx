"""Protect all 28 original PERF-01 cases when incorporating failed 64-fit evidence."""
from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from generate_inputs import cases
from refine_eligibility_fit_cohort import refine, FIT_SUCCESS, FIT_MISMATCH


def fixtures():
    workloads=cases({128:"sha128",512:"sha512",1024:"sha1024"})
    for c in workloads:
        c["case_id"]=c.pop("id")
        c["classification"]="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
        if c["case_id"] in ("throughput_fit_16x128","throughput_fit_64x128"):
            c["classification"]="BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED"
    original={
        "schema":"perf01-prospective-eligibility-candidate-v1",
        "status":"AUTHOR_SIDE_INVENTORY_ONLY_NOT_REVIEWED_NOT_FROZEN_NOT_TIMED",
        "total_predeclared_cases":28,
        "frozen_source_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "frozen_matlab_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "cases":workloads,
    }
    rows=[{"subject_index_zero_based":i,
           "classification":FIT_MISMATCH if i==7 else FIT_SUCCESS}
          for i in range(64)]
    fit={
        "schema":"perf01-paired-full-cohort-fit-diagnostic-v1",
        "status":"UNFROZEN_DIAGNOSTIC_NO_TIMING_NO_SCIENTIFIC_PASS",
        "hgfx_sha":original["frozen_source_sha"],
        "matlab_sha":original["frozen_matlab_sha"],
        "subject_count":64,
        "classification_counts":{FIT_SUCCESS:63,FIT_MISMATCH:1},
        "by_prefix":[{"subject_count":n} for n in (1,16,64)],
        "cases":rows,
    }
    return original,fit


class TestPerf01RefineEligibility(unittest.TestCase):
    def test_original_candidate_unchanged_and_two_blocked_reasons_updated(self):
        original,fit=fixtures()
        pristine=deepcopy(original)
        o=refine(original,fit)
        self.assertEqual(original,pristine)
        self.assertEqual(len(o["cases"]),28)
        self.assertEqual(o["status"],original["status"])
        self.assertEqual(o["independent_review"],"NOT_RECEIVED")
        by_id={x["case_id"]:x for x in o["cases"]}
        self.assertEqual(by_id["throughput_fit_1x128"]["classification"],
                         "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING")
        for prefix,count in ((16,15),(64,63)):
            row=by_id[f"throughput_fit_{prefix}x128"]
            self.assertEqual(row["classification"],
                             "BLOCKED_MULTISUBJECT_FIT_NUMERICAL_MISMATCH")
            self.assertEqual(row["previous_classification"],
                             "BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED")
            self.assertEqual(row["additional_fitting_evidence"]["same_numerical_output"],count)
            self.assertEqual(row["additional_fitting_evidence"]["numerical_mismatch"],1)

    def test_missing_subject_fails(self):
        old,fit=fixtures()
        fit["cases"].pop()
        with self.assertRaisesRegex(ValueError,"Missing or duplicate"):
            refine(old,fit)

    def test_mismatched_reported_source_counts_are_rejected(self):
        old,fit=fixtures()
        fit["classification_counts"]={FIT_SUCCESS:64}
        with self.assertRaisesRegex(ValueError,"conflicts"):
            refine(old,fit)

    def test_wrong_reference_fails(self):
        old,fit=fixtures()
        fit["matlab_sha"]="unrelated"
        with self.assertRaisesRegex(ValueError,"Incompatible"):
            refine(old,fit)

    def test_no_silent_reclassification_if_original_cell_changed(self):
        old,fit=fixtures()
        row=next(x for x in old["cases"] if x["case_id"]=="throughput_fit_16x128")
        row["classification"]="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
        with self.assertRaisesRegex(ValueError,"silently replace"):
            refine(old,fit)


if __name__=="__main__":
    unittest.main()
