"""Gaussian observation families."""
from __future__ import annotations
from collections.abc import Sequence
import numpy as np
from .base import ignored_mask,output_arrays,response_vector

def _core(responses,mean,var,*,irregular_trials):
    x=np.asarray(mean,dtype=np.float64).reshape(-1); n=x.size
    y=response_vector(responses,n); reg=~ignored_mask(n,irregular_trials)
    logp,yhat,res=output_arrays(n); yr=y[reg]; xr=x[reg]; ze=float(var)
    logp[reg]=-0.5*np.log(8*np.arctan(1.0)*ze)-(yr-xr)**2/(2*ze)
    yhat[reg]=xr; res[reg]=yr-xr
    return logp,yhat,res

def gaussian_obs(responses,inf_states,ptrans,*,irregular_trials:Sequence[int]|None=None):
    s=np.asarray(inf_states,dtype=np.float64); ze=np.exp(np.asarray(ptrans,dtype=np.float64).reshape(-1)[0])
    return _core(responses,s[:,0,0],ze,irregular_trials=irregular_trials)

def gaussian_obs_offset(responses,inf_states,ptrans,*,irregular_trials:Sequence[int]|None=None):
    s=np.asarray(inf_states,dtype=np.float64); p=np.asarray(ptrans,dtype=np.float64).reshape(-1)
    return _core(responses,p[1]+s[:,0,0],np.exp(p[0]),irregular_trials=irregular_trials)
