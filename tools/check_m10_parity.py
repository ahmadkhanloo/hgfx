from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.fit_statistics import finalize_laplace_statistics, fit_statistics
from hgfx.compat.fitting import (
    fit_hgf_binary_unitsq_compat,
    fit_hgf_binary_unitsq_multistart_compat,
    hgf_binary_unitsq_fit_problem,
)

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(normalize(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any, *, rtol=2e-6, atol=2e-8) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        if a.size == e.size:
            a = a.reshape(-1)
            e = e.reshape(-1)
        else:
            raise AssertionError(f"{label} shape mismatch: Python={a.shape}, MATLAB={e.shape}")
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return
    bad = np.argwhere(~close)
    index = tuple(int(i) for i in bad[0]) if bad.size else ()
    av = float(a[index]) if index else float(a)
    ev = float(e[index]) if index else float(e)
    raise AssertionError(
        f"{label} divergence index={index}: MATLAB={ev:.17g}, "
        f"Python={av:.17g}, abs={abs(av-ev):.3e}"
    )


def check_default_fit(payload: dict[str, Any]) -> None:
    f = payload["fit"]
    responses = arr(f["responses"])
    inputs = arr(f["inputs"])

    fit = fit_hgf_binary_unitsq_compat(responses, inputs)
    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    stats = fit_statistics(problem, fit.optimizer)

    check("fit.final", fit.final_full, f["final"], rtol=3e-8, atol=3e-10)
    check("fit.H", stats.hessian, f["H"])
    check("fit.Sigma", stats.sigma, f["Sigma"], rtol=5e-6, atol=5e-8)
    check("fit.Corr", stats.correlation, f["Corr"], rtol=5e-6, atol=5e-8)
    check("fit.negLl", fit.objective.neg_log_likelihood, f["negLl"], rtol=3e-8, atol=3e-10)
    check("fit.negLj", fit.objective.neg_log_joint, f["negLj"], rtol=3e-8, atol=3e-10)
    check("fit.LME", stats.lme, f["LME"])
    check("fit.decomp.logjoint", stats.decomposition.logjoint, f["decompLME"]["logjoint"])
    check(
        "fit.decomp.postpredcorr",
        stats.decomposition.postpredcorr,
        f["decompLME"]["postpredcorr"],
    )
    check("fit.decomp.freepars", stats.decomposition.freepars, f["decompLME"]["freepars"])
    check("fit.accu", stats.accuracy, f["accu"])
    check("fit.comp", stats.complexity, f["comp"])
    check("fit.AIC", stats.aic, f["AIC"])
    check("fit.BIC", stats.bic, f["BIC"])


def check_fallback(payload: dict[str, Any]) -> None:
    f = payload["fallback"]
    stats = finalize_laplace_statistics(
        val_min=5.0,
        neg_log_likelihood=4.0,
        numerical_hessian=np.array([[1.0, 0.0], [0.0, -0.25]], dtype=np.float64),
        inverse_hessian_from_optimizer=np.array(
            [[0.5, 0.02], [0.02, 0.25]], dtype=np.float64
        ),
        n_data_points=20,
    )
    if not stats.used_optimizer_hessian:
        raise AssertionError("fallback oracle did not use optimizer inverse Hessian")
    check("fallback.H", stats.hessian, f["H"], rtol=2e-12, atol=2e-14)
    check("fallback.Sigma", stats.sigma, f["Sigma"], rtol=2e-12, atol=2e-14)
    check("fallback.Corr", stats.correlation, f["Corr"], rtol=2e-12, atol=2e-14)
    check("fallback.LME", stats.lme, f["LME"], rtol=2e-12, atol=2e-14)
    check("fallback.logjoint", stats.decomposition.logjoint, f["logjoint"])
    check("fallback.postpredcorr", stats.decomposition.postpredcorr, f["postpredcorr"])
    check("fallback.freepars", stats.decomposition.freepars, f["freepars"])
    check("fallback.accu", stats.accuracy, f["accu"])
    check("fallback.comp", stats.complexity, f["comp"])
    check("fallback.AIC", stats.aic, f["AIC"])
    check("fallback.BIC", stats.bic, f["BIC"])


def check_multistart(payload: dict[str, Any]) -> None:
    f = payload["fit"]
    m = payload["multistart"]
    best_fit, best_stats, best_index = fit_hgf_binary_unitsq_multistart_compat(
        arr(f["responses"]),
        arr(f["inputs"]),
        arr(m["restart_free_parameters"]),
    )
    if best_index < 0 or best_index > int(m["nRandInit"]):
        raise AssertionError(f"invalid selected restart index {best_index}")
    check("multistart.final", best_fit.final_full, m["final"], rtol=8e-7, atol=8e-9)
    check("multistart.LME", best_stats.lme, m["LME"], rtol=8e-6, atol=8e-8)
    check(
        "multistart.negLj",
        best_fit.objective.neg_log_joint,
        m["negLj"],
        rtol=8e-7,
        atol=8e-9,
    )
    check("multistart.H", best_stats.hessian, m["H"], rtol=1e-5, atol=1e-7)
    check("multistart.Sigma", best_stats.sigma, m["Sigma"], rtol=1e-5, atol=1e-7)
    check("multistart.Corr", best_stats.correlation, m["Corr"], rtol=1e-5, atol=1e-7)
    check("multistart.AIC", best_stats.aic, m["AIC"], rtol=8e-7, atol=8e-9)
    check("multistart.BIC", best_stats.bic, m["BIC"], rtol=8e-7, atol=8e-9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    md = payload["metadata"]
    if md["reference_version"] != "8.2.0":
        raise AssertionError(f"unexpected HGF version: {md['reference_version']}")
    if md["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError(f"unexpected HGF commit: {md['reference_commit']}")
    if md["schema_version"] != "m10-1":
        raise AssertionError(f"unexpected fixture schema: {md['schema_version']}")

    check_default_fit(payload)
    check_fallback(payload)
    check_multistart(payload)
    print("M10 MATLAB/Python Hessian/LME parity: PASS")


if __name__ == "__main__":
    main()
