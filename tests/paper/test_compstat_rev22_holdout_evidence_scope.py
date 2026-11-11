"""Synthetic read-only REV-2.2 D08 holdout-vs-official evidence scope tests."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from tools.compstat_rev22_holdout_evidence_scope import (
    REF, SOURCES, read_source, require,
)


class TestRev22HoldoutEvidenceScope(unittest.TestCase):
    def test_four_distinct_authentic_original_artifact_provenance(self):
        self.assertEqual(set(SOURCES), {"official", "optimizer", "likelihood", "sensitivity"})
        self.assertEqual([SOURCES[x]["seed"] for x in SOURCES],
                         [123456789, 314159265, 314159265, 314159265])
        self.assertEqual(len({x["id"] for x in SOURCES.values()}), 4)
        self.assertEqual(len({x["zip"] for x in SOURCES.values()}), 4)
        for value in SOURCES.values():
            self.assertEqual(len(value["zip"]), 64)
            self.assertEqual(len(value["source"][1]), 64)
            self.assertEqual(len(value["comparison"][1]), 64)

    def test_frozen_toolbox_reference_cannot_drift(self):
        self.assertEqual(REF, "2437f4dc241541072722a2695ddeca7b44d83dd3")

    def test_archive_sha_mismatch_rejected_before_json_read(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "not_an_original_archive.zip"
            path.write_bytes(b"untrusted bytestream")
            with self.assertRaisesRegex(ValueError, "ZIP SHA changed"):
                read_source(path, "official")

    def test_source_member_hash_and_seed_scope_are_checked(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "synthetic.zip"
            src = {
                "protocol": "synthetic-original-probe",
                "seed": 123456789,
                "reference_commit": REF,
                "inputs": [0.0] * 614,
                "responses": [0.5] * 614,
            }
            cmp = {"protocol": "synthetic-original-probe",
                   "reference_commit": REF}
            contents = {"source.json": json.dumps(src).encode(),
                        "comparison.json": json.dumps(cmp).encode()}
            with ZipFile(path, "w") as z:
                for n, val in contents.items():
                    z.writestr(n, val)
            spec = {
                "id": 999, "seed": 123456789, "protocol": "synthetic-original-probe",
                "zip": sha256(path.read_bytes()).hexdigest(),
                "source": ("source.json", sha256(contents["source.json"]).hexdigest()),
                "comparison": ("comparison.json", sha256(contents["comparison.json"]).hexdigest()),
            }
            with patch.dict(SOURCES, {"synthetic": spec}):
                raw, comparison = read_source(path, "synthetic")
                self.assertEqual(raw["seed"], 123456789)
                self.assertEqual(comparison["protocol"], "synthetic-original-probe")
            changed = dict(spec, seed=314159265)
            with patch.dict(SOURCES, {"synthetic": changed}):
                with self.assertRaisesRegex(ValueError, "seed mismatch"):
                    read_source(path, "synthetic")
            bad_blob = dict(spec, source=("source.json", "0" * 64))
            with patch.dict(SOURCES, {"synthetic": bad_blob}):
                with self.assertRaisesRegex(ValueError, "member SHA changed"):
                    read_source(path, "synthetic")

    def test_source_protocol_rejects_unknown_source(self):
        with self.assertRaises(ValueError):
            require(False, "Expected controlled error")

    def test_no_hgfx_matlab_jax_or_optimizer_execution_imports(self):
        path = Path(__file__).resolve().parents[2] / "tools/compstat_rev22_holdout_evidence_scope.py"
        content = path.read_text(encoding="utf8")
        self.assertNotIn("import hgfx", content)
        self.assertNotIn("import jax", content)
        self.assertNotIn("fitModel(", content)
        self.assertNotIn("simModel(", content)
        self.assertNotIn("quasinewton_optim(", content)
        self.assertIn("HOLDOUT_EVIDENCE_NOT_TRANSFERABLE_TO_OFFICIAL_SEED", content)

    def test_original_seed_is_explicitly_not_equated_to_holdout(self):
        self.assertNotEqual(SOURCES["official"]["seed"], SOURCES["optimizer"]["seed"])
        self.assertIn("new_D08_fits_allowed", (
            Path(__file__).resolve().parents[2] /
            "tools/compstat_rev22_holdout_evidence_scope.py").read_text())

    def test_no_protocol_can_claim_rev24_global_pass(self):
        content = (Path(__file__).resolve().parents[2] /
                   "tools/compstat_rev22_holdout_evidence_scope.py").read_text()
        self.assertIn('"rev24": "NOT_GLOBAL_PASS"', content)
        self.assertIn('"D2_D3": "BLOCKED"', content)
        self.assertIn('"original_holdout_fail_preserved": True', content)


if __name__ == "__main__":
    unittest.main()
