#!/usr/bin/env python3
"""REV-2.1 original 324-case source-only pre-experiment feasibility auditor.

NO MATLAB, JAX, HGFX, participant data, observed trial values or numerical
experiment are evaluated. Do not auto-repair a native M12B vector whose
*free* transformed logit centre is mathematically undefined.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from hashlib import sha1,sha256
import json
import math
from pathlib import Path
import re
from zipfile import ZipFile

RUN_ID = "41809919116"
RUN_HEAD = "e09f72020dbab52f2d73b90ff4d9ee40999b9fae"
ZIP_SHA256 = "1adfd1cd69b6f7d7a89ba2c8b9d564e774fd8a8841fa7243d6972605bd9f7391"
MEMBER_SHA256 = "47432c35aa4914a652a8f1dc2aad81dc4d76fb5175dd0fc1fd47532b81756b70"
BASELINE_BLOB = "fd9ea7d1f1cd00eb0f9ea5aecbe37ae09d299275"
MATLAB_REF = "2437f4dc241541072722a2695ddeca7b44d83dd3"
MATLAB_CONFIG_BLOB = "c05a77f1c3b9a0b820120b9dcbd05c5a65857925"
MATLAB_TRANSFORM_BLOB = "de46708de2d0af43e5fc26f12a4c27510743e725"
SELECTION_SEED = 2026111021
SELECTION_SHA256 = "adcb0e8694e72c8c82e4ae3416d54d409273729dea0558b9c3e31043d5c06047"
PHI2_ZERO_BASED = 7
PHI3_ZERO_BASED = 8
DEFAULT_NATIVE_BASELINE = (math.nan,0.0,1.0,math.nan,.1,1.0,
                           math.nan,0.0,.2,math.nan,0.0,1.0,
                           1.0,1.0,math.nan,-2.0,-6.0)
STATUS = "BLOCKED_M12B_TRANSFORMED_BASELINE_UNDEFINED"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def git_blob_id(data: bytes) -> str:
    return sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()


def parse_scalar(node: ast.AST) -> float:
    """Only literal numeric values or explicitly typed np.nan; no eval()."""
    if isinstance(node, ast.Constant) and type(node.value) in (float,int):
        return float(node.value)
    if (isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub)):
        return -parse_scalar(node.operand)
    if (isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name)
            and node.value.id=="np" and node.attr=="nan"):
        return math.nan
    raise ValueError("Source vector contains a nonliteral parameter")


def parse_original_native_vector(text: str) -> tuple[float,...]:
    tree=ast.parse(text)
    candidates=[]
    for assignment in tree.body:
        if not isinstance(assignment,ast.Assign):
            continue
        if not any(isinstance(x,ast.Name) and x.id=="P" for x in assignment.targets):
            continue
        call=assignment.value
        require(isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute)
                and isinstance(call.func.value,ast.Name)
                and call.func.value.id=="np" and call.func.attr=="asarray"
                and len(call.args)==1 and isinstance(call.args[0],ast.List),
                "Original P definition is not a static NumPy literal vector")
        candidates.append(tuple(parse_scalar(v) for v in call.args[0].elts))
    require(len(candidates)==1 and len(candidates[0])==17,
            "Expected one original 17-element native M12B vector")
    return candidates[0]


def original_statuses(path: Path) -> tuple[list[dict],dict]:
    raw=path.read_bytes()
    require(sha_bytes(raw)==ZIP_SHA256,"Original 324-case archive ZIP SHA mismatch")
    with ZipFile(path) as z:
        require(z.namelist()==["fullcohort_summary.json"],
                "Original warning archive member set changed")
        body=z.read("fullcohort_summary.json")
    require(sha_bytes(body)==MEMBER_SHA256,
            "Original fullcohort_summary.json SHA mismatch")
    doc=json.loads(body)
    require(doc.get("github_run_id")==RUN_ID
            and doc.get("expected_cases")==doc.get("total_cases")==324
            and doc.get("hgfx_wheel")=="1.0.0"
            and doc.get("overall_status")=="PASS_FIXED_VECTOR_PARITY_ALL_CASES"
            and doc.get("trials_in_source_grid")==25920,
            "Archived original science metadata drift")
    records=doc["per_case_statuses"]
    require(len(records)==324 and doc.get("warning_case_count")==48,
            "Archived status denominator drift")
    expected=([f"suthaharan_2021_{k:04d}" for k in range(1,261)]
              +[f"reed_2020_{k:04d}" for k in range(1,65)])
    require([x["id"] for x in records]==expected,
            "Unexpected case IDs/order in historical results")
    for row in records:
        require(row["status"]=="PASS_FIXED_VECTOR_FORWARD_PARITY"
                and row["failed_fields"]==[]
                and row["first_divergence"] is None
                and type(row["warnings"]) is int
                and type(row["ignored_trials"]) is int
                and row["warnings"]>=0 and row["ignored_trials"]>=0,
                "Original case/field status mismatch")
    histogram=Counter(x["warnings"] for x in records)
    require(histogram==Counter({0:276,1:29,3:19})
            and sum(x["warnings"] for x in records)==86
            and sum(x["ignored_trials"] for x in records)==293,
            "Original warning counts / ignored trials changed")
    require(all(x["warnings"]==0 and x["ignored_trials"]==0
                for x in records[:260]),"Suthaharan data warning status changed")
    return records,doc


def fixed_block_selection() -> dict:
    ids=[f"suthaharan_2021_{i:04d}" for i in range(1,261)]
    ranked=sorted(ids,key=lambda item:
                  (sha_bytes(f"{SELECTION_SEED}:{item}".encode("ascii")),item))
    chosen=sorted(ranked[:64])
    reed=[f"reed_2020_{i:04d}" for i in range(1,65)]
    require(len(chosen)==len(set(chosen))==64
            and len(reed)==len(set(reed))==64,
            "Precommitted source-independent selection invalid")
    digest=sha_bytes(("\n".join(chosen)+"\n").encode("ascii"))
    require(digest==SELECTION_SHA256,
            "Prerecorded Suthaharan block selection SHA256 mismatch")
    return {
        "seed":SELECTION_SEED,
        "rule":"rank SHA256(ASCII(f'{seed}:{source_case_id}')); lowest 64 of 260",
        "selected_suthaharan_blocks":64,
        "selected_suthaharan_case_ids_sha256":SELECTION_SHA256,
        "all_original_reed_blocks":64,
        "total_multivector_source_blocks":128,
        "selection_independent_of_scientific_outcomes":True,
        "raw_case_ids_exported":False,
    }


def inspect_phi2_domain(native: tuple[float,...],
                        config_source: str,transform_source: str) -> dict:
    require(len(native)==17,
            "M12B exact native vector must contain all 17 parameters")
    require(re.search(r"case\s+'hgf'[\s\S]*?c\.logitphisa\s*=\s*\[\s*NaN\s*,\s*1\s*,\s*1\s*\]",
                      config_source) is not None,
            "Original HGF phi2 transformed prior variance cannot be independently verified")
    require(re.search(r"pvec\(2\*l\+1:3\*l\)\s*=\s*tapas_sgm\(ptrans\(2\*l\+1:3\*l\),1\)",
                      transform_source) is not None,
            "Frozen MATLAB AR1 MAB phi transform differs from expected sigmoid")
    value=native[PHI2_ZERO_BASED]
    positive_variance=1.0  # independently checked by exact source regex above
    finite_inverse=math.isfinite(value) and 0.0<value<1.0
    result={
        "parameter":"phi2",
        "native_vector_index_zero_based":PHI2_ZERO_BASED,
        "native_value":value,
        "native_phi3_neighbor_value":native[PHI3_ZERO_BASED],
        "transformed_prior_variance":positive_variance,
        "is_free_under_original_hgf_prior":True,
        "finite_inverse_logit_exists":finite_inverse,
        "inverse_logit_when_finite":(math.log(value/(1.0-value))
                                    if finite_inverse else None),
        "model_parameter_space":"original M12B vector native; HGF priors transformed",
    }
    return result


def audit(*, original_zip: Path, original_source: Path,
          config_source: Path, transform_source: Path) -> dict:
    records,summary=original_statuses(original_zip)
    specs=[
        (original_source,BASELINE_BLOB,"original single-case source"),
        (config_source,MATLAB_CONFIG_BLOB,"MATLAB HGF prior config"),
        (transform_source,MATLAB_TRANSFORM_BLOB,"MATLAB native transform"),
    ]
    for file,expected,label in specs:
        require(git_blob_id(file.read_bytes())==expected,
                f"Wrong original source Git blob: {label}")
    native=parse_original_native_vector(original_source.read_text(encoding="utf-8"))
    require(all((math.isnan(a) and math.isnan(b)) or a==b
                for a,b in zip(native,DEFAULT_NATIVE_BASELINE)),
            "Original native M12B parameter vector differs from published source")
    phi2=inspect_phi2_domain(native,
                              config_source.read_text(encoding="utf-8"),
                              transform_source.read_text(encoding="utf-8"))
    blocked=phi2["is_free_under_original_hgf_prior"] and not phi2["finite_inverse_logit_exists"]
    require(blocked,"This frozen source-only guard requires explicit new protocol review if source permits transformed baseline")
    return {
        "task":"REV-2.1",
        "audit":"PRE_EXECUTION_SOURCE_ONLY_2026_11_10",
        "status":STATUS,
        "scientific_or_model_executions":0,
        "fullcohort_original_run":int(RUN_ID),
        "fullcohort_original_run_head":RUN_HEAD,
        "original_hgfx_release":"1.0.0",
        "reference_hgf_commit":MATLAB_REF,
        "original_archive_zip_sha256":ZIP_SHA256,
        "original_summary_member_sha256":MEMBER_SHA256,
        "original_324_cases":len(records),
        "original_260_suthaharan_blocks":260,
        "original_64_reed_blocks":64,
        "original_warning_blocks":summary["warning_case_count"],
        "original_warning_events":sum(x["warnings"] for x in records),
        "original_ignored_trials":sum(x["ignored_trials"] for x in records),
        "original_warning_types_available":False,
        "source_git_blobs":{
            "original_compare_realdata_pair.py":BASELINE_BLOB,
            "hgf_ar1_binary_mab_config_base.m":MATLAB_CONFIG_BLOB,
            "hgf_ar1_binary_mab_transp.m":MATLAB_TRANSFORM_BLOB,
        },
        "selection":fixed_block_selection(),
        "baseline_transform_check":phi2,
        "mathematical_blocker":
            "Original native phi2=0 is FREE under the HGF transformed prior, "
            "but logit(0)=-Inf; no finite original M12B-centred transformed perturbation exists.",
        "no_clipping_or_imputation":True,
        "new_multivector_vectors_generated":0,
        "new_forward_cases_evaluated":0,
        "author_human_resolution_required_before_science":True,
        "original_REV24_and_D2_D3":"BLOCKED_UNCHANGED",
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-zip",type=Path,required=True)
    p.add_argument("--original-source",type=Path,required=True)
    p.add_argument("--config-source",type=Path,required=True)
    p.add_argument("--transform-source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    require(not a.output.exists(),"Do not overwrite existing preflight audit")
    result=audit(original_zip=a.original_zip,original_source=a.original_source,
                 config_source=a.config_source,transform_source=a.transform_source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,
                                   allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "archived_source_blocks":result["original_324_cases"],
        "archived_warning_blocks":result["original_warning_blocks"],
        "archived_warning_events":result["original_warning_events"],
        "phi2_native":result["baseline_transform_check"]["native_value"],
        "phi2_free":result["baseline_transform_check"]["is_free_under_original_hgf_prior"],
        "finite_inverse":result["baseline_transform_check"]["finite_inverse_logit_exists"],
        "scientific_executions":0,
        "output_sha256":sha_bytes(a.output.read_bytes())
    },sort_keys=True))


if __name__=="__main__":
    main()
