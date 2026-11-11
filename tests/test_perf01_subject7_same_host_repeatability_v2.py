"""Issue 90: fail-closed tests for prospective four-process ABBA replay."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"))
from compare_subject7_same_host_repeatability_v2 import ORDER, STATUS, strict_pair, validate_environment, validate_explicit_coretype
from test_perf01_subject7_full_trajectory import full_row, new_case, summary

def environment():
    result={}
    for name in ORDER:
        mode="SkylakeX" if name.startswith("SkylakeX_") else "Haswell"
        result[name]={
            "run_id":"42299999999","github_sha":"a"*40,
            "platform":"Linux","machine":"x86_64","linux_cpu_model":"test",
            "numpy":"2.3.5","python":"3.11","jax_platforms":"cpu",
            "affinity":[24,25,26,27],"cpu_set_requested":[24,25,26,27],
            "openblas_threads":4,"mode":mode,"raw_sha256":"b"*64,
            "openblas_coretype":"SkylakeX" if mode=="SkylakeX" else "Haswell",
            "pools":[{"internal_api":"openblas",
                      "architecture":"SkylakeX" if mode=="SkylakeX" else "Haswell",
                      "version":"0.3.30","num_threads":4}],
        }
    return result

class ABBAReplay(unittest.TestCase):
    def test_prespecified_order_and_science(self):
        self.assertEqual(ORDER,("SkylakeX_1","Haswell_1","Haswell_2","SkylakeX_2"))
        self.assertIn("ORIGINAL_63_OF_64_NONPASS",STATUS)
    def test_identical_all_28_fields(self):
        a=full_row()
        self.assertTrue(strict_pair(a,deepcopy(a))["all_serialized_binary64_equal"])
        self.assertEqual(strict_pair(a,deepcopy(a))["field_count"],28)
    def test_small_finite_difference_not_hidden(self):
        a=full_row();b=deepcopy(a);b["traj"]["mu"][83][1]=1e-15
        r=strict_pair(a,b)
        self.assertFalse(r["all_serialized_binary64_equal"])
        self.assertEqual(r["fields"]["traj.mu"]["differing_serialized_binary64_values"],1)
    def test_negative_zero_bit_detected(self):
        a=full_row();b=deepcopy(a);b["optim"]["AIC"]=-0.
        self.assertFalse(strict_pair(a,b)["fields"]["AIC"]["serialized_binary64_equal"])
    def test_missing_scientific_field_fails(self):
        a=full_row();b=deepcopy(a);del b["traj"]["mu"]
        with self.assertRaisesRegex(ValueError,"inventory"): strict_pair(a,b)
    def test_controlled_environment(self):
        self.assertTrue(validate_environment(environment())["same_runner_affinity_verified"])
    def test_missing_one_replication_fails(self):
        e=environment();del e["SkylakeX_2"]
        with self.assertRaisesRegex(ValueError,"four predeclared"): validate_environment(e)
    def test_different_cpu_affinity_fails(self):
        e=environment();e["Haswell_2"]["affinity"]=[24,25,26,28]
        with self.assertRaisesRegex(ValueError,"affinity"): validate_environment(e)
    def test_wrong_effective_blas_fails(self):
        e=environment();e["SkylakeX_2"]["pools"][0]["architecture"]="Haswell"
        with self.assertRaisesRegex(ValueError,"OpenBLAS"): validate_environment(e)
    def test_wrong_thread_count_fails(self):
        e=environment();e["Haswell_1"]["openblas_threads"]=1
        with self.assertRaisesRegex(ValueError,"provenance"): validate_environment(e)
    def test_missing_raw_digest_fails(self):
        e=environment();e["SkylakeX_1"]["raw_sha256"]=""
        with self.assertRaisesRegex(ValueError,"checksum"): validate_environment(e)
    def test_mode_swap_fails(self):
        e=environment();e["Haswell_1"]["mode"]="SkylakeX"
        with self.assertRaisesRegex(ValueError,"mode"): validate_environment(e)


    def test_explicit_skylakex_and_haswell_cases_accepted(self):
        frozen=full_row()
        a=new_case("auto");a["blas_mode_requested"]="SkylakeX"
        b=new_case("Haswell")
        self.assertIs(validate_explicit_coretype(a,"SkylakeX",summary(),frozen),a)
        self.assertIs(validate_explicit_coretype(b,"Haswell",summary(),frozen),b)
    def test_wrong_actual_requested_dispatch_rejected(self):
        a=new_case("auto")
        with self.assertRaisesRegex(ValueError,"explicit-coretype"):
            validate_explicit_coretype(a,"SkylakeX",summary(),full_row())
    def test_unknown_dispatch_rejected(self):
        a=new_case("Haswell")
        with self.assertRaisesRegex(ValueError,"Unknown predeclared"):
            validate_explicit_coretype(a,"SandyBridge",summary(),full_row())
    def test_explicit_mode_source_checks_still_strict(self):
        a=new_case("auto");a["blas_mode_requested"]="SkylakeX"
        a["source_config_sha256"]="tampered"
        with self.assertRaisesRegex(ValueError,"explicit-coretype"):
            validate_explicit_coretype(a,"SkylakeX",summary(),full_row())
    def test_explicit_mode_original_start_not_mutated(self):
        a=new_case("auto");a["blas_mode_requested"]="SkylakeX"
        a["optim"]["init"][12]=-2.
        with self.assertRaisesRegex(ValueError,"start"):
            validate_explicit_coretype(a,"SkylakeX",summary(),full_row())

if __name__=="__main__":
    unittest.main()
