"""Synthetic negative/positive checks for within-one-runner dispatch attribution."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_issue90_same_host import compare, ORIGINAL_SHA


def sample(mode):
    rows=[]
    for engine in ("hgfx","matlab"):
        for i in range(24):
            saved="1111111111111111"
            changed="2222222222222222"
            altered=mode!="Haswell" and engine=="hgfx" and i==0
            rows.append({
                "engine":engine,"record_index_zero_based":i,
                "numpy_norm_vs_archived":{
                    "archived_bits":saved,"current_bits":changed if altered else saved},
                "numpy_slope_vs_archived":{
                    "archived_bits":saved,"current_bits":changed if altered else saved},
            })
    return {
        "schema":"perf01d-issue90-host-binary64-ulp-audit-v1",
        "status":"ENGINEERING_ULP_MEASUREMENTS_ONLY_NOT_EXACT_REPLAY_PASS",
        "original_bfgs_run":"42187240378",
        "original_bfgs_raw_sha256":ORIGINAL_SHA,
        "original_fitting_science":"63/64 non-PASS, subject index 7 traj.mu/traj.muhat",
        "total_original_engine_history_rows":48,
        "rows":rows,
        "archived_numpy_norm_ulp_mismatches":0 if mode=="Haswell" else 1,
        "archived_numpy_slope_ulp_mismatches":0 if mode=="Haswell" else 1,
        "runtime":{
            "platform":"Linux-check",
            "linux_cpu_model":"TEST CPU",
            "python":"Python 3.11",
            "numpy":"2.3.5",
            "thread_pools":[{"internal_api":"openblas","architecture":mode}],
            "environment":{
                "OPENBLAS_CORETYPE":None if mode=="auto" else mode,
                "GITHUB_RUN_ID":"fixed-run",
            },
        },
    }


def fixtures():
    return {name:sample(name) for name in ("auto","Haswell","SkylakeX")}


class TestWithinHost(unittest.TestCase):
    def test_48_cases_and_controlled_dispatch(self):
        r=compare(fixtures())
        self.assertEqual(r["status"],
                         "CONTROLLED_SAME_RUNNER_FLOAT_DISPATCH_DIAGNOSTIC_NO_GATE_PASS")
        self.assertEqual(r["total_source_rows"],48)
        self.assertEqual(r["norm_auto_vs_haswell_differing_rows"],1)
        self.assertEqual(r["slope_auto_vs_haswell_differing_rows"],1)
        self.assertEqual(r["norm_auto_vs_skylakex_differing_rows"],0)
        self.assertEqual(r["archived_norm_mismatch_counts"]["Haswell"],0)

    def test_incomplete_dispatch_modes_rejected(self):
        d=fixtures()
        del d["SkylakeX"]
        with self.assertRaisesRegex(ValueError,"three"):
            compare(d)

    def test_different_run_rejected(self):
        d=fixtures()
        d["SkylakeX"]["runtime"]["environment"]["GITHUB_RUN_ID"]="other"
        with self.assertRaisesRegex(ValueError,"Not same"):
            compare(d)

    def test_different_cpu_rejected(self):
        d=fixtures()
        d["Haswell"]["runtime"]["linux_cpu_model"]="other"
        with self.assertRaisesRegex(ValueError,"Not same"):
            compare(d)

    def test_incorrect_numpy_version_rejected(self):
        d=fixtures()
        for x in d.values():
            x["runtime"]["numpy"]="2.4.0"
        with self.assertRaisesRegex(ValueError,"NumPy version"):
            compare(d)

    def test_missing_source_row_rejected(self):
        d=fixtures()
        d["auto"]["rows"].pop()
        with self.assertRaisesRegex(ValueError,"incomplete"):
            compare(d)

    def test_tampered_archived_original_rejected(self):
        d=fixtures()
        d["Haswell"]["original_bfgs_raw_sha256"]["hgfx_raw.json"]="tampered"
        with self.assertRaisesRegex(ValueError,"Invalid"):
            compare(d)

    def test_different_archived_value_rejected(self):
        d=fixtures()
        d["SkylakeX"]["rows"][3]["numpy_norm_vs_archived"]["archived_bits"]="7777777777777777"
        with self.assertRaisesRegex(ValueError,"Original"):
            compare(d)

    def test_wrong_mode_environment_rejected(self):
        d=fixtures()
        d["auto"]["runtime"]["environment"]["OPENBLAS_CORETYPE"]="Haswell"
        with self.assertRaisesRegex(ValueError,"unset"):
            compare(d)

    def test_missing_openblas_source_rejected(self):
        d=fixtures()
        d["auto"]["runtime"]["thread_pools"]=[]
        with self.assertRaisesRegex(ValueError,"OpenBLAS"):
            compare(d)


if __name__=="__main__":
    unittest.main()
