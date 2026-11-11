"""PERF-01D original full-fit dispatch comparator cannot redefine science gate."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_issue90_hgfx_full_fit import (
    HGFX, MATLAB, BFGS_RAW, delta, validate_mode, read_archive
)


def fixture():
    x=[[-3.+i,-6.,3.871201010907891] for i in range(25)]
    t=[np.eye(3).tolist() for _ in range(24)]
    return {
        "schema":"perf01-subject7-bfgs-state-hgfx-v1",
        "status":"UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED",
        "subject_index_zero_based":7,
        "trials":128,
        "source_run_id":"41863441006",
        "frozen_hgfx_sha":HGFX,
        "frozen_matlab_sha":MATLAB,
        "source_input_sha256":"original-input",
        "source_config_sha256":"original-config",
        "n_rand_init":0,
        "finite_slots":25,
        "ridders_min_steps":10,
        "original_raw_fits_verified":True,
        "frozen_start_matches":True,
        "iter_x":x+[[None,None,None]]*76,
        "iter_val":[float(i) for i in range(25)]+[None]*76,
        "iter_inverse_hessian":t,
        "ridders_recomputed_history":[{"grad":[1.,2.,3.]} for _ in range(25)],
        "final_full":[1.,2.,3.],
    }


class TestFullFitDispatch(unittest.TestCase):
    def test_unchanged_original_version_and_raw_source(self):
        self.assertEqual(HGFX,"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27")
        self.assertEqual(MATLAB,"2437f4dc241541072722a2695ddeca7b44d83dd3")
        self.assertEqual(len(BFGS_RAW),2)

    def test_frozen_full_fit_source_valid(self):
        x=fixture()
        item=validate_mode(x,"auto",x)
        self.assertEqual(item["x"].shape,(101,3))
        self.assertEqual(item["T"].shape,(24,3,3))

    def test_unequal_full_fit_inputs_rejected(self):
        src=fixture()
        other=fixture()
        other["source_config_sha256"]="tampered"
        with self.assertRaisesRegex(ValueError,"checksum"):
            validate_mode(src,"auto",other)

    def test_original_parameter_start_rejected_if_modified(self):
        src=fixture()
        src["iter_x"][0][0]=0.5
        with self.assertRaisesRegex(ValueError,"start"):
            validate_mode(src,"auto",fixture())

    def test_lost_original_fit_slot_rejected(self):
        src=fixture()
        src["iter_val"][23]=None
        with self.assertRaisesRegex(ValueError,"history"):
            validate_mode(src,"auto",fixture())

    def test_nonpass_modification_rejected(self):
        src=fixture()
        src["status"]="PARITY_PASS"
        with self.assertRaisesRegex(ValueError,"metadata"):
            validate_mode(src,"auto",fixture())

    def test_nan_mask_no_finite_false_positive(self):
        arr1=np.array([1.,np.nan,np.nan])
        arr2=np.array([1.,np.nan,np.nan])
        out=delta(arr1,arr2)
        self.assertEqual(out["number_nonzero_finite_coordinate_differences"],0)
        self.assertTrue(out["nonfinite_masks_match"])
        self.assertTrue(out["bitwise_value_equality"])

    def test_inf_sign_mask_checked(self):
        out=delta([float("inf")],[-float("inf")])
        self.assertFalse(out["nonfinite_masks_match"])

    def test_different_numeric_endpoint_detected(self):
        out=delta([1.,2.,3.],[1.,2.,4.])
        self.assertEqual(out["max_abs_diff"],1.)
        self.assertEqual(out["number_nonzero_finite_coordinate_differences"],1)
        self.assertFalse(out["bitwise_value_equality"])

    def test_archived_missing_original_is_not_recreated(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileNotFoundError):
                read_archive(Path(t))


if __name__=="__main__":
    unittest.main()
