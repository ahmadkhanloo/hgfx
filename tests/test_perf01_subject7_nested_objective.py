"""Fail-closed controls for prespecified native 50-anchor real fitModel objective hook."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from subject7_nested_fitmodel_objective import (
    get_anchor_records,HGFX_SHA,MATLAB_SHA,SOURCE_RUN,SOURCE_COMMIT,
    MATLAB_RAW_SHA256,STATUS,ROWS,EXPECTED_START,
)

def valid_source():
    def case():
        x=[list(EXPECTED_START)]+[[float(j),float(j+1),float(j+2)]
                                   for j in range(1,ROWS)]
        x.extend([[None,None,None] for _ in range(101-ROWS)])
        return {"subject_index_zero_based":7,"n_trials":128,
                "start_matches_frozen_snapshot":True,"n_rand_init":0,
                "finite_optimizer_history_slots":25,
                "optimizer_iteration_count":101,
                "optimizer_history":{"x":x,"val":[float(j) for j in range(25)]+[None]*76}}
    return {
        "schema":"perf01d-subject7-same-runner-matlab-v1",
        "status":"AUTHOR_SIDE_UNTIMED_FROZEN_MATLAB_TWO_PUBLIC_FITS_NO_PARITY_DECISION",
        "github_run_id":SOURCE_RUN,"github_sha":SOURCE_COMMIT,
        "frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run":"41863441006",
        "original_63_64_nonpass":True,
        "original_subject_index_zero_based":7,
        "matlab_release":"2026a",
        "no_timing":True,"no_scientific_gate_promotion":True,
        "fit_order":["MATLAB_1","MATLAB_2"],
        "cases":[case(),case()],
    }

class ActualFrozenNestedObjectiveSourceControls(unittest.TestCase):
    def test_predeclared_original_two_by_25_denominator(self):
        rows=get_anchor_records(valid_source())
        self.assertEqual(len(rows),50)
        self.assertEqual([v["anchor_origin"] for v in rows[:25]],["MATLAB_1"]*25)
        self.assertEqual([v["anchor_origin"] for v in rows[25:]],["MATLAB_2"]*25)
        self.assertEqual([v["record_index_zero_based"] for v in rows],
                         list(range(25))*2)
        self.assertEqual(rows[0]["free_parameters"],list(EXPECTED_START))

    def test_status_does_not_promote_original_parity(self):
        self.assertIn("NOT_SCIENTIFIC_PASS",STATUS)
        self.assertEqual(ROWS,25)
        self.assertEqual(len(MATLAB_RAW_SHA256),64)

    def invalid(self,mutate,pattern):
        data=valid_source()
        mutate(data)
        with self.assertRaisesRegex(ValueError,pattern):
            get_anchor_records(data)

    def test_original_63_of_64_failure_cannot_be_rewritten(self):
        self.invalid(lambda d:d.update(original_63_64_nonpass=False),"source/gate")

    def test_frozen_matlab_source_cannot_change(self):
        self.invalid(lambda d:d.update(frozen_matlab_sha="0"*40),"source/gate")

    def test_archived_native_matlab_fit_count_cannot_shrink(self):
        self.invalid(lambda d:d["cases"].pop(),"two unmodified")

    def test_original_25_finite_trace_cannot_shrink(self):
        self.invalid(lambda d:d["cases"][0]["optimizer_history"]["val"].__setitem__(24,None),
                     "25 finite history")

    def test_extra_26th_finite_trace_cannot_be_hidden(self):
        self.invalid(lambda d:d["cases"][0]["optimizer_history"]["val"].__setitem__(25,5.0),
                     "25 finite history")

    def test_original_start_cannot_be_mutated(self):
        self.invalid(lambda d:d["cases"][1]["optimizer_history"]["x"][0].__setitem__(0,-2.),
                     "25 finite history")

    def test_missing_101_buffer_raises(self):
        self.invalid(lambda d:d["cases"][1]["optimizer_history"]["x"].pop(),
                     "101 allocated")

    def test_missing_random_restart_policy_raises(self):
        self.invalid(lambda d:d["cases"][0].update(n_rand_init=1),"fit/start")

    def test_nonfinite_anchor_not_silently_dropped(self):
        self.invalid(lambda d:d["cases"][1]["optimizer_history"]["x"][12].__setitem__(1,None),
                     "25 finite history")

    def test_stored_trajectory_source_matlab_run_cannot_be_changed(self):
        self.invalid(lambda d:d.update(github_run_id="unrelated"),"source/gate")

if __name__=="__main__":
    unittest.main()
