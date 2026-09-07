from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.objective import gaussian_log_prior, hgf_binary_unitsq_objective

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
RTOL = 2e-11
ATOL = 2e-13


def _normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(_normalize(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        raise AssertionError(f"{label} shape mismatch: Python={a.shape} MATLAB={e.shape}")
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(close):
        return
    index = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = float(a[index]) if index else float(a)
    ev = float(e[index]) if index else float(e)
    raise AssertionError(
        f"{label} first divergence index={index}: MATLAB={ev:.17g}, "
        f"Python={av:.17g}, abs={abs(av-ev):.3e}"
    )


def check_prior(label: str, actual, expected: dict[str, Any]) -> None:
    matlab_indices = np.asarray(actual.indices, dtype=np.int64) + 1
    check(f"{label}.indices", matlab_indices, expected["matlab_indices"])
    check(f"{label}.terms", actual.terms, expected["terms"])
    check(f"{label}.total", actual.total, expected["total"])


def check_case(name: str, case: dict[str, Any]) -> None:
    inputs = arr(case["inputs"])
    result = hgf_binary_unitsq_objective(
        arr(case["responses"]),
        inputs,
        arr(case["ptrans_prc"]),
        arr(case["ptrans_obs"]),
    )
    if result.rval != 0:
        raise AssertionError(f"{name}: Python objective returned rval={result.rval}")

    input_column = inputs if inputs.ndim == 1 else inputs[:, 0]
    check(
        f"{name}.ignored_indices",
        np.flatnonzero(np.isnan(input_column)) + 1,
        case["ignored_matlab_indices"],
    )
    check(
        f"{name}.irregular_indices",
        np.flatnonzero(result.irregular_mask) + 1,
        case["irregular_matlab_indices"],
    )
    check(
        f"{name}.trial_log_likelihoods",
        result.trial_log_likelihoods,
        case["trial_log_likelihoods"],
    )
    check(
        f"{name}.regular_trial_log_likelihoods",
        result.regular_trial_log_likelihoods,
        case["regular_trial_log_likelihoods"],
    )
    check(f"{name}.log_likelihood", result.log_likelihood, case["log_likelihood"])
    check(
        f"{name}.neg_log_likelihood",
        result.neg_log_likelihood,
        case["neg_log_likelihood"],
    )
    check_prior(f"{name}.perceptual_prior", result.perceptual_prior, case["perceptual_prior"])
    check_prior(f"{name}.observation_prior", result.observation_prior, case["observation_prior"])
    check(f"{name}.neg_log_joint", result.neg_log_joint, case["neg_log_joint"])


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
    if metadata["schema_version"] != "m8-1":
        raise AssertionError(f"unexpected fixture schema: {metadata['schema_version']}")

    for name, case in payload["cases"].items():
        check_case(name, case)

    synthetic = payload["synthetic_prior"]
    actual_prior = gaussian_log_prior(
        [1.0, 2.0, 3.0, 5.0],
        [0.0, 2.0, 0.0, 4.0],
        [1.0, 0.0, np.nan, 4.0],
    )
    check_prior("synthetic_prior", actual_prior, synthetic)

    print("M8 MATLAB/Python objective parity: PASS")


if __name__ == "__main__":
    main()
