"""Prevent PERF-01 64-subject fitting regressions and false scientific eligibility."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_fit_cohort import compare
from compare_fits import TOLS


def fixtures():
    optim={name:[0.0] for name in TOLS}
    optim["decompLME"]={"logjoint":0.0,"postpredcorr":0.0,"freepars":0.0}
    hrows=[]
    mrows=[]
    for i in range(64):
        common={
            "model":"hgf_binary","n_trials":128,
            "subject_index_zero_based":i,
            "start_matches_frozen_snapshot":True,
            "n_rand_init":0,
            "optimizer_iteration_count":6,
            "optim":dict(optim),
            "traj":{"mu":[[0.0,1.0]],"sa":[[1.0,2.0]]},
        }
        hrows.append({**common,"status":"HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION"})
        mrows.append({**common,"status":"MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION"})
    hgfx={
        "schema":"perf01-hgfx-full-cohort-fit-v1",
        "hgfx_distribution":"1.0.0",
        "release_expected_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "input_sha256":"inputhash","config_sha256":"confighash",
        "cases":hrows,
    }
    matlab={
        "schema":"perf01-matlab-full-cohort-fit-v1",
        "oracle_expected_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "matlab_release":"2026a",
        "cases":mrows,
    }
    return hgfx,matlab


class TestPerf01FullCohortFits(unittest.TestCase):
    def test_all_subjects_and_prefixes_are_retained(self):
        a,b=fixtures()
        out=compare(a,b)
        self.assertEqual(out["subject_count"],64)
        self.assertEqual(len(out["cases"]),64)
        self.assertEqual(out["classification_counts"],{
            "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":64,
        })
        self.assertEqual([x["subject_count"] for x in out["by_prefix"]],[1,16,64])
        self.assertEqual([x["numerical_output_concordant"] for x in out["by_prefix"]],[1,16,64])
        self.assertEqual(out["status"],"UNFROZEN_DIAGNOSTIC_NO_TIMING_NO_SCIENTIFIC_PASS")

    def test_one_different_fit_parameter_preserved(self):
        a,b=fixtures()
        b["cases"][17]["optim"]["final"]=[1.0]
        out=compare(a,b)
        self.assertEqual(out["classification_counts"]["FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"],1)
        self.assertEqual(out["classification_counts"]["FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"],63)
        self.assertIn("final",out["cases"][17]["mismatched_fields"])

    def test_both_fits_failed_not_scientifically_pass(self):
        a,b=fixtures()
        a["cases"][0].update(status="HGFX_FULL_FIT_ERROR",error="optimizer unstable")
        b["cases"][0].update(status="MATLAB_FULL_FIT_ERROR",
                             error_identifier="tapas:hgf:StartpointUnstableRegionOfPriors")
        out=compare(a,b)
        self.assertEqual(out["classification_counts"]["BOTH_FITS_FAILED_MECHANISM_UNVERIFIED"],1)
        self.assertEqual(out["by_prefix"][0]["failed_or_noncomparable"],1)

    def test_implicit_restart_or_start_change_is_blocked(self):
        a,b=fixtures()
        b["cases"][3].update(status="MATLAB_UNEXPECTED_RESTART_OR_START",
                             start_matches_frozen_snapshot=False)
        out=compare(a,b)
        self.assertEqual(out["cases"][3]["classification"],"BLOCKED_START_POLICY_NOT_MATCHED")

    def test_iteration_path_mismatch_is_recorded(self):
        a,b=fixtures()
        b["cases"][2]["optimizer_iteration_count"]=7
        out=compare(a,b)
        self.assertFalse(out["cases"][2]["iteration_count_equal"])
        self.assertEqual(out["cases"][2]["optimization_path_caveat"],"ITERATION_COUNT_DIFFERS")

    def test_missing_and_duplicate_subjects_fail_closed(self):
        a,b=fixtures()
        a["cases"].pop()
        with self.assertRaisesRegex(ValueError,"subjects missing"):
            compare(a,b)
        a,b=fixtures()
        a["cases"][3]=a["cases"][2]
        with self.assertRaisesRegex(ValueError,"without duplicates"):
            compare(a,b)

    def test_wrong_oracle_sha_fails_closed(self):
        a,b=fixtures()
        b["oracle_expected_sha"]="not-the-reference"
        with self.assertRaisesRegex(ValueError,"Unverified"):
            compare(a,b)


if __name__=="__main__":
    unittest.main()
