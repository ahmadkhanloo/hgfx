"""Fail-closed tests for original 2^2 frozen omega counterfactual decomposition."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from subject7_omega_counterfactual_hgfx import CORNERS,ORIGIN_INDEX,exact_vectors
from compare_subject7_omega_counterfactual import (
    STATUS,RAW,HGFX_SHA,MATLAB_SHA,EXPECTED_4,
    validate,signed_decomposition,details
)


def two_endpoints():
    m=np.asarray([np.nan,0,1,np.nan,-2.3,0,np.nan,0,0,0,0,np.nan,
                  -3,-6,3.87],dtype=float)
    h=m.copy()
    h[12]=-3.00000001
    h[13]=-5.99999998
    h[14]=3.87000001
    return h,m


def fake_raw(engine):
    h,m=two_endpoints()
    vectors=exact_vectors(h,m)
    cases=[]
    for corner in CORNERS:
        a,b=ORIGIN_INDEX[corner]
        cases.append({
            "corner":corner,
            "omega2_from":"HGFX" if a else "MATLAB",
            "omega3_from":"HGFX" if b else "MATLAB",
            "status":f"EVALUATED_FROZEN_UNTIMED_{engine.upper()}_FORWARD",
            "full_transformed_vector":[float(x) if np.isfinite(x) else None
                                       for x in vectors[corner]],
            "traj":{name:[[0.]*(2 if name=="w" else 3) for _ in range(128)]
                    for name in ("mu","muhat","sa","sahat","da","epsi","psi",
                                 "ud","v","w","wt")},
            "inf_states":[[[0.]*4 for _ in range(3)] for _ in range(128)],
        })
    hashes=dict(RAW)
    if engine=="matlab":
        hashes={k.replace("_raw.json","_raw_json"):v for k,v in hashes.items()}
    source={
        "schema":f"perf01d-subject7-omega-counterfactual-{engine}-v1",
        "status":"AUTHOR_SIDE_2X2_OMEGA_FORWARD_DIAGNOSTIC_NO_FITTING_OR_SCIENTIFIC_PASS",
        "original_64_fit_run":"41863441006",
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "original_raw_sha256":hashes,
        "source_input_sha256":"original-input",
        "source_config_sha256":"original-config",
        "subject_index_zero_based":7,
        "trials":128,
        "model":"hgf_binary",
        "observation":"unitsq_sgm",
        "perceptual_free_coordinates_zero_based":[12,13],
        "observation_free_coordinate_zero_based":14,
        "observation_coordinate_role":
            "fixed_original_MATLAB_in_mixed_corners_not_used_in_perceptual_forward",
        "original_full_parameter_ends_preserved":True,
        "predeclared_corner_order":list(CORNERS),
        "cases":cases,
    }
    return source


def summary():
    return {"hgfx_input_sha256":"original-input",
            "hgfx_config_sha256":"original-config"}


class TestOriginalPerceptualCounterfactual(unittest.TestCase):
    def test_exact_original_2x2_denominator(self):
        self.assertEqual(len(CORNERS),4)
        self.assertEqual(tuple(EXPECTED_4),CORNERS)
        self.assertEqual(set(ORIGIN_INDEX.values()),{(0,0),(1,0),(0,1),(1,1)})
        self.assertIn("NOT_FIT_PARITY",STATUS)

    def test_exact_vectors_preserve_endpoint_and_observation(self):
        h,m=two_endpoints()
        v=exact_vectors(h,m)
        self.assertTrue(np.array_equal(v["MM_original_matlab"],m,equal_nan=True))
        self.assertTrue(np.array_equal(v["HH_original_hgfx"],h,equal_nan=True))
        self.assertEqual(v["HM_hgfx_omega2_matlab_omega3"][12],h[12])
        self.assertEqual(v["HM_hgfx_omega2_matlab_omega3"][13],m[13])
        self.assertEqual(v["MH_matlab_omega2_hgfx_omega3"][12],m[12])
        self.assertEqual(v["MH_matlab_omega2_hgfx_omega3"][13],h[13])
        self.assertEqual(v["HM_hgfx_omega2_matlab_omega3"][14],m[14])
        self.assertEqual(v["MH_matlab_omega2_hgfx_omega3"][14],m[14])

    def test_source_consistent_four_corner_both_engines(self):
        h,m=two_endpoints()
        expected=exact_vectors(h,m)
        for engine in ("matlab","hgfx"):
            got=validate(fake_raw(engine),engine,summary(),expected)
            self.assertEqual(tuple(got),CORNERS)

    def test_source_raw_sha_tamper_is_blocked(self):
        h,m=two_endpoints()
        a=fake_raw("hgfx")
        a["original_raw_sha256"]["hgfx_raw.json"]="tampered"
        with self.assertRaisesRegex(ValueError,"protocol/identity"):
            validate(a,"hgfx",summary(),exact_vectors(h,m))

    def test_wrong_critical_omega_coordinate_is_blocked(self):
        h,m=two_endpoints()
        a=fake_raw("hgfx")
        a["cases"][1]["full_transformed_vector"][12]=-5.
        with self.assertRaisesRegex(ValueError,"parameter vector"):
            validate(a,"hgfx",summary(),exact_vectors(h,m))

    def test_missing_corner_is_blocked(self):
        h,m=two_endpoints()
        a=fake_raw("matlab")
        a["cases"].pop()
        with self.assertRaisesRegex(ValueError,"four"):
            validate(a,"matlab",summary(),exact_vectors(h,m))

    def test_missing_hgf_field_is_blocked(self):
        h,m=two_endpoints()
        a=fake_raw("hgfx")
        del a["cases"][0]["traj"]["muhat"]
        with self.assertRaisesRegex(ValueError,"parameter vector"):
            validate(a,"hgfx",summary(),exact_vectors(h,m))

    def test_w_shape_follows_real_128x2(self):
        h,m=two_endpoints()
        a=fake_raw("hgfx")
        a["cases"][0]["traj"]["w"]=[[0,0,0] for _ in range(128)]
        with self.assertRaisesRegex(ValueError,"w shape"):
            validate(a,"hgfx",summary(),exact_vectors(h,m))

    def test_reject_mismatched_endpoint_nan(self):
        h,m=two_endpoints()
        h[1]=np.nan
        with self.assertRaisesRegex(ValueError,"shape/NaN"):
            exact_vectors(h,m)

    def test_reject_unexpected_nonfree_parameter_difference(self):
        h,m=two_endpoints()
        h[10]=1e-6
        with self.assertRaisesRegex(ValueError,"nonfitted"):
            exact_vectors(h,m)

    def test_shapley_exact_linear_additive(self):
        base=np.array([[1.,2.]])
        change2=np.array([[4.,2.]])  # H/M = base + omega2
        change3=np.array([[1.,7.]])  # M/H = base + omega3
        target=np.array([[4.,7.]])   # H/H
        source=np.array([[0.25,-0.5]])
        fitted_h=target+source
        v=signed_decomposition(base,change3,change2,target,fitted_h,base)
        np.testing.assert_allclose(v["omega2"],[[3.,0.]])
        np.testing.assert_allclose(v["omega3"],[[0.,5.]])
        np.testing.assert_allclose(v["same_vector_source_at_HH_plus_own_fit_reconstruction"],source)
        np.testing.assert_allclose(v["reconstruction_residual"],[[0.,0.]])

    def test_shapley_interaction_symmetrically_apportioned(self):
        base=np.array([[0.]])
        change2=np.array([[1.]])
        change3=np.array([[1.]])
        target=np.array([[4.]])  # 2 units interaction
        r=signed_decomposition(base,change3,change2,target,target,base)
        self.assertEqual(float(r["omega2"][0,0]),2.)
        self.assertEqual(float(r["omega3"][0,0]),2.)
        self.assertEqual(float(r["omega_sum_residual"][0,0]),0.)

    def test_signed_contributions_can_cancel(self):
        base=np.array([[0.]])
        change2=np.array([[3.]])
        change3=np.array([[-2.]])
        target=np.array([[1.]])
        x=signed_decomposition(base,change3,change2,target,target,base)
        self.assertEqual(float(x["omega2"][0,0]),3.)
        self.assertEqual(float(x["omega3"][0,0]),-2.)
        self.assertEqual(float(x["observed"][0,0]),1.)

    def test_bad_finite_mask_blocks_uninterpretable_decomposition(self):
        zero=np.array([[0.,0.]])
        nan=np.array([[0.,np.nan]])
        with self.assertRaisesRegex(ValueError,"nonfinite masks"):
            signed_decomposition(zero,zero,zero,zero,nan,zero)

    def test_original_critical_trial_indices_preserved(self):
        base=np.zeros((128,3))
        hgfx=base.copy()
        for i in (83,108,116,126):
            hgfx[i,1]=8e-10
        comp=signed_decomposition(base,base,base,hgfx,hgfx,base)
        row=details(comp,base)
        self.assertEqual(row["num_original_outside_fixed_tolerance"],4)
        self.assertEqual([x["trial_one_based"] for x in row["original_outside_fixed_tolerance"]],
                         [84,109,117,127])
        self.assertEqual([x["level_one_based"] for x in row["original_outside_fixed_tolerance"]],
                         [2,2,2,2])

    def test_no_diversion_from_full_original_fit_gate(self):
        self.assertEqual(HGFX_SHA,"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27")
        self.assertEqual(MATLAB_SHA,"2437f4dc241541072722a2695ddeca7b44d83dd3")
        self.assertEqual(len(RAW),2)


if __name__=="__main__":
    unittest.main()
