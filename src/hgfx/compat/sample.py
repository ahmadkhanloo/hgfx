"""MATLAB-style sampleModel adapter over the M11 prior-predictive core."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.core.parameters import ModelConfig

from .result import CompatibilityResult, MatlabStruct, config_struct, parameter_struct
from .simulation import sample_model as _sample_model


def sample_model_result(
    inputs,
    perceptual_config: ModelConfig | str | None = None,
    observation_config: ModelConfig | str | None = None,
    seed: int | None = None,
    *,
    perceptual_standard_normals: Sequence[float] | np.ndarray | None = None,
    observation_standard_normals: Sequence[float] | np.ndarray | None = None,
    response_uniforms: Sequence[float] | np.ndarray | None = None,
    irregular_intervals: bool | None = False,
) -> CompatibilityResult:
    """Return frozen sampleModel fields with named/native/transformed parameters."""

    raw = _sample_model(
        inputs,
        perceptual_config,
        observation_config,
        seed=seed,
        perceptual_standard_normals=perceptual_standard_normals,
        observation_standard_normals=observation_standard_normals,
        response_uniforms=response_uniforms,
        irregular_intervals=irregular_intervals,
    )
    c_sim_fields: dict[str, object] = {
        "prc_model": raw.perceptual_model,
        "seed": np.nan if raw.seed is None else int(raw.seed),
    }
    if raw.observation_model is not None:
        c_sim_fields["obs_model"] = raw.observation_model

    return CompatibilityResult(
        kind="sample",
        u=raw.inputs.copy(),
        ign=tuple(index + 1 for index in raw.ignored_trials),
        c_prc=config_struct(raw.perceptual_config),
        c_obs=(
            None if raw.observation_config is None else config_struct(raw.observation_config)
        ),
        c_sim=MatlabStruct(c_sim_fields),
        p_prc=parameter_struct(
            raw.perceptual_config,
            raw.perceptual_parameters,
            transformed_parameters=raw.perceptual_transformed_parameters,
        ),
        p_obs=(
            None
            if raw.observation_config is None or raw.observation_parameters is None
            else parameter_struct(
                raw.observation_config,
                raw.observation_parameters,
                transformed_parameters=raw.observation_transformed_parameters,
            )
        ),
        traj=MatlabStruct(raw.trajectory),
        y=None if raw.responses is None else raw.responses.copy(),
    )


sampleModel = sample_model_result

__all__ = ["sample_model_result", "sampleModel"]
