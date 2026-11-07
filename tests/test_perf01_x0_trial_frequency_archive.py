"""Fail-closed synthetic all-71 x all-128 original trial LL source audit."""
from __future__ import annotations
from copy import deepcopy
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"benchmarks"/"runtime_v1"))
import compare_original_x0_objective_terms as cv
import aggregate_original_x0_trial_likelihood_bits as freq
from test_perf01_x0_objective_terms import dataset


def fixture():
    h,m,oh,om,fit,raw,env=dataset()
    for i in range(14,71):
        old=m["nodes"][i]["components"]["full_trial_log_likelihood"][0]
        m["nodes"][i]["components"]["full_trial_log_likelihood"][0]=math.nextafter(old,math.inf)
    with patch.dict(os.environ,env):
        checked=cv.audit(h,m,oh,om,fit,raw)
    return h,m,checked


class TrueSourceTrialBitFrequencyControls(unittest.TestCase):
    def test_positive_all_71_original_source_nodes_with_128_trials(self):
        h,m,c=fixture()
        r=freq.aggregate_trial_ll(h,m,c)
        self.assertEqual(r["different_trial_positions_across_all_71_nodes"],1)
        self.assertEqual(r["full_128_trial_position_mismatch_rows"][0]["source_node_mismatch_count"],71)
        self.assertEqual(r["minimum_trial_positions_differing_at_any_node"],1)
        self.assertEqual(r["maximum_trial_positions_differing_at_any_node"],1)
        self.assertEqual(len(r["original_14_final_joint_mismatch_nodes"]),14)

    def test_original_one_ulp_difference_preserved(self):
        h,m,c=fixture()
        r=freq.aggregate_trial_ll(h,m,c)
        self.assertEqual(r["full_128_trial_position_mismatch_rows"][0]["maximum_binary64_trial_ll_ulp_distance"],1)

    def test_another_trial_is_never_silently_excluded(self):
        h,m,c=fixture()
        m["nodes"][22]["components"]["full_trial_log_likelihood"][1]=math.nextafter(1.,math.inf)
        r=freq.aggregate_trial_ll(h,m,c)
        self.assertEqual(r["different_trial_positions_across_all_71_nodes"],2)
        self.assertEqual(r["full_128_trial_position_mismatch_rows"][1]["original_71_source_mismatch_nodes"],[22])

    def test_missing_original_trial_node_refused(self):
        h,m,c=fixture();m["nodes"].pop()
        with self.assertRaisesRegex(ValueError,"provenance"):
            freq.aggregate_trial_ll(h,m,c)

    def test_original_14_real_joint_mismatch_indices_immutable(self):
        h,m,c=fixture();m["nodes"][3]["components"]["negative_log_joint"]=200.
        with self.assertRaisesRegex(ValueError,"14 genuine"):
            freq.aggregate_trial_ll(h,m,c)

    def test_forged_original_scientific_pass_refused(self):
        h,m,c=fixture();c["original_scientific_fit"]="64/64 PASS"
        with self.assertRaisesRegex(ValueError,"provenance"):
            freq.aggregate_trial_ll(h,m,c)

    def test_forged_independent_reviewer_refused(self):
        h,m,c=fixture();c["independent_scientific_review"]="APPROVED"
        with self.assertRaisesRegex(ValueError,"provenance"):
            freq.aggregate_trial_ll(h,m,c)

    def test_missing_128th_trial_refused(self):
        h,m,c=fixture();m["nodes"][8]["components"]["full_trial_log_likelihood"].pop()
        with self.assertRaisesRegex(ValueError,"128"):
            freq.aggregate_trial_ll(h,m,c)

    def test_invalid_trial_mask_refused(self):
        h,m,c=fixture();m["nodes"][12]["components"]["regular_trial_mask"].pop()
        with self.assertRaisesRegex(ValueError,"128"):
            freq.aggregate_trial_ll(h,m,c)

    def test_missing_prior_source_parity_refused(self):
        h,m,c=fixture();c["full_original_71_node_component_counts"]["perceptual_prior_terms"]["nodes_with_bit_difference"]=1
        with self.assertRaisesRegex(ValueError,"provenance"):
            freq.aggregate_trial_ll(h,m,c)

    def test_nonfinite_trial_scalar_refused(self):
        h,m,c=fixture();m["nodes"][40]["components"]["full_trial_log_likelihood"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            freq.aggregate_trial_ll(h,m,c)

    def test_source_node_order_refused(self):
        h,m,c=fixture();m["nodes"][2]["original_node_index"]=3
        with self.assertRaisesRegex(ValueError,"reordered"):
            freq.aggregate_trial_ll(h,m,c)

    def test_all_71_must_really_have_original_trial_ll_difference(self):
        h,m,c=fixture();m["nodes"][40]["components"]["full_trial_log_likelihood"][0]=1.
        with self.assertRaisesRegex(ValueError,"all-71"):
            freq.aggregate_trial_ll(h,m,c)

    def test_sha_bound_to_original_real_success_run(self):
        self.assertEqual(freq.SOURCE_RUN,"42402421462")
        self.assertEqual(len(freq.SHA),3)
        self.assertEqual(freq.SOURCE_SHA,"3ae1ac5330bd1b6bc1ea8017f16f0f66be6b3b57")


if __name__=="__main__":unittest.main()
