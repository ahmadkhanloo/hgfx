"""REV-2.4 original Panel E contract tests — synthetic ONLY, no fit/oracle."""
from __future__ import annotations

from types import SimpleNamespace
import copy
import json
import unittest

import numpy as np

from tools.compstat_rev24_panel_e_inputs import digest
from tools.compstat_rev24_panel_e_hgfx import (
    EXPECTED, as_float_array, evaluate, evaluate_case,
    validate_inputs,
)
from tools.compstat_rev24_panel_e_compare import audit


def fake_manifest():
    cases=[]
    for i,cid in enumerate(EXPECTED):
        model,obs,t,n,ov=(
            ("ehgf_binary","unitsq_sgm",320,15,0.5) if i==0 else
            ("uhgf","gaussian_obs",614,11,0.1) if i==1 else
            ("hgf_binary","unitsq_sgm",128,15,1.0)
        )
        full=["NaN"]*(n-3)+[-3.,2.,3.]
        entry={
            "case_id":cid,"perceptual_model":model,"observation_model":obs,
            "trials":t,"inputs":[1.]*t,"responses":[0.]*t,
            "obs_prior_variance":ov,
            "source_prior_variances":None,
            "source":"synthetic-contract-only",
            "endpoints":{"matlab":full,"hgfx":None if i==0 else full.copy()},
        }
        entry["case_sha256"]=digest(entry)
        cases.append(entry)
    return {"protocol":"compstat-rev2-4-objective-cross-eval-v1",
            "panel":"E","science_status":"NOT_EXECUTED",
            "expected_cases":66,
            "source_sha256":{"d02":"a"*64,"d08":"b"*64,"cohort64":"c"*64},
            "original_cohort_inputs_sha256":"d"*64,
            "cases":cases}


def fake_objective(case,full):
    return SimpleNamespace(
        rval=0, log_likelihood=-10.0, neg_log_likelihood=10.,
        neg_log_joint=11.,
        trial_log_likelihoods=np.full(case["trials"],-10.0/case["trials"]),
        perceptual_prior=SimpleNamespace(total=-0.5),
        observation_prior=SimpleNamespace(total=-0.5),
    )


def fake_matlab_output(doc,hg):
    out=copy.deepcopy(hg)
    out["source"]="matlab"
    out.pop("runtime",None)
    out.pop("release_wheel_sha256",None)
    out.pop("private_source_sha256",None)
    out["original_cohort_inputs_sha256"]=doc["original_cohort_inputs_sha256"]
    for row in out["cases"]:
        row["source"]="matlab"
    return out


class Rev24PanelEContracts(unittest.TestCase):
    def test_full_66_cases_and_132_endpoint_slots_preserved(self):
        doc=fake_manifest()
        self.assertEqual(len(validate_inputs(doc)),66)
        r=evaluate(doc,fake_objective,wheel_sha256="c"*64,runtime={"test":True})
        self.assertEqual(len(r["cases"]),132)
        self.assertEqual(sum(x["valid"] for x in r["cases"]),131)
        self.assertEqual(r["cases"][1]["status"],"INSUFFICIENT_REFERENCE_EVIDENCE")
        self.assertIs(json.loads(json.dumps(r,allow_nan=False))["cases"][0]["valid"],True)

    def test_sanitized_comparison_no_raw_values_and_no_global_pass(self):
        doc=fake_manifest()
        hg=evaluate(doc,fake_objective,wheel_sha256="c"*64,runtime={})
        mat=fake_matlab_output(doc,hg)
        result=audit(doc,mat,hg)
        self.assertEqual(result["case_denominator"],66)
        self.assertEqual(result["endpoint_slot_denominator"],132)
        self.assertEqual(result["total_valid_both"],131)
        self.assertEqual(result["summary_by_model"]["hgf_binary"]
                         ["SHARED_OBJECTIVE_WITHIN_EXISTING_GATE"],128)
        self.assertEqual(result["summary_by_model"]["ehgf_binary"]
                         ["INSUFFICIENT_REFERENCE_EVIDENCE"],1)
        self.assertEqual(result["summary_by_model"]["ehgf_binary"]
                         ["NO_PREDECLARED_FAMILY_OBJECTIVE_GATE"],1)
        self.assertEqual(result["summary_by_model"]["uhgf"]
                         ["NO_PREDECLARED_FAMILY_OBJECTIVE_GATE"],2)
        self.assertEqual(result["scientific_gate"],"NOT_GLOBAL_PASS")
        self.assertNotIn('"inputs"',json.dumps(result))
        self.assertNotIn('"responses"',json.dumps(result))
        self.assertNotIn('"endpoints"',json.dumps(result))
        self.assertNotIn('"trial_log_likelihoods"',json.dumps(result))

    def test_one_sided_invalid_preserves_original_slot(self):
        doc=fake_manifest()
        hg=evaluate(doc,fake_objective,wheel_sha256="c"*64,runtime={})
        mat=fake_matlab_output(doc,hg)
        hg["cases"][20]["valid"]=False
        hg["cases"][20]["status"]="INVALID_OBJECTIVE"
        result=audit(doc,mat,hg)
        self.assertEqual(len(result["cases"]),132)
        self.assertEqual(result["cases"][20]["classification"],"ONE_SIDED_INVALID")
        self.assertEqual(result["summary_by_model"]["hgf_binary"]
                         ["ONE_SIDED_INVALID"],1)

    def test_wrong_original_source_and_fabricated_d02_rejected(self):
        doc=fake_manifest()
        doc["cases"][0]["endpoints"]["hgfx"]=["NaN"]*12+[-3.,2.,3.]
        with self.assertRaisesRegex(ValueError,"Original case hash"):
            validate_inputs(doc)
        doc=fake_manifest()
        doc["cases"][1]["perceptual_model"]="uhgf_binary"
        doc["cases"][1]["case_sha256"]=digest(
            {k:v for k,v in doc["cases"][1].items() if k!="case_sha256"})
        with self.assertRaisesRegex(ValueError,"Original frozen config"):
            validate_inputs(doc)

    def test_unexpected_omissions_and_nonfinite_likelihood_not_parity(self):
        doc=fake_manifest()
        hg=evaluate(doc,fake_objective,wheel_sha256="c"*64,runtime={})
        mat=fake_matlab_output(doc,hg)
        hg["cases"].pop()
        with self.assertRaisesRegex(ValueError,"132 slots"):
            audit(doc,mat,hg)
        hg=evaluate(doc,fake_objective,wheel_sha256="c"*64,runtime={})
        hg["cases"][9]["trial_log_likelihoods"][0]="NaN"
        with self.assertRaisesRegex(ValueError,"valid per-trial likelihood"):
            audit(doc,mat,hg)

    def test_nonfinite_original_endpoints_preserve_status_no_imputation(self):
        doc=fake_manifest()
        doc["cases"][2]["endpoints"]["matlab"][-1]="NaN"
        doc["cases"][2]["case_sha256"]=digest(
            {k:v for k,v in doc["cases"][2].items() if k!="case_sha256"})
        seen=[]
        def objective(case, full):
            seen.append(full[-1])
            return fake_objective(case,full)
        r=evaluate(doc,objective,wheel_sha256="c"*64,runtime={})
        self.assertTrue(any(np.isnan(x) for x in seen))
        self.assertEqual(len(r["cases"]),132)


if __name__=="__main__":
    unittest.main()
