"""Frozen HGF 8.2.0 compatibility configs used by M2 parity tests."""

from __future__ import annotations

import math

from hgfx.core.parameters import ModelConfig, ParameterSpec
from hgfx.core.transforms import EXPONENTIAL, IDENTITY, SIGMOID, bounded_sigmoid


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


def _jget_config(update_type: str) -> ModelConfig:
    if update_type == "hgf":
        mux_means, mux_vars = [99991.0, 1.0], [0.0, 0.0]
        logsax_means, logsax_vars = [math.log(3.0), math.log(0.1)], [0.0, 0.0]
        mua_means, mua_vars = [0.0, 1.0], [0.1, 0.0]
        logsaa_means, logsaa_vars = [math.log(3.0), math.log(0.1)], [0.0, 0.0]
        omu_mean, omu_var = 0.0, 0.0
        omx_means, omx_vars = [0.0, -7.0], [25.0, 1.0]
        oma_means, oma_vars = [0.0, -7.0], [25.0, 1.0]
    else:
        mux_means, mux_vars = [99991.0, 1.0], [0.0, 0.0]
        logsax_means, logsax_vars = [math.log(16.0), 0.0], [1.0, 1.0]
        mua_means, mua_vars = [-4.0, -4.0], [0.0, 0.0]
        logsaa_means, logsaa_vars = [0.0, math.log(4.0)], [1.0, 1.0]
        omu_mean, omu_var = 8.0, 0.0
        omx_means, omx_vars = [-1.0, 0.0], [4.0, 4.0]
        oma_means, oma_vars = [4.0, 2.0], [4.0, 4.0]

    parameters: list[ParameterSpec] = []
    index = 1
    groups = (
        ("mux_0", "mux_0", mux_means, mux_vars, IDENTITY),
        ("logsax_0", "sax_0", logsax_means, logsax_vars, EXPONENTIAL),
        ("mua_0", "mua_0", mua_means, mua_vars, IDENTITY),
        ("logsaa_0", "saa_0", logsaa_means, logsaa_vars, EXPONENTIAL),
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

    scalar_groups = (
        ("logkau", "kau", 0.0, 0.0, EXPONENTIAL),
        ("logkax_1", "kax", 0.0, 0.0, EXPONENTIAL),
        ("logkaa_1", "kaa", 0.0, 0.0, EXPONENTIAL),
        ("omu", "omu", omu_mean, omu_var, IDENTITY),
    )
    for name, native, mean, variance, transform in scalar_groups:
        parameters.append(ParameterSpec(
            name=name,
            native_name=native,
            matlab_index=index,
            prior_mean=mean,
            prior_variance=variance,
            transform=transform,
            component=None if native in {"kau", "omu"} else 1,
        ))
        index += 1

    for prefix, native, means, variances in (
        ("omx", "omx", omx_means, omx_vars),
        ("oma", "oma", oma_means, oma_vars),
    ):
        parameters.extend(_vector_params(
            start_index=index,
            transformed_prefix=prefix,
            native_name=native,
            means=means,
            variances=variances,
            transform=IDENTITY,
        ))
        index += len(means)

    return ModelConfig(
        model=f"{update_type}_jget",
        parameters=tuple(parameters),
        options={"n_levels": 2, "update_type": update_type},
        source_files=(
            f"perceptual/{update_type}_jget_config.m",
            "perceptual/hgf_jget_config_base.m",
            f"perceptual/{update_type}_jget_transp.m",
            "perceptual/hgf_jget_unified.m",
        ),
    )


def hgf_jget_config() -> ModelConfig:
    return _jget_config("hgf")


def ehgf_jget_config() -> ModelConfig:
    return _jget_config("ehgf")


def uhgf_jget_config() -> ModelConfig:
    return _jget_config("uhgf")


def _categorical_config(*, normalized: bool = False) -> ModelConfig:
    no = 3
    logit_uniform = math.log((1.0 / no) / (1.0 - 1.0 / no))
    parameters: list[ParameterSpec] = []
    index = 1
    groups = (
        ("mu2_0", "mu2_0", [logit_uniform] * no, [0.0] * no, IDENTITY),
        ("logsa2_0", "sa2_0", [0.0] * no, [0.0] * no, EXPONENTIAL),
    )
    for prefix, native, means, variances, transform in groups:
        parameters.extend(_vector_params(
            start_index=index, transformed_prefix=prefix, native_name=native,
            means=means, variances=variances, transform=transform,
        ))
        index += len(means)
    for name, native, mean, variance, transform in (
        ("mu3_0", "mu3_0", 1.0, 0.0, IDENTITY),
        ("logsa3_0", "sa3_0", math.log(0.1), 1.0, EXPONENTIAL),
        ("logitka", "ka", 0.0, 0.0, bounded_sigmoid(2.0)),
        ("om", "om", -4.0, 25.0, IDENTITY),
        ("logitth", "th", 0.0, 2.0, bounded_sigmoid(0.1)),
    ):
        parameters.append(ParameterSpec(
            name=name, native_name=native, matlab_index=index,
            prior_mean=mean, prior_variance=variance, transform=transform, component=None,
        ))
        index += 1
    source = "hgf_categorical_norm" if normalized else "hgf_categorical"
    return ModelConfig(
        # Frozen norm config itself says model='hgf_categorical'; preserve
        # distinction explicitly in options while keeping a usable HGFX name.
        model=source,
        parameters=tuple(parameters),
        options={"n_outcomes": no, "kaub": 2.0, "thub": 0.1, "normalized": normalized},
        source_files=(
            f"perceptual/{source}_config.m",
            f"perceptual/{source}_transp.m",
            f"perceptual/{source}.m",
        ),
    )


def hgf_categorical_config() -> ModelConfig:
    return _categorical_config(normalized=False)


def hgf_categorical_norm_config() -> ModelConfig:
    return _categorical_config(normalized=True)


def hgf_whatworld_config() -> ModelConfig:
    ns = 4
    ntr = ns * ns
    logit_uniform = math.log((1.0 / ns) / (1.0 - 1.0 / ns))
    parameters: list[ParameterSpec] = []
    index = 1
    for prefix, native, means, variances, transform in (
        ("mu2_0", "mu2_0", [logit_uniform] * ntr, [0.0] * ntr, IDENTITY),
        ("logsa2_0", "sa2_0", [0.0] * ntr, [0.0] * ntr, EXPONENTIAL),
    ):
        parameters.extend(_vector_params(
            start_index=index, transformed_prefix=prefix, native_name=native,
            means=means, variances=variances, transform=transform,
        ))
        index += len(means)
    for name, native, mean, variance, transform in (
        ("mu3_0", "mu3_0", 1.0, 0.0, IDENTITY),
        ("logsa3_0", "sa3_0", math.log(0.1), 1.0, EXPONENTIAL),
        ("logitka", "ka", 0.0, 0.0, bounded_sigmoid(2.0)),
        ("om", "om", -6.0, 25.0, IDENTITY),
        ("logitth", "th", 0.0, 2.0, bounded_sigmoid(0.1)),
    ):
        parameters.append(ParameterSpec(
            name=name, native_name=native, matlab_index=index,
            prior_mean=mean, prior_variance=variance, transform=transform, component=None,
        ))
        index += 1
    return ModelConfig(
        model="hgf_whatworld",
        parameters=tuple(parameters),
        options={"n_states": ns, "kaub": 2.0, "thub": 0.1},
        source_files=(
            "perceptual/hgf_whatworld_config.m",
            "perceptual/hgf_whatworld_transp.m",
            "perceptual/hgf_whatworld.m",
        ),
    )


def hgf_whichworld_config() -> ModelConfig:
    nw = 2
    parameters: list[ParameterSpec] = []
    index = 1
    for prefix, native, means, variances, transform in (
        ("mu2_0", "mu2_0", [0.0, 0.0], [0.0, 0.0], IDENTITY),
        ("logsa2_0", "sa2_0", [0.0, 0.0], [1.0, 1.0], EXPONENTIAL),
    ):
        parameters.extend(_vector_params(
            start_index=index, transformed_prefix=prefix, native_name=native,
            means=means, variances=variances, transform=transform,
        ))
        index += len(means)
    for name, native, mean, variance, transform in (
        ("mu3_0", "mu3_0", 1.0, 0.0, IDENTITY),
        ("logsa3_0", "sa3_0", math.log(0.1), 1.0, EXPONENTIAL),
        ("logitka", "ka", 0.0, 0.0, bounded_sigmoid(2.0)),
        ("om", "om", 0.0, 25.0, IDENTITY),
        ("logitth", "th", 0.0, 2.0, bounded_sigmoid(2.0)),
        ("m", "m", 0.0, 0.0, IDENTITY),
        ("logitphi", "phi", math.log(0.1 / 0.9), 2.0, SIGMOID),
    ):
        parameters.append(ParameterSpec(
            name=name, native_name=native, matlab_index=index,
            prior_mean=mean, prior_variance=variance, transform=transform, component=None,
        ))
        index += 1
    return ModelConfig(
        model="hgf_whichworld",
        parameters=tuple(parameters),
        options={"nw": nw, "kaub": 2.0, "thub": 2.0, "source_defect": "hgf_whichworld.m uses undefined da in lr1 cleanup"},
        source_files=(
            "perceptual/hgf_whichworld_config.m",
            "perceptual/hgf_whichworld_transp.m",
            "perceptual/hgf_whichworld.m",
        ),
    )


def _empty_response_config(model: str, source_prefix: str) -> ModelConfig:
    return ModelConfig(
        model=model,
        parameters=(),
        source_files=(
            f"perceptual/{source_prefix}_config.m",
            f"perceptual/{source_prefix}_transp.m",
            f"perceptual/{source_prefix}.m",
        ),
    )


def bayes_optimal_config() -> ModelConfig:
    return _empty_response_config("Bayes optimal", "bayes_optimal")


def bayes_optimal_binary_config() -> ModelConfig:
    return _empty_response_config("Bayes optimal (binary)", "bayes_optimal_binary")


def bayes_optimal_categorical_config() -> ModelConfig:
    return _empty_response_config("Bayes optimal categorical", "bayes_optimal_categorical")


def bayes_optimal_whatworld_config() -> ModelConfig:
    return _empty_response_config("Bayes optimal whatworld", "bayes_optimal_whatworld")


def bayes_optimal_whichworld_config() -> ModelConfig:
    return _empty_response_config("Bayes optimal whichworld", "bayes_optimal_whichworld")


def _rs_config(model: str, source: str, *, whatworld: bool = False) -> ModelConfig:
    if whatworld:
        means = [math.log(0.0052), math.log(0.0006), math.log(0.001)]
        variances = [0.1, 0.001, 1000.0]
        names = ["logze1", "logze2", "logze3"]
        native = ["ze1", "ze2", "ze3"]
    else:
        means = [math.log(0.0052), math.log(0.0052), math.log(0.0006), math.log(0.001)]
        variances = [0.1, 0.1, 0.001, 1000.0]
        names = ["logze1v", "logze1i", "logze2", "logze3"]
        native = ["ze1v", "ze1i", "ze2", "ze3"]
    params = tuple(
        ParameterSpec(
            name=name, native_name=native_name, matlab_index=i + 1,
            prior_mean=mean, prior_variance=variance, transform=EXPONENTIAL,
            component=None,
        )
        for i, (name, native_name, mean, variance) in enumerate(
            zip(names, native, means, variances, strict=True)
        )
    )
    transp = "rs_whatworld_transp" if whatworld else "rs_transp"
    return ModelConfig(
        model=model, parameters=params,
        source_files=(
            f"perceptual/{source}_config.m",
            f"perceptual/{transp}.m",
            f"perceptual/{source}.m",
        ),
    )


def rs_belief_config() -> ModelConfig:
    return _rs_config("Response speed: belief", "rs_belief")


def rs_precision_config() -> ModelConfig:
    return _rs_config("Response speed: precision", "rs_precision")


def rs_surprise_config() -> ModelConfig:
    return _rs_config("Response speed: surprise", "rs_surprise")


def rs_precision_whatworld_config() -> ModelConfig:
    return _rs_config("Response speed: precision", "rs_precision_whatworld", whatworld=True)


def squared_pe_config() -> ModelConfig:
    return ModelConfig(
        model="gaussian_obs",
        parameters=(ParameterSpec(
            name="logze", native_name="ze", matlab_index=1,
            prior_mean=math.log(0.05), prior_variance=0.0, transform=EXPONENTIAL,
            component=None,
        ),),
        source_files=(
            "perceptual/squared_pe_config.m",
            "perceptual/squared_pe_transp.m",
            "perceptual/squared_pe.m",
        ),
    )


def condhalluc_obs_config() -> ModelConfig:
    return ModelConfig(
        model="condhalluc_obs",
        parameters=(ParameterSpec(
            name="logbe", native_name="be", matlab_index=1,
            prior_mean=math.log(48.0), prior_variance=1.0, transform=EXPONENTIAL,
            component=None,
        ),),
        source_files=(
            "observation/condhalluc_obs_config.m",
            "observation/condhalluc_obs_transp.m",
            "observation/condhalluc_obs.m",
            "observation/condhalluc_obs_sim.m",
        ),
    )


def condhalluc_obs2_config() -> ModelConfig:
    return ModelConfig(
        model="condhalluc_obs2",
        parameters=(
            ParameterSpec("logbe", "be", 1, math.log(48.0), 1.0, EXPONENTIAL, None),
            ParameterSpec("lognu", "nu", 2, 0.0, 1.0, EXPONENTIAL, None),
        ),
        source_files=(
            "observation/condhalluc_obs2_config.m",
            "observation/condhalluc_obs2_transp.m",
            "observation/condhalluc_obs2.m",
            "observation/condhalluc_obs2_sim.m",
        ),
    )


def condhalluc_obs3_config() -> ModelConfig:
    return ModelConfig(
        model="condhalluc_obs3",
        parameters=(ParameterSpec(
            name="logbe", native_name="be", matlab_index=1,
            prior_mean=math.log(48.0), prior_variance=1.0, transform=EXPONENTIAL,
            component=None,
        ),),
        source_files=(
            "observation/condhalluc_obs3_config.m",
            "observation/condhalluc_obs3_transp.m",
            "observation/condhalluc_obs3.m",
            "observation/condhalluc_obs3_sim.m",
        ),
    )


def softmax_wld_config() -> ModelConfig:
    return ModelConfig(
        model="softmax_wld",
        parameters=(
            ParameterSpec("logbe", "be", 1, 0.0, 16.0, EXPONENTIAL, None),
            ParameterSpec("la_wd", "la_wd", 2, 0.0, 0.25, IDENTITY, None),
            ParameterSpec("la_ld", "la_ld", 3, 0.0, 0.25, IDENTITY, None),
        ),
        options={"predorpost": 1, "source_likelihood_quirk": "ptrans1 reused as la_wd"},
        source_files=(
            "observation/softmax_wld_config.m",
            "observation/softmax_wld_transp.m",
            "observation/softmax_wld.m",
            "observation/softmax_wld_sim.m",
        ),
    )


def softmax_mu3_wld_config() -> ModelConfig:
    return ModelConfig(
        model="softmax_mu3_wld",
        parameters=(
            ParameterSpec("la_wd", "la_wd", 1, 0.0, 0.25, IDENTITY, None),
            ParameterSpec("la_ld", "la_ld", 2, 0.0, 0.25, IDENTITY, None),
        ),
        options={"predorpost": 1},
        source_files=(
            "observation/softmax_mu3_wld_config.m",
            "observation/softmax_mu3_wld_transp.m",
            "observation/softmax_mu3_wld.m",
            "observation/softmax_mu3_wld_sim.m",
        ),
    )


def logrt_linear_whatworld_config() -> ModelConfig:
    return ModelConfig(
        model="Linear log-reaction time for WhatWorld models",
        parameters=(
            ParameterSpec("be0", "be0", 1, math.log(500.0), 4.0, IDENTITY, None),
            ParameterSpec("be1", "be1", 2, 0.0, 4.0, IDENTITY, None),
            ParameterSpec("be2", "be2", 3, 0.0, 4.0, IDENTITY, None),
            ParameterSpec("be3", "be3", 4, 0.0, 4.0, IDENTITY, None),
            ParameterSpec("logze", "ze", 5, math.log(math.log(20.0)), math.log(2.0), EXPONENTIAL, None),
        ),
        source_files=(
            "observation/logrt_linear_whatworld_config.m",
            "observation/logrt_linear_whatworld_transp.m",
            "observation/logrt_linear_whatworld.m",
        ),
    )

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
