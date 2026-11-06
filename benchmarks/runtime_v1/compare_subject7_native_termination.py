#!/usr/bin/env python3
"""Unchanged-source MATLAB verbose and HGFX native-stop scientific diagnostic.

The MATLAB public fit is run twice on same MATLAB session; ONLY logging changes.
No MATLAB function is instrumented/modified. Both original scientific full-fit
sources remain 63/64 NON-PASS; a stop reason is not a parity verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from compare_fits import TOLS,numeric
from compare_trialwise import decode_tree
from fit_cohort_hgfx import FIT_FIELDS
from compare_subject7_full_fit_trajectories import load_original,compare_pair

HGFX="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB="2437f4dc241541072722a2695ddeca7b44d83dd3"
RUN="41863441006"
MARKERS={
    "tol_arg":"Converged on step size",
    "tol_grad":"Converged on gradient size",
    "max_resets":"Warning: optimization terminated because the maximum number of resets was reached.",
    "max_iter_warning":"Warning: optimization terminated because the maximum number of iterations was reached.",
}

def valid(matlab:dict,hgfx:dict,original:Path)->dict:
    summary,oldh,oldm=load_original(original)
    if (matlab.get("schema")!="perf01d-subject7-source-native-termination-matlab-v1"
            or matlab.get("status")!="AUTHOR_SIDE_VERBOSE_TERMINATION_NOT_A_SCIENCE_PASS_NO_TIMING"
            or hgfx.get("schema")!="perf01d-subject7-source-native-termination-hgfx-v1"
            or hgfx.get("status")!="AUTHOR_SIDE_DIRECT_FROZEN_OPTIMIZER_TERMINATION_NOT_SCIENTIFIC_PASS"):
        raise ValueError("Source native termination schema/status altered")
    for engine,item in (("MATLAB",matlab),("HGFX",hgfx)):
        if (item.get("frozen_hgfx_sha")!=HGFX
            or item.get("frozen_matlab_sha")!=MATLAB
            or str(item.get("original_64_fit_run_id"))!=RUN
            or item.get("original_raw_sha256")!=summary["raw_evidence_sha256"]
            or item.get("source_input_sha256")!=summary["hgfx_input_sha256"]
            or item.get("source_config_sha256")!=summary["hgfx_config_sha256"]
            or item.get("subject_index_zero_based")!=7
            or item.get("trials")!=128
            or item.get("model")!="hgf_binary"
            or item.get("observation_model")!="unitsq_sgm"):
            raise ValueError(f"{engine}: original frozen scientific identity altered")
    if (matlab.get("changed_option")!="verbose_only_false_to_true"
            or matlab.get("same_session_normal_verbose_exact_all_fields") is not True
            or matlab.get("m_files_unchanged") is not True
            or matlab.get("no_timing") is not True
            or matlab.get("n_rand_init")!=0
            or matlab.get("finite_history_slots")!=25
            or matlab.get("allocated_history_slots")!=101
            or not matlab.get("matlab_fitModel_path","").endswith("/fitModel.m")
            or not matlab.get("matlab_quasinewton_path","").endswith("/quasinewton_optim.m")):
        raise ValueError("MATLAB strict source-native verbose-only control failed")
    if not all(matlab["same_session_exact_optim_fields"].values()):
        raise ValueError("MATLAB verbose changed full optimizer output")
    if set(matlab["same_session_exact_trajectory_fields"])!=set(oldm["traj"]):
        raise ValueError("MATLAB original full trajectory inventory altered")
    if not all(matlab["same_session_exact_trajectory_fields"].values()):
        raise ValueError("MATLAB verbose changed original full trajectory")

    source_reason=matlab.get("source_native_termination")
    console=matlab.get("verbose_console","")
    observed=[code for code,message in MARKERS.items() if message in console]
    if observed!=[source_reason] or matlab.get("source_native_event_matches")!=observed:
        raise ValueError("MATLAB native console termination not uniquely supported")
    if any(message in matlab.get("normal_console","") for message in MARKERS.values()):
        raise ValueError("MATLAB supposedly quiet baseline contains a termination event")

    for entry in ("baseline_full","verbose_full"):
        full=matlab[entry]
        if not set(FIT_FIELDS).issubset(full):
            raise ValueError("MATLAB output lost original full optimizer fields")
    for field in FIT_FIELDS:
        if numeric(matlab["baseline_full"][field],matlab["verbose_full"][field],
                   *TOLS.get(field,(3e-8,3e-10)))["mismatch_count"]:
            raise ValueError(f"MATLAB verbose altered original numeric field {field}")
    for field in oldm["traj"]:
        a=np.asarray(decode_tree(matlab["baseline_traj"][field]),float)
        b=np.asarray(decode_tree(matlab["verbose_traj"][field]),float)
        if not np.array_equal(a,b,equal_nan=True):
            raise ValueError(f"MATLAB verbose altered original trialwise trajectory {field}")
    if (hgfx.get("free_indices_zero_based")!=[12,13,14]
            or hgfx.get("original_n_rand_init")!=0
            or hgfx.get("history_allocated_slots")!=101
            or hgfx.get("history_finite_slots")!=25
            or hgfx.get("source_native_termination") not in ("tol_arg","tol_grad","max_iter","max_resets")
            or hgfx.get("source_native_iterations") not in range(1,101)
            or hgfx.get("source_native_reset_count")!=0
            or set(hgfx.get("public_vs_same_source_direct_exact",{}))
                 !={"arg_min","iter_x","iter_val"}
            or not all(hgfx["public_vs_same_source_direct_exact"].values())):
        raise ValueError("Frozen HGFX optimizer native reason not reproduced by public fit")
    if not np.array_equal(np.asarray(decode_tree(hgfx["public_fitted_full"]),float),
                          np.asarray(decode_tree(hgfx["direct_fitted_free"]),float),
                          equal_nan=True):
        # The comparison must extract the same three 0-based indices.
        hf=np.asarray(decode_tree(hgfx["public_fitted_full"]),float)
        direct=np.asarray(decode_tree(hgfx["direct_fitted_free"]),float)
        if not (hf.shape==(15,) and direct.shape==(3,) and
                np.array_equal(hf[[12,13,14]],direct,equal_nan=True)):
            raise ValueError("HGFX direct native result differs from public fitted free vector")
    # Enforce source full-fit start matches the original archive for both.
    baseline=matlab["baseline_full"]
    if not np.array_equal(np.asarray(decode_tree(baseline["init"]),float),
                          np.asarray(decode_tree(oldm["optim"]["init"]),float),
                          equal_nan=True):
        raise ValueError("MATLAB initial source 15-vector changed")
    if np.asarray(decode_tree(matlab["verbose_public_fit_final"]),float).shape!=(15,):
        raise ValueError("MATLAB full transformed final vector missing")
    fresh_reference={"optim":{k:baseline[k] for k in FIT_FIELDS},
                     "traj":matlab["baseline_traj"]}
    fresh_old=compare_pair(fresh_reference,oldm)
    return {
        "schema":"perf01d-subject7-source-native-termination-pair-v1",
        "status":"AUTHOR_SIDE_NATIVE_TERMINATION_RECORDED_NO_SCIENTIFIC_FIT_PASS",
        "original_64_fit_run":RUN,
        "frozen_hgfx_sha":HGFX,
        "frozen_matlab_sha":MATLAB,
        "original_64_raw_sha256":summary["raw_evidence_sha256"],
        "subject_index_zero_based":7,
        "original_scientific_result":"63/64 NONPASS; original subject 7 mu/muhat fail",
        "matlab_source_termination_reason":source_reason,
        "hgfx_source_termination_reason":hgfx["source_native_termination"],
        "hgfx_source_iterations":hgfx["source_native_iterations"],
        "hgfx_source_resets":hgfx["source_native_reset_count"],
        "matlab_same_runner_only_verbose_flag_changed":True,
        "matlab_normal_verbose_all_outputs_exact":True,
        "hgfx_direct_vs_same_host_public_all_optimizer_states_exact":True,
        "matlab_new_default_vs_original_archive_28_field_DIAGNOSTIC_ONLY":fresh_old,
        "matlab_finite_history_slots":25,
        "hgfx_finite_history_slots":25,
        "source_terminal_buffers_duplicated_in_original_do_not_prove_reason":True,
        "limitations":[
            "MATLAB uses only source-native verbose option. No MATLAB source edited, no optimizer semantics changed.",
            "HGFX exposed original source-native stop reason through direct optimizer with exact same-process public fit record verification.",
            "MATLAB and HGFX source-native stop labels are diagnostic and not a whole-model fitting equivalence verdict.",
            "Original complete 64-subject fitting remains 63/64 NONPASS; no thresholds, seeds, starts or dataset changed.",
            "No timing, physical GPU or independent scientific peer review. PERF-01C NOT FROZEN.",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    for arg in ("matlab","hgfx","original","output"):
        parser.add_argument("--"+arg,type=Path,required=True)
    a=parser.parse_args()
    d=valid(json.loads(a.matlab.read_bytes()),
            json.loads(a.hgfx.read_bytes()),a.original)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":d["status"],
        "MATLAB":d["matlab_source_termination_reason"],
        "HGFX":d["hgfx_source_termination_reason"],
        "source_normal_verbose_exact":True,
        "new_matlab_vs_archive_failed_fields":
           d["matlab_new_default_vs_original_archive_28_field_DIAGNOSTIC_ONLY"]["mismatched_fields"],
        "original_64_fit":"63/64 NONPASS",
        "timing":"NONE",
    },sort_keys=True))

if __name__=="__main__":
    main()
