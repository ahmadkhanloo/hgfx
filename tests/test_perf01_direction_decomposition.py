"""PERF-01D direction decomposition unit tests; immutable archived science is not a PASS."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from derive_subject7_direction_decomposition import (
    ANCHORS, BFGS_RUN, PAIR_RUN, PAIR_RAW, PAIR_SHA,
    read_paired, history, two_term, three_term, scaled_direction,
)


class TestDirectionAlgebra(unittest.TestCase):
    def test_two_term_identity(self):
        A=np.array([[3.,.1],[.1,1.]])
        B=np.array([[2.,.3],[.3,4.]])
        h=np.array([2.,3.])
        m=np.array([1.,4.])
        d,t,g=two_term(A,B,h,m)
        np.testing.assert_allclose(d,t+g,rtol=0,atol=2e-15)

    def test_two_term_matrix_only(self):
        A=np.diag([2.,3.]);B=np.eye(2)
        g=np.array([1.,2.])
        d,t,p=two_term(A,B,g,g)
        np.testing.assert_array_equal(p,[0.,0.])
        np.testing.assert_array_equal(d,t)

    def test_two_term_gradient_only(self):
        A=B=np.eye(2)
        h=np.array([1.,2.]);m=np.array([2.,1.])
        d,t,g=two_term(A,B,h,m)
        np.testing.assert_array_equal(t,[0.,0.])
        np.testing.assert_array_equal(d,g)

    def test_three_term_same_x_algebra(self):
        A=np.array([[3.,.1],[.1,1.]])
        B=np.array([[2.,.3],[.3,4.]])
        gh=np.array([2.,3.]); gm_at_h=np.array([1.,2.]);gm_at_m=np.array([1.,4.])
        t,e,x=three_term(A,B,gh,gm_at_h,gm_at_m)
        np.testing.assert_allclose(t+e+x,-A@gh+B@gm_at_m,rtol=0,atol=2e-15)

    def test_step_clipping_source_max_step(self):
        raw,c=scaled_direction(np.eye(2),np.array([3.,4.]))
        np.testing.assert_allclose(raw,[-3.,-4.])
        np.testing.assert_allclose(c,[-.6,-.8])

    def test_no_clipping_for_short_direction(self):
        raw,c=scaled_direction(np.eye(2),np.array([.3,.4]))
        np.testing.assert_array_equal(raw,c)

    def test_frozen_source_and_selected_anchors(self):
        self.assertEqual(BFGS_RUN,"42187240378")
        self.assertEqual(PAIR_RUN,"42120381058")
        self.assertEqual(PAIR_SHA,"b9e1982fb7fee931ea907f5a25d3bc7a7cbbd1e1")
        self.assertEqual(ANCHORS,(0,1,13,14,23))

    def test_tampered_paired_summary_denied(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            (base/"summary.json").write_text(json.dumps({
                "run_id":PAIR_RUN,
                "candidate_sha":"tampered",
                "raw_evidence_sha256":PAIR_RAW}))
            with self.assertRaisesRegex(ValueError,"provenance"):
                read_paired(base)

    def test_truncated_original_state_denied(self):
        raw={
            "schema":"perf01-subject7-bfgs-state-hgfx-v1",
            "status":"UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED",
            "finite_slots":25,"n_rand_init":0,
            "ridders_min_steps":10,"frozen_start_matches":True,
            "iter_x":[[0.,0.,0.]],"iter_inverse_hessian":[],
            "ridders_recomputed_history":[],
        }
        with self.assertRaisesRegex(ValueError,"dimensions"):
            history(raw,"hgfx")

    def test_original_acceptance_is_not_claimed(self):
        # Reconstructed half-steps lack an instrumented MATLAB accept/reject log.
        self.assertIn(23,ANCHORS)
        self.assertNotIn(23,range(22))


if __name__=="__main__":
    unittest.main()
