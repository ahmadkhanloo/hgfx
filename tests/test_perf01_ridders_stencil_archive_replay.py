"""Negative and positive archive-only source audit controls: never a scientific gate."""
from __future__ import annotations
from copy import deepcopy
import sys
from pathlib import Path
import unittest

SRC=Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"
sys.path.insert(0,str(SRC))
import subject7_first_ridders_stencil as base
import replay_initial_ridders_stencil_archive as audit


def make_fixture():
    steps=[11,11,13]
    nodes=[{"ordinal":0,"x":base.START.copy(),"x_hex":base.xhex(base.START),"value":100.}]
    for axis in range(3):
        h=1.
        for step in range(steps[axis]):
            for sign in (1.,-1.):
                xx=base.START.copy();xx[axis]+=sign*h
                nodes.append({"ordinal":len(nodes),"x":xx,"x_hex":base.xhex(xx),
                              "value":float(100.+axis+sign*h)})
            h/=1.2
    h={
        "schema":base.SCHEMA,"status":"SOURCE_HGFX_INITIAL_RIDDERS_OWN_STENCIL",
        "frozen_hgfx_sha":base.HGFX,"frozen_matlab_sha":base.MATLAB,
        "original_63_subject_fit_status":"63/64 SCIENTIFIC NONPASS",
        "environment":{"github_run_id":audit.RUN,"github_sha":audit.SOURCE_SHA},
        "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
        "min_steps":10,"steps_per_coordinate":steps,
        "hgfx_gradient":[1.,2.,3.],"hgfx_nodes":deepcopy(nodes),
    }
    m={
        "schema":"perf01d-real-private-matlab-first-ridders-stencil-v1",
        "frozen_hgfx_sha":base.HGFX,"frozen_matlab_sha":base.MATLAB,
        "github_run_id":audit.RUN,"tested_sha":audit.SOURCE_SHA,
        "source_hgfx_stencil_sha256":audit.MEMBERS["hgfx-first-ridders.json"],
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "original_failure":{"traj_mu":4,"traj_muhat":4},
        "native_wrapped_26_and_iter_exact":True,"hook_count":1,
        "original_optimizer_delegated":True,
        "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
        "min_steps":10,"matlab_nodes":deepcopy(nodes),
        "matlab_gradient":[1.,2.,3.],
    }
    hrows,mrows=base.classify_stencil(nodes)[1],base.classify_stencil(m["matlab_nodes"])[1]
    pairs=[]
    for axis in range(3):
        lhs=[z for z in hrows if z["coord_zero_based"]==axis]
        rhs=[z for z in mrows if z["coord_zero_based"]==axis]
        for step,(a,bb) in enumerate(zip(lhs,rhs),start=1):
            for sign in ("positive","negative"):
                pairs.append({"coord_zero_based":axis,"step_one_based":step,
                              "sign":sign,"same_stencil_x_binary64":True})
    cross_h=[{"index":i,"x":z["x"],"hgfx_value":z["value"],
              "matlab_value_same_x":z["value"],"same_objective_binary64":True}
             for i,z in enumerate(nodes)]
    cross_m=[{"index":i,"x":z["x"],"matlab_value":z["value"],
              "hgfx_value_same_x":z["value"],"same_objective_binary64":True}
             for i,z in enumerate(nodes)]
    d={
       "schema":"perf01d-initial-ridders-same-x-both-objectives-v1",
       "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
       "source_hgfx_sha256":audit.MEMBERS["hgfx-first-ridders.json"],
       "source_matlab_sha256":audit.MEMBERS["matlab-first-private-ridders.json"],
       "independent_scientific_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
       "performance_timing":"NOT_RUN",
       "hgfx_step_counts":steps,"matlab_step_counts":steps,
       "hgfx_objective_eval_count":len(nodes),"matlab_objective_eval_count":len(nodes),
       "all_hgfx_own_stencil_nodes":cross_h,
       "all_matlab_own_stencil_nodes":cross_m,
       "same_x_hgfx_own_stencil_objective_equal_binary64_count":len(nodes),
       "same_x_matlab_own_stencil_objective_equal_binary64_count":len(nodes),
       "original_own_stencil_pair_inventory":pairs,
    }
    native={
       "schema":"perf01d-matlab-initial-ridders-private-raw-public-verification-v1",
       "real_mat_sha256":audit.MEMBERS["matlab-first-ridders-native-and-wrapped.mat"],
       "native_wrapped_26_exact":True,"native_wrapped_complete_iter_exact":True,
       "all_actual_26_field_pairs":[{"field":f"field_{i}","exact_equal_nan":True}
                                    for i in range(26)],
       "original_full_fit":"63/64 SCIENTIFIC NONPASS",
       "independent_scientific_review":"NOT_RECEIVED",
    }
    cases=[{} for _ in range(8)]
    cases[7]={"mismatched_fields":["traj.mu","traj.muhat"],
              "fields":{"traj.mu":{"mismatch_count":4},
                        "traj.muhat":{"mismatch_count":4}}}
    original={"hgfx_sha":base.HGFX,"matlab_sha":base.MATLAB,"subject_count":64,
              "classification_counts":{
                  "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
                  "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1},
              "cases":cases}
    return h,m,d,native,original


class FrozenRiddersSourceArchiveReplayTests(unittest.TestCase):
    def test_all_71_nodes_identical_on_both_source_grids(self):
        z=audit.audit(*make_fixture())
        self.assertEqual(z["hgfx_steps"],[11,11,13])
        self.assertEqual(z["matlab_steps"],[11,11,13])
        self.assertEqual(z["paired_source_stencil_coordinates_exact_binary64_count"],70)
        self.assertEqual(z["each_original_source_grid_cross_objective_comparison"]["hgfx"]["equal_scalar_bits"],71)

    def test_report_real_same_x_one_ulp_difference_without_tolerance(self):
        h,m,d,native,orig=make_fixture()
        value=d["all_hgfx_own_stencil_nodes"][5]["matlab_value_same_x"]
        import math
        d["all_hgfx_own_stencil_nodes"][5]["matlab_value_same_x"]=math.nextafter(value,math.inf)
        d["all_hgfx_own_stencil_nodes"][5]["same_objective_binary64"]=False
        d["same_x_hgfx_own_stencil_objective_equal_binary64_count"]=70
        z=audit.audit(h,m,d,native,orig)
        self.assertEqual(z["each_original_source_grid_cross_objective_comparison"]["hgfx"]["unequal_scalar_bits"],1)
        self.assertEqual(z["each_original_source_grid_cross_objective_comparison"]["hgfx"]["maximum_same_x_objective_ulp_difference"],1)

    def test_mutated_cross_value_flag_is_rejected(self):
        h,m,d,n,o=make_fixture()
        d["all_hgfx_own_stencil_nodes"][5]["matlab_value_same_x"]+=0.25
        with self.assertRaisesRegex(ValueError,"same-x cross-eval"):
            audit.audit(h,m,d,n,o)

    def test_missing_cross_node_is_rejected(self):
        h,m,d,n,o=make_fixture()
        d["all_hgfx_own_stencil_nodes"].pop()
        with self.assertRaisesRegex(ValueError,"inventory"):
            audit.audit(h,m,d,n,o)

    def test_wrong_scientific_64_of_64_forgery_is_rejected(self):
        h,m,d,n,o=make_fixture()
        o["classification_counts"]["FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"]=64
        with self.assertRaisesRegex(ValueError,"63/64"):
            audit.audit(h,m,d,n,o)

    def test_wrong_original_4_plus_4_forgery_is_rejected(self):
        h,m,d,n,o=make_fixture()
        o["cases"][7]["fields"]["traj.mu"]["mismatch_count"]=0
        with self.assertRaisesRegex(ValueError,"63/64"):
            audit.audit(h,m,d,n,o)

    def test_original_matlab_raw_full_iter_neutrality_required(self):
        h,m,d,n,o=make_fixture()
        n["native_wrapped_complete_iter_exact"]=False
        with self.assertRaisesRegex(ValueError,"neutrality"):
            audit.audit(h,m,d,n,o)

    def test_forged_independent_reviewer_signoff_rejected(self):
        h,m,d,n,o=make_fixture()
        h["independent_review"]="APPROVED"
        with self.assertRaisesRegex(ValueError,"scientific status"):
            audit.audit(h,m,d,n,o)

    def test_tampered_original_matlab_source_sha_rejected(self):
        h,m,d,n,o=make_fixture()
        m["source_hgfx_stencil_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"MATLAB nested source"):
            audit.audit(h,m,d,n,o)

    def test_reordered_paired_stencil_record_rejected(self):
        h,m,d,n,o=make_fixture()
        d["original_own_stencil_pair_inventory"][0]["coord_zero_based"]=2
        with self.assertRaisesRegex(ValueError,"reordered"):
            audit.audit(h,m,d,n,o)

    def test_missing_matlab_ridders_pair_rejected(self):
        h,m,d,n,o=make_fixture()
        m["matlab_nodes"].pop()
        with self.assertRaisesRegex(ValueError,"pair"):
            audit.audit(h,m,d,n,o)

    def test_original_26_field_member_missing_rejected(self):
        h,m,d,n,o=make_fixture()
        n["all_actual_26_field_pairs"].pop()
        with self.assertRaisesRegex(ValueError,"neutrality"):
            audit.audit(h,m,d,n,o)


if __name__=="__main__":unittest.main()
