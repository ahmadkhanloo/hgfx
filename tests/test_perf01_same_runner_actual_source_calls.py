"""Synthetic fail-closed checks. Not scientific validation of frozen fitting."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
S=ROOT/"benchmarks"/"runtime_v1"
sys.path.insert(0,str(S))
import compare_same_runner_actual_optimizer_calls as pair
import hgfx_actual_optimizer_calls as one


def base():
    sites={name:i+1 for i,name in enumerate((
       "INITIAL","LINESEARCH","RESET","ARMIO_BREAK_EXECUTED",
       "ACCEPTED_UPDATE_EXECUTED","BFGS_CURVATURE_UPDATE_EXECUTED",
       "TERMINATION_TOL_ARG_EXECUTED","TERMINATION_TOL_GRAD_EXECUTED",
       "TERMINATION_MAX_RESETS_EXECUTED","DESCENT_CLIPPED_EXECUTED"))}
    hm={
        "schema":pair.SCHEMA,
        "status":"AUTHOR_SIDE_ACTUAL_FROZEN_HGFX_SOURCE_CALLS_NOT_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":pair.HGFX,"frozen_matlab_sha":pair.MATLAB,
        "old_bfgs_hgfx_raw_sha256":pair.OLD_H,"old_bfgs_matlab_raw_sha256":pair.OLD_M,
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failure":{"traj.mu":4,"traj.muhat":4},
        "subject_index_zero_based":7,"trials":128,
        "neutrality_26_public_fields":True,"neutrality_full_iter":True,
        "original_finite_history_slots":25,
        "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
        "no_performance_timing":True,
        "source_python_optimizer_sites":sites,
        "direct_counts":{"INITIAL":1,"LINESEARCH":1,"RESET":0},
        "indirect_call_count":50,"all_objective_calls":52,
        "branch_executed_counts":{"ARMIO_BREAK_EXECUTED":1},
        "host":{"github_run_id":"42","github_sha":"f"*40},
    }
    xs=[[-3.,-6.,3.871201010907891]]+[[float(i),float(i+1),float(i+2)] for i in range(1,25)]
    vs=[100.-i for i in range(25)]
    calls=[
       {"kind":"INITIAL","source_line":sites["INITIAL"],
        "direct_index_zero_based":0,"call_number":1,
        "objective":100.,"free_x":xs[0].copy(),"finite":True},
       {"kind":"LINESEARCH","source_line":sites["LINESEARCH"],
        "direct_index_zero_based":1,"call_number":5,
        "objective":99.,"free_x":xs[1].copy(),"finite":True,
        "actual_original_j":0,"actual_original_step_fraction":1.,
        "actual_original_matlab_i":1},
    ]
    events=[{"label":"ARMIO_BREAK_EXECUTED","source_line":sites["ARMIO_BREAK_EXECUTED"],
             "optimizer_iteration_one_based":1,"actual_j":0,
             "candidate_x":xs[1].copy(),"candidate_value":99.}]
    pairs=[{"field":"optim."+k,"equal_nan_exact":True,"first_difference":None} for k in one.OPT]
    pairs.extend({"field":"traj.test_"+str(i),"equal_nan_exact":True,"first_difference":None}
                 for i in range(11))
    h={"metadata":hm,"calls":calls,
       "executed_source_branch_bodies":events,
       "original_native_101_iter_x":copy.deepcopy(xs)+[[None,None,None] for i in range(76)],
       "original_native_101_iter_val":vs.copy()+[None for i in range(76)],
       "native_vs_wrapped_26_field_results":pairs}
    mm={
        "schema":"perf01d-native-matlab-direct-objective-calls-v1",
        "frozen_matlab_sha":pair.MATLAB,"frozen_hgfx_sha":pair.HGFX,
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
        "timing":"NOT_RUN",
        "native_instrumented_stable_identical":True,
        "native_instrumented_history_identical":True,
        "direct_counts":[1,24,0,0],"github_run_id":"42","tested_sha":"f"*40,
        "indirect_calls":120,
    }
    mc=[{"kind":"INITIAL","free_x":xs[0].copy(),"private_objective":100.,
         "call_number":1}]
    mc.extend({"kind":"LINESEARCH","free_x":xs[i].copy(),"private_objective":vs[i],
               "call_number":i+1}
              for i in range(1,25))
    m={"metadata":mm,"direct_calls":mc,
       "native_history_x":copy.deepcopy(xs),"native_history_val":vs.copy()}
    return h,m


class OriginalSourceBranchControls(unittest.TestCase):
    def test_valid_same_run_pair_and_identical_source_trial(self):
        h,m=base()
        r=pair.compare_same_host(h,m)
        self.assertIsNone(r["first_bitwise_history_path_difference_zero_based"])
        self.assertEqual(r["first_bitwise_actual_trial_vector_difference_zero_based"],1)  # HGFX fixture has only one trial; MATLAB has 24
        self.assertEqual(r["same_x_cross_engine_trial_scalar_equal_count"],1)
        self.assertEqual(r["source_trial_count_difference"],-23)
        self.assertEqual(r["original_scientific_fitting"],"63/64 SCIENTIFIC NONPASS")

    def test_synthetic_bitwise_nan_and_nested_values(self):
        a={"a":np.array([[np.nan,1.]]),"b":(np.array([2]), {"x":3.})}
        b=copy.deepcopy(a)
        self.assertIsNone(one.exact_pair(a,b))
        b["a"][0,1]=1.1
        self.assertIsNotNone(one.exact_pair(a,b))

    def test_shape_change_not_hidden(self):
        self.assertIsNotNone(one.exact_pair(np.array([[1.]]),np.array([1.])))

    def test_missing_public_field_fails(self):
        h,m=base()
        h["native_vs_wrapped_26_field_results"].pop()
        with self.assertRaisesRegex(ValueError,"native versus wrapper"):
            pair.compare_same_host(h,m)

    def test_forged_scientific_pass_rejected(self):
        h,m=base();h["metadata"]["original_science"]="64/64 PASS"
        with self.assertRaisesRegex(ValueError,"scientific/provenance"):
            pair.compare_same_host(h,m)

    def test_cross_run_mixed_artifact_rejected(self):
        h,m=base();m["metadata"]["github_run_id"]="other run"
        with self.assertRaisesRegex(ValueError,"SAME"):
            pair.compare_same_host(h,m)

    def test_source_line_forgery_rejected(self):
        h,m=base();h["calls"][1]["source_line"]+=1
        with self.assertRaisesRegex(ValueError,"reordering/source"):
            pair.compare_same_host(h,m)

    def test_source_gradient_call_indirect_count_rejected(self):
        h,m=base();h["metadata"]["all_objective_calls"]+=1
        with self.assertRaisesRegex(ValueError,"accounting"):
            pair.compare_same_host(h,m)

    def test_j_max_regularization_rejected(self):
        h,m=base();h["calls"][1]["actual_original_j"]=17
        with self.assertRaisesRegex(ValueError,"regularization"):
            pair.compare_same_host(h,m)

    def test_executed_source_body_line_forgery_rejected(self):
        h,m=base();h["executed_source_branch_bodies"][0]["source_line"]+=7
        with self.assertRaisesRegex(ValueError,"source body"):
            pair.compare_same_host(h,m)

    def test_true_path_difference_preserved_not_matched_approximately(self):
        h,m=base();m["native_history_x"][3][0]+=1e-9
        r=pair.compare_same_host(h,m)
        self.assertEqual(r["first_bitwise_history_path_difference_zero_based"],3)
        self.assertGreater(r["maximum_own_path_same_record_coordinate_delta"],0)

    def test_missing_hgfx_original_history_rejected(self):
        h,m=base();h["original_native_101_iter_val"].pop()
        with self.assertRaisesRegex(ValueError,"full history"):
            pair.compare_same_host(h,m)

    def test_empty_or_nonfinite_source_vector_rejected(self):
        h,m=base();h["calls"][1]["free_x"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            pair.compare_same_host(h,m)

    def test_frozen_python_optimizer_source_catalog(self):
        import hgfx.optim.compat_quasinewton as q
        s=one.catalog_source(Path(q.__file__))
        self.assertEqual(len(s),10)
        self.assertTrue(s["INITIAL"] < s["LINESEARCH"] < s["RESET"])
        self.assertGreater(s["ARMIO_BREAK_EXECUTED"],s["LINESEARCH"])

    def test_source_catalog_rejects_changed_original_statement(self):
        import hgfx.optim.compat_quasinewton as q
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            x=Path(d)/"q.py"
            x.write_text(Path(q.__file__).read_text().replace(
                "newval = float(function(newx))","newval = float(different(newx))"))
            with self.assertRaisesRegex(ValueError,"nonunique"):
                one.catalog_source(x)


if __name__=="__main__":
    unittest.main()
