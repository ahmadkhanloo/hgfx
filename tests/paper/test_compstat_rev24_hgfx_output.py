"""REV-2.4 released-objective output JSON contracts; synthetic only."""
import json
from types import SimpleNamespace
import unittest

import numpy as np

from tools.compstat_rev24_hgfx_eval import evaluate_one


class Rev24HGFXOutputContract(unittest.TestCase):
    def mock_objective(self, *, valid=True):
        return SimpleNamespace(
            rval=0 if valid else -1,
            neg_log_likelihood=0.0 if valid else float("nan"),
            neg_log_joint=1.25 if valid else float("nan"),
            log_likelihood=0.0 if valid else float("nan"),
            trial_log_likelihoods=np.zeros(128, dtype=np.float64),
            perceptual_prior=SimpleNamespace(total=-0.5),
            observation_prior=SimpleNamespace(total=-0.75),
        )

    def row(self):
        return {
            "case_id": "REV24-G-hgf_binary-000",
            "case_sha256": "a" * 64,
            "full_transformed": [None, 0.5],
            "free_transformed": [0.5],
        }

    def group(self):
        return {"free_indices_zero_based": [1], "config_sha256": "b" * 64}

    def test_valid_objective_serializes_numpy_bool_as_json_bool(self):
        def stub(**kwargs):
            self.assertEqual(kwargs["model"], "hgf_binary")
            return self.mock_objective()
        result = evaluate_one(
            "hgf_binary", self.row(), self.group(),
            np.zeros(128), np.ones(128), stub,
        )
        self.assertIs(type(result["valid"]), bool)
        self.assertTrue(result["valid"])
        roundtrip = json.loads(json.dumps(result, allow_nan=False))
        self.assertIs(roundtrip["valid"], True)
        self.assertEqual(len(roundtrip["trial_log_likelihoods"]), 128)

    def test_failed_objective_is_kept_and_serializable(self):
        result = evaluate_one(
            "hgf_binary", self.row(), self.group(),
            np.zeros(128), np.ones(128),
            lambda **kwargs: self.mock_objective(valid=False),
        )
        self.assertIs(type(result["valid"]), bool)
        self.assertFalse(result["valid"])
        self.assertEqual(result["neg_log_joint"], "NaN")
        self.assertIs(json.loads(json.dumps(result, allow_nan=False))["valid"], False)

    def test_exception_remains_explicit_invalid_case(self):
        def broken(**kwargs):
            raise FloatingPointError("original unstable vector")
        result = evaluate_one(
            "hgf_binary", self.row(), self.group(),
            np.zeros(128), np.ones(128), broken,
        )
        self.assertEqual(result["error_type"], "FloatingPointError")
        self.assertIs(type(result["valid"]), bool)
        self.assertFalse(result["valid"])
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
