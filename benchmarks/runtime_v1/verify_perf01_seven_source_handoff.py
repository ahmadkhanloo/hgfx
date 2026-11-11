#!/usr/bin/env python3
"""PERF-01C seven-source raw-archive replay, author side only.

Existing 6 original scientific artifact sets are replayed by the *unchanged*
six-source scientific comparator. Seventh source: four original HGFX v1.0.0
ABBA fits from CI run 42249566219, with their original raw SHA256 and BLAS
metadata. This is NOT an independent review, matched-host MATLAB replication,
final timing, GPU evidence or a change to original 63/64 NONPASS.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from verify_evidence_regression import verify as verify_original_six
from compare_subject7_same_host_repeatability_v2 import derive, ORDER
from verify_perf01_prefreeze_ledger import load as load_tracked, verify as verify_tracked

TRACKED_ABBA_SHA256 = "7898bee80dd50a53b2ae9605fdf10d4e9562ef3b45783fb103a822a1ec619730"
RAW_SOURCE_RUN = "42249566219"
RAW_SOURCE_SHA = "c84e76ac15779357b620a3d273add224cad2cdf5"
ANALYSIS_RUN = "42250539438"
ANALYSIS_SHA = "9b8d6cd69382248ac1fabdff92fd242992cf63e9"
EXPECTED_RAW = {
    "SkylakeX_1":"8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2",
    "Haswell_1":"10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a",
    "Haswell_2":"10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a",
    "SkylakeX_2":"8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2",
}
EXPECTED_ORIGINAL = {
    "SkylakeX_1": ["traj.mu","traj.muhat"],
    "SkylakeX_2": ["traj.mu","traj.muhat"],
    "Haswell_1": ["traj.epsi","traj.mu","traj.muhat","traj.psi"],
    "Haswell_2": ["traj.epsi","traj.mu","traj.muhat","traj.psi"],
}
PAIRS = {
    "SkylakeX_within_mode": (),
    "Haswell_within_mode": (),
    "cross_mode_first": ("traj.mu","traj.muhat"),
    "cross_mode_second": ("traj.mu","traj.muhat"),
    "cross_mode_interleaved_a": ("traj.mu","traj.muhat"),
    "cross_mode_interleaved_b": ("traj.mu","traj.muhat"),
}
TRIAL_FAILS = ("traj.mu","traj.muhat")
STATUS = "AUTHOR_SIDE_SEVEN_RAW_SOURCES_REPLAY_MATCH_DECISIONS_NOT_INDEPENDENT_REVIEW"
def require(cond, label):
    if not cond:
        raise AssertionError(label)

def digest(p: Path):
    return sha256(p.read_bytes()).hexdigest()

def decision_digest(data):
    """Stable *decisions* only. Descriptive floating reductions are not normalized or discarded."""
    def numeric(v):
        require(v["field_count"] == len(v["fields"]) == 28, "original 28 numeric fields")
        return {
            "field_count":28, "classification":v["classification"],
            "mismatched_fields":v["mismatched_fields"],
            "fields":{k:{p:row[p] for p in ("atol","rtol","mismatch_count",
                       "status","first_mismatch_index_zero_based")}
                      for k,row in sorted(v["fields"].items())},
            "critical_indices":{k:[r["index_zero_based"] for r in v["critical_field_mismatch_details"][k]]
                                for k in TRIAL_FAILS},
        }
    def strict(v):
        require(v["field_count"] == len(v["fields"]) == 28, "original 28 binary64 fields")
        return {
            "field_count":28,
            "all_serialized_binary64_equal":v["all_serialized_binary64_equal"],
            "fields":{k:{p:row[p] for p in ("shape","serialized_binary64_equal",
                   "differing_serialized_binary64_values","finite_mask_equal")}
                      for k,row in sorted(v["fields"].items())},
        }
    return {
        "pairwise":{k:{"numeric":numeric(v["original_numeric_tolerances"]),
                       "binary64":strict(v["strict_serialized_binary64"]),
                       "left":v["left"],"right":v["right"]}
                    for k,v in sorted(data["pairwise"].items())},
        "vs_original":{k:{"matlab":numeric(v["vs_original_matlab"]),
                           "hgfx":numeric(v["vs_original_hgfx"])}
                       for k,v in sorted(data["vs_original"].items())},
    }

def check_derived(new, recorded):
    require(new["status"] == recorded["status"] ==
            "AUTHOR_SIDE_ABBA_V2_EXPLICIT_CORES_DIAGNOSTIC_ORIGINAL_63_OF_64_NONPASS",
            "original 63/64 scientific NONPASS status must remain")
    require(new["original_science"] == recorded["original_science"] ==
            "63/64 NONPASS; original subject zero-based 7", "science status")
    for fld in ("frozen_hgfx_sha","frozen_matlab_sha","original_64_fit_run",
                "original_64_raw_sha256","original_failed_fields","original_failed_cells",
                "environment","fresh_raw_sha256","same_runner_control","schema"):
        require(new[fld] == recorded[fld], "historical provenance modified: "+fld)
    require(set(new["pairwise"]) == set(PAIRS)
            and set(new["vs_original"]) == set(ORDER),
            "ABBA six-pair and four-reference denominators")
    for name, pair in new["pairwise"].items():
        required=list(PAIRS[name])
        numeric=pair["original_numeric_tolerances"]
        binary=pair["strict_serialized_binary64"]
        require(numeric["mismatched_fields"] == required
                and binary["all_serialized_binary64_equal"] == (not required),
                "ABBA original-tolerance/bitwise condition: "+name)
        for field in TRIAL_FAILS:
            require(len(numeric["critical_field_mismatch_details"][field]) ==
                    (4 if required else 0), "ABBA critical trial count: "+name)
    for name, v in new["vs_original"].items():
        expected=EXPECTED_ORIGINAL[name]
        matlab=v["vs_original_matlab"]
        require(matlab["mismatched_fields"] == expected and
                all(len(matlab["critical_field_mismatch_details"][field]) ==
                    (4 if name.startswith("SkylakeX") else 14) for field in TRIAL_FAILS),
                "original MATLAB 4/14 subject-7 field failures: "+name)
    fingerprint_new=decision_digest(new)
    fingerprint_old=decision_digest(recorded)
    require(fingerprint_new == fingerprint_old,
            "ABBA source replay changed old-tolerance/bitwise per-field DECISIONS")
    # Compare complete JSON to archive without silently normalizing float drift:
    new_without_provenance={k:v for k,v in new.items() if k!="analysis_provenance"}
    old_without_provenance={k:v for k,v in recorded.items() if k!="analysis_provenance"}
    return {
        "complete_derived_report_exact_except_analysis_provenance":
            new_without_provenance == old_without_provenance,
        "all_six_pairwise_and_four_reference_28_field_decisions_match":True,
        "descriptive_floats_recomputed_without_changing_original_tolerances":True,
    }

def replay(root: Path, archives: Path, abba_raw: Path):
    original_six=verify_original_six(root, archives)
    tracked, tracked_sha = load_tracked(root.parents[1])
    tracked_verdict=verify_tracked(tracked)
    require(tracked_verdict["status"] ==
            "AUTHOR_SIDE_TRACKED_LEDGER_CONSISTENT_NOT_INDEPENDENT_REVIEW",
            "tracked derived coherence regression")
    frozen_raw=abba_raw / "four_fits"
    environment={}
    raw_hashes={}
    for name in ORDER:
        rawfile=frozen_raw/(name+"_raw.json")
        envfile=frozen_raw/(name+"_environment.json")
        require(digest(rawfile)==EXPECTED_RAW[name], "source original ABBA SHA256: "+name)
        meta=json.loads(envfile.read_bytes())
        require(meta["run_id"]==RAW_SOURCE_RUN and meta["github_sha"]==RAW_SOURCE_SHA
                and meta["raw_sha256"]==EXPECTED_RAW[name],
                "source original ABBA environment identity: "+name)
        environment[name]=meta
        raw_hashes[name]=EXPECTED_RAW[name]
    environment_file=abba_raw/"environments.json"
    environment_file.write_text(json.dumps(environment,sort_keys=True,indent=2)+"\n")
    source_dir=archives/"41863441006"
    summary=root/"fit_cohort_results/summary-41863441006.json"
    require(summary.is_file(), "original 64-source summary missing")
    # Derive original summary path using a *separate* input folder so the archive remains immutable.
    from shutil import copy2
    original_input=abba_raw/"original_64"
    original_input.mkdir(parents=True,exist_ok=True)
    for name in ("hgfx_raw.json","matlab_raw.json"):
        copy2(source_dir/name,original_input/name)
    copy2(summary,original_input/summary.name)
    new=derive(original_input,frozen_raw,environment_file)
    recorded_path=root/"issue90_results/derived-archived-v2-42250539438.json"
    require(digest(recorded_path)==TRACKED_ABBA_SHA256,
            "original ABBA derived report tracked SHA256 changed")
    recorded=json.loads(recorded_path.read_bytes())
    require(recorded["analysis_provenance"]["analysis_run_id"]==ANALYSIS_RUN
            and recorded["analysis_provenance"]["analysis_sha"]==ANALYSIS_SHA
            and recorded["analysis_provenance"]["archived_source_run_id"]==RAW_SOURCE_RUN,
            "archived original analysis attribution changed")
    matching=check_derived(new, recorded)
    return {
        "status":STATUS,
        "scope":"7 ORIGINAL ARCHIVED SOURCE RUNS, 4 ABBA HGFX FIT RAW FILES, NO NEW FIT",
        "six_original_sources":original_six,
        "tracked_ledger":tracked_verdict,
        "tracked_derived_report_sha256":tracked_sha,
        "seventh_abba_original_raw_sha256":raw_hashes,
        "seventh_abba_source_run_id":RAW_SOURCE_RUN,
        "seventh_abba_original_source_sha":RAW_SOURCE_SHA,
        "seventh_abba_archived_analysis_run_id":ANALYSIS_RUN,
        "seventh_abba_28_field_decisions":matching,
        "seventh_abba_recomputed_full_derived_report":new,
        "seventh_abba_archived_derived_report_sha256":TRACKED_ABBA_SHA256,
        "scientific_full_fit":"63/64 NONPASS; original zero-based subject 7",
        "reviewer_signature":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "final_performance_timing":"NOT_RUN",
    }
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,
                        default=Path(__file__).resolve().parent)
    parser.add_argument("--archives",type=Path,required=True)
    parser.add_argument("--abba",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=replay(args.root,args.archives,args.abba)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":result["status"],"archived_six_source":result["six_original_sources"]["status"],
        "same_runner_abba_original_four_sha256":"4/4",
        "abba_stable_decisions":result["seventh_abba_28_field_decisions"],
        "original_science":"63/64 NONPASS",
        "reviewer_signature":"NOT_RECEIVED","performance_timing":"NOT_RUN",
    },sort_keys=True))
if __name__=="__main__":
    main()
