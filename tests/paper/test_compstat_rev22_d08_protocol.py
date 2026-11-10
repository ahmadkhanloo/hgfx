"""REV-2.2 official D08 protocol/transport tests; synthetic only, no fitting."""

from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import unittest

import numpy as np

from tools.compstat_rev22_d08_hgfx import (
    NATIVE_SIM,PROTOCOL,f64,hessian_diagnostics,jsonarray,
)
from tools.compstat_rev22_d08_compare import (
    input_identity,pair_field,
)

ROOT=Path(__file__).resolve().parents[2]


class Rev22D08SyntheticContractTests(unittest.TestCase):
    def test_original_release_family_and_case_are_frozen(self):
        self.assertEqual(PROTOCOL,"compstat-rev2-2-d08-original-oracle-v1")
        self.assertEqual(NATIVE_SIM,
                         [1.04,1.,.0001,.1,0.,0.,1.,-13.,-2.,1e4])
        script=(ROOT/"reference/matlab/run_rev22_d08_matlab.m").read_text()
        self.assertIn("123456789",script)
        self.assertIn("'uhgf'",script)
        self.assertIn("'gaussian_obs'",script)
        self.assertIn("numel(x)==614",script)
        self.assertIn("quasinewton_optim_config",script)
        self.assertNotIn("314159265",script)
        self.assertNotIn("riddersgradient(",script)
        self.assertNotIn("fminunc(",script)

    def test_frozen_reference_data_and_code_sha(self):
        src=ROOT/"external/hgf-toolbox/demo/example_usdchf.txt"
        self.assertTrue(src.is_file())
        sha=subprocess.check_output(
            ["git","-C",str(ROOT/"external/hgf-toolbox"),
             "hash-object","demo/example_usdchf.txt"],text=True
        ).strip()
        self.assertEqual(sha,"29a4d0322faf8894c414883c517950aa87b481db")
        self.assertEqual(len(np.loadtxt(src)),614)
        m=ROOT/"reference/matlab/export_m18_workflows.m"
        self.assertEqual(subprocess.check_output(
            ["git","hash-object",str(m)],cwd=ROOT,text=True
        ).strip(),"bc5dae87294e106ca57532c995ea92ac091ed313")

    def test_matlab_ieee_column_major_array_restored_without_discard(self):
        a={"hgfx_numeric":"ieee-strings-v1","shape":[2,3],
           "data":[1.,2.,3.,"NaN","Infinity","-Infinity"]}
        out=f64(a)
        self.assertEqual(out.shape,(2,3))
        self.assertEqual(out[0,0],1.)
        self.assertEqual(out[1,0],2.)
        self.assertTrue(math.isnan(out[1,1]))
        self.assertTrue(math.isinf(out[0,2]))
        self.assertEqual(out[1,2],-math.inf)

    def test_refuse_missing_or_invalid_ieee_array(self):
        with self.assertRaisesRegex(ValueError,"shape invalid"):
            f64({"hgfx_numeric":"ieee-strings-v1",
                 "shape":[2,3],"data":[1.,2.]})
        with self.assertRaisesRegex(ValueError,"IEEE transport"):
            f64({"shape":[2,3],"data":[1.,2.]})

    def test_existing_frozen_float_tolerance_and_nonfinite_status(self):
        self.assertTrue(pair_field("x",[1.],[1.+1e-10])["ok"])
        self.assertFalse(pair_field("x",[1.],[1.+1e-5])["ok"])
        self.assertTrue(pair_field("x",["NaN"],["NaN"])["ok"])
        self.assertFalse(pair_field("x",["NaN"],[1.])["ok"])
        self.assertTrue(pair_field("x",[1.,2.],[[1.],[2.]])["ok"])
        self.assertFalse(pair_field("x",[[1.,2.]],[[1.],[2.]])["ok"])

    def test_hessian_condition_does_not_forge_pd_for_indefinite_or_nonfinite(self):
        good=hessian_diagnostics([[2.,0.],[0.,1.]])
        self.assertTrue(good["positive_definite"])
        self.assertEqual(good["condition_2"],2.)
        self.assertFalse(hessian_diagnostics([[-2.,0.],[0.,1.]])["positive_definite"])
        self.assertFalse(hessian_diagnostics([[float("nan")]])["finite"])

    def test_json_scalar_ieee_transport_and_matrix(self):
        encoded=jsonarray(np.array([[1.,float("nan")],[float("inf"),-1.]]))
        self.assertEqual(encoded,[[1.,"NaN"],["Infinity",-1.]])

    def test_cross_reference_authentic_identity_rejects_seed_swap(self):
        base={
          "protocol":PROTOCOL,"model":"uhgf","observation_model":"gaussian_obs",
          "seed":314159265,"trials":614,
          "reference_commit":"2437f4dc241541072722a2695ddeca7b44d83dd3",
          "release_source_commit":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        }
        a=dict(base,source="matlab")
        a["inputs"]=[1.]*614;a["responses"]=[.5]*614
        a["native_simulation"]=NATIVE_SIM;a["native_observation"]=.00002
        b=dict(base,source="hgfx")
        b["wheel_sha256"]="5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90"
        b["inputs_f64_sha256"]=sha256(
            np.asarray(a["inputs"],dtype="<f8").tobytes()).hexdigest()
        b["responses_f64_sha256"]=sha256(
            np.asarray(a["responses"],dtype="<f8").tobytes()).hexdigest()
        c=dict(base,source="matlab_cross")
        with self.assertRaisesRegex(ValueError,"official D08"):
            input_identity(a,b,c)

    def test_cross_evaluation_must_not_refit_or_tune(self):
        x=(ROOT/"reference/matlab/run_rev22_d08_matlab_cross.m").read_text()
        self.assertIn("rev22_objective_at_endpoint",x)
        self.assertNotIn("fitModel(",x.split("function out=rev22_objective_at_endpoint")[1])
        self.assertNotIn("fminunc(",x)
        self.assertIn("matlab_original_negLj",x)
        self.assertIn("original_matlab_fit_rerun=false",x)

    def test_no_unauthorized_global_parity_claim(self):
        x=(ROOT/"tools/compstat_rev22_d08_compare.py").read_text()
        self.assertIn('scientific_global_parity":"NOT_GLOBAL_PASS"',x)
        self.assertIn('NO_PREDECLARED_UHGF_FAMILY_GATE',x)
        self.assertIn('UNRESOLVED_DISCREPANCY',x)


if __name__=="__main__":
    unittest.main()
