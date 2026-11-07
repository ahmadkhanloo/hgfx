"""Issue #90: exact binary64 audit maths and original raw-provenance guards."""
from __future__ import annotations

from pathlib import Path
import json
import math
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from audit_subject7_host_binary64 import (
    RUN, CANDIDATE, SHA, STATUS,
    bits, ulp_distance, decimal_dot, decimal_norm, matvec_decimal,
    inspect_scalar, verify,
)


class TestHostFloatAudit(unittest.TestCase):
    def test_frozen_archived_run_and_keys(self):
        self.assertEqual(RUN,"42187240378")
        self.assertEqual(CANDIDATE,"5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d")
        self.assertEqual(len(SHA),2)
        self.assertIn("NOT_EXACT_REPLAY_PASS",STATUS)

    def test_binary64_bits_exact(self):
        self.assertEqual(bits(1.),"3ff0000000000000")
        self.assertEqual(bits(-0.),"8000000000000000")
        self.assertEqual(bits(0.),"0000000000000000")

    def test_ulp_one_positive(self):
        self.assertEqual(ulp_distance(1.,math.nextafter(1.,math.inf)),1)
        self.assertEqual(ulp_distance(1.,math.nextafter(1.,-math.inf)),1)

    def test_ulp_one_negative(self):
        self.assertEqual(ulp_distance(-1.,math.nextafter(-1.,math.inf)),1)
        self.assertEqual(ulp_distance(-1.,math.nextafter(-1.,-math.inf)),1)

    def test_ulp_zero_distinct(self):
        self.assertEqual(ulp_distance(-0.,0.),1)
        self.assertEqual(ulp_distance(2.,2.),0)

    def test_nonfinite_ulp_refused(self):
        with self.assertRaisesRegex(ValueError,"finite"):
            ulp_distance(float("nan"),1.)

    def test_decimal_dot_is_exact_f64_operands(self):
        self.assertEqual(decimal_dot([1.,2.,3.],[4.,5.,6.]),32.)
        self.assertEqual(decimal_dot([1.,1e16,-1e16],[1.,1.,1.]),1.)

    def test_decimal_norm(self):
        self.assertEqual(decimal_norm([3.,4.]),5.)
        self.assertEqual(decimal_norm([0.,0.,0.]),0.)

    def test_frozen_three_parameter_matrix_only(self):
        T=np.diag([1.,2.,3.]);g=np.array([2.,3.,4.])
        np.testing.assert_array_equal(matvec_decimal(T,g),[-2.,-6.,-12.])
        with self.assertRaisesRegex(ValueError,"three-free-parameter"):
            matvec_decimal(np.eye(2),np.ones(2))

    def test_scalar_audit_reports_exact_ulp(self):
        v=math.nextafter(1.,math.inf)
        report=inspect_scalar(v,1.)
        self.assertFalse(report["exact_binary64_match"])
        self.assertEqual(report["ulps"],1)
        self.assertEqual(report["archived_bits"],bits(1.))

    def test_source_summary_sha_identity_denied_if_changed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"summary.json").write_text(json.dumps({
                "github_run_id":RUN,
                "candidate_sha":"edited_after_run",
                "raw_evidence_sha256":SHA,
            }))
            (p/"comparison.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"identity"):
                verify(p)

    def test_replay_does_not_relax_original_status(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            orig={
                "github_run_id":RUN,
                "candidate_sha":CANDIDATE,
                "raw_evidence_sha256":SHA,
                "source_run_id":"41863441006",
                "status":"SCIENTIFIC_PARITY_PASS",
            }
            (p/"summary.json").write_text(json.dumps(orig))
            (p/"comparison.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"identity"):
                verify(p)


if __name__=="__main__":
    unittest.main()
