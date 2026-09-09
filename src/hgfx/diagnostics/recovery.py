"""Scientific recovery diagnostics for M18."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.objective import ObjectiveResult, evaluate_objective
from hgfx.compat.simulation import ehgf_binary_config, sim_model, uhgf_binary_config
from hgfx.core.parameters import ModelConfig
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.models.hgf_binary import hgf_binary
from hgfx.models.uhgf_binary import uhgf_binary
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions, QuasiNewtonResult, quasinewton_optim
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

BINARY_VARIANTS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
_CONFIGS = {
    "hgf_binary": hgf_binary_config,
    "ehgf_binary": ehgf_binary_config,
    "uhgf_binary": uhgf_binary_config,
}
_FORWARD = {
    "hgf_binary": hgf_binary,
    "ehgf_binary": ehgf_binary,
    "uhgf_binary": uhgf_binary,
}


@dataclass(frozen=True)
class RecoveryFit:
    model: str
    perceptual_config: ModelConfig
    observation_config: ModelConfig
    optimizer: QuasiNewtonResult
    initial_full: np.ndarray
    final_full: np.ndarray
    free_indices: tuple[int, ...]
    objective: ObjectiveResult
    aic: float
    bic: float

    @property
    def final_free(self) -> np.ndarray:
        return self.final_full[np.asarray(self.free_indices, dtype=np.int64)].copy()


@dataclass(frozen=True)
class ParameterRecoveryRecord:
    model: str
    trial_count: int
    replicate: int
    seed: int
    true_free: np.ndarray
    fitted_free: np.ndarray
    error: np.ndarray
    neg_log_joint: float
    converged: bool


@dataclass(frozen=True)
class ParameterRecoverySummary:
    n: int
    n_parameters: int
    bias: np.ndarray
    rmse: np.ndarray
    correlation: np.ndarray
    convergence_rate: float
    median_absolute_error: np.ndarray


@dataclass(frozen=True)
class ModelRecoveryRecord:
    generating_model: str
    selected_model: str
    trial_count: int
    replicate: int
    seed: int
    bic_by_model: dict[str, float]
    aic_by_model: dict[str, float]


def _variant_components(model: str):
    if model not in _CONFIGS:
        raise ValueError(f"Unsupported recovery model {model!r}; expected one of {BINARY_VARIANTS!r}")
    return _CONFIGS[model], _FORWARD[model]


def _free_indices(prc: ModelConfig, obs: ModelConfig) -> tuple[int, ...]:
    variances = np.concatenate((prc.priorsas, obs.priorsas)).astype(np.float64)
    return tuple(int(i) for i in np.flatnonzero((~np.isnan(variances)) & (variances != 0.0)))


def _objective_for_variant(*, model: str, responses, inputs, full_parameters) -> ObjectiveResult:
    config_factory, forward = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    full = np.asarray(full_parameters, dtype=np.float64).reshape(-1)
    n_prc = len(prc.parameters)
    if full.size != n_prc + len(obs.parameters):
        raise ValueError("full parameter vector has the wrong length")
    return evaluate_objective(
        responses=responses,
        inputs=inputs,
        perceptual_parameters=full[:n_prc],
        observation_parameters=full[n_prc:],
        perceptual_config=prc,
        observation_config=obs,
        perceptual_function=forward,
        observation_function=unitsq_sgm,
        irregular_intervals=bool(prc.options.get("irregular_intervals", False)),
        observation_kwargs={"predorpost": int(obs.options.get("predorpost", 1))},
    )


def fit_binary_variant(
    responses,
    inputs,
    model: str,
    *,
    options: QuasiNewtonOptions | None = None,
    initial_free: Sequence[float] | np.ndarray | None = None,
) -> RecoveryFit:
    """Fit HGF/eHGF/uHGF with the validated objective and compatibility optimizer."""
    config_factory, _ = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    initial_full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    free_indices = _free_indices(prc, obs)
    idx = np.asarray(free_indices, dtype=np.int64)
    start = initial_full[idx].copy() if initial_free is None else np.asarray(
        initial_free, dtype=np.float64
    ).reshape(-1)
    if start.size != len(free_indices):
        raise ValueError(f"Expected {len(free_indices)} free start parameters, got {start.size}")

    def expand(free_parameters) -> np.ndarray:
        free = np.asarray(free_parameters, dtype=np.float64).reshape(-1)
        if free.size != len(free_indices):
            raise ValueError("free parameter vector has the wrong length")
        full = initial_full.copy()
        full[idx] = free
        return full

    def scalar_objective(free_parameters) -> float:
        return float(_objective_for_variant(
            model=model, responses=responses, inputs=inputs,
            full_parameters=expand(free_parameters)
        ).neg_log_joint)

    initial_result = _objective_for_variant(
        model=model, responses=responses, inputs=inputs, full_parameters=expand(start)
    )
    if initial_result.rval != 0 or not np.isfinite(initial_result.neg_log_joint):
        raise RuntimeError(f"Initial recovery fit point is unstable for {model}")

    optimizer = quasinewton_optim(scalar_objective, start, options or QuasiNewtonOptions())
    final_full = expand(optimizer.arg_min)
    objective = _objective_for_variant(
        model=model, responses=responses, inputs=inputs, full_parameters=final_full
    )
    n_free = len(free_indices)
    n_data = max(int(np.sum(~np.isnan(np.asarray(responses, dtype=np.float64).reshape(-1)))), 1)
    aic = float(2.0 * objective.neg_log_likelihood + 2.0 * n_free)
    bic = float(2.0 * objective.neg_log_likelihood + n_free * np.log(n_data))
    return RecoveryFit(
        model=model, perceptual_config=prc, observation_config=obs,
        optimizer=optimizer, initial_full=initial_full, final_full=final_full,
        free_indices=free_indices, objective=objective, aic=aic, bic=bic
    )


def _correlation(true_values: np.ndarray, fitted_values: np.ndarray) -> np.ndarray:
    if true_values.shape != fitted_values.shape or true_values.ndim != 2:
        raise ValueError("recovery arrays must be matching two-dimensional matrices")
    result = np.full(true_values.shape[1], np.nan, dtype=np.float64)
    for column in range(true_values.shape[1]):
        x, y = true_values[:, column], fitted_values[:, column]
        if x.size >= 2 and np.std(x) > 0.0 and np.std(y) > 0.0:
            result[column] = float(np.corrcoef(x, y)[0, 1])
    return result


def summarize_parameter_recovery(
    records: Iterable[ParameterRecoveryRecord],
) -> ParameterRecoverySummary:
    rows = list(records)
    if not rows:
        raise ValueError("at least one parameter recovery record is required")
    truth = np.vstack([row.true_free for row in rows]).astype(np.float64)
    fitted = np.vstack([row.fitted_free for row in rows]).astype(np.float64)
    if truth.shape != fitted.shape:
        raise ValueError("true and fitted parameter matrices must have matching shapes")
    errors = fitted - truth
    return ParameterRecoverySummary(
        n=len(rows),
        n_parameters=truth.shape[1],
        bias=np.mean(errors, axis=0),
        rmse=np.sqrt(np.mean(errors**2, axis=0)),
        correlation=_correlation(truth, fitted),
        convergence_rate=float(np.mean([row.converged for row in rows])),
        median_absolute_error=np.median(np.abs(errors), axis=0),
    )


def deterministic_binary_inputs(trials: int, seed: int) -> np.ndarray:
    if trials < 8:
        raise ValueError("recovery experiments require at least 8 trials")
    rng = np.random.default_rng(seed)
    values = rng.integers(0, 2, size=trials).astype(np.float64)
    values[:4] = np.array([0.0, 1.0, 0.0, 1.0])
    return values


def _truth_vector(
    model: str, inputs, *, replicate: int, scale: float
) -> tuple[np.ndarray, np.ndarray, tuple[int, ...]]:
    config_factory, _ = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    variances = np.concatenate((prc.priorsas, obs.priorsas)).astype(np.float64)
    free_indices = _free_indices(prc, obs)
    idx = np.asarray(free_indices, dtype=np.int64)
    std = np.sqrt(variances[idx])
    phase = np.arange(1, len(free_indices) + 1, dtype=np.float64)
    full[idx] += scale * std * np.sin((replicate + 1.0) * phase * 1.61803398875)
    return full, full[idx].copy(), free_indices


def simulate_binary_variant(
    model: str, inputs, transformed_full_parameters, *, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    config_factory, _ = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    full = np.asarray(transformed_full_parameters, dtype=np.float64).reshape(-1)
    n_prc = len(prc.parameters)
    if full.size != n_prc + len(obs.parameters):
        raise ValueError("full parameter vector has the wrong length")
    result = sim_model(
        inputs, model, prc.transformed_to_native(full[:n_prc]),
        "unitsq_sgm", obs.transformed_to_native(full[n_prc:]), seed=seed
    )
    if result.responses is None or result.response_probabilities is None:
        raise RuntimeError("binary simulation did not produce responses")
    return result.responses, result.response_probabilities


def run_parameter_recovery(
    *, model: str = "hgf_binary", trial_counts: Sequence[int] = (128, 256),
    replicates: int = 4, seed: int = 1800, truth_scale: float = 0.25,
    options: QuasiNewtonOptions | None = None,
) -> list[ParameterRecoveryRecord]:
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    rows: list[ParameterRecoveryRecord] = []
    for trial_count in trial_counts:
        for replicate in range(replicates):
            run_seed = int(seed + int(trial_count) * 100 + replicate)
            inputs = deterministic_binary_inputs(int(trial_count), run_seed)
            truth_full, truth_free, free_indices = _truth_vector(
                model, inputs, replicate=replicate, scale=truth_scale
            )
            responses, _ = simulate_binary_variant(model, inputs, truth_full, seed=run_seed + 1)
            fit = fit_binary_variant(responses, inputs, model, options=options)
            if fit.free_indices != free_indices:
                raise RuntimeError("simulation and fitting free-parameter order diverged")
            fitted = fit.final_free
            rows.append(ParameterRecoveryRecord(
                model=model, trial_count=int(trial_count), replicate=replicate, seed=run_seed,
                true_free=truth_free, fitted_free=fitted, error=fitted - truth_free,
                neg_log_joint=float(fit.objective.neg_log_joint),
                converged=fit.optimizer.termination in {"tol_arg", "tol_grad"},
            ))
    return rows


def fit_candidate_set(
    responses, inputs, *, candidates: Sequence[str] = BINARY_VARIANTS,
    options: QuasiNewtonOptions | None = None,
) -> dict[str, RecoveryFit]:
    if len(set(candidates)) != len(candidates):
        raise ValueError("candidate model names must be unique")
    return {model: fit_binary_variant(responses, inputs, model, options=options) for model in candidates}


def run_model_recovery(
    *, generating_models: Sequence[str] = BINARY_VARIANTS,
    candidates: Sequence[str] = BINARY_VARIANTS, trial_counts: Sequence[int] = (128, 256),
    replicates: int = 2, seed: int = 1810, truth_scale: float = 0.25,
    options: QuasiNewtonOptions | None = None,
) -> list[ModelRecoveryRecord]:
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    rows: list[ModelRecoveryRecord] = []
    for generator_index, generating_model in enumerate(generating_models):
        for trial_count in trial_counts:
            for replicate in range(replicates):
                run_seed = seed + generator_index * 1_000_000 + int(trial_count) * 100 + replicate
                inputs = deterministic_binary_inputs(int(trial_count), run_seed)
                truth_full, _, _ = _truth_vector(
                    generating_model, inputs, replicate=replicate, scale=truth_scale
                )
                responses, _ = simulate_binary_variant(
                    generating_model, inputs, truth_full, seed=run_seed + 1
                )
                fits = fit_candidate_set(responses, inputs, candidates=candidates, options=options)
                bic = {name: float(fit.bic) for name, fit in fits.items()}
                aic = {name: float(fit.aic) for name, fit in fits.items()}
                selected = min(bic, key=bic.get)
                rows.append(ModelRecoveryRecord(
                    generating_model=generating_model, selected_model=selected,
                    trial_count=int(trial_count), replicate=replicate, seed=run_seed,
                    bic_by_model=bic, aic_by_model=aic
                ))
    return rows


def model_recovery_matrix(
    records: Iterable[ModelRecoveryRecord], *, models: Sequence[str] = BINARY_VARIANTS
) -> np.ndarray:
    matrix = np.zeros((len(models), len(models)), dtype=np.float64)
    index = {name: i for i, name in enumerate(models)}
    for row in records:
        if row.generating_model not in index or row.selected_model not in index:
            raise ValueError("record contains a model outside the requested matrix order")
        matrix[index[row.generating_model], index[row.selected_model]] += 1.0
    for row_index in range(matrix.shape[0]):
        total = float(np.sum(matrix[row_index]))
        if total > 0.0:
            matrix[row_index] /= total
    return matrix


__all__ = [
    "BINARY_VARIANTS", "RecoveryFit", "ParameterRecoveryRecord",
    "ParameterRecoverySummary", "ModelRecoveryRecord", "fit_binary_variant",
    "summarize_parameter_recovery", "deterministic_binary_inputs",
    "simulate_binary_variant", "run_parameter_recovery", "fit_candidate_set",
    "run_model_recovery", "model_recovery_matrix",
]
