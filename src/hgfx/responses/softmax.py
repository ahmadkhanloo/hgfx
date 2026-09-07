"""Softmax observation families."""
from __future__ import annotations
from collections.abc import Sequence
import numpy as np
from .base import first_input_column,ignored_mask,output_arrays,response_vector

def _chosen(prob,choices):
    idx=choices.astype(np.int64)-1
    if np.any(idx<0) or np.any(idx>=prob.shape[1]): raise ValueError("choices must be 1..N")
    return prob[np.arange(prob.shape[0]),idx]

def softmax(responses,inf_states,ptrans,*,irregular_trials:Sequence[int]|None=None,predorpost:int=1):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n)
    reg=~ignored_mask(n,irregular_trials); logp,yhat,res=output_arrays(n)
    pop=0 if predorpost==1 else 2; states=s[reg,0,:,pop]; yr=y[reg]
    be=np.exp(np.asarray(ptrans,dtype=np.float64).reshape(-1)[0])
    e=np.exp(be*states); prob=e/np.sum(e,axis=1,keepdims=True); probc=_chosen(prob,yr)
    logp[reg]=np.log(probc); yhat[reg]=probc; res[reg]=-np.log(probc)
    return logp,yhat,res

def softmax_binary(responses,inf_states,ptrans,*,inputs,irregular_trials:Sequence[int]|None=None,predorpost:int=1):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n)
    _,umat=first_input_column(inputs,n)
    if umat.shape[1] not in {1,3}: raise ValueError("inputs incompatible with softmax_binary")
    reg=~ignored_mask(n,irregular_trials); logp,yhat,res=output_arrays(n)
    pop=0 if predorpost==1 else 2; x=s[reg,0,pop]; yr=y[reg]
    be=np.exp(np.asarray(ptrans,dtype=np.float64).reshape(-1)[0])
    if umat.shape[1]==1:
        arg=be*(2*x-1)*(2*yr-1)
    else:
        r0=umat[reg,1]; r1=umat[reg,2]
        arg=be*(r1*x-r0*(1-x))*(2*yr-1)
    probc=1/(1+np.exp(-arg)); logp[reg]=np.log(probc)
    yh=yr*probc+(1-yr)*(1-probc); yhat[reg]=yh; res[reg]=(yr-yh)/np.sqrt(yh*(1-yh))
    return logp,yhat,res

def softmax_2beta(responses,inf_states,ptrans,*,inputs,irregular_trials:Sequence[int]|None=None,predorpost:int=1):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n); u,_=first_input_column(inputs,n)
    reg=~ignored_mask(n,irregular_trials); logp,yhat,res=output_arrays(n)
    states=s[reg,0,:,0,predorpost-1]; yr=y[reg]; ur=u[reg]; be=np.exp(np.asarray(ptrans,dtype=np.float64).reshape(-1)[:2])
    e1=np.exp(be[0]*states); e2=np.exp(be[1]*states)
    p1=e1/np.sum(e1,axis=1,keepdims=True); p2=e2/np.sum(e2,axis=1,keepdims=True)
    probc=_chosen(p1,yr)*(ur==1)+_chosen(p2,yr)*(ur==0)
    logp[reg]=np.log(probc); yhat[reg]=probc; res[reg]=-np.log(probc)
    return logp,yhat,res

def softmax_mu3(responses,inf_states,ptrans=None,*,irregular_trials:Sequence[int]|None=None,predorpost:int=1):
    s=np.asarray(inf_states,dtype=np.float64); n=s.shape[0]; y=response_vector(responses,n)
    reg=~ignored_mask(n,irregular_trials); logp,yhat,res=output_arrays(n)
    pop=0 if predorpost==1 else 2; states=s[reg,0,:,pop]; mu3=s[reg,2,0,2]; yr=y[reg]
    be=np.exp(-mu3)[:,None]; e=np.exp(be*states); prob=e/np.sum(e,axis=1,keepdims=True); probc=_chosen(prob,yr)
    logp[reg]=np.log(probc); yhat[reg]=probc; res[reg]=-np.log(probc)
    return logp,yhat,res
