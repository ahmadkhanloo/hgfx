"""Regression checks for PERF-01 reporting policy (no scientific or speedup claim)."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"))

from compare_trialwise import compare_numeric
from compare_fits import compare as compare_fitting, TOLS

BLOCKED = "BLOCKED_UNSTABLE_DEFAULT_START_MATLAB_RESAMPLES_HGFX_REJECTS"


class Perf01ComparisonTests(unittest.TestCase):
    def test_trialwise_nan_and_numeric_equality(self):
        result=compare_numeric([[None,0.1],["Infinity",-1.0]],
                               [[None,0.1],["Infinity",-1.0]])
        self.assertEqual(result["status"], "WITHIN_DIAGNOSTIC_TOLERANCE")
        self.assertEqual(result["mismatch_count"],0)

    def test_trialwise_first_mismatch_is_one_based_trial(self):
        result=compare_numeric([[0.1,0.2],[0.3,0.4]],[[0.1,0.2],[0.3,0.8]])
        self.assertEqual(result["status"],"MISMATCH")
        self.assertEqual(result["first_mismatch_index_zero_based"],[1,1])
        self.assertEqual(result["first_mismatch_trial_one_based"],2)

    def test_trialwise_shape_mismatch_never_passes(self):
        result=compare_numeric([[0.1,0.2]],[[0.1],[0.2]])
        self.assertEqual(result["status"],"SHAPE_MISMATCH")

    @staticmethod
    def fixture():
        optim={k:[0.0] for k in TOLS}
        optim["decompLME"]={"logjoint":0.0,"postpredcorr":0.0,"freepars":0.0}
        h={"hgfx_version":"1.0.0","cases":[
           {"n_trials":128,"status":"HGFX_FULL_FIT_COMPLETED_PARITY_NOT_ASSESSED",
            "optim":optim,"traj":{"mu":[[0.5,0.2]]},"n_rand_init":0},
           *({"n_trials":n,"status":BLOCKED} for n in (512,1024)),
        ]}
        m={"oracle_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
           "matlab_release":"2026a","cases":[
           {"n_trials":128,"status":"MATLAB_FULL_FIT_COMPLETED_PARITY_NOT_ASSESSED",
            "optim":{**optim},"traj":{"mu":[[0.5,0.2]]},"n_rand_init":0},
           *({"n_trials":n,"status":BLOCKED} for n in (512,1024)),
        ]}
        return h,m

    def test_fitting_mixed_eligibility_preserved(self):
        h,m=self.fixture()
        out=compare_fitting(h,m)
        self.assertEqual(len(out["rows"]),3)
        self.assertEqual(out["classification_counts"]["FULL_FIT_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"],1)
        self.assertEqual(out["classification_counts"]["BLOCKED_UNSTABLE_DEFAULT_START_NONCOMPARABLE_RESTART_POLICY"],2)

    def test_fitting_numerical_mismatch_cannot_pass(self):
        h,m=self.fixture()
        m["cases"][0]["optim"]={**m["cases"][0]["optim"],"final":[2.0]}
        out=compare_fitting(h,m)
        self.assertEqual(out["rows"][0]["classification"],"FULL_FIT_NUMERICAL_OR_WORKFLOW_MISMATCH")
        self.assertEqual(out["rows"][0]["fields"]["final"]["status"],"MISMATCH")

    def test_fitting_missing_horizon_raises(self):
        h,m=self.fixture()
        m["cases"].pop()
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            compare_fitting(h,m)

    def test_source_identity_is_required(self):
        h,m=self.fixture()
        h["hgfx_version"]="1.1.0b1"
        with self.assertRaisesRegex(ValueError,"Unexpected source identity"):
            compare_fitting(h,m)


if __name__=="__main__":
    unittest.main()
