"""Python reproduction of the official HGF Toolbox eHGF challenge demo.

This example uses the exact 320-trial input and native-space parameter vector
from the frozen HGF Toolbox 8.2.0 ``demo/hgf_demo.m`` section used by HGFX's
release parity gate.

Expected reference behavior is intentionally asymmetric: the classic HGF
rejects this parameter region because posterior precision becomes negative,
while eHGF runs successfully. Reproducing that limitation is part of v1
MATLAB compatibility; it is not a scientific PASS for classic HGF.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import hgfx


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "external" / "hgf-toolbox" / "demo" / "example_binary_input.txt"
NATIVE_PARAMETERS = np.asarray(
    [np.nan, 0.0, 1.0, np.nan, 1.0, 1.0, np.nan, 0.0, 0.0, 1.0, 1.5, np.nan, -4.0, 3.0],
    dtype=np.float64,
)


def load_official_input(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(
            f"Official demo input not found at {path}. From a source checkout run "
            "`git submodule update --init --recursive`, or pass --input PATH."
        )
    return np.asarray(np.loadtxt(path), dtype=np.float64)


def run_demo(inputs: np.ndarray) -> dict[str, object]:
    classic_error: str | None = None
    classic_success = False
    try:
        hgfx.sim_model(inputs, "hgf_binary", NATIVE_PARAMETERS)
        classic_success = True
    except ValueError as exc:
        classic_error = str(exc)

    ehgf_result = hgfx.sim_model(inputs, "ehgf_binary", NATIVE_PARAMETERS)

    if classic_success:
        raise RuntimeError(
            "Classic HGF unexpectedly succeeded in the frozen demo failure regime."
        )
    if classic_error is None or "Negative posterior precision" not in classic_error:
        raise RuntimeError(
            "Classic HGF did not reproduce the frozen negative-posterior-precision behavior."
        )
    if ehgf_result.trajectory["mu"].shape[0] != np.asarray(inputs).shape[0]:
        raise RuntimeError("eHGF output length does not match the official demo input.")

    return {
        "trials": int(np.asarray(inputs).shape[0]),
        "hgf_binary_success": classic_success,
        "hgf_binary_error": classic_error,
        "ehgf_binary_success": True,
        "ehgf_mu_shape": tuple(int(v) for v in ehgf_result.trajectory["mu"].shape),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce the frozen MATLAB HGF demo eHGF challenge in Python."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to HGF Toolbox demo/example_binary_input.txt",
    )
    args = parser.parse_args()

    inputs = load_official_input(args.input)
    result = run_demo(inputs)

    print("HGFX official MATLAB demo reproduction: model-selection challenge")
    print(f"trials={result['trials']}")
    print(f"hgf_binary_success={result['hgf_binary_success']}")
    print(f"hgf_binary_error={result['hgf_binary_error']}")
    print(f"ehgf_binary_success={result['ehgf_binary_success']}")
    print(f"ehgf_mu_shape={result['ehgf_mu_shape']}")
    print("status=PASS_EXPECTED_REFERENCE_BEHAVIOR")


if __name__ == "__main__":
    main()
