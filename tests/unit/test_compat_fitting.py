from __future__ import annotations

import numpy as np

from hgfx.compat.fitting import (
    fit_hgf_binary_unitsq_compat,
    hgf_binary_unitsq_fit_problem,
)
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions, quasinewton_optim


def fixture_data() -> tuple[np.ndarray, np.ndarray]:
    inputs = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    responses = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    return responses, inputs


def test_quasinewton_converges_on_quadratic() -> None:
    def objective(x: np.ndarray) -> float:
        return float(
            (x[0] - 0.75) ** 2
            + 2.0 * (x[1] + 1.25) ** 2
            + 0.15 * x[0] * x[1]
        )

    result = quasinewton_optim(
        objective,
        np.array([2.0, -3.0]),
        QuasiNewtonOptions(),
    )
    assert result.val_min < objective(np.array([2.0, -3.0]))
    assert np.isfinite(result.inverse_hessian).all()
    assert result.iterations <= 100


def test_fit_problem_matches_matlab_free_parameter_selection() -> None:
    responses, inputs = fixture_data()
    problem = hgf_binary_unitsq_fit_problem(responses, inputs)

    # Combined MATLAB 1-based free indices are om_2=13, om_3=14, logze=15.
    assert problem.free_indices == (12, 13, 14)
    np.testing.assert_allclose(problem.initial_free, [-3.0, -6.0, np.log(48.0)])

    changed = problem.expand(problem.initial_free + np.array([0.1, -0.2, 0.3]))
    fixed = np.ones(problem.initial_full.size, dtype=bool)
    fixed[list(problem.free_indices)] = False
    np.testing.assert_equal(changed[fixed], problem.initial_full[fixed])


def test_compat_fit_improves_or_preserves_joint_objective() -> None:
    responses, inputs = fixture_data()
    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    initial = problem.evaluate_full(problem.initial_full)

    result = fit_hgf_binary_unitsq_compat(responses, inputs)

    assert result.objective.rval == 0
    assert result.objective.neg_log_joint <= initial.neg_log_joint
    np.testing.assert_allclose(
        result.final_full[list(problem.free_indices)],
        result.optimizer.arg_min,
    )
    assert np.isfinite(result.perceptual_native[problem.free_indices[0]])
    assert np.isfinite(result.observation_native[0])
