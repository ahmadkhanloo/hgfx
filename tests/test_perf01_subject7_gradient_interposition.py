"""Pure synthetic controls for the eight precommitted post-result gradient arms.

All tests here are engineering controls and NOT original scientific fitting parity.
"""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

MODULE=Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"/"subject7_exact_anchor_gradient_interposition.py"
spec=importlib.util.spec_from_file_location("subject7_exact_anchor_gradient_interposition",MODULE)
probe=importlib.util.module_from_spec(spec)
# The imported prior source-locked inventory is resolved by the workflow path.
import sys
sys.path.insert(0,str(MODULE.parent))
spec.loader.exec_module(probe)


def sample_rows():
    rows=[]
    for i in range(25):
        x=[float(i),float(-i),float(i)+0.25]
        if i==0:x=list(probe.START)
        if i==6:x=list(probe.SIX)
        if i==24:x=rows[23]["free_parameters"][:]
        g=[float(i)+0.1,float(i)+0.2,float(i)+0.3]
        rows.append({"free_parameters":x,"hgfx":{"gradient":g[:]},
                     "matlab":{"gradient":[v+0.001 for v in g]}})
    return rows


def fake_fn(function,x,options=None):
    return [11.,12.,13.],[0.1,0.2,0.3]


class ExactAnchorCounterfactualSyntheticTests(unittest.TestCase):
    def test_arm_denominator_and_order_are_fixed(self):
        self.assertEqual(len(probe.ARMS),8)
        self.assertEqual(probe.ARMS[0],"baseline_unmodified")
        self.assertEqual(probe.ARMS[-1],"matlab_gradient_all_original_hgfx_history_25")

    def test_source_original_scientific_failure_retained_as_hardcode(self):
        self.assertEqual(probe.SOURCE_50_RUN,"42305573614")
        self.assertEqual(probe.START,(-3.,-6.,3.871201010907891))
        self.assertEqual(probe.SIX[0],-1.1621811570388512)

    def test_exact_same_binary64(self):
        self.assertEqual(probe.xyz_key(probe.START),probe.xyz_key(list(probe.START)))

    def test_one_ulp_anchor_must_not_match(self):
        x=list(probe.START)
        x[0]=math.nextafter(x[0],math.inf)
        self.assertNotEqual(probe.xyz_key(x),probe.xyz_key(probe.START))

    def test_bad_vector_fails_closed(self):
        with self.assertRaises(ValueError):
            probe.xyz_key([1.,2.])
        with self.assertRaises(ValueError):
            probe.xyz_key([1.,2.,math.nan])

    def test_arm_target_scope_source_counts(self):
        rows=sample_rows()
        expected={
            "baseline_unmodified":0,
            "placebo_original_hgfx_gradient_at_start":1,
            "matlab_gradient_start_component0":1,
            "matlab_gradient_start_all3":1,
            "matlab_gradient_record6_component0":1,
            "matlab_gradient_record6_all3":1,
            "matlab_gradient_start_and_record6_all3":2,
            "matlab_gradient_all_original_hgfx_history_25":24,
        }
        for arm,n in expected.items():
            self.assertEqual(len(probe.arm_sources(arm,rows)),n,arm)

    def test_placebo_returns_hgfx_archived_gradient(self):
        rows=sample_rows()
        mapping=probe.arm_sources("placebo_original_hgfx_gradient_at_start",rows)
        self.assertTrue((mapping[probe.xyz_key(probe.START)]["target"]==rows[0]["hgfx"]["gradient"]).all())

    def test_original_source_history_duplicates_cannot_conflict(self):
        rows=sample_rows()
        rows[24]["matlab"]["gradient"][0]+=1.
        with self.assertRaises(ValueError):
            probe.arm_sources("matlab_gradient_all_original_hgfx_history_25",rows)

    def test_matlab_substituted_first_component_only(self):
        rows=sample_rows()
        fake=SimpleNamespace(ridders_gradient=fake_fn)
        prov={}
        with probe.interposition(fake,fake_fn,"matlab_gradient_record6_component0",rows,prov) as (hits,m):
            g,e=fake.ridders_gradient(None,list(probe.SIX))
            self.assertEqual(g[0],rows[6]["matlab"]["gradient"][0])
            self.assertEqual(g[1],12.)
            self.assertEqual(g[2],13.)
            self.assertEqual(len(hits),1)
            self.assertEqual(prov["calls"][0]["replaced_component_indices_zero_based"],[0])
        self.assertIs(fake.ridders_gradient,fake_fn)

    def test_no_exact_anchor_is_not_intervened(self):
        rows=sample_rows()
        fake=SimpleNamespace(ridders_gradient=fake_fn)
        prov={}
        x=list(probe.SIX)
        x[0]=math.nextafter(x[0],math.inf)
        with probe.interposition(fake,fake_fn,"matlab_gradient_record6_all3",rows,prov) as (hits,m):
            g,e=fake.ridders_gradient(None,x)
            self.assertEqual(g,[11.,12.,13.])
            self.assertEqual(len(hits),0)
            self.assertFalse(prov["calls"][0]["intervened"])

    def test_all3_changes_all_components(self):
        rows=sample_rows()
        fake=SimpleNamespace(ridders_gradient=fake_fn)
        prov={}
        with probe.interposition(fake,fake_fn,"matlab_gradient_start_all3",rows,prov) as (hits,m):
            g,e=fake.ridders_gradient(None,list(probe.START))
            self.assertEqual(list(g),rows[0]["matlab"]["gradient"])
            self.assertEqual(e,[.1,.2,.3])
        self.assertIs(fake.ridders_gradient,fake_fn)

    def test_original_gradient_restored_when_exception(self):
        rows=sample_rows()
        fake=SimpleNamespace(ridders_gradient=fake_fn)
        with self.assertRaisesRegex(RuntimeError,"fixture"):
            with probe.interposition(fake,fake_fn,"matlab_gradient_start_all3",rows,{}):
                raise RuntimeError("fixture")
        self.assertIs(fake.ridders_gradient,fake_fn)

    def test_cannot_enter_double_patched_state(self):
        rows=sample_rows()
        fake=SimpleNamespace(ridders_gradient=lambda x:None)
        with self.assertRaises(ValueError):
            with probe.interposition(fake,fake_fn,"matlab_gradient_start_all3",rows,{}):
                pass

    def test_baseline_does_not_modify_original_ridders(self):
        rows=sample_rows()
        fake=SimpleNamespace(ridders_gradient=fake_fn)
        with probe.interposition(fake,fake_fn,"baseline_unmodified",rows,{}) as (hits,m):
            self.assertIs(fake.ridders_gradient,fake_fn)
            self.assertEqual(m,{})
            self.assertEqual(hits,set())


if __name__=="__main__":
    unittest.main()
