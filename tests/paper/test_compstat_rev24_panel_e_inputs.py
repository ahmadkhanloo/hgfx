"""REV-2.4 Panel E private-input builder: synthetic-only, no scientific objective."""
import copy
import json
import unittest

from tools.compstat_rev24_panel_e_inputs import (
    build_private_inputs, sanitized_audit, digest,
)


def synthetic_sources():
    d02 = {"cases": [{
        "id": "D02_fit", "model": "ehgf_binary",
        "observation": "unitsq_sgm", "seed": 123456789,
        "obs_prior_variance": 0.5,
        "inputs": [0] * 320, "responses": [1] * 320,
        "fit": {"final": {"shape": [1, 15], "data": [None] * 12 + [1., 2., 3.]},
                "prc_priorsas": {"shape": [1, 14], "data": [None] * 12 + [4., 4.]},
                "obs_priorsas": 0.5},
    }]}
    d08 = {"case_id": "D08_fit", "model": "uhgf",
           "observation": "gaussian_obs", "inputs": [1.] * 614,
           "responses": [0.] * 614, "final": [float(i) for i in range(11)],
           "prc_priorsas": [0.] * 10, "obs_priorsas": 0.1}
    comparison = {"endpoint_parameters": [
        {"index": i, "matlab": float(i), "hgfx": float(i) + .01}
        for i in range(11)
    ]}
    fixture = {"subject_indices_zero_based": list(range(64)),
               "subject_count": 64, "trial_count": 128,
               "u": [[0.] * 128 for _ in range(64)],
               "y": [[1.] * 128 for _ in range(64)]}
    def side():
        return {"model": "hgf_binary", "observation_model": "unitsq_sgm",
                "subjects": 64, "trials": 128,
                "cases": [{"subject_index_zero_based": idx,
                           "optim": {"final": [None] * 12 + [float(idx), -3., 3.]}}
                          for idx in range(64)]}
    hgfx = side()
    hgfx["input_sha256"] = "6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae"
    return d02, d08, comparison, hgfx, side(), fixture


class Rev24PanelEPrivateInputsContract(unittest.TestCase):
    def test_original_66_cases_and_missing_d02_endpoint_retained(self):
        doc = build_private_inputs(*synthetic_sources())
        self.assertEqual(doc["expected_cases"], 66)
        self.assertEqual([c["case_id"] for c in doc["cases"][:3]],
                         ["D02_fit", "D08_fit", "cohort64_subject_00"])
        self.assertEqual(doc["cases"][-1]["case_id"], "cohort64_subject_63")
        self.assertIsNone(doc["cases"][0]["endpoints"]["hgfx"])
        self.assertEqual(doc["cases"][0]["endpoint_status"]["hgfx"],
                         "INSUFFICIENT_REFERENCE_EVIDENCE")
        self.assertEqual(doc["cases"][1]["perceptual_model"], "uhgf")
        self.assertEqual(doc["cases"][1]["observation_model"], "gaussian_obs")
        self.assertEqual(doc["cases"][0]["obs_prior_variance"], 0.5)
        self.assertEqual(doc["cases"][1]["obs_prior_variance"], 0.1)
        self.assertEqual(doc["cases"][2]["trials"], 128)

    def test_sanitized_audit_does_not_leak_original_vectors(self):
        payload = build_private_inputs(*synthetic_sources())
        report = sanitized_audit(payload)
        self.assertEqual(report["original_cases"], 66)
        self.assertEqual(report["original_matlab_endpoints"], 66)
        self.assertEqual(report["original_hgfx_endpoints"], 65)
        self.assertEqual(report["insufficient_reference_evidence"], ["D02_fit"])
        self.assertEqual(report["objective_evaluations"], 0)
        self.assertEqual(report["science_gate"], "NOT_ASSESSED")
        raw = json.dumps(report)
        self.assertNotIn('"inputs"', raw)
        self.assertNotIn('"responses"', raw)
        self.assertNotIn('"endpoints"', raw)
        self.assertNotIn('"cases"', raw)
        self.assertNotIn('"optim"', raw)
        self.assertEqual(report["private_input_sha256"], digest(payload))

    def test_missing_original_cohort_endpoint_rejected(self):
        parts = list(synthetic_sources())
        parts[3]["cases"][7]["optim"]["final"].pop()
        with self.assertRaisesRegex(ValueError, "subject 7 HGFX"):
            build_private_inputs(*parts)

    def test_d08_wrong_family_and_inconsistent_endpoint_rejected(self):
        parts = list(synthetic_sources())
        parts[1]["model"] = "uhgf_binary"
        with self.assertRaisesRegex(ValueError, "D08 model"):
            build_private_inputs(*parts)
        parts = list(synthetic_sources())
        parts[2]["endpoint_parameters"][4]["matlab"] += 10.
        with self.assertRaisesRegex(ValueError, "D08 independent MATLAB"):
            build_private_inputs(*parts)

    def test_original_row_identity_and_full_denominator_required(self):
        parts = list(synthetic_sources())
        parts[4]["cases"][4]["subject_index_zero_based"] = 5
        with self.assertRaisesRegex(ValueError, "subject order"):
            build_private_inputs(*parts)
        parts = list(synthetic_sources())
        parts[5]["u"][8] = [0.] * 127
        with self.assertRaisesRegex(ValueError, "subject 8"):
            build_private_inputs(*parts)


if __name__ == "__main__":
    unittest.main()
