from __future__ import annotations

import argparse, json
from pathlib import Path
from typing import Any
import numpy as np

from hgfx.responses import (
    bayes_optimal, bayes_optimal_binary, bayes_optimal_categorical,
    bayes_optimal_whatworld, bayes_optimal_whichworld,
    squared_pe, rs_belief, rs_precision, rs_precision_whatworld, rs_surprise,
    condhalluc_obs, condhalluc_obs2, condhalluc_obs3,
    softmax_wld, softmax_mu3_wld, logrt_linear_whatworld,
)

RTOL=2e-10
ATOL=2e-12
REF="2437f4dc241541072722a2695ddeca7b44d83dd3"

def norm(x:Any)->Any:
    if x is None: return np.nan
    if isinstance(x,list): return [norm(v) for v in x]
    return x

def arr(x:Any)->np.ndarray:
    return np.asarray(norm(x),dtype=np.float64)

def check(label:str,got,exp)->None:
    a=arr(got); e=arr(exp)
    if a.shape!=e.shape:
        if a.size==e.size: e=e.reshape(a.shape)
        else: raise AssertionError(f"{label} shape Python={a.shape} MATLAB={e.shape}")
    ok=np.isclose(a,e,rtol=RTOL,atol=ATOL,equal_nan=True)
    if np.all(ok): return
    idx=tuple(int(i) for i in np.argwhere(~ok)[0]) if np.ndim(ok) else ()
    av=float(a[idx]) if idx else float(a); ev=float(e[idx]) if idx else float(e)
    raise AssertionError(f"{label} divergence at {idx}: MATLAB={ev:.17g} Python={av:.17g} abs={abs(av-ev):.3e}")

def compare(label:str,got,exp:dict[str,Any])->None:
    for key,value in zip(("logp","yhat","res"),got,strict=True):
        check(f"{label}.{key}",value,exp[key])

FAILURES: list[str] = []

def record(label:str,got,exp:dict[str,Any])->None:
    try:
        compare(label, got, exp)
    except AssertionError as exc:
        FAILURES.append(str(exc))

def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("matlab_json",type=Path); ns=ap.parse_args()
    p=json.loads(ns.matlab_json.read_text(encoding="utf-8"))
    assert p["metadata"]["schema_version"]=="m12fg-1"
    assert p["metadata"]["reference_commit"]==REF
    irr=[2]; n=8
    u=np.array([0,1,0,1,1,0,1,0],dtype=np.float64)
    y=np.array([.011,.012,.013,.014,.015,.016,.017,.018],dtype=np.float64)
    base=np.full((n,3,4),np.nan,dtype=np.float64)
    base[:,0,0]=np.linspace(.2,.8,n); base[:,0,1]=np.linspace(.15,.25,n)
    base[:,1,0]=np.linspace(-1,1,n); base[:,1,1]=np.linspace(.3,.5,n)
    base[:,2,0]=np.linspace(-2,1,n); base[:,2,1]=np.linspace(.4,.7,n)

    record("bayes_optimal",bayes_optimal(u,base,irregular_trials=irr),p["bayes_optimal"])
    record("bayes_optimal_binary",bayes_optimal_binary(u,base,irregular_trials=irr),p["bayes_optimal_binary"])
    record("squared_pe",squared_pe(u,base,[np.log(.2)],irregular_trials=irr),p["squared_pe"])
    prs=np.log([.0052,.0052,.0006,.001])
    record("rs_belief",rs_belief(y,u,base,prs,irregular_trials=irr),p["rs_belief"])
    record("rs_precision",rs_precision(y,u,base,prs,irregular_trials=irr),p["rs_precision"])
    record("rs_surprise",rs_surprise(y,u,base,prs,irregular_trials=irr),p["rs_surprise"])

    cat=np.zeros((n,1,3,1),dtype=np.float64); cat[:,0,:,0]=[.2,.3,.5]
    cu=np.array([1,2,3,1,3,2,1,3],dtype=np.float64)
    record("bayes_optimal_categorical",bayes_optimal_categorical(cu,cat,irregular_trials=irr),p["bayes_optimal_categorical"])

    wwh=np.zeros((n,1,4,1,1),dtype=np.float64); wwh[:,0,:,0,0]=[.1,.2,.3,.4]
    record("bayes_optimal_whichworld",bayes_optimal_whichworld(u,wwh,irregular_trials=irr),p["bayes_optimal_whichworld"])

    ns2=2
    wht=np.full((n,2,ns2,ns2,1,2),np.nan,dtype=np.float64)
    wht[:,0,:,:,0,0]=np.array([[.7,.4],[.3,.6]])
    wht[:,0,:,:,0,1]=np.array([[.2,.3],[.25,.35]])
    wht[:,1,:,:,0,0]=np.array([[.5,-.5],[.7,-.7]])
    wu=np.array([1,2,1,2,2,1,2,1],dtype=np.float64)
    record("bayes_optimal_whatworld",bayes_optimal_whatworld(wu,wht,n_states=2,irregular_trials=irr),p["bayes_optimal_whatworld"])
    record("rs_precision_whatworld",rs_precision_whatworld(y,wu,wht,np.log([.0052,.0006,.001]),n_states=2,irregular_trials=irr),p["rs_precision_whatworld"])

    ch=np.column_stack((u,np.array([0,.25,.5,.75,0,.25,.5,.75],dtype=np.float64)))
    yr=np.array([0,1,1,0,1,0,1,1],dtype=np.float64)
    record("condhalluc_obs",condhalluc_obs(yr,ch,base,[np.log(48)],irregular_trials=irr),p["condhalluc_obs"])
    record("condhalluc_obs2",condhalluc_obs2(yr,ch,base,[np.log(48),0],irregular_trials=irr),p["condhalluc_obs2"])
    record("condhalluc_obs3",condhalluc_obs3(yr,ch,base,[np.log(48)],irregular_trials=irr),p["condhalluc_obs3"])

    nc=3
    sw=np.full((n,3,nc,4),np.nan,dtype=np.float64)
    for k in range(n):
        sw[k,0,:,0]=np.array([.2,.5,.3])+.01*(k+1)
        sw[k,0,:,2]=np.array([.25,.45,.30])+.01*(k+1)
        sw[k,2,0,2]=-1+.1*(k+1)
    choices=np.array([1,2,3,1,2,3,1,2],dtype=np.float64)
    world_inputs=np.column_stack((u,choices))
    record("softmax_wld",softmax_wld(choices,world_inputs,sw,[np.log(1.3),.2,-.1],irregular_trials=irr,predorpost=1),p["softmax_wld"])
    record("softmax_mu3_wld",softmax_mu3_wld(choices,world_inputs,sw,[.2,-.1],irregular_trials=irr,predorpost=1),p["softmax_mu3_wld"])

    lrt=np.full((n,3,2,2,4),np.nan,dtype=np.float64)
    for k in range(n):
        lrt[k,0,:,:,0]=np.array([[.7,.4],[.3,.6]])
        lrt[k,0,:,:,2]=np.array([[1,0],[0,0]]) if (k+1)%2 else np.array([[0,0],[1,0]])
        lrt[k,1,:,:,2]=np.array([[.4,-.4],[.6,-.6]])
        lrt[k,1,:,:,3]=np.array([[.25,.3],[.35,.4]])
        lrt[k,2,0,0,2]=-1+.05*(k+1)
    logy=np.log(np.array([500,520,510,530,540,525,535,515],dtype=np.float64))
    record("logrt_linear_whatworld",logrt_linear_whatworld(logy,wu,lrt,[np.log(500),.1,-.05,.02,np.log(.2)],irregular_trials=irr),p["logrt_linear_whatworld"])
    if FAILURES:
        raise AssertionError("M12F/G parity failures:\\n" + "\\n".join(FAILURES))
    print("M12F/G MATLAB/Python parity: PASS")

if __name__=="__main__": main()
