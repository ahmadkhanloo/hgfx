"""REV-2.4 D019 prospective diagnostic source/trace contract; SYNTHETIC only."""
from __future__ import annotations

from copy import deepcopy
import unittest
import numpy as np

from tools.compstat_rev24_ehgf019_hgfx_trace import (
    DIAGNOSTIC, SOURCE_CASE, SOURCE_CASE_SHA, SOURCE_MANIFEST_SHA,
    MATRIX_FIELDS, STATE_FIELDS, encode_array,
)
from tools.compstat_rev24_ehgf019_trace_compare import (
    classify, first_status_event, paired_numeric_summary,
    likelihood_status_reproduction, values_checked, ORIGINAL_MEMBERS,
    normalize_matlab_flattened_trace,
)


def fake_trace(side):
    fields={key:[[0.0]*3 for _ in range(128)] for key in MATRIX_FIELDS}
    fields["w"]=[[0.0]*2 for _ in range(128)]
    return {
        "diagnostic":DIAGNOSTIC,
        "source":side,"source_manifest_sha256":SOURCE_MANIFEST_SHA,
        "source_case_id":SOURCE_CASE,"source_case_sha256":SOURCE_CASE_SHA,
        "release_source_commit":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "matlab_reference_commit":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "trials":128,"levels":3,
        "original_600_case_grid_modified":False,
        "scientific_gate":"NOT_ASSESSED_DIAGNOSTIC_ONLY",
        "trial_log_likelihoods":[-0.5]*128,
        "inferred_states":{name:[[0.0]*3 for _ in range(128)]
                           for name in STATE_FIELDS},
        "trajectories":fields,
    }


class OriginalD019TraceContracts(unittest.TestCase):
    def test_original_artifact_has_exact_four_immutable_members(self):
        self.assertEqual(set(ORIGINAL_MEMBERS), {
            "manifest.json", "matlab.json", "hgfx.json", "comparison.json",
        })
        self.assertEqual(ORIGINAL_MEMBERS["comparison.json"],
                         "cfd0c7e9f66890c2873706b77518a721119b725a04393ad99ef71e573c780430")

    def test_matlab_flat_128x3_colmajor_is_transport_only(self):
        original=fake_trace("matlab")
        for field in ("muhat","sahat","mu","sa"):
            original["inferred_states"][field]=[
                1000.0*lev+float(t) for lev in range(3) for t in range(128)
            ]
        for field,matrix in original["trajectories"].items():
            original["trajectories"][field]=[
                matrix[t][lev]
                for lev in range(2 if field=="w" else 3)
                for t in range(128)
            ]
        rebuilt,fields=normalize_matlab_flattened_trace(original)
        self.assertEqual(len(fields),15)
        self.assertEqual(rebuilt["inferred_states"]["mu"][11],
                         [11.0,1011.0,2011.0])
        self.assertEqual(rebuilt["trajectories"]["w"][0],[0.0,0.0])
        values_checked(rebuilt,"matlab")
        self.assertEqual(len(original["inferred_states"]["mu"]),384)
        again,fields2=normalize_matlab_flattened_trace(rebuilt)
        self.assertFalse(fields2)
        self.assertEqual(again,rebuilt)

    def test_ambiguous_matlab_layout_must_fail_closed(self):
        doc=fake_trace("matlab")
        doc["inferred_states"]["mu"]=[0.0]*384
        doc["inferred_states"]["mu"].pop()
        with self.assertRaisesRegex(ValueError,"Unrecognized MATLAB trace"):
            normalize_matlab_flattened_trace(doc)

    def test_trace_identity_and_complete_fields(self):
        doc=fake_trace("matlab")
        values_checked(doc,"matlab")
        values_checked(fake_trace("hgfx"),"hgfx")

    def test_source_case_reference_cannot_be_changed(self):
        doc=fake_trace("hgfx")
        doc["source_case_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"source identity"):
            values_checked(doc,"hgfx")

    def test_first_nonfinite_state_localization_and_trial_label(self):
        left=fake_trace("matlab")
        right=fake_trace("hgfx")
        right["inferred_states"]["sahat"][11][1]="NaN"
        event=first_status_event(left["inferred_states"]["sahat"],
                                 right["inferred_states"]["sahat"],
                                 "inferred_states.sahat")
        self.assertEqual(event["trial_zero_based"],11)
        self.assertEqual(event["level_zero_based"],1)
        self.assertEqual(event["hgfx_status"],"NaN")
        self.assertEqual(event["matlab_status"],"FINITE")

    def test_no_failure_gate_from_ulp_numeric_difference(self):
        left=[[0.1,0.2]]*128
        right=deepcopy(left)
        right[0][0]=np.nextafter(0.1,1.0).item()
        self.assertIsNone(first_status_event(left,right,"trace.mu"))
        r=paired_numeric_summary(left,right,"trace.mu")
        self.assertEqual(r["first_nonidentical_finite"]["trial_zero_based"],0)
        self.assertEqual(r["numeric_gate"],"NONE_PREDECLARED_FOR_EHGF")

    def test_archived_nonfinite_status_reproduction(self):
        archived={"valid":False,"trial_log_likelihoods":[0.0]*11+["NaN"]*117}
        diag={"trial_log_likelihoods":[0.0]*11+["NaN"]*117}
        r=likelihood_status_reproduction(archived,diag)
        self.assertTrue(r["nonfinite_status_reproduced"])
        self.assertEqual(r["archived_nonfinite_first_trial"],11)
        diag["trial_log_likelihoods"][11]=0.0
        self.assertFalse(likelihood_status_reproduction(
            archived,diag)["nonfinite_status_reproduced"])

    def test_nonfinite_json_encoding_and_shape_guard(self):
        values=np.zeros((128,3))
        values[11,0]=np.nan
        values[12,1]=np.inf
        out=encode_array(values)
        self.assertEqual(out[11][0],"NaN")
        self.assertEqual(out[12][1],"+Inf")
        with self.assertRaisesRegex(ValueError,"128-by-level"):
            encode_array(np.zeros((127,3)))

    def test_missing_trace_or_wrong_matrix_width_rejected(self):
        doc=fake_trace("matlab")
        doc["trajectories"]["w"]=[[1.,2.,3.]]*128
        with self.assertRaisesRegex(ValueError,"wrong level"):
            values_checked(doc,"matlab")
        doc=fake_trace("matlab")
        doc["trial_log_likelihoods"].pop()
        with self.assertRaisesRegex(ValueError,"original response length"):
            values_checked(doc,"matlab")

    def test_nonstandard_sentinel_rejected(self):
        for invalid in (True,None,float("inf"),"Infinity","ERROR"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):classify(invalid)


if __name__=="__main__":
    unittest.main()
