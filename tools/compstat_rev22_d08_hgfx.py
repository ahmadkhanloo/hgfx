#!/usr/bin/env python3
"""REV-2.2 official D08 same-input released-Wheel fit; ONE fixed experiment.

Consumes authentic MATLAB simulated responses. The worktree itself is not
the scientific HGFX executable. No seed changes, refit at alternate starting
points, parameter repair, threshold tuning or published release mutation.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np

from tools.compstat_rev24_manifest import (
    NUMPY_VERSION, FROZEN_RELEASE, MATLAB_REFERENCE, require_released_runtime,
)

PROTOCOL="compstat-rev2-2-d08-original-oracle-v1"
NATIVE_SIM=[1.04,1.0,0.0001,0.1,0.0,0.0,1.0,-13.0,-2.0,10000.0]


def check(ok,reason):
    if not ok:
        raise ValueError(reason)


def f64(value):
    if isinstance(value,dict):
        check(value.get("hgfx_numeric")=="ieee-strings-v1" and
              isinstance(value.get("shape"),list) and
              isinstance(value.get("data"),list),
              "Wrong frozen MATLAB IEEE transport schema")
        vals=[{"NaN":float("nan"),"Infinity":float("inf"),
               "-Infinity":-float("inf")}.get(v,v)
              if isinstance(v,str) else v for v in value["data"]]
        dims=tuple(int(d) for d in value["shape"])
        check(int(np.prod(dims))==len(vals),"MATLAB IEEE shape invalid")
        return np.asarray(vals,dtype=np.float64).reshape(dims,order="F")
    return np.asarray(value,dtype=np.float64)


def scalar(value):
    number=float(value)
    if np.isnan(number):
        return "NaN"
    if np.isposinf(number):
        return "Infinity"
    if np.isneginf(number):
        return "-Infinity"
    return number


def jsonarray(value):
    if isinstance(value,(dict,)):
        return {str(k):jsonarray(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [jsonarray(v) for v in value]
    if isinstance(value,np.ndarray):
        return jsonarray(value.tolist())
    if isinstance(value,(np.integer,)):
        return int(value)
    if isinstance(value,(np.bool_,bool)):
        return bool(value)
    if isinstance(value,(np.floating,float,int)):
        return scalar(value)
    return value


def hessian_diagnostics(H):
    h=np.asarray(H,dtype=np.float64)
    check(h.ndim==2 and h.shape[0]==h.shape[1],
          "Hessian must be square without invented values")
    if not np.isfinite(h).all():
        return {"finite":False,"symmetric":False,
                "positive_definite":False,"condition_2":"NaN"}
    sym=np.allclose(h,h.T,rtol=0,atol=0)
    try:
        eigen=np.linalg.eigvalsh((h+h.T)*0.5)
        eigmin=float(np.min(eigen))
        eigmax=float(np.max(eigen))
        condition=float(np.linalg.cond(h))
    except np.linalg.LinAlgError:
        return {"finite":True,"symmetric":bool(sym),
                "positive_definite":False,"condition_2":"NaN",
                "eigenvalues_failed":True}
    return {"finite":True,"symmetric_exact":bool(sym),
            "positive_definite":bool(eigmin>0.0),
            "minimum_eigenvalue":scalar(eigmin),
            "maximum_eigenvalue":scalar(eigmax),
            "condition_2":scalar(condition)}


def evaluate(reference: dict,wheel_hash: str) -> dict:
    check(reference["protocol"]==PROTOCOL
          and reference["source"]=="matlab"
          and reference["model"]=="uhgf"
          and reference["observation_model"]=="gaussian_obs"
          and reference["seed"]==123456789
          and reference["trials"]==614
          and reference["reference_commit"]==MATLAB_REFERENCE
          and reference["release_source_commit"]==FROZEN_RELEASE
          and reference["inputs_source_git_blob"]==
              "29a4d0322faf8894c414883c517950aa87b481db",
          "Original source model/seed/release drift")
    check(np.array_equal(f64(reference["native_simulation"]).reshape(-1),
                         np.asarray(NATIVE_SIM,dtype=np.float64)),
          "Frozen official simulated parameter vector changed")
    check(float(reference["native_observation"])==0.00002,
          "Original Gaussian simulation observation variance changed")
    u=f64(reference["inputs"]).reshape(-1)
    y=f64(reference["responses"]).reshape(-1)
    check(u.shape==y.shape==(614,) and np.isfinite(u).all() and np.isfinite(y).all(),
          "Source and simulated responses must be complete and finite")
    # Import only the verified released Wheel in the caller, never development.
    import hgfx
    from hgfx.compat.workflows import WorkflowFitProblem,resolve_config
    prc=resolve_config("uhgf").resolve_placeholders(u)
    obs=resolve_config("gaussian_obs").resolve_placeholders(u)
    problem=WorkflowFitProblem(y,u,prc,obs)
    means=np.r_[prc.priormus,obs.priormus]
    variances=np.r_[prc.priorsas,obs.priorsas]
    m_means=f64(reference["prior_means"]).reshape(-1)
    m_vars=f64(reference["prior_variances"]).reshape(-1)
    check(np.array_equal(means,m_means,equal_nan=True) and
          np.array_equal(variances,m_vars,equal_nan=True),
          "MATLAB vs published Wheel priors or resolved placeholders differ")
    matlab_init=f64(reference["init"]).reshape(-1)
    check(np.array_equal(problem.initial_full,matlab_init,equal_nan=True),
          "MATLAB vs published Wheel initial transformed vector differs")
    initial_matlab=f64(reference["final"]).reshape(-1)
    check(initial_matlab.size==means.size and
          np.isfinite(initial_matlab).all(),
          "MATLAB original endpoint unavailable: stop, no cherry-pick")
    expected_free=f64(reference["free_indices_matlab"]).astype(int).reshape(-1)-1
    check(np.array_equal(expected_free,np.asarray(problem.free_indices)),
          "Frozen optimizer free-index mask mismatch")
    fit=hgfx.fitModel(y,u,"uhgf","gaussian_obs")
    x=np.asarray(fit.optim.final,dtype=np.float64).reshape(-1)
    check(x.shape==initial_matlab.shape,"Published Wheel final parameter length drift")
    at_reference=problem.evaluate_full(initial_matlab)
    at_hgfx=problem.evaluate_full(x)
    return {
        "protocol":PROTOCOL,
        "source":"hgfx",
        "model":"uhgf","observation_model":"gaussian_obs",
        "seed":123456789,"trials":614,
        "reference_commit":MATLAB_REFERENCE,
        "release_source_commit":FROZEN_RELEASE,
        "wheel_sha256":wheel_hash,
        "status":"RAW_SCIENCE_UNCLASSIFIED",
        "inputs_f64_sha256":sha256(np.asarray(u,dtype="<f8").tobytes()).hexdigest(),
        "responses_f64_sha256":sha256(np.asarray(y,dtype="<f8").tobytes()).hexdigest(),
        "initial":jsonarray(np.asarray(fit.optim.init,dtype=np.float64)),
        "free_indices_matlab":jsonarray(expected_free+1),
        "prior_means":jsonarray(means),
        "prior_variances":jsonarray(variances),
        "final":jsonarray(x),
        "native_fit_perceptual":jsonarray(fit.p_prc.p),
        "native_fit_observation":jsonarray(fit.p_obs.p),
        "negLl":scalar(fit.optim.negLl),
        "negLj":scalar(fit.optim.negLj),
        "BIC":scalar(fit.optim.BIC),
        "LME":scalar(fit.optim.LME),
        "H":jsonarray(fit.optim.H),
        "Sigma":jsonarray(fit.optim.Sigma),
        "Corr":jsonarray(fit.optim.Corr),
        "hessian_diagnostics":hessian_diagnostics(fit.optim.H),
        "traj":jsonarray(fit.traj.to_dict()),
        "yhat":jsonarray(fit.optim.yhat),
        "res":jsonarray(fit.optim.res),
        "objectives":{
            "matlab_endpoint":{
                "rval":int(at_reference.rval),
                "negLl":scalar(at_reference.neg_log_likelihood),
                "negLj":scalar(at_reference.neg_log_joint),
                "trialLogLls":jsonarray(at_reference.trial_log_likelihoods),
                "perceptual_prior_total":scalar(at_reference.perceptual_prior.total),
                "observation_prior_total":scalar(at_reference.observation_prior.total),
            },
            "hgfx_endpoint":{
                "rval":int(at_hgfx.rval),
                "negLl":scalar(at_hgfx.neg_log_likelihood),
                "negLj":scalar(at_hgfx.neg_log_joint),
                "trialLogLls":jsonarray(at_hgfx.trial_log_likelihoods),
                "perceptual_prior_total":scalar(at_hgfx.perceptual_prior.total),
                "observation_prior_total":scalar(at_hgfx.observation_prior.total),
            },
        },
        "termination":"NOT_EXPORTED",
        "converged":"NOT_EXPORTED",
        "warning_coverage":"WARNING_COVERAGE_INCOMPLETE",
        "runtime":{
            "python":platform.python_version(),
            "numpy":np.__version__,
            "platform":platform.platform(),
            "installed_hgfx":importlib.metadata.version("hgfx"),
        },
        "interpretation":"NO_GLOBAL_PARITY_OR_VERIFIED_CONVERGENCE_CLAIM",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matlab-reference",type=Path,required=True)
    p.add_argument("--release-wheel",type=Path,required=True)
    p.add_argument("--frozen-tag-source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    check(not args.output.exists(),"Refuse overwrite of scientific input/output")
    wheel_hash=require_released_runtime(args.release_wheel,args.frozen_tag_source)
    check(wheel_hash=="5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90",
          "Wrong original released HGFX 1.0.0 Wheel")
    check(np.__version__==NUMPY_VERSION,"NumPy source version changed")
    import hgfx
    import jax
    check(jax.config.read("jax_enable_x64") and jax.default_backend()=="cpu",
          "Run on actual JAX CPU binary64, not mock or GPU")
    check(Path(hgfx.__file__).resolve()==
          Path(importlib.metadata.distribution("hgfx").locate_file(
              "hgfx/__init__.py")).resolve(),
          "HGFX loaded from mutable worktree rather than released wheel")
    reference=json.loads(args.matlab_reference.read_text(encoding="utf-8"))
    result=evaluate(reference,wheel_hash)
    result["runtime"]["jax"]=jax.__version__
    result["runtime"]["jax_backend"]=jax.default_backend()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,
                                      allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],"case":"official_D08_fit",
        "n":result["trials"],"wheel":wheel_hash,
        "self_endpoints_cross_evaluated":2,
        "output_sha256":sha256(args.output.read_bytes()).hexdigest(),
        "scientific_gate":"NOT_CLASSIFIED_YET",
    },sort_keys=True))


if __name__=="__main__":
    main()
