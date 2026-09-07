"""Cumulative-Gaussian binary observation model."""
from __future__ import annotations
import math
from collections.abc import Sequence
import numpy as np
from .base import ignored_mask,output_arrays,response_vector

def _erf(values):
    a=np.asarray(values,dtype=np.float64)
    return np.asarray([math.erf(float(v)) for v in a.reshape(-1)],dtype=np.float64).reshape(a.shape)

def cdfgaussian_obs(responses,inf_states,ptrans=None,*,irregular_trials:Sequence[int]|None=None):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n)
    reg=~ignored_mask(n,irregular_trials); logp,yhat,res=output_arrays(n)
    mu2=s[reg,1,2]; sa2=s[reg,1,3]; yr=y[reg]
    x2lt0=0.5*(1+_erf((0-mu2)/(sa2*np.sqrt(2.0))))
    probc=yr*(1-x2lt0)+(1-yr)*x2lt0; yh=1-x2lt0
    logp[reg]=np.log(probc); yhat[reg]=yh; res[reg]=(yr-yh)/np.sqrt(yh*(1-yh))
    return logp,yhat,res
