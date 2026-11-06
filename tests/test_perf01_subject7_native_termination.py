"""PERF-01D original optimizer native-stop evidence negative controls (NO science PASS)."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from unittest import TestCase,main
from unittest.mock import patch
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
import compare_subject7_native_termination as native
from fit_cohort_hgfx import FIT_FIELDS


def scientific():
    optim={name:0. for name in FIT_FIELDS}
    optim["init"]=[None]*12+[-3.,-6.,3.871201010907891]
    optim["final"]=[None]*12+[-8.22346,-5.98,3.76]
    optim["decompLME"]={"logjoint":0.,"postpredcorr":0.,"freepars":0.}
    traj={name:[[0.]*(2 if name=="w" else 3) for _ in range(128)]
          for name in ("mu","muhat","sa","sahat","da","epsi","psi",
                        "ud","v","w","wt")}
    original={"optim":optim,"traj":traj}
    summary={"raw_evidence_sha256":{"hgfx_raw.json":"original-h",
                                    "matlab_raw.json":"original-m"},
             "hgfx_input_sha256":"input0",
             "hgfx_config_sha256":"config0"}
    return original,summary


def raw():
    old,summary=scientific()
    matlab={
        "schema":"perf01d-subject7-source-native-termination-matlab-v1",
        "status":"AUTHOR_SIDE_VERBOSE_TERMINATION_NOT_A_SCIENCE_PASS_NO_TIMING",
        "frozen_hgfx_sha":native.HGFX,
        "frozen_matlab_sha":native.MATLAB,
        "original_64_fit_run_id":native.RUN,
        "original_raw_sha256":dict(summary["raw_evidence_sha256"]),
        "source_input_sha256":"input0",
        "source_config_sha256":"config0",
        "subject_index_zero_based":7,
        "trials":128,
        "model":"hgf_binary",
        "observation_model":"unitsq_sgm",
        "changed_option":"verbose_only_false_to_true",
        "same_session_normal_verbose_exact_all_fields":True,
        "m_files_unchanged":True,"no_timing":True,
        "n_rand_init":0,"finite_history_slots":25,
        "allocated_history_slots":101,
        "matlab_fitModel_path":"/repo/core/fitModel.m",
        "matlab_quasinewton_path":"/repo/core/quasinewton_optim.m",
        "same_session_exact_optim_fields":{name:True for name in FIT_FIELDS},
        "same_session_exact_trajectory_fields":{name:True for name in old["traj"]},
        "source_native_termination":"tol_arg",
        "source_native_event_matches":["tol_arg"],
        "normal_console":"Results:",
        "verbose_console":"Optimizing...\nConverged on step size\nResults:",
        "baseline_full":deepcopy(old["optim"]),
        "verbose_full":deepcopy(old["optim"]),
        "baseline_traj":deepcopy(old["traj"]),
        "verbose_traj":deepcopy(old["traj"]),
        "verbose_public_fit_final":list(old["optim"]["final"]),
    }
    hgfx={
        "schema":"perf01d-subject7-source-native-termination-hgfx-v1",
        "status":"AUTHOR_SIDE_DIRECT_FROZEN_OPTIMIZER_TERMINATION_NOT_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":native.HGFX,
        "frozen_matlab_sha":native.MATLAB,
        "original_64_fit_run_id":native.RUN,
        "original_raw_sha256":dict(summary["raw_evidence_sha256"]),
        "source_input_sha256":"input0","source_config_sha256":"config0",
        "subject_index_zero_based":7,"trials":128,
        "model":"hgf_binary","observation_model":"unitsq_sgm",
        "free_indices_zero_based":[12,13,14],
        "original_n_rand_init":0,
        "history_allocated_slots":101,
        "history_finite_slots":25,
        "source_native_termination":"tol_arg",
        "source_native_iterations":24,
        "source_native_reset_count":0,
        "public_vs_same_source_direct_exact":{
            "arg_min":True,"iter_x":True,"iter_val":True},
        "public_fitted_full":list(old["optim"]["final"]),
        "direct_fitted_free":list(old["optim"]["final"][12:15]),
    }
    return matlab,hgfx,summary,old


class TestOriginalNativeStop(TestCase):
    def evaluate(self,matlab,hgfx,summary,old):
        with patch.object(native,"load_original",return_value=(summary,old,old)):
            return native.valid(matlab,hgfx,Path("no-io-mocked"))

    def test_frozen_original_schema_fails_safe_no_promotion(self):
        a,b,s,o=raw()
        report=self.evaluate(a,b,s,o)
        self.assertIn("NO_SCIENTIFIC_FIT_PASS",report["status"])
        self.assertIn("63/64",report["original_scientific_result"])
        self.assertTrue(report["matlab_normal_verbose_all_outputs_exact"])

    def test_matlab_native_step_marker(self):
        a,b,s,o=raw()
        self.assertEqual(self.evaluate(a,b,s,o)["matlab_source_termination_reason"],"tol_arg")

    def test_matlab_native_gradient_marker(self):
        a,b,s,o=raw()
        a["source_native_termination"]="tol_grad"
        a["source_native_event_matches"]=["tol_grad"]
        a["verbose_console"]="Converged on gradient size"
        self.assertEqual(self.evaluate(a,b,s,o)["matlab_source_termination_reason"],"tol_grad")

    def test_missing_matlab_native_reason_rejected(self):
        a,b,s,o=raw()
        a["verbose_console"]="Results:\n no optimizer status"
        with self.assertRaisesRegex(ValueError,"termination"):
            self.evaluate(a,b,s,o)

    def test_ambiguous_matlab_native_stop_rejected(self):
        a,b,s,o=raw()
        a["verbose_console"]+="\nConverged on gradient size"
        with self.assertRaisesRegex(ValueError,"termination"):
            self.evaluate(a,b,s,o)

    def test_changed_verbose_fit_outputs_rejected(self):
        a,b,s,o=raw()
        a["verbose_full"]["final"][-1]+=1e-5
        with self.assertRaisesRegex(ValueError,"numeric field"):
            self.evaluate(a,b,s,o)

    def test_changed_trajectory_rejected_even_when_flags_claim_exact(self):
        a,b,s,o=raw()
        a["verbose_traj"]["mu"][83][1]+=1e-8
        with self.assertRaisesRegex(ValueError,"trajectory"):
            self.evaluate(a,b,s,o)

    def test_native_hgfx_direct_mismatch_rejected(self):
        a,b,s,o=raw()
        b["public_vs_same_source_direct_exact"]["arg_min"]=False
        with self.assertRaisesRegex(ValueError,"optimizer native"):
            self.evaluate(a,b,s,o)

    def test_wrong_source_original_sha_rejected(self):
        a,b,s,o=raw()
        b["original_raw_sha256"]["hgfx_raw.json"]="altered"
        with self.assertRaisesRegex(ValueError,"identity"):
            self.evaluate(a,b,s,o)

    def test_wrong_experiment_subject_rejected(self):
        a,b,s,o=raw()
        a["subject_index_zero_based"]=6
        with self.assertRaisesRegex(ValueError,"identity"):
            self.evaluate(a,b,s,o)

    def test_hgfx_wrong_free_coordinates_rejected(self):
        a,b,s,o=raw()
        b["free_indices_zero_based"]=[11,12,14]
        with self.assertRaisesRegex(ValueError,"optimizer native"):
            self.evaluate(a,b,s,o)

    def test_nonquiet_matlab_reference_flag_rejected(self):
        a,b,s,o=raw()
        a["normal_console"]="Converged on step size"
        with self.assertRaisesRegex(ValueError,"quiet baseline"):
            self.evaluate(a,b,s,o)


    def test_matlab_json_normalized_source_sha_fields_accepted(self):
        a,b,s,o=raw()
        a["original_raw_sha256"]={
            k.replace("_raw.json","_raw_json"):v
            for k,v in a["original_raw_sha256"].items()}
        result=self.evaluate(a,b,s,o)
        self.assertEqual(result["matlab_source_termination_reason"],"tol_arg")

    def test_matlab_json_normalized_sha_tamper_rejected(self):
        a,b,s,o=raw()
        a["original_raw_sha256"]={
            k.replace("_raw.json","_raw_json"):v
            for k,v in a["original_raw_sha256"].items()}
        a["original_raw_sha256"]["hgfx_raw_json"]="altered"
        with self.assertRaisesRegex(ValueError,"identity"):
            self.evaluate(a,b,s,o)



if __name__=="__main__":
    main()
