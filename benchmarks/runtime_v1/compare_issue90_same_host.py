#!/usr/bin/env python3
"""Within-ONE-runner OpenBLAS dispatched-kernel binary64 audit, not a science gate.

Input: three separately started Python processes with same SHA-locked BFGS
source, NumPy/version/hardware, differing only OPENBLAS_CORETYPE. Captured
float bits are measurements; no numerical tolerance or fitting decision.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MODES=("auto","Haswell","SkylakeX")
STATUS="CONTROLLED_SAME_RUNNER_FLOAT_DISPATCH_DIAGNOSTIC_NO_GATE_PASS"
ORIGINAL_SHA={
    "hgfx_raw.json":"060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce",
    "matlab_raw.json":"4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a",
}


def audited(report:dict,mode:str)->dict:
    if (report.get("schema")!="perf01d-issue90-host-binary64-ulp-audit-v1"
            or report.get("status")!="ENGINEERING_ULP_MEASUREMENTS_ONLY_NOT_EXACT_REPLAY_PASS"
            or report.get("original_bfgs_run")!="42187240378"
            or report.get("original_bfgs_raw_sha256")!=ORIGINAL_SHA
            or report.get("original_fitting_science")!="63/64 non-PASS, subject index 7 traj.mu/traj.muhat"
            or report.get("total_original_engine_history_rows")!=48):
        raise ValueError(f"Invalid {mode} immutable source/scientific status")
    rows=report.get("rows")
    if len(rows)!=48 or {(r["engine"],r["record_index_zero_based"])
                         for r in rows} != {(e,i) for e in ("hgfx","matlab") for i in range(24)}:
        raise ValueError(f"{mode}: duplicate/incomplete source row inventory")
    if mode=="auto":
        if report["runtime"]["environment"]["OPENBLAS_CORETYPE"] not in (None,""):
            raise ValueError("auto: OPENBLAS_CORETYPE must be unset")
    elif report["runtime"]["environment"]["OPENBLAS_CORETYPE"]!=mode:
        raise ValueError(f"{mode}: forced OpenBLAS core was not recorded")
    pool=report["runtime"].get("thread_pools",[])
    if not any(p.get("internal_api")=="openblas" for p in pool):
        raise ValueError(f"{mode}: missing effective OpenBLAS provenance")
    return {(r["engine"],int(r["record_index_zero_based"])):r for r in rows}


def compare(reports:dict)->dict:
    if set(reports)!=set(MODES):
        raise ValueError("Exactly original three same-host dispatch modes are required")
    indexed={mode:audited(reports[mode],mode) for mode in MODES}
    environments=[reports[mode]["runtime"] for mode in MODES]
    if (len({e["platform"] for e in environments})!=1
            or len({e["python"] for e in environments})!=1
            or len({e["numpy"] for e in environments})!=1
            or len({e["linux_cpu_model"] for e in environments})!=1
            or len({e["environment"]["GITHUB_RUN_ID"] for e in environments})!=1):
        raise ValueError("Not same physical runner/run/version/CPU; reject controlled comparison")
    if environments[0]["numpy"]!="2.3.5":
        raise ValueError("Audit NumPy version changed without explicit protocol update")
    rows=[]
    for engine in ("hgfx","matlab"):
        for i in range(24):
            r={m:indexed[m][(engine,i)] for m in MODES}
            # All modes must target SAME archived norm/slope bits, not mixed source.
            for field in ("numpy_norm_vs_archived","numpy_slope_vs_archived"):
                if len({r[m][field]["archived_bits"] for m in MODES})!=1:
                    raise ValueError(f"Original {field} changed across dispatch modes at {engine}:{i}")
            row={"engine":engine,"record_index_zero_based":i}
            for field,short in (("numpy_norm_vs_archived","norm"),("numpy_slope_vs_archived","slope")):
                row[short+"_bits"]={m:r[m][field]["current_bits"] for m in MODES}
                row[short+"_archive_bits"]=r["auto"][field]["archived_bits"]
                row[short+"_auto_eq_haswell"]=bool(r["auto"][field]["current_bits"]==r["Haswell"][field]["current_bits"])
                row[short+"_auto_eq_skylakex"]=bool(r["auto"][field]["current_bits"]==r["SkylakeX"][field]["current_bits"])
                row[short+"_haswell_eq_archived"]=bool(r["Haswell"][field]["current_bits"]==row[short+"_archive_bits"])
                row[short+"_skylakex_eq_archived"]=bool(r["SkylakeX"][field]["current_bits"]==row[short+"_archive_bits"])
            rows.append(row)
    def count(field,predicate):
        return sum(bool(row[field])==predicate for row in rows)
    return {
        "schema":"perf01d-issue90-within-runner-dispatch-comparison-v1",
        "status":STATUS,
        "original_bfgs_source_run":"42187240378",
        "original_raw_sha256":ORIGINAL_SHA,
        "shared_host":{"platform":environments[0]["platform"],
                       "linux_cpu_model":environments[0]["linux_cpu_model"],
                       "numpy":environments[0]["numpy"],
                       "github_run_id":environments[0]["environment"]["GITHUB_RUN_ID"]},
        "effective_blas_architecture":{m:next(p.get("architecture") for p in reports[m]["runtime"]["thread_pools"] if p.get("internal_api")=="openblas")
                                        for m in MODES},
        "archived_norm_mismatch_counts":{m:reports[m]["archived_numpy_norm_ulp_mismatches"] for m in MODES},
        "archived_slope_mismatch_counts":{m:reports[m]["archived_numpy_slope_ulp_mismatches"] for m in MODES},
        "norm_auto_vs_haswell_differing_rows":count("norm_auto_eq_haswell",False),
        "slope_auto_vs_haswell_differing_rows":count("slope_auto_eq_haswell",False),
        "norm_auto_vs_skylakex_differing_rows":count("norm_auto_eq_skylakex",False),
        "slope_auto_vs_skylakex_differing_rows":count("slope_auto_eq_skylakex",False),
        "total_source_rows":len(rows),
        "record_bits":rows,
        "limitations":[
            "Single GitHub runner controls observed CPU/OS/Python/NumPy, but still not an experimental reproduction of archived original runner CPU/kernel.",
            "Only derived dot/norm binary64 operations are compared. No fitting, output trajectory, CPU benchmark time, physical GPU or external scientific approval.",
            "Changing OpenBLAS dispatch to get matching archived decimal representations is a diagnostic intervention, not a validated scientific method or permission to change production optimiser.",
            "Original scientific 63/64 and external review issue #88 remain blocking. Original strict bitwise replay failures remain preserved at issue #90.",
        ],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--auto",type=Path,required=True)
    ap.add_argument("--haswell",type=Path,required=True)
    ap.add_argument("--skylakex",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    modes={
        "auto":json.loads(a.auto.read_bytes()),
        "Haswell":json.loads(a.haswell.read_bytes()),
        "SkylakeX":json.loads(a.skylakex.read_bytes()),
    }
    report=compare(modes)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":STATUS,
        "github_run_id":report["shared_host"]["github_run_id"],
        "cpu":report["shared_host"]["linux_cpu_model"],
        "blas":report["effective_blas_architecture"],
        "auto_vs_haswell_norm":report["norm_auto_vs_haswell_differing_rows"],
        "auto_vs_haswell_slope":report["slope_auto_vs_haswell_differing_rows"],
        "auto_vs_skylakex_norm":report["norm_auto_vs_skylakex_differing_rows"],
        "auto_vs_skylakex_slope":report["slope_auto_vs_skylakex_differing_rows"],
        "archived_norm":report["archived_norm_mismatch_counts"],
        "archived_slope":report["archived_slope_mismatch_counts"],
    },sort_keys=True))


if __name__=="__main__":
    main()
