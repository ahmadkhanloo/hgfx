"""Fail-closed synthetic controls for exact frozen Ridders source-formula replay."""
from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import replay_initial_ridders_richardson_table as source
from replay_initial_ridders_stencil_archive import scientific_original


def synthetic_pairs(base=1.,steps=11,div=1.2,distort_final=False):
    h=1.
    out=[]
    for i in range(steps):
        slope=1000. if distort_final and i==steps-1 else base
        out.append({
            "coord_zero_based":0,
            "step_one_based":i+1,
            "positive":{"value":float(slope*h)},
            "negative":{"value":float(-slope*h)},
        })
        h/=div
    return out


class FrozenSourceFormulaTests(unittest.TestCase):
    def test_uniform_gradient_strict_ties_do_not_replace_best(self):
        a=source.reconstruct_axis(synthetic_pairs(),0)
        self.assertEqual(a["reconstructed_best_cell_zero_based"],[1,1])
        self.assertEqual(a["reconstructed_best_derivative"],1.)
        self.assertEqual(a["reconstructed_best_error"],0.)
        self.assertEqual(a["number_strict_best_updates"],1)
        self.assertIsNone(a["reconstructed_first_source_stop_step"])

    def test_actual_min_steps_rule_11th_pair_may_stop(self):
        a=source.reconstruct_axis(synthetic_pairs(distort_final=True),0)
        self.assertEqual(a["reconstructed_first_source_stop_step"],11)
        self.assertTrue(a["reconstructed_stopping_matches_observed_source_pair_count"])
        self.assertFalse(a["full_triangular_row_source_reconstruction"][9]["source_stop_eligible"])
        self.assertTrue(a["full_triangular_row_source_reconstruction"][10]["source_stop_eligible"])

    def test_no_early_stop_eligibility_before_11(self):
        a=source.reconstruct_axis(synthetic_pairs(),0)
        self.assertFalse(any(t["source_stop_eligible"] for t in
                             a["full_triangular_row_source_reconstruction"][:10]))

    def test_full_triangular_matrix_cell_count(self):
        a=source.reconstruct_axis(synthetic_pairs(),0)
        self.assertEqual(sum(len(z["p_cells"]) for z in a["full_triangular_row_source_reconstruction"]),
                         11*12//2)

    def test_wrong_min_steps_rejected(self):
        with self.assertRaisesRegex(ValueError,"options/steps"):
            source.reconstruct_axis(synthetic_pairs(),0,min_steps=9)

    def test_wrong_div_rejected(self):
        with self.assertRaisesRegex(ValueError,"options/steps"):
            source.reconstruct_axis(synthetic_pairs(),0,div=1.1)

    def test_wrong_tf_rejected(self):
        with self.assertRaisesRegex(ValueError,"options/steps"):
            source.reconstruct_axis(synthetic_pairs(),0,tf=3.0)

    def test_dropped_source_pair_rejected(self):
        with self.assertRaisesRegex(ValueError,"inventory"):
            source.reconstruct_axis(synthetic_pairs(steps=10),0)

    def test_wrong_source_axis_rejected(self):
        rows=synthetic_pairs()
        rows[2]["coord_zero_based"]=1
        with self.assertRaisesRegex(ValueError,"axis"):
            source.reconstruct_axis(rows,0)

    def test_nan_original_objective_rejected(self):
        rows=synthetic_pairs()
        rows[1]["positive"]["value"]=float("nan")
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            source.reconstruct_axis(rows,0)

    def test_exact_observed_float_comparison_flags_one_ulp(self):
        b=math.nextafter(1.,2.)
        v=source.compare_scalar(1.,b)
        self.assertFalse(v["exact_equal_binary64"])
        self.assertEqual(v["ulp_distance"],1)
        self.assertGreater(v["absolute_difference"],0.)

    def test_literal_source_pins_not_any_original_fitting_science(self):
        self.assertEqual(source.MIN_STEPS,10)
        self.assertEqual(source.MAX_STEPS,100)
        self.assertEqual(source.DIV,1.2)
        self.assertEqual(source.RUN,"42389292284")
        self.assertNotEqual(source.SOURCE["hgfx-first-ridders.json"],
                            source.SOURCE["matlab-first-private-ridders.json"])

    def test_forged_original_full_science_rejected(self):
        v={"hgfx_sha":source.HGFX,"matlab_sha":source.MATLAB,
           "subject_count":64,
           "classification_counts":{
              "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":64,
              "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":0},
           "cases":[{}]*8}
        with self.assertRaisesRegex(ValueError,"63/64"):
            scientific_original(v)

    def test_float_bitwise_separates_signed_zero(self):
        self.assertFalse(source.binary_equal(+0.0,-0.0))

    def test_overlong_source_ridders_grid_rejected(self):
        with self.assertRaisesRegex(ValueError,"inventory"):
            source.reconstruct_axis(synthetic_pairs(steps=101),0)


if __name__=="__main__":
    unittest.main()
