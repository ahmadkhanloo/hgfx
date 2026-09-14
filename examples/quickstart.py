from __future__ import annotations

import numpy as np

import hgfx


def main() -> None:
    """Run a minimal MATLAB-equivalent HGF fit using only the public HGFX API."""
    inputs = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    responses = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )

    result = hgfx.fit_model(responses, inputs)

    print(f"kind={result.kind}")
    print(f"trials={result.traj.mu.shape[0]}")
    print(f"LME={float(result.optim.LME):.6f}")
    print(f"BIC={float(result.optim.BIC):.6f}")


if __name__ == "__main__":
    main()
