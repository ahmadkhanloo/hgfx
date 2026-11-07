"""Source-only synthetic controls for immutable MATLAB chronological archive replay."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"benchmarks"/"runtime_v1"
sys.path.insert(0,str(SRC))
spec=importlib.util.spec_from_file_location("matlab_chronology",SRC/"compare_matlab_direct_call_chronology.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def fixtures():
    xs=[[-3.,-6.,3.871201010907891]]
    xs += [[float(i),float(i+1),float(-i)] for i in range(1,24)]
    xs.append(xs[-1].copy())  # original duplicated terminal slot, not a unique BFGS step
    vs=[100.]+[100.-i for i in range(1,24)]
    vs.append(vs[-1])
    calls=[]
    for i in range(25):
        calls.append({
            "kind":"INITIAL" if i==0 else "LINESEARCH",
            "direct_index_zero_based":i, "call_number":i+1,
            "free_x":xs[i].copy(), "private_objective":vs[i],
        })
    m={
        "github_run_id":v.RAW_REFERENCE_RUN,"tested_sha":v.RAW_REFERENCE_SHA,
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
        "timing":"NOT_RUN","direct_call_count":25,"total_calls":1938,
        "indirect_calls":1913,"direct_counts":[1,24,0,0],
        "native_instrumented_stable_identical":True,
        "native_instrumented_history_identical":True,
    }
    trace={
        "schema":"perf01d-native-matlab-direct-objective-calls-v1",
        "metadata":m,"direct_calls":calls,
        "native_history_x":deepcopy(xs),"native_history_val":vs.copy(),
        "native_history_finite_zero_based":list(range(25)),
    }
    def old(name):
        return {
            "schema":f"perf01-subject7-bfgs-state-{name}-v1",
            "status":"UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED",
            "source_run_id":"41863441006",
            "subject_index_zero_based":7,"model":"hgf_binary","trials":128,
            "frozen_hgfx_sha":v.HGFX,"frozen_matlab_sha":v.MATLAB,
            "original_raw_fits_verified":True,"frozen_start_matches":True,
            "finite_slots":25,"ridders_min_steps":10,"n_rand_init":0,
            "iter_x":deepcopy(xs)+[[None,None,None] for _ in range(76)],
            "iter_val":vs.copy()+[None for _ in range(76)],
            "source_input_sha256":"same","source_config_sha256":"same",
        }
    return trace,old("hgfx"),old("matlab")


class SourceChronologyTests(unittest.TestCase):
    def test_positive_full_sequence_and_terminal_ambiguity(self):
        t,h,m=fixtures()
        z=v.compare_chronology(t,h,m)
        self.assertEqual(z["same_run_exact_chronological_call_to_history_match_count"],25)
        self.assertTrue(z["same_run_exact_chronological_call_to_history_all_equal"])
        self.assertTrue(z["terminal_history_duplicate_last_two"])
        self.assertEqual(z["distinct_exact_binary64_direct_candidate_vectors"],23)
        self.assertIsNone(z["first_same_run_matlab_vs_prior_matlab_history_bit_difference"])
        self.assertEqual(z["original_scientific_fitting"],"63/64 SCIENTIFIC NONPASS")

    def test_missing_source_candidate_is_rejected(self):
        t,h,m=fixtures()
        t["direct_calls"].pop()
        with self.assertRaisesRegex(ValueError,"chronological source call order"):
            v.compare_chronology(t,h,m)

    def test_swapped_candidate_order_is_reported_not_silently_remapped(self):
        t,h,m=fixtures()
        t["direct_calls"][3]["free_x"],t["direct_calls"][4]["free_x"]= (
            t["direct_calls"][4]["free_x"],t["direct_calls"][3]["free_x"])
        z=v.compare_chronology(t,h,m)
        self.assertFalse(z["same_run_exact_chronological_call_to_history_all_equal"])
        self.assertEqual(z["first_nonmatching_direct_row"],3)

    def test_different_actual_coordinate_is_reported_not_thresholded(self):
        t,h,m=fixtures()
        t["direct_calls"][6]["free_x"][0]+=1e-10
        z=v.compare_chronology(t,h,m)
        self.assertEqual(z["first_nonmatching_direct_row"],6)

    def test_source_value_change_is_reported(self):
        t,h,m=fixtures()
        t["direct_calls"][7]["private_objective"]+=0.001
        self.assertEqual(v.compare_chronology(t,h,m)["first_nonmatching_direct_row"],7)

    def test_original_source_frozen_commit_must_match(self):
        t,h,m=fixtures()
        m["frozen_matlab_sha"]="not-the-reference"
        with self.assertRaisesRegex(ValueError,"identity changed"):
            v.compare_chronology(t,h,m)

    def test_original_input_config_must_match(self):
        t,h,m=fixtures()
        h["source_config_sha256"]="changed"
        with self.assertRaisesRegex(ValueError,"input/config"):
            v.compare_chronology(t,h,m)

    def test_science_cannot_be_reclassified(self):
        t,h,m=fixtures()
        t["metadata"]["original_science"]="64/64 PASS"
        with self.assertRaisesRegex(ValueError,"provenance changed"):
            v.compare_chronology(t,h,m)

    def test_forged_reviewer_signoff_is_rejected(self):
        t,h,m=fixtures()
        t["metadata"]["independent_review"]="APPROVED"
        with self.assertRaisesRegex(ValueError,"provenance changed"):
            v.compare_chronology(t,h,m)

    def test_modified_historical_matlab_path_is_preserved_as_difference(self):
        t,h,m=fixtures()
        m["iter_x"][8][1]+=1e-9
        z=v.compare_chronology(t,h,m)
        self.assertEqual(z["first_same_run_matlab_vs_prior_matlab_history_bit_difference"],8)
        self.assertTrue(z["same_run_exact_chronological_call_to_history_all_equal"])

    def test_null_or_nan_source_coordinate_rejected(self):
        t,h,m=fixtures()
        t["direct_calls"][6]["free_x"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            v.compare_chronology(t,h,m)

    def test_signed_zero_distinguished_by_binary64(self):
        self.assertTrue(0.0 == -0.0)
        self.assertFalse(v.same_bits(0.0,-0.0))

    def test_failed_source_digest_is_rejected(self):
        from hashlib import sha256
        self.assertNotEqual(sha256(b"tampered").hexdigest(),v.MATLAB_TRACE_SHA)
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            v.verify_bfgs_source(b"fake",b"fake")


if __name__=="__main__":
    unittest.main()
