"""Fail-closed synthetic tests for prospective direct MATLAB nested-gradient/BFGS audit.

No synthetic result here is treated as scientific parity or real-MATLAB evidence.
"""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np

BASE = Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"
sys.path.insert(0, str(BASE))
spec = importlib.util.spec_from_file_location(
    "direct_nested_bfgs", BASE / "subject7_direct_nested_gradient_bfgs.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def synthetic_trace():
    xs = np.full((101, 3), np.nan)
    xs[:25] = np.array([[float(i) / 100., float(i) / 200., 0.] for i in range(25)])
    t = np.repeat(np.eye(3)[None, :, :], 23, axis=0)
    rows = [{
        "anchor_origin": "hgfx",
        "record_index_zero_based": i,
        "hgfx": {"objective": float(100 - i), "gradient": [0.1, 0.2, -0.1]},
        "matlab": {"objective": float(100 - i), "gradient": [0.1, 0.2, -0.1]},
    } for i in range(25)]
    return {"iter_x": xs.tolist(), "iter_inverse_hessian": t.tolist()}, rows


class DirectNestedGradientTests(unittest.TestCase):
    def test_01_ulp_exact(self):
        x = 45.
        self.assertEqual(audit.ulp_distance(x, x), 0)
        self.assertEqual(audit.ulp_distance(x, np.nextafter(x, np.inf)), 1)

    def test_02_two_ulp(self):
        x = np.nextafter(45., np.inf)
        self.assertEqual(audit.ulp_distance(45., np.nextafter(x, np.inf)), 2)

    def test_03_negative_values(self):
        x = -2.
        self.assertEqual(audit.ulp_distance(x, np.nextafter(x, -np.inf)), 1)

    def test_04_ulp_nan_rejected(self):
        with self.assertRaises(ValueError):
            audit.ulp_distance(float("nan"), 1.)

    def test_05_gradstop_below(self):
        m = audit.stop_margin(np.ones(3), [0.0001, 0., 0.], 1.)
        self.assertTrue(m["condition_converges_if_tested"])
        self.assertGreater(m["signed_margin_tol_minus_score"], 0.)

    def test_06_gradstop_above(self):
        m = audit.stop_margin(np.ones(3), [0.002, 0., 0.], 1.)
        self.assertFalse(m["condition_converges_if_tested"])
        self.assertLess(m["signed_margin_tol_minus_score"], 0.)

    def test_07_gradstop_exact_boundary(self):
        m = audit.stop_margin(np.ones(3), [0.001, 0., 0.], 1.)
        self.assertFalse(m["condition_converges_if_tested"])
        self.assertEqual(m["signed_margin_tol_minus_score"], 0.)

    def test_08_gradstop_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            audit.stop_margin(np.ones(3), [float("nan"), 0., 0.], 1.)

    def test_09_all_decision_denominators(self):
        raw, rows = synthetic_trace()
        r = audit.bfgs_margins(raw, rows, "hgfx")
        self.assertEqual(len(r["gradient_stop_descriptive_all_25"]), 25)
        self.assertEqual(len(r["curvature_safe_original_slots_1_to_22"]), 22)
        self.assertEqual(len(r["line_search_safe_original_transitions_0_to_21"]), 22)
        self.assertEqual(r["terminal_ambiguous_transition_indices_excluded"], [22, 23])

    def test_10_no_silent_missing_gradient(self):
        raw, rows = synthetic_trace()
        rows[14]["hgfx"]["gradient"] = [float("nan"), 0., 0.]
        with self.assertRaises(ValueError):
            audit.bfgs_margins(raw, rows, "hgfx")

    def test_11_no_silent_dropped_history(self):
        raw, rows = synthetic_trace()
        with self.assertRaises(ValueError):
            audit.bfgs_margins(raw, rows[:-1], "hgfx")

    def test_12_no_silent_matrix_truncation(self):
        raw, rows = synthetic_trace()
        raw["iter_inverse_hessian"] = raw["iter_inverse_hessian"][:22]
        with self.assertRaises(ValueError):
            audit.bfgs_margins(raw, rows, "hgfx")

    def test_13_curvature_zero_branch(self):
        raw, rows = synthetic_trace()
        r = audit.bfgs_margins(raw, rows, "hgfx")
        self.assertFalse(r["curvature_safe_original_slots_1_to_22"][0]["reconstructed_update_condition"])

    def test_14_nonfinite_value_rejected(self):
        raw, rows = synthetic_trace()
        rows[2]["hgfx"]["objective"] = float("inf")
        with self.assertRaises(ValueError):
            audit.bfgs_margins(raw, rows, "hgfx")

    def test_15_immutable_source_hash_key_inventory(self):
        self.assertEqual(set(audit.HASHES), {"matlab_raw.json", "hgfx_raw.json"})
        self.assertEqual(len(audit.HASHES["matlab_raw.json"]), 64)
        self.assertEqual(len(audit.HASHES["hgfx_raw.json"]), 64)

    def test_16_unchanged_scientific_identity(self):
        self.assertEqual(audit.RUN, "42187240378")
        self.assertEqual(audit.START, [-3., -6., 3.871201010907891])
        self.assertEqual(audit.ORIG, ("hgfx", "matlab"))


if __name__ == "__main__":
    unittest.main()
