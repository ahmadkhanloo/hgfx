"""Public fitModel-compatible orchestration over the frozen M8-M10 core."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from hgfx.core.parameters import ModelConfig
from hgfx.core.trials import build_trial_masks
from hgfx.models.hgf_binary import hgf_binary
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

from .configs import hgf_binary_config, unitsq_sgm_config
from .fit_statistics import FitStatistics, fit_statistics
from .fitting import (
    CompatibilityFitResult,
    fit_hgf_binary_unitsq_compat,
    fit_hgf_binary_unitsq_multistart_compat,
)
from .matlab_names import coerce_quasinewton_options, require_model
from .result import CompatibilityResult, MatlabStruct, config_struct, parameter_struct


def _optimizer_struct(
    fit: CompatibilityFitResult,
    stats: FitStatistics,
    *,
    start_full: np.ndarray,
    yhat: np.ndarray,
    residuals: np.ndarray,
) -> MatlabStruct:
    objective = fit.objective
    return MatlabStruct(
        {
            "init": np.asarray(start_full, dtype=np.float64).copy(),
            "final": fit.final_full.copy(),
            "H": stats.hessian.copy(),
            "Sigma": stats.sigma.copy(),
            "Corr": stats.correlation.copy(),
            "trialLogLlsplit": objective.trial_log_likelihoods.copy(),
            "negLl": float(objective.neg_log_likelihood),
            "negLj": float(objective.neg_log_joint),
            "LME": float(stats.lme),
            "decompLME": {
                "logjoint": float(stats.decomposition.logjoint),
                "postpredcorr": float(stats.decomposition.postpredcorr),
                "freepars": float(stats.decomposition.freepars),
            },
            "accu": float(stats.accuracy),
            "comp": float(stats.complexity),
            "iter": {
                "count": int(fit.optimizer.iterations),
                "resets": int(fit.optimizer.resets),
                "termination": fit.optimizer.termination,
            },
            "AIC": float(stats.aic),
            "BIC": float(stats.bic),
            "yhat": yhat.copy(),
            "res": residuals.copy(),
        }
    )


def _optimization_config_struct(options: QuasiNewtonOptions, n_rand_init: int) -> MatlabStruct:
    return MatlabStruct(
        {
            "algorithm": "BFGS quasi-Newton",
            "verbose": bool(options.verbose),
            "tolGrad": float(options.tol_grad),
            "tolArg": float(options.tol_arg),
            "maxStep": float(options.max_step),
            "maxIter": int(options.max_iter),
            "maxRegu": int(options.max_regu),
            "maxRst": int(options.max_rst),
            "nRandInit": int(n_rand_init),
            "seedRandInit": np.nan,
            "optIter": bool(options.opt_iter),
        }
    )


def fit_model(
    responses,
    inputs,
    perceptual_config: str | ModelConfig = "hgf_binary_config",
    observation_config: str | ModelConfig = "unitsq_sgm_config",
    optimization_config: str | Mapping[str, Any] | QuasiNewtonOptions | None = (
        "quasinewton_optim_config"
    ),
    *,
    restart_free_parameters: Sequence[Sequence[float]] | np.ndarray | None = None,
) -> CompatibilityResult:
    """Fit the validated M9 slice and return a MATLAB-style result.

    M13 is an API milestone, not a new inference milestone. Numerical work is
    delegated to the already-validated hgf_binary + unitsq_sgm M8-M10 core.
    """

    require_model(perceptual_config, "hgf_binary", role="perceptual_config")
    require_model(observation_config, "unitsq_sgm", role="observation_config")
    options = coerce_quasinewton_options(optimization_config)

    if restart_free_parameters is None:
        fit = fit_hgf_binary_unitsq_compat(responses, inputs, options=options)
        stats = fit_statistics(fit.problem, fit.optimizer)
        start_full = fit.problem.initial_full.copy()
        n_rand_init = 0
    else:
        restarts = np.asarray(restart_free_parameters, dtype=np.float64)
        fit, stats, best_index = fit_hgf_binary_unitsq_multistart_compat(
            responses,
            inputs,
            restarts,
            options=options,
        )
        if restarts.size:
            restarts = restarts.reshape(-1, len(fit.problem.free_indices))
        else:
            restarts = restarts.reshape(0, len(fit.problem.free_indices))
        selected_free = (
            fit.problem.initial_free
            if best_index == 0
            else np.asarray(restarts[best_index - 1], dtype=np.float64)
        )
        start_full = fit.problem.expand(selected_free)
        n_rand_init = int(restarts.shape[0])

    masks = build_trial_masks(responses, inputs)
    ignored = tuple(int(index) for index in np.flatnonzero(masks.ignored))
    irregular = tuple(int(index) for index in np.flatnonzero(masks.irregular))

    prc = hgf_binary_config().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    trajectory, inf_states = hgf_binary(
        inputs,
        fit.perceptual_transformed,
        transformed=True,
        irregular_intervals=bool(prc.options.get("irregular_intervals", False)),
        ignored_trials=ignored,
    )
    _, yhat, residuals = unitsq_sgm(
        responses,
        inf_states,
        fit.observation_transformed,
        irregular_trials=irregular,
        predorpost=int(obs.options.get("predorpost", 1)),
    )

    p_prc = parameter_struct(
        prc,
        fit.perceptual_native,
        transformed_parameters=fit.perceptual_transformed,
    )
    p_obs = parameter_struct(
        obs,
        fit.observation_native,
        transformed_parameters=fit.observation_transformed,
    )
    optim = _optimizer_struct(
        fit,
        stats,
        start_full=start_full,
        yhat=np.asarray(yhat, dtype=np.float64),
        residuals=np.asarray(residuals, dtype=np.float64),
    )

    return CompatibilityResult(
        kind="fit",
        u=np.asarray(inputs, dtype=np.float64).copy(),
        y=np.asarray(responses, dtype=np.float64).copy(),
        irr=tuple(index + 1 for index in irregular),
        ign=tuple(index + 1 for index in ignored),
        c_prc=config_struct(prc),
        c_obs=config_struct(obs),
        c_opt=_optimization_config_struct(options, n_rand_init),
        p_prc=p_prc,
        p_obs=p_obs,
        traj=MatlabStruct(trajectory),
        optim=optim,
        yhat=np.asarray(yhat, dtype=np.float64).copy(),
        res=np.asarray(residuals, dtype=np.float64).copy(),
    )


fitModel = fit_model

__all__ = ["fit_model", "fitModel"]
