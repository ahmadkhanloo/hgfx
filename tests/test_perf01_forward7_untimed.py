"""Fail-closed tests for the untimed seven-forward original-case contract."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "runtime_v1"
sys.path.insert(0, str(DATA))
from compare_forward7_untimed import BAD, EXPECTED, GOOD, TRAJ, compare  # noqa: E402


def examples():
    registry = json.loads((DATA / "inputs_manifest.json").read_text())
    original = {v["id"]: v for v in registry["cases"]}
    base = {
        "status": "DIAGNOSTIC_ONLY_NOT_BENCHMARK_NOT_SCIENTIFIC_PASS",
        "original_case_denominator": 28,
        "forward_case_count": 7,
    }
    hgfx = dict(base, schema="perf01c-forward7-hgfx-untimed-v1",
                hgfx_sha="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27", cells=[])
    matlab = dict(base, schema="perf01c-forward7-matlab-untimed-v1",
                  matlab_sha="2437f4dc241541072722a2695ddeca7b44d83dd3", cells=[])
    for case_id, (model, n) in EXPECTED.items():
        path = DATA / "configs" / f"{model}_{n}.json"
        record = {
            "case_id": case_id, "model": model, "trials": n, "subject_index": 0,
            "source_sha256": original[case_id]["source_sha256"],
            "inf_states": [[[0.0] * 4 for _ in range(3)] for _ in range(n)],
            "traj": {f: [[0.0, 0.0] for _ in range(n)] for f in TRAJ},
        }
        hgfx["cells"].append(dict(record,
                                  config_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                  status="HGFX_UNTIMED_FORWARD_COMPLETED_MATLAB_UNVERIFIED"))
        matlab["cells"].append(dict(record,
                                   resolved_function_path=f"/frozen/{model}.m",
                                   status="MATLAB_UNTIMED_FORWARD_COMPLETED_HGFX_UNVERIFIED"))
    return hgfx, matlab


class Forward7UntimedContract(unittest.TestCase):
    def test_exact_full_unmodified_seven_diagnostic_rows(self):
        h, m = examples()
        r = compare(DATA, h, m)
        self.assertEqual(r["counts"], {GOOD: 7})
        self.assertEqual((r["old_denominator"], r["old_pending"], r["old_blocked"]),
                         (28, 16, 12))
        self.assertEqual(r["perf01c"], "BLOCK_FREEZE_NOT_FROZEN")
        self.assertEqual(r["performance"], "NOT_MEASURED")
        self.assertEqual(len(r["rows"][0]["fields"]), 12)

    def test_detect_full_output_float_mismatch_without_relaxing_threshold(self):
        h, m = examples()
        h["cells"][0]["traj"]["mu"][12][0] = 1e-5
        r = compare(DATA, h, m)
        self.assertEqual(r["counts"][BAD], 1)
        self.assertEqual(r["counts"][GOOD], 6)

    def test_reject_trial_axis_swapped_even_if_total_element_count_matches(self):
        h, m = examples()
        m["cells"][0]["traj"]["mu"] = [[0.0] * 128 for _ in range(2)]
        with self.assertRaisesRegex(ValueError, "Axes/shape"):
            compare(DATA, h, m)

    def test_reject_missing_or_duplicate_original_forward_case(self):
        h, m = examples()
        h["cells"][-1] = copy.deepcopy(h["cells"][0])
        with self.assertRaisesRegex(ValueError, "case denominator"):
            compare(DATA, h, m)

    def test_reject_source_digest_and_no_true_forward_call(self):
        h, m = examples()
        h["cells"][0]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Source/subject/model"):
            compare(DATA, h, m)
        h, m = examples()
        m["cells"][0]["status"] = "MATLAB_ERROR"
        with self.assertRaisesRegex(ValueError, "Missing genuine"):
            compare(DATA, h, m)

    def test_reject_unresolved_model_path_and_missing_trajectory(self):
        h, m = examples()
        m["cells"][0]["resolved_function_path"] = ""
        with self.assertRaisesRegex(ValueError, "active forward function"):
            compare(DATA, h, m)
        h, m = examples()
        del h["cells"][0]["traj"]["psi"]
        with self.assertRaisesRegex(ValueError, "trajectory field"):
            compare(DATA, h, m)


if __name__ == "__main__":
    unittest.main()
