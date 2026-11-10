"""Archive-integrity contract only; no MATLAB, HGFX, or participant analysis."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from tools.compstat_rev24_endpoint_sources import (
    SOURCES, audit_archive, audit_sources,
)


class EndpointSourceContracts(unittest.TestCase):
    def make_zip(self, directory, files):
        path = Path(directory) / "original.zip"
        with ZipFile(path, "w") as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_original_source_registry_exact(self):
        self.assertEqual(tuple(SOURCES), ("d02", "d08", "cohort64"))
        self.assertEqual(SOURCES["cohort64"]["artifact_id"], 13341288055)
        self.assertEqual(SOURCES["d08"]["model"], "uhgf + gaussian_obs")
        self.assertEqual(len(SOURCES["cohort64"]["expected_files"]), 2)

    def test_good_archive_does_not_claim_endpoints(self):
        with tempfile.TemporaryDirectory() as directory:
            path, sha = self.make_zip(directory, {"reference.txt": b"frozen"})
            source = copy.deepcopy(SOURCES["d02"])
            source["zip_sha256"] = sha
            result = audit_archive(path, "d02", source)
            self.assertEqual(result["archive_identity"], "SHA256_VERIFIED")
            self.assertEqual(result["objective_cross_evaluation"], "NOT_RUN")
            self.assertEqual(result["endpoint_vector_coverage"], "NOT_EVALUATED")

    def test_bad_zip_hash_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = self.make_zip(directory, {"ref": b"source"})
            with self.assertRaisesRegex(ValueError, "archive SHA256 mismatch"):
                audit_archive(path, "d02", SOURCES["d02"])

    def test_inner_cohort_hash_and_duplicate_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            path, sha = self.make_zip(directory,
                    {"hgfx_raw.json": b"a", "matlab_raw.json": b"b"})
            source = copy.deepcopy(SOURCES["cohort64"])
            source["zip_sha256"] = sha
            source["expected_files"] = {"hgfx_raw.json": hashlib.sha256(b"a").hexdigest(),
                                        "matlab_raw.json": hashlib.sha256(b"b").hexdigest()}
            result = audit_archive(path, "cohort64", source)
            self.assertEqual(len(result["verified_inner_sha256"]), 2)
            source["expected_files"]["matlab_raw.json"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "matlab_raw.json SHA256 mismatch"):
                audit_archive(path, "cohort64", source)

    def test_all_three_sources_required(self):
        with self.assertRaisesRegex(ValueError, "all required"):
            audit_sources({"d02": Path("unused")})


if __name__ == "__main__":
    unittest.main()
