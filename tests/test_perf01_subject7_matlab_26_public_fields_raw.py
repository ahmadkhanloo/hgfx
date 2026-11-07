"""Synthetic MAT-v7 raw 26-field archive checks; not independent scientific approval."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
from scipy.io import savemat

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks" / "runtime_v1" / "replay_subject7_matlab_26_public_fields.py"
spec = importlib.util.spec_from_file_location("perf01d_public_fields_replay", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def original_fit():
    cases = [{} for _ in range(8)]
    cases[7] = {"mismatched_fields": ["traj.mu", "traj.muhat"],
                "fields": {"traj.mu": {"mismatch_count": 4},
                           "traj.muhat": {"mismatch_count": 4}}}
    return {"subject_count": 64,
            "classification_counts": {
                "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
                "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1},
            "cases": cases}


def raw_fixtures():
    optim = {f: np.array([[float(i)]]) for i, f in enumerate(audit.OPT)}
    optim["init"] = {"theta": np.array([[1.0, float("nan")]]),
                     "nested": {"a": np.array([[3., 4.]])}}
    optim["trialLogLlsplit"] = np.array([[np.array([[1., float("nan")]])]], dtype=object)
    traj = {f"record_{i}": np.array([[float(i), float("nan")]]) for i in range(11)}
    public = {"optim": optim, "traj": traj}
    metadata = {
        "schema": audit.SCHEMA,
        "frozen_hgfx_sha": audit.HGFX_SHA,
        "frozen_matlab_sha": audit.MATLAB_SHA,
        "original_source_candidate_sha256": audit.CANDIDATE_SHA,
        "original_64_public_science": "63/64 SCIENTIFIC NONPASS",
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "performance_timing": "NOT_RUN",
        "subject_index_zero_based": 7,
        "original_trial_count": 128,
        "field_count": 26,
        "hook_count": 1,
        "original_optimizer_delegated": True,
        "native_instrumented_26_field_equality_producer": True,
        "github_run_id": "12345678",
        "tested_sha": "f" * 40,
        "matlab_version": "R2026a",
        "optim_fields": np.array(audit.OPT, dtype=object),
        "traj_fields": np.array(list(traj), dtype=object),
    }
    private = {
        "tested_sha": "f" * 40,
        "github_run_id": "12345678",
        "frozen_hgfx_sha": audit.HGFX_SHA,
        "frozen_matlab_sha": audit.MATLAB_SHA,
        "source_original_candidate_sha256": audit.CANDIDATE_SHA,
        "original_science": "63/64 SCIENTIFIC NONPASS",
        "hook_count": 1,
        "original_optimizer_delegated": True,
        "compared_stable_field_count": 26,
        "native_instrumented_stable_fields_identical": True,
        "calls": [{"private_objective": 108.28848680066957}],
    }
    return public, metadata, private, original_fit()


def prepare(*, mutate=None):
    native, metadata, private, original = raw_fixtures()
    intercepted = copy.deepcopy(native)
    if mutate:
        mutate(intercepted, metadata, private, original)
    with tempfile.TemporaryDirectory() as folder:
        file = Path(folder) / "public.mat"
        savemat(file, {"native_public": native, "instrumented_public": intercepted,
                       "metadata": metadata}, do_compression=False)
        a, b, c, digest = audit.read_public(file)
        return audit.replay(a, b, c, private, original, digest)


class TwentySixRawFieldTests(unittest.TestCase):
    def test_full_15_plus_11_nested_and_nan_match(self):
        output = prepare()
        self.assertTrue(output["native_and_instrumented_fieldwise_exact"])
        self.assertEqual(len(output["field_results"]), 26)
        self.assertTrue(all(x["equal_nan_exact"] for x in output["field_results"]))
        self.assertEqual(output["original_scientific_fitting"], "63/64 SCIENTIFIC NONPASS")

    def test_deep_nan_location_nonmatch_not_hidden(self):
        out = prepare(mutate=lambda other, m, p, o: other["optim"]["init"]["theta"].__setitem__((0, 1), 1.5))
        self.assertFalse(out["native_and_instrumented_fieldwise_exact"])
        self.assertTrue(any(x["field"] == "optim.init" and not x["equal_nan_exact"]
                            for x in out["field_results"]))

    def test_different_shape_detected(self):
        out = prepare(mutate=lambda other, m, p, o: other["traj"].__setitem__("record_3", np.array([[3.]])))
        self.assertFalse(out["native_and_instrumented_fieldwise_exact"])

    def test_added_nested_struct_field_detected(self):
        out = prepare(mutate=lambda other, m, p, o: other["optim"]["init"]["nested"].__setitem__(
            "extra", np.array([[99.]])))
        self.assertFalse(out["native_and_instrumented_fieldwise_exact"])

    def test_removed_top_level_field_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "omitted or added"):
            prepare(mutate=lambda other, m, p, o: other["optim"].pop("res"))

    def test_mutated_original_63_of_64_denominator_fails(self):
        with self.assertRaisesRegex(ValueError, "63/64"):
            prepare(mutate=lambda other, m, p, original: original["cases"][7]["fields"]["traj.mu"].__setitem__(
                "mismatch_count", 0))

    def test_mutated_frozen_matlab_sha_fails(self):
        with self.assertRaisesRegex(ValueError, "metadata changed"):
            prepare(mutate=lambda other, m, p, o: m.__setitem__("frozen_matlab_sha", "unexpected"))

    def test_modified_private_run_sha_fails(self):
        with self.assertRaisesRegex(ValueError, "private MATLAB report"):
            prepare(mutate=lambda other, m, p, o: p.__setitem__("tested_sha", "f" * 39 + "e"))

    def test_mismatched_field_selection_fails(self):
        with self.assertRaisesRegex(ValueError, "selection changed"):
            prepare(mutate=lambda other, m, p, o: m.__setitem__(
                "optim_fields", np.array(list(audit.OPT[:-1]) + ["foo"], dtype=object)))

    def test_mismatched_producer_flag_fails(self):
        with self.assertRaisesRegex(ValueError, "producer neutrality"):
            prepare(mutate=lambda other, m, p, o: m.__setitem__(
                "native_instrumented_26_field_equality_producer", False))


if __name__ == "__main__":
    unittest.main()
