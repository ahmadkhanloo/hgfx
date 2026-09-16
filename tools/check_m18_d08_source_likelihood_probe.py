#!/usr/bin/env python3
"""Localize the exact first D08 failed-holdout likelihood residual."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT,_array
from hgfx.compat.objective import _matlab_sum
from hgfx.compat.workflows import WorkflowFitProblem,resolve_config

PROTOCOL='m18-d08-source-likelihood-probe-1'

def arr(v): return _array(v)
def scalar(v): return np.float64(arr(v).reshape(-1)[0])
def acmp(a,e):
    aa=np.asarray(a,dtype=np.float64); ee=np.asarray(e,dtype=np.float64)
    if aa.shape!=ee.shape:
        if aa.size==ee.size: ee=ee.reshape(aa.shape)
        else: return {'exact':False,'shape':[list(aa.shape),list(ee.shape)]}
    both_nan=np.isnan(aa)&np.isnan(ee); exact=(aa==ee)|both_nan
    finite=np.isfinite(aa)&np.isfinite(ee); diff=np.zeros_like(aa,dtype=np.float64); diff[finite]=np.abs(aa[finite]-ee[finite])
    first=None
    if not np.all(exact):
        idx=tuple(int(x) for x in np.argwhere(~exact)[0]); first={'index':list(idx),'hgfx':float(aa[idx]),'matlab':float(ee[idx]),'abs_diff':float(abs(aa[idx]-ee[idx]))}
    return {'exact':bool(np.all(exact)),'max_abs_diff':float(np.max(diff)) if diff.size else 0.0,'first_difference':first}

def scalar_loop(values):
    total=np.float64(0.0)
    for v in np.asarray(values,dtype=np.float64).reshape(-1): total=np.float64(total+v)
    return total

def main(reference_path:Path,output_path:Path)->int:
    ref=json.loads(reference_path.read_text())
    if ref.get('protocol')!=PROTOCOL or ref.get('reference_commit')!=REFERENCE_COMMIT: raise ValueError('Frozen protocol/reference mismatch')
    if ref.get('case_id')!='D08_fit' or int(ref.get('seed'))!=314159265: raise ValueError('Frozen D08 seed mismatch')
    if int(ref.get('source_trace_row_1based'))!=38 or int(ref.get('component_free_index_1based'))!=1 or int(ref.get('ridders_step_1based'))!=1 or ref.get('side')!='plus' or scalar(ref.get('h'))!=1.0: raise ValueError('Frozen source sample mismatch')
    u=arr(ref['inputs']).reshape(-1); y=arr(ref['responses']).reshape(-1)
    prc=resolve_config('uhgf').resolve_placeholders(u); obs=resolve_config('gaussian_obs').resolve_placeholders(u); problem=WorkflowFitProblem(y,u,prc,obs)
    free=arr(ref['sample_free']).reshape(-1); source=arr(ref['source_x']).reshape(-1)
    if free.size!=7 or source.size!=7 or not np.array_equal(free[1:],source[1:]) or free[0]-source[0]!=1.0: raise ValueError('Could not reconstruct frozen free vector')
    full=problem.expand(free); full_ref=arr(ref['full_transformed']).reshape(-1); full_cmp=acmp(full,full_ref)
    if not full_cmp['exact']:
        classification='INSUFFICIENT_REFERENCE_EVIDENCE'; out={'protocol':PROTOCOL,'classification':classification,'full_vector':full_cmp}; output_path.parent.mkdir(parents=True,exist_ok=True); output_path.write_text(json.dumps(out,indent=2)+'\n'); return 2
    n=problem.n_perceptual
    traj,states=problem.forward(u,full[:n],transformed=True,irregular_intervals=False,ignored_trials=())
    logp,yhat,res=problem.observation(y,states,full[n:],irregular_trials=())
    states_cmp=acmp(states,ref['inf_states']); x_cmp=acmp(states[:,0,0],ref['observation_x']); logp_cmp=acmp(logp,ref['trial_log_likelihoods']); yhat_cmp=acmp(yhat,ref['yhat']); res_cmp=acmp(res,ref['res'])
    ze=np.exp(np.float64(full[n])); xr=np.asarray(states[:,0,0],dtype=np.float64); yr=np.asarray(y,dtype=np.float64)
    normalizer=-np.float64(.5)*np.log(np.float64(8.0)*np.arctan(np.float64(1.0))*ze)
    residual=yr-xr; sq=residual**2; denom=np.float64(2.0)*ze; quadratic=sq/denom; formula=normalizer-quadratic
    primitives={
      'ze':acmp(np.asarray([ze]),np.asarray([scalar(ref['ze'])])),
      'normalizer':acmp(np.asarray([normalizer]),np.asarray([scalar(ref['primitives']['normalizer'])])),
      'residual':acmp(residual,ref['primitives']['residual']),
      'squared_residual':acmp(sq,ref['primitives']['squared_residual']),
      'denominator':acmp(np.asarray([denom]),np.asarray([scalar(ref['primitives']['denominator'])])),
      'quadratic':acmp(quadratic,ref['primitives']['quadratic']),
      'logp_formula':acmp(formula,ref['primitives']['logp_formula']),
    }
    objective=problem.evaluate_full(full)
    matlab_vector=scalar(ref['log_likelihood_sum']); matlab_scalar=scalar(ref['log_likelihood_scalar_loop']); numpy_sum=np.sum(np.asarray(logp,dtype=np.float64),dtype=np.float64); py_scalar=scalar_loop(logp); compat=_matlab_sum(logp)
    reductions={'matlab_vector':float(matlab_vector),'matlab_scalar_loop':float(matlab_scalar),'matlab_vector_vs_scalar_abs_diff':float(abs(matlab_vector-matlab_scalar)),'numpy_sum':float(numpy_sum),'python_scalar_loop':float(py_scalar),'compat_matlab_sum':float(compat),'objective_log_likelihood':float(objective.log_likelihood),'numpy_vs_matlab_vector_abs_diff':float(abs(numpy_sum-matlab_vector)),'scalar_loop_vs_matlab_scalar_abs_diff':float(abs(py_scalar-matlab_scalar)),'compat_vs_matlab_vector_abs_diff':float(abs(compat-matlab_vector))}
    if not states_cmp['exact']: classification='FORWARD_STATE_DIVERGENCE'
    elif not logp_cmp['exact']: classification='GAUSSIAN_OBSERVATION_PRIMITIVE_DIVERGENCE'
    elif np.float64(objective.log_likelihood)!=matlab_vector: classification='LIKELIHOOD_REDUCTION_DIVERGENCE'
    else: classification='NO_LOCAL_DIVERGENCE'
    out={'protocol':PROTOCOL,'reference_commit':REFERENCE_COMMIT,'case_id':'D08_fit','seed':314159265,'classification':classification,'full_vector':full_cmp,'inf_states':states_cmp,'observation_x':x_cmp,'trial_log_likelihoods':logp_cmp,'yhat':yhat_cmp,'res':res_cmp,'primitives':primitives,'reductions':reductions,'acceptance_effect':'NONE_DIAGNOSTIC_ONLY'}
    output_path.parent.mkdir(parents=True,exist_ok=True); output_path.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'classification':classification,'inf_states':states_cmp,'trial_log_likelihoods':logp_cmp,'reductions':reductions}),flush=True); return 0

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('reference',type=Path); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); raise SystemExit(main(a.reference,a.output))
