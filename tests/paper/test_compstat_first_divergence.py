"""REV-1.4 source integrity and first-exceedance tests; no scientific fit."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from tools.audit_compstat_first_divergence import archive_files, canonical_hash, mismatches


class TestRev14SourceAudit(unittest.TestCase):
    def test_case_digest_excludes_stored_identifier(self):
        d = {"kind": "parameter_recovery", "seed": 72718, "u": [0, 1]}
        expected = hashlib.sha256(b'{"kind":"parameter_recovery","seed":72718,"u":[0,1]}').hexdigest()
        self.assertEqual(canonical_hash({**d, "case_id": "any", "case_sha256": "x"},
                                        ("case_id", "case_sha256")), expected)

    def test_first_gate_failure_is_not_first_nonzero_difference(self):
        a = [[0.0, 1.0, 0.0] for _ in range(128)]
        b = [[0.0, 1.0, 0.0] for _ in range(128)]
        a[3][1] = 1.0 + 1e-12
        a[83][1] = 1.0 + 1e-6
        result = mismatches(a, b)
        self.assertEqual(result["first_nonzero_difference"]["trial_zero_based"], 3)
        self.assertEqual(result["first_outside_existing_gate"]["trial_zero_based"], 83)
        self.assertEqual(result["outside_gate_cells_zero_based"], [[83, 1]])

    def test_no_false_pass_for_nonfinite_source(self):
        a = [[0.0, 1.0, 0.0] for _ in range(128)]
        a[2][1] = float("nan")
        with self.assertRaises(ValueError):
            mismatches(a, [[0.0, 1.0, 0.0] for _ in range(128)])

    def test_wrong_zip_digest_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "orig.zip"
            with ZipFile(path, "w") as z:
                z.writestr("manifest.json", "{}")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                archive_files(path, "0" * 64)

    def test_duplicate_zip_member_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "orig.zip"
            with ZipFile(path, "w") as z:
                z.writestr("x.json", "{}")
                z.writestr("x.json", "{}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "Duplicate archive entries"):
                archive_files(path, digest)


if __name__ == "__main__":
    unittest.main()
