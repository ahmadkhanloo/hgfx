"""REV-2.4 Panel E derived endpoint bound contracts; NO new objectives."""
import json
import math
import unittest

from tools.compstat_rev24_endpoint_gap_bounds import (
    endpoint_bound,compute_bounds,
)


def fixture():
    d08={
        "case_id":"D08_fit","model":"uhgf",
        "observation":"gaussian_obs","negLj":4.0,
    }
    d08c={"objective":{"matlab_negLj":4.0,"hgfx_fit_negLj":4.2}}
    def raw(side):
        return {"model":"hgf_binary","observation_model":"unitsq_sgm",
                "input_sha256":"6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae",
                "cases":[{"subject_index_zero_based":i,
                          "optim":{"negLj":100.0+i+(0.1 if side=="hgfx" else 0)}}
                         for i in range(64)]}
    rows=[
        {"case_id":"D02_fit","at_original_endpoint":"matlab",
         "classification":"NO_PREDECLARED_FAMILY_OBJECTIVE_GATE"},
        {"case_id":"D02_fit","at_original_endpoint":"hgfx",
         "classification":"INSUFFICIENT_REFERENCE_EVIDENCE"},
    ]
    for side in ("matlab","hgfx"):
        rows.append({
            "case_id":"D08_fit","at_original_endpoint":side,
            "model":"uhgf","matlab_valid":True,"hgfx_valid":True,
            "objective_field_abs_differences":{
                "neg_log_joint":{"abs_difference":0.0}},
        })
    for i in range(64):
        for side in ("matlab","hgfx"):
            rows.append({
                "case_id":f"cohort64_subject_{i:02d}",
                "at_original_endpoint":side,"model":"hgf_binary",
                "matlab_valid":True,"hgfx_valid":True,
                "objective_field_abs_differences":{
                    "neg_log_joint":{"abs_difference":0.005}},
            })
    doc={"protocol":"compstat-rev2-4-objective-cross-eval-v1",
         "panel":"E","scientific_gate":"NOT_GLOBAL_PASS",
         "case_denominator":66,"endpoint_slot_denominator":132,
         "original_cohort_inputs_sha256":
         "6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae",
         "cases":rows}
    return d08,d08c,raw("matlab"),raw("hgfx"),doc


class PanelEGapBoundsTests(unittest.TestCase):
    def test_bound_triangle_and_zero_error(self):
        x=endpoint_bound(5,5.1,0,0)
        self.assertAlmostEqual(x["observed_cross_fit_objective_gap"],0.1)
        self.assertAlmostEqual(x["matlab_endpoint_objective_gap_lower_bound"],0.1)
        self.assertAlmostEqual(x["hgfx_endpoint_objective_gap_upper_bound"],0.1)
        y=endpoint_bound(2,2.1,0.05,0.02)
        self.assertAlmostEqual(y["matlab_endpoint_objective_gap_lower_bound"],0.08)
        self.assertAlmostEqual(y["matlab_endpoint_objective_gap_upper_bound"],0.12)
        self.assertAlmostEqual(y["hgfx_endpoint_objective_gap_lower_bound"],0.05)
        self.assertAlmostEqual(y["hgfx_endpoint_objective_gap_upper_bound"],0.15)

    def test_all_subject_bounds_and_d02_missing_retained(self):
        result=compute_bounds(*fixture())
        self.assertEqual(result["original_subjects"],64)
        self.assertEqual(result["complete_original_endpoint_pairs"],65)
        self.assertEqual(result["missing_original_hgfx_endpoint"],["D02_fit"])
        self.assertEqual(result["cohort64"]["max_observed_cross_fit_objective_gap"]
                         ["subject_zero_based"],0)
        self.assertAlmostEqual(result["d08"]["observed_cross_fit_objective_gap"],0.2)
        self.assertEqual(result["science_execution"],"NONE_NEW")
        self.assertFalse(result["accepted_as_new_gate"])
        self.assertEqual(result["reported_panel_e_science_gate"],"NOT_GLOBAL_PASS")
        raw=json.dumps(result)
        self.assertNotIn('"inputs"',raw)
        self.assertNotIn('"responses"',raw)
        self.assertNotIn('"optim"',raw)

    def test_subject_removed_is_rejected(self):
        args=list(fixture())
        args[3]["cases"].pop(7)
        with self.assertRaisesRegex(ValueError,"64-subject"):
            compute_bounds(*args)

    def test_source_model_or_endpoint_substitution_rejected(self):
        args=list(fixture())
        args[0]["model"]="uhgf_binary"
        with self.assertRaisesRegex(ValueError,"D08 source model"):
            compute_bounds(*args)
        args=list(fixture())
        args[-1]["cases"][1]["classification"]="NO_PREDECLARED_FAMILY_OBJECTIVE_GATE"
        with self.assertRaisesRegex(ValueError,"D02 absent"):
            compute_bounds(*args)

    def test_abs_gap_negative_not_permitted(self):
        with self.assertRaisesRegex(ValueError,"Negative absolute"):
            endpoint_bound(1,1,-0.1,0.1)

    def test_original_inputs_and_validity_required(self):
        args=list(fixture())
        args[-1]["original_cohort_inputs_sha256"]="x"*64
        with self.assertRaisesRegex(ValueError,"original paired"):
            compute_bounds(*args)
        args=list(fixture())
        args[-1]["cases"][4]["hgfx_valid"]=False
        with self.assertRaisesRegex(ValueError,"objective invalid"):
            compute_bounds(*args)


if __name__=="__main__":unittest.main()
