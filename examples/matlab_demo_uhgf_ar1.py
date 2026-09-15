"""Python reproduction of the official uHGF -> uHGF-AR(1) MATLAB demo.

The inputs and native-space parameter vectors are copied from the frozen HGF
Toolbox 8.2.0 ``demo/hgf_demo.m`` workflow used by HGFX's release gate.
The two level-3 extrema below are descriptive values from the frozen MATLAB
reference and are checked with the same release tolerances used by the parity
gate.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from hgfx.models.hgf_ar1_binary import uhgf_ar1_binary
from hgfx.models.uhgf_binary import uhgf_binary


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "external" / "hgf-toolbox" / "demo" / "example_binary_input.txt"

UHGF_NATIVE_PARAMETERS = np.asarray(
    [np.nan, 0.0, 1.0, np.nan, 1.0, 1.0, np.nan, 0.0, 0.0, 1.0, 1.0, np.nan, -2.5, 3.0],
    dtype=np.float64,
)
UHGF_AR1_NATIVE_PARAMETERS = np.asarray(
    [
        np.nan,
        0.0,
        1.0,
        np.nan,
        1.0,
        1.0,
        np.nan,
        0.0,
        0.3,
        np.nan,
        0.0,
        1.0,
        np.nan,
        0.0,
        0.0,
        1.0,
        1.0,
        np.nan,
        -2.5,
        3.0,
    ],
    dtype=np.float64,
)

MATLAB_UHGF_LEVEL3_MAX_ABS_MU = np.float64(16.99162398501939)
MATLAB_UHGF_AR1_LEVEL3_MAX_ABS_MU = np.float64(4.0927117005012175)
RTOL = 5e-11
ATOL = 5e-13


def load_official_input(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(
            f"Official demo input not found at {path}. From a source checkout run "
            "`git submodule update --init --recursive`, or pass --input PATH."
        )
    return np.asarray(np.loadtxt(path), dtype=np.float64)


def _level3_max_abs_mu(trajectory: dict[str, np.ndarray]) -> float:
    mu = np.asarray(trajectory["mu"], dtype=np.float64)
    if mu.ndim != 2 or mu.shape[1] < 3:
        raise RuntimeError("Expected a trajectory with at least three HGF levels.")
    return float(np.nanmax(np.abs(mu[:, 2])))


def run_demo(inputs: np.ndarray) -> dict[str, float | int]:
    uhgf_trajectory, _ = uhgf_binary(
        inputs,
        UHGF_NATIVE_PARAMETERS,
        transformed=False,
    )
    ar1_trajectory, _ = uhgf_ar1_binary(
        inputs,
        UHGF_AR1_NATIVE_PARAMETERS,
        transformed=False,
    )

    uhgf_level3 = _level3_max_abs_mu(uhgf_trajectory)
    ar1_level3 = _level3_max_abs_mu(ar1_trajectory)

    if not np.isclose(
        uhgf_level3,
        MATLAB_UHGF_LEVEL3_MAX_ABS_MU,
        rtol=RTOL,
        atol=ATOL,
    ):
        raise RuntimeError(
            "uHGF level-3 excursion no longer matches the frozen MATLAB demo reference."
        )
    if not np.isclose(
        ar1_level3,
        MATLAB_UHGF_AR1_LEVEL3_MAX_ABS_MU,
        rtol=RTOL,
        atol=ATOL,
    ):
        raise RuntimeError(
            "uHGF-AR(1) level-3 excursion no longer matches the frozen MATLAB demo reference."
        )

    return {
        "trials": int(np.asarray(inputs).shape[0]),
        "uhgf_level3_max_abs_mu": uhgf_level3,
        "uhgf_ar1_level3_max_abs_mu": ar1_level3,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce the frozen MATLAB uHGF -> uHGF-AR(1) demo in Python."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to HGF Toolbox demo/example_binary_input.txt",
    )
    args = parser.parse_args()

    result = run_demo(load_official_input(args.input))
    print("HGFX official MATLAB demo reproduction: uHGF -> uHGF-AR(1)")
    print(f"trials={result['trials']}")
    print(f"uhgf_level3_max_abs_mu={result['uhgf_level3_max_abs_mu']:.17g}")
    print(f"uhgf_ar1_level3_max_abs_mu={result['uhgf_ar1_level3_max_abs_mu']:.17g}")
    print("status=PASS_FROZEN_MATLAB_REFERENCE_VALUES")


if __name__ == "__main__":
    main()
