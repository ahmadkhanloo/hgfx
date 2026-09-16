"""Python companion to the frozen HGF Toolbox 8.2.0 ``demo/hgf_demo.m``.

This script follows the official demo sequence in Python. Cross-language
numerical equality is established by the dedicated MATLAB-aware validation
workflows indexed in ``docs/user/HGF_DEMO_COVERAGE.md``; this companion checks
that the complete user-facing workflow composes and runs end to end.

MATLAB and NumPy do not guarantee identical RNG streams for the same numeric
seed. For the official ``sampleModel`` demo seeds (123 and 456), HGFX therefore
uses the standard-normal parameter drivers exported by MATLAB in validated D09
evidence. This controls the stochastic input without changing seeds, priors, or
model criteria.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

import hgfx
from hgfx.compat import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.simulation import simulate_unitsq_sgm
from hgfx.models.hgf import hgf
from hgfx.models.hgf_ar1_binary import uhgf_ar1_binary
from hgfx.plotting import (
    fit_plot_corr,
    fit_plot_residual_diagnostics,
    prepare_fit_correlation_surface,
    prepare_residual_diagnostics,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BINARY_INPUT = (
    REPO_ROOT / "external" / "hgf-toolbox" / "demo" / "example_binary_input.txt"
)
DEFAULT_CONTINUOUS_INPUT = (
    REPO_ROOT / "external" / "hgf-toolbox" / "demo" / "example_usdchf.txt"
)

# Frozen MATLAB parameter-draw drivers from D09:
# run 34842943557, artifact 10346184455,
# reference HGF Toolbox 8.2.0 @ 2437f4dc241541072722a2695ddeca7b44d83dd3.
MATLAB_SAMPLE_DRIVERS = {
    123: {
        "prc": np.asarray(
            [
                0.764310937692435,
                -0.6049952538315488,
                -1.0349918070643873,
                0.20140973662758177,
                0.6679770866856835,
                -0.3234871279175406,
                1.3343358777479575,
                0.6214274023833514,
                -0.03294186660521125,
                -0.2950906465860296,
                -0.5548149872398399,
                0.564374164439532,
                -0.13374435858784225,
                -1.675718153292302,
            ],
            dtype=np.float64,
        ),
        "obs": np.asarray([-0.3486661614627253], dtype=np.float64),
    },
    456: {
        "prc": np.asarray(
            [
                -1.6203108643504316,
                -0.6009911918787696,
                0.7106172486950192,
                0.7212535695400398,
                0.22637620517938697,
                0.2521952371757336,
                0.6360318640472987,
                1.1462095372220327,
                -0.5916843987412042,
                -0.9896439213346486,
                -0.1602596632358972,
                -0.4290974010777622,
                0.29452903302794703,
                -0.5219363913863537,
            ],
            dtype=np.float64,
        ),
        "obs": np.asarray([0.1901096754074365], dtype=np.float64),
    },
}


def _load(path: Path, label: str) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found at {path}. Run `git submodule update --init --recursive` "
            "or pass an explicit path."
        )
    return np.asarray(np.loadtxt(path), dtype=np.float64)


def _finite_max_abs(value: Any) -> float:
    array = np.asarray(value, dtype=np.float64)
    finite = array[np.isfinite(array)]
    return float(np.max(np.abs(finite))) if finite.size else float("nan")


def _fit_summary(result) -> dict[str, Any]:
    return {
        "LME": float(result.optim.LME),
        "AIC": float(result.optim.AIC),
        "BIC": float(result.optim.BIC),
        "negLl": float(result.optim.negLl),
        "negLj": float(result.optim.negLj),
        "p_prc": np.asarray(result.p_prc.p, dtype=np.float64).tolist(),
        "p_obs": np.asarray(result.p_obs.p, dtype=np.float64).tolist(),
        "corr_shape": list(np.asarray(result.optim.Corr).shape),
        "sigma_shape": list(np.asarray(result.optim.Sigma).shape),
    }


def _sim_summary(result) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": str(result.c_sim.prc_model),
        "trials": int(np.asarray(result.u).shape[0]),
    }
    if result.traj is not None and hasattr(result.traj, "mu"):
        payload["mu_max_abs"] = _finite_max_abs(result.traj.mu)
    if result.y is not None:
        payload["response_mean"] = float(np.nanmean(np.asarray(result.y, dtype=np.float64)))
    return payload


def _sample_with_matlab_parameter_driver(
    inputs: np.ndarray,
    perceptual_config,
    observation_config,
    seed: int,
):
    driver = MATLAB_SAMPLE_DRIVERS[seed]
    return hgfx.sample_model(
        inputs,
        perceptual_config,
        observation_config,
        seed,
        perceptual_standard_normals=driver["prc"],
        observation_standard_normals=driver["obs"],
    )


def _optional_plots(results: dict[str, Any]) -> None:
    import matplotlib.pyplot as plt

    binary_input = np.asarray(results["_binary_input"], dtype=np.float64)
    fig, ax = plt.subplots()
    ax.plot(np.arange(1, binary_input.size + 1), binary_input, ".")
    ax.set_xlabel("Trial number")
    ax.set_ylabel("u")
    ax.set_xlim(1, binary_input.size)
    ax.set_ylim(-0.1, 1.1)
    ax.set_title("Official binary input")

    for key in (
        "binary_recovery_result",
        "ehgf_fit_result",
        "uhgf_fit_result",
        "rw_fit_result",
    ):
        result = results.get(key)
        if result is not None:
            try:
                fit_plot_corr(result)
            except ValueError:
                pass

    for key in ("continuous_fit_result", "binary_recovery_result"):
        result = results.get(key)
        if result is not None:
            fit_plot_residual_diagnostics(result)

    plt.show()


def run_demo(
    binary_input: np.ndarray,
    continuous_input: np.ndarray,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the computational sequence of frozen ``hgf_demo.m``."""

    hgfx.enable_x64()
    summary: dict[str, Any] = {
        "reference": "HGF Toolbox 8.2.0 @ 2437f4dc241541072722a2695ddeca7b44d83dd3",
        "binary_trials": int(binary_input.shape[0]),
        "continuous_trials": int(continuous_input.shape[0]),
    }
    runtime: dict[str, Any] = {"_binary_input": binary_input}

    print("[1/15] Bayes-optimal binary HGF fit")
    bopars = hgfx.fit_model(
        None,
        binary_input,
        "hgf_binary_config",
        "bayes_optimal_binary_config",
        "quasinewton_optim_config",
    )
    summary["bayes_optimal_binary"] = _fit_summary(bopars)

    print("[2/15] Binary HGF response simulation")
    sim = hgfx.sim_model(
        binary_input,
        "hgf_binary",
        np.asarray(
            [np.nan, 0, 1, np.nan, 1, 1, np.nan, 0, 0, 1, 1, np.nan, -2.5, -6],
            dtype=np.float64,
        ),
        "unitsq_sgm",
        np.asarray([5.0], dtype=np.float64),
        123456789,
    )
    summary["binary_simulation"] = _sim_summary(sim)

    print("[3/15] Recover binary HGF parameters")
    binary_prc = hgf_binary_config()
    binary_obs = unitsq_sgm_config()
    est = hgfx.fit_model(
        sim.y,
        sim.u,
        binary_prc,
        binary_obs,
        "quasinewton_optim_config",
    )
    summary["binary_recovery"] = _fit_summary(est)
    corr = prepare_fit_correlation_surface(est)
    summary["binary_recovery"]["corr_max_abs_offdiag"] = float(
        np.nanmax(np.abs(np.asarray(corr["Corr"]) - np.eye(len(corr["labels"]))))
    )
    runtime["binary_recovery_result"] = est

    print("[4/15] Change observation prior variance and sample from priors")
    modified_obs = replace(
        binary_obs,
        parameters=(replace(binary_obs.parameters[0], prior_variance=0.5),),
    )
    sample1 = _sample_with_matlab_parameter_driver(
        binary_input, binary_prc, modified_obs, 123
    )
    sample2 = _sample_with_matlab_parameter_driver(
        binary_input, binary_prc, modified_obs, 456
    )
    summary["prior_sampling"] = {
        "observation_prior_variance": float(modified_obs.priorsas[0]),
        "seed_123_response_mean": float(np.nanmean(sample1.y)),
        "seed_456_response_mean": float(np.nanmean(sample2.y)),
        "parameter_driver_source": "MATLAB D09 run 34842943557 artifact 10346184455",
    }

    print("[5/15] Enhanced HGF simulation and recovery")
    esim = hgfx.sim_model(
        binary_input,
        "ehgf_binary",
        np.asarray(
            [np.nan, 0, 1, np.nan, 1, 1, np.nan, 0, 0, 1, 1.5, np.nan, -4, 3],
            dtype=np.float64,
        ),
        "unitsq_sgm",
        np.asarray([5.0], dtype=np.float64),
        123456789,
    )
    eest = hgfx.fit_model(
        esim.y,
        esim.u,
        "ehgf_binary_config",
        modified_obs,
        "quasinewton_optim_config",
    )
    summary["ehgf_simulation"] = _sim_summary(esim)
    summary["ehgf_recovery"] = _fit_summary(eest)
    runtime["ehgf_fit_result"] = eest

    print("[6/15] Unbounded HGF simulation and recovery")
    usim = hgfx.sim_model(
        binary_input,
        "uhgf_binary",
        np.asarray(
            [np.nan, 0, 1, np.nan, 1, 1, np.nan, 0, 0, 1, 1, np.nan, -2.5, -6],
            dtype=np.float64,
        ),
        "unitsq_sgm",
        np.asarray([5.0], dtype=np.float64),
        123456789,
    )
    uest = hgfx.fit_model(
        usim.y,
        usim.u,
        "uhgf_binary_config",
        modified_obs,
        "quasinewton_optim_config",
    )
    summary["uhgf_simulation"] = _sim_summary(usim)
    summary["uhgf_recovery"] = _fit_summary(uest)
    runtime["uhgf_fit_result"] = uest

    print("[7/15] uHGF high-volatility and AR(1) regularization")
    usim2 = hgfx.sim_model(
        binary_input,
        "uhgf_binary",
        np.asarray(
            [np.nan, 0, 1, np.nan, 1, 1, np.nan, 0, 0, 1, 1, np.nan, -2.5, 3],
            dtype=np.float64,
        ),
        "unitsq_sgm",
        np.asarray([5.0], dtype=np.float64),
        123456789,
    )
    ar1_parameters = np.asarray(
        [
            np.nan, 0, 1,
            np.nan, 1, 1,
            np.nan, 0, 0.3,
            np.nan, 0, 1,
            np.nan, 0, 0,
            1, 1,
            np.nan, -2.5, 3,
        ],
        dtype=np.float64,
    )
    ar1_traj, ar1_states = uhgf_ar1_binary(
        binary_input, ar1_parameters, transformed=False
    )
    ar1_y, _ = simulate_unitsq_sgm(
        ar1_states, np.asarray([5.0]), seed=123456789
    )
    summary["uhgf_high_volatility"] = _sim_summary(usim2)
    summary["uhgf_ar1"] = {
        "trials": int(binary_input.shape[0]),
        "level3_max_abs_mu": float(
            np.nanmax(np.abs(np.asarray(ar1_traj["mu"])[:, 2]))
        ),
        "response_mean": float(np.nanmean(ar1_y)),
    }

    print("[8/15] Rescorla-Wagner fit to the same simulated binary responses")
    est1a = hgfx.fit_model(
        sim.y,
        sim.u,
        "rw_binary_config",
        "unitsq_sgm_config",
        "quasinewton_optim_config",
    )
    summary["rw_fit"] = _fit_summary(est1a)
    runtime["rw_fit_result"] = est1a

    print("[9/15] Bayes-optimal continuous HGF fit")
    bopars2 = hgfx.fit_model(
        None,
        continuous_input,
        "hgf_config",
        "bayes_optimal_config",
        "quasinewton_optim_config",
    )
    summary["bayes_optimal_continuous"] = _fit_summary(bopars2)

    print("[10/15] Continuous two-level HGF simulation")
    sim2 = hgfx.sim_model(
        continuous_input,
        "hgf",
        np.asarray(
            [1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4],
            dtype=np.float64,
        ),
        "gaussian_obs",
        np.asarray([0.00002], dtype=np.float64),
        123456789,
    )
    summary["continuous_hgf_simulation"] = _sim_summary(sim2)

    print("[11/15] Continuous three-level HGF forward trajectory")
    sim2a_parameters = np.asarray(
        [1.04, 1, 1, 0.0001, 0.1, 0.1, 0, 0, 0, 1, 1, -13, -2, -2, 1e4],
        dtype=np.float64,
    )
    sim2a_traj, _ = hgf(continuous_input, sim2a_parameters, transformed=False)
    summary["continuous_three_level_hgf"] = {
        "trials": int(continuous_input.shape[0]),
        "mu_max_abs": _finite_max_abs(sim2a_traj["mu"]),
        "precision_weight_shape": list(np.asarray(sim2a_traj["wt"]).shape),
    }

    print("[12/15] Recover continuous HGF parameters and residual diagnostics")
    est2 = hgfx.fit_model(
        sim2.y,
        continuous_input,
        "hgf_config",
        "gaussian_obs_config",
        "quasinewton_optim_config",
    )
    summary["continuous_hgf_recovery"] = _fit_summary(est2)
    summary["continuous_hgf_recovery"]["residual_count"] = int(
        prepare_residual_diagnostics(est2)["res"].size
    )
    summary["binary_recovery"]["residual_count"] = int(
        prepare_residual_diagnostics(est)["res"].size
    )
    runtime["continuous_fit_result"] = est2

    print("[13/15] Enhanced continuous HGF simulation and recovery")
    esim2 = hgfx.sim_model(
        continuous_input,
        "ehgf",
        np.asarray(
            [1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4],
            dtype=np.float64,
        ),
        "gaussian_obs",
        np.asarray([0.00002], dtype=np.float64),
        123456789,
    )
    eest2 = hgfx.fit_model(
        esim2.y,
        continuous_input,
        "ehgf_config",
        "gaussian_obs_config",
        "quasinewton_optim_config",
    )
    summary["continuous_ehgf_simulation"] = _sim_summary(esim2)
    summary["continuous_ehgf_recovery"] = _fit_summary(eest2)

    print("[14/15] Unbounded continuous HGF simulation and recovery")
    usim_cont = hgfx.sim_model(
        continuous_input,
        "uhgf",
        np.asarray(
            [1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4],
            dtype=np.float64,
        ),
        "gaussian_obs",
        np.asarray([0.00002], dtype=np.float64),
        123456789,
    )
    uest2 = hgfx.fit_model(
        usim_cont.y,
        continuous_input,
        "uhgf_config",
        "gaussian_obs_config",
        "quasinewton_optim_config",
    )
    summary["continuous_uhgf_simulation"] = _sim_summary(usim_cont)
    summary["continuous_uhgf_recovery"] = _fit_summary(uest2)

    print("[15/15] Bayesian parameter averaging")
    sim2b = hgfx.sim_model(
        continuous_input,
        "hgf",
        np.asarray(
            [1.04, 1, 0.0001, 0.1, 0, 0, 1, -14.5, -2.5, 1e4],
            dtype=np.float64,
        ),
        "gaussian_obs",
        np.asarray([0.00002], dtype=np.float64),
        12345,
    )
    est2b = hgfx.fit_model(
        sim2b.y,
        continuous_input,
        "hgf_config",
        "gaussian_obs_config",
        "quasinewton_optim_config",
    )
    bpa = hgfx.bayesian_parameter_average(est2, est2b)
    summary["bpa"] = {
        "p_prc": np.asarray(bpa.p_prc.p, dtype=np.float64).tolist(),
        "p_obs": np.asarray(bpa.p_obs.p, dtype=np.float64).tolist(),
        "corr_shape": list(np.asarray(bpa.optim.Corr).shape),
        "sigma_shape": list(np.asarray(bpa.optim.Sigma).shape),
    }

    return summary, runtime


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the HGFX Python companion to frozen MATLAB demo/hgf_demo.m."
    )
    parser.add_argument("--binary-input", type=Path, default=DEFAULT_BINARY_INPUT)
    parser.add_argument("--continuous-input", type=Path, default=DEFAULT_CONTINUOUS_INPUT)
    parser.add_argument(
        "--output", type=Path, default=None, help="Optional JSON summary path"
    )
    parser.add_argument(
        "--plots", action="store_true", help="Show user-facing matplotlib diagnostics"
    )
    args = parser.parse_args()

    binary_input = _load(args.binary_input, "Official binary demo input")
    continuous_input = _load(args.continuous_input, "Official USD/CHF demo input")
    summary, runtime = run_demo(binary_input, continuous_input)

    encoded = json.dumps(summary, indent=2, sort_keys=True, allow_nan=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    print("status=HGFX_FULL_HGF_DEMO_COMPLETED")

    if args.plots:
        _optional_plots(runtime)


if __name__ == "__main__":
    main()
