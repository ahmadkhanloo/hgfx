"""Fail-closed synthetic controls for source-formula replay of Ridders raw calls.

These deliberately do not certify scientific fitting, gradients or timing.
"""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"
spec = importlib.util.spec_from_file_location(
    "replay_subject7_ridders_stencil_source_selection",
    BASE / "replay_subject7_ridders_stencil_source_selection.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def make_three_dim_trace():
    base = audit.TARGET[:]
    trace = [{"free_parameters": base[:], "objective": 50.0}]
    for j in range(3):
        h = 1.
        for i in range(11):
            if i: h /= 1.2
            for sign in (1., -1.):
                x = base[:]
                x[j] += sign * h
                trace.append({"free_parameters": x, "objective": 50.0 + x[j]})
    return trace


class RiddersOriginalTraceReplayTests(unittest.TestCase):
    def test_source_and_original_gate_anchored(self):
        self.assertEqual(audit.RUN, "42361286407")
        self.assertEqual(audit.PROTOCOL_SHA, "e1c3e2e83045896195701926a5f94fa361b0f091")
        self.assertEqual(audit.TARGET[0], -1.1621811570388512)

    def test_one_full_synthetic_trace_splits_without_loss(self):
        seq = make_three_dim_trace()
        a = audit.source_components(seq, audit.TARGET)
        self.assertEqual(len(a), 3)
        self.assertEqual([len(q) for q in a], [22,22,22])

    def test_first_original_f_x_must_be_exact(self):
        seq = make_three_dim_trace()
        seq[0]["free_parameters"][0] += 1e-2
        with self.assertRaises(ValueError):
            audit.source_components(seq, audit.TARGET)

    def test_source_pair_order_cannot_be_reversed(self):
        seq = make_three_dim_trace()
        seq[1],seq[2] = seq[2],seq[1]
        with self.assertRaises(ValueError):
            audit.source_components(seq,audit.TARGET)

    def test_source_axis_permutation_cannot_be_accepted(self):
        seq = make_three_dim_trace()
        seq[1]["free_parameters"] = seq[23]["free_parameters"][:]
        with self.assertRaises(ValueError):
            audit.source_components(seq,audit.TARGET)

    def test_source_missing_original_perturbation_cannot_be_accepted(self):
        seq = make_three_dim_trace()
        del seq[24]
        with self.assertRaises(ValueError):
            audit.source_components(seq,audit.TARGET)

    def test_source_nonfinite_objective_denied(self):
        seq = make_three_dim_trace()
        seq[25]["objective"] = math.inf
        with self.assertRaises(ValueError):
            audit.source_components(seq,audit.TARGET)

    def test_replay_source_minimum_steps_denied(self):
        seq = make_three_dim_trace()
        groups = audit.source_components(seq,audit.TARGET)
        with self.assertRaises(ValueError):
            audit.replay_group(groups[0][:-4], 0.0, 0.0)

    def test_replay_source_gradient_and_error_cannot_be_unverified(self):
        seq = make_three_dim_trace()
        groups = audit.source_components(seq,audit.TARGET)
        with self.assertRaises(ValueError):
            audit.replay_group(groups[0], 0.0, 0.0)

    def test_unavailable_archived_bytes_denied(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                audit.analyze_archive(Path(d))


if __name__ == "__main__":
    unittest.main()
