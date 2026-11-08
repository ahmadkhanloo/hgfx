#!/usr/bin/env python3
"""PERF-01C native MATLAB BLAS target-cap evidence: untimed / not a freeze.

An MKL_Get_Max_Threads observation is a *target*, not observed parallel
workers; original strict MATLAB MKL_NUM_THREADS=1 environment requirement
remains failed whenever MATLAB reports an empty value.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_cpu_host_attestation import (
    COMMON_IDENTITY, HGFX_SOURCE_SHA, MATLAB_SOURCE_SHA, require,
)

NEUTRAL_STATUS = "READ_ONLY_NATIVE_LIBRARY_DIAGNOSTIC_NOT_BENCHMARK"
SCHEMA = "perf01c-matlab-native-blas-untimed-v1"


def compare(hgfx: dict, matlab: dict, native: dict) -> dict:
    require(hgfx.get("schema") == "perf01c-cpu-host-untimed-python-v1"
            and matlab.get("schema") == "perf01c-cpu-host-untimed-matlab-v1"
            and native.get("schema") == SCHEMA,
            "Unrecognized evidence schema")
    require(hgfx.get("source_sha") == HGFX_SOURCE_SHA
            and matlab.get("source_sha") == MATLAB_SOURCE_SHA,
            "Frozen code source not pinned")
    for key in COMMON_IDENTITY:
        require(hgfx.get(key) and hgfx[key] == matlab.get(key),
                "Same CPU host identity missing or mismatched: " + key)
    require(native.get("github_run_id") == matlab["github_run_id"]
            and native.get("github_sha") == matlab["github_sha"]
            and native.get("boot_id") == matlab["boot_id"],
            "Native MATLAB observation from different Actions execution/host")
    require(native.get("matlab_release") == "2026a"
            and matlab.get("matlab_release") == "2026a"
            and matlab.get("matlab_max_num_comp_threads") == 1
            and native.get("max_num_comp_threads") == 1,
            "Unverified MATLAB R2026a compute-thread request")
    require(native.get("status") == NEUTRAL_STATUS
            and native.get("clock") == "ABSENT"
            and native.get("performance") == "NOT_MEASURED"
            and native.get("scientific_gate") == "BLOCK_FREEZE_NOT_FROZEN"
            and native.get("active_blas_worker_count_proven") is False,
            "Attempt to claim timers, performance or measured BLAS workers")
    require(isinstance(native.get("process_pid"), int)
            and native["process_pid"] > 0,
            "Invalid native process identity")
    for name in ("thread_count_before", "thread_count_after_blas",
                 "thread_count_after_probe"):
        require(isinstance(native.get(name), int) and native[name] > 0,
                "Missing process-wide thread diagnostic: " + name)
    observed_env = matlab.get("environment_thread_requests", {}).get("MKL_NUM_THREADS")
    require(native.get("requested_mkl_env_inside_matlab") == observed_env,
            "MATLAB native and baseline MKL environment snapshots disagree")

    compiled = native.get("native_mkl_api_compile_status") == "COMPILED"
    mex = native.get("native") or {}
    if compiled:
        require(mex.get("query_kind") ==
                "TARGET_MAX_THREAD_CAP_NOT_OBSERVED_WORKER_COUNT",
                "Ambiguous native MKL API measurement type")
        require(mex.get("pid") == native["process_pid"],
                "Native MEX inspected wrong PID")
        require(isinstance(mex.get("mapped_library_count"), int)
                and mex["mapped_library_count"] >= 0,
                "Native loaded-library count missing")
        require(isinstance(mex.get("mapped_libraries"), str)
                and isinstance(mex.get("mkl_symbol_source"), str),
                "Native loaded-library evidence incomplete")
        require(isinstance(mex.get("mkl_get_max_threads_available"), bool),
                "Native MKL API availability not boolean")
        require(isinstance(mex.get("mkl_target_max_threads"), int),
                "Native MKL target thread cap not numeric integer")
        require(isinstance(mex.get("omp_get_max_threads_available"), bool),
                "OpenMP API availability not boolean")
        require(isinstance(mex.get("omp_target_max_threads"), int)
                and isinstance(mex.get("omp_symbol_source"), str),
                "OpenMP target evidence incomplete")
        if mex["omp_get_max_threads_available"]:
            require(mex["omp_target_max_threads"] > 0,
                    "OpenMP API returned nonpositive target threads")
            require(bool(mex["omp_symbol_source"]),
                    "OpenMP symbol resolved without a source")
        else:
            require(mex["omp_target_max_threads"] == -1,
                    "Missing OpenMP symbol must not infer target workers")
        if mex["mkl_get_max_threads_available"]:
            require(mex["mkl_target_max_threads"] > 0,
                    "Native MKL API returned nonpositive thread cap")
        else:
            require(mex["mkl_target_max_threads"] == -1,
                    "Missing MKL symbol must not imply observed target")
    else:
        require(native.get("native_mkl_api_compile_status") == "UNAVAILABLE_OR_FAILED",
                "Native MEX compilation state unknown")
        require(bool(native.get("native_mkl_api_error_message")),
                "MEX instrumentation failure not preserved")

    old_env_blocked = observed_env != "1"
    omp_target = (mex.get("omp_target_max_threads")
                  if compiled and mex.get("omp_get_max_threads_available") else None)
    target = (mex.get("mkl_target_max_threads")
              if compiled and mex.get("mkl_get_max_threads_available") else None)
    policy = "BLOCKED_MATLAB_MKL_ENV" if old_env_blocked else "STILL_NOT_FROZEN"
    return {
        "schema": "perf01c-matlab-native-blas-comparison-v1",
        "status": "NATIVE_READ_ONLY_DIAGNOSTIC_RECORDED",
        "same_host": True,
        "original_env_rule": "FAIL" if old_env_blocked else "REQUESTED_VALUE_SEEN",
        "original_environment_gate": policy,
        "matlab_mkl_env": observed_env,
        "hgfx_mkl_env": hgfx.get("environment_thread_requests", {}).get(
            "MKL_NUM_THREADS"),
        "matlab_native_mex_compiled": compiled,
        "matlab_blas_mapped_libraries": mex.get("mapped_libraries", "") if compiled else "",
        "matlab_mkl_native_symbol_available": (
            mex.get("mkl_get_max_threads_available", False) if compiled else False
        ),
        "matlab_mkl_target_max_threads": target,
        "matlab_mkl_target_one_observed": target == 1,
        "matlab_openmp_target_max_threads": omp_target,
        "matlab_openmp_target_one_observed": omp_target == 1,
        "openmp_target_is_not_mkl_or_active_worker_count": True,
        "matlab_actual_blas_worker_count_independently_verified": False,
        "matlab_process_threads_before": native["thread_count_before"],
        "matlab_process_threads_after_blas": native["thread_count_after_blas"],
        "matlab_process_threads_after_probe": native["thread_count_after_probe"],
        "process_threads_are_not_blas_worker_count": True,
        "affinity_pinning_proved": False,
        "thermal_power_or_contended_runner_proved": False,
        "benchmark": "NOT_RUN_NOT_AUTHORIZED",
        "clock": "ABSENT",
        "scientific_gate": "BLOCK_FREEZE_NOT_FROZEN",
        "independent_reviewer_signoff": "NOT_RECEIVED",
        "run_id": native["github_run_id"],
        "executed_git_sha": native["github_sha"],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hgfx", required=True, type=Path)
    p.add_argument("--matlab", required=True, type=Path)
    p.add_argument("--native", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    report = compare(json.loads(a.hgfx.read_bytes()),
                     json.loads(a.matlab.read_bytes()),
                     json.loads(a.native.read_bytes()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(report["status"], "/",
          report["original_environment_gate"],
          "/ NO TIMER / NO SCIENTIFIC OR PERFORMANCE PASS")


if __name__ == "__main__":
    main()
