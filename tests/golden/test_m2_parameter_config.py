from __future__ import annotations

import math

import numpy as np
import pytest

from hgfx.compat.configs import hgf_binary_config, hgf_config, unitsq_sgm_config
from hgfx.core.placeholders import compute_placeholder_values
from hgfx.core.priors import PriorStatus, prior_status
from hgfx.core.trials import build_time_axis, build_trial_masks


def test_hgf_binary_flat_order_and_status_match_matlab() -> None:
    config = hgf_binary_config()

    assert [parameter.native_name for parameter in config.parameters] == [
        "mu_0", "mu_0", "mu_0",
        "sa_0", "sa_0", "sa_0",
        "rho", "rho", "rho",
        "ka", "ka",
        "om", "om", "om",
    ]
    np.testing.assert_allclose(
        config.priormus,
        np.array([
            np.nan, 0.0, 1.0,
            np.nan, math.log(0.1), 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, -3.0, -6.0,
        ]),
        equal_nan=True,
    )
    np.testing.assert_allclose(
        config.priorsas,
        np.array([
            np.nan, 0.0, 0.0,
            np.nan, 0.0, 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, 16.0, 16.0,
        ]),
        equal_nan=True,
    )
    assert config.matlab_free_indices == (13, 14)
    assert config.matlab_undefined_indices == (1, 4, 7, 12)


def test_continuous_hgf_placeholders_and_fixed_free_semantics() -> None:
    inputs = np.arange(1.0, 26.0, dtype=np.float64) / 25.0
    config = hgf_config()
    resolved = config.resolve_placeholders(inputs)

    placeholders = compute_placeholder_values(inputs)
    assert resolved.priormus[0] == pytest.approx(placeholders.first_input)
    assert resolved.priorsas[0] == pytest.approx(placeholders.var_first_20)
    assert resolved.priormus[2] == pytest.approx(placeholders.log_var_first_20)
    assert resolved.priormus[-3] == pytest.approx(placeholders.log_var_first_20)
    assert resolved.priormus[-1] == pytest.approx(-placeholders.log_var_first_20)

    assert prior_status(0.0) is PriorStatus.FIXED
    assert prior_status(float("nan")) is PriorStatus.UNDEFINED
    assert prior_status(1.0) is PriorStatus.FREE


def test_transformed_to_native_matches_matlab_layout() -> None:
    config = hgf_binary_config()
    transformed = np.linspace(-1.0, 1.0, len(config.parameters))
    native = config.transformed_to_native(transformed)
    structured = config.transformed_to_native_structure(transformed)

    np.testing.assert_allclose(structured["mu_0"], native[0:3])
    np.testing.assert_allclose(structured["sa_0"], np.exp(transformed[3:6]))
    np.testing.assert_allclose(structured["rho"], native[6:9])
    np.testing.assert_allclose(structured["ka"], np.exp(transformed[9:11]))
    np.testing.assert_allclose(structured["om"], native[11:14])


def test_unitsq_sgm_config_matches_matlab() -> None:
    config = unitsq_sgm_config()
    assert config.options["predorpost"] == 1
    np.testing.assert_allclose(config.priormus, [math.log(48.0)])
    np.testing.assert_allclose(config.priorsas, [1.0])
    np.testing.assert_allclose(
        config.transformed_to_native(config.priormus),
        [48.0],
    )


def test_trial_masks_match_fitmodel_data_prep() -> None:
    inputs = np.array([0.0, 1.0, np.nan, 1.0])
    responses = np.array([1.0, np.nan, 0.0, 1.0])
    masks = build_trial_masks(responses, inputs)

    assert masks.ignored_matlab_indices == (3,)
    assert masks.irregular_matlab_indices == (2, 3)


def test_time_axis_matches_hgf_time_axis() -> None:
    regular = np.array([0.1, 0.2, 0.3])
    np.testing.assert_array_equal(
        build_time_axis(regular, irregular_intervals=False),
        np.ones(4),
    )

    irregular = np.array([
        [0.1, 0.5],
        [0.2, 2.0],
        [0.3, 1.5],
    ])
    np.testing.assert_array_equal(
        build_time_axis(irregular, irregular_intervals=True),
        np.array([0.0, 0.5, 2.0, 1.5]),
    )

    with pytest.raises(ValueError, match="more than one column"):
        build_time_axis(regular, irregular_intervals=True)
