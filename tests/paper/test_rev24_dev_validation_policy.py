"""REV-2.4 B08 proposed maintenance validation: SOURCE-ONLY, NO SCIENCE.

Read-only tests for the immutable v1.0.0 reference, the exact development
single-line eHGF patch and the absence of an approved scientific trigger.
They MUST NOT import HGFX or run the MATLAB numerical model.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"evidence/revision/protocols/REV-2.4_EHGF019_DEVELOPMENT_VALIDATION_CONTRACT.json"
SOURCE=ROOT/"src/hgfx/updates/volatility.py"
MATLAB=ROOT/"external/hgf-toolbox/building_blocks/hgf_volatility_update.m"


def git(*args):
    return subprocess.check_output(
        ["git",*args],cwd=ROOT,text=True,stderr=subprocess.PIPE
    ).strip()


class ProposedDevScientificValidationContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_unapproved_human_and_author_gate_is_fail_closed(self):
        c=self.c
        self.assertEqual(c["status"],"PROPOSED_NOT_REVIEWED_NOT_AUTHORIZED")
        approval=c["review_requirement"]
        self.assertIs(approval["human_review_accepted"],False)
        self.assertIs(approval["author_execution_approval"],False)
        self.assertIs(approval["automatic_scientific_trigger_allowed"],False)
        self.assertEqual(c["outcome_policy"]["d2_d3"],"BLOCKED")
        self.assertEqual(c["outcome_policy"]["current_scientific_gate"],
                         "NOT_GLOBAL_PASS")
        self.assertEqual(c["outcome_policy"]["current_full_cpu_gate"],"NOT_PASS")

    def test_original_source_identity_not_development_replacement(self):
        x=self.c["source"]
        self.assertEqual(x["original_hgfx_release_commit"],
                         "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27")
        self.assertEqual(x["original_toolbox_commit"],
                         "2437f4dc241541072722a2695ddeca7b44d83dd3")
        self.assertEqual(x["original_hgfx_release_volatility_blob"],
                         "afdbdcb5b4ae15926a7526cc604f6ca8f6fe7a76")
        self.assertNotEqual(x["original_hgfx_release_volatility_blob"],
                            x["developer_source_blob"])
        released=git("show",x["original_hgfx_release_commit"]+
                     ":"+x["developer_source_path"])
        self.assertIn("pi = pihat + np.maximum(np.float64(0.0), correction)",released)
        self.assertNotIn("pi = pihat + np.fmax(np.float64(0.0), correction)",released)
        self.assertEqual(git("rev-parse","v1.0.0^{commit}"),
                         x["original_hgfx_release_commit"])

    def test_development_source_blob_and_one_operation_scoped(self):
        x=self.c["source"]
        self.assertEqual(git("hash-object",str(SOURCE)),
                         x["developer_source_blob"])
        live=SOURCE.read_text(encoding="utf-8")
        self.assertIn("if update_type == \"ehgf\":",live)
        self.assertIn("pi = pihat + np.fmax(np.float64(0.0), correction)",live)
        self.assertNotIn("pi = pihat + np.maximum(np.float64(0.0), correction)",live)
        diff_files=git("diff","--name-only",x["developer_patch_parent"],
                       x["developer_patch_commit"]).splitlines()
        self.assertEqual(diff_files,[x["developer_source_path"]])
        patch=git("diff","--unified=0",x["developer_patch_parent"],
                  x["developer_patch_commit"],"--",x["developer_source_path"])
        self.assertIn("-            pi = pihat + np.maximum(np.float64(0.0), correction)",patch)
        self.assertIn("+            pi = pihat + np.fmax(np.float64(0.0), correction)",patch)
        self.assertNotIn("if update_type == \"uhgf\"\n+",patch)

    def test_exact_frozen_original_matlab_source_present(self):
        x=self.c["source"]
        self.assertEqual(git("-C","external/hgf-toolbox","rev-parse","HEAD"),
                         x["original_toolbox_commit"])
        self.assertTrue(MATLAB.is_file())
        source=MATLAB.read_text(encoding="utf-8")
        self.assertIn("pihat_j + max(0, 1/2 * ka_jm1^2 * ww * (ww + rr * dd))",
                      source)
        self.assertIn("elseif strcmp(update_type, 'ehgf')",source)
        self.assertEqual(git("hash-object",str(MATLAB)),
                         x["original_toolbox_source_blob"])

    def test_exact_case_locked_no_fitting_or_other_grid_runs(self):
        t=self.c["experiment"]
        self.assertEqual(t["allowed_case_ids"],["REV24-G-ehgf_binary-019"])
        self.assertEqual(t["case_sha256"],
                         "276d21f43a91fc8748438aafc6ec44f759f23dc2ae97dae8b4cc1274aba3fefb")
        self.assertEqual(t["original_600_grid_artifact_id"],13743694091)
        self.assertEqual(t["trial_count"],128)
        self.assertEqual(t["transformed_parameter_count"],15)
        self.assertEqual(t["free_indices_zero_based"],[12,13,14])
        self.assertEqual((t["model"],t["observation"]),
                         ("ehgf_binary","unitsq_sgm"))
        self.assertIs(t["no_fit"],True)
        self.assertIs(t["no_new_seeds_or_inputs"],True)
        self.assertEqual(t["reference_matlab_version"],
                         "26.2.0.3433840 (R2026b) Update 1")

    def test_bounded_status_only_never_predeclared_ehgf_objective_parity(self):
        p=self.c["outcome_policy"]
        self.assertEqual(p["objective_family_gate"],
                         "NO_PREDECLARED_EHGF_OBJECTIVE_GATE")
        self.assertEqual(p["nonnumeric_validity_exclusions"],0)
        self.assertEqual(set(p["allowed_limited_outcomes"]),{
            "TARGETED_ONE_CASE_STATUS_MATCH","TARGETED_ONE_CASE_STATUS_MISMATCH",
            "EXECUTION_BLOCKED"})
        for key in ("fit_parity_claim_allowed","global_parity_claim_allowed",
                    "original_release_reclassification_allowed",
                    "original_panel_g_or_e_replay_allowed"):
            self.assertIs(p[key],False,key)

    def test_every_supporting_document_exists(self):
        for file in self.c["documentation"].values():
            self.assertTrue((ROOT/file).is_file(),file)
        human=self.c["review_requirement"]["human_domain_expert_report"]
        self.assertTrue(human.startswith("docs/research/reviews/"))
        self.assertNotEqual(human,
                            "docs/research/reviews/REV24_INDEPENDENT_REVIEW_2026-11-10.md")


if __name__=="__main__":
    unittest.main()
