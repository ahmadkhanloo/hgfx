from __future__ import annotations

import argparse, json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from hgfx.compat import (
    hgf_ar1_config,
    hgf_binary_mab_config, hgf_ar1_mab_config,
    hgf_ar1_binary_mab_config, ehgf_ar1_binary_mab_config, uhgf_ar1_binary_mab_config,
    hgf_jget_config, ehgf_jget_config, uhgf_jget_config,
    hgf_categorical_config, hgf_categorical_norm_config, hgf_whatworld_config, hgf_whichworld_config,
    bayes_optimal_config, bayes_optimal_binary_config, bayes_optimal_categorical_config,
    bayes_optimal_whatworld_config, bayes_optimal_whichworld_config,
    rs_belief_config, rs_precision_config, rs_precision_whatworld_config, rs_surprise_config,
    squared_pe_config,
    condhalluc_obs_config, condhalluc_obs2_config, condhalluc_obs3_config,
    softmax_wld_config, softmax_mu3_wld_config, logrt_linear_whatworld_config,
)
from hgfx.models import hhmm_default_config_tree, hhmm_prior_vectors

REF="2437f4dc241541072722a2695ddeca7b44d83dd3"

def norm(x:Any)->Any:
    if x is None: return np.nan
    if isinstance(x,list): return [norm(v) for v in x]
    return x

def arr(x:Any)->np.ndarray:
    return np.asarray(norm(x),dtype=np.float64)

def check_arr(label:str,a,e)->None:
    a=arr(a)
    if isinstance(e,dict) and "values" in e and "kind" in e:
        values=arr(e["values"]).reshape(-1)
        kind=arr(e["kind"]).astype(int).reshape(-1)
        flat=a.reshape(-1)
        if flat.size!=values.size:
            raise AssertionError(f"{label}: size Python={flat.size} MATLAB={values.size}")
        finite=kind==0
        if not np.allclose(flat[finite],values[finite],rtol=0,atol=1e-14,equal_nan=False):
            bad=np.flatnonzero(~np.isclose(flat[finite],values[finite],rtol=0,atol=1e-14))[0]
            idx=np.flatnonzero(finite)[bad]
            raise AssertionError(f"{label} finite divergence at {idx}: Python={flat[idx]} MATLAB={values[idx]}")
        if not np.all(np.isnan(flat[kind==1])):
            raise AssertionError(f"{label}: MATLAB NaN positions do not match Python")
        if not np.all(np.isposinf(flat[kind==2])):
            raise AssertionError(f"{label}: MATLAB +Inf positions do not match Python")
        if not np.all(np.isneginf(flat[kind==-2])):
            raise AssertionError(f"{label}: MATLAB -Inf positions do not match Python")
        return
    e=arr(e)
    if a.shape!=e.shape:
        if a.size==e.size: e=e.reshape(a.shape)
        else: raise AssertionError(f"{label}: shape Python={a.shape} MATLAB={e.shape}")
    if not np.allclose(a,e,rtol=0,atol=1e-14,equal_nan=True):
        idx=tuple(int(i) for i in np.argwhere(~np.isclose(a,e,rtol=0,atol=1e-14,equal_nan=True))[0])
        raise AssertionError(f"{label} divergence at {idx}: Python={a[idx]} MATLAB={e[idx]}")

def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("matlab_json",type=Path); ns=ap.parse_args()
    p=json.loads(ns.matlab_json.read_text())
    assert p["metadata"]["schema_version"]=="m12-config-1"
    assert p["metadata"]["reference_commit"]==REF
    funcs:dict[str,Callable]={
        "hgf_ar1_config":hgf_ar1_config,
        "hgf_binary_mab_config":hgf_binary_mab_config,
        "hgf_ar1_mab_config":hgf_ar1_mab_config,
        "hgf_ar1_binary_mab_config":hgf_ar1_binary_mab_config,
        "ehgf_ar1_binary_mab_config":ehgf_ar1_binary_mab_config,
        "uhgf_ar1_binary_mab_config":uhgf_ar1_binary_mab_config,
        "hgf_jget_config":hgf_jget_config,
        "ehgf_jget_config":ehgf_jget_config,
        "uhgf_jget_config":uhgf_jget_config,
        "hgf_categorical_config":hgf_categorical_config,
        "hgf_categorical_norm_config":hgf_categorical_norm_config,
        "hgf_whatworld_config":hgf_whatworld_config,
        "hgf_whichworld_config":hgf_whichworld_config,
        "bayes_optimal_config":bayes_optimal_config,
        "bayes_optimal_binary_config":bayes_optimal_binary_config,
        "bayes_optimal_categorical_config":bayes_optimal_categorical_config,
        "bayes_optimal_whatworld_config":bayes_optimal_whatworld_config,
        "bayes_optimal_whichworld_config":bayes_optimal_whichworld_config,
        "rs_belief_config":rs_belief_config,
        "rs_precision_config":rs_precision_config,
        "rs_precision_whatworld_config":rs_precision_whatworld_config,
        "rs_surprise_config":rs_surprise_config,
        "squared_pe_config":squared_pe_config,
        "condhalluc_obs_config":condhalluc_obs_config,
        "condhalluc_obs2_config":condhalluc_obs2_config,
        "condhalluc_obs3_config":condhalluc_obs3_config,
        "softmax_wld_config":softmax_wld_config,
        "softmax_mu3_wld_config":softmax_mu3_wld_config,
        "logrt_linear_whatworld_config":logrt_linear_whatworld_config,
    }
    for name,fn in funcs.items():
        cfg=fn(); exp=p["configs"][name]
        check_arr(name+".priormus",cfg.priormus,exp["priormus"])
        check_arr(name+".priorsas",cfg.priorsas,exp["priorsas"])
        for key in ("n_levels","n_bandits","coupled","irregular_intervals","update_type","n_outcomes","n_states","nw","kaub","thub","predorpost"):
            if key in exp:
                got=cfg.options.get(key)
                if isinstance(exp[key],bool):
                    assert bool(got)==bool(exp[key]), f"{name}.{key}: Python={got} MATLAB={exp[key]}"
                elif isinstance(exp[key],str):
                    assert str(got)==exp[key], f"{name}.{key}: Python={got} MATLAB={exp[key]}"
                else:
                    assert np.isclose(float(got),float(exp[key])), f"{name}.{key}: Python={got} MATLAB={exp[key]}"

    mus,sas=hhmm_prior_vectors(hhmm_default_config_tree())
    exp=p["configs"]["tapas_hhmm_config"]
    check_arr("tapas_hhmm_config.priormus",mus,exp["priormus"])
    check_arr("tapas_hhmm_config.priorsas",sas,exp["priorsas"])
    assert int(exp["n_outcomes"])==2
    print("M12 complete config/prior parity: PASS")

if __name__=="__main__": main()
