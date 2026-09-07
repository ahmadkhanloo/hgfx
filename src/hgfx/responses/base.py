"""Shared MATLAB-compatible observation-model helpers."""
from __future__ import annotations
from collections.abc import Sequence
import numpy as np

def ignored_mask(n_trials:int, irregular_trials:Sequence[int]|None)->np.ndarray:
    mask=np.zeros(n_trials,dtype=bool)
    if irregular_trials is None: return mask
    for index in irregular_trials:
        if index<0 or index>=n_trials: raise IndexError(f"irregular trial index out of range: {index}")
        mask[index]=True
    return mask

def output_arrays(n_trials:int)->tuple[np.ndarray,np.ndarray,np.ndarray]:
    return (np.full(n_trials,np.nan,dtype=np.float64),np.full(n_trials,np.nan,dtype=np.float64),np.full(n_trials,np.nan,dtype=np.float64))

def response_vector(responses,n_trials:int)->np.ndarray:
    y=np.asarray(responses,dtype=np.float64)
    if y.ndim==2: y=y[:,0]
    if y.ndim!=1 or y.size!=n_trials: raise ValueError("response shape mismatch")
    return y

def first_input_column(inputs,n_trials:int)->tuple[np.ndarray,np.ndarray]:
    u=np.asarray(inputs,dtype=np.float64)
    if u.ndim==1:
        if u.size!=n_trials: raise ValueError("input length mismatch")
        return u,u[:,None]
    if u.ndim==2 and u.shape[0]==n_trials and u.shape[1]>=1:
        return u[:,0],u
    raise ValueError("input shape mismatch")

def total_log_likelihood(logp)->float:
    return float(np.nansum(np.asarray(logp,dtype=np.float64)))
