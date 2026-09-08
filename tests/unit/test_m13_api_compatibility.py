from __future__ import annotations

import numpy as np

import hgfx
from hgfx.compat import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.result import CompatibilityResult, MatlabStruct
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


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


def native_hgf_parameters() -> np.ndarray:
    config = hgf_binary_config()
    ptrans = config.priormus.copy()
    ptrans[12] = -2.7
    ptrans[13] = -5.4
    return config.transformed_to_native(ptrans)


def test_matlab_struct_is_mapping_and_attribute_accessible() -> None:
    value = MatlabStruct({"outer": {"x": np.array([1.0, 2.0])}, "name": "demo"})
    assert value["name"] == "demo"
    np.testing.assert_array_equal(value.outer.x, [1.0, 2.0])

    exported = value.to_dict()
    assert isinstance(exported["outer"], dict)
    exported["outer"]["x"][0] = 99.0
    assert value.outer.x[0] == 1.0


def test_simmodel_public_api_preserves_matlab_fields_and_one_based_ign() -> None:
    inputs = np.array([0.0, 1.0, np.nan, 0.0, 1.0, 0.0])
    uniforms = np.linspace(0.05, 0.95, inputs.size, endpoint=False)

    result = hgfx.simModel(
        inputs,
        "hgf_binary",
        native_hgf_parameters(),
        "unitsq_sgm",
        np.array([12.0]),
        123,
        response_uniforms=uniforms,
    )

    assert isinstance(result, CompatibilityResult)
    assert result.kind == "sim"
    assert result.ign == (3,)
    assert result.c_sim.prc_model == "hgf_binary"
    assert result.c_sim.obs_model == "unitsq_sgm"
    assert result.c_sim.seed == 123
    assert result.p_prc.p.shape == (14,)
    assert result.p_obs.p.shape == (1,)
    assert result.traj.mu.shape[0] == inputs.size
    assert result.y is not None
    assert result.yhat is not None

    exported = result.to_dict(matlab_style=True)
    assert set(("u", "ign", "c_sim", "p_prc", "traj", "y", "yhat")) <= set(exported)
    assert exported["ign"] == (3,)


def test_samplemodel_public_api_exposes_transformed_and_native_parameter_vectors() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 0.0])
    prc = hgf_binary_config()
    obs = unitsq_sgm_config()
    z_prc = np.zeros(len(prc.parameters), dtype=np.float64)
    z_obs = np.zeros(len(obs.parameters), dtype=np.float64)

    result = hgfx.sampleModel(
        inputs,
        prc,
        obs,
        7,
        perceptual_standard_normals=z_prc,
        observation_standard_normals=z_obs,
        response_uniforms=np.linspace(0.05, 0.95, inputs.size, endpoint=False),
    )

    assert result.kind == "sample"
    assert result.p_prc is not None
    assert result.p_obs is not None
    assert result.p_prc.p.shape == result.p_prc.ptrans.shape
    assert result.p_obs.p.shape == result.p_obs.ptrans.shape
    assert "yhat" not in result.to_dict(matlab_style=True)


def test_fitmodel_result_supports_legacy_downstream_access_and_export() -> None:
    responses, inputs = fixture_data()
    result = hgfx.fitModel(
        responses,
        inputs,
        "hgf_binary_config",
        "unitsq_sgm_config",
        QuasiNewtonOptions(max_iter=2),
    )

    assert result.kind == "fit"
    assert result.irr == ()
    assert result.ign == ()
    assert result.p_prc is not None
    assert result.p_obs is not None
    assert result.traj is not None
    assert result.optim is not None
    assert result.yhat is not None
    assert result.res is not None

    def legacy_consumer(est: CompatibilityResult) -> tuple[int, float, float]:
        return est.traj.mu.shape[0], float(est.p_prc.om[-1]), float(est.optim.LME)

    n_trials, omega3, lme = legacy_consumer(result)
    assert n_trials == inputs.size
    assert np.isfinite(omega3)
    assert np.isfinite(lme)

    matlab = result.to_dict(matlab_style=True)
    assert "yhat" not in matlab
    assert "res" not in matlab
    assert "yhat" in matlab["optim"]
    assert "res" in matlab["optim"]
    np.testing.assert_allclose(matlab["p_prc"]["ptrans"], result.p_prc.ptrans)
    np.testing.assert_allclose(matlab["optim"]["yhat"], result.yhat, equal_nan=True)

    python_style = result.to_dict(matlab_style=False)
    assert "yhat" in python_style
    assert "res" in python_style


def test_public_snake_case_and_matlab_aliases_are_both_available() -> None:
    assert hgfx.fit_model is hgfx.fitModel
    assert hgfx.sim_model is not None
    assert hgfx.sample_model is not None
    assert hgfx.simModel is not None
    assert hgfx.sampleModel is not None
