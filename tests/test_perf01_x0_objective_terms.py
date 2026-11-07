"""Synthetic source checks for 71 original HGFX/MATLAB objective decomposition."""
from __future__ import annotations
import copy
from hashlib import sha256
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import compare_original_x0_objective_terms as cv
from subject7_first_ridders_stencil import START,xhex


def dataset():
    runs={"GITHUB_RUN_ID":"12345678","GITHUB_SHA":"a"*40}
    keys={
        "schema":cv.SCHEMA,
        "status":"AUTHOR_SIDE_FROZEN_HGFX_71_SOURCE_TERM_DECOMPOSITION",
        "frozen_hgfx_sha":cv.HGFX,"frozen_matlab_sha":cv.MATLAB,
        "original_real_source_run":cv.RUN,"original_real_source_sha":cv.SOURCE_SHA,
        "original_hgfx_source_member_sha256":cv.MEMBERS["hgfx-first-ridders.json"],
        "original_matlab_source_member_sha256":cv.MEMBERS["matlab-first-private-ridders.json"],
        "original_scientific_fit":"63/64 SCIENTIFIC NONPASS",
        "original_failed_fields":{"traj.mu":4,"traj.muhat":4},
        "original_71_source_node_count":71,"environment":{
            "run_id":runs["GITHUB_RUN_ID"],"tested_sha":runs["GITHUB_SHA"]},
        "independent_scientific_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN"}
    component={
        "full_trial_log_likelihood":[1.]*128,
        "regular_trial_mask":[True]*128,
        "log_likelihood":128.,
        "negative_log_likelihood":-128.,
        "perceptual_prior_terms":[2.,3.],
        "perceptual_prior_log_total":5.,
        "observation_prior_terms":[1.],
        "observation_prior_log_total":1.,
        "negative_log_joint":200.,
    }
    own=[];theirs=[];old_h=[];old_m=[]
    raw=b"test frozen-hgfx 71 node derivative evidence"
    for i in range(71):
        x=START.copy();x[0]+=i*0.25
        c=copy.deepcopy(component);m=copy.deepcopy(component)
        private=float(math.nextafter(200.,201.)) if i<14 else 200.
        if i<14:
            m["negative_log_joint"]=private
            m["full_trial_log_likelihood"][0]=float(math.nextafter(1.,2.))
        own.append({"original_node_index":i,"x":x,"x_hex":xhex(x),
                    "original_hgfx_source_scalar":200.,
                    "original_matlab_private_source_scalar":private,"components":c})
        theirs.append({"original_node_index":i,"x":x.copy(),"x_hex":xhex(x),
                       "original_hgfx_source_scalar":200.,
                       "original_matlab_private_source_scalar":private,"components":m})
        old_h.append({"ordinal":i,"x":x.copy(),"value":200.})
        old_m.append({"ordinal":i,"x":x.copy(),"value":private})
    h=dict(keys,nodes=own)
    m={
      "schema":cv.MAT_SCHEMA,
      "status":"AUTHOR_SIDE_REAL_FROZEN_MATLAB_MODEL_SOURCE_CONSTITUENTS",
      "original_hgfx_component_sha256":sha256(raw).hexdigest(),
      "source_original_real_run":cv.RUN,"source_original_real_sha":cv.SOURCE_SHA,
      "frozen_hgfx_sha":cv.HGFX,"frozen_matlab_sha":cv.MATLAB,
      "subject_index_zero_based":7,"n_trials":128,
      "original_scientific_fit":"63/64 SCIENTIFIC NONPASS",
      "original_failure":{"traj_mu":4,"traj_muhat":4},
      "original_native_optimization":"UNMODIFIED_FROZEN_FITMODEL",
      "original_71_source_node_count":71,
      "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
      "github_run_id":runs["GITHUB_RUN_ID"],"tested_sha":runs["GITHUB_SHA"],
      "native_perceptual_function":"hgf_binary",
      "native_observation_function":"unitsq_sgm",
      "perceptual_source_file":"/reference/_original_models/hgf_binary.m",
      "observation_source_file":"/reference/observation_models/unitsq_sgm.m",
      "negative_log_joint_source_file":"/reference/core/fitModel.m",
      "nodes":theirs,
    }
    cases=[{} for _ in range(8)]
    cases[7]={"mismatched_fields":["traj.mu","traj.muhat"],
              "fields":{"traj.mu":{"mismatch_count":4},
                        "traj.muhat":{"mismatch_count":4}}}
    fit={
      "hgfx_sha":cv.HGFX,"matlab_sha":cv.MATLAB,"subject_count":64,
      "classification_counts":{
        "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
        "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1},
      "cases":cases,
    }
    return h,m,{"hgfx_nodes":old_h},{"matlab_nodes":old_m},fit,raw,runs


class FrozenObjectiveDecompositionControls(unittest.TestCase):
    def replay(self,*parts):
        h,m,oh,om,fit,raw,env=parts if parts else dataset()
        with patch.dict(os.environ,env):
            return cv.audit(h,m,oh,om,fit,raw)

    def test_source_guarded_71_full_terms_exact(self):
        z=self.replay()
        self.assertEqual(z["first_gradient_same_x_joint_unequal_count"],14)
        self.assertEqual(len(z["all_14_original_joint_mismatch_indices"]),14)
        self.assertEqual(z["original_scientific_fit"],"63/64 SCIENTIFIC NONPASS")

    def test_forged_scientific_64_64_refused(self):
        v=list(dataset());v[4]["classification_counts"]["FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"]=64
        with self.assertRaisesRegex(ValueError,"63/64"):
            self.replay(*v)

    def test_forged_reviewer_acceptance_refused(self):
        v=list(dataset());v[0]["independent_scientific_review"]="APPROVED"
        with self.assertRaisesRegex(ValueError,"63/64 provenance"):
            self.replay(*v)

    def test_wrong_original_real_run_refused(self):
        v=list(dataset());v[1]["source_original_real_run"]="other"
        with self.assertRaisesRegex(ValueError,"Genuine MATLAB"):
            self.replay(*v)

    def test_wrong_original_model_lineage_refused(self):
        v=list(dataset());v[1]["perceptual_source_file"]="/fake/new.m"
        with self.assertRaisesRegex(ValueError,"lineage"):
            self.replay(*v)

    def test_missing_128_trial_vector_refused(self):
        v=list(dataset());v[1]["nodes"][4]["components"]["full_trial_log_likelihood"].pop()
        with self.assertRaisesRegex(ValueError,"vector length"):
            self.replay(*v)

    def test_missing_original_node_refused(self):
        v=list(dataset());v[0]["nodes"].pop()
        with self.assertRaisesRegex(ValueError,"71"):
            self.replay(*v)

    def test_changed_private_scalar_detected(self):
        v=list(dataset());v[1]["nodes"][0]["components"]["negative_log_joint"]+=1e-5
        with self.assertRaisesRegex(ValueError,"source scalar"):
            self.replay(*v)

    def test_changed_source_x_bits_detected(self):
        v=list(dataset());v[1]["nodes"][5]["x"][0]+=1e-6
        with self.assertRaisesRegex(ValueError,"binary64"):
            self.replay(*v)

    def test_mask_mismatch_refused(self):
        v=list(dataset());v[1]["nodes"][0]["components"]["regular_trial_mask"][0]=False
        with self.assertRaisesRegex(ValueError,"mask"):
            self.replay(*v)

    def test_nonfinite_source_trial_refused(self):
        v=list(dataset());v[1]["nodes"][0]["components"]["full_trial_log_likelihood"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            self.replay(*v)

    def test_extra_unexpected_prior_term_field_refused(self):
        v=list(dataset());v[0]["nodes"][0]["components"]["invented"]=3.
        with self.assertRaisesRegex(ValueError,"fields"):
            self.replay(*v)

    def test_alter_only_trial_ll_changes_pertrial_count(self):
        v=list(dataset());v[1]["nodes"][17]["components"]["full_trial_log_likelihood"][1]+=0.5
        z=self.replay(*v)
        self.assertEqual(z["full_original_71_node_component_counts"]["full_trial_log_likelihood"]["nodes_with_bit_difference"],15)

    def test_forged_hgfx_member_sha_rejected(self):
        v=list(dataset());v[0]["original_hgfx_source_member_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"63/64 provenance"):
            self.replay(*v)


if __name__=="__main__":unittest.main()
