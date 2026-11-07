"""Fail-closed source arithmetic stage controls for 71 genuine original nodes × 128 trials × 2 inputs."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest

import numpy as np
from hgfx.math.matlab_exp import matlab_exp_scalar
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
from original_x0_unitsq_arithmetic_python import stage_formula,compare,bit,STAGE_NAMES
from compare_original_x0_unitsq_arithmetic import finite_vector,ACTIVE_STAGES


class OriginalUnitsqArithmeticStageTests(unittest.TestCase):
    def test_20_original_named_source_stages(self):
        x=[0.4]*128
        y=[0.,1.]*64
        z=float(matlab_exp_scalar(-0.2))
        fields=stage_formula(x,y,z)
        self.assertEqual(tuple(fields),STAGE_NAMES)
        self.assertEqual(len(fields),20)
        self.assertTrue(all(len(v)==128 for v in fields.values()))

    def test_formula_exact_for_fixed_half_probability(self):
        x=np.full(128,0.5,dtype=np.float64)
        y=np.asarray([0.,1.]*64,dtype=np.float64)
        z=float(matlab_exp_scalar(-0.2))
        inf=np.zeros((128,3,4),dtype=np.float64)
        inf[:,0,0]=x
        actual=unitsq_sgm(y,inf,[-0.2],predorpost=1)[0].tolist()
        deriv=stage_formula(x,y,z)
        self.assertEqual(compare(actual,deriv["formula_logp"]),[])

    def test_log1p_prediction_near_one_switch_matches_source_rule(self):
        xx=np.full(128,0.9999999999999,dtype=np.float64)
        a=stage_formula(xx,[1.]*128,2.)
        self.assertEqual(compare(a["logx_selected"],a["logx_alt"]),[])

    def test_log1p_one_minus_prediction_near_zero_switch(self):
        xx=np.full(128,1e-6,dtype=np.float64)
        a=stage_formula(xx,[0.]*128,2.)
        self.assertEqual(compare(a["log1mx_selected"],a["log1mx_alt"]),[])

    def test_missing_trial_must_fail(self):
        with self.assertRaisesRegex(ValueError,"128"):
            stage_formula([0.5]*127,[1.]*127,1.)

    def test_invalid_zero_predictor_refused(self):
        with self.assertRaisesRegex(ValueError,"probabilities"):
            stage_formula([0.]*128,[1.]*128,1.)

    def test_invalid_negative_zeta_refused(self):
        with self.assertRaisesRegex(ValueError,"zeta"):
            stage_formula([0.5]*128,[1.]*128,-1.)

    def test_nan_source_native_refused(self):
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            bit(float("nan"))

    def test_exact_one_ulp_mismatch_preserved(self):
        x=[1.]*128;y=x.copy();y[14]=math.nextafter(1.,math.inf)
        self.assertEqual(compare(x,y),[14])

    def test_signed_zero_not_silently_equal(self):
        x=[0.]*128;y=x.copy();y[0]=-0.
        self.assertEqual(compare(x,y),[0])

    def test_incomplete_source_stage_inventory_refused(self):
        self.assertEqual(len(set(STAGE_NAMES)),20)
        self.assertEqual(set(ACTIVE_STAGES).difference(STAGE_NAMES),set())
        self.assertIn("pow_x",ACTIVE_STAGES)
        self.assertIn("log_normalizer",ACTIVE_STAGES)

    def test_extra_or_missing_source_trial_refused(self):
        with self.assertRaisesRegex(ValueError,"128"):
            finite_vector([1.]*127,"invalid")
        with self.assertRaisesRegex(ValueError,"128"):
            finite_vector([1.]*129,"invalid")

    def test_invalid_nonfinite_stage_vector_refused(self):
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            finite_vector([1.]*127+[float("inf")],"invalid")

    def test_native_log_ratio_inputs_were_not_replaced_by_tolerance(self):
        x=np.full(128,0.25,dtype=np.float64)
        a=stage_formula(x,[1.]*128,1.)
        self.assertEqual(a["x"],[0.25]*128)
        self.assertEqual(a["y"],[1.]*128)


if __name__=="__main__":unittest.main()
