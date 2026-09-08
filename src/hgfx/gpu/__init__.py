"""JAX fast-mode execution primitives."""

from .batching import pad_mask, pad_trials, trial_length_bucket
from .compile_cache import CompileSignature, CompilationCache, GLOBAL_COMPILE_CACHE
from .devices import DeviceInfo, available_devices, device_put, has_gpu, select_device
from .engine import (
    FastForwardResult,
    FastObjectiveResult,
    FastObjectiveBatchResult,
    fast_binary_hgf,
    fast_binary_hgf_vmap,
    fast_binary_unitsq_objective,
    fast_binary_unitsq_objective_vmap,
)
from .fitting import (
    BFGSOptimizer,
    BFGSOptions,
    DeviceOptimizer,
    DeviceOptimizerResult,
    FastFitProblem,
    FastFitResult,
    FastValueGradResult,
    fast_binary_unitsq_value_and_grad,
    fit_hgf_binary_unitsq_fast,
    hgf_binary_unitsq_fast_fit_problem,
)

__all__ = [
    "CompileSignature",
    "CompilationCache",
    "GLOBAL_COMPILE_CACHE",
    "DeviceInfo",
    "available_devices",
    "has_gpu",
    "select_device",
    "device_put",
    "trial_length_bucket",
    "pad_trials",
    "pad_mask",
    "FastForwardResult",
    "FastObjectiveResult",
    "FastObjectiveBatchResult",
    "fast_binary_hgf",
    "fast_binary_hgf_vmap",
    "fast_binary_unitsq_objective",
    "fast_binary_unitsq_objective_vmap",
    "FastFitProblem",
    "FastValueGradResult",
    "BFGSOptions",
    "DeviceOptimizerResult",
    "DeviceOptimizer",
    "BFGSOptimizer",
    "FastFitResult",
    "hgf_binary_unitsq_fast_fit_problem",
    "fast_binary_unitsq_value_and_grad",
    "fit_hgf_binary_unitsq_fast",
]
