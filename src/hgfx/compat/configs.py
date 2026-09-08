"""Frozen HGF 8.2.0 compatibility configs used by M2 parity tests."""

from __future__ import annotations

import math

from hgfx.core.parameters import ModelConfig, ParameterSpec
from hgfx.core.transforms import EXPONENTIAL, IDENTITY, SIGMOID


def _vector_params(
    *,
    start_index: int,
    transformed_prefix: str,
    native_name: str,
    means: list[float],
    variances: list[float],
    transform,
) -> list[ParameterSpec]:
    return [
        ParameterSpec(
            name=f"{transformed_prefix}[{component}]",
            native_name=native_name,
            matlab_index=start_index + component,
            prior_mean=float(mean),
            prior_variance=float(variance),
            transform=transform,
            component=component,
        )
        for component, (mean, variance) in enumerate(
            zip(means, variances, strict=True)
        )
    ]


def hgf_binary_config() -> ModelConfig:
    parameters: list[ParameterSpec] = []
    index = 1

    groups = (
        ("mu_0", "mu_0", [math.nan, 0.0, 1.0], [math.nan, 0.0, 0.0], IDENTITY),
        (
            "logsa_0",
            "sa_0",
            [math.nan, math.log(0.1), math.log(1.0)],
            [math.nan, 0.0, 0.0],
            EXPONENTIAL,
        ),
        ("rho", "rho", [math.nan, 0.0, 0.0], [math.nan, 0.0, 0.0], IDENTITY),
        (
            "logka",
            "ka",
            [math.log(1.0), math.log(1.0)],
            [0.0, 0.0],
            EXPONENTIAL,
        ),
        ("om", "om", [math.nan, -3.0, -6.0], [math.nan, 16.0, 16.0], IDENTITY),
    )

    for transformed_prefix, native_name, means, variances, transform in groups:
        parameters.extend(
            _vector_params(
                start_index=index,
                transformed_prefix=transformed_prefix,
                native_name=native_name,
                means=means,
                variances=variances,
                transform=transform,
            )
        )
        index += len(means)

    return ModelConfig(
        model="hgf_binary",
        parameters=tuple(parameters),
        options={
            "n_levels": 3,
            "irregular_intervals": False,
            "update_type": "hgf",
        },
        source_files=(
            "perceptual/hgf_binary_config.m",
            "perceptual/hgf_binary_config_base.m",
            "perceptual/hgf_binary_transp.m",
            "perceptual/hgf_binary_namep.m",
        ),
    )


def hgf_config() -> ModelConfig:
    parameters: list[ParameterSpec] = []
    index = 1

    groups = (
        ("mu_0", "mu_0", [99991.0, 1.0], [99992.0, 0.0], IDENTITY),
        (
            "logsa_0",
            "sa_0",
            [99993.0, math.log(0.1)],
            [1.0, 1.0],
            EXPONENTIAL,
        ),
        ("rho", "rho", [0.0, 0.0], [0.0, 0.0], IDENTITY),
        ("logka", "ka", [math.log(1.0)], [0.0], EXPONENTIAL),
        ("om", "om", [99993.0, -4.0], [16.0, 16.0], IDENTITY),
    )

    for transformed_prefix, native_name, means, variances, transform in groups:
        parameters.extend(
            _vector_params(
                start_index=index,
                transformed_prefix=transformed_prefix,
                native_name=native_name,
                means=means,
                variances=variances,
                transform=transform,
            )
        )
        index += len(means)

    parameters.append(
        ParameterSpec(
            name="logpi_u",
            native_name="pi_u",
            matlab_index=index,
            prior_mean=-99993.0,
            prior_variance=4.0,
            transform=EXPONENTIAL,
            component=None,
        )
    )

    return ModelConfig(
        model="hgf",
        parameters=tuple(parameters),
        options={
            "n_levels": 2,
            "irregular_intervals": False,
            "update_type": "hgf",
        },
        source_files=(
            "perceptual/hgf_config.m",
            "perceptual/hgf_config_base.m",
            "perceptual/hgf_transp.m",
            "perceptual/hgf_namep.m",
        ),
    )



def hgf_ar1_config() -> ModelConfig:
    """Frozen hgf_ar1_config.m for the default two-level continuous AR1 HGF."""

    parameters: list[ParameterSpec] = []
    index = 1
    groups = (
        ("mu_0", "mu_0", [99991.0, 1.0], [99992.0, 0.0], IDENTITY),
        (
            "logsa_0",
            "sa_0",
            [99993.0, math.log(0.1)],
            [1.0, 1.0],
            EXPONENTIAL,
        ),
        (
            "logitphi",
            "phi",
            [math.log(0.1 / 0.9), -math.inf],
            [100.0, 0.0],
            SIGMOID,
        ),
        ("m", "m", [99991.0, 1.0], [99992.0, 0.0], IDENTITY),
        ("logka", "ka", [0.0], [0.0], EXPONENTIAL),
        # Frozen hgf_ar1_transp leaves both omega entries in native space.
        # The last element is exponentiated only inside hgf_ar1.m as theta.
        ("om", "om", [99994.0, -6.0], [100.0, 100.0], IDENTITY),
    )
    for transformed_prefix, native_name, means, variances, transform in groups:
        parameters.extend(
            _vector_params(
                start_index=index,
                transformed_prefix=transformed_prefix,
                native_name=native_name,
                means=means,
                variances=variances,
                transform=transform,
            )
        )
        index += len(means)

    parameters.append(
        ParameterSpec(
            name="logal",
            native_name="al",
            matlab_index=index,
            prior_mean=99993.0,
            prior_variance=4.0,
            transform=EXPONENTIAL,
            component=None,
        )
    )
    return ModelConfig(
        model="hgf_ar1",
        parameters=tuple(parameters),
        options={"n_levels": 2, "irregular_intervals": False, "update_type": "hgf"},
        source_files=(
            "perceptual/hgf_ar1_config.m",
            "perceptual/hgf_ar1_transp.m",
            "perceptual/hgf_ar1_namep.m",
            "perceptual/hgf_ar1.m",
        ),
    )


def hgf_binary_mab_config() -> ModelConfig:
    parameters: list[ParameterSpec] = []
    index = 1
    groups = (
        ("mu_0", "mu_0", [math.nan, 0.0, 1.0], [math.nan, 0.0, 0.0], IDENTITY),
        ("logsa_0", "sa_0", [math.nan, math.log(0.1), 0.0], [math.nan, 0.0, 0.0], EXPONENTIAL),
        ("rho", "rho", [math.nan, 0.0, 0.0], [math.nan, 0.0, 0.0], IDENTITY),
        ("logka", "ka", [0.0, 0.0], [0.0, 0.0], EXPONENTIAL),
        ("om", "om", [math.nan, -2.0, -6.0], [math.nan, 16.0, 16.0], IDENTITY),
    )
    for prefix, native, means, variances, transform in groups:
        parameters.extend(_vector_params(
            start_index=index,
            transformed_prefix=prefix,
            native_name=native,
            means=means,
            variances=variances,
            transform=transform,
        ))
        index += len(means)
    return ModelConfig(
        model="hgf_binary_mab",
        parameters=tuple(parameters),
        options={"n_levels": 3, "n_bandits": 3, "coupled": False, "irregular_intervals": False, "update_type": "hgf"},
        source_files=(
            "perceptual/hgf_binary_mab_config.m",
            "perceptual/hgf_binary_mab_transp.m",
            "perceptual/hgf_binary_mab.m",
        ),
    )


def hgf_ar1_mab_config() -> ModelConfig:
    parameters: list[ParameterSpec] = []
    index = 1
    groups = (
        ("mu_0", "mu_0", [50.0, 1.0], [0.0, 0.0], IDENTITY),
        ("logsa_0", "sa_0", [math.log(70.0), math.log(0.1)], [0.0, 0.0], EXPONENTIAL),
        ("logitphi", "phi", [math.log(0.02 / 0.98), -math.inf], [1.0, 0.0], SIGMOID),
        ("m", "m", [50.0, 1.0], [64.0, 0.0], IDENTITY),
        ("logka", "ka", [0.0], [0.0], EXPONENTIAL),
        ("om", "om", [4.0, -4.0], [16.0, 16.0], IDENTITY),
    )
    for prefix, native, means, variances, transform in groups:
        parameters.extend(_vector_params(
            start_index=index,
            transformed_prefix=prefix,
            native_name=native,
            means=means,
            variances=variances,
            transform=transform,
        ))
        index += len(means)
    parameters.append(ParameterSpec(
        name="logal",
        native_name="al",
        matlab_index=index,
        prior_mean=math.log(128.0),
        prior_variance=0.0,
        transform=EXPONENTIAL,
        component=None,
    ))
    return ModelConfig(
        model="hgf_ar1_mab",
        parameters=tuple(parameters),
        options={"n_levels": 2, "n_bandits": 3, "irregular_intervals": False, "update_type": "hgf"},
        source_files=(
            "perceptual/hgf_ar1_mab_config.m",
            "perceptual/hgf_ar1_mab_transp.m",
            "perceptual/hgf_ar1_mab.m",
        ),
    )


def _ar1_binary_mab_config(update_type: str) -> ModelConfig:
    parameters: list[ParameterSpec] = []
    index = 1
    if update_type == "hgf":
        groups = (
            ("mu_0", "mu_0", [math.nan, 0.0, 1.0], [math.nan, 1.0, 1.0], IDENTITY),
            ("logsa_0", "sa_0", [math.nan, math.log(0.1), 0.0], [math.nan, 1.0, 1.0], EXPONENTIAL),
            ("logitphi", "phi", [math.nan, math.log(0.4 / 0.6), math.log(0.2 / 0.8)], [math.nan, 1.0, 1.0], SIGMOID),
            ("m", "m", [math.nan, 0.0, 1.0], [math.nan, 0.0, 0.0], IDENTITY),
            ("logka", "ka", [0.0, 0.0], [0.0, 0.1], EXPONENTIAL),
            ("om", "om", [math.nan, -2.0, -2.0], [math.nan, 1.0, 1.0], IDENTITY),
        )
        n_bandits = 3
    else:
        groups = (
            ("mu_0", "mu_0", [math.nan, 0.0, 1.0], [math.nan, 1.0, 1.0], IDENTITY),
            ("logsa_0", "sa_0", [math.nan, math.log(0.1), 0.0], [math.nan, 1.0, 1.0], EXPONENTIAL),
            ("logitphi", "phi", [math.nan, math.log(0.4 / 0.6), math.log(0.2 / 0.8)], [math.nan, 0.0, 0.0], SIGMOID),
            ("m", "m", [math.nan, 0.0, 1.0], [math.nan, 0.0, 1.0], IDENTITY),
            ("rho", "rho", [math.nan, 0.0, 0.0], [math.nan, 0.0, 0.0], IDENTITY),
            ("logka", "ka", [0.0, 0.0], [0.0, 0.1], EXPONENTIAL),
            ("om", "om", [math.nan, -3.0, 2.0], [math.nan, 4.0, 4.0], IDENTITY),
        )
        n_bandits = 4
    for prefix, native, means, variances, transform in groups:
        parameters.extend(_vector_params(
            start_index=index,
            transformed_prefix=prefix,
            native_name=native,
            means=means,
            variances=variances,
            transform=transform,
        ))
        index += len(means)
    return ModelConfig(
        model=f"{update_type}_ar1_binary_mab",
        parameters=tuple(parameters),
        options={"n_levels": 3, "n_bandits": n_bandits, "coupled": False, "irregular_intervals": False, "update_type": update_type},
        source_files=(
            f"perceptual/{update_type}_ar1_binary_mab_config.m",
            "perceptual/hgf_ar1_binary_mab_config_base.m",
            f"perceptual/{update_type}_ar1_binary_mab_transp.m",
            "perceptual/hgf_ar1_binary_mab_unified.m",
        ),
    )


def hgf_ar1_binary_mab_config() -> ModelConfig:
    return _ar1_binary_mab_config("hgf")


def ehgf_ar1_binary_mab_config() -> ModelConfig:
    return _ar1_binary_mab_config("ehgf")


def uhgf_ar1_binary_mab_config() -> ModelConfig:
    return _ar1_binary_mab_config("uhgf")

def unitsq_sgm_config() -> ModelConfig:
    return ModelConfig(
        model="unitsq_sgm",
        parameters=(
            ParameterSpec(
                name="logze",
                native_name="ze",
                matlab_index=1,
                prior_mean=math.log(48.0),
                prior_variance=1.0,
                transform=EXPONENTIAL,
                component=None,
            ),
        ),
        options={"predorpost": 1},
        source_files=(
            "observation/unitsq_sgm_config.m",
            "observation/unitsq_sgm_transp.m",
            "observation/unitsq_sgm_namep.m",
        ),
    )
