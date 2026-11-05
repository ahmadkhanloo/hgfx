"""PERF-01D optimizer trace must not mistake preallocation for iterations."""
from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_optimizer_trace_subject7 import compare


def payload(label: str, count: int = 3, shift: float = 0.0):
    xs = [[None, None, None] for _ in range(101)]
    vals = [None] * 101
    for i in range(count):
        xs[i] = [float(i) + (shift if i >= 2 else 0), 0., 0.]
        vals[i] = float(99 - i)
    return {
        "schema": f"perf01-subject7-optimizer-trace-{label}-v1",
        "status": "FULL_PUBLIC_FIT_TRACE_EXPORTED",
        "subject_index_zero_based": 7,
        "trials": 128,
        "model": "hgf_binary",
        "source_run_id": "41863441006",
        "frozen_hgfx_sha": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "frozen_matlab_sha": "2437f4dc241541072722a2695ddeca7b44d83dd3",
        "original_raw_fits_verified": True,
        "frozen_start_matches": True,
        "n_rand_init": 0,
        "source_config_sha256": "same_frozen_config",
        "source_input_sha256": "same_frozen_input",
        "iter_x": xs,
        "iter_val": vals,
        "final_full": [None]*12 + [1., 2., 3.],
        "original_final_full": [None]*12 + [1., 2., 3.],
        "fit_neg_lj": 97.0,
    }


class TestOptimizerPathPreallocation(unittest.TestCase):
    def test_101_allocated_does_not_imply_100_completed_iterations(self):
        o = compare(payload("hgfx"), payload("matlab"))
        self.assertEqual(o["allocated_slots_per_implementation"], 101)
        self.assertEqual(o["recorded_finite_slots"], {"hgfx": 3, "matlab": 3})
        self.assertIsNone(o["first_different_record"])
        self.assertEqual(o["termination_reason"]["matlab"],
                         "NOT_EXPOSED_BY_UNMODIFIED_PUBLIC_FITMODEL")
        self.assertIn("NOT_PROMOTED", o["classification"])

    def test_earliest_numerical_path_difference_is_reported_not_hidden(self):
        o = compare(payload("hgfx", shift=1e-2), payload("matlab"))
        self.assertEqual(o["first_different_record"]["record_index_zero_based"], 2)
        self.assertEqual(o["all_different_record_count"], 1)

    def test_different_recorded_finite_counts_reported_not_assumed_iterations(self):
        o = compare(payload("hgfx", count=2), payload("matlab", count=3))
        self.assertEqual(o["slot_mismatch_count"], 1)
        self.assertEqual(o["shared_finite_slot_count"], 2)

    def test_missing_middle_row_fails_closed(self):
        a, b = payload("hgfx"), payload("matlab")
        a["iter_x"][1] = [None, None, None]
        a["iter_val"][1] = None
        with self.assertRaisesRegex(ValueError, "noncontiguous"):
            compare(a, b)

    def test_preallocated_array_shape_change_fails(self):
        a,b = payload("hgfx"),payload("matlab")
        a["iter_val"].pop()
        with self.assertRaisesRegex(ValueError, "101"):
            compare(a,b)

    def test_x_val_validity_disagreement_is_a_failure(self):
        a,b=payload("hgfx"),payload("matlab")
        a["iter_val"][1]=None
        with self.assertRaisesRegex(ValueError, "finite masks"):
            compare(a,b)

    def test_wrong_frozen_product_fails(self):
        a,b=payload("hgfx"),payload("matlab")
        b["frozen_matlab_sha"]="changed"
        with self.assertRaisesRegex(ValueError, "source/fit identity"):
            compare(a,b)

    def test_different_config_source_fails(self):
        a,b=payload("hgfx"),payload("matlab")
        b["source_input_sha256"]="different"
        with self.assertRaisesRegex(ValueError, "provenance"):
            compare(a,b)

    def test_numeric_termination_reason_never_inferred(self):
        a,b=payload("hgfx"),payload("matlab")
        o=compare(a,b)
        self.assertNotIn("PASS",o["classification"])
        self.assertIn("NOT_INFERRED",o["termination_reason"]["hgfx"])


if __name__ == "__main__":
    unittest.main()
