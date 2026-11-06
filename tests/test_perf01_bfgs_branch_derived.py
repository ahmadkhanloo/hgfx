"""PERF-01D immutable derived curvature audit: structural negative controls."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from derive_subject7_bfgs_branch import (
    SAFE_BFGS_SLOTS, SAFE_STEP_SLOTS, curvature_decisions,
)


def dummy():
    x=[[-3.+i,-6.,3.871201010907891] for i in range(25)]
    x.extend([[None,None,None] for _ in range(76)])
    gradient=[{"grad":[-1.,0.,0.]} for _ in range(25)]
    inv=np.eye(3).tolist()
    return {"iter_x":x,
            "ridders_recomputed_history":gradient,
            "iter_inverse_hessian":[[row[:] for row in inv] for _ in range(24)]}


class TestImmutableBFGSCurvature(unittest.TestCase):
    def test_fixed_safe_branch_denominators(self):
        self.assertEqual(SAFE_BFGS_SLOTS,tuple(range(1,23)))
        self.assertEqual(SAFE_STEP_SLOTS,tuple(range(22)))
        self.assertNotIn(23,SAFE_BFGS_SLOTS)
        self.assertNotIn(22,SAFE_STEP_SLOTS)

    def test_equal_gradient_no_bfgs_branch_and_no_matrix_change(self):
        r=curvature_decisions(dummy())
        self.assertEqual(len(r),22)
        self.assertTrue(all(not x["source_condition_would_apply_update"] for x in r))
        self.assertTrue(all(x["condition_vs_saved_matrix_change_agree"] for x in r))

    def test_synthetic_hidden_bfgs_matrix_change_is_detected(self):
        d=dummy()
        d["iter_inverse_hessian"][4][0][0]+=0.5
        rows=curvature_decisions(d)
        disagree=[r["record_index_zero_based"] for r in rows
                  if not r["condition_vs_saved_matrix_change_agree"]]
        self.assertEqual(disagree,[4,5])

    def test_missing_ridders_slot_must_fail(self):
        d=dummy()
        d["ridders_recomputed_history"].pop()
        with self.assertRaisesRegex(ValueError,"dimensions"):
            curvature_decisions(d)

    def test_missing_matrix_history_must_fail(self):
        d=dummy()
        d["iter_inverse_hessian"]=d["iter_inverse_hessian"][:22]
        with self.assertRaisesRegex(ValueError,"dimensions"):
            curvature_decisions(d)

    def test_nonfinite_gradient_must_fail(self):
        d=dummy()
        d["ridders_recomputed_history"][2]["grad"][1]=None
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            curvature_decisions(d)

    def test_negative_curvature_has_no_update(self):
        d=dummy()
        d["ridders_recomputed_history"][1]["grad"]=[-3.,0.,0.]
        row=curvature_decisions(d)[0]
        self.assertLess(row["curvature_scalar_dgrad_dot_dx"],0)
        self.assertFalse(row["source_condition_would_apply_update"])

    def test_zero_curvature_threshold_does_not_imply_update(self):
        row=curvature_decisions(dummy())[0]
        self.assertEqual(row["curvature_source_threshold"],0)
        self.assertFalse(row["source_condition_would_apply_update"])


if __name__=="__main__":
    unittest.main()
