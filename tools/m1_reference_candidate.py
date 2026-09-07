from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from hgfx.golden import load_fixture


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute the independent Python candidate for the M1 tapas_logit fixture."
    )
    parser.add_argument("fixture_dir", type=Path)
    parser.add_argument("output_npz", type=Path)
    args = parser.parse_args()

    fixture = load_fixture(args.fixture_dir)
    x = np.asarray(fixture.inputs["x"], dtype=np.float64)
    a = float(fixture.config["a"])
    y = np.log(x / (a - x))
    args.output_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output_npz, y=y)
    print(f"candidate={args.output_npz}")


if __name__ == "__main__":
    main()
