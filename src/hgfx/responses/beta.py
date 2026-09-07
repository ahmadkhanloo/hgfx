"""Beta observation model."""
from __future__ import annotations
import math
from collections.abc import Sequence
import numpy as np
from hgfx.math.logistic import sigmoid
from .base import ignored_mask,output_arrays,response_vector

def _gamma(a):
    a=np.asarray(a,dtype=np.float64)
    return np.asarray([math.gamma(float(v)) for v in a.reshape(-1)],dtype=np.float64).reshape(a.shape)

def beta_obs(responses,inf_states,ptrans,*,irregular_trials:Sequence[int]|None=None,predorpost:int=1,perceptual_model:str="hgf_binary"):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n)
    reg=~ignored_mask(n,irregular_trials); logp,yhat,res=output_arrays(n)
    if perceptual_model=="rw_binary":
        mu=np.asarray(s[:,0] if s.ndim>1 else s,dtype=np.float64).reshape(n)
    else:
        mu=s[:,0,0].copy()
        if predorpost==2: mu=np.asarray(sigmoid(s[:,1,2],1.0),dtype=np.float64)
    mur=mu[reg]; yr=0.95*(y[reg]-0.5)+0.5; nu=np.exp(np.asarray(ptrans,dtype=np.float64).reshape(-1)[0])
    al=mur*nu; be=nu-al
    dens=_gamma(al+be)/(_gamma(al)*_gamma(be))*yr**(al-1)*(1-yr)**(be-1)
    logp[reg]=np.log(dens); yhat[reg]=mur; res[reg]=yr-mur
    return logp,yhat,res
