from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.fitting import fit_hgf_binary_unitsq_compat, hgf_binary_unitsq_fit_problem
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions, quasinewton_optim

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
RTOL = 2e-8
ATOL = 2e-10


def normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(normalize(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any, *, rtol=RTOL, atol=ATOL) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        # MATLAB JSON serializes singleton vectors as scalars.
        if a.size == e.size:
            a = a.reshape(-1)
            e = e.reshape(-1)
        else:
            raise AssertionError(f"{label} shape mismatch: Python={a.shape}, MATLAB={e.shape}")

    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return
    bad = np.argwhere(~close)
    index = tuple(int(i) for i in bad[0]) if bad.size else ()
    av = float(a[index]) if index else float(a)
    ev = float(e[index]) if index else float(e)
    raise AssertionError(
        f"{label} divergence index={index}: MATLAB={ev:.17g}, "
        f"Python={av:.17g}, abs={abs(av-ev):.3e}"
    )


def options_from_payload(data: dict[str, Any]) -> QuasiNewtonOptions:
    return QuasiNewtonOptions(
        tol_grad=float(data["tolGrad"]),
        tol_arg=float(data["tolArg"]),
        max_step=float(data["maxStep"]),
        max_iter=int(data["maxIter"]),
        max_regu=int(data["maxRegu"]),
        max_rst=int(data["maxRst"]),
        opt_iter=bool(data["optIter"]),
    )


def check_quadratic(payload: dict[str, Any], options: QuasiNewtonOptions) -> None:
    q = payload["quadratic"]

    def objective(x: np.ndarray) -> float:
        return float(
            (x[0] - 0.75) ** 2
            + 2.0 * (x[1] + 1.25) ** 2
            + 0.15 * x[0] * x[1]
        )

    result = quasinewton_optim(objective, arr(q["init"]), options)
    check("quadratic.arg_min", result.arg_min, q["arg_min"])
    check("quadratic.val_min", result.val_min, q["val_min"])
    check(
        "quadratic.inverse_hessian",
        result.inverse_hessian,
        q["inverse_hessian"],
        rtol=8e-8,
        atol=5e-10,
    )


def check_fit(payload: dict[str, Any], options: QuasiNewtonOptions) -> None:
    f = payload["fit"]
    responses = arr(f["responses"])
    inputs = arr(f["inputs"])

    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    check(
        "fit.free_indices",
        np.asarray(problem.free_indices, dtype=np.float64) + 1,
        f["free_matlab_indices"],
        rtol=0,
        atol=0,
    )
    check("fit.initial_full", problem.initial_full, f["initial_full"], rtol=0, atol=0)
    check("fit.initial_free", problem.initial_free, f["initial_free"], rtol=0, atol=0)

    initial = problem.evaluate_full(problem.initial_full)
    check("fit.initial_neg_log_joint", initial.neg_log_joint, f["initial_neg_log_joint"])
    check(
        "fit.initial_neg_log_likelihood",
        initial.neg_log_likelihood,
        f["initial_neg_log_likelihood"],
    )

    result = fit_hgf_binary_unitsq_compat(responses, inputs, options=options)

    check("fit.arg_min", result.optimizer.arg_min, f["arg_min"])
    check("fit.val_min", result.optimizer.val_min, f["val_min"])
    check(
        "fit.inverse_hessian",
        result.optimizer.inverse_hessian,
        f["inverse_hessian"],
        rtol=2e-6,
        atol=2e-8,
    )
    check("fit.final_full", result.final_full, f["final_full"])
    check(
        "fit.perceptual_transformed",
        result.perceptual_transformed,
        f["perceptual_transformed"],
    )
    check(
        "fit.observation_transformed",
        result.observation_transformed,
        f["observation_transformed"],
    )
    check("fit.perceptual_native", result.perceptual_native, f["perceptual_native"])
    check("fit.observation_native", result.observation_native, f["observation_native"])
    check("fit.neg_log_joint", result.objective.neg_log_joint, f["neg_log_joint"])
    check(
        "fit.neg_log_likelihood",
        result.objective.neg_log_likelihood,
        f["neg_log_likelihood"],
    )
    if int(f["rval"]) != result.objective.rval:
        raise AssertionError(
            f"fit.rval mismatch: Python={result.objective.rval}, MATLAB={f['rval']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    metadata = payload["metadata"]
    if metadata["reference_version"] != "8.2.0":
        raise AssertionError(f"unexpected HGF version: {metadata['reference_version']}")
    if metadata["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError(f"unexpected HGF commit: {metadata['reference_commit']}")
    if metadata["schema_version"] != "m9-1":
        raise AssertionError(f"unexpected fixture schema: {metadata['schema_version']}")

    config = payload["optimizer_config"]
    if int(config["nRandInit"]) != 0:
        raise AssertionError("M9 deterministic gate requires frozen nRandInit=0")
    options = options_from_payload(config)

    check_quadratic(payload, options)
    check_fit(payload, options)
    print("M9 MATLAB/Python compatibility fitting parity: PASS")


if __name__ == "__main__":
    main()
