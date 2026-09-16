import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec = importlib.util.spec_from_file_location("d04", Path("tools/check_m18_demo_uhgf_ar1.py"))
d04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d04)


def test_tagged_nonfinite_values_are_distinct():
    values = d04._array(["NaN", "Infinity", "-Infinity", 1.0])
    assert np.isnan(values[0])
    assert np.isposinf(values[1])
    assert np.isneginf(values[2])
    assert values[3] == 1
    assert d04._first_mismatch("wt", [np.inf], ["NaN"]) is not None
    assert d04._first_mismatch("wt", [np.inf], ["Infinity"]) is None


def test_lossy_null_is_rejected():
    with pytest.raises(ValueError, match="null"):
        d04._array([1, None])


def test_matlab_column_major_shape_is_preserved():
    encoded = {
        "hgfx_numeric": "ieee-strings-v1",
        "shape": [2, 2],
        "data": [1, "Infinity", "NaN", "-Infinity"],
    }
    actual = np.array([[1, np.nan], [np.inf, -np.inf]])
    np.testing.assert_array_equal(d04._array(encoded), actual)
