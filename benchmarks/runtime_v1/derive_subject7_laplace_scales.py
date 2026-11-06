#!/usr/bin/env python3
"""Post-hoc Laplace curvature-scale audit of SIX original same-runner public fits.

NO new MATLAB/HGFX fitting, objective probes, timings, threshold changes or
scientific identifiability verdicts. Do not confuse this fitted local Hessian
scale with an independently validated inferential uncertainty certificate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

SOURCE_RUN = "42268256755"
SOURCE_COMMIT = "331bb639dd65f3a3e2620b34f736a9b5156b8725"
REPLAY_RUN = "42268990557"
MATLAB_HASH = "2133b60ca7dcd51b85d93dfad109f715bd8fe35fa71c2bd84ff4a63cac672139"
HGFX_HASHES = {
    "SkylakeX_1": "8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2",
    "Haswell_1": "10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a",
    "Haswell_2": "10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a",
    "SkylakeX_2": "8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2",
}
MODES = tuple(HGFX_HASHES)
MATLAB_NAMES = ("MATLAB_1","MATLAB_2")
ORIGINAL_HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
ORIGINAL_MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
STATUS = "POSTHOC_LOCAL_LAPLACE_SCALE_DIAGNOSTIC_ORIGINAL_FITTING_63_OF_64_NONPASS"
OLD_TRAJ_TOLERANCE = {"rtol": 3e-8, "atol": 3e-10}

def require(yes, message):
    if not yes:
        raise ValueError(message)

def checksum(path):
    return sha256(path.read_bytes()).hexdigest()

def matrix(raw):
    arr=np.asarray(raw, dtype=np.float64)
    require(arr.shape==(3,3) and np.isfinite(arr).all(),
            "Frozen fit expected a finite full 3x3 Laplace matrix")
    return arr

def posterior_geometry(optim):
    H = matrix(optim["H"])
    Sigma = matrix(optim["Sigma"])
    # Diagnostic geometry only. No numerical threshold is turned into a PASS.
    Hs=(H+H.T)/2.
    Ss=(Sigma+Sigma.T)/2.
    eig=np.linalg.eigvalsh(Hs)
    seig=np.linalg.eigvalsh(Ss)
    sigma_diag=np.diag(Sigma)
    has_pd=bool((eig>0).all() and (seig>0).all() and (sigma_diag>0).all())
    return {
        "H":H,
        "Sigma":Sigma,
        "H_eigenvalues_ascending":eig.tolist(),
        "Sigma_eigenvalues_ascending":seig.tolist(),
        "H_symmetry_residual_max_abs":float(np.max(np.abs(H-H.T))),
        "Sigma_symmetry_residual_max_abs":float(np.max(np.abs(Sigma-Sigma.T))),
        "inverse_pair_H_Sigma_residual_max_abs":float(
            np.max(np.abs(H@Sigma-np.eye(3,dtype=np.float64)))),
        "H_2norm_condition_number":float(np.linalg.cond(H)),
        "local_H_and_Sigma_positive_definite":has_pd,
        "Sigma_diagonal_sqrt":np.sqrt(sigma_diag).tolist() if has_pd else None,
    }

def fit_record(record):
    opt=record["optim"]
    require(set(opt)=={
        "init","final","H","Sigma","Corr","trialLogLlsplit",
        "negLl","negLj","LME","decompLME","AIC","BIC","yhat","res","resAC"
    }, "Missing one of the original 15 full fitting optimizer output fields")
    final=np.asarray(opt["final"],dtype=np.float64)
    start=np.asarray(opt["init"],dtype=np.float64)
    require(final.shape==start.shape==(15,)
            and np.isfinite(final[[12,13,14]]).all()
            and np.isfinite(start[[12,13,14]]).all(),
            "Original frozen 15-parameter full optimizer fit shape/finite free values changed")
    require(float(opt["negLj"])>0 and np.isfinite(float(opt["negLj"])),
            "Original finite negative log joint missing")
    return opt,posterior_geometry(opt),final[[12,13,14]]

def derive(folder:Path, paired_path:Path):
    paired=json.loads(paired_path.read_bytes())
    require(paired.get("schema")=="perf01d-subject7-real-matched-actions-runner-matlab-hgfx-v1"
            and paired.get("status")=="AUTHOR_SIDE_SAME_RUNNER_FRESH_MATLAB_HGFX_FITS_NOT_SCIENTIFIC_PASS"
            and paired.get("original_scientific")==
                    "63/64 NONPASS; original subject-7 traj.mu and traj.muhat 4+4"
            and paired.get("original_64_fit_run_id")=="41863441006"
            and paired.get("frozen_hgfx_sha")==ORIGINAL_HGFX
            and paired.get("frozen_matlab_sha")==ORIGINAL_MATLAB
            and str(paired.get("new_matlab_run"))==SOURCE_RUN
            and str(paired.get("new_hgfx_run"))==SOURCE_RUN
            and paired.get("perf01c")=="NOT_FROZEN"
            and paired.get("independent_scientific_review")=="NOT_RECEIVED"
            and paired.get("performance_timing")=="NOT_RUN"
            and paired.get("no_original_scientific_result_overwrite") is True,
            "Original same-runner 63/64 NONPASS or review gate was rewritten")
    require(checksum(folder/"matlab_raw.json")==MATLAB_HASH==
            paired["new_matlab_raw_sha256"],
            "Fresh same-runner MATLAB source bytes/hash have changed")
    matlab_raw=json.loads((folder/"matlab_raw.json").read_bytes())
    require(matlab_raw.get("schema")=="perf01d-subject7-same-runner-matlab-v1"
            and str(matlab_raw.get("github_run_id"))==SOURCE_RUN
            and matlab_raw.get("github_sha")==SOURCE_COMMIT
            and matlab_raw.get("matlab_release")=="2026a"
            and len(matlab_raw.get("cases",[]))==2,
            "Fresh MATLAB cases/identity from source runner changed")
    ref_cases={}
    for i,name in enumerate(MATLAB_NAMES):
        c=matlab_raw["cases"][i]
        require(c.get("status")=="MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
                and c.get("n_rand_init")==0
                and c.get("start_matches_frozen_snapshot") is True
                and c.get("subject_index_zero_based")==7,
                "Source MATLAB original public fit/start not verified: "+name)
        ref_cases[name]=fit_record(c)

    require(set(paired.get("new_hgfx_raw_sha256",{}))==set(MODES)
            and set(paired.get("all_eight_fresh_matlab_hgfx_28_field_comparisons",{}))==
                {mode+"_vs_"+name for mode in MODES for name in MATLAB_NAMES},
            "Original 4x2 full 28-field complete paired inventory lost")
    hgfx_cases={}
    for name in MODES:
        path=folder/(name+"_raw.json")
        require(checksum(path)==HGFX_HASHES[name]==paired["new_hgfx_raw_sha256"][name],
                "Original HGFX raw file source SHA256 changed: "+name)
        row=json.loads(path.read_bytes())
        require(row.get("status")=="AUTHOR_SIDE_UNTIMED_COMPLETE_PUBLIC_FIT_NO_PARITY_DECISION"
                and row.get("subject_index_zero_based")==7
                and row.get("frozen_hgfx_sha")==ORIGINAL_HGFX
                and row.get("frozen_matlab_sha")==ORIGINAL_MATLAB
                and row.get("n_rand_init")==0
                and row.get("frozen_start_matches") is True
                and row.get("blas_mode_requested")==
                    ("SkylakeX" if name.startswith("SkylakeX") else "Haswell"),
                "Source HGFX original real public fit/start/BLAS mode changed: "+name)
        hgfx_cases[name]=fit_record(row)
    require(np.array_equal(ref_cases["MATLAB_1"][2],
                           ref_cases["MATLAB_2"][2]),
            "Two same-session MATLAB original public endpoints changed")
    for a,b in (("Haswell_1","Haswell_2"),("SkylakeX_1","SkylakeX_2")):
        require(np.array_equal(hgfx_cases[a][2],hgfx_cases[b][2]),
                "Frozen original same-mode endpoint is no longer exactly repeated: "+a)
    require(paired["same_source_repeated_fit"]["matlab_full_28_field"]
              ["all_serialized_binary64_equal"] is True,
            "Original MATLAB two-fit 28-field exactness changed")
    for key,name in (("hgfx_haswell_full_28_field","Haswell"),
                     ("hgfx_skylakex_full_28_field","SkylakeX")):
        require(paired["same_source_repeated_fit"][key]
                 ["all_serialized_binary64_equal"] is True,
                "Original HGFX within-mode exactness changed: "+name)

    result=[]
    for mode in MODES:
        opt,g,x=hgfx_cases[mode]
        for m in MATLAB_NAMES:
            ref_opt,ref_g,ref_x=ref_cases[m]
            k=mode+"_vs_"+m
            comparison=paired["all_eight_fresh_matlab_hgfx_28_field_comparisons"][k]
            expected=["traj.mu","traj.muhat"] if mode.startswith("SkylakeX") else [
                "traj.epsi","traj.mu","traj.muhat","traj.psi"]
            require(comparison["field_count"]==28
                    and comparison["mismatched_fields"]==expected,
                    "Original paired 28-field scientific NONPASS altered: "+k)
            for f in ("traj.mu","traj.muhat"):
                expected_n=4 if mode.startswith("SkylakeX") else 14
                require(comparison["fields"][f]["rtol"]==OLD_TRAJ_TOLERANCE["rtol"]
                        and comparison["fields"][f]["atol"]==OLD_TRAJ_TOLERANCE["atol"]
                        and comparison["fields"][f]["mismatch_count"]==expected_n,
                        "Original old trajectory tolerance/denominator changed: "+k)
            d=x-ref_x
            if ref_g["local_H_and_Sigma_positive_definite"]:
                mahalanobis=float(np.sqrt(max(0.0,float(d@ref_g["H"]@d))))
                std=np.asarray(ref_g["Sigma_diagonal_sqrt"],np.float64)
                standardised=(d/std).tolist()
            else:
                mahalanobis=None
                standardised=None
            result.append({
                "hgfx_source":mode,"matlab_source":m,
                "original_outside_tolerance_fields":comparison["mismatched_fields"],
                "original_mu_outside_tolerance_cells":comparison["fields"]["traj.mu"]["mismatch_count"],
                "original_muhat_outside_tolerance_cells":comparison["fields"]["traj.muhat"]["mismatch_count"],
                "free_parameter_deltas_hgfx_minus_matlab":d.tolist(),
                "free_parameter_euclidean_norm":float(np.linalg.norm(d)),
                "conditional_local_laplace_hessian_quadratic_distance":mahalanobis,
                "per_parameter_delta_divided_by_fitted_matlab_laplace_sigma":standardised,
                "neg_log_joint_delta_hgfx_minus_matlab":float(opt["negLj"])-float(ref_opt["negLj"]),
            })
    return {
        "schema":"perf01d-subject7-posthoc-hessian-scale-v1",
        "status":STATUS,
        "original_real_source_run":SOURCE_RUN,
        "original_real_source_sha":SOURCE_COMMIT,
        "previous_derived_run":REPLAY_RUN,
        "original_matlab_raw_sha256":MATLAB_HASH,
        "original_hgfx_raw_sha256":HGFX_HASHES,
        "source_28_field_pair_denominator":8,
        "original_unchanged_trajectory_tolerance":OLD_TRAJ_TOLERANCE,
        "source_matlab_local_laplace_geometry":{
            name:{
                k:v for k,v in ref_cases[name][1].items() if k not in ("H","Sigma")
            } for name in MATLAB_NAMES
        },
        "source_hgfx_local_laplace_geometry":{
            name:{k:v for k,v in hgfx_cases[name][1].items()
                  if k not in ("H","Sigma")} for name in MODES
        },
        "all_eight_original_full_fit_pair_scales":result,
        "original_64_fit_scientific_gate":"63/64 NONPASS; original zero-based subject7, mu/muhat",
        "independent_reviewer_verdict":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "final_performance_timing":"NOT_RUN",
        "interpretation_limits":[
            "Post-hoc descriptive geometry of already fitted local 3x3 numerical Hessian H and Laplace covariance Sigma; not a prospective case gate.",
            "Conditional local Laplace scale is NOT validated frequentist confidence, causal effect or scientific model identifiability proof.",
            "The initial complete 64-subject fit remains 63/64 NONPASS; no acceptance threshold, subject count or model was changed.",
            "Same GitHub VM does not mean matched library kernels/threads or approved timed environment.",
            "No new MATLAB/HGFX optimizer fit, GPU, runtime timing or independent reference-classification verdict."
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-six",type=Path,required=True)
    ap.add_argument("--paired",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    r=derive(args.source_six,args.paired)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    maxd=max(x["conditional_local_laplace_hessian_quadratic_distance"]
              for x in r["all_eight_original_full_fit_pair_scales"]
              if x["conditional_local_laplace_hessian_quadratic_distance"] is not None)
    print(json.dumps({"status":r["status"],"pair_count":8,
        "maximum_conditional_local_laplace_quadratic_distance":maxd,
        "original_fit":"63/64 NONPASS","independent_review":"NOT_RECEIVED",
        "performance_timing":"NOT_RUN"},sort_keys=True))

if __name__=="__main__":
    main()
