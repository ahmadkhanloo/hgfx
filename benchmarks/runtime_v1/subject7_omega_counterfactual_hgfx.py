#!/usr/bin/env python3
"""PERF-01D: full 2x2 predeclared counterfactual HGF perceptual omega grid.

The only two *perceptual* fitted coordinates in frozen HGF are
zero-based 12 (omega level 2) and 13 (omega level 3).
The original fitted observation coordinate 14 is NOT used by HGF forward.
This experiment runs no optimizer, has no timers, and is NOT a science PASS.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np

from subject7_crossed_forward_hgfx import (
    HGFX_SHA,MATLAB_SHA,ORIGINAL_RUN,FIELDS,run as original_three_forward,
)
from scientific_preflight import FORWARD
from trialwise_hgfx_export import clean
from generate_inputs import encode

CORNERS=("MM_original_matlab","HM_hgfx_omega2_matlab_omega3",
         "MH_matlab_omega2_hgfx_omega3","HH_original_hgfx")
ORIGIN_INDEX={"MM_original_matlab":(0,0),
              "HM_hgfx_omega2_matlab_omega3":(1,0),
              "MH_matlab_omega2_hgfx_omega3":(0,1),
              "HH_original_hgfx":(1,1)}


def exact_vectors(h:np.ndarray,m:np.ndarray)->dict[str,np.ndarray]:
    if h.shape!=(15,) or m.shape!=(15,) or not np.array_equal(np.isnan(h),np.isnan(m)):
        raise ValueError("Wrong original 15 transformed-parameter shape/NaN mask")
    if not np.array_equal(h[:12],m[:12],equal_nan=True):
        raise ValueError("Unexpected nonfitted perceptual-coordinate difference")
    v={}
    for name,(selector2,selector3) in ORIGIN_INDEX.items():
        a=m.copy()  # frozen original MATLAB observation param, index14, for mixed corners
        a[12]=h[12] if selector2 else m[12]
        a[13]=h[13] if selector3 else m[13]
        if name=="HH_original_hgfx":
            a[14]=h[14]  # original true HGFX endpoint; not used by HGF forward
        v[name]=a
    if (not np.array_equal(v["MM_original_matlab"],m,equal_nan=True)
            or not np.array_equal(v["HH_original_hgfx"],h,equal_nan=True)
            or not np.isfinite([h[12],h[13],m[12],m[13]]).all()):
        raise ValueError("Original immutable corner endpoints were not preserved")
    return v


def execute(root:Path,archive:Path)->dict:
    if metadata.version("hgfx")!="1.0.0":
        raise ValueError("Frozen release expected")
    base=original_three_forward(root,archive)  # checks both original raw SHA and 63/64
    old={x["origin"]:x for x in base["cases"]}
    h=np.asarray(old["original_hgfx_fitted_endpoint"]["full_transformed_vector"],float)
    m=np.asarray(old["original_matlab_fitted_endpoint"]["full_transformed_vector"],float)
    vectors=exact_vectors(h,m)
    u_data=json.loads((root/"inputs"/"binary_128_s64.json").read_bytes())
    u=np.asarray(u_data["u"][7],float)
    rows=[]
    for name in CORNERS:
        v=vectors[name]
        if name=="MM_original_matlab":
            original=old["original_matlab_fitted_endpoint"]
        elif name=="HH_original_hgfx":
            original=old["original_hgfx_fitted_endpoint"]
        else:
            original=None
        if original is not None:
            traj=original["traj"]
            states=original["inf_states"]
        else:
            traj_raw,inf=FORWARD["hgf_binary"](
                u,v[:14],transformed=True,
                ignored_trials=np.flatnonzero(np.isnan(u)).tolist())
            traj=clean(traj_raw)
            states=clean(inf)
        if set(traj)!=FIELDS:
            raise ValueError("Missing original HGF trajectory fields")
        for field in FIELDS:
            shape=(128,2) if field=="w" else (128,3)
            if np.asarray(traj[field],float).shape!=shape:
                raise ValueError(f"Wrong original {field} forward shape")
        if np.asarray(states,float).shape!=(128,3,4):
            raise ValueError("Wrong original inference states")
        rows.append({
            "corner":name,
            "omega2_from":"HGFX" if ORIGIN_INDEX[name][0] else "MATLAB",
            "omega3_from":"HGFX" if ORIGIN_INDEX[name][1] else "MATLAB",
            "status":"EVALUATED_FROZEN_UNTIMED_HGFX_FORWARD",
            "full_transformed_vector":clean(v),
            "traj":traj,
            "inf_states":states,
        })
    return {
        "schema":"perf01d-subject7-omega-counterfactual-hgfx-v1",
        "status":"AUTHOR_SIDE_2X2_OMEGA_FORWARD_DIAGNOSTIC_NO_FITTING_OR_SCIENTIFIC_PASS",
        "original_64_fit_run":ORIGINAL_RUN,
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "original_raw_sha256":base["original_raw_sha256"],
        "source_input_sha256":base["source_input_sha256"],
        "source_config_sha256":base["source_config_sha256"],
        "subject_index_zero_based":7,
        "trials":128,
        "model":"hgf_binary",
        "observation":"unitsq_sgm",
        "perceptual_free_coordinates_zero_based":[12,13],
        "observation_free_coordinate_zero_based":14,
        "observation_coordinate_role":"fixed_original_MATLAB_in_mixed_corners_not_used_in_perceptual_forward",
        "original_full_parameter_ends_preserved":True,
        "predeclared_corner_order":list(CORNERS),
        "cases":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=execute(a.input,a.original)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(result))
    print(json.dumps({"status":result["status"],
                      "corners":result["predeclared_corner_order"]},sort_keys=True))


if __name__=="__main__":
    main()
