"""Boundary-marker and fail-closed negative controls: no timing or MATLAB needed."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "runtime_v1"
sys.path.insert(0, str(DATA))

from compare_forward7_boundary_untimed import (  # noqa: E402
    AFTER, BEFORE, BOUNDARY, SCOPE, SOURCES, compare,
)
from forward7_boundary_hgfx_untimed import forward_only_call  # noqa: E402
from test_perf01_forward7_untimed import examples  # noqa: E402


def bound_examples():
    h, m = examples()
    for engine, payload in (("hgfx", h), ("matlab", m)):
        payload.update({
            "schema": SOURCES[engine],
            "candidate_boundary": BOUNDARY,
            "input_preparation": BEFORE,
            "output_shape_validation_and_serialization": AFTER,
            "clock": "ABSENT",
        })
        for row in payload["cells"]:
            row["boundary_id"] = BOUNDARY
            row["boundary_scope"] = SCOPE
            row["clock"] = "ABSENT"
    return h, m


class OriginalForwardCallBoundaryTests(unittest.TestCase):
    def test_exact_seven_full_outputs_not_performance_claim(self):
        h, m = bound_examples()
        report = compare(DATA, h, m)
        self.assertEqual(report["counts"], {"UNFROZEN_FORWARD_DIAGNOSTIC_CONCORDANCE": 7})
        self.assertEqual(report["perf01c"], "BLOCK_FREEZE_NOT_FROZEN")
        self.assertEqual(report["benchmark"], "NOT_RUN_NOT_AUTHORIZED")
        self.assertEqual(report["external_independent_approval"], "NOT_RECEIVED")
        self.assertEqual((report["old_denominator"], report["old_blocked"]), (28, 12))

    def test_reject_changed_boundary_and_clock_claim(self):
        for target, key, value in (
            ("hgfx", "clock", "PERF_COUNTER"),
            ("matlab", "candidate_boundary", "INCLUDE_IO"),
            ("matlab", "input_preparation", "INSIDE_CALL"),
            ("hgfx", "output_shape_validation_and_serialization", "INSIDE_CALL"),
        ):
            h, m = bound_examples()
            (h if target == "hgfx" else m)[key] = value
            with self.subTest(target=target, key=key):
                with self.assertRaisesRegex(ValueError, "boundary contract"):
                    compare(DATA, h, m)

    def test_reject_one_case_different_scope(self):
        h, m = bound_examples()
        m["cells"][6]["boundary_scope"] = "FORWARD_PLUS_LIKELIHOOD"
        with self.assertRaisesRegex(ValueError, "case boundary"):
            compare(DATA, h, m)

    def test_original_numerical_mismatch_still_fails(self):
        h, m = bound_examples()
        h["cells"][0]["traj"]["mu"][12][0] = 1e-4
        report = compare(DATA, h, m)
        self.assertEqual(report["counts"]["FORWARD_CONTRACT_OR_NUMERICAL_MISMATCH"], 1)

    def test_original_trial_axis_and_source_fail_closed(self):
        h, m = bound_examples()
        m["cells"][0]["traj"]["sa"] = [[0.0] * 128] * 2
        with self.assertRaisesRegex(ValueError, "Axes/shape"):
            compare(DATA, h, m)
        h, m = bound_examples()
        h["cells"][0]["source_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "Source/subject/model"):
            compare(DATA, h, m)

    def test_compute_wrapper_calls_unmodified_full_perceptual_source_only(self):
        calls = []

        def fake(inputs, p, **kwargs):
            calls.append((inputs.copy(), p.copy(), kwargs))
            return {"mu": np.zeros((len(inputs), 3))}, np.zeros((len(inputs), 3, 4))

        import forward7_boundary_hgfx_untimed as engine
        with patch.object(engine, "FORWARD", {"hgf_binary": fake}):
            traj, states = forward_only_call(
                "hgf_binary", np.array([0., 1.]), np.array([1., 2.])
            )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][2], {"transformed": True, "ignored_trials": ()})
        self.assertEqual(states.shape, (2, 3, 4))
        self.assertEqual(set(traj), {"mu"})


if __name__ == "__main__":
    unittest.main()
