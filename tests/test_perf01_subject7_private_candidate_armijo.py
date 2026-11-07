"""Fail-closed synthetic guards for a real-source, post-result MATLAB Armijo probe."""
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"
s = importlib.util.spec_from_file_location("subject7_private_candidate_armijo",
                                           ROOT / "subject7_private_candidate_armijo.py")
probe = importlib.util.module_from_spec(s)
s.loader.exec_module(probe)


def source():
    d = {
        "schema": "perf01d-postresult-source-one-step-original-record6-v1",
        "source_original_frozen_hgfx": probe.HGFX,
        "source_original_frozen_matlab": probe.MATLAB,
        "source_original_64_public_fit_science": "63/64 SCIENTIFIC NONPASS",
        "source_original_zero_based_subject7_4_plus_4_mismatches": {"traj.mu": 4, "traj.muhat": 4},
        "source_original_bfgs_run": "42187240378",
        "source_50_actual_private_probe_run": "42305573614",
        "source_50_raw_sha256": {
            "paired-direct-private-gradient-bfgs-margins.json": probe.SOURCE_GRADIENT_SHA
        },
        "original_history_record_zero_based": 6,
        "subject_index_zero_based": 7,
        "original_trial_count": 128,
        "one_identical_x": list(probe.X6),
        "post_result_selection": True,
        "selection_already_preliminarily_calculated_before_script_commit": True,
        "one_step_is_NOT_a_completed_fitting_result": True,
        "one_step_is_NOT_an_unmodified_original_MATLAB_optimizer_branch_log": True,
        "same_source_hgfx_objective_used_for_two_counterfactual_one_step_candidates": True,
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "timing": "NOT_RUN",
    }
    d["same_T6_and_x6_one_step_directions"] = {
        k: {
            "source_next_full_step_free_x": [1., 2., 3.] if i == 0 else [4., 5., 6.],
            "original_source_clipping_applied": True,
            "original_armijo_delta_RHS_using_unclipped_slope": -.0005,
            "source_current_value": 108.28848680066957,
            "new_evaluated_hgfx_objective_at_candidate": 105.8 + i*.1,
        }
        for i, k in enumerate(probe.SOURCE_KEYS)
    }
    return d


def report(candidate):
    return {
        "schema": "perf01d-actual-private-matlab-candidate-armijo-v1",
        "source_original_candidate_sha256": probe.CANDIDATE_SHA,
        "frozen_hgfx_sha": probe.HGFX,
        "frozen_matlab_sha": probe.MATLAB,
        "original_science": "63/64 SCIENTIFIC NONPASS",
        "hook_count": 1,
        "original_optimizer_delegated": True,
        "native_instrumented_stable_fields_identical": True,
        "compared_stable_field_count": 26,
        "calls": [{
            "name": "original_hgfx_source_x6",
            "free_x": list(probe.X6),
            "status": "EVALUATED_FINITE",
            "private_objective": 108.28848680066957,
        }] + [
            {"name": k,
             "free_x": candidate["same_T6_and_x6_one_step_directions"][k]["source_next_full_step_free_x"],
             "status": "EVALUATED_FINITE",
             "private_objective": 105.8 + i*.1,
             "previous_hgfx_objective_at_candidate": 105.8 + i*.1,
             "original_armijo_delta_rhs": -.0005,
             "private_armijo_delta_lhs": (105.8 + i*.1) - 108.28848680066957,
             "private_armijo_full_step": True}
            for i, k in enumerate(probe.SOURCE_KEYS)
        ],
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "timing": "NOT_RUN",
    }


class SourceGuardTests(unittest.TestCase):
    def test_valid_complete_original_source(self):
        self.assertIs(probe.validate_candidate(source()) is not None, True)

    def test_original_scientific_failure_is_mandatory(self):
        d = source()
        d["source_original_zero_based_subject7_4_plus_4_mismatches"]["traj.mu"] = 0
        with self.assertRaisesRegex(ValueError, "failed evidence"):
            probe.validate_candidate(d)

    def test_same_state_x6_is_not_matlab_own_x6(self):
        d = source()
        d["one_identical_x"][0] += 1e-6
        with self.assertRaisesRegex(ValueError, "chosen x6"):
            probe.validate_candidate(d)

    def test_both_counterfactuals_required_without_selection(self):
        d = source()
        del d["same_T6_and_x6_one_step_directions"][probe.SOURCE_KEYS[1]]
        with self.assertRaisesRegex(ValueError, "two source candidates"):
            probe.validate_candidate(d)

    def test_original_unclipped_armijo_slope_mandatory(self):
        d = source()
        d["same_T6_and_x6_one_step_directions"][probe.SOURCE_KEYS[0]][
            "original_armijo_delta_RHS_using_unclipped_slope"] = float("nan")
        with self.assertRaisesRegex(ValueError, "clipping/slope"):
            probe.validate_candidate(d)

    def test_private_candidate_observation_valid_not_a_fit_pass(self):
        d = source()
        output = probe.validate_result(d, report(d))
        self.assertEqual(output["original_science"], "63/64 SCIENTIFIC NONPASS")
        self.assertEqual(output["perf01c"], "NOT_FROZEN")

    def test_reject_changed_private_armijo_boolean(self):
        d = source()
        v = report(d)
        v["calls"][1]["private_armijo_full_step"] = False
        with self.assertRaisesRegex(ValueError, "Armijo decision"):
            probe.validate_result(d, v)

    def test_reject_non_neutral_matlab_callback(self):
        d = source()
        v = report(d)
        v["native_instrumented_stable_fields_identical"] = False
        with self.assertRaisesRegex(ValueError, "neutrality"):
            probe.validate_result(d, v)

    def test_preserve_unmeasured_numeric_sentinel_without_false_pass(self):
        d = source()
        v = report(d)
        v["calls"][2]["status"] = "REALMAX_SENTINEL"
        v["calls"][2]["private_objective"] = 1.7976931348623157e308
        v["calls"][2].pop("private_armijo_delta_lhs")
        v["calls"][2].pop("private_armijo_full_step")
        got = probe.validate_result(d, v)
        self.assertIsNone(got["original_candidates"][2]["private_armijo"])


if __name__ == "__main__":
    unittest.main()
