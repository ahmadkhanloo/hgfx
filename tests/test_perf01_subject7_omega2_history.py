"""Exact original omega2 signed path review, negative controls and no-gate status."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from derive_subject7_omega2_history import EXPECTED,first,pointwise_drift
from compare_fits import TOLS


class TestFrozenOmega2History(unittest.TestCase):
    def test_scientific_status_never_auto_pass(self):
        self.assertEqual(EXPECTED,
            "AUTHOR_SIDE_ORIGINAL_OMEGA2_25_HISTORY_NOT_CAUSAL_OR_SCIENTIFIC_PASS")
        self.assertEqual(TOLS["final"],(3e-8,3e-10))

    def test_original_three_free_coords_equal_start(self):
        x=np.array([[-3.,-6.,3.871201010907891]]*25)
        out=pointwise_drift(x,x,*TOLS["final"])
        self.assertEqual(len(out),25)
        self.assertFalse(any(v["omega2_abs_diff"] for v in out))
        self.assertFalse(any(v["omega2_outside_final_tolerance_descriptive_not_optimizer_iter_gate"]
                             for v in out))

    def test_sub_tol_omega2_and_super_tol_omega3_are_separate(self):
        h=np.array([[-3.,-6.,3.87],[-3.+1e-9,-6.+1e-6,3.87]])
        m=np.array([[-3.,-6.,3.87]]*2)
        out=pointwise_drift(h,m,3e-8,3e-10)
        self.assertEqual(out[1]["omega2_signed_diff"],h[1,0]-m[1,0])
        self.assertFalse(out[1]["omega2_outside_final_tolerance_descriptive_not_optimizer_iter_gate"])
        self.assertTrue(out[1]["any_free_outside_final_tolerance_descriptive_not_optimizer_iter_gate"])

    def test_first_exact_nonzero_not_final_threshold(self):
        h=np.array([[-3.,-6.,3.87],[-3.+1e-12,-6.,3.87],
                    [-3.+2e-7,-6.,3.87]])
        m=np.array([[-3.,-6.,3.87]]*3)
        rows=pointwise_drift(h,m,3e-8,3e-10)
        self.assertEqual(first(row["omega2_abs_diff"]>0 for row in rows),1)
        self.assertEqual(first(row["omega2_outside_final_tolerance_descriptive_not_optimizer_iter_gate"] for row in rows),2)

    def test_first_returns_none_without_satisfying_record(self):
        self.assertIsNone(first([False,False]))
        self.assertEqual(first([False,True,True]),1)

    def test_original_history_matrix_shape_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"Nx3"):
            pointwise_drift(np.ones((25,2)),np.ones((25,2)),3e-8,3e-10)

    def test_missing_history_or_extra_record_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"matching"):
            pointwise_drift(np.ones((25,3)),np.ones((24,3)),3e-8,3e-10)

    def test_nonfinite_original_history_denied(self):
        x=np.ones((25,3))
        y=x.copy()
        y[14,0]=np.nan
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            pointwise_drift(x,y,3e-8,3e-10)

    def test_signed_omega2_direction_is_preserved(self):
        h=np.array([[-3.,-6.,3.87],[-2.,-7.,3.9]])
        m=np.array([[-3.,-6.,3.87],[-1.,-8.,4.1]])
        r=pointwise_drift(h,m,3e-8,3e-10)
        self.assertEqual(r[1]["omega2_signed_diff"],-1.)
        self.assertEqual(r[1]["omega3_signed_diff"],1.)
        self.assertEqual(r[1]["obs_logze_signed_diff"],-0.19999999999999973)
        self.assertTrue(r[1]["omega2_outside_final_tolerance_descriptive_not_optimizer_iter_gate"])


if __name__=="__main__":
    unittest.main()
