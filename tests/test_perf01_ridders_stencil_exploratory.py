"""Focused positive/negative engineering controls for post-result Ridders stencil trace.

These do not establish HGFX scientific parity, timing or any frozen gate.
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"
spec = importlib.util.spec_from_file_location(
    "subject7_ridders_stencil_exploratory", BASE / "subject7_ridders_stencil_exploratory.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def sample_stream(target=None, value_offset=0):
    t = list(target or audit.TARGET)
    cases = [{"free_parameters": t[:], "objective": 100.0}]
    for i, side in ((0, 0.2), (0, -0.2), (1, 0.1), (1, -0.1),
                    (2, 0.3), (2, -0.3)):
        x = t[:]
        x[i] += side
        cases.append({"free_parameters": x, "objective": 100.0 + side + value_offset})
    return cases


class RiddersStencilExploratoryTests(unittest.TestCase):
    def test_target_is_explicit_post_result_not_new_gate(self):
        self.assertEqual(audit.SOURCE_RUN, "42305573614")
        self.assertEqual(audit.TARGET, [-1.1621811570388512,
                                        -6.37816839506084,
                                        -0.23738383160834042])
        self.assertNotEqual(audit.PRESPEC_SHA, audit.SOURCE_SHA)

    def test_ulp_exact_and_single_increment(self):
        import math
        self.assertEqual(audit.ulp(100.0, 100.0), 0)
        self.assertEqual(audit.ulp(100.0, math.nextafter(100.0, math.inf)), 1)

    def test_stream_validates_all_three_coordinate_perturbations(self):
        audit.validate_stream(sample_stream(), audit.TARGET, "synthetic")

    def test_missing_initial_function_evaluation_denied(self):
        s = sample_stream()
        s[0]["free_parameters"][0] += 0.1
        with self.assertRaises(ValueError):
            audit.validate_stream(s, audit.TARGET, "synthetic")

    def test_simultaneous_coordinate_tamper_denied(self):
        s = sample_stream()
        s[3]["free_parameters"][0] += 0.1
        with self.assertRaises(ValueError):
            audit.validate_stream(s, audit.TARGET, "synthetic")

    def test_nonfinite_objective_denied(self):
        s = sample_stream()
        s[3]["objective"] = float("nan")
        with self.assertRaises(ValueError):
            audit.validate_stream(s, audit.TARGET, "synthetic")

    def test_nonfinite_coordinate_denied(self):
        s = sample_stream()
        s[3]["free_parameters"][0] = float("inf")
        with self.assertRaises(ValueError):
            audit.validate_stream(s, audit.TARGET, "synthetic")

    def test_complete_synthetic_paired_replay(self):
        s = sample_stream()
        result = audit.pair_streams(s, s)
        self.assertEqual(result["hgfx_call_count"], 7)
        self.assertEqual(result["matlab_call_count"], 7)
        self.assertEqual(result["index_aligned_exact_coordinate_pairs"], 7)
        self.assertEqual(result["index_aligned_exact_coordinate_objective_differences"], 0)
        self.assertIsNone(result["first_coord_mismatch_index"])

    def test_ulp_difference_only_when_identical_coordinates(self):
        import math
        s = sample_stream()
        t = sample_stream()
        t[2]["objective"] = math.nextafter(t[2]["objective"], math.inf)
        res = audit.pair_streams(s, t)
        self.assertEqual(res["first_objective_mismatch_index"], 2)
        self.assertEqual(res["max_matched_objective_ulp"], 1)

    def test_misaligned_stencil_not_silently_paired(self):
        s = sample_stream()
        t = sample_stream()
        t[2]["free_parameters"][0] += 0.00001
        res = audit.pair_streams(s, t)
        self.assertEqual(res["index_aligned_exact_coordinate_pairs"], 6)
        self.assertEqual(res["first_coord_mismatch_index"], 2)
        self.assertFalse(res["all_calls_by_original_index_with_unpaired_coordinates_explicit"][2]["same_binary64_coordinates"])

    def test_shorter_trace_preserves_unpaired_tail(self):
        s = sample_stream()
        s.append(dict(s[-1]))  # 8 synthetic calls, but both streams still meet minimum inventory.
        t = sample_stream()      # 7 synthetic calls; only final eighth call is absent.
        res = audit.pair_streams(s, t)
        self.assertEqual(res["hgfx_call_count"], 8)
        self.assertEqual(res["matlab_call_count"], 7)
        self.assertEqual(res["first_coord_mismatch_index"], 7)
        self.assertFalse(res["all_calls_by_original_index_with_unpaired_coordinates_explicit"][-1]["both_present"])

    def test_missing_source_artifact_denied(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                audit.source_check(Path(d), Path(d))

    def test_bitwise_coordinate_comparison(self):
        import math
        t = audit.TARGET[:]
        u = t[:]
        self.assertTrue(audit.same_coord(t, u))
        u[0] = math.nextafter(u[0], math.inf)
        self.assertFalse(audit.same_coord(t, u))


if __name__ == "__main__":
    unittest.main()
