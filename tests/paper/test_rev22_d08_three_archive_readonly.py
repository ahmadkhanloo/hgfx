"""REV-2.2 three original archive audit synthetic contracts. NEVER run HGF."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.compstat_rev22_d08_three_archive_readonly import (
    ARCHIVES,ATOL,RTOL,TRAJECTORIES,arrays_identical,
    f64,paired_status,read_original_zip,
)


class ThreeArchiveReadOnlyContract(unittest.TestCase):
    def test_original_three_immutable_archive_sources_frozen(self):
        self.assertEqual(len(ARCHIVES),3)
        self.assertEqual(len(ARCHIVES["historical"]["members"]),2)
        self.assertEqual(len(ARCHIVES["A"]["members"]),4)
        self.assertEqual(len(ARCHIVES["B"]["members"]),4)
        self.assertEqual(ARCHIVES["A"]["members"]["matlab_reference.json"],
                         ARCHIVES["B"]["members"]["matlab_reference.json"])
        self.assertEqual(len(TRAJECTORIES),12)

    def test_frozen_existing_tolerances_not_relaxed(self):
        self.assertEqual(RTOL,3e-8)
        self.assertEqual(ATOL,3e-10)

    def test_matlab_column_major_101_by_7_is_preserved(self):
        raw={"hgfx_numeric":"ieee-strings-v1","shape":[2,3],
             "data":[1.,2.,3.,"NaN","Infinity","-Infinity"]}
        array=f64(raw)
        self.assertEqual(array.shape,(2,3))
        self.assertEqual(array[0,0],1.)
        self.assertEqual(array[1,0],2.)
        self.assertTrue(np.isnan(array[1,1]))
        self.assertTrue(np.isposinf(array[0,2]))
        self.assertTrue(np.isneginf(array[1,2]))

    def test_aligned_flat_and_column_matrix_have_no_spurious_cross_product(self):
        x=[1.0,2.0,3.0]
        y=[[1.0],[2.0],[3.0]]
        self.assertTrue(arrays_identical(x,y))
        record=paired_status(x,y)
        self.assertEqual(record["shape"],[3])
        self.assertEqual(record["n_values"],3)
        self.assertEqual(record["out_of_existing_numeric_yardstick"],0)

    def test_same_vector_small_float_disagreement_is_not_bitwise_parity(self):
        a=np.array([1.,10.])
        b=np.array([1.+1e-10,10.-5e-9])
        self.assertFalse(np.array_equal(a,b))
        record=paired_status(a,b)
        self.assertEqual(record["out_of_existing_numeric_yardstick"],0)
        self.assertGreater(record["max_absolute_difference_on_finite_pairs"],0.)
        self.assertEqual(record["scientific_family_gate"],
                         "NO_PREDECLARED_UHGF_SAME_VECTOR_GATE")

    def test_nonfinite_status_difference_is_never_ignored(self):
        d=paired_status(np.array([np.nan,np.inf,-np.inf]),
                        np.array([np.nan,-np.inf,-np.inf]))
        self.assertEqual(d["nonfinite_status_differences"],1)
        self.assertEqual(d["out_of_existing_numeric_yardstick"],1)
        self.assertEqual(d["bad_zero_based_coordinates"],[[1]])

    def test_actual_out_of_gate_is_detected_under_existing_not_new_tol(self):
        a=np.array([[1.,2.],[1.,2.]])
        b=a.copy();b[1,0]+=1e-3
        d=paired_status(a,b)
        self.assertEqual(d["out_of_existing_numeric_yardstick"],1)
        self.assertEqual(d["bad_zero_based_coordinates"],[[1,0]])

    def test_reject_wrong_archived_science_zip_before_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"fake.zip"
            p.write_bytes(b"raw model bytes must NEVER be interpreted as original evidence")
            with self.assertRaisesRegex(ValueError,"archive SHA drift"):
                read_original_zip(p,"historical")

    def test_no_model_evaluation_imported_by_read_only_auditor(self):
        p=Path(__file__).resolve().parents[2] / "tools/compstat_rev22_d08_three_archive_readonly.py"
        source=p.read_text(encoding="utf8")
        self.assertNotIn("import hgfx",source)
        self.assertNotIn("import jax",source)
        self.assertNotIn("fitModel(",source)
        self.assertNotIn("quasinewton_optim(",source)


if __name__=="__main__":
    unittest.main()
