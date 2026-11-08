"""PERF-01C same-runner CPU metadata: immutable/untimed fail-closed tests."""
from __future__ import annotations

import copy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"
sys.path.insert(0, str(ROOT))

from compare_cpu_host_attestation import compare  # noqa: E402
from probe_cpu_host_hgfx_untimed import EXPECTED_ENV  # noqa: E402


def paired() -> tuple[dict, dict]:
    common = {
        "status": "AUTHOR_SIDE_HOST_DIAGNOSTIC_ONLY_NO_TIMING",
        "github_run_id": "123456789",
        "github_sha": "f" * 40,
        "boot_id": "example-boot-id-not-a-real-host",
        "kernel_release": "linux-test-kernel",
        "os_arch": "x86_64",
        "cpu_model": "example",
        "cpu_vendor": "GenuineIntel",
        "cpu_microcode": "0xfa",
        "cpu_flags": "sse2 avx2",
        "online_logical_cpus": 4,
        "allowed_cpu_list": "0-3",
        "cpu_frequency_governor": "NOT_VISIBLE",
        "environment_thread_requests": {k: "1" for k in EXPECTED_ENV},
        "timers": "ABSENT",
        "scientific_gate": "BLOCK_FREEZE_NOT_FROZEN",
    }
    hgfx = {
        **copy.deepcopy(common),
        "schema": "perf01c-cpu-host-untimed-python-v1",
        "engine": "hgfx",
        "source_sha": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "runtime_threadpools": [
            {"user_api": "blas", "num_threads": 1,
             "internal_api": "openblas", "version": "example"}
        ],
    }
    matlab = {
        **copy.deepcopy(common),
        "schema": "perf01c-cpu-host-untimed-matlab-v1",
        "engine": "matlab",
        "source_sha": "2437f4dc241541072722a2695ddeca7b44d83dd3",
        "matlab_release": "2026a",
        "matlab_max_num_comp_threads": 1,
        "matlab_blas_runtime": "NOT_INDEPENDENTLY_OBSERVED",
    }
    return hgfx, matlab


class HostAttestationContractTests(unittest.TestCase):
    def test_same_host_does_not_claim_matlab_blas_or_speedup(self):
        h, m = paired()
        r = compare(h, m)
        self.assertEqual(
            r["status"],
            "HOST_AFFINITY_AND_REQUESTED_THREADS_MATCH_MATLAB_BLAS_RUNTIME_UNVERIFIED",
        )
        self.assertFalse(r["matlab_blas_active_threads_observed"])
        self.assertFalse(r["energy_or_thermal_control_proved"])
        self.assertEqual(r["performance"], "NOT_MEASURED")
        self.assertEqual(r["scientific_gate"], "BLOCK_FREEZE_NOT_FROZEN")

    def test_reject_different_host_affinity_cpu_model_microcode(self):
        for field, changed in (
            ("boot_id", "different"), ("allowed_cpu_list", "1-2"),
            ("cpu_model", "different"), ("cpu_microcode", "different"),
            ("cpu_flags", "different"), ("github_sha", "0" * 40),
        ):
            h, m = paired()
            m[field] = changed
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    compare(h, m)

    def test_reject_uncontrolled_requested_threads_and_python_blas(self):
        h, m = paired()
        h["environment_thread_requests"]["OPENBLAS_NUM_THREADS"] = "4"
        with self.assertRaisesRegex(ValueError, "thread env"):
            compare(h, m)
        h, m = paired()
        h["runtime_threadpools"][0]["num_threads"] = 4
        with self.assertRaisesRegex(ValueError, "not single-threaded"):
            compare(h, m)
        h, m = paired()
        h["runtime_threadpools"] = []
        with self.assertRaisesRegex(ValueError, "unavailable"):
            compare(h, m)

    def test_reject_matlab_thread_claim_and_frozen_identity(self):
        h, m = paired()
        m["matlab_max_num_comp_threads"] = 4
        with self.assertRaisesRegex(ValueError, "compute-thread"):
            compare(h, m)
        h, m = paired()
        m["source_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source identity"):
            compare(h, m)
        h, m = paired()
        m["matlab_blas_runtime"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "Do not claim"):
            compare(h, m)

    def test_no_timing_or_freeze_spoofing(self):
        h, m = paired()
        h["timers"] = "PERF_COUNTER"
        with self.assertRaisesRegex(ValueError, "benchmark/freezing"):
            compare(h, m)
        h, m = paired()
        m["scientific_gate"] = "PASS"
        with self.assertRaisesRegex(ValueError, "benchmark/freezing"):
            compare(h, m)


if __name__ == "__main__":
    unittest.main()
