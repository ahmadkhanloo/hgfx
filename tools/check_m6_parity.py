from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.math.lambert_w import lambert_w0
from hgfx.models.uhgf import uhgf
from hgfx.models.uhgf_binary import uhgf_binary
from hgfx.updates.volatility import hgf_volatility_update

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
TRAJ_RTOL = 5e-11
TRAJ_ATOL = 5e-13
DIAG_RTOL = 5e-12
DIAG_ATOL = 5e-14


def _normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(_normalize(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any, *, rtol: float, atol: float) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        raise AssertionError(
            f"{label} shape mismatch: Python={a.shape} MATLAB={e.shape}"
        )
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return
    index = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = float(a[index]) if index else float(a)
    ev = float(e[index]) if index else float(e)
    abs_diff = abs(av - ev)
    scale = max(abs(ev), atol)
    rel_diff = abs_diff / scale
    context = ""
    if index:
        context = f", index={index}"
        if len(index) >= 1:
            context += f", trial={index[0] + 1}"
        if len(index) >= 2:
            context += f", level={index[1] + 1}"
    raise AssertionError(
        f"{label} first divergence{context}: MATLAB={ev:.17g}, "
        f"Python={av:.17g}, abs={abs_diff:.3e}, rel={rel_diff:.3e}, "
        f"rtol={rtol:.1e}, atol={atol:.1e}"
    )


def uhgf_details(args: tuple[float, ...]) -> dict[str, Any]:
    (
        muhat_j,
        pihat_j,
        ka_jm1,
        _pihat_jm1,
        da_jm1,
        _mu_prev_j,
        om_jm1,
        pi_prev_jm1,
        pi_jm1,
        mu_jm1,
        muhat_jm1,
        t_k,
    ) = (np.float64(v) for v in args)

    with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
        v_jm1 = t_k * np.exp(ka_jm1 * muhat_j + om_jm1)
        if np.isinf(v_jm1):
            w_jm1 = np.float64(1.0)
        else:
            w_jm1 = np.float64(1.0) / (
                np.float64(1.0)
                + np.float64(1.0) / (pi_prev_jm1 * v_jm1)
            )

        pi1 = pihat_j + np.float64(0.5) * ka_jm1**2 * w_jm1 * (
            np.float64(1.0) - w_jm1
        )
        mu1 = muhat_j + np.float64(0.5) / pi1 * ka_jm1 * w_jm1 * da_jm1

        al_aux = np.float64(1.0) / pi_prev_jm1
        be_aux = np.float64(1.0) / pi_jm1 + (mu_jm1 - muhat_jm1) ** 2
        gamma_c = np.log(t_k) + ka_jm1 * muhat_j + om_jm1
        pihat_y = pihat_j / ka_jm1**2
        log_w_arg = (
            np.log(be_aux)
            - np.log(np.float64(2.0) * pihat_y)
            + np.float64(0.5) / pihat_y
            - gamma_c
        )
        max_log = np.log(np.finfo(np.float64).max)
        w_arg = np.exp(np.minimum(log_w_arg, max_log))
        v_w = np.float64(lambert_w0(float(w_arg)))
        y_star = gamma_c + v_w - np.float64(0.5) / pihat_y
        x_star = (y_star - np.log(t_k) - om_jm1) / ka_jm1

        s2 = t_k * np.exp(ka_jm1 * x_star + om_jm1)
        if np.isinf(s2):
            w2 = np.float64(1.0)
            da2 = np.float64(-1.0)
        else:
            w2 = np.float64(1.0) / (np.float64(1.0) + al_aux / s2)
            da2 = be_aux / (al_aux + s2) - np.float64(1.0)

        pi2_raw = pihat_j + np.float64(0.5) * ka_jm1**2 * w2 * (
            w2 + (np.float64(2.0) * w2 - np.float64(1.0)) * da2
        )
        pi2 = pi2_raw
        precision_fallback = bool(pi2 <= 0)
        if precision_fallback:
            pi2 = pihat_j + np.float64(0.5) * ka_jm1**2 * w2 * (
                np.float64(1.0) - w2
            )
        mu2 = x_star + (
            np.float64(0.5) * ka_jm1 * w2 * da2
            - pihat_j * (x_star - muhat_j)
        ) / pi2

        nonfinite_fallback = bool(not np.isfinite(pi2) or not np.isfinite(mu2))
        if nonfinite_fallback:
            pi2 = pi1
            mu2 = mu1

        ey1 = t_k * np.exp(ka_jm1 * mu1 + om_jm1)
        i1 = (
            -np.float64(0.5) * np.log(al_aux + ey1)
            - np.float64(0.5) * be_aux / (al_aux + ey1)
            - np.float64(0.5) * pihat_j * (mu1 - muhat_j) ** 2
        )
        ey2 = t_k * np.exp(ka_jm1 * mu2 + om_jm1)
        i2 = (
            -np.float64(0.5) * np.log(al_aux + ey2)
            - np.float64(0.5) * be_aux / (al_aux + ey2)
            - np.float64(0.5) * pihat_j * (mu2 - muhat_j) ** 2
        )
        blend = np.float64(1.0) / (
            np.float64(1.0) + np.exp(i1 - i2)
        )
        final_mu = (np.float64(1.0) - blend) * mu1 + blend * mu2
        final_sig2 = (
            (np.float64(1.0) - blend) / pi1
            + blend / pi2
            + blend * (np.float64(1.0) - blend) * (mu1 - mu2) ** 2
        )
        final_pi = np.float64(1.0) / final_sig2

    public_output = hgf_volatility_update(*args, "uhgf")

    return {
        "v": v_jm1,
        "w": w_jm1,
        "pi1": pi1,
        "mu1": mu1,
        "al_aux": al_aux,
        "be_aux": be_aux,
        "gamma_c": gamma_c,
        "pihat_y": pihat_y,
        "log_w_arg": log_w_arg,
        "max_log": max_log,
        "w_arg": w_arg,
        "v_w": v_w,
        "y_star": y_star,
        "x_star": x_star,
        "s2": s2,
        "w2": w2,
        "da2": da2,
        "pi2_raw": pi2_raw,
        "precision_fallback": precision_fallback,
        "pi2": pi2,
        "mu2": mu2,
        "nonfinite_fallback": nonfinite_fallback,
        "ey1": ey1,
        "i1": i1,
        "ey2": ey2,
        "i2": i2,
        "blend": blend,
        "final_mu": final_mu,
        "final_sig2": final_sig2,
        "final_pi": final_pi,
        "public_output": public_output,
    }


def check_diagnostic_case(name: str, expected: dict[str, Any], args: tuple[float, ...]) -> None:
    actual = uhgf_details(args)
    bool_fields = {"precision_fallback", "nonfinite_fallback"}

    if set(actual) != set(expected):
        raise AssertionError(
            f"{name} diagnostic fields mismatch: "
            f"Python={sorted(actual)} MATLAB={sorted(expected)}"
        )

    for field in sorted(actual):
        if field in bool_fields:
            if bool(actual[field]) != bool(expected[field]):
                raise AssertionError(
                    f"{name}.{field} mismatch: Python={actual[field]} MATLAB={expected[field]}"
                )
            continue
        check(
            f"{name}.{field}",
            actual[field],
            expected[field],
            rtol=DIAG_RTOL,
            atol=DIAG_ATOL,
        )

    check(
        f"{name}.details_vs_public",
        [actual["final_pi"], actual["final_mu"], actual["v"], actual["w"]],
        actual["public_output"],
        rtol=DIAG_RTOL,
        atol=DIAG_ATOL,
    )


def check_trajectory_case(name: str, case: dict[str, Any]) -> None:
    inputs = arr(case["inputs"])
    ptrans = arr(case["ptrans"])
    irregular = bool(case["irregular_intervals"])

    if case["model"] == "uhgf_binary":
        traj, inf_states = uhgf_binary(
            inputs,
            ptrans,
            transformed=True,
            irregular_intervals=irregular,
        )
    elif case["model"] == "uhgf":
        traj, inf_states = uhgf(
            inputs,
            ptrans,
            transformed=True,
            irregular_intervals=irregular,
        )
    else:
        raise AssertionError(f"unknown model in fixture {name}: {case['model']!r}")

    expected_traj = case["traj"]
    if set(traj) != set(expected_traj):
        raise AssertionError(
            f"{name} trajectory fields mismatch: "
            f"Python={sorted(traj)} MATLAB={sorted(expected_traj)}"
        )

    for field in sorted(traj):
        expected = expected_traj[field]
        actual = np.asarray(traj[field])
        if (
            field == "w"
            and actual.ndim == 2
            and actual.shape[1] == 1
            and arr(expected).ndim == 1
            and arr(expected).size == actual.size
        ):
            expected = arr(expected).reshape(actual.shape)
        check(
            f"{name}.traj.{field}",
            actual,
            expected,
            rtol=TRAJ_RTOL,
            atol=TRAJ_ATOL,
        )

    check(
        f"{name}.inf_states",
        inf_states,
        case["inf_states"],
        rtol=TRAJ_RTOL,
        atol=TRAJ_ATOL,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))

    metadata = payload["metadata"]
    if metadata["reference_version"] != "8.2.0":
        raise AssertionError(f"unexpected HGF version: {metadata['reference_version']}")
    if metadata["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError(f"unexpected HGF commit: {metadata['reference_commit']}")
    if metadata["schema_version"] != "m6-1":
        raise AssertionError(f"unexpected fixture schema: {metadata['schema_version']}")

    nominal = (
        0.25, 2.0, 0.7, 3.0, 0.2, 0.1,
        -2.0, 2.5, 3.2, 0.4, 0.35, 1.3,
    )
    extreme = (
        0.2, 1e-4, 1.0, 0.5, 0.3, 0.1,
        -1.0, 1.5, 2.0, 0.4, 0.35, 1.0,
    )
    check_diagnostic_case("diagnostics.nominal", payload["diagnostics"]["nominal"], nominal)
    check_diagnostic_case(
        "diagnostics.logspace_fallback",
        payload["diagnostics"]["logspace_fallback"],
        extreme,
    )

    for name, case in payload["trajectories"].items():
        check_trajectory_case(name, case)

    print("M6 MATLAB/Python uHGF forward parity: PASS")


if __name__ == "__main__":
    main()
