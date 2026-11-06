"""PERF-01D crossed same-vector forward negative controls; no new science gate."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))

from compare_subject7_crossed_forward import (
    ANCHORS, FIELDS, RTOL, ATOL, SOURCE,
    RAW, HGFX_SHA, MATLAB_SHA, mismatch_points, compare_traj, verify_raw,
)


def p():
    return {k:np.asarray([None,0.,1.,None,-2.3025850929940455,0.,None,
             0.,0.,0.,0.,None,-8.,-6.,1.]).astype(float) for k in ANCHORS}


def report(engine):
    params=p()
    vectors=list(params.values())
    rows=[]
    for name,v in zip(ANCHORS,vectors):
        rows.append({
            "origin":name,
            "status":"EVALUATED_IDENTICAL_FROZEN_VECTOR_"+engine.upper(),
            "full_transformed_vector":[x if np.isfinite(x) else None for x in v],
            "traj":{k:[[0.,0.,0.] for _ in range(128)] for k in FIELDS},
            "inf_states":[[[0.]*4 for _ in range(3)] for _ in range(128)],
        })
    return {
        "schema":"perf01d-subject7-crossed-forward-"+engine+"-v1",
        "status":"SAME_VECTOR_FORWARD_DIAGNOSTIC_NO_FULL_FIT_NO_TIMING_NO_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "source_run_id":SOURCE,
        "original_raw_sha256":RAW if engine=="hgfx" else {
            "hgfx_raw_json":RAW["hgfx_raw.json"],
            "matlab_raw_json":RAW["matlab_raw.json"]},
        "source_input_sha256":"unmodified-input",
        "source_config_sha256":"unmodified-config",
        "subject_index_zero_based":7,
        "trials":128,
        "model":"hgf_binary",
        "perceptual_parameter_count":14,
        "observation_parameter_count":1,
        "free_indices_zero_based":[12,13,14],
        "anchor_origins":list(ANCHORS),
        "original_endpoints_unmodified":True,
        "cases":rows,
    }


def summary():
    return {"raw_evidence_sha256":RAW,
            "hgfx_input_sha256":"unmodified-input",
            "hgfx_config_sha256":"unmodified-config"}


class TestCrossedSameVectorForward(unittest.TestCase):
    def test_source_sha_and_three_anchors_fixed(self):
        self.assertEqual(len(ANCHORS),3)
        self.assertEqual(len(FIELDS),11)
        self.assertEqual((RTOL,ATOL),(3e-8,3e-10))
        self.assertEqual(SOURCE,"41863441006")

    def test_complete_valid_three_cases(self):
        for engine in ("hgfx","matlab"):
            actual=verify_raw(report(engine),engine,summary(),p())
            self.assertEqual(set(actual),set(ANCHORS))

    def test_traj_numeric_within_original_tolerance(self):
        a=report("hgfx")["cases"][0]["traj"]
        b=deepcopy(a)
        d=compare_traj(a,b)
        self.assertEqual(d["field_count"],11)
        self.assertEqual(d["mismatched_fields"],[])
        self.assertIn("DIAGNOSTIC_ONLY",d["status"])

    def test_original_small_near_zero_failure(self):
        a=report("hgfx")["cases"][0]["traj"]
        b=deepcopy(a)
        a["mu"][83][1]=7.8e-10
        a["muhat"][84][1]=7.8e-10
        d=compare_traj(a,b)
        self.assertEqual(d["mismatched_fields"],["mu","muhat"])
        self.assertEqual(d["critical_coordinates"]["mu"][0]["trial_one_based"],84)
        self.assertEqual(d["critical_coordinates"]["muhat"][0]["trial_one_based"],85)

    def test_index_inventory_no_exclusion(self):
        a=report("hgfx")["cases"][0]["traj"]
        b=deepcopy(a)
        for i in (83,108,116,126):
            a["mu"][i][1]=9e-10
        delta=mismatch_points(a["mu"],b["mu"])
        self.assertEqual([x["trial_one_based"] for x in delta],[84,109,117,127])

    def test_wrong_engine_origin_is_rejected(self):
        r=report("matlab")
        r["cases"][2]["origin"]=r["cases"][1]["origin"]
        with self.assertRaisesRegex(ValueError,"denominator"):
            verify_raw(r,"matlab",summary(),p())

    def test_changed_original_vector_is_rejected(self):
        r=report("hgfx")
        r["cases"][0]["full_transformed_vector"][12]=-999.
        with self.assertRaisesRegex(ValueError,"original transformed"):
            verify_raw(r,"hgfx",summary(),p())

    def test_original_sha_tamper_is_rejected(self):
        r=report("hgfx")
        r["original_raw_sha256"]["hgfx_raw.json"]="changed"
        with self.assertRaisesRegex(ValueError,"Unverified"):
            verify_raw(r,"hgfx",summary(),p())

    def test_missing_traj_field_is_rejected(self):
        a=report("hgfx")["cases"][0]["traj"]
        b=deepcopy(a)
        del a["muhat"]
        with self.assertRaisesRegex(ValueError,"inventory"):
            compare_traj(a,b)

    def test_duplicate_anchor_rejected(self):
        r=report("hgfx")
        r["cases"].append(deepcopy(r["cases"][1]))
        with self.assertRaisesRegex(ValueError,"denominator"):
            verify_raw(r,"hgfx",summary(),p())

    def test_parity_would_not_be_full_fit_pass(self):
        self.assertIn("NO_FULL_FIT",report("hgfx")["status"])
        self.assertIn("NO_SCIENTIFIC_PASS",report("hgfx")["status"])


if __name__=="__main__":
    unittest.main()
