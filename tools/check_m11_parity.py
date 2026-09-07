from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat import hgf_binary_config, sample_model, sim_model, unitsq_sgm_config

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
RTOL = 3e-10
ATOL = 3e-12


def norm(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [norm(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(norm(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        if a.size == e.size:
            e = e.reshape(a.shape)
        else:
            raise AssertionError(f"{label} shape: Python={a.shape} MATLAB={e.shape}")
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(close):
        return
    index = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = float(a[index]) if index else float(a)
    ev = float(e[index]) if index else float(e)
    raise AssertionError(
        f"{label} first divergence index={index}: "
        f"MATLAB={ev:.17g}, Python={av:.17g}, abs={abs(av-ev):.3e}"
    )


def sampled_prc_config():
    config = hgf_binary_config()
    parameters = list(config.parameters)
    parameters[12] = replace(parameters[12], prior_variance=0.01)
    parameters[13] = replace(parameters[13], prior_variance=0.01)
    return replace(config, parameters=tuple(parameters))


def check_sim_case(payload: dict[str, Any]) -> None:
    case = payload["sim"]
    inputs = arr(case["inputs"]).reshape(-1)
    p_prc = arr(case["p_prc"]).reshape(-1)
    p_obs = arr(case["p_obs"]).reshape(-1)
    uniforms = arr(case["exported_uniforms"]).reshape(-1)

    result = sim_model(
        inputs,
        "hgf_binary",
        p_prc,
        "unitsq_sgm",
        p_obs,
        seed=int(case["seed"]),
        response_uniforms=uniforms,
    )

    matlab_ignored = tuple(int(x) - 1 for x in arr(case["ignored_matlab"]).reshape(-1))
    if result.ignored_trials != matlab_ignored:
        raise AssertionError(
            f"ignored trials differ: Python={result.ignored_trials} MATLAB={matlab_ignored}"
        )

    check("sim.infStates", result.inf_states, case["infStates"])
    check("sim.probability", result.response_probabilities, case["probability"])
    check("sim.exported_uniform_responses", result.responses, case["exported_uniform_responses"])

    for field in ("mu", "sa", "muhat", "sahat", "da"):
        check(f"sim.traj.{field}", result.trajectory[field], case["traj"][field])

    # Explicitly prove the frozen simModel quirk: full perceptual states keep
    # ignored rows, but returned muhat/sahat have those rows deleted.
    check("sim.full_muhat", result.inf_states[:, :, 0], case["full_muhat"])
    check("sim.full_sahat", result.inf_states[:, :, 1], case["full_sahat"])
    if result.trajectory["muhat"].shape[0] != inputs.size - len(result.ignored_trials):
        raise AssertionError("simModel ignored-row trimming semantics were not preserved")

    matlab_y = arr(case["responses"]).reshape(-1)
    if matlab_y.size != inputs.size or not np.all(np.isin(matlab_y, [0.0, 1.0])):
        raise AssertionError("MATLAB simModel response evidence is not binary/shape-correct")


def check_sample_case(payload: dict[str, Any]) -> None:
    case = payload["sample"]
    inputs = arr(case["inputs"]).reshape(-1)
    z_prc = arr(case["prc_standard_normals"]).reshape(-1)
    z_obs = arr(case["obs_standard_normals"]).reshape(-1)

    result = sample_model(
        inputs,
        sampled_prc_config(),
        unitsq_sgm_config(),
        seed=int(case["seed"]),
        perceptual_standard_normals=z_prc,
        observation_standard_normals=z_obs,
        # responses are intentionally not cross-language gated
        response_uniforms=np.linspace(0.03, 0.97, inputs.size),
    )

    check("sample.p_prc_trans", result.perceptual_transformed_parameters, case["p_prc_trans"])
    check("sample.p_prc", result.perceptual_parameters, case["p_prc"])
    check("sample.p_obs_trans", result.observation_transformed_parameters, case["p_obs_trans"])
    check("sample.p_obs", result.observation_parameters, case["p_obs"])

    for field in ("mu", "sa", "muhat", "sahat", "da"):
        check(f"sample.traj.{field}", result.trajectory[field], case["traj"][field])

    if result.trajectory["muhat"].shape[0] != inputs.size:
        raise AssertionError("sampleModel must not inherit simModel's ignored-row trimming")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    metadata = payload["metadata"]
    assert metadata["schema_version"] == "m11-1"
    assert metadata["reference_version"] == "8.2.0"
    assert metadata["reference_commit"] == REFERENCE_COMMIT

    check_sim_case(payload)
    check_sample_case(payload)
    print("M11 MATLAB/Python simulation parity: PASS")


if __name__ == "__main__":
    main()
