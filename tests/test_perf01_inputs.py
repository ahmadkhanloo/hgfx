"""Unit tests for the prospective PERF-01 input generator; no HGFX inference."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "benchmarks/runtime_v1/generate_inputs.py"
spec = importlib.util.spec_from_file_location("perf01_inputs", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestPerf01Inputs(unittest.TestCase):
    def test_registry_and_arrays(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = module.produce(root)
            self.assertEqual(len(manifest["cases"]), 28)
            self.assertEqual([sum(c["tier"] == tier for c in manifest["cases"]) for tier in ("primary", "secondary", "throughput", "robustness")], [9, 12, 6, 1])
            self.assertEqual(len(set(c["id"] for c in manifest["cases"])), 28)
            for horizon in (128, 512, 1024):
                data = json.loads((root / "inputs" / f"binary_{horizon}_s64.json").read_text())
                self.assertEqual(data["subject_count"], 64)
                self.assertEqual(len(data["u"]), 64)
                self.assertEqual(len(data["u"][0]), horizon)
                self.assertEqual(len(data["y"][0]), horizon)
                self.assertEqual(set(data["u"][0]), {0, 1})
                self.assertEqual(set(data["y"][0]), {0, 1})
            module.produce(root, check=True)

    def test_reproducible_and_tamper_detected(self):
        with tempfile.TemporaryDirectory() as temp1, tempfile.TemporaryDirectory() as temp2:
            a, b = Path(temp1), Path(temp2)
            module.produce(a)
            module.produce(b)
            self.assertEqual((a / "inputs_manifest.json").read_bytes(), (b / "inputs_manifest.json").read_bytes())
            fixture = a / "inputs" / "binary_128_s64.json"
            fixture.write_bytes(fixture.read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "noncanonical"):
                module.produce(a, check=True)
            with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
                module.produce(a, check=False)


if __name__ == "__main__":
    unittest.main()
