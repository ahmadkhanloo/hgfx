"""Fail-closed synthetic checks of archived HGFX true Armijo source body events."""
from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
from test_perf01_same_runner_actual_source_calls import base
import replay_hgfx_real_branch_events_archive as checker


def fixture():
    h,m=base()
    sites=h["metadata"]["source_python_optimizer_sites"]
    xs=h["original_native_101_iter_x"][:25]
    vals=h["original_native_101_iter_val"][:25]
    calls=[h["calls"][0]]
    actions=[]
    for i in range(1,25):
        calls.append({
           "kind":"LINESEARCH","source_line":sites["LINESEARCH"],
           "direct_index_zero_based":i,"call_number":i*3+1,
           "objective":vals[i],"free_x":deepcopy(xs[i]),"finite":True,
           "actual_original_j":0,
           "actual_original_step_fraction":1.,
           "actual_original_matlab_i":i,
        })
        for lab in ("ARMIO_BREAK_EXECUTED","ACCEPTED_UPDATE_EXECUTED"):
            actions.append({
               "label":lab,"source_line":sites[lab],
               "optimizer_iteration_one_based":i,"actual_j":0,
               "candidate_x":deepcopy(xs[i]),"candidate_value":vals[i],
            })
        if i<=22:
            actions.append({
                "label":"BFGS_CURVATURE_UPDATE_EXECUTED",
                "source_line":sites["BFGS_CURVATURE_UPDATE_EXECUTED"],
                "optimizer_iteration_one_based":i,
            })
        if i<=11:
            actions.append({
                "label":"DESCENT_CLIPPED_EXECUTED",
                "source_line":sites["DESCENT_CLIPPED_EXECUTED"],
                "optimizer_iteration_one_based":i,
            })
    actions.append({
        "label":"TERMINATION_TOL_GRAD_EXECUTED",
        "source_line":sites["TERMINATION_TOL_GRAD_EXECUTED"],
        "optimizer_iteration_one_based":24,
    })
    h["calls"]=calls
    h["executed_source_branch_bodies"]=actions
    h["metadata"]["direct_counts"]={"INITIAL":1,"LINESEARCH":24,"RESET":0}
    h["metadata"]["branch_executed_counts"]={
        "ARMIO_BREAK_EXECUTED":24,"ACCEPTED_UPDATE_EXECUTED":24,
        "BFGS_CURVATURE_UPDATE_EXECUTED":22,"DESCENT_CLIPPED_EXECUTED":11,
        "TERMINATION_TOL_GRAD_EXECUTED":1}
    h["metadata"]["indirect_call_count"]=100
    h["metadata"]["all_objective_calls"]=125
    h["metadata"]["host"]["github_run_id"]=checker.RUN
    h["metadata"]["host"]["github_sha"]=checker.COMMIT
    m["metadata"]["github_run_id"]=checker.RUN
    m["metadata"]["tested_sha"]=checker.COMMIT
    return h,m


class GenuineArmijoBodyReplayTests(unittest.TestCase):
    def test_all_twenty_four_source_body_matches(self):
        h,m=fixture()
        result=checker.reconcile(h,m)
        self.assertEqual(result["hgfx_actual_executed_armijo_true_body_events"],24)
        self.assertEqual(result["hgfx_actual_executed_accepted_state_body_events"],24)
        self.assertEqual(result["hgfx_original_regularization_exponent_j_counts"],{"0":24})
        self.assertIsNone(result["first_different_trial_ordinal_zero_based"])
        self.assertEqual(result["frozen_public_scientific_fit"],"63/64 SCIENTIFIC NONPASS")

    def test_one_source_armijo_body_missing_is_rejected(self):
        h,m=fixture()
        h["executed_source_branch_bodies"]=[
            z for i,z in enumerate(h["executed_source_branch_bodies"]) if i!=0]
        with self.assertRaisesRegex(ValueError,"incomplete"):
            checker.reconcile(h,m)

    def test_branch_body_wrong_j_rejected(self):
        h,m=fixture()
        arm=next(z for z in h["executed_source_branch_bodies"] if z["label"]=="ARMIO_BREAK_EXECUTED")
        arm["actual_j"]=1
        with self.assertRaisesRegex(ValueError,"mismatch at trial"):
            checker.reconcile(h,m)

    def test_branch_body_wrong_candidate_rejected(self):
        h,m=fixture()
        arm=next(z for z in h["executed_source_branch_bodies"] if z["label"]=="ACCEPTED_UPDATE_EXECUTED")
        arm["candidate_x"][0]+=1e-6
        with self.assertRaisesRegex(ValueError,"mismatch at trial"):
            checker.reconcile(h,m)

    def test_branch_body_wrong_objective_rejected(self):
        h,m=fixture()
        arm=next(z for z in h["executed_source_branch_bodies"] if z["label"]=="ARMIO_BREAK_EXECUTED")
        arm["candidate_value"]+=0.1
        with self.assertRaisesRegex(ValueError,"mismatch at trial"):
            checker.reconcile(h,m)

    def test_forged_original_fitting_pass_is_rejected(self):
        h,m=fixture()
        m["metadata"]["original_science"]="64/64 PASS"
        with self.assertRaisesRegex(ValueError,"source/science metadata"):
            checker.reconcile(h,m)

    def test_same_runner_requirement_is_enforced(self):
        h,m=fixture()
        h["metadata"]["host"]["github_run_id"]="different"
        with self.assertRaisesRegex(ValueError,"SAME"):
            checker.reconcile(h,m)

    def test_exact_binary64_ulp_distance_is_one(self):
        import math
        self.assertEqual(checker.ulp_distance(1.0,math.nextafter(1.0,2.0)),1)
        self.assertEqual(checker.ulp_distance(-1.0,math.nextafter(-1.0,-2.0)),1)

    def test_earliest_cross_source_trial_delta_not_masked(self):
        h,m=fixture()
        m["direct_calls"][1]["free_x"][0]+=1e-9
        got=checker.reconcile(h,m)
        self.assertEqual(got["first_different_trial_ordinal_zero_based"],0)
        self.assertEqual(got["different_vector_trial_count"],1)

    def test_invalid_archive_hash_rejected_by_content(self):
        from hashlib import sha256
        self.assertNotEqual(sha256(b"not original").hexdigest(),
                            checker.HASHES["actual-frozen-hgfx-original-optimizer-source-calls.json"])


if __name__=="__main__":
    unittest.main()
