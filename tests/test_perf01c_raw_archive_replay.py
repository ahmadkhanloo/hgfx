"""Unit tests for independent raw archive byte integrity and fieldwise arithmetic."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1] / "benchmarks" / "runtime_v1"
sys.path.insert(0, str(ROOT))

from verify_perf01c_raw_archives import (  # noqa: E402
    independent_trajectory_failures, read_original_members,
)


class OriginalArchiveAudit(unittest.TestCase):
    def artifact_example(self, base: Path):
        blobs = {"a.json": b'{"a": 1}', "b.json": b'{"b": 2}'}
        zip_path = base / "source.zip"
        with zipfile.ZipFile(zip_path, "w") as z:
            for name, data in blobs.items():
                z.writestr(name, data)
        frozen = {
            "sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
            "members": {
                n: hashlib.sha256(d).hexdigest() for n, d in blobs.items()
            },
        }
        return zip_path, frozen

    def test_exact_original_zip_and_member_hashes(self):
        with TemporaryDirectory() as d:
            archive, expected = self.artifact_example(Path(d))
            contents, mode = read_original_members(archive, expected)
            self.assertEqual(mode, "EXACT_ZIP_AND_MEMBER_SHA256")
            self.assertEqual(contents, {"a.json": {"a": 1}, "b.json": {"b": 2}})

    def test_gh_extracted_members_have_no_unearned_zip_claim(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            archive, expected = self.artifact_example(root)
            folder = root / "extracted"
            folder.mkdir()
            with zipfile.ZipFile(archive) as z:
                z.extractall(folder)
            result, mode = read_original_members(folder, expected)
            self.assertEqual(mode, "EXTRACTED_MEMBERS_SHA256_ONLY_NO_ZIP_CLAIM")
            self.assertEqual(result["a.json"], {"a": 1})

    def test_reject_modified_original_zip_even_if_json_semantics_unchanged(self):
        with TemporaryDirectory() as d:
            archive, expected = self.artifact_example(Path(d))
            with zipfile.ZipFile(archive, "a") as z:
                z.comment = b"post-hoc archive byte mutation"
            with self.assertRaisesRegex(ValueError, "ZIP SHA256 mismatch"):
                read_original_members(archive, expected)

    def test_reject_changed_raw_member_even_if_archive_hash_patched(self):
        with TemporaryDirectory() as d:
            archive, expected = self.artifact_example(Path(d))
            with zipfile.ZipFile(archive, "a") as z:
                z.writestr("a.json", b'{"a": 9}')
            expected["sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "duplicate or extra ZIP member"):
                read_original_members(archive, expected)

    def test_reject_changed_extracted_member(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            archive, expected = self.artifact_example(root)
            folder = root / "extracted"
            folder.mkdir()
            with zipfile.ZipFile(archive) as z:
                z.extractall(folder)
            (folder / "b.json").write_bytes(b'{"b": 999}')
            with self.assertRaisesRegex(ValueError, "member SHA256 mismatch"):
                read_original_members(folder, expected)

    def test_original_trajectory_tolerance_is_frozen_not_bitwise(self):
        left = {"traj": {"mu": [[1.0, 0.0, 1.0] for _ in range(128)]}}
        right = {"traj": {"mu": [[1.0, 0.0, 1.0] for _ in range(128)]}}
        left["traj"]["mu"][1][1] = 2.9e-10
        result = independent_trajectory_failures(left, right, "mu")
        self.assertEqual(result["mismatch_count"], 0)
        left["traj"]["mu"][1][1] = 3.1e-10
        result = independent_trajectory_failures(left, right, "mu")
        self.assertEqual(result["mismatch_indices_zero_based"], [[1, 1]])
        self.assertEqual(result["atol"], 3e-10)
        self.assertEqual(result["rtol"], 3e-8)

    def test_reject_incomplete_and_nonfinite_scientific_arrays(self):
        left = {"traj": {"mu": [[1.0, 0.0, 1.0] for _ in range(128)]}}
        right = {"traj": {"mu": [[1.0, 0.0, 1.0] for _ in range(128)]}}
        left["traj"]["mu"] = left["traj"]["mu"][:-1]
        with self.assertRaisesRegex(ValueError, "128-trial"):
            independent_trajectory_failures(left, right, "mu")
        left["traj"]["mu"] = [[1.0, 0.0, 1.0] for _ in range(128)]
        left["traj"]["mu"][0][1] = float("nan")
        with self.assertRaisesRegex(ValueError, "Non-finite"):
            independent_trajectory_failures(left, right, "mu")


if __name__ == "__main__":
    unittest.main()
