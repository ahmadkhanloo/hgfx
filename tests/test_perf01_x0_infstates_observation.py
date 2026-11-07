"""Fail-closed original x0 source HGF infStates/unitsq stage audit controls."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from hgfx.responses.unitsq_sigmoid import unitsq_sgm
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import compare_original_x0_infstates_observation as x
from original_x0_hgfx_infstates import ORIGINAL_TERM_SHA
from subject7_first_ridders_stencil import xhex,START


class SyntheticProblem:
    n_perceptual=14
    responses=np.zeros(128,dtype=np.float64)
    inputs=np.ones(128,dtype=np.float64)
    def expand(self,z):
        return np.asarray([0.]*15,dtype=np.float64)


def make_fixture():
    problem=SyntheticProblem()
    predictor=[0.5]*128
    states={key:[[0.5,0.5,0.5] for _ in range(128)]
            for key in x.STAGES}
    state=np.full((128,3,4),0.5,dtype=np.float64)
    raw=unitsq_sgm(problem.responses,state,np.array([0.]),predorpost=1)[0]
    native=[float(v) for v in raw]
    matlab=native.copy();matlab[0]=math.nextafter(matlab[0],math.inf)
    hh=[];mm=[];oldh=[];oldm=[]
    for i in range(71):
        at=START.copy();at[0]+=i/128
        h={"ordinal":i,"x":at,"x_hex":xhex(at),
           "native_source_objective":100.,
           "original_matlab_private_source_objective":math.nextafter(100.,math.inf),
           "native_logp":native.copy(),
           "native_prediction_level1":predictor.copy(),
           "native_posterior_level1":predictor.copy(),
           "native_zeta":1.,"native_inf_states":copy.deepcopy(states)}
        m={"ordinal":i,"x":at,"x_hex":xhex(at),
           "original_hgfx_objective":100.,
           "original_genuine_private_objective":math.nextafter(100.,math.inf),
           "native_logp":matlab.copy(),
           "native_prediction_level1":predictor.copy(),
           "native_posterior_level1":predictor.copy(),
           "native_zeta":1.,"native_inf_states":copy.deepcopy(states),
           "matlab_unitsq_on_hgfx_prediction_logp":matlab.copy()}
        hh.append(h);mm.append(m)
        oldh.append({"original_node_index":i,"x":at,
                     "components":{"full_trial_log_likelihood":native.copy()},
                     "original_hgfx_source_scalar":100.})
        oldm.append({"original_node_index":i,"x":at,
                     "components":{"full_trial_log_likelihood":matlab.copy()},
                     "original_matlab_private_source_scalar":math.nextafter(100.,math.inf)})
    env={"GITHUB_RUN_ID":"1337001","GITHUB_SHA":"d"*40}
    h={"schema":"perf01d-frozen-hgfx-infstates-71-native-obs-v1",
       "status":"ORIGINAL_FROZEN_HGFX_INFSTATES_AND_UNITSQ_SOURCE_EXACT_ALL_71",
       "frozen_hgfx_sha":x.HGFX,"frozen_matlab_sha":x.MATLAB,
       "original_true_private_ridders_run":x.RUN,
       "original_true_private_ridders_sha":x.SOURCE_SHA,
       "original_constituents_source_run":"42402421462",
       "original_71_node_count":71,"n_trials":128,
       "inf_states_shape_per_node":[128,3,4],
       "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
       "original_failures":{"traj.mu":4,"traj.muhat":4},
       "original_source_term_sha256":ORIGINAL_TERM_SHA,
       "independent_scientific_review":"NOT_RECEIVED",
       "perf01c":"NOT_FROZEN","predorpost":1,
       "selected_source_infstate_component":"muhat",
       "original_irregular_trial_indices_zero_based":[],
       "environment":{"run_id":env["GITHUB_RUN_ID"],
                      "tested_sha":env["GITHUB_SHA"]},
       "nodes":hh}
    rawh=(json.dumps(h,sort_keys=True)+"\n").encode()
    m={"schema":x.M_SCHEMA,
       "status":"ORIGINAL_FROZEN_MATLAB_INFSTATES_NATIVE_EXACT_AND_OBS_ON_HGFX",
       "frozen_hgfx_sha":x.HGFX,"frozen_matlab_sha":x.MATLAB,
       "original_true_private_ridders_run":x.RUN,
       "original_true_private_ridders_sha":x.SOURCE_SHA,
       "original_constituents_source_run":"42402421462",
       "original_hgfx_infstates_sha256":sha256(rawh).hexdigest(),
       "original_71_node_count":71,"n_trials":128,
       "inf_states_shape_per_node":[128,3,4],
       "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
       "original_failures":{"traj_mu":4,"traj_muhat":4},
       "independent_scientific_review":"NOT_RECEIVED",
       "perf01c":"NOT_FROZEN","predorpost":1,
       "native_fit_unmodified":True,
       "native_perceptual_function":"hgf_binary",
       "native_observation_function":"unitsq_sgm",
       "native_perceptual_file":"/frozen/_original_models/hgf_binary.m",
       "native_observation_file":"/frozen/observation/unitsq_sgm.m",
       "native_fitmodel_file":"/frozen/core/fitModel.m",
       "github_run_id":env["GITHUB_RUN_ID"],
       "tested_sha":env["GITHUB_SHA"],
       "nodes":mm}
    cases=[{} for _ in range(8)]
    cases[7]={"mismatched_fields":["traj.mu","traj.muhat"],
              "fields":{"traj.mu":{"mismatch_count":4},
                        "traj.muhat":{"mismatch_count":4}}}
    fit={"subject_count":64,"hgfx_sha":x.HGFX,"matlab_sha":x.MATLAB,
         "classification_counts":{
           "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
           "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1},
         "cases":cases}
    return h,m,{"nodes":oldh},{"nodes":oldm},fit,rawh,problem,env


class FrozenInfstateStageChecks(unittest.TestCase):
    def evaluate(self,parts=None):
        parts=parts if parts is not None else make_fixture()
        h,m,a,b,fit,raw,p,env=parts
        with patch.dict(os.environ,env):
            return x.main_compare(h,m,a,b,fit,raw,p)

    def test_valid_complete_exact_original_native_ll_and_cross(self):
        z=self.evaluate()
        self.assertEqual(z["original_71_node_count"],71)
        self.assertEqual(z["per_comparison_nodes_with_at_least_one_trial_difference"]["native_per_trial_logp"],71)
        self.assertEqual(z["per_comparison_nodes_with_at_least_one_trial_difference"]["first_level_muhat"],0)
        self.assertEqual(z["per_comparison_nodes_with_at_least_one_trial_difference"]["matlab_vs_hgfx_observation_on_hgfx_prediction"],71)

    def test_missing_one_trial_refused(self):
        p=list(make_fixture());p[1]["nodes"][4]["native_prediction_level1"].pop()
        with self.assertRaisesRegex(ValueError,"128"):self.evaluate(p)

    def test_reordered_original_source_refused(self):
        p=list(make_fixture());p[1]["nodes"][6]["ordinal"]=7
        with self.assertRaisesRegex(ValueError,"ordering"):self.evaluate(p)

    def test_native_old_real_matlab_trial_oracle_refused(self):
        p=list(make_fixture());p[1]["nodes"][2]["native_logp"][1]+=0.125
        with self.assertRaisesRegex(ValueError,"original exact 128"):self.evaluate(p)

    def test_original_hgfx_observation_native_oracle_refused(self):
        p=list(make_fixture());p[0]["nodes"][2]["native_logp"][0]+=0.1
        with self.assertRaisesRegex(ValueError,"original exact 128"):self.evaluate(p)

    def test_forged_original_64_64_science_refused(self):
        p=list(make_fixture());p[4]["classification_counts"]["FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"]=64
        with self.assertRaisesRegex(ValueError,"63/64"):self.evaluate(p)

    def test_forged_original_four_mu_mismatches_refused(self):
        p=list(make_fixture());p[0]["original_failures"]["traj.mu"]=0
        with self.assertRaisesRegex(ValueError,"provenance"):self.evaluate(p)

    def test_forged_independent_reviewer_refused(self):
        p=list(make_fixture());p[0]["independent_scientific_review"]="APPROVED"
        with self.assertRaisesRegex(ValueError,"provenance"):self.evaluate(p)

    def test_forged_native_source_lineage_refused(self):
        p=list(make_fixture());p[1]["native_observation_file"]="/other/unitsq_sgm.m"
        with self.assertRaisesRegex(ValueError,"lineage"):self.evaluate(p)

    def test_corrupted_original_source_sha_refused(self):
        p=list(make_fixture());p[1]["original_hgfx_infstates_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"provenance"):self.evaluate(p)

    def test_nan_pattern_comparison_is_preserved(self):
        self.assertTrue(x.equal(None,None))
        self.assertFalse(x.equal(None,0.))
        p=list(make_fixture())
        p[1]["nodes"][1]["native_inf_states"]["sa"][7][2]=None
        z=self.evaluate(p)
        self.assertEqual(z["per_component_infstate_node_nan_mask_differences"]["sa"],1)

    def test_nonfinite_source_input_refused(self):
        p=list(make_fixture());p[1]["nodes"][3]["native_prediction_level1"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"contains null"):self.evaluate(p)

    def test_wrong_source_selected_prediction_refused(self):
        p=list(make_fixture());p[1]["nodes"][3]["native_prediction_level1"][0]=0.25
        with self.assertRaisesRegex(ValueError,"genuine infStates slice"):self.evaluate(p)

    def test_forged_source_zeta_refused(self):
        p=list(make_fixture());p[1]["nodes"][6]["native_zeta"]=float("nan")
        with self.assertRaisesRegex(ValueError,"zeta"):self.evaluate(p)


if __name__=="__main__":
    unittest.main()
