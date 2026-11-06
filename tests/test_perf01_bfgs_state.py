"""PERF-01D BFGS trace: no metadata, slot, or evidence can disappear."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_subject7_bfgs_state import compare


def fixture(engine: str):
    start=[-3.0,-6.0,3.871201010907891]
    x=[[start[0]+i,start[1],start[2]] for i in range(24)]
    x.append(list(x[-1]))
    val=[float(100-i) for i in range(24)]
    val.append(val[-1])
    filled=[{"record_index_zero_based":i,"free_parameters":list(row),
             "objective_recomputed":v,"grad":[-1.,0.,0.],
             "ridders_error":[0.,0.,0.]}
            for i,(row,v) in enumerate(zip(x,val))]
    inv=[np.eye(3).tolist() for _ in range(24)]
    return {
        "schema":f"perf01-subject7-bfgs-state-{engine}-v1",
        "status":"UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED",
        "model":"hgf_binary","trials":128,
        "subject_index_zero_based":7,
        "source_run_id":"41863441006",
        "frozen_hgfx_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "frozen_matlab_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "source_input_sha256":"unaltered-source-input",
        "source_config_sha256":"unaltered-source-config",
        "original_raw_fits_verified":True,"frozen_start_matches":True,
        "n_rand_init":0,
        "ridders_min_steps":10,
        "finite_slots":25,
        "iter_x":x+[[None]*3 for _ in range(76)],
        "iter_val":val+[None]*76,
        "iter_inverse_hessian":inv,
        "iter_resets_one_based":[],
        "ridders_recomputed_history":filled,
    }


class TestBFGSStates(unittest.TestCase):
    def test_complete_public_history_and_24_matrices(self):
        o=compare(fixture("hgfx"),fixture("matlab"))
        self.assertEqual(o["filled_history_slots"],25)
        self.assertEqual(o["preallocated_history_slots"],101)
        self.assertEqual(o["matrix_shared_slot_count"],24)
        self.assertEqual(len(o["line_search_candidates"]),24)
        self.assertEqual(o["line_search_candidates"][0]["hgfx"]["best_half_step_exponent"],0)
        self.assertEqual(o["line_search_candidates"][0]["hgfx"]["candidate_reconstruction_max_abs_residual"],0)
        self.assertTrue(o["both_terminal_history_duplicate"])
        self.assertIn("NOT_SCIENTIFIC_PASS",o["status"])

    def test_frozen_bfgs_inverse_matrix_difference_retained(self):
        h,m=fixture("hgfx"),fixture("matlab")
        h["iter_inverse_hessian"][4][0][0]=1.25
        r=compare(h,m)
        self.assertEqual(r["first_nonzero_matrix_difference"]["record_index_zero_based"],4)
        self.assertAlmostEqual(r["maximum_matrix_component_difference"],0.25)

    def test_modified_reference_release_rejected(self):
        h,m=fixture("hgfx"),fixture("matlab")
        m["frozen_matlab_sha"]="different"
        with self.assertRaisesRegex(ValueError,"unverified"):
            compare(h,m)

    def test_omitted_hessian_cannot_silently_pass(self):
        h,m=fixture("hgfx"),fixture("matlab")
        h["iter_inverse_hessian"]=h["iter_inverse_hessian"][:22]
        with self.assertRaisesRegex(ValueError,"inverse-Hessian"):
            compare(h,m)

    def test_missing_gradient_slot_rejected(self):
        h,m=fixture("hgfx"),fixture("matlab")
        h["ridders_recomputed_history"].pop()
        with self.assertRaisesRegex(ValueError,"all 25"):
            compare(h,m)

    def test_wrong_parameter_point_rejected(self):
        h,m=fixture("hgfx"),fixture("matlab")
        m["ridders_recomputed_history"][2]["free_parameters"][0]+=1
        with self.assertRaisesRegex(ValueError,"not evaluated at saved"):
            compare(h,m)

    def test_reset_trace_duplicates_rejected(self):
        h,m=fixture("hgfx"),fixture("matlab")
        m["iter_resets_one_based"]=[7,7]
        with self.assertRaisesRegex(ValueError,"reset"):
            compare(h,m)

    def test_invalid_gradient_cannot_justify_optimizer_pass(self):
        h,m=fixture("hgfx"),fixture("matlab")
        h["ridders_recomputed_history"][1]["grad"][1]=None
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            compare(h,m)

    def test_different_original_input_rejected(self):
        h,m=fixture("hgfx"),fixture("matlab")
        h["source_input_sha256"]="different"
        with self.assertRaisesRegex(ValueError,"SHA256"):
            compare(h,m)

    def test_no_line_search_approval_on_reconstruction(self):
        h,m=fixture("hgfx"),fixture("matlab")
        h["iter_x"][2][0]+=0.33
        h["ridders_recomputed_history"][2]["free_parameters"][0]+=0.33
        r=compare(h,m)
        row=r["line_search_candidates"][1]["hgfx"]
        self.assertGreater(row["candidate_reconstruction_max_abs_residual"],0)
        self.assertIn("CANDIDATE_ONLY",row["status"])
        self.assertIn("not an instrumented",r["important_limitations"][1])


if __name__=="__main__":
    unittest.main()
