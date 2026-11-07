#!/usr/bin/env python3
"""Audit genuine raw MATLAB-v7 native vs delegated private Ridders public fit values.

Reads 26 preexisting public stable fields and whole original optimizer iter
without trusting MATLAB producer's aggregated isequaln boolean.
Author-side independent *code path*, not independent scientific review.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from scipy.io import loadmat

from replay_subject7_matlab_26_public_fields import (
    OPT, only_struct, matlab_text, matlab_strings, scalar, compare_exact,
)

SCHEMA="perf01d-real-private-matlab-first-ridders-stencil-v1"
HGFX="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB="2437f4dc241541072722a2695ddeca7b44d83dd3"


def need(x,msg):
    if not x:
        raise ValueError(msg)


def inspect_mat(mat, reported, hgfx_source, original):
    need(original["subject_count"]==64 and original["classification_counts"]=={
        "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
        "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1}
        and original["cases"][7]["mismatched_fields"]==["traj.mu","traj.muhat"]
        and all(original["cases"][7]["fields"][k]["mismatch_count"]==4
                for k in ("traj.mu","traj.muhat")),
        "Original 63/64 subject 7 4+4 failed scientific fitting changed")
    d=loadmat(mat,struct_as_record=False,squeeze_me=False,
              chars_as_strings=True,mat_dtype=True)
    need(set(("native_public","instrumented_public","native_iter",
              "instrumented_iter","metadata")).issubset(d),
         "Original private MATLAB raw MAT-v7 missing actual native/wrapped values")
    a,b,ma=(only_struct(d[q]) for q in ("native_public","instrumented_public","metadata"))
    need(matlab_text(ma.schema)==SCHEMA
         and matlab_text(ma.frozen_hgfx_sha)==HGFX
         and matlab_text(ma.frozen_matlab_sha)==MATLAB
         and matlab_text(ma.source_hgfx_stencil_sha256)==sha256(hgfx_source).hexdigest()
         and matlab_text(ma.original_science)=="63/64 SCIENTIFIC NONPASS"
         and matlab_text(ma.independent_review)=="NOT_RECEIVED"
         and matlab_text(ma.perf01c)=="NOT_FROZEN"
         and matlab_text(ma.timing)=="NOT_RUN"
         and scalar(ma.hook_count)==1 and bool(scalar(ma.delegated))
         and bool(scalar(ma.native_wrapped_26_and_iter_exact))
         and matlab_text(ma.github_run_id)==str(reported["github_run_id"])
         and matlab_text(ma.tested_sha)==str(reported["tested_sha"]),
         "Original raw MATLAB native/wrapped metadata, source SHA or independent review changed")
    opt=matlab_strings(ma.opt_fields)
    traj=matlab_strings(ma.traj_fields)
    need(tuple(opt)==OPT and len(traj)==11 and len(set(traj))==11,
         "Original 15+11 MATLAB public stable fields inventory altered")
    evidence=[]
    for group,fields in (("optim",opt),("traj",traj)):
        xx,yy=only_struct(getattr(a,group)),only_struct(getattr(b,group))
        need(set(xx._fieldnames)==set(yy._fieldnames)==set(fields),
             "Original MATLAB full raw public stable group missing field")
        for name in fields:
            issue=compare_exact(getattr(xx,name),getattr(yy,name),group+"."+name)
            evidence.append({"field":group+"."+name,
                             "exact_equal_nan":issue is None,"difference":issue})
    iissue=compare_exact(only_struct(d["native_iter"]),
                         only_struct(d["instrumented_iter"]),"optim.iter")
    need(len(evidence)==26 and all(z["exact_equal_nan"] for z in evidence)
         and iissue is None,
         "Actual native/wrapped 26 or full original MATLAB iter DIFFER: invalid instrument")
    return {
        "schema":"perf01d-matlab-initial-ridders-private-raw-public-verification-v1",
        "status":"AUTHOR_SIDE_SAME_RUN_MATLAB_NEUTRALITY_26_AND_FULL_ITER",
        "real_mat_sha256":sha256(Path(mat).read_bytes()).hexdigest(),
        "original_full_fit":"63/64 SCIENTIFIC NONPASS",
        "native_wrapped_26_exact":True,
        "native_wrapped_complete_iter_exact":True,
        "all_actual_26_field_pairs":evidence,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for f in ("mat","report","hgfx-source","original-fit","output"):
        p.add_argument("--"+f,type=Path,required=True)
    a=p.parse_args()
    d=inspect_mat(a.mat,json.loads(a.report.read_bytes()),
                  a.hgfx_source.read_bytes(),json.loads(a.original_fit.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in d.items() if k!="all_actual_26_field_pairs"},sort_keys=True))


if __name__=="__main__": main()
