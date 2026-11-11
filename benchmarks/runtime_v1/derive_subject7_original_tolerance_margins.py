#!/usr/bin/env python3
"""Original-tolerance exceedance/lag diagnostic for subject 7 (author side).

Consumes SHA-pinned, already archived ABBA v2 JSON, no new model execution.
Does not reclassify the original 63/64 scientific NONPASS or time anything.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = "benchmarks/runtime_v1/issue90_results/derived-archived-v2-42250539438.json"
SOURCE_SHA256 = "7898bee80dd50a53b2ae9605fdf10d4e9562ef3b45783fb103a822a1ec619730"
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
TRAJ = ("traj.mu", "traj.muhat")
MODES = ("SkylakeX_1", "Haswell_1", "Haswell_2", "SkylakeX_2")
PAIR_NAMES = (
    "SkylakeX_within_mode", "Haswell_within_mode",
    "cross_mode_first", "cross_mode_second",
    "cross_mode_interleaved_a", "cross_mode_interleaved_b",
)
STATUS = "AUTHOR_SIDE_ORIGINAL_TOLERANCE_EXCEEDANCE_63_OF_64_NONPASS"

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)

def check_pair(report: dict, expected_mismatch: list[str]) -> dict:
    """Compute every failed-cell exceedance using the *original* rtols/atols."""
    require(report["field_count"] == len(report["fields"]) == 28,
            "original 28-field set has changed")
    require(report["mismatched_fields"] == expected_mismatch,
            "original field mismatch classification changed")
    critical = report["critical_field_mismatch_details"]
    require(set(critical) == set(TRAJ), "original critical field set changed")
    details = {}
    expected_n = 0 if not expected_mismatch else (14 if "traj.psi" in expected_mismatch else 4)
    for field in TRAJ:
        spec = report["fields"][field]
        rows = critical[field]
        require(spec["rtol"] == 3e-8 and spec["atol"] == 3e-10,
                "unchanged original trajectory tolerance changed")
        require(len(rows) == spec["mismatch_count"] == expected_n,
                "original number of failed trialwise cells changed")
        require(spec["status"] == ("MISMATCH" if rows else
                                   "WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"),
                "original mismatch status changed")
        if rows:
            require(spec["first_mismatch_index_zero_based"] == rows[0]["index_zero_based"],
                    "original first mismatch location changed")
        computed = []
        for item in rows:
            i = item["index_zero_based"]
            require(isinstance(i,list) and len(i)==2 and i[1]==1 and 0<=i[0]<128,
                    "original failed trial/level changed")
            x = float(item["reference_value"])
            y = float(item["hgfx_value"])
            difference = abs(x-y)
            tolerance = 3e-10 + 3e-8 * abs(x)
            require(all(math.isfinite(z) for z in (difference, tolerance)) and tolerance>0,
                    "nonfinite original numerical data")
            require(math.isclose(difference, item["abs_difference"], rel_tol=1e-12, abs_tol=2e-18)
                    and math.isclose(tolerance, item["unchanged_tolerance_bound_at_reference"],
                                     rel_tol=1e-12, abs_tol=2e-18),
                    "original residual or tolerance-bound numerical evidence modified")
            require(difference>tolerance, "previously failed cell is now within tolerance")
            require(item["trial_one_based"]==i[0]+1 and item["level_one_based"]==2,
                    "original trial or level presentation changed")
            computed.append({
                "index_zero_based":i,
                "trial_one_based":i[0]+1,
                "reference_value":x,
                "other_value":y,
                "abs_difference":difference,
                "original_atol":spec["atol"],
                "original_rtol":spec["rtol"],
                "original_tolerance_bound":tolerance,
                "exceedance_ratio":difference/tolerance,
            })
        details[field]={"failed_cells":len(computed),
                        "max_exceedance_ratio":max((r["exceedance_ratio"]
                                                  for r in computed),default=None),
                        "cells":computed}
    mu, muhat = details["traj.mu"]["cells"], details["traj.muhat"]["cells"]
    require(len(mu)==len(muhat), "trajectory field failure counts disagree")
    for left,right in zip(mu,muhat):
        require(right["index_zero_based"] == [left["index_zero_based"][0]+1,
                                              left["index_zero_based"][1]]
                and left["reference_value"] == right["reference_value"]
                and left["other_value"] == right["other_value"],
                "one-trial mu -> muhat lag does not hold for original failed cells")
    return details

def analyze(archive: dict, raw_sha256: str) -> dict:
    require(raw_sha256 == SOURCE_SHA256, "recorded source report SHA256 changed")
    require(archive["status"] ==
            "AUTHOR_SIDE_ABBA_V2_EXPLICIT_CORES_DIAGNOSTIC_ORIGINAL_63_OF_64_NONPASS"
            and archive["original_science"]=="63/64 NONPASS; original subject zero-based 7"
            and archive["frozen_hgfx_sha"]==HGFX_SHA
            and archive["frozen_matlab_sha"]==MATLAB_SHA
            and archive["original_64_fit_run"]=="41863441006"
            and archive["original_failed_fields"]==list(TRAJ)
            and archive["original_failed_cells"]=={field:4 for field in TRAJ},
            "original scientific result/source identity changed")
    provenance=archive["analysis_provenance"]
    require(provenance["analysis_run_id"]=="42250539438"
            and provenance["archived_source_run_id"]=="42249566219"
            and provenance["not_new_fitting"] is True
            and provenance["original_63_64_unchanged"] is True
            and provenance["original_numeric_tolerances_unchanged"] is True,
            "original ABBA fit/replay provenance changed")
    require(set(archive["vs_original"]) == set(MODES)
            and set(archive["pairwise"]) == set(PAIR_NAMES),
            "four source modes or six predeclared comparisons missing")
    reference = {}
    for mode in MODES:
        expected = list(TRAJ) if mode.startswith("SkylakeX") else [
            "traj.epsi", "traj.mu", "traj.muhat", "traj.psi"]
        reference[mode] = check_pair(
            archive["vs_original"][mode]["vs_original_matlab"], expected)
    pairs = {}
    for label in PAIR_NAMES:
        pair=archive["pairwise"][label]
        expected=[] if "within_mode" in label else list(TRAJ)
        strict=pair["strict_serialized_binary64"]
        require(strict["field_count"]==len(strict["fields"])==28
                and strict["all_serialized_binary64_equal"] == (not expected),
                "ABBA same-mode binary equality or cross-mode mismatch changed")
        pairs[label] = check_pair(pair["original_numeric_tolerances"], expected)
    def compact(items):
        return {key:{"failed_mu_cells":value["traj.mu"]["failed_cells"],
                     "failed_muhat_cells":value["traj.muhat"]["failed_cells"],
                     "max_mu_exceedance_ratio":value["traj.mu"]["max_exceedance_ratio"],
                     "failed_mu_trials_one_based":[v["trial_one_based"]
                                      for v in value["traj.mu"]["cells"]]}
                for key,value in items.items()}
    return {
        "schema":"perf01d-issue90-original-tolerance-margin-v1",
        "status":STATUS,
        "source_report_sha256":raw_sha256,
        "frozen_hgfx_sha":HGFX_SHA, "frozen_matlab_sha":MATLAB_SHA,
        "archived_source_run_id":"42249566219",
        "archived_replay_run_id":"42250539438",
        "archived_original_matlab_run_id":"41863441006",
        "same_runner_blas_cross_mode":pairs,
        "cross_run_original_matlab":reference,
        "same_runner_summary":compact(pairs),
        "original_matlab_summary":compact(reference),
        "inherited_tolerances":{"atol":3e-10,"rtol":3e-8},
        "original_fit":"63/64 SCIENTIFIC NONPASS; original subject index 7",
        "independent_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN",
        "limitations":[
            "All exceedance ratios use unchanged old acceptance thresholds and are descriptive, not a new pass gate.",
            "Archived MATLAB-vs-HGFX comparisons are cross-run/different-host, not simultaneous same-host MATLAB fits.",
            "Only recorded failing cells are compared here, not full scientific optimizer trajectories or model identifiability.",
            "No new MATLAB execution, HGFX fit, physical GPU or performance timing was performed.",
        ],
    }

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    original=(args.root/SOURCE).read_bytes()
    result=analyze(json.loads(original),hashlib.sha256(original).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":result["status"],"vs_original_matlab":result["original_matlab_summary"],
        "cross_blas":result["same_runner_summary"],
        "original_fit":"63/64 SCIENTIFIC NONPASS",
        "performance_timing":"NOT_RUN",
    },sort_keys=True))

if __name__=="__main__":
    main()
