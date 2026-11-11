"""Read-only official-seed original Ridders/Armijo/ULP audit synthetic contracts."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import numpy as np

from tools.compstat_rev22_official_ridders_archive_audit import (
    REF, OLD_DEV_HEAD, WHEEL, INPUT_SHA, RESPONSE_SHA,
    SRC, binary64_sha, get_source, number_array,
)


class TestOfficialRiddersArchive(unittest.TestCase):
    def test_five_original_frozen_authentic_archive_identifiers(self):
        self.assertEqual(set(SRC), {"endpoint","ridders","transition","sensitivity","new_A"})
        self.assertEqual({k:len(v["sha"]) for k,v in SRC.items()},
                         {k:64 for k in SRC})
        self.assertEqual(len({v["artifact"] for v in SRC.values()}),5)
        self.assertEqual(SRC["ridders"]["artifact"],10345886333)
        self.assertEqual(SRC["transition"]["artifact"],10345846351)
        self.assertEqual(SRC["sensitivity"]["artifact"],10346050821)

    def test_same_original_fixed_seeds_reference_source_versions(self):
        self.assertEqual(REF,"2437f4dc241541072722a2695ddeca7b44d83dd3")
        self.assertEqual(OLD_DEV_HEAD,"d360fcd45c996c21ab482d1cd6b45dea6d65574f")
        self.assertEqual(WHEEL,"5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90")
        self.assertNotEqual(OLD_DEV_HEAD,
                            "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27")

    def test_exact_binary64_column_major_transport(self):
        obj={"hgfx_numeric":"ieee-strings-v1","shape":[2,3],
             "data":[1,2,3,"NaN","Infinity","-Infinity"]}
        m=number_array(obj)
        self.assertEqual(m.shape,(2,3))
        self.assertEqual(m[1,0],2)
        self.assertTrue(np.isnan(m[1,1]))
        self.assertTrue(np.isposinf(m[0,2]))
        self.assertTrue(np.isneginf(m[1,2]))

    def test_no_silent_gates_or_clipping_seed(self):
        self.assertEqual(len(INPUT_SHA),64)
        self.assertEqual(len(RESPONSE_SHA),64)
        p=Path(__file__).resolve().parents[2]/"tools/compstat_rev22_official_ridders_archive_audit.py"
        source=p.read_text()
        self.assertIn("NO_RIDDERS_DIVERGENCE",source)
        self.assertIn("NO_TRANSITION_DIVERGENCE",source)
        self.assertIn("NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED",source)
        self.assertIn("NOT_GLOBAL_PASS",source)
        self.assertIn("UNRESOLVED_DISCREPANCY",source)
        self.assertIn("NOT_OBSERVED",source)

    def test_bad_ZIP_rejected_before_archive_json_interpretation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"not_original.zip"
            path.write_bytes(b"not a real archived D08 result")
            with self.assertRaisesRegex(ValueError,"archive SHA drift"):
                get_source(path,"ridders")

    def test_tampered_member_rejected_before_data_use(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"synthetic.zip"
            original={"case":"synthetic official", "seed":123456789}
            blob=json.dumps(original).encode()
            with ZipFile(p,"w") as z:z.writestr("source.json",blob)
            good={"sha":sha256(p.read_bytes()).hexdigest(),
                  "reference":("source.json",sha256(blob).hexdigest()),
                  "artifact":-1,"run":-1}
            with patch.dict(SRC,{"synthetic":good}):
                self.assertEqual(get_source(p,"synthetic")["source.json"],original)
            bad={**good,"reference":("source.json","0"*64)}
            with patch.dict(SRC,{"synthetic":bad}):
                with self.assertRaisesRegex(ValueError,"SHA drift"):
                    get_source(p,"synthetic")

    def test_no_runtime_or_scientific_model_imports(self):
        source=(Path(__file__).resolve().parents[2]/
                "tools/compstat_rev22_official_ridders_archive_audit.py").read_text()
        self.assertNotIn("import hgfx",source)
        self.assertNotIn("import jax",source)
        self.assertNotIn("fitModel(",source)
        self.assertNotIn("simModel(",source)
        self.assertNotIn("ridders_gradient(",source)
        self.assertNotIn("quasinewton_optim(",source)


if __name__=="__main__":
    unittest.main()
