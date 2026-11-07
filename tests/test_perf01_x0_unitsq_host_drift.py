"""Negative controls for original 71×128 unitsq same-raw-host bit diagnostics."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import diagnose_original_x0_unitsq_host_drift as d


class OriginalSourceCPUDriftTests(unittest.TestCase):
    def test_equal_128_trial_original_native_ll(self):
        self.assertEqual(d.compare_bits([1.]*128,[1.]*128),[])

    def test_exact_one_ulp_trial_difference_retained(self):
        a=[1.]*128;b=a.copy();b[17]=math.nextafter(1.,math.inf)
        out=d.compare_bits(a,b)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["trial_index_zero_based"],17)
        self.assertEqual(out[0]["binary64_ordered_ulp_distance"],1)
        self.assertEqual(out[0]["original_hex"],"0x1.0000000000000p+0")

    def test_signed_zero_drift_is_not_hidden(self):
        a=[0.]*128;b=a.copy();b[4]=-0.0
        self.assertEqual(d.compare_bits(a,b)[0]["trial_index_zero_based"],4)

    def test_two_distant_original_trial_mismatches_retained(self):
        a=[2.]*128;b=a.copy()
        b[0]=math.nextafter(2.,math.inf)
        b[127]=math.nextafter(2.,-math.inf)
        self.assertEqual([v["trial_index_zero_based"] for v in d.compare_bits(a,b)],[0,127])

    def test_missing_128th_original_trial_not_allowed(self):
        with self.assertRaisesRegex(ValueError,"128-trial"):
            d.compare_bits([1.]*127,[1.]*127)

    def test_extra_original_trial_not_allowed(self):
        with self.assertRaisesRegex(ValueError,"128-trial"):
            d.compare_bits([1.]*129,[1.]*129)

    def test_source_nonfinite_not_allowed(self):
        a=[1.]*128;b=a.copy();b[8]=float("nan")
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            d.compare_bits(a,b)

    def test_source_unknown_type_not_allowed(self):
        a=[1.]*128;b=a.copy();b[8]="1.0"
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            d.compare_bits(a,b)

    def test_sha256_source_pin_verbatim(self):
        self.assertEqual(d.H_SOURCE_SHA,
            "53c998070dbbfc8b8a5c5ce7e8d962b44f9820635f60c567fd2012bf48fcd415")
        self.assertEqual(d.REAL_SHA,
            "a6168bb2b1be07a0f084abc07599e9ffda61b22b")

    def test_environment_fingerprint_captures_numpy_cpu_dispatch(self):
        info=d.runtime_fingerprint()
        self.assertIn("numpy_runtime",info)
        self.assertIn("cpuinfo_first_core",info)
        self.assertTrue(info["numpy"])
        self.assertIn("libc",info)


if __name__=="__main__":unittest.main()
