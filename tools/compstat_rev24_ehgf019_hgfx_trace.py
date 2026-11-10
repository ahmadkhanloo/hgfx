#!/usr/bin/env python3
"""Prospective REV-2.4 D019 trace: released HGFX 1.0.0, original fixed vector.

One immutable original synthetic case only. No fitting, clipping, fixes or
numerical acceptance claims. All states are for the same original 128 trials.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np

from tools.compstat_rev24_manifest import (
    FROZEN_RELEASE, MATLAB_REFERENCE, NUMPY_VERSION,
    ieee, release_config_vectors, require_released_runtime, validate_manifest,
)
from tools.compstat_rev24_hgfx_eval import f64

DIAGNOSTIC = "rev24-ehgf019-latent-trace-v1"
SOURCE_CASE = "REV24-G-ehgf_binary-019"
SOURCE_CASE_SHA = "276d21f43a91fc8748438aafc6ec44f759f23dc2ae97dae8b4cc1274aba3fefb"
SOURCE_MANIFEST_SHA = "35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95"
MATRIX_FIELDS = ("mu", "sa", "muhat", "sahat", "v", "w", "da",
                 "psi", "epsi", "wt", "ud")
STATE_FIELDS = ("muhat", "sahat", "mu", "sa")


def check(value, message):
    if not value:
        raise ValueError(message)


def source_case(doc):
    validate_manifest(doc)
    check(doc["manifest_sha256"] == SOURCE_MANIFEST_SHA,
          "Cannot substitute or regenerate another Panel G input manifest")
    group = doc["strata"][1]
    check(group["model"] == "ehgf_binary"
          and group["observation_model"] == "unitsq_sgm"
          and len(group["rows"]) == 200, "Wrong original model/group")
    case = group["rows"][19]
    check(case["case_id"] == SOURCE_CASE
          and case["case_sha256"] == SOURCE_CASE_SHA
          and case["replicate_zero_based"] == 19,
          "Original failing vector/source hash changed")
    check(group["free_indices_zero_based"] == [12, 13, 14],
          "Original parameter mask/order mismatch")
    check(doc["trials"] == 128
          and len(doc["inputs"]) == len(doc["responses"]) == 128,
          "Original trials changed")
    return group, case


def encode_array(values):
    source = np.asarray(values, dtype=np.float64)
    check(source.ndim == 2 and source.shape[0] == 128,
          "Every trace must be a 128-by-level numerical array")
    return [[ieee(x) for x in row] for row in source]


def output_trace(traj, states, logp, case, manifest, *,
                 wheel_sha256, runtime):
    values = np.asarray(states, dtype=np.float64)
    check(values.ndim == 3 and values.shape == (128, 3, 4),
          "Original eHGF binary inferred states must be 128x3x4")
    result = {
        "diagnostic": DIAGNOSTIC,
        "source": "hgfx",
        "source_manifest_sha256": SOURCE_MANIFEST_SHA,
        "source_case_id": SOURCE_CASE,
        "source_case_sha256": SOURCE_CASE_SHA,
        "release_source_commit": FROZEN_RELEASE,
        "matlab_reference_commit": MATLAB_REFERENCE,
        "release_wheel_sha256": wheel_sha256,
        "trials": 128,
        "levels": 3,
        "source_trial_log_likelihoods_sha256":
            hashlib.sha256(json.dumps([ieee(x) for x in np.asarray(logp).reshape(-1)],
                                      sort_keys=True, separators=(",", ":"),
                                      allow_nan=False).encode()).hexdigest(),
        "trial_log_likelihoods": [ieee(x) for x in np.asarray(logp).reshape(-1)],
        "inferred_states": {
            name: encode_array(values[:, :, axis])
            for axis, name in enumerate(STATE_FIELDS)
        },
        "trajectories": {
            key: encode_array(traj[key]) for key in MATRIX_FIELDS
        },
        "original_600_case_grid_modified": False,
        "scientific_gate": "NOT_ASSESSED_DIAGNOSTIC_ONLY",
        "runtime": runtime,
    }
    check(len(result["trial_log_likelihoods"]) == 128,
          "Missing per-trial likelihoods")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--release-wheel",type=Path,required=True)
    p.add_argument("--frozen-tag-source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    check(not args.output.exists(),"Original diagnostic output must not be overwritten")
    wheel_sha=require_released_runtime(args.release_wheel,args.frozen_tag_source)
    check(np.__version__ == NUMPY_VERSION,"NumPy version drift")
    import hgfx
    import jax
    import jaxlib
    from hgfx.compat.simulation import ehgf_binary_config
    from hgfx.models.ehgf_binary import ehgf_binary
    from hgfx.responses.unitsq_sigmoid import unitsq_sgm
    check(jax.config.read("jax_enable_x64") and jax.default_backend()=="cpu",
          "Frozen scientific platform must be CPU float64")
    check(Path(hgfx.__file__).resolve() ==
          Path(importlib.metadata.distribution("hgfx").locate_file(
              "hgfx/__init__.py")).resolve(),
          "HGFX imported from worktree rather than released frozen Wheel")
    doc=json.loads(args.manifest.read_text(encoding="utf-8"))
    group,case=source_case(doc)
    full=f64(case["full_transformed"])
    check(np.array_equal(full[[12,13,14]],
                         np.asarray(case["free_transformed"],dtype=np.float64)),
          "Original full vs free vector mismatch")
    u=np.asarray(doc["inputs"],dtype=np.float64)
    y=np.asarray(doc["responses"],dtype=np.float64)
    original_config=ehgf_binary_config().resolve_placeholders(u)
    means=np.r_[original_config.priormus, np.log(48.0)]
    variances=np.r_[original_config.priorsas, 1.0]
    check(group["prior_means_full"] == [ieee(x) for x in means]
          and group["prior_variances_full_ieee"] == [ieee(x) for x in variances],
          "Diagnostic release configuration does not match frozen manifest")
    traj,states=ehgf_binary(
        u,full[:14],transformed=True,
        irregular_intervals=bool(original_config.options.get("irregular_intervals",False)),
        ignored_trials=[]
    )
    ll,_,_=unitsq_sgm(y,states,full[14:],
                      predorpost=1,irregular_trials=[])
    result=output_trace(traj,states,ll,case,doc,wheel_sha256=wheel_sha,
                        runtime={
                            "python":platform.python_version(),"platform":platform.platform(),
                            "numpy":np.__version__,"jax":jax.__version__,
                            "jaxlib":jaxlib.__version__,
                            "hgfx":importlib.metadata.version("hgfx"),
                            "backend":jax.default_backend(),
                        })
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "diagnostic":DIAGNOSTIC,
        "case":SOURCE_CASE,
        "first_nonfinite_likelihood":next(
            (i for i,x in enumerate(result["trial_log_likelihoods"])
             if isinstance(x,str)),None),
        "output_sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "scientific_gate":"NOT_ASSESSED_DIAGNOSTIC_ONLY",
    },sort_keys=True))


if __name__=="__main__":
    main()
