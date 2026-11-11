"""Local fitted Hessian-scale audit; deterministic synthetic negative controls.

Not a scientific identifiability, acceptance or new tolerance test.
"""
from __future__ import annotations
from copy import deepcopy
import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from derive_subject7_laplace_scales import (
    fit_record,posterior_geometry,OLD_TRAJ_TOLERANCE,STATUS,
)
from fit_cohort_hgfx import FIT_FIELDS

def optim():
    data={key:0. for key in FIT_FIELDS}
    data["init"]=[0.]*15
    data["final"]=[0.]*15
    data["H"]=[[1.,0.,0.],[0.,2.,0.],[0.,0.,4.]]
    data["Sigma"]=[[1.,0.,0.],[0.,.5,0.],[0.,0.,.25]]
    data["negLj"]=100.
    return data

class PosthocLaplaceScaleGuards(unittest.TestCase):
    def test_no_scientific_gate_promotion_or_tolerance_change(self):
        self.assertEqual(OLD_TRAJ_TOLERANCE,{"rtol":3e-8,"atol":3e-10})
        self.assertIn("POSTHOC",STATUS)
        self.assertIn("NONPASS",STATUS)

    def test_positive_definite_finite_hessian_laplace_covariance(self):
        g=posterior_geometry(optim())
        self.assertTrue(g["local_H_and_Sigma_positive_definite"])
        self.assertEqual(g["H_eigenvalues_ascending"],[1.,2.,4.])
        self.assertEqual(g["H_2norm_condition_number"],4.)
        self.assertEqual(g["Sigma_diagonal_sqrt"],[1.,2**(-.5),.5])
        self.assertEqual(g["inverse_pair_H_Sigma_residual_max_abs"],0.)

    def test_symmetric_numerical_drift_is_reported_not_silently_reset(self):
        o=optim()
        o["H"][0][1]=1e-8
        g=posterior_geometry(o)
        self.assertEqual(g["H_symmetry_residual_max_abs"],1e-8)

    def test_non_positive_hessian_is_flagged_without_fabricating_distance(self):
        o=optim()
        o["H"][0][0]=-1.
        g=posterior_geometry(o)
        self.assertFalse(g["local_H_and_Sigma_positive_definite"])
        self.assertIsNone(g["Sigma_diagonal_sqrt"])

    def test_bad_hessian_shape_fails(self):
        o=optim()
        o["H"]=[[1.,0.],[0.,1.]]
        with self.assertRaisesRegex(ValueError,"3x3"):
            posterior_geometry(o)

    def test_nonfinite_laplace_hessian_fails(self):
        o=optim()
        o["H"][2][2]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite"):
            posterior_geometry(o)

    def test_missing_original_fit_field_rejected(self):
        o=optim()
        del o["negLl"]
        with self.assertRaisesRegex(ValueError,"15 full fitting"):
            fit_record({"optim":o})

    def test_invalid_15_dof_parameter_shape_rejected(self):
        o=optim()
        o["final"]=[0.]*14
        with self.assertRaisesRegex(ValueError,"15-parameter"):
            fit_record({"optim":o})

    def test_nonfinite_original_free_fit_rejected(self):
        o=optim()
        o["final"][12]=float("inf")
        with self.assertRaisesRegex(ValueError,"finite free"):
            fit_record({"optim":o})

    def test_complete_realistic_frozen_shape(self):
        o=optim()
        o["final"][12]=1e-8
        result,geometry,free=fit_record({"optim":o})
        self.assertEqual(result["negLj"],100.)
        self.assertTrue(geometry["local_H_and_Sigma_positive_definite"])
        self.assertEqual(free.tolist(),[1e-8,0.,0.])

if __name__=="__main__":
    unittest.main()
