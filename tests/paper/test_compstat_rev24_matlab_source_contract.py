"""Static entrypoint guard: does not replace actual MATLAB HGF execution."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "reference/matlab/run_compstat_rev24_matlab.m"


class MatlabModelDispatchContract(unittest.TestCase):
    def test_model_dispatch_uses_frozen_config_function_handle(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("perceptual = pc.prc_fun;", text)
        self.assertIn("[~, states] = perceptual(r_data, full(1:prc_length), 'trans');", text)
        self.assertNotIn("str2func([model '_unified'])", text)
        self.assertIn("r_data.c_prc = pc;", text)

    def test_family_registry_preserved(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("names = {'hgf_binary', 'ehgf_binary', 'uhgf_binary'};", text)
        self.assertIn("assert(index == 600);", text)
        self.assertIn("'NOT_ASSESSED_NO_HGFX_PAIR'", text)


if __name__ == "__main__":
    unittest.main()
