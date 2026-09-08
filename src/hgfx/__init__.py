"""HGFX: GPU-native Hierarchical Gaussian Filter research toolbox."""

from ._config import enable_x64
from .compat.fit import fitModel, fit_model
from .compat.result import CompatibilityResult, MatlabStruct
from .compat.sample import sampleModel, sample_model_result
from .compat.sim import simModel, sim_model_result

# Python-first public spellings. The M11 raw orchestration functions remain
# available as hgfx.compat.sim_model/sample_model for numerical parity tooling.
sim_model = sim_model_result
sample_model = sample_model_result

__all__ = [
    "enable_x64",
    "CompatibilityResult",
    "MatlabStruct",
    "fit_model",
    "sim_model",
    "sample_model",
    "fitModel",
    "simModel",
    "sampleModel",
]
