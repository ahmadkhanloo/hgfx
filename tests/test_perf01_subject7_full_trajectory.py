"""Issue 89 PERF-01D complete frozen fitted trajectory parity negative controls."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))

from compare_subject7_full_fit_trajectories import (
    DESCRIPTIVE, HGFX_SHA, MATLAB_SHA, TRIAL_TOL, SOURCE_FIELDS,
    compare_pair, detailed_differences, validate_new,
)
from fit_cohort_hgfx import FIT_FIELDS
from compare_fits import TOLS


def full_row():
    optim={name:0. for name in FIT_FIELDS}
    optim["init"]=[None]*15
    optim["init"][12]=-3.
    optim["init"][13]=-6.
    optim["init"][14]=3.871201010907891
    optim["final"]=optim["init"][:]
    optim["decompLME"]={"logjoint":0.,"postpredcorr":0.,"freepars":0.}
    traj={name:[[0.,0.,0.] for _ in range(128)] for name in (
        "da","epsi","mu","muhat","psi","sa","sahat","ud","v","w","wt")}
    return {"optim":optim,"traj":traj}


def new_case(mode="auto"):
    original=full_row()
    return {**original,
        "schema":"perf01d-subject7-full-fit-traj-hgfx-v1",
        "status":"AUTHOR_SIDE_UNTIMED_COMPLETE_PUBLIC_FIT_NO_PARITY_DECISION",
        "subject_index_zero_based":7,"trials":128,"model":"hgf_binary",
        "observation":"unitsq_sgm",
        "frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run_id":"41863441006",
        "original_64_raw_sha256":{"hgfx_raw.json":"frozen-h","matlab_raw.json":"frozen-m"},
        "source_input_sha256":"input-h","source_config_sha256":"config-h",
        "frozen_start_matches":True,"n_rand_init":0,
        "history_buffer_slots":101,"finite_history_slots":25,
        "blas_mode_requested":None if mode=="auto" else "Haswell",
    }


def summary():
    return {"raw_evidence_sha256":{"hgfx_raw.json":"frozen-h","matlab_raw.json":"frozen-m"},
            "hgfx_input_sha256":"input-h","hgfx_config_sha256":"config-h"}


class TestFullFittedTrajectory(unittest.TestCase):
    def test_unmodified_exact_original_numeric_tolerance(self):
        self.assertEqual(TRIAL_TOL,(3e-8,3e-10))
        self.assertEqual(SOURCE_FIELDS,("mu","muhat"))
        self.assertEqual(TOLS["final"],(3e-8,3e-10))
        self.assertEqual(DESCRIPTIVE,"UNFROZEN_AUTHOR_SIDE_COMPLETE_TRAJECTORY_COMPARISON_NO_SCIENCE_PASS")

    def test_complete_original_fields_no_mismatches(self):
        a=full_row();b=full_row()
        result=compare_pair(a,b)
        self.assertEqual(result["mismatched_fields"],[])
        self.assertEqual(result["classification"],
            "FULL_FIT_OUTPUTS_WITHIN_ORIGINAL_NUMERIC_TOLERANCES_DIAGNOSTIC_ONLY")
        self.assertEqual(result["field_count"],len(TOLS)+3+len(a["traj"]))

    def test_original_failed_critical_trial_mismatch_preserved(self):
        a=full_row();b=full_row()
        a["traj"]["mu"][83][1]=7.841805399477764e-10
        a["traj"]["muhat"][84][1]=7.841805399477764e-10
        x=compare_pair(a,b)
        self.assertEqual(x["mismatched_fields"],["traj.mu","traj.muhat"])
        self.assertEqual(x["critical_field_mismatch_details"]["traj.mu"][0]["index_zero_based"],[83,1])
        self.assertEqual(x["critical_field_mismatch_details"]["traj.muhat"][0]["trial_one_based"],85)
        self.assertIn("MISMATCH",x["classification"])

    def test_exact_old_tolerance_catches_near_zero(self):
        data=detailed_differences([[1.e-8]],[[0.]],3e-8,3e-10)
        self.assertEqual(len(data),1)
        self.assertEqual(data[0]["unchanged_tolerance_bound_at_reference"],3e-10)

    def test_missing_traj_field_rejected(self):
        a=full_row();b=full_row()
        del a["traj"]["muhat"]
        with self.assertRaisesRegex(ValueError,"inventory"):
            compare_pair(a,b)

    def test_extra_fit_field_rejected(self):
        a=full_row();b=full_row()
        a["optim"]["unapproved"]="new"
        with self.assertRaisesRegex(ValueError,"inventory"):
            compare_pair(a,b)

    def test_new_case_mode_rejects_altered_input(self):
        c=new_case()
        c["source_input_sha256"]="tampered"
        with self.assertRaisesRegex(ValueError,"not verified"):
            validate_new(c,"auto",summary(),full_row())

    def test_new_case_mode_rejects_wrong_dispatch(self):
        c=new_case("Haswell")
        with self.assertRaisesRegex(ValueError,"not verified"):
            validate_new(c,"auto",summary(),full_row())

    def test_new_case_mode_accepts_exact_same_start(self):
        c=new_case()
        self.assertEqual(validate_new(c,"auto",summary(),full_row())["trials"],128)

    def test_no_restarts_accepted(self):
        c=new_case()
        c["n_rand_init"]=1
        with self.assertRaisesRegex(ValueError,"not verified"):
            validate_new(c,"auto",summary(),full_row())

    def test_missing_new_raw_trajectory_rejected(self):
        c=new_case()
        del c["traj"]["mu"]
        with self.assertRaisesRegex(ValueError,"fields"):
            validate_new(c,"auto",summary(),full_row())

    def test_wrong_old_start_rejected(self):
        c=new_case()
        c["optim"]["init"][12]=-2.
        with self.assertRaisesRegex(ValueError,"start"):
            validate_new(c,"auto",summary(),full_row())


if __name__=="__main__":
    unittest.main()
