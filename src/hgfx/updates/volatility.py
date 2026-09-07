"""Volatility-level HGF posterior update (B08)."""

from __future__ import annotations

import numpy as np

from hgfx.math.lambert_w import lambert_w0


def hgf_volatility_update(
    muhat_j: float,
    pihat_j: float,
    ka_jm1: float,
    pihat_jm1: float,
    da_jm1: float,
    mu_prev_j: float,
    om_jm1: float,
    pi_prev_jm1: float,
    pi_jm1: float,
    mu_jm1: float,
    muhat_jm1: float,
    t_k: float,
    update_type: str = "hgf",
) -> tuple[float, float, float, float]:
    """Mirror frozen HGF v8.2.0 ``hgf_volatility_update.m``.

    The HGF/eHGF/uHGF branches are kept in one compatibility implementation,
    matching the frozen source. M4 gates the standard ``hgf`` trajectory; the
    later eHGF/uHGF milestones gate their complete recursive trajectories.
    """
    muhat = np.float64(muhat_j)
    pihat = np.float64(pihat_j)
    ka = np.float64(ka_jm1)
    pihat_lower = np.float64(pihat_jm1)
    da_lower = np.float64(da_jm1)
    mu_prev = np.float64(mu_prev_j)
    om = np.float64(om_jm1)
    pi_prev_lower = np.float64(pi_prev_jm1)
    pi_lower = np.float64(pi_jm1)
    mu_lower = np.float64(mu_jm1)
    muhat_lower = np.float64(muhat_jm1)
    t = np.float64(t_k)

    with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
        v_lower = t * np.exp(ka * mu_prev + om)
        w_lower = v_lower * pihat_lower

        if update_type == "hgf":
            pi = pihat + np.float64(0.5) * ka**2 * w_lower * (
                w_lower + (np.float64(2.0) * w_lower - np.float64(1.0)) * da_lower
            )
            if pi <= 0:
                raise ValueError(
                    "Negative posterior precision. Parameters are in a region "
                    "where model assumptions are violated."
                )
            mu = (
                muhat
                + np.float64(0.5)
                * (np.float64(1.0) / pi)
                * ka
                * w_lower
                * da_lower
            )
            return float(pi), float(mu), float(v_lower), float(w_lower)

        if update_type == "ehgf":
            mu = (
                muhat
                + np.float64(0.5)
                * (np.float64(1.0) / pihat)
                * ka
                * w_lower
                * da_lower
            )
            vv = t * np.exp(ka * mu + om)
            pimhat = np.float64(1.0) / (np.float64(1.0) / pi_prev_lower + vv)
            ww = vv * pimhat
            rr = (vv - np.float64(1.0) / pi_prev_lower) * pimhat
            dd = (
                (np.float64(1.0) / pi_lower + (mu_lower - muhat_lower) ** 2)
                * pimhat
                - np.float64(1.0)
            )
            correction = np.float64(0.5) * ka**2 * ww * (ww + rr * dd)
            pi = pihat + np.maximum(np.float64(0.0), correction)
            return float(pi), float(mu), float(v_lower), float(w_lower)

        if update_type == "uhgf":
            v_lower = t * np.exp(ka * muhat + om)
            if np.isinf(v_lower):
                w_lower = np.float64(1.0)
            else:
                w_lower = np.float64(1.0) / (
                    np.float64(1.0)
                    + np.float64(1.0) / (pi_prev_lower * v_lower)
                )

            pi1 = pihat + np.float64(0.5) * ka**2 * w_lower * (
                np.float64(1.0) - w_lower
            )
            mu1 = (
                muhat
                + np.float64(0.5)
                * (np.float64(1.0) / pi1)
                * ka
                * w_lower
                * da_lower
            )

            al_aux = np.float64(1.0) / pi_prev_lower
            be_aux = np.float64(1.0) / pi_lower + (mu_lower - muhat_lower) ** 2
            gamma_c = np.log(t) + ka * muhat + om
            pihat_y = pihat / ka**2
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
            x_star = (y_star - np.log(t) - om) / ka

            s2 = t * np.exp(ka * x_star + om)
            if np.isinf(s2):
                w2 = np.float64(1.0)
                da2 = np.float64(-1.0)
            else:
                w2 = np.float64(1.0) / (np.float64(1.0) + al_aux / s2)
                da2 = be_aux / (al_aux + s2) - np.float64(1.0)

            pi2 = pihat + np.float64(0.5) * ka**2 * w2 * (
                w2 + (np.float64(2.0) * w2 - np.float64(1.0)) * da2
            )
            if pi2 <= 0:
                pi2 = pihat + np.float64(0.5) * ka**2 * w2 * (
                    np.float64(1.0) - w2
                )
            mu2 = x_star + (
                np.float64(0.5) * ka * w2 * da2
                - pihat * (x_star - muhat)
            ) / pi2

            if not np.isfinite(pi2) or not np.isfinite(mu2):
                pi2 = pi1
                mu2 = mu1

            ey1 = t * np.exp(ka * mu1 + om)
            i1 = (
                -np.float64(0.5) * np.log(al_aux + ey1)
                - np.float64(0.5) * be_aux / (al_aux + ey1)
                - np.float64(0.5) * pihat * (mu1 - muhat) ** 2
            )
            ey2 = t * np.exp(ka * mu2 + om)
            i2 = (
                -np.float64(0.5) * np.log(al_aux + ey2)
                - np.float64(0.5) * be_aux / (al_aux + ey2)
                - np.float64(0.5) * pihat * (mu2 - muhat) ** 2
            )
            blend = np.float64(1.0) / (
                np.float64(1.0) + np.exp(i1 - i2)
            )
            mu = (np.float64(1.0) - blend) * mu1 + blend * mu2
            sig2 = (
                (np.float64(1.0) - blend) / pi1
                + blend / pi2
                + blend * (np.float64(1.0) - blend) * (mu1 - mu2) ** 2
            )
            pi = np.float64(1.0) / sig2
            return float(pi), float(mu), float(v_lower), float(w_lower)

    raise ValueError(
        f"Unknown update type: {update_type}. Must be 'hgf', 'ehgf', or 'uhgf'."
    )
