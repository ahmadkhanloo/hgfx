"""Reference workflow adapters over existing validated numerical components.

Scope: official binary/continuous HGF, eHGF, uHGF and RW demo fits.
Matrix IDs C01-C04, P01-P04/P13, O06/O17. Numerical algorithms stay in M8-M10.
"""

import math
from dataclasses import dataclass, replace

import numpy as np

from hgfx.core.parameters import ModelConfig, ParameterSpec
from hgfx.core.priors import optimization_indices
from hgfx.core.transforms import EXPONENTIAL, SIGMOID
from hgfx.core.trials import build_trial_masks
from hgfx.models import ehgf, ehgf_binary, hgf, hgf_binary, rw_binary, uhgf, uhgf_binary
from hgfx.optim.compat_quasinewton import quasinewton_optim
from hgfx.responses.auxiliary import bayes_optimal, bayes_optimal_binary
from hgfx.responses.gaussian import gaussian_obs
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

from . import configs
from .fit_statistics import fit_statistics
from .fitting import CompatibilityFitResult
from .matlab_names import coerce_quasinewton_options, strip_config_suffix
from .objective import evaluate_objective
from .result import CompatibilityResult, MatlabStruct, config_struct, parameter_struct
from .simulation import ehgf_binary_config, uhgf_binary_config


def rw_binary_config():
    return ModelConfig(
        "rw_binary",
        (
            ParameterSpec("logitv_0", "v_0", 1, 0.0, 0.0, SIGMOID, None),
            ParameterSpec("logital", "al", 2, 0.0, 1.0, SIGMOID, None),
        ),
        source_files=("perceptual/rw_binary_config.m",),
    )


def gaussian_obs_config():
    return ModelConfig(
        "gaussian_obs",
        (ParameterSpec("logze", "ze", 1, math.log(0.005), 0.1, EXPONENTIAL, None),),
        source_files=("observation/gaussian_obs_config.m",),
    )


def resolve_config(value):
    if isinstance(value, ModelConfig):
        return value
    name = strip_config_suffix(value)
    if name in ("ehgf", "uhgf"):
        base = configs.hgf_config()
        return replace(base, model=name, options={**base.options, "update_type": name})
    extra = {
        "ehgf_binary": ehgf_binary_config,
        "uhgf_binary": uhgf_binary_config,
        "rw_binary": rw_binary_config,
        "gaussian_obs": gaussian_obs_config,
    }
    if name in extra:
        return extra[name]()
    factory = getattr(configs, name + "_config", None)
    if factory is None:
        raise ValueError(f"Unsupported workflow configuration: {value}")
    return factory()


FORWARDS = {
    "hgf": hgf,
    "ehgf": ehgf,
    "uhgf": uhgf,
    "hgf_binary": hgf_binary,
    "ehgf_binary": ehgf_binary,
    "uhgf_binary": uhgf_binary,
    "rw_binary": rw_binary,
}


def forward_for(config):
    fn = FORWARDS.get(config.model)
    if fn is None:
        raise ValueError(f"Unsupported fitting workflow: {config.model}")

    def forward(inputs, parameters, **kwargs):
        if config.model == "rw_binary":
            kwargs.pop("irregular_intervals", None)
            traj, states = fn(inputs, parameters, **kwargs)
            # MATLAB N-by-1 infStates supports (:,1,1); normalize Python rank.
            return traj, np.asarray(states).reshape(-1, 1, 1)
        return fn(inputs, parameters, **kwargs)

    return forward


def observation_for(config, inputs):
    name = config.model
    if name == "unitsq_sgm":
        return lambda y, s, p, **kw: unitsq_sgm(
            y, s, p, predorpost=config.options.get("predorpost", 1), **kw
        )
    if name == "gaussian_obs":
        return gaussian_obs
    if name in ("Bayes optimal", "Bayes optimal (binary)"):
        fn = bayes_optimal_binary if name.endswith("(binary)") else bayes_optimal
        return lambda y, s, p, **kw: fn(inputs, s, **kw)
    raise ValueError(f"Unsupported observation workflow: {name}")


@dataclass
class WorkflowFitProblem:
    responses: np.ndarray
    inputs: np.ndarray
    prc: ModelConfig
    obs: ModelConfig

    def __post_init__(self):
        self.n_perceptual = len(self.prc.parameters)
        self.initial_full = np.r_[self.prc.priormus, self.obs.priormus]
        self.free_indices = optimization_indices(np.r_[self.prc.priorsas, self.obs.priorsas])
        self.initial_free = self.initial_full[list(self.free_indices)].copy()
        self.forward = forward_for(self.prc)
        self.observation = observation_for(self.obs, self.inputs)

    def expand(self, free):
        free = np.asarray(free, dtype=np.float64).reshape(-1)
        if free.size != len(self.free_indices):
            raise ValueError("Wrong number of free parameters")
        full = self.initial_full.copy()
        full[list(self.free_indices)] = free
        return full

    def evaluate_full(self, full):
        return evaluate_objective(
            responses=self.responses,
            inputs=self.inputs,
            perceptual_parameters=full[: self.n_perceptual],
            observation_parameters=full[self.n_perceptual :],
            perceptual_config=self.prc,
            observation_config=self.obs,
            perceptual_function=self.forward,
            observation_function=self.observation,
            irregular_intervals=bool(self.prc.options.get("irregular_intervals", False)),
        )

    def evaluate_free(self, free):
        return float(self.evaluate_full(self.expand(free)).neg_log_joint)


def fit_workflow(
    responses,
    inputs,
    perceptual_config,
    observation_config,
    optimization_config=None,
    *,
    restart_free_parameters=None,
):
    from .fit import _optimization_config_struct, _optimizer_struct

    prc = resolve_config(perceptual_config).resolve_placeholders(inputs)
    obs = resolve_config(observation_config).resolve_placeholders(inputs)
    y = np.asarray([] if responses is None else responses, dtype=np.float64)
    u = np.asarray(inputs, dtype=np.float64)
    problem = WorkflowFitProblem(y, u, prc, obs)
    options = coerce_quasinewton_options(optimization_config)
    starts = [problem.initial_free]
    if restart_free_parameters is not None:
        restarts = np.asarray(restart_free_parameters, dtype=np.float64)
        if restarts.size:
            starts.extend(restarts.reshape(-1, len(problem.free_indices)))
    best = None
    for start in starts:
        initial = problem.evaluate_full(problem.expand(start))
        if initial.rval or not np.isfinite(initial.neg_log_joint):
            raise RuntimeError("Compatibility start point is not stable.")
        optimizer = quasinewton_optim(problem.evaluate_free, start, options)
        full = problem.expand(optimizer.arg_min)
        objective = problem.evaluate_full(full)
        n = problem.n_perceptual
        fit = CompatibilityFitResult(
            problem,
            optimizer,
            full,
            objective,
            full[:n],
            full[n:],
            prc.transformed_to_native(full[:n]),
            obs.transformed_to_native(full[n:]),
        )
        stats = fit_statistics(problem, optimizer)
        if best is None or stats.lme > best[1].lme:
            best = fit, stats, problem.expand(start)
    fit, stats, start_full = best
    masks = build_trial_masks(y, u)
    ignored = tuple(np.flatnonzero(masks.ignored))
    irregular = tuple(np.flatnonzero(masks.irregular))
    traj, states = problem.forward(
        u,
        fit.perceptual_transformed,
        transformed=True,
        irregular_intervals=bool(prc.options.get("irregular_intervals", False)),
        ignored_trials=ignored,
    )
    _, yhat, res = problem.observation(
        y, states, fit.observation_transformed, irregular_trials=irregular
    )
    optim = _optimizer_struct(fit, stats, start_full=start_full, yhat=yhat, residuals=res)
    return CompatibilityResult(
        kind="fit",
        u=u.copy(),
        y=y.copy(),
        irr=masks.irregular_matlab_indices,
        ign=masks.ignored_matlab_indices,
        c_prc=config_struct(prc),
        c_obs=config_struct(obs),
        c_opt=_optimization_config_struct(options, len(starts) - 1),
        p_prc=parameter_struct(
            prc, fit.perceptual_native, transformed_parameters=fit.perceptual_transformed
        ),
        p_obs=parameter_struct(
            obs, fit.observation_native, transformed_parameters=fit.observation_transformed
        ),
        traj=MatlabStruct(traj),
        optim=optim,
        yhat=yhat,
        res=res,
    )
