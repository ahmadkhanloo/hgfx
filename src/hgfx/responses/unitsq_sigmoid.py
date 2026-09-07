"""Unit-square sigmoid observation families."""
from __future__ import annotations
from collections.abc import Sequence
import numpy as np
from .base import ignored_mask,output_arrays,response_vector

def _core(responses,x,ze,*,irregular_trials):
    x=np.asarray(x,dtype=np.float64).reshape(-1); n=x.size
    y=response_vector(responses,n); reg=~ignored_mask(n,irregular_trials)
    logp,yhat,res=output_arrays(n); xr=x[reg]; yr=y[reg]
    zr=np.asarray(ze,dtype=np.float64)
    if zr.ndim==0: zr=np.full(xr.shape,zr,dtype=np.float64)
    else: zr=zr.reshape(-1)[reg]
    with np.errstate(divide="ignore",invalid="ignore",over="ignore"):
        logx=np.log(xr); alt=np.log1p(xr-1.0); m=(1.0-xr)<1e-4; logx[m]=alt[m]
        log1mx=np.log(1.0-xr); alt2=np.log1p(-xr); m2=xr<1e-4; log1mx[m2]=alt2[m2]
        logp[reg]=yr*zr*(logx-log1mx)+zr*log1mx-np.log((1.0-xr)**zr+xr**zr)
        yhat[reg]=xr; res[reg]=(yr-xr)/np.sqrt(xr*(1.0-xr))
    return logp,yhat,res

def unitsq_sgm(responses,inf_states,ptrans,*,irregular_trials:Sequence[int]|None=None,predorpost:int=1):
    s=np.asarray(inf_states,dtype=np.float64); pop=0 if predorpost==1 else 2
    ze=np.exp(np.asarray(ptrans,dtype=np.float64).reshape(-1)[0])
    return _core(responses,s[:,0,pop],ze,irregular_trials=irregular_trials)

def unitsq_sgm_mu3(responses,inf_states,ptrans=None,*,irregular_trials:Sequence[int]|None=None):
    s=np.asarray(inf_states,dtype=np.float64)
    return _core(responses,s[:,0,0],np.exp(-s[:,2,0]),irregular_trials=irregular_trials)
