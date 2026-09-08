"""MATLAB-style simModel adapter over the M11 simulation core."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .matlab_names import strip_config_suffix
from .result import CompatibilityResult, MatlabStruct, config_struct, parameter_struct
from .simulation import sim_model as _sim_model


def sim_model_result(
    inputs,
    perceptual_model: str,
    perceptual_parameters,
    observation_model: str | None = None,
    observation_parameters=None,
    seed: int | None = None,
    *,
    irregular_intervals: bool | None = False,
    response_uniforms: Sequence[float] | np.ndarray | None = None,
) -> CompatibilityResult:
    """Return frozen simModel fields while retaining the raw M11 API separately."""

    prc_name = strip_config_suffix(perceptual_model)
    obs_name = None if observation_model is None else strip_config_suffix(observation_model)
    raw = _sim_model(
        inputs,
        prc_name,
        perceptual_parameters,
        obs_name,
        observation_parameters,
        seed=seed,
        irregular_intervals=irregular_intervals,
        response_uniforms=response_uniforms,
    )

    c_sim_fields: dict[str, object] = {"prc_model": raw.perceptual_model}
    if raw.observation_model is not None:
        c_sim_fields["obs_model"] = raw.observation_model
        c_sim_fields["seed"] = np.nan if raw.seed is None else int(raw.seed)

    return CompatibilityResult(
        kind="sim",
        u=raw.inputs.copy(),
        ign=tuple(index + 1 for index in raw.ignored_trials),
        c_prc=config_struct(raw.perceptual_config),
        c_obs=(
            None if raw.observation_config is None else config_struct(raw.observation_config)
        ),
        c_sim=MatlabStruct(c_sim_fields),
        p_prc=parameter_struct(raw.perceptual_config, raw.perceptual_parameters),
        p_obs=(
            None
            if raw.observation_config is None or raw.observation_parameters is None
            else parameter_struct(raw.observation_config, raw.observation_parameters)
        ),
        traj=MatlabStruct(raw.trajectory),
        y=None if raw.responses is None else raw.responses.copy(),
        yhat=(
            None
            if raw.response_probabilities is None
            else raw.response_probabilities.copy()
        ),
    )


simModel = sim_model_result

__all__ = ["sim_model_result", "simModel"]
