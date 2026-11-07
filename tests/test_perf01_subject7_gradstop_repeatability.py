"""Fail-closed source-native tolGrad and 2-run numeric-repeatability controls."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from derive_subject7_gradstop_repeatability import (
    STATUS,NATIVE_RUNS,TOL_GRAD,TRIAL_RTOL,TRIAL_ATOL,FIELDS,
    metric,finite_comparison,trialwise_pair,
)


def trajectory():
    return {k:[[0.]*(2 if k=="w" else 3) for _ in range(128)]
            for k in FIELDS}


class TestNativeGradientMarginReplay(unittest.TestCase):
    def test_immutable_review_scope(self):
        self.assertEqual(NATIVE_RUNS,("42232378487","42232421468"))
        self.assertEqual(TOL_GRAD,0.001)
        self.assertEqual((TRIAL_RTOL,TRIAL_ATOL),(3e-8,3e-10))
        self.assertEqual(len(FIELDS),11)
        self.assertIn("NOT_SCIENTIFIC_PASS",STATUS)

    def test_exact_frozen_source_criterion_scaling(self):
        x=[-8.0,-6.0,4.0]
        g=[0.002,0.001,0.003]
        obj=100.0
        result=metric(x,g,[1e-12]*3,obj)
        expected=max(8*0.002,6*0.001,4*0.003)/100
        self.assertAlmostEqual(result["source_tolGrad_metric"],expected)
        self.assertEqual(result["source_gradient_component_winning_index_zero_based"],0)
        self.assertEqual(result["source_metric_fraction_of_threshold"],expected/.001)

    def test_denominator_and_abs_source_rule(self):
        v=metric([-0.5,0.4,-1.5],[-2.,1.5,1.], [0,0,0],-0.2)
        self.assertEqual(v["source_scaled_gradient_components"],[2.,1.5,1.5])
        self.assertEqual(v["source_gradient_component_winning_index_zero_based"],0)

    def test_ridders_error_is_not_certified_bound(self):
        v=metric([-3,-6,3.8],[0.002,0.,0.],[1e-4,0,0],3.5)
        self.assertTrue(v["estimate_only_not_rigorous_error_bound"])
        self.assertGreater(v["Ridders_scaled_error_linf_HEURISTIC"],0.)

    def test_nonfinite_gradient_disallowed(self):
        with self.assertRaisesRegex(ValueError,"malformed"):
            metric([-3,-6,3.8],[np.nan,1,0],[1e-14]*3,50)

    def test_negative_error_estimate_disallowed(self):
        with self.assertRaisesRegex(ValueError,"malformed"):
            metric([-3,-6,3.8],[0,0,0],[-1,0,0],50)

    def test_changed_history_finite_mask_rejected(self):
        a=np.array([[0.,1.,np.nan],[1.,2.,np.nan]])
        b=a.copy();b[0,2]=7.
        with self.assertRaisesRegex(ValueError,"finite mask"):
            finite_comparison(a,b,(2,3))

    def test_detect_first_true_bitwise_drift(self):
        a=np.array([[1.,2.,3.],[4.,5.,6.]])
        b=a.copy();b[1,0]+=1e-8
        v=finite_comparison(a,b,(2,3))
        self.assertEqual(v["first_differing_index_zero_based"],[1,0])
        self.assertEqual(v["differing_finite_entries"],1)
        self.assertFalse(v["same_binary64"])

    def test_same_finite_arrays_are_exact(self):
        a=np.array([[1.,np.nan],[2.,3.]])
        r=finite_comparison(a,a.copy(),(2,2))
        self.assertTrue(r["same_binary64"])
        self.assertEqual(r["differing_finite_entries"],0)
        self.assertIsNone(r["first_differing_index_zero_based"])

    def test_old_4_plus_4_science_fail_is_preserved(self):
        m=trajectory();a=deepcopy(m);b=deepcopy(m)
        for k,positions in (("mu",[83,108,116,126]),("muhat",[84,109,117,127])):
            for p in positions:
                a[k][p][1]=8e-10
                b[k][p][1]=8e-10+1e-12
        report=trialwise_pair(a,b,m)
        self.assertEqual(report["mu"]["HGFX_run_first_vs_MATLAB_mismatched_cells_OLD_TOL"],4)
        self.assertEqual(report["muhat"]["HGFX_run_second_vs_MATLAB_mismatched_cells_OLD_TOL"],4)
        self.assertEqual(report["mu"]["between_two_HGFX_run_mismatched_cells_OLD_TOL"],0)

    def test_tampered_subject7_science_is_rejected(self):
        m=trajectory();a=deepcopy(m);b=deepcopy(m)
        with self.assertRaisesRegex(ValueError,"4\\+4"):
            trialwise_pair(a,b,m)

    def test_missing_field_fails_closed(self):
        m=trajectory();a=deepcopy(m);b=deepcopy(m)
        del a["muhat"]
        with self.assertRaisesRegex(ValueError,"all-11"):
            trialwise_pair(a,b,m)

    def test_wrong_original_w_shape_fails_closed(self):
        m=trajectory();a=deepcopy(m);b=deepcopy(m)
        a["w"]=[[0.,0.,0.] for _ in range(128)]
        with self.assertRaisesRegex(ValueError,"shape"):
            trialwise_pair(a,b,m)


if __name__=="__main__":
    unittest.main()
