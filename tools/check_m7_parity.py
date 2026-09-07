from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
import numpy as np
from hgfx.responses import (
 beta_obs,cdfgaussian_obs,gaussian_obs,gaussian_obs_offset,
 logrt_linear_binary,logrt_linear_binary_minimal,softmax,softmax_2beta,
 softmax_binary,softmax_mu3,total_log_likelihood,unitsq_sgm,unitsq_sgm_mu3)

REFERENCE_COMMIT="2437f4dc241541072722a2695ddeca7b44d83dd3"
RTOL=2e-11
ATOL=2e-13

def norm(v:Any)->Any:
 if v is None: return np.nan
 if isinstance(v,list): return [norm(x) for x in v]
 return v

def arr(v:Any)->np.ndarray:
 return np.asarray(norm(v),dtype=np.float64)

def check(label,actual,expected):
 a=arr(actual); e=arr(expected)
 if a.shape!=e.shape:
  if a.size==e.size: e=e.reshape(a.shape)
  else: raise AssertionError(f"{label} shape: Python={a.shape} MATLAB={e.shape}")
 ok=np.isclose(a,e,rtol=RTOL,atol=ATOL,equal_nan=True)
 if np.all(ok): return
 idx=tuple(int(i) for i in np.argwhere(~ok)[0]) if np.ndim(ok) else ()
 av=float(a[idx]) if idx else float(a); ev=float(e[idx]) if idx else float(e)
 raise AssertionError(f"{label} first divergence index={idx}: MATLAB={ev:.17g}, Python={av:.17g}, abs={abs(av-ev):.3e}")

def binary_states(n=8):
 s=np.zeros((n,3,4),dtype=np.float64); x=np.linspace(.15,.85,n)
 s[:,0,0]=x; s[:,0,1]=x*(1-x); s[:,0,2]=np.clip(x+.03,.05,.95); s[:,0,3]=.2
 s[:,1,0]=np.linspace(-.8,.8,n); s[:,1,1]=.35; s[:,1,2]=np.linspace(-.7,.9,n); s[:,1,3]=np.linspace(.2,.5,n)
 s[:,2,0]=np.linspace(-2.4,-1.4,n); s[:,2,1]=.5; s[:,2,2]=np.linspace(-2.2,-1.2,n); s[:,2,3]=.6
 return s

def categorical_states(n=8,nc=3):
 s=np.zeros((n,3,nc,4),dtype=np.float64)
 for k in range(n):
  for c in range(nc):
   s[k,0,c,0]=-.4+.25*c+.03*k
   s[k,0,c,2]=-.3+.22*c+.02*k
 s[:,2,0,2]=np.linspace(-1,.2,n)
 return s

def main():
 p=argparse.ArgumentParser(); p.add_argument("matlab_json",type=Path); args=p.parse_args()
 payload=json.loads(args.matlab_json.read_text(encoding="utf-8"))
 m=payload["metadata"]
 assert m["reference_version"]=="8.2.0"
 assert m["reference_commit"]==REFERENCE_COMMIT
 assert m["schema_version"]=="m7-1"

 s=binary_states(); yb=np.array([0,1,1,0,1,0,1,1.]); u=yb.copy(); yc=np.linspace(.1,.9,8); yg=np.linspace(6.1,6.8,8); irr=[3]
 actual={
  "unitsq_sgm":unitsq_sgm(yb,s,[np.log(12.)],irregular_trials=irr),
  "unitsq_sgm_mu3":unitsq_sgm_mu3(yb,s,irregular_trials=irr),
  "softmax_binary":softmax_binary(yb,s,[np.log(2.)],inputs=u,irregular_trials=irr),
  "cdfgaussian_obs":cdfgaussian_obs(yb,s,irregular_trials=irr),
  "beta_obs":beta_obs(yc,s,[np.log(8.)],irregular_trials=irr),
  "gaussian_obs":gaussian_obs(yg,s,[np.log(.4)],irregular_trials=irr),
  "gaussian_obs_offset":gaussian_obs_offset(yg,s,[np.log(.4),6.],irregular_trials=irr),
  "logrt_linear_binary":logrt_linear_binary(yg,s,[6.2,.2,-.3,.4,-.1,np.log(.2)],inputs=u,irregular_trials=irr),
  "logrt_linear_binary_minimal":logrt_linear_binary_minimal(yg,s,[6.2,.2,-.3,np.log(.2)],inputs=u,irregular_trials=irr),
 }
 sc=categorical_states(); ym=np.array([1,2,3,1,3,2,1,2.]); um=np.array([1,0,1,0,1,0,1,0.])
 actual["softmax"]=softmax(ym,sc,[np.log(1.7)],irregular_trials=irr)
 actual["softmax_mu3"]=softmax_mu3(ym,sc,irregular_trials=irr)
 s5=np.zeros((8,1,3,1,2),dtype=np.float64); s5[:,0,:,0,0]=sc[:,0,:,0]; s5[:,0,:,0,1]=sc[:,0,:,2]
 actual["softmax_2beta"]=softmax_2beta(ym,s5,[np.log(1.5),np.log(.8)],inputs=um,irregular_trials=irr,predorpost=2)

 if set(actual)!=set(payload["cases"]):
  raise AssertionError(f"case mismatch Python={sorted(actual)} MATLAB={sorted(payload['cases'])}")
 for name,(logp,yhat,res) in actual.items():
  exp=payload["cases"][name]
  check(f"{name}.logp",logp,exp["logp"])
  check(f"{name}.yhat",yhat,exp["yhat"])
  check(f"{name}.res",res,exp["res"])
  check(f"{name}.total_loglik",total_log_likelihood(logp),exp["total_loglik"])
 print("M7 MATLAB/Python observation parity: PASS")

if __name__=="__main__":
 main()
