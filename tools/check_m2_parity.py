from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, hgf_config, unitsq_sgm_config
from hgfx.core.placeholders import compute_placeholder_values
from hgfx.core.trials import build_time_axis, build_trial_masks


def _numeric_array(value: Any) -> np.ndarray:
    if not isinstance(value, list):
        value = [value]
    return np.asarray(
        [np.nan if item is None else item for item in value],
        dtype=np.float64,
    )


def _assert_array(label: str, actual: np.ndarray, expected: Any) -> None:
    reference = _numeric_array(expected).reshape(-1)
    actual = np.asarray(actual, dtype=np.float64).reshape(-1)
    if actual.shape != reference.shape or not np.allclose(
        actual, reference, rtol=1e-12, atol=1e-12, equal_nan=True
    ):
        raise AssertionError(
            f"{label} mismatch\nPython={actual!r}\nMATLAB={reference!r}"
        )


def _assert_named(
    label: str,
    actual: dict[str, float | np.ndarray],
    expected: dict[str, Any],
) -> None:
    if set(actual) != set(expected):
        raise AssertionError(
            f"{label} fields mismatch: Python={sorted(actual)} MATLAB={sorted(expected)}"
        )
    for key in sorted(actual):
        _assert_array(f"{label}.{key}", np.asarray(actual[key]), expected[key])


def _check_config(name: str, config, exported: dict[str, Any]) -> None:
    if config.model != exported["model"]:
        raise AssertionError(
            f"{name}.model mismatch: Python={config.model!r} MATLAB={exported['model']!r}"
        )
    _assert_array(f"{name}.priormus", config.priormus, exported["priormus"])
    _assert_array(f"{name}.priorsas", config.priorsas, exported["priorsas"])
    _assert_array(
        f"{name}.free_indices",
        np.asarray(config.matlab_free_indices),
        exported["free_indices"],
    )
    _assert_array(
        f"{name}.fixed_indices",
        np.asarray(config.matlab_fixed_indices),
        exported["fixed_indices"],
    )
    _assert_array(
        f"{name}.undefined_indices",
        np.asarray(config.matlab_undefined_indices),
        exported["undefined_indices"],
    )
    sample = _numeric_array(exported["sample_transformed"])
    native = config.transformed_to_native(sample)
    _assert_array(f"{name}.sample_native", native, exported["sample_native"])
    _assert_named(
        f"{name}.sample_named",
        config.transformed_to_native_structure(sample),
        exported["sample_named"],
    )

    for option in ("n_levels", "irregular_intervals", "predorpost"):
        if option in exported:
            if config.options[option] != exported[option]:
                raise AssertionError(
                    f"{name}.{option} mismatch: "
                    f"Python={config.options[option]!r} MATLAB={exported[option]!r}"
                )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))

    _check_config("hgf_binary", hgf_binary_config(), payload["hgf_binary"])
    _check_config("hgf", hgf_config(), payload["hgf"])
    _check_config("unitsq_sgm", unitsq_sgm_config(), payload["unitsq_sgm"])

    inputs = np.arange(1.0, 26.0, dtype=np.float64) / 25.0
    placeholders = compute_placeholder_values(inputs)
    p = payload["placeholders"]
    _assert_array("p99991", [placeholders.first_input], p["p99991"])
    _assert_array("p99992", [placeholders.var_first_20], p["p99992"])
    _assert_array("p99993", [placeholders.log_var_first_20], p["p99993"])
    _assert_array(
        "p99994",
        [placeholders.log_var_first_20_minus_2],
        p["p99994"],
    )

    resolved = hgf_config().resolve_placeholders(inputs)
    _assert_array(
        "hgf_resolved_priormus",
        resolved.priormus,
        payload["hgf_resolved_priormus"],
    )
    _assert_array(
        "hgf_resolved_priorsas",
        resolved.priorsas,
        payload["hgf_resolved_priorsas"],
    )

    masks = build_trial_masks(
        np.array([1.0, np.nan, 0.0, 1.0]),
        np.array([0.0, 1.0, np.nan, 1.0]),
    )
    _assert_array(
        "ignored_indices",
        np.asarray(masks.ignored_matlab_indices),
        payload["masks"]["ignored"],
    )
    _assert_array(
        "irregular_indices",
        np.asarray(masks.irregular_matlab_indices),
        payload["masks"]["irregular"],
    )

    _assert_array(
        "time_axis_regular",
        build_time_axis(
            np.array([0.1, 0.2, 0.3]),
            irregular_intervals=False,
        ),
        payload["time_axis_regular"],
    )
    _assert_array(
        "time_axis_irregular",
        build_time_axis(
            np.array([[0.1, 0.5], [0.2, 2.0], [0.3, 1.5]]),
            irregular_intervals=True,
        ),
        payload["time_axis_irregular"],
    )

    print("M2 MATLAB/Python parameter-config parity: PASS")


if __name__ == "__main__":
    main()
