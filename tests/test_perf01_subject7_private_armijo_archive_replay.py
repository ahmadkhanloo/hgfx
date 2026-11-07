"""Source-independent synthetic checks for archived MATLAB private Armijo replay.

No scientific acceptance threshold, original source, or raw artifact is rewritten.
"""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
SCRIPT = HERE / "benchmarks" / "runtime_v1" / "replay_subject7_private_armijo_archive.py"
SRC_FIXTURE = HERE / "tests" / "test_perf01_subject7_private_candidate_armijo.py"


def module_from(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


replay = module_from(SCRIPT, "perf01_armijo_replay")
fixture = module_from(SRC_FIXTURE, "perf01_armijo_fixture")


def mock_inputs():
    source = fixture.source()
    source["source_original_record6_value"] = 108.28848680066957
    for key in replay.GRADIENT_KEYS:
        source["same_T6_and_x6_one_step_directions"][key][
            "original_source_unclipped_gradient_dot_direction"] = -5.
    raw = fixture.report(source)
    raw["github_run_id"] = replay.ORIGINAL_RUN
    raw["tested_sha"] = replay.ORIGINAL_SHA
    derived = {
        "matlab_raw_sha256": replay.MATLAB_RAW_SHA,
        "raw_candidate_sha256": replay.SOURCE_CANDIDATE_SHA,
        "status": "AUTHOR_SIDE_THREE_PRIVATE_OBJECTIVE_CALLS_ONLY",
        "original_science": "63/64 SCIENTIFIC NONPASS",
        "review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "original_candidates": [{
            "name": r["name"], "status": r["status"],
            "matlab_private_value": r["private_objective"],
            "private_armijo": r.get("private_armijo_full_step"),
        } for r in raw["calls"]],
    }
    provenance = {
        "run_id": replay.ORIGINAL_RUN,
        "tested_candidate_commit": replay.ORIGINAL_SHA,
        "protocol_commit": replay.ORIGINAL_PROTOCOL,
        "original_public_fit": "63/64 SCIENTIFIC NONPASS",
        "independent_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "performance_timing": "NOT_RUN",
        "sha256": {
            "private-matlab-three-candidate-objectives.json": replay.MATLAB_RAW_SHA,
            "derived-private-matlab-armijo-summary.json": replay.ORIGINAL_DERIVED_SHA,
        },
    }
    cases = [{} for _ in range(8)]
    cases[7] = {
        "mismatched_fields": ["traj.mu", "traj.muhat"],
        "fields": {"traj.mu": {"mismatch_count": 4},
                   "traj.muhat": {"mismatch_count": 4}},
    }
    original = {
        "subject_count": 64,
        "classification_counts": {
            "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
            "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1,
        },
        "cases": cases,
    }
    return source, raw, derived, provenance, original


class ArchiveReplayTests(unittest.TestCase):
    def test_complete_three_case_replay_not_a_scientific_pass(self):
        x = replay.replay(*mock_inputs())
        self.assertEqual(x["status"], "AUTHOR_SIDE_SHA_LOCKED_ARCHIVE_ARITHMETIC_REPLAY_ONLY")
        self.assertEqual(x["original_scientific_fitting"], "63/64 SCIENTIFIC NONPASS")
        self.assertEqual(len(x["candidate_arithmetic"]), 2)
        self.assertEqual([r["source_formula_full_step_armijo"] for r in x["candidate_arithmetic"]],
                         [True, True])

    def test_reject_original_scientific_failure_mutation(self):
        data = mock_inputs()
        data[-1]["cases"][7]["fields"]["traj.muhat"]["mismatch_count"] = 0
        with self.assertRaisesRegex(ValueError, "63/64"):
            replay.replay(*data)

    def test_reject_new_raw_report_other_commit(self):
        data = mock_inputs()
        data[1]["tested_sha"] = "other"
        with self.assertRaisesRegex(ValueError, "experiment identity"):
            replay.replay(*data)

    def test_reject_private_armijo_decision_flip(self):
        data = mock_inputs()
        data[1]["calls"][1]["private_armijo_full_step"] = False
        with self.assertRaisesRegex(ValueError, "Armijo"):
            replay.replay(*data)

    def test_reject_missing_original_candidate(self):
        data = mock_inputs()
        data[1]["calls"].pop()
        with self.assertRaisesRegex(ValueError, "Three complete"):
            replay.replay(*data)

    def test_reject_mutated_source_full_step_slope(self):
        data = mock_inputs()
        data[0]["same_T6_and_x6_one_step_directions"][replay.GRADIENT_KEYS[1]][
            "original_source_unclipped_gradient_dot_direction"] = -6.
        with self.assertRaisesRegex(ValueError, "slope/RHS"):
            replay.replay(*data)

    def test_reject_tampered_original_matlab_objective(self):
        data = mock_inputs()
        data[1]["calls"][2]["private_objective"] = 105.
        with self.assertRaisesRegex(ValueError, "Armijo"):
            replay.replay(*data)

    def test_reject_author_side_derived_report_conflict(self):
        data = mock_inputs()
        data[2]["original_candidates"][2]["private_armijo"] = False
        with self.assertRaisesRegex(ValueError, "derived"):
            replay.replay(*data)

    def test_reject_independent_review_fabrication(self):
        data = mock_inputs()
        data[3]["independent_review"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "provenance"):
            replay.replay(*data)

    def test_sha_read_refuses_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "fake-source.json"
            file.write_text("{}")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                replay.sha_read(file, replay.MATLAB_RAW_SHA)


if __name__ == "__main__":
    unittest.main()
