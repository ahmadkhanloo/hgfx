#!/usr/bin/env python3
"""Archive-only deep exact source stage report reproduction on a separate CPU.

DOES NOT invoke native MATLAB or HGFX unitsq model computations.
Reads full SHA-locked original 71×128×2 actual source stage arrays, rechecks
all original 63/64 and source/model provenance and rederives fieldwise
bit comparisons; deep-compares entire report to the immutable real run.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from compare_original_x0_unitsq_arithmetic import report
from replay_original_x0_infstates_observation_archive import first_difference
from subject7_first_ridders_stencil import base_problem, HGFX, MATLAB
from original_x0_unitsq_arithmetic_python import SOURCE_H,SOURCE_M,SOURCE_AUDIT

ORIGINAL_RUN="42408646109"
ORIGINAL_SHA="8e9a21e62efc5099e7e519bbf13b44f505cd1ad8"
SOURCE_SHA={
 "authentic-hgfx-71x128x2-unitsq-arithmetic.json":"0afd513e73549143f210cbf83360439bb144913116c6f794212425754ce935b6",
 "authentic-matlab-71x128x2-unitsq-arithmetic.json":"343528058e711737d12105ae3b70b7dcfeecce6232d0d195478c38d163791413",
 "independent-original-71x128x2-unitsq-first-arithmetic-stage.json":"9a65d743a13f1da62e6751e4636605d9c712b6bb1575debfae515006fb2abb7c",
}


def need(ok,msg):
    if not ok:raise ValueError(msg)


def load_sha(path,expected):
    raw=path.read_bytes()
    need(sha256(raw).hexdigest()==expected,
         "Immutable original true-source intermediate SHA-256 changed: "+path.name)
    return json.loads(raw),raw


def replay(root,bfgs,real_source,oldstage,out):
    prior={}
    raw={}
    for name,sha in SOURCE_SHA.items():
        prior[name],raw[name]=load_sha(real_source/name,sha)
    previous={}
    for name,sha in (("original-hgfx-71-infstates-and-native-ll.json",SOURCE_H),
                     ("original-matlab-71-infstates-and-cross-ll.json",SOURCE_M),
                     ("independent-hgf-infstates-unitsq-71-source-stage.json",SOURCE_AUDIT)):
        previous[name],_=load_sha(oldstage/name,sha)
    oldh=previous["original-hgfx-71-infstates-and-native-ll.json"]
    oldm=previous["original-matlab-71-infstates-and-cross-ll.json"]
    oldaudit=previous["independent-hgf-infstates-unitsq-71-source-stage.json"]
    need(oldaudit["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and oldaudit["per_comparison_nodes_with_at_least_one_trial_difference"]["zeta"]==0
         and len(oldaudit["all_original_nodes_and_counterfactual_trial_indices"])==71,
         "Authentic old independent MATLAB/HGFX source-stage audit changed")
    oldh["old_hgfx_on_matlab_predictor"]=[
        z["hgfx_unitsq_on_matlab_pred_logp"]
        for z in oldaudit["all_original_nodes_and_counterfactual_trial_indices"]]
    _,fit=base_problem(root,bfgs)
    data=report(
        prior["authentic-hgfx-71x128x2-unitsq-arithmetic.json"],
        prior["authentic-matlab-71x128x2-unitsq-arithmetic.json"],
        oldh,oldm,fit,
        raw["authentic-hgfx-71x128x2-unitsq-arithmetic.json"],
        prior["authentic-hgfx-71x128x2-unitsq-arithmetic.json"]["environment"]["github_run_id"],
        prior["authentic-hgfx-71x128x2-unitsq-arithmetic.json"]["environment"]["github_sha"],
    )
    data["source_matlab_arithmetic_sha256"]=SOURCE_SHA["authentic-matlab-71x128x2-unitsq-arithmetic.json"]
    original=prior["independent-original-71x128x2-unitsq-first-arithmetic-stage.json"]
    need(data["status"]=="VALIDATED_SAME_X_SOURCE_FORMULA_INTERMEDIATE_LOCALIZATION"
         and data["source_trial_comparisons_per_predictor"]==
         {"hgfx_predictor":9088,"matlab_predictor":9088}
         and data["source_native_exact_guard_failures"]==[]
         and data["formula_native_exact_guard_failures"]==[]
         and data["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS",
         "Original genuine source model or full 71x128x2 scientific failure controls changed")
    different=first_difference(data,original)
    result={
      "schema":"perf01d-genuine-original-unitsq-arithmetic-archive-deep-replay-v1",
      "status":("EXACT_FULL_ORIGINAL_UNITSQ_ARITHMETIC_STAGE_REPLAY"
                 if different is None else "NONEXACT_ORIGINAL_UNITSQ_ARITHMETIC_STAGE_REPLAY"),
      "original_source_run":ORIGINAL_RUN,"original_source_commit":ORIGINAL_SHA,
      "original_source_member_sha256":SOURCE_SHA,
      "previous_original_hgf_source_sha256":{"hgfx":SOURCE_H,"matlab":SOURCE_M,"audit":SOURCE_AUDIT},
      "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
      "original_fitting":"63/64 SCIENTIFIC NONPASS",
      "original_failed_subject7_traj_mu":4,"original_failed_subject7_traj_muhat":4,
      "first_full_report_difference":different,
      "new_independently_reconstructed_report":data,
      "external_independent_scientific_review":"NOT_RECEIVED",
      "original_perf01c":"NOT_FROZEN",
      "paper_speedup":"NOT_RUN","physical_gpu":"NOT_RUN",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":result["status"],
                      "original_source":ORIGINAL_RUN,
                      "first_difference":different,
                      "original_63_64":"SCIENTIFIC NONPASS",
                      "effective_first_differing_stage_freq":
                       data["effective_first_differing_stage_freq"]},sort_keys=True))
    need(different is None,"Immutable original full 71x128x2 arithmetic stage summary NOT exact: "+str(different))


def main():
    p=argparse.ArgumentParser()
    for field in ("root","old-bfgs","real-source","old-stage","output"):
        p.add_argument("--"+field,required=True,type=Path)
    a=p.parse_args()
    replay(a.root,a.old_bfgs,a.real_source,a.old_stage,a.output)


if __name__=="__main__":
    main()
