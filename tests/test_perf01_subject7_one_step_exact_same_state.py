"""Synthetic source formula tests: post-result one original BFGS state only."""
from pathlib import Path
import importlib.util
import sys
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/"benchmarks"/"runtime_v1"
sys.path.insert(0,str(ROOT))
s=importlib.util.spec_from_file_location("subject7_one_step_exact_same_state",ROOT/"subject7_one_step_exact_same_state.py")
probe=importlib.util.module_from_spec(s)
s.loader.exec_module(probe)


class FrozenSourceOneStepTests(unittest.TestCase):
    def test_source_record6_only(self):
        self.assertEqual(probe.INDEX,6)

    def test_negative_gradient_is_full_step_with_no_clipping(self):
        x=np.asarray([1.,2.,3.])
        d=probe.original_direction(x,np.eye(3),[0.1,0.2,0.3],10.)
        self.assertFalse(d["original_source_clipping_applied"])
        np.testing.assert_allclose(d["source_next_full_step_free_x"],[.9,1.8,2.7])
        self.assertLess(d["original_source_unclipped_gradient_dot_direction"],0)

    def test_source_max_step_is_one(self):
        d=probe.original_direction([0.,0.,0.],np.eye(3),[3.,4.,0.],10.)
        self.assertTrue(d["original_source_clipping_applied"])
        np.testing.assert_allclose(d["source_clipped_full_step_direction"],[-.6,-.8,0.])
        self.assertEqual(d["original_source_step_norm"],5.)

    def test_source_slope_is_unclipped(self):
        d=probe.original_direction([0.,0.,0.],np.eye(3),[3.,4.,0.],10.)
        self.assertEqual(d["original_source_unclipped_gradient_dot_direction"],-25.)
        self.assertEqual(d["original_armijo_delta_RHS_using_unclipped_slope"],-0.0025)

    def test_source_zero_gradient_denied(self):
        with self.assertRaises(ValueError):
            probe.original_direction([0.,0.,0.],np.eye(3),[0.,0.,0.],10.)

    def test_nonfinite_values_denied(self):
        with self.assertRaises(ValueError):
            probe.original_direction([0.,0.,0.],np.eye(3),[float("nan"),0.,0.],10.)

    def test_bad_shape_denied(self):
        with self.assertRaises(ValueError):
            probe.original_direction([0.,0.,0.],np.eye(2),[1.,0.,0.],10.)

    def test_one_component_gradient_perturbation_can_change_clipped_direction(self):
        x=np.asarray([1.,2.,3.])
        a=probe.original_direction(x,np.eye(3),[3.,4.,0.],10.)
        b=probe.original_direction(x,np.eye(3),[3.+1e-7,4.,0.],10.)
        self.assertGreater(np.max(np.abs(np.asarray(a["source_next_full_step_free_x"])-b["source_next_full_step_free_x"])),0)

    def test_source_next_step_is_relative_to_unchanged_exact_x(self):
        x=np.asarray([1.,2.,3.])
        a=probe.original_direction(x,np.eye(3),[.3,.4,0.],10.)
        x2=np.asarray([1.001,2.,3.])
        b=probe.original_direction(x2,np.eye(3),[.3,.4,0.],10.)
        np.testing.assert_allclose(np.asarray(b["source_next_full_step_free_x"])-a["source_next_full_step_free_x"],[.001,0.,0.])

    def test_historically_failed_source_mandatory(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                probe.analyze(Path(d),Path(d),Path(d))


if __name__=="__main__":
    unittest.main()
