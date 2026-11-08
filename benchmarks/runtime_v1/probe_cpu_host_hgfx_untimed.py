#!/usr/bin/env python3
"""PERF-01C host/affinity/thread attestation for the frozen CPU Forward workload.

Untimed environment metadata ONLY. This is neither performance evidence nor
proof that MATLAB's active BLAS/OpenMP runtime matches Python's.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

EXPECTED_ENV = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "BLIS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
HGFX_SOURCE_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"


def file_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def cpuinfo_field(name: str) -> str:
    first = file_text("/proc/cpuinfo").split("\n\n", 1)[0]
    for line in first.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key.strip() == name:
                return value.strip()
    return ""


def allowed_list() -> str:
    for line in file_text("/proc/self/status").splitlines():
        if line.startswith("Cpus_allowed_list:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("Cpus_allowed_list not visible in /proc/self/status")


def command(args: list[str]) -> str:
    return subprocess.check_output(args, text=True, timeout=10).strip()


def produce() -> dict:
    if not sys.platform.startswith("linux"):
        raise RuntimeError("Host preflight requires the Linux same-runner workflow")
    if metadata.version("hgfx") != "1.0.0":
        raise RuntimeError("Must attest the installed frozen HGFX 1.0.0")
    # A trivial, untimed call loads NumPy's actual BLAS before inspecting
    # threadpoolctl. This is not a benchmark or a substitute for active MATLAB
    # MKL/BLAS runtime observation.
    np.dot(np.ones((2, 2), dtype=np.float64), np.ones((2, 2), dtype=np.float64))
    from threadpoolctl import threadpool_info

    threadpools = threadpool_info()
    return {
        "schema": "perf01c-cpu-host-untimed-python-v1",
        "status": "AUTHOR_SIDE_HOST_DIAGNOSTIC_ONLY_NO_TIMING",
        "engine": "hgfx",
        "source_sha": HGFX_SOURCE_SHA,
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_sha": os.environ.get("GITHUB_SHA", ""),
        "boot_id": file_text("/proc/sys/kernel/random/boot_id"),
        "kernel_release": platform.release(),
        "os_arch": command(["uname", "-m"]),
        "cpu_model": cpuinfo_field("model name"),
        "cpu_vendor": cpuinfo_field("vendor_id"),
        "cpu_microcode": cpuinfo_field("microcode"),
        "cpu_flags": cpuinfo_field("flags"),
        "online_logical_cpus": int(command(["nproc", "--all"])),
        "allowed_cpu_list": allowed_list(),
        "environment_thread_requests": {k: os.environ.get(k, "")
                                        for k in EXPECTED_ENV},
        "runtime_threadpools": [
            {
                "user_api": p.get("user_api", ""),
                "internal_api": p.get("internal_api", ""),
                "num_threads": p.get("num_threads"),
                "threading_layer": p.get("threading_layer", ""),
                "version": p.get("version", ""),
            } for p in threadpools
        ],
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "jax_version": metadata.version("jax"),
        "jaxlib_version": metadata.version("jaxlib"),
        "threadpoolctl_version": metadata.version("threadpoolctl"),
        "cpu_frequency_governor": (
            file_text("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
            if Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").is_file()
            else "NOT_VISIBLE"
        ),
        "timers": "ABSENT",
        "matlab_blas_runtime": "NOT_OBSERVED_IN_PYTHON",
        "scientific_gate": "BLOCK_FREEZE_NOT_FROZEN",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    result = produce()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print("Python frozen host/BLAS probe exported; no timing or CPU speed claim")


if __name__ == "__main__":
    main()
