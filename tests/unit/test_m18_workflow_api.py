from dataclasses import replace
import numpy as np
import pytest
import hgfx
from hgfx.compat.configs import unitsq_sgm_config
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


def test_supplied_prior_is_not_silently_discarded():
    u = np.tile([0.0, 1.0, 0.0, 1.0], 5)
    obs = unitsq_sgm_config()
    obs = replace(
        obs, parameters=(replace(obs.parameters[0], prior_mean=np.log(2), prior_variance=0),)
    )
    est = hgfx.fit_model(
        u, u, observation_config=obs, optimization_config=QuasiNewtonOptions(max_iter=1)
    )
    assert est.p_obs.p[0] == pytest.approx(2.0)
    assert est.c_obs.priorsas[0] == 0


def test_continuous_simulation_exported_driver():
    u = np.linspace(1.0, 1.1, 20)
    p = [1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4]
    sim = hgfx.sim_model(u, "hgf", p, "gaussian_obs", 0.00002, response_normals=np.zeros(20))
    np.testing.assert_array_equal(sim.y, sim.traj.muhat[:, 0])
