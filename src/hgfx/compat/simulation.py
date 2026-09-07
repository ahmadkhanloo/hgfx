"""MATLAB-compatible simulation and prior-predictive sampling.

M11 freezes the orchestration boundary of HGF Toolbox 8.2.0 simModel.m
and sampleModel.m. Random streams are intentionally not claimed to be
byte-identical across MATLAB and NumPy. Callers can inject exact random
drivers exported by MATLAB for deterministic cross-language validation.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

import numpy as np

from hgfx.core.parameters import ModelConfig
from hgfx.core.placeholders import first_input_column
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.models.hgf_binary import hgf_binary
from hgfx.models.uhgf_binary import uhgf_binary

from .configs import hgf_binary_config, unitsq_sgm_config


@dataclass(frozen=True)
class SimulationResult:
    """Compatibility representation of simModel / sampleModel output."""

    inputs: np.ndarray
    ignored_trials: tuple[int, ...]
    perceptual_model: str
    perceptual_config: ModelConfig
    perceptual_parameters: np.ndarray
    trajectory: dict[str, np.ndarray]
    inf_states: np.ndarray
    observation_model: str | None = None
    observation_config: ModelConfig | None = None
    observation_parameters: np.ndarray | None = None
    responses: np.ndarray | None = None
    response_probabilities: np.ndarray | None = None
    seed: int | None = None
    perceptual_transformed_parameters: np.ndarray | None = None
    observation_transformed_parameters: np.ndarray | None = None


def _binary_variant_config(update_type: str) -> ModelConfig:
    base = hgf_binary_config()
    parameters = list(base.parameters)
    if update_type == "ehgf":
        parameters[12] = replace(parameters[12], prior_mean=-3.0, prior_variance=4.0)
        parameters[13] = replace(parameters[13], prior_mean=2.0, prior_variance=4.0)
    return replace(
        base,
        model=f"{update_type}_binary",
        parameters=tuple(parameters),
        options={"n_levels": 3, "irregular_intervals": False, "update_type": update_type},
        source_files=(
            f"perceptual/{update_type}_binary_config.m",
            "perceptual/hgf_binary_config_base.m",
            f"perceptual/{update_type}_binary_transp.m",
            f"perceptual/{update_type}_binary_namep.m",
        ),
    )


def ehgf_binary_config() -> ModelConfig:
    return _binary_variant_config("ehgf")


def uhgf_binary_config() -> ModelConfig:
    return _binary_variant_config("uhgf")


_PERCEPTUAL_CONFIGS = {
    "hgf_binary": hgf_binary_config,
    "ehgf_binary": ehgf_binary_config,
    "uhgf_binary": uhgf_binary_config,
}

_PERCEPTUAL_FORWARD = {
    "hgf_binary": hgf_binary,
    "ehgf_binary": ehgf_binary,
    "uhgf_binary": uhgf_binary,
}


def _as_config(config: ModelConfig | str | None, *, default: str) -> ModelConfig:
    if config is None:
        return _PERCEPTUAL_CONFIGS[default]()
    if isinstance(config, ModelConfig):
        return config
    normalized = config[:-7] if config.endswith("_config") else config
    if normalized in _PERCEPTUAL_CONFIGS:
        return _PERCEPTUAL_CONFIGS[normalized]()
    if normalized == "unitsq_sgm":
        return unitsq_sgm_config()
    raise ValueError(f"Unsupported compatibility config: {config}")


def _ignored_trials(inputs) -> tuple[int, ...]:
    values = np.asarray(first_input_column(inputs), dtype=np.float64).reshape(-1)
    return tuple(int(i) for i in np.flatnonzero(np.isnan(values)))


def _generator(seed: int | None) -> np.random.Generator:
    return np.random.default_rng(seed)


def _draw_vector(
    supplied: Sequence[float] | np.ndarray | None,
    *,
    size: int,
    rng: np.random.Generator,
    name: str,
) -> np.ndarray:
    if supplied is None:
        return np.asarray(rng.standard_normal(size), dtype=np.float64)
    values = np.asarray(supplied, dtype=np.float64).reshape(-1)
    if values.size != size:
        raise ValueError(f"{name} must contain exactly {size} values")
    return values


def unitsq_sgm_probability(
    inf_states,
    observation_parameters,
    *,
    predorpost: int = 1,
) -> np.ndarray:
    """Deterministic probability path of frozen unitsq_sgm_sim.m."""

    states = np.asarray(inf_states, dtype=np.float64)
    if states.ndim != 3 or states.shape[1] < 1 or states.shape[2] < 3:
        raise ValueError("binary HGF inf_states must have shape (trial, level, state)")
    pop = 0 if int(predorpost) == 1 else 2
    x = states[:, 0, pop]
    ze = float(np.asarray(observation_parameters, dtype=np.float64).reshape(-1)[0])
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        numerator = x**ze
        probability = numerator / (numerator + (1.0 - x) ** ze)
    return np.asarray(probability, dtype=np.float64)


def simulate_unitsq_sgm(
    inf_states,
    observation_parameters,
    *,
    predorpost: int = 1,
    seed: int | None = None,
    uniform_draws: Sequence[float] | np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate Bernoulli responses while exposing deterministic probabilities."""

    probability = unitsq_sgm_probability(
        inf_states,
        observation_parameters,
        predorpost=predorpost,
    )
    if uniform_draws is None:
        draws = _generator(seed).random(probability.size)
    else:
        draws = np.asarray(uniform_draws, dtype=np.float64).reshape(-1)
        if draws.size != probability.size:
            raise ValueError("uniform_draws length must match number of trials")
        if np.any((draws < 0.0) | (draws >= 1.0)):
            raise ValueError("uniform_draws must be in [0, 1)")
    responses = (draws < probability).astype(np.float64)
    return responses, probability


def softmax_binary_probability(
    inf_states,
    observation_parameters,
    *,
    predorpost: int = 1,
) -> np.ndarray:
    """Deterministic path of frozen softmax_binary_sim.m."""

    states = np.asarray(inf_states, dtype=np.float64)
    pop = 0 if int(predorpost) == 1 else 2
    x = states[:, 0, pop]
    beta = float(np.asarray(observation_parameters, dtype=np.float64).reshape(-1)[0])
    arg = beta * (2.0 * x - 1.0)
    return np.asarray(1.0 / (1.0 + np.exp(-arg)), dtype=np.float64)


def simulate_softmax_binary(
    inf_states,
    observation_parameters,
    *,
    predorpost: int = 1,
    seed: int | None = None,
    uniform_draws: Sequence[float] | np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    probability = softmax_binary_probability(
        inf_states,
        observation_parameters,
        predorpost=predorpost,
    )
    if uniform_draws is None:
        draws = _generator(seed).random(probability.size)
    else:
        draws = np.asarray(uniform_draws, dtype=np.float64).reshape(-1)
        if draws.size != probability.size:
            raise ValueError("uniform_draws length must match number of trials")
    return (draws < probability).astype(np.float64), probability


def simulate_gaussian_obs(
    inf_states,
    observation_parameters,
    *,
    seed: int | None = None,
    standard_normal_draws: Sequence[float] | np.ndarray | None = None,
    offset: float = 0.0,
) -> np.ndarray:
    """Frozen Gaussian observation sampling with optional exported normal draws."""

    states = np.asarray(inf_states, dtype=np.float64)
    mean = np.asarray(states[:, 0, 0], dtype=np.float64) + np.float64(offset)
    variance = float(np.asarray(observation_parameters, dtype=np.float64).reshape(-1)[0])
    if variance < 0.0:
        raise ValueError("Gaussian observation variance must be non-negative")
    z = _draw_vector(
        standard_normal_draws,
        size=mean.size,
        rng=_generator(seed),
        name="standard_normal_draws",
    )
    return mean + np.sqrt(np.float64(variance)) * z


def _simulate_observation(
    model: str,
    inf_states: np.ndarray,
    native_parameters: np.ndarray,
    *,
    config: ModelConfig,
    seed: int | None,
    uniform_draws: Sequence[float] | np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray | None]:
    if model == "unitsq_sgm":
        return simulate_unitsq_sgm(
            inf_states,
            native_parameters,
            predorpost=int(config.options.get("predorpost", 1)),
            seed=seed,
            uniform_draws=uniform_draws,
        )
    if model == "softmax_binary":
        return simulate_softmax_binary(
            inf_states,
            native_parameters,
            predorpost=int(config.options.get("predorpost", 1)),
            seed=seed,
            uniform_draws=uniform_draws,
        )
    raise ValueError(f"Unsupported observation simulation model: {model}")


def _trim_simmodel_binary_trajectory(
    trajectory: dict[str, np.ndarray],
    ignored: tuple[int, ...],
) -> dict[str, np.ndarray]:
    """Mirror destructive row deletion in the frozen simModel.m NaN check."""

    result = {key: np.asarray(value).copy() for key, value in trajectory.items()}
    if not ignored:
        return result
    idx = np.asarray(ignored, dtype=np.int64)
    for key in ("muhat", "sahat"):
        if key in result:
            result[key] = np.delete(result[key], idx, axis=0)
    return result


def sim_model(
    inputs,
    perceptual_model: str,
    perceptual_parameters,
    observation_model: str | None = None,
    observation_parameters=None,
    *,
    seed: int | None = None,
    irregular_intervals: bool | None = False,
    response_uniforms: Sequence[float] | np.ndarray | None = None,
) -> SimulationResult:
    """Compatibility implementation of frozen simModel.m for binary HGF variants."""

    if perceptual_model not in _PERCEPTUAL_FORWARD:
        raise ValueError(f"Unsupported perceptual simulation model: {perceptual_model}")
    ignored = _ignored_trials(inputs)
    prc_config = _PERCEPTUAL_CONFIGS[perceptual_model]()
    p_prc = np.asarray(perceptual_parameters, dtype=np.float64).reshape(-1)
    trajectory, inf_states = _PERCEPTUAL_FORWARD[perceptual_model](
        inputs,
        p_prc,
        transformed=False,
        irregular_intervals=irregular_intervals,
        ignored_trials=ignored,
    )
    returned_trajectory = _trim_simmodel_binary_trajectory(trajectory, ignored)

    input_array = np.asarray(inputs, dtype=np.float64).copy()
    if observation_model is None:
        return SimulationResult(
            inputs=input_array,
            ignored_trials=ignored,
            perceptual_model=perceptual_model,
            perceptual_config=prc_config,
            perceptual_parameters=p_prc.copy(),
            trajectory=returned_trajectory,
            inf_states=np.asarray(inf_states, dtype=np.float64),
        )
    if observation_parameters is None:
        raise ValueError("observation_parameters are required with an observation_model")

    if observation_model != "unitsq_sgm":
        raise ValueError(f"Unsupported compatibility observation config: {observation_model}")
    obs_config = unitsq_sgm_config()
    p_obs = np.asarray(observation_parameters, dtype=np.float64).reshape(-1)
    y, probability = _simulate_observation(
        observation_model,
        np.asarray(inf_states, dtype=np.float64),
        p_obs,
        config=obs_config,
        seed=seed,
        uniform_draws=response_uniforms,
    )
    return SimulationResult(
        inputs=input_array,
        ignored_trials=ignored,
        perceptual_model=perceptual_model,
        perceptual_config=prc_config,
        perceptual_parameters=p_prc.copy(),
        trajectory=returned_trajectory,
        inf_states=np.asarray(inf_states, dtype=np.float64),
        observation_model=observation_model,
        observation_config=obs_config,
        observation_parameters=p_obs.copy(),
        responses=y,
        response_probabilities=probability,
        seed=seed,
    )


def sample_model(
    inputs,
    perceptual_config: ModelConfig | str | None = None,
    observation_config: ModelConfig | str | None = None,
    *,
    seed: int | None = None,
    perceptual_standard_normals: Sequence[float] | np.ndarray | None = None,
    observation_standard_normals: Sequence[float] | np.ndarray | None = None,
    response_uniforms: Sequence[float] | np.ndarray | None = None,
    irregular_intervals: bool | None = False,
) -> SimulationResult:
    """Compatibility implementation of frozen sampleModel.m.

    The frozen default is ehgf_binary_config. Exact MATLAB prior draws can
    be injected as standard-normal vectors; otherwise NumPy supplies a local
    reproducible stream from seed.
    """

    prc_config = _as_config(perceptual_config, default="ehgf_binary").resolve_placeholders(inputs)
    if prc_config.model not in _PERCEPTUAL_FORWARD:
        raise ValueError(f"Unsupported sampled perceptual model: {prc_config.model}")

    rng = _generator(seed)
    prc_z = _draw_vector(
        perceptual_standard_normals,
        size=len(prc_config.parameters),
        rng=rng,
        name="perceptual_standard_normals",
    )
    with np.errstate(invalid="ignore"):
        ptrans_prc = prc_config.priormus + prc_z * np.sqrt(prc_config.priorsas)
    p_prc = prc_config.transformed_to_native(ptrans_prc)

    ignored = _ignored_trials(inputs)
    trajectory, inf_states = _PERCEPTUAL_FORWARD[prc_config.model](
        inputs,
        p_prc,
        transformed=False,
        irregular_intervals=irregular_intervals,
        ignored_trials=ignored,
    )

    input_array = np.asarray(inputs, dtype=np.float64).copy()
    if observation_config is None:
        return SimulationResult(
            inputs=input_array,
            ignored_trials=ignored,
            perceptual_model=prc_config.model,
            perceptual_config=prc_config,
            perceptual_parameters=p_prc,
            perceptual_transformed_parameters=ptrans_prc,
            trajectory={key: np.asarray(value).copy() for key, value in trajectory.items()},
            inf_states=np.asarray(inf_states, dtype=np.float64),
            seed=seed,
        )

    obs_config = _as_config(observation_config, default="ehgf_binary")
    if obs_config.model != "unitsq_sgm":
        raise ValueError(f"Unsupported sampled observation model: {obs_config.model}")
    obs_z = _draw_vector(
        observation_standard_normals,
        size=len(obs_config.parameters),
        rng=rng,
        name="observation_standard_normals",
    )
    with np.errstate(invalid="ignore"):
        ptrans_obs = obs_config.priormus + obs_z * np.sqrt(obs_config.priorsas)
    p_obs = obs_config.transformed_to_native(ptrans_obs)

    # Frozen observation simulation functions reinitialize RNG from c_sim.seed.
    y, probability = _simulate_observation(
        obs_config.model,
        np.asarray(inf_states, dtype=np.float64),
        p_obs,
        config=obs_config,
        seed=seed,
        uniform_draws=response_uniforms,
    )
    return SimulationResult(
        inputs=input_array,
        ignored_trials=ignored,
        perceptual_model=prc_config.model,
        perceptual_config=prc_config,
        perceptual_parameters=p_prc,
        perceptual_transformed_parameters=ptrans_prc,
        trajectory={key: np.asarray(value).copy() for key, value in trajectory.items()},
        inf_states=np.asarray(inf_states, dtype=np.float64),
        observation_model=obs_config.model,
        observation_config=obs_config,
        observation_parameters=p_obs,
        observation_transformed_parameters=ptrans_obs,
        responses=y,
        response_probabilities=probability,
        seed=seed,
    )
