#!/usr/bin/env python3
"""Fail-closed same-runner CPU-host metadata audit for PERF-01C; no timings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from probe_cpu_host_hgfx_untimed import EXPECTED_ENV

COMMON_IDENTITY = (
    "github_run_id", "github_sha", "boot_id", "kernel_release",
    "os_arch", "cpu_model", "cpu_vendor", "cpu_microcode", "cpu_flags",
    "online_logical_cpus", "allowed_cpu_list",
)
HGFX_SOURCE_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SOURCE_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def compare(hgfx: dict, matlab: dict) -> dict:
    require(hgfx.get("schema") == "perf01c-cpu-host-untimed-python-v1"
            and matlab.get("schema") == "perf01c-cpu-host-untimed-matlab-v1",
            "Wrong paired host probe schema")
    require(hgfx.get("engine") == "hgfx" and matlab.get("engine") == "matlab"
            and hgfx.get("source_sha") == HGFX_SOURCE_SHA
            and matlab.get("source_sha") == MATLAB_SOURCE_SHA,
            "Wrong frozen CPU engine/source identity")
    for obj in (hgfx, matlab):
        require(obj.get("timers") == "ABSENT"
                and obj.get("scientific_gate") == "BLOCK_FREEZE_NOT_FROZEN"
                and obj.get("status") == "AUTHOR_SIDE_HOST_DIAGNOSTIC_ONLY_NO_TIMING",
                "Unexpected benchmark/freezing claim in CPU probe")
    for key in COMMON_IDENTITY:
        require(hgfx.get(key) and matlab.get(key)
                and hgfx[key] == matlab[key],
                "Same-host/affinity evidence missing or differs: " + key)
    require(hgfx["online_logical_cpus"] >= 1,
            "Invalid host logical CPU count")
    require(matlab.get("matlab_release") == "2026a"
            and matlab.get("matlab_max_num_comp_threads") == 1,
            "MATLAB version or compute-thread request not established")
    for engine, obj in (("HGFX", hgfx), ("MATLAB", matlab)):
        env = obj.get("environment_thread_requests", {})
        require(set(env) == set(EXPECTED_ENV)
                and all(env[k] == "1" for k in EXPECTED_ENV),
                engine + " thread env request missing or unequal to 1")
    require(hgfx["environment_thread_requests"] ==
            matlab["environment_thread_requests"],
            "Cross-engine environment thread requests differ")
    python_pools = hgfx.get("runtime_threadpools")
    require(isinstance(python_pools, list) and python_pools,
            "Python active threadpool metadata unavailable")
    for pool in python_pools:
        require(isinstance(pool.get("num_threads"), int)
                and pool["num_threads"] == 1,
                "Active Python numerical threadpool is not single-threaded")
    require(any(p.get("user_api") == "blas" for p in python_pools),
            "No observed Python BLAS runtime/threadpool")
    require(matlab.get("matlab_blas_runtime") == "NOT_INDEPENDENTLY_OBSERVED",
            "Do not claim MATLAB BLAS runtime without independent evidence")

    return {
        "schema": "perf01c-cpu-host-attestation-untimed-comparison-v1",
        "status": "HOST_AFFINITY_AND_REQUESTED_THREADS_MATCH_MATLAB_BLAS_RUNTIME_UNVERIFIED",
        "same_boot_id": True,
        "same_kernel_cpu_microcode_flags_affinity": True,
        "same_requested_env_thread_limits": True,
        "matlab_max_num_comp_threads": 1,
        "python_active_threadpool_count": len(python_pools),
        "python_active_threadpools_single_threaded": True,
        "python_blas_active_threads_observed": True,
        "matlab_blas_active_threads_observed": False,
        "identical_core_isolation_or_background_contention_proved": False,
        "energy_or_thermal_control_proved": False,
        "source_sha": hgfx["github_sha"],
        "run_id": hgfx["github_run_id"],
        "clock": "ABSENT",
        "performance": "NOT_MEASURED",
        "scientific_gate": "BLOCK_FREEZE_NOT_FROZEN",
        "independent_reviewer_signoff": "NOT_RECEIVED",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hgfx", type=Path, required=True)
    p.add_argument("--matlab", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = compare(json.loads(a.hgfx.read_bytes()), json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(report["status"], "untimed; not a benchmark and not a freeze")


if __name__ == "__main__":
    main()
