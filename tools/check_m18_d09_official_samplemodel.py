#!/usr/bin/env python3
"""Validate official MATLAB D09 sampleModel demo calls with exported random drivers."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
import numpy as np
from hgfx.compat import hgf_binary_config, sample_model, unitsq_sgm_config

REFERENCE_COMMIT="2437f4dc241541072722a2695ddeca7b44d83dd3"
PROTOCOL="m18-d09-official-samplemodel-1"
RTOL=3e-10
ATOL=3e-12

def norm(v:Any)->Any:
    if v is None: return np.nan
    if isinstance(v,list): return [norm(x) for x in v]
    return v

def arr(v:Any)->np.ndarray: return np.asarray(norm(v),dtype=np.float64)

def compare(label:str,actual:Any,expected:Any):
    a=arr(actual); e=arr(expected)
    if a.shape!=e.shape:
        if a.size==e.size: e=e.reshape(a.shape)
        else: return {"label":label,"pass":False,"reason":"shape","actual_shape":list(a.shape),"expected_shape":list(e.shape)}
    close=np.isclose(a,e,rtol=RTOL,atol=ATOL,equal_nan=True)
    if np.all(close):
        diff=np.abs(a-e); finite=np.isfinite(diff)
        return {"label":label,"pass":True,"max_abs":float(np.max(diff[finite])) if np.any(finite) else 0.0}
    idx=tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    return {"label":label,"pass":False,"index":list(idx),"hgfx":float(a[idx]) if idx else float(a),"matlab":float(e[idx]) if idx else float(e),"abs_diff":float(abs((a[idx] if idx else a)-(e[idx] if idx else e)))}

def main(reference_path:Path,output_path:Path)->int:
    ref=json.loads(reference_path.read_text())
    if ref.get("protocol")!=PROTOCOL or ref.get("reference_commit")!=REFERENCE_COMMIT: raise ValueError("Frozen D09 protocol/reference mismatch")
    if [int(x) for x in ref.get("seeds",[])]!=[123,456]: raise ValueError("Frozen D09 seeds mismatch")
    inputs=arr(ref["inputs"]).reshape(-1); results=[]; failures=[]
    for case in ref.get("cases",[]):
        seed=int(case["seed"]); z_prc=arr(case["prc_standard_normals"]).reshape(-1); z_obs=arr(case["obs_standard_normals"]).reshape(-1)
        result=sample_model(inputs,hgf_binary_config(),unitsq_sgm_config(),seed=seed,perceptual_standard_normals=z_prc,observation_standard_normals=z_obs,response_uniforms=np.linspace(.03,.97,inputs.size))
        checks=[]
        checks.append(compare("p_prc_trans",result.perceptual_transformed_parameters,case["p_prc_trans"]))
        checks.append(compare("p_prc",result.perceptual_parameters,case["p_prc"]))
        checks.append(compare("p_obs_trans",result.observation_transformed_parameters,case["p_obs_trans"]))
        checks.append(compare("p_obs",result.observation_parameters,case["p_obs"]))
        expected_traj=case["traj"]
        missing=[]
        for field,expected in expected_traj.items():
            if field not in result.trajectory:
                missing.append(field); checks.append({"label":f"traj.{field}","pass":False,"reason":"missing_field"})
            else:
                checks.append(compare(f"traj.{field}",result.trajectory[field],expected))
        matlab_ignored=tuple(int(x)-1 for x in arr(case.get("ignored_matlab",[])).reshape(-1))
        semantics_pass=(result.ignored_trials==matlab_ignored and result.seed==seed and int(np.asarray(case["c_sim_seed"]).reshape(-1)[0])==seed)
        checks.append({"label":"result_semantics","pass":semantics_pass,"hgfx_ignored":list(result.ignored_trials),"matlab_ignored":list(matlab_ignored),"seed":seed})
        case_pass=all(bool(c["pass"]) for c in checks)
        if not case_pass: failures.extend([{"seed":seed,**c} for c in checks if not c["pass"]])
        results.append({"seed":seed,"pass":case_pass,"checks":checks,"matlab_response_shape":list(arr(case["responses"]).shape),"response_equality_gated":False})
    if len(results)!=2: classification="INSUFFICIENT_REFERENCE_EVIDENCE"
    elif failures: classification="IMPLEMENTATION_MISMATCH"
    else: classification="PASS"
    out={"protocol":PROTOCOL,"reference_commit":REFERENCE_COMMIT,"classification":classification,"tolerance":{"rtol":RTOL,"atol":ATOL},"cases":results,"failures":failures,"rng_note":"Cross-runtime parameter sampling uses exact MATLAB-exported standard-normal drivers; MATLAB response RNG bytes are not equality-gated."}
    output_path.parent.mkdir(parents=True,exist_ok=True); output_path.write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps({"classification":classification,"failures":failures[:3]}),flush=True)
    return 0 if classification=="PASS" else 2

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("reference",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); raise SystemExit(main(a.reference,a.output))
