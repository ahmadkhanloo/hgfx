"""Untimed native MATLAB BLAS identification: no scope/threshold changes."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks" / "runtime_v1"))
from test_perf01_cpu_host_attestation import paired  # noqa: E402
from compare_matlab_native_blas_untimed import compare, main  # noqa: E402


def example():
    h, m = paired()
    m["environment_thread_requests"]["MKL_NUM_THREADS"] = ""
    native = {
        "schema": "perf01c-matlab-native-blas-untimed-v1",
        "status": "READ_ONLY_NATIVE_LIBRARY_DIAGNOSTIC_NOT_BENCHMARK",
        "clock": "ABSENT",
        "performance": "NOT_MEASURED",
        "scientific_gate": "BLOCK_FREEZE_NOT_FROZEN",
        "github_run_id": m["github_run_id"],
        "github_sha": m["github_sha"],
        "boot_id": m["boot_id"],
        "matlab_release": "2026a",
        "process_pid": 4321,
        "max_num_comp_threads": 1,
        "requested_mkl_env_inside_matlab": "",
        "thread_count_before": 27,
        "thread_count_after_blas": 28,
        "thread_count_after_probe": 28,
        "native_mkl_api_compile_status": "COMPILED",
        "native_mkl_api_error_identifier": "",
        "native_mkl_api_error_message": "",
        "active_blas_worker_count_proven": False,
        "native": {
            "pid": 4321,
            "mapped_libraries": "/matlab/bin/glnxa64/libmkl_rt.so",
            "mapped_library_count": 1,
            "mkl_get_max_threads_available": True,
            "mkl_target_max_threads": 1,
            "mkl_symbol_source": "/matlab/bin/glnxa64/libmkl_rt.so",
            "query_kind": "TARGET_MAX_THREAD_CAP_NOT_OBSERVED_WORKER_COUNT",
            "omp_get_max_threads_available": True,
            "omp_target_max_threads": 1,
            "omp_symbol_source": "/matlab/sys/os/glnxa64/libiomp5.so",
        },
    }
    return h, m, native


class NativeMatlabBlasProvenance(unittest.TestCase):
    def test_mkl_one_target_not_active_worker_and_original_rule_still_blocked(self):
        h, m, n = example()
        r = compare(h, m, n)
        self.assertEqual(r["matlab_mkl_target_max_threads"], 1)
        self.assertTrue(r["matlab_mkl_target_one_observed"])
        self.assertFalse(r["matlab_actual_blas_worker_count_independently_verified"])
        self.assertEqual(r["original_environment_gate"], "BLOCKED_MATLAB_MKL_ENV")
        self.assertEqual(r["original_env_rule"], "FAIL")
        self.assertEqual(r["benchmark"], "NOT_RUN_NOT_AUTHORIZED")
        self.assertEqual(r["scientific_gate"], "BLOCK_FREEZE_NOT_FROZEN")

    def test_other_target_never_treated_as_single_thread(self):
        h, m, n = example()
        n["native"]["mkl_target_max_threads"] = 4
        r = compare(h, m, n)
        self.assertEqual(r["matlab_mkl_target_max_threads"], 4)
        self.assertFalse(r["matlab_mkl_target_one_observed"])
        self.assertEqual(r["original_environment_gate"], "BLOCKED_MATLAB_MKL_ENV")

    def test_openmp_target_is_separate_from_mkl_target_and_workers(self):
        h, m, n = example()
        n["native"]["omp_target_max_threads"] = 4
        r = compare(h, m, n)
        self.assertEqual(r["matlab_openmp_target_max_threads"], 4)
        self.assertFalse(r["matlab_openmp_target_one_observed"])
        self.assertEqual(r["matlab_mkl_target_max_threads"], 1)
        self.assertFalse(r["matlab_actual_blas_worker_count_independently_verified"])
        h, m, n = example()
        n["native"]["omp_get_max_threads_available"] = False
        n["native"]["omp_target_max_threads"] = -1
        r = compare(h, m, n)
        self.assertIsNone(r["matlab_openmp_target_max_threads"])
        h, m, n = example()
        n["native"]["omp_get_max_threads_available"] = False
        with self.assertRaisesRegex(ValueError, "must not infer"):
            compare(h, m, n)

    def test_unavailable_symbol_and_compiler_are_reported_not_faked(self):
        h, m, n = example()
        n["native"]["mkl_get_max_threads_available"] = False
        n["native"]["mkl_target_max_threads"] = -1
        r = compare(h, m, n)
        self.assertIsNone(r["matlab_mkl_target_max_threads"])
        self.assertFalse(r["matlab_mkl_target_one_observed"])
        h, m, n = example()
        n["native"] = {}
        n["native_mkl_api_compile_status"] = "UNAVAILABLE_OR_FAILED"
        n["native_mkl_api_error_message"] = "No supported C compiler"
        r = compare(h, m, n)
        self.assertFalse(r["matlab_native_mex_compiled"])
        self.assertIsNone(r["matlab_mkl_target_max_threads"])

    def test_fail_closed_wrong_process_source_host_and_clock(self):
        for field, value in (
            ("process_pid", 5), ("clock", "WALL_TIMER"),
            ("active_blas_worker_count_proven", True),
            ("github_run_id", "different"),
        ):
            h, m, n = example()
            if field == "process_pid":
                n["native"]["pid"] = 4321
            n[field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    compare(h, m, n)
        h, m, n = example()
        m["source_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Frozen"):
            compare(h, m, n)

    def test_wrong_mkl_symbol_semantics_rejected(self):
        h, m, n = example()
        n["native"]["query_kind"] = "ACTUAL_PARALLEL_WORKERS"
        with self.assertRaisesRegex(ValueError, "measurement type"):
            compare(h, m, n)
        h, m, n = example()
        n["native"]["mkl_get_max_threads_available"] = False
        n["native"]["mkl_target_max_threads"] = 1
        with self.assertRaisesRegex(ValueError, "must not imply"):
            compare(h, m, n)

    def test_native_and_base_matlab_environment_must_agree(self):
        h, m, n = example()
        n["requested_mkl_env_inside_matlab"] = "1"
        with self.assertRaisesRegex(ValueError, "snapshots disagree"):
            compare(h, m, n)

    def test_machine_readable_report_survives_unresolved_symbol(self):
        h, m, n = example()
        n["native"]["mkl_get_max_threads_available"] = False
        n["native"]["mkl_target_max_threads"] = -1
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            for name, payload in (("h.json", h), ("m.json", m), ("n.json", n)):
                (base / name).write_text(json.dumps(payload))
            with patch("sys.argv", [
                "compare_matlab_native_blas_untimed.py",
                "--hgfx", str(base / "h.json"),
                "--matlab", str(base / "m.json"),
                "--native", str(base / "n.json"),
                "--output", str(base / "out.json"),
            ]):
                main()
            report = json.loads((base / "out.json").read_text())
            self.assertEqual(report["original_env_rule"], "FAIL")
            self.assertIsNone(report["matlab_mkl_target_max_threads"])
            self.assertEqual(report["performance"] if "performance" in report else
                             report["benchmark"], "NOT_RUN_NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
