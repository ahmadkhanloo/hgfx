"""Python companion to the frozen HGF Toolbox 8.2.0 ``demo/hgf_demo.m``.

The goal of this example is workflow fidelity, not pixel-identical MATLAB
figures.  It follows the official demo sequence with HGFX's public compatibility
API wherever that surface exists.  Two specialized forward-only sections
(three-level continuous HGF and uHGF-AR(1)) use the validated model functions
directly because the MATLAB demo only inspects their trajectories.

Cross-language numerical evidence for each section is indexed in
``docs/user/HGF_DEMO_COVERAGE.md``.  The stochastic MATLAB and NumPy random
streams are intentionally not claimed to be byte-identical; exact oracle gates
inject/export common random drivers where required.
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
from hgfx.models.hgf import hgf
from hgfx.models.hgf_ar1_binary import uhgf_ar1_binary
from hgfx.compat.simulation import simulate_unitsq_sgm
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

    for key in ("binary_recovery_result", "ehgf_fit_result", "uhgf_fit_result", "rw_fit_result"):
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


def run_demo(binary_input: np.ndarray, continuous_input: np.ndarray) -> tuple[dict[str, Any], dict[str, Any]]:
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
    # Python configs are immutable and their flat priors are computed properties.
    # Replacing the ParameterSpec is therefore the direct equivalent of editing
    # logzesa followed by MATLAB align_priors().
    modified_obs = replace(
        binary_obs,
        parameters=(replace(binary_obs.parameters[0], prior_variance=0.5),),
    )
    sample1 = hgfx.sample_model(binary_input, binary_prc, modified_obs, 123)
    sample2 = hgfx.sample_model(binary_input, binary_prc, modified_obs, 456)
    summary["prior_sampling"] = {
        "observation_prior_variance": float(modified_obs.priorsas[0]),
        "seed_123_response_mean": float(np.nanmean(sample1.y)),
        "seed_456_response_mean": float(np.nanmean(sample2.y)),
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
    ar1_traj, ar1_states = uhgf_ar1_binary(binary_input, ar1_parameters, transformed=False)
    ar1_y, _ = simulate_unitsq_sgm(ar1_states, np.asarray([5.0]), seed=123456789)
    summary["uhgf_high_volatility"] = _sim_summary(usim2)
    summary["uhgf_ar1"] = {
        "trials": int(binary_input.shape[0]),
        "level3_max_abs_mu": float(np.nanmax(np.abs(np.asarray(ar1_traj["mu"])[:, 2]))),
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
        np.asarray([1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4], dtype=np.float64),
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
    residual_surface = prepare_residual_diagnostics(est2)
    summary["continuous_hgf_recovery"]["residual_count"] = int(residual_surface["res"].size)
    binary_residual_surface = prepare_residual_diagnostics(est)
    summary["binary_recovery"]["residual_count"] = int(binary_residual_surface["res"].size)
    runtime["continuous_fit_result"] = est2

    print("[13/15] Enhanced continuous HGF simulation and recovery")
    esim2 = hgfx.sim_model(
        continuous_input,
        "ehgf",
        np.asarray([1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4], dtype=np.float64),
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
        np.asarray([1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4], dtype=np.float64),
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
        np.asarray([1.04, 1, 0.0001, 0.1, 0, 0, 1, -14.5, -2.5, 1e4], dtype=np.float64),
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
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON summary path")
    parser.add_argument("--plots", action="store_true", help="Show user-facing matplotlib diagnostics")
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
