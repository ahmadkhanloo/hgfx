from __future__ import annotations

import argparse, json
from pathlib import Path
from typing import Any
import numpy as np

from hgfx.models import (
    hgf_categorical, hgf_categorical_norm, hgf_whatworld, hgf_whichworld,
    hhmm_default_config_tree, hhmm_prior_vectors, hierarchical_hidden_markov_model,
)

RTOL=2e-9
ATOL=2e-11
REF="2437f4dc241541072722a2695ddeca7b44d83dd3"

def norm(x:Any)->Any:
    if x is None: return np.nan
    if isinstance(x,list): return [norm(v) for v in x]
    return x

def arr(x:Any)->np.ndarray:
    return np.asarray(norm(x),dtype=np.float64)

def check(label:str,a,e)->None:
    a=arr(a); e=arr(e)
    if a.shape!=e.shape:
        if a.size==e.size: e=e.reshape(a.shape)
        else: raise AssertionError(f"{label} shape Python={a.shape} MATLAB={e.shape}")
    ok=np.isclose(a,e,rtol=RTOL,atol=ATOL,equal_nan=True)
    if np.all(ok): return
    idx=tuple(int(i) for i in np.argwhere(~ok)[0]) if np.ndim(ok) else ()
    av=float(a[idx]) if idx else float(a); ev=float(e[idx]) if idx else float(e)
    raise AssertionError(f"{label} divergence at {idx}: MATLAB={ev:.17g} Python={av:.17g} abs={abs(av-ev):.3e}")

def compare(label:str,got,exp):
    traj,inf=got
    check(label+".infStates",inf,exp["infStates"])
    for field,value in exp["traj"].items():
        if field not in traj: raise AssertionError(f"{label} missing {field}")
        check(label+".traj."+field,traj[field],value)

def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("matlab_json",type=Path); ns=ap.parse_args()
    p=json.loads(ns.matlab_json.read_text())
    assert p["metadata"]["schema_version"]=="m12de-1"
    assert p["metadata"]["reference_commit"]==REF
    cases=p["cases"]; irr=[2]

    u=np.array([1,2,3,2,1,3,3,1],dtype=np.float64)
    l3=np.log((1/3)/(2/3))
    pc=np.array([l3,l3,l3,1,1,1,1,.1,1,-4,.05],dtype=np.float64)
    compare("hgf_categorical",hgf_categorical(u,pc,n_outcomes=3,ignored_trials=irr),cases["hgf_categorical"])
    compare("hgf_categorical_norm",hgf_categorical_norm(u,pc,n_outcomes=3,ignored_trials=irr),cases["hgf_categorical_norm"])

    uw=np.array([1,2,2,1,2,1,1,2],dtype=np.float64)
    pw=np.array([0,0,0,0,1,1,1,1,1,.1,1,-4,.05],dtype=np.float64)
    compare("hgf_whatworld",hgf_whatworld(uw,pw,n_states=2,ignored_trials=irr),cases["hgf_whatworld"])

    ub=np.array([0,1,1,0,1,0,0,1],dtype=np.float64)
    pwhich=np.array([0,0,1,1,1,.1,1,-4,.05,0,.1],dtype=np.float64)
    compare("hgf_whichworld",hgf_whichworld(ub,pwhich,n_worlds=2,ignored_trials=irr),cases["hgf_whichworld"])

    tree=hhmm_default_config_tree()
    ptrans,_=hhmm_prior_vectors(tree)
    compare("tapas_hhmm",hierarchical_hidden_markov_model(
        np.array([1,2,1,2,2,1,1,2],dtype=np.float64),
        ptrans, tree_config=tree, transformed=True, ignored_trials=irr
    ),cases["tapas_hhmm"])
    print("M12D/E MATLAB/Python parity: PASS")

if __name__=="__main__": main()
