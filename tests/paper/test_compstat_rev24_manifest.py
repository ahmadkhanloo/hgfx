"""REV-2.4 deterministic input-grid/identity tests; no HGFX model or MATLAB run."""
from __future__ import annotations

import copy
import hashlib
import tempfile
from pathlib import Path
from zipfile import ZipFile
import unittest

import numpy as np

from tools.compstat_rev24_manifest import (
    BASE_SEED, MODELS, NUMPY_VERSION, PROTOCOL, REPLICATES,
    binary_data, build_manifest, f64_hash, validate_manifest,
    verify_installed_wheel_files, verify_wheel_against_tag_sources,
)


def small_fake_configs():
    # This is a fake schema for testing manifest arithmetic ONLY; the actual
    # scientific manifest requires real installed v1.0.0 configs and a real
    # original wheel. Fake priors must NEVER become empirical/scientific input.
    return {
        name: (
            np.asarray([0.0, 2.0, -3.0, 1.0], dtype=np.float64),
            np.asarray([1.0, 0.0, np.nan, 4.0], dtype=np.float64),
        )
        for name in MODELS
    }


class Rev24ManifestContractTests(unittest.TestCase):
    def build(self):
        return build_manifest(small_fake_configs(), "a" * 64, NUMPY_VERSION)

    def test_case_grid_is_exactly_600_without_selection(self):
        m = self.build()
        self.assertEqual(m["protocol"], PROTOCOL)
        self.assertEqual([len(group["rows"]) for group in m["strata"]],
                         [REPLICATES] * 3)
        self.assertEqual([g["seed"] for g in m["strata"]],
                         [BASE_SEED, BASE_SEED + 1, BASE_SEED + 2])
        self.assertEqual([g["model"] for g in m["strata"]], list(MODELS))
        validate_manifest(m)

    def test_deterministic_reproduction(self):
        one, two = self.build(), self.build()
        self.assertEqual(one, two)
        self.assertEqual(one["manifest_sha256"], two["manifest_sha256"])

    def test_fixed_and_undefined_prior_slots_never_move(self):
        m = self.build()
        for group in m["strata"]:
            self.assertEqual(group["free_indices_zero_based"], [0, 3])
            for row in group["rows"]:
                self.assertEqual(row["full_transformed"][1], 2.0)
                self.assertEqual(row["full_transformed"][2], -3.0)

    def test_binary64_data_exact_sha(self):
        u, y = binary_data()
        self.assertEqual(u.shape, (128,))
        self.assertEqual(y.shape, (128,))
        self.assertEqual(f64_hash(u),
                         hashlib.sha256(u.astype("<f8").tobytes()).hexdigest())
        self.assertTrue(set(u) <= {0.0, 1.0})
        self.assertTrue(set(y) <= {0.0, 1.0})

    def test_tampered_case_is_rejected(self):
        m = self.build()
        m["strata"][0]["rows"][4]["full_transformed"][1] = 2.5
        with self.assertRaises(ValueError):
            validate_manifest(m)

    def test_undefined_nan_placeholders_are_preserved_without_resampling(self):
        configs = small_fake_configs()
        for model in MODELS:
            means, variances = configs[model]
            means[2] = float("nan")
            variances[2] = float("nan")
        manifest = build_manifest(configs, "a" * 64, NUMPY_VERSION)
        validate_manifest(manifest)
        for group in manifest["strata"]:
            self.assertEqual(len(group["rows"]), REPLICATES)
            self.assertEqual(group["prior_means_full"][2], "NaN")
            self.assertEqual(group["prior_variances_full_ieee"][2], "NaN")
            for row in group["rows"]:
                self.assertEqual(row["full_transformed"][2], "NaN")
                self.assertEqual(row["replicate_zero_based"], int(row["case_id"].split("-")[-1]))

    def test_infinite_parameter_placeholder_is_not_silently_accepted(self):
        configs = small_fake_configs()
        configs[MODELS[0]][0][2] = float("inf")
        with self.assertRaisesRegex(ValueError, "Infinite resolved prior mean"):
            build_manifest(configs, "a" * 64, NUMPY_VERSION)

    def test_installed_release_matches_wheel_and_tamper_fails(self):
        class DummyDist:
            def __init__(self, base):
                self.base = base

            def locate_file(self, name):
                return self.base / name

        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            wheel = base / "hgfx-1.0.0-py3-none-any.whl"
            module = base / "hgfx" / "models" / "example.py"
            module.parent.mkdir(parents=True, exist_ok=True)
            module.write_bytes(b"print('original')")
            with ZipFile(wheel, "w") as z:
                z.writestr("hgfx/models/example.py", module.read_bytes())
            self.assertEqual(verify_installed_wheel_files(wheel, DummyDist(base)), 1)
            module.write_bytes(b"print('modified')")
            with self.assertRaisesRegex(ValueError, "differs"):
                verify_installed_wheel_files(wheel, DummyDist(base))

    def test_config_fingerprint_rejects_prior_drift(self):
        manifest = self.build()
        self.assertEqual(len(manifest["strata"][0]["config_sha256"]), 64)
        manifest["strata"][0]["prior_means_full"][1] = 999.0
        with self.assertRaisesRegex(ValueError, "config fingerprint"):
            validate_manifest(manifest)

    def test_tagged_release_source_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            wheel = base / "hgfx-1.0.0-py3-none-any.whl"
            frozen_tag = base / "v1"
            module = frozen_tag / "src" / "hgfx" / "models" / "example.py"
            module.parent.mkdir(parents=True, exist_ok=True)
            module.write_bytes(b"original module from frozen tag")
            with ZipFile(wheel, "w") as archive:
                archive.writestr("hgfx/models/example.py", module.read_bytes())
            self.assertEqual(verify_wheel_against_tag_sources(wheel, frozen_tag), 1)
            module.write_bytes(b"unexpected change in published wheel or tag")
            with self.assertRaisesRegex(ValueError, "source differs"):
                verify_wheel_against_tag_sources(wheel, frozen_tag)

    def test_wrong_rng_version_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Requires exact NumPy"):
            build_manifest(small_fake_configs(), "a" * 64, "2.3.5")

    def test_missing_case_is_rejected(self):
        m = self.build()
        m["strata"][2]["rows"].pop()
        with self.assertRaisesRegex(ValueError, "denominator"):
            validate_manifest(m)


if __name__ == "__main__":
    unittest.main()
