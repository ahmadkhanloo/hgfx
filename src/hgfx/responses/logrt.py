"""Linear log-reaction-time observation families."""
from __future__ import annotations
from collections.abc import Sequence
import numpy as np
from hgfx.math.logistic import sigmoid
from .base import first_input_column,ignored_mask,output_arrays,response_vector

def _finish(y,logrt,var,reg):
    n=reg.size; logp,yhat,res=output_arrays(n); yr=y[reg]; ze=float(var)
    logp[reg]=-0.5*np.log(8*np.arctan(1.0)*ze)-(yr-logrt)**2/(2*ze)
    yhat[reg]=logrt; res[reg]=yr-logrt
    return logp,yhat,res

def logrt_linear_binary(responses,inf_states,ptrans,*,inputs,irregular_trials:Sequence[int]|None=None):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n); u,_=first_input_column(inputs,n)
    reg=~ignored_mask(n,irregular_trials); p=np.asarray(ptrans,dtype=np.float64).reshape(-1); ze=np.exp(p[5])
    m1=s[:,0,0]; sa1=s[:,0,1]; mu2=s[:,1,2]; sa2=s[:,1,3]; mu3=s[:,2,2]
    mr=m1[reg]; ur=u[reg]; poo=mr**ur*(1-mr)**(1-ur); surp=-np.log2(poo); bernv=sa1[reg]
    sg=np.asarray(sigmoid(mu2,1.0),dtype=np.float64); inferv=(sg*(1-sg)*sa2)[reg]; pv=(sg*(1-sg)*np.exp(mu3))[reg]
    pred=p[0]+p[1]*surp+p[2]*bernv+p[3]*inferv+p[4]*pv
    return _finish(y,pred,ze,reg)

def logrt_linear_binary_minimal(responses,inf_states,ptrans,*,inputs,irregular_trials:Sequence[int]|None=None):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n); u,_=first_input_column(inputs,n)
    reg=~ignored_mask(n,irregular_trials); p=np.asarray(ptrans,dtype=np.float64).reshape(-1); ze=np.exp(p[3])
    m1=s[:,0,0]; bern=m1*(1-m1); mr=m1[reg]; ur=u[reg]; surp=-np.log2(mr**ur*(1-mr)**(1-ur))
    pred=p[0]+p[1]*surp+p[2]*bern[reg]
    return _finish(y,pred,ze,reg)
