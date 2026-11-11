#!/usr/bin/env python3
"""PERF-01D: post-result gradient interposition at EXACT original MATLAB/HGFX x.

Counterfactual experiment only. Original frozen HGFX code is NOT modified.
Never count counterfactual optimizer outputs as scientific fitting parity or speed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from hashlib import sha256
from importlib import metadata
import json
import math
import os
from pathlib import Path
import platform
import struct
import traceback

import numpy as np

from subject7_direct_nested_gradient_bfgs import original_inventory, HASHES, REF, HGFX

SOURCE_50_RUN = "42305573614"
SOURCE_50_SHA = "b9ff63685aac7ecd10a7cc4d1c33a4dc28699a62"
PROTOCOL_SHA = "7049b23a6acf118038149a1bbbb31cb5d40da45f"
SOURCE50_SHA256 = {
    "locked-50-bfgs-anchors.json": "d92690111b2fa128c045f29b39aa95110b5e5cd838f90c48a733400a3e537913",
    "real-private-matlab-ridders.json": "90de6c75c13736fae95bc0645950ac0352546fd7262c4d5f70d97f8b9b14e978",
    "paired-direct-private-gradient-bfgs-margins.json": "2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d",
}
ARMS = (
    "baseline_unmodified",
    "placebo_original_hgfx_gradient_at_start",
    "matlab_gradient_start_component0",
    "matlab_gradient_start_all3",
    "matlab_gradient_record6_component0",
    "matlab_gradient_record6_all3",
    "matlab_gradient_start_and_record6_all3",
    "matlab_gradient_all_original_hgfx_history_25",
)
START = (-3.0,-6.0,3.871201010907891)
SIX = (-1.1621811570388512,-6.37816839506084,-0.23738383160834042)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def xyz_key(values):
    a = np.asarray(values, np.float64).reshape(-1)
    require(a.shape == (3,) and np.isfinite(a).all(),
            "Expected finite 3-vector for exact original source anchor")
    return tuple(struct.pack(">d",float(x)) for x in a)


def original_source_inventory(root, archived_bfgs, archived50):
    raw, _ = original_inventory(root, archived_bfgs)
    for name,h in SOURCE50_SHA256.items():
        require(sha(archived50/name) == h,
                "50-point genuine private MATLAB raw evidence was altered: " + name)
    paired = json.loads((archived50/"paired-direct-private-gradient-bfgs-margins.json").read_bytes())
    anchors = json.loads((archived50/"locked-50-bfgs-anchors.json").read_bytes())
    matlab = json.loads((archived50/"real-private-matlab-ridders.json").read_bytes())
    require(paired["source_original_64_full_fit"] == "63/64 SCIENTIFIC NONPASS"
            and paired["original_bfgs_run_id"] == "42187240378"
            and paired["original_bfgs_raw_sha256"] == HASHES
            and paired["source_original_zero_based_subject_7_failure"] == {"traj.mu":4,"traj.muhat":4}
            and paired["full_original_50_anchor_occurrences"] == 50
            and paired["fully_evaluated_matlab_private_gradients"] == 50
            and paired["instrumentation_neutral"] is True
            and paired["independent_scientific_review"] == "NOT_RECEIVED"
            and paired["perf01c"] == "NOT_FROZEN"
            and anchors["original_science"] == "63/64 NONPASS"
            and len(anchors["cases"]) == 50
            and matlab["github_run_id"] == SOURCE_50_RUN
            and matlab["github_sha"] == SOURCE_50_SHA
            and matlab["frozen_hgfx_sha"] == HGFX
            and matlab["frozen_matlab_sha"] == REF
            and matlab["same_session_28_fields_isequaln"] is True,
            "Direct private MATLAB 50-anchor source/report is not independently checked")
    rows = paired["all_50_original_same_x_paired_gradient_records"]
    require(len(rows) == 50, "All 50 source rows must remain present")
    require([r["anchor_origin"] for r in rows] == ["hgfx"]*25+["matlab"]*25
            and [r["record_index_zero_based"] for r in rows] == list(range(25))*2,
            "Original source order and denominators changed")
    for i in range(25):
        require(xyz_key(rows[i]["free_parameters"]) == xyz_key(raw["hgfx"]["iter_x"][i])
                and xyz_key(rows[25+i]["free_parameters"]) == xyz_key(raw["matlab"]["iter_x"][i])
                and rows[i]["matlab_status"] == rows[25+i]["matlab_status"] == "EVALUATED",
                "Original source fit and 50 direct private MATLAB observations mismatch")
    require(xyz_key(rows[0]["free_parameters"]) == xyz_key(START)
            and xyz_key(rows[6]["free_parameters"]) == xyz_key(SIX)
            and rows[6]["same_x_max_abs_gradient_component_difference"] == 6.884955006114524e-08
            and rows[6]["same_x_abs_objective_difference"] == 0.,
            "Selected counterexample was posthoc altered")
    for row in rows:
        for src in ("hgfx", "matlab"):
            g = np.asarray(row[src]["gradient"], float)
            require(g.shape == (3,) and np.isfinite(g).all(),
                    "Original direct MATLAB/HGFX source gradient incomplete")
    return raw, rows


def arm_sources(arm, hgfx_history_rows):
    require(arm in ARMS, "Unexpected or retrospectively selected arm")
    require(len(hgfx_history_rows) == 25, "Original HGFX history denominator changed")
    selected = []
    if "start_and_record6" in arm:
        selected = [0,6]
    elif arm.startswith("placebo_") or arm.startswith("matlab_gradient_start"):
        selected = [0]
    elif "record6" in arm:
        selected = [6]
    elif arm == "matlab_gradient_all_original_hgfx_history_25":
        selected = list(range(25))
    source = "hgfx" if arm.startswith("placebo_") else "matlab"
    table = {}
    for i in selected:
        row = hgfx_history_rows[i]
        key = xyz_key(row["free_parameters"])
        target = np.asarray(row[source]["gradient"], np.float64)
        require(target.shape == (3,) and np.isfinite(target).all(),
                "Archived original source gradient is incomplete")
        if key in table:
            require(np.array_equal(table[key]["target"], target),
                    "Repeated original history coordinate has conflicting gradients")
            table[key]["source_indices"].append(i)
        else:
            table[key] = {"target":target.copy(), "source_indices":[i], "source":source}
    return table


@contextmanager
def interposition(module, orig_gradient, arm, hgfx_history_rows, provenance):
    """Restore source gradient function even if optimizer fails."""
    require(module.ridders_gradient is orig_gradient, "Original frozen Ridders module already patched")
    mapping = arm_sources(arm,hgfx_history_rows)
    hit_keys = set()
    calls = []

    def swapped(fn, x, options=None):
        orig, err = orig_gradient(fn, x, options)
        orig = np.asarray(orig, np.float64).reshape(-1)
        err = np.asarray(err, np.float64).reshape(-1)
        require(orig.shape == err.shape == (3,)
                and np.isfinite(orig).all() and np.isfinite(err).all(),
                "Original frozen gradient/error nonfinite; counterfactual not comparable")
        key = xyz_key(x)
        injected = key in mapping
        out = orig.copy()
        components = []
        if injected:
            v = mapping[key]["target"]
            components = [0] if arm.endswith("component0") else [0,1,2]
            for component in components:
                out[component] = v[component]
            hit_keys.add(key)
        calls.append({
            "gradient_call_zero_based": len(calls),
            "exact_free_parameters": np.asarray(x,np.float64).reshape(-1).tolist(),
            "intervened": bool(injected),
            "source_original_hgfx_gradient": orig.tolist(),
            "source_original_hgfx_ridders_error": err.tolist(),
            "returned_diagnostic_gradient": out.tolist(),
            "replaced_component_indices_zero_based": components,
            "matched_original_source_history_slots_zero_based":
                mapping[key]["source_indices"] if injected else [],
            "substituted_from": mapping[key]["source"] if injected else None,
        })
        return out,err

    try:
        if arm != "baseline_unmodified":
            module.ridders_gradient = swapped
        provenance["intervention_sites_declared"] = [
            {"source_history_indices":val["source_indices"],
             "exact_free_parameters":list(np.frombuffer(b"".join(key),dtype=">f8")),
             "source":val["source"],"target_gradient":val["target"].tolist()}
            for key,val in mapping.items()
        ]
        provenance["calls"] = calls
        yield hit_keys, mapping
    finally:
        module.ridders_gradient = orig_gradient


def json_matrix(x):
    a = np.asarray(x,np.float64)
    def norm(v):
        return float(v) if math.isfinite(float(v)) else None
    if a.ndim == 1:
        return [norm(v) for v in a]
    return [[norm(v) for v in row] for row in a]


def host_provenance():
    cpu_info = ""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu_info=line.split(":",1)[1].strip()
                break
    except OSError:
        pass
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu_info or platform.processor(),
        "numpy": metadata.version("numpy"),
        "scipy": metadata.version("scipy"),
        "jax": metadata.version("jax"),
        "jaxlib": metadata.version("jaxlib"),
        "hgfx": metadata.version("hgfx"),
        "openblas_coretype": os.environ.get("OPENBLAS_CORETYPE","UNSET"),
        "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS","UNSET"),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS","UNSET"),
        "mkl_num_threads": os.environ.get("MKL_NUM_THREADS","UNSET"),
        "jax_platforms": os.environ.get("JAX_PLATFORMS","UNSET"),
        "runner_name": os.environ.get("RUNNER_NAME","UNSET"),
    }


def run(root, archive_bfgs, archive50, output):
    from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
    import hgfx.optim.compat_quasinewton as q

    require(metadata.version("hgfx") == "1.0.0",
            "Only original frozen HGFX v1.0.0 may serve as counterfactual base")
    raw, source_rows = original_source_inventory(root,archive_bfgs,archive50)
    base = json.loads((root/"inputs"/"binary_128_s64.json").read_bytes())
    problem = hgf_binary_unitsq_fit_problem(np.asarray(base["y"][7],np.float64),
                                             np.asarray(base["u"][7],np.float64))
    require(problem.free_indices == (12,13,14)
            and xyz_key(problem.initial_free) == xyz_key(START),
            "Original unchanged source start/config changed")
    opts = q.QuasiNewtonOptions(tol_grad=1e-3,tol_arg=1e-3,max_step=1.,
                                max_iter=100,max_regu=16,max_rst=10,
                                verbose=False,opt_iter=True)
    require(opts == q.QuasiNewtonOptions(), "Frozen optimizer policy differs")
    untouched_ridders = q.ridders_gradient
    ref_h = np.asarray(raw["hgfx"]["final_full"],np.float64).reshape(-1)
    ref_m = np.asarray(raw["matlab"]["final_full"],np.float64).reshape(-1)
    assert ref_h.shape == ref_m.shape == problem.initial_full.shape
    freeidx = np.asarray(problem.free_indices,np.int64)
    h = ref_h[freeidx]
    m = ref_m[freeidx]
    report = {
        "schema":"perf01d-exploratory-exact-anchor-gradient-interposition-v1",
        "status":"AUTHOR_SIDE_COUNTERFACTUAL_NOT_ORIGINAL_FROZEN_FIT",
        "protocol_committed_before_counterfactual_results":PROTOCOL_SHA,
        "exact_original_50_probe_run":SOURCE_50_RUN,
        "source_original_bfgs_run":"42187240378",
        "source_original_bfgs_raw_sha256":HASHES,
        "source_50_raw_sha256":SOURCE50_SHA256,
        "source_input_sha256":sha(root/"inputs"/"binary_128_s64.json"),
        "source_config_sha256":sha(root/"configs"/"hgf_binary_128.json"),
        "frozen_hgfx_sha":HGFX,
        "frozen_matlab_sha":REF,
        "original_64_public_fit_science":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_trajectory_mismatches":{"traj.mu":4,"traj.muhat":4},
        "original_reference_hgfx_free_endpoint":h.tolist(),
        "original_reference_matlab_free_endpoint":m.tolist(),
        "source_subject_index_zero_based":7,
        "source_trials":128,
        "arms_prespecified_in_order":list(ARMS),
        "host":host_provenance(),
        "no_performance_timing":True,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "arms":[],
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    for arm in ARMS:
        audit = {"name":arm,"interposition_is_not_original_hgfx":arm!="baseline_unmodified"}
        try:
            with interposition(q,untouched_ridders,arm,source_rows[:25],audit) as (hits,mapping):
                res=q.quasinewton_optim(problem.evaluate_free,problem.initial_free,opts)
            require(q.ridders_gradient is untouched_ridders, "Original source gradient not restored")
            end = np.asarray(res.arg_min, np.float64)
            require(end.shape == (3,) and np.isfinite(end).all()
                    and math.isfinite(float(res.val_min)), "Nonfinite diagnostic endpoint")
            audit.update({
                "execution_status":"COMPLETE",
                "intervention_status":("NOT_APPLICABLE_BASELINE" if not mapping
                                       else "EXACT_SOURCE_ANCHOR_TRIGGERED" if hits
                                       else "NOT_REACHED_EXACT_ANCHOR"),
                "intervention_sites_reached_count":len(hits),
                "intervention_calls_count":sum(int(z["intervened"]) for z in audit["calls"]),
                "original_101_iter_x":json_matrix(res.iter_x),
                "original_101_iter_val":json_matrix(res.iter_val),
                "original_inverse_hessian_final":json_matrix(res.inverse_hessian),
                "original_inverse_hessian_history": [json_matrix(t) for t in res.iter_inverse_hessians],
                "original_reset_indices_one_based":list(res.iter_resets),
                "reported_iterations":res.iterations,
                "reported_resets":res.resets,
                "reported_termination":res.termination,
                "counterfactual_final_free_parameters":end.tolist(),
                "counterfactual_final_objective":float(res.val_min),
                "max_abs_distance_to_original_hgfx_free_endpoint":float(np.max(np.abs(end-h))),
                "max_abs_distance_to_original_matlab_free_endpoint":float(np.max(np.abs(end-m))),
            })
            if arm=="baseline_unmodified":
                obs_x=np.asarray(raw["hgfx"]["iter_x"][:25],np.float64)
                ours=res.iter_x[:25]
                audit["baseline_original_25_history_matches_bitwise"]=bool(np.array_equal(ours,obs_x))
                audit["baseline_first_mismatch_slot_zero_based"] = next((
                    i for i in range(25) if not np.array_equal(ours[i],obs_x[i])
                ),None)
                audit["baseline_new_host_matches_original_hgfx_free_endpoint_binary64"]=bool(
                    np.array_equal(end,h))
                audit["baseline_new_host_max_abs_source_history_x_difference"]=float(
                    np.max(np.abs(ours-obs_x)))
        except Exception as exc:
            audit.update({
                "execution_status":"ERROR_RETAINED",
                "error_class":type(exc).__name__,
                "error":str(exc),
                "traceback":traceback.format_exc(),
            })
        require(q.ridders_gradient is untouched_ridders,
                "Post-run frozen source gradient function was not restored")
        report["arms"].append(audit)
        (output.parent/("arm-"+arm+".json")).write_text(json.dumps(audit,indent=2,sort_keys=True,allow_nan=False)+"\n")
        print(json.dumps({"arm":arm,"execution":audit["execution_status"],
                          "injection":audit.get("intervention_status"),
                          "n_calls":audit.get("intervention_calls_count"),
                          "to_matlab":audit.get("max_abs_distance_to_original_matlab_free_endpoint")},
                         sort_keys=True),flush=True)
    require(len(report["arms"])==len(ARMS)
            and [x["name"] for x in report["arms"]]==list(ARMS),
            "Original eight prespecified arms must all be retained")
    ok=all(x["execution_status"]=="COMPLETE" for x in report["arms"])
    if ok:
        base_end=np.asarray(report["arms"][0]["counterfactual_final_free_parameters"],float)
        for r in report["arms"]:
            new=np.asarray(r["counterfactual_final_free_parameters"],float)
            r["max_abs_distance_to_same_host_unmodified_baseline"]=float(np.max(np.abs(new-base_end)))
    report["status"]=("AUTHOR_SIDE_COUNTERFACTUAL_ALL_8_COMPLETED_NOT_SCIENTIFIC_PASS"
                       if ok else "AUTHOR_SIDE_COUNTERFACTUAL_INCOMPLETE_FAILURE_RETAINED")
    output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],
                      "baseline_original_history_exact":report["arms"][0].get("baseline_original_25_history_matches_bitwise"),
                      "scientific_original":"63/64 NONPASS",
                      "independent_review":"NOT_RECEIVED",
                      "perf01c":"NOT_FROZEN"},sort_keys=True),flush=True)
    require(ok,"One or more counterfactual arms failed; all outputs preserved")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-bfgs",required=True,type=Path)
    p.add_argument("--archive50",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    run(a.root,a.archive_bfgs,a.archive50,a.output)


if __name__=="__main__":
    main()
