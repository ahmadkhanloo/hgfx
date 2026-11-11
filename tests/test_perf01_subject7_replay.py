"""PERF-01 subject-7 cross-endpoint replay: preserve mismatches, no false PASS."""
from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_subject7_replay import classify, TRAJECTORY_FIELDS


def data():
    def row(origin, release):
        return {
            "endpoint_source":origin,
            "status":("HGFX_REPLAY_COMPLETED" if release=="hgfx" else "MATLAB_REPLAY_COMPLETED"),
            "transformed_final_vector":[0.0] if origin=="hgfx" else [1.0],
            "inf_states":[[[0.5]]],
            "trial_log_likelihoods":[-0.5],
            "yhat":[0.5],
            "residuals":[0.25],
            "traj":{key:[[0.0]] for key in TRAJECTORY_FIELDS},
        }
    base={"product_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
          "oracle_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
          "source_run_id":"41863441006",
          "subject_index_zero_based":7,"trials":128}
    h={**base,"schema":"perf01-subject7-hgfx-cross-replay-v1",
       "endpoint_max_abs_delta":1.0,
       "cases":[row("hgfx","hgfx"),row("matlab","hgfx")]}
    m={**base,"schema":"perf01-subject7-matlab-cross-replay-v1",
       "cases":[row("hgfx","matlab"),row("matlab","matlab")]}
    return h,m


class TestSubject7SameVectorDiagnostic(unittest.TestCase):
    def test_same_vector_both_endpoints_do_not_invent_scientific_pass(self):
        h,m=data()
        r=classify(h,m)
        self.assertEqual(r["classification"],
            "OPTIMIZER_ENDPOINT_SENSITIVITY_CANDIDATE_NOT_SCIENTIFIC_PASS")
        self.assertIn("NO_GATE_PROMOTION",r["status"])
        self.assertEqual(len(r["same_vector_cross_implementation"]),2)

    def test_injected_genuine_same_vector_inference_difference_fails(self):
        h,m=data()
        m["cases"][1]["traj"]["mu"]=[[0.01]]
        out=classify(h,m)
        self.assertEqual(out["classification"],
            "COMMON_VECTOR_INFERENCE_OR_OBSERVATION_MISMATCH")
        self.assertEqual(out["same_vector_cross_implementation"][1]["failed_fields"],
            ["traj.mu"])

    def test_parameter_vector_mismatch_is_not_parity(self):
        h,m=data()
        m["cases"][0]["transformed_final_vector"]=[5.0]
        result=classify(h,m)
        self.assertEqual(result["classification"],"UNRESOLVED_REPLAY_OR_SOURCE_MISMATCH")

    def test_missing_trajectory_field_refuses_diagnostics(self):
        h,m=data()
        del m["cases"][0]["traj"]["mu"]
        with self.assertRaisesRegex(ValueError,"trajectory schema"):
            classify(h,m)

    def test_missing_endpoint_is_fatal(self):
        h,m=data()
        m["cases"].pop()
        with self.assertRaisesRegex(ValueError,"Both exact"):
            classify(h,m)

    def test_hgfx_oracle_sha_mismatch_is_fatal(self):
        h,m=data()
        m["oracle_sha"]="not-the-oracle"
        with self.assertRaisesRegex(ValueError,"identity"):
            classify(h,m)


if __name__=="__main__":
    unittest.main()
