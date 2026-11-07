"""PERF-01D prospective same-runner scientific probes; negative controls only."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
from compare_subject7_same_runner_matlab_hgfx import (
    REF_ORDER, ORDER, STATUS, MATLAB_SCHEMA,
    validate_matlab, full_history_pair, validate_hgfx,
)
from test_perf01_subject7_full_trajectory import full_row, new_case, summary

RUN="42299999999"
SHA="a"*40
def fixture():
    base=full_row()
    raw=deepcopy(base)
    raw.update({
        "subject_index_zero_based":7, "n_trials":128,
        "model":"hgf_binary","observation":"unitsq_sgm",
        "status":"MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION",
        "n_rand_init":0,"start_matches_frozen_snapshot":True,
        "console_characters":80,
        "optimizer_iteration_count":101,
        "finite_optimizer_history_slots":25,
        "optimizer_history":{
            "val":[0.0]*25+[None]*76,
            "x":[[0.0,0.0,0.0] for _ in range(101)],
        },
    })
    data={
        "schema":MATLAB_SCHEMA,
        "status":"AUTHOR_SIDE_UNTIMED_FROZEN_MATLAB_TWO_PUBLIC_FITS_NO_PARITY_DECISION",
        "frozen_hgfx_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "frozen_matlab_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "original_64_fit_run":"41863441006",
        "original_64_raw_sha256":summary()["raw_evidence_sha256"],
        "original_63_64_nonpass":True,
        "original_subject_index_zero_based":7,
        "source_input_sha256":"input-h",
        "source_config_sha256":"config-h",
        "matlab_release":"2026a","matlab_version":"9.x",
        "matlab_fitModel_resolved_path":"/runner/matlab-reference/core/fitModel.m",
        "matlab_hgf_binary_resolved_path":"/runner/matlab-reference/models/hgf_binary.m",
        "runner_name":"test-runner","machine_arch":"glnxa64",
        "github_run_id":RUN,"github_sha":SHA,
        "no_timing":True,"no_scientific_gate_promotion":True,
        "fit_order":list(REF_ORDER),
        "cases":[deepcopy(raw),deepcopy(raw)],
    }
    return data,base

class SameRunnerPublicFitControls(unittest.TestCase):
    def test_original_four_modes_two_matlab_predeclared(self):
        self.assertEqual(ORDER,("SkylakeX_1","Haswell_1","Haswell_2","SkylakeX_2"))
        self.assertEqual(REF_ORDER,("MATLAB_1","MATLAB_2"))
        self.assertIn("NOT_SCIENTIFIC_PASS",STATUS)

    def test_two_complete_matlab_full_fits_and_history_accepted(self):
        x,old=fixture()
        rows=validate_matlab(x,summary(),old,RUN,SHA)
        self.assertEqual(len(rows),2)
        self.assertTrue(full_history_pair(*rows)["val"]["serialized_binary64_equal"])
        self.assertTrue(full_history_pair(*rows)["x"]["serialized_binary64_equal"])

    def test_missing_matlab_replication_rejected(self):
        x,old=fixture()
        x["cases"].pop()
        with self.assertRaisesRegex(ValueError,"Two predeclared"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_mutated_matlab_original_start_rejected(self):
        x,old=fixture()
        x["cases"][1]["optim"]["init"][12]=-2.
        with self.assertRaisesRegex(ValueError,"start changed"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_hidden_matlab_console_side_effect_rejected(self):
        x,old=fixture()
        x["cases"][0]["console_characters"]=0
        with self.assertRaisesRegex(ValueError,"stdout"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_matlab_json_normalized_both_historical_raw_hash_keys(self):
        x,old=fixture()
        x["original_64_raw_sha256"]={
            "hgfx_raw_json":"frozen-h","matlab_raw_json":"frozen-m"}
        self.assertEqual(len(validate_matlab(x,summary(),old,RUN,SHA)),2)

    def test_matlab_json_unexpected_raw_hash_key_rejected(self):
        x,old=fixture()
        x["original_64_raw_sha256"]={
            "hgfx_raw_json":"frozen-h","matlab_raw_json":"frozen-m","extra":"untrusted"}
        with self.assertRaisesRegex(ValueError,"provenance changed"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_forged_reference_sha_rejected(self):
        x,old=fixture()
        x["frozen_matlab_sha"]="0"*40
        with self.assertRaisesRegex(ValueError,"provenance changed"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_mismatched_runner_rejected(self):
        x,old=fixture()
        x["github_run_id"]="UNRELATED"
        with self.assertRaisesRegex(ValueError,"provenance changed"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_missing_one_matlab_trajectory_rejected(self):
        x,old=fixture()
        del x["cases"][1]["traj"]["muhat"]
        with self.assertRaisesRegex(ValueError,"inventory"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_missing_finite_history_slot_rejected(self):
        x,old=fixture()
        x["cases"][0]["optimizer_history"]["val"][24]=None
        with self.assertRaisesRegex(ValueError,"history"):
            validate_matlab(x,summary(),old,RUN,SHA)

    def test_matlab_history_non_bitwise_difference_reported_not_suppressed(self):
        x,_=fixture()
        x["cases"][1]["optimizer_history"]["x"][10][1]=1e-15
        r=full_history_pair(*x["cases"])
        self.assertFalse(r["x"]["serialized_binary64_equal"])
        self.assertEqual(r["x"]["differing_serialized_binary64_values"],1)

    def test_both_predeclared_hgfx_modes_use_unchanged_old_start(self):
        old=full_row()
        a=new_case("auto");a["blas_mode_requested"]="SkylakeX"
        b=new_case("Haswell")
        self.assertEqual(validate_hgfx(a,"SkylakeX",summary(),old)["n_rand_init"],0)
        self.assertEqual(validate_hgfx(b,"Haswell",summary(),old)["n_rand_init"],0)

    def test_hgfx_mode_substitution_rejected(self):
        with self.assertRaisesRegex(ValueError,"explicit-coretype"):
            validate_hgfx(new_case("auto"),"SkylakeX",summary(),full_row())

if __name__=="__main__":
    unittest.main()
