"""Author-side PERF-01C eligibility inventory stays complete and fail-closed."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from build_eligibility_candidate import classify
from generate_inputs import cases


def evidence():
    registry={"protocol_id":"hgfx-matlab-runtime-1",
              "_bytes_sha256":"fixture-manifest-hash",
              "cases":cases({128:"sha128",512:"sha512",1024:"sha1024"})}
    trial=[]
    rows=[]
    strata=[]
    for model in ("hgf_binary","ehgf_binary","uhgf_binary"):
        for n in (128,512,1024):
            invalid=(model=="hgf_binary" and n in (512,1024))
            trial.append({"model":model,"trials":n,"masked":False,
                "diagnostic_classification":("BOTH_FAILED_FIRST_INVALID_PREFIX_AGREES_UNVERIFIED_MECHANISM"
                    if invalid else "FULL_TRIALWISE_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE")})
            for subject in range(64):
                rows.append({"model":model,"trials":n,"subject_index_zero_based":subject})
            for prefix in (1,16,64):
                completed=0 if invalid else prefix
                missing=prefix-completed
                strata.append({
                    "model":model,"trials":n,"submitted_subjects":prefix,
                    "completed_scalar_pairs":completed,
                    "both_invalid_reference_behavior_pairs":missing,
                    "blocked_or_mismatched_subjects":0,
                    "matlab_objective_completed":completed,
                    "hgfx_objective_completed":completed,
                })
    trial.append({"model":"hgf_binary","trials":512,"masked":True,
        "diagnostic_classification":"BOTH_FAILED_FIRST_INVALID_PREFIX_AGREES_UNVERIFIED_MECHANISM"})
    fitting={"schema":"perf01-fit-comparison-v1",
        "status":"DIAGNOSTIC_ONLY_UNFROZEN_NO_PERFORMANCE",
        "rows":[{"n_trials":n,"classification":(
          "FULL_FIT_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES" if n==128 else
          "BLOCKED_UNSTABLE_DEFAULT_START_NONCOMPARABLE_RESTART_POLICY")}
          for n in (128,512,1024)]}
    cohort={"schema":"perf01-all-subject-paired-diagnostic-v1",
        "hgfx_source_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "matlab_oracle_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "input_manifest_sha256":"fixture-manifest-hash",
        "rows":rows,"strata":strata}
    return registry,{"schema":"hgfx-perf01-trialwise-comparison-v1",
                     "status":"EXPLORATORY_NOT_FROZEN_NOT_FINAL_SCIENTIFIC_GATE",
                     "rows":trial},fitting,cohort


class TestPerf01Eligibility(unittest.TestCase):
    def test_all_28_cases_counted_and_headline_denied(self):
        result=classify(*evidence())
        self.assertEqual(result["total_predeclared_cases"],28)
        self.assertEqual(result["primary_cases"],9)
        self.assertEqual(len(result["blocked_case_ids"]),12)
        self.assertEqual(result["classification_counts"],{
            "BLOCKED_INVALID_FROZEN_REFERENCE_WORKLOAD":8,
            "BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED":2,
            "BLOCKED_NONCOMPARABLE_FITTING_START_POLICY":2,
            "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING":16,
        })
        self.assertFalse(result["all_nine_primary_eligible"])
        self.assertIn("NOT_FROZEN",result["status"])

    def test_missing_case_fails_not_silent_exclusion(self):
        a,b,c,d=evidence()
        a["cases"].pop()
        with self.assertRaisesRegex(ValueError,"Original 28-case"):
            classify(a,b,c,d)

    def test_missing_subject_fails_not_silent_shrink(self):
        a,b,c,d=evidence()
        d["rows"].pop()
        with self.assertRaisesRegex(ValueError,"Incomplete diagnostic evidence"):
            classify(a,b,c,d)

    def test_wrong_source_sha_fails(self):
        a,b,c,d=evidence()
        d["matlab_oracle_sha"]="wrong"
        with self.assertRaisesRegex(ValueError,"Wrong frozen"):
            classify(a,b,c,d)

    def test_nonmatching_trialwise_case_blocks(self):
        a,b,c,d=evidence()
        b["rows"][0]["diagnostic_classification"]="TRIALWISE_MISMATCH"
        o=classify(a,b,c,d)
        primary128=next(x for x in o["cases"]
                     if x["tier"]=="primary" and x["trials"]==128 and x["stage"]=="forward")
        self.assertEqual(primary128["classification"],"BLOCKED_INCOMPLETE_SCIENTIFIC_EVIDENCE")
        self.assertFalse(o["all_nine_primary_eligible"])


if __name__=="__main__":
    unittest.main()
