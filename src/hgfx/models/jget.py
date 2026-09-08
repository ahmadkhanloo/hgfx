"""Jumping Gaussian estimation task (JGET) HGF family."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from hgfx.updates.precision_prediction import hgf_pihat, hgf_pihat_last
from hgfx.updates.volatility import hgf_volatility_update
from hgfx.updates.volatility_pe import hgf_volatility_pe


def _first_input(inputs) -> np.ndarray:
    arr = np.asarray(inputs, dtype=np.float64)
    if arr.ndim == 1:
        return arr
    if arr.ndim == 2 and arr.shape[1] >= 1:
        return arr[:, 0]
    raise ValueError("JGET inputs must be 1D or a matrix with at least one column")


def hgf_jget_unified(
    inputs,
    parameters,
    *,
    update_type: str,
    transformed: bool = False,
    ignored_trials: Sequence[int] | None = None,
    validate: bool = True,
):
    """Mirror frozen hgf_jget_unified.m."""

    if update_type not in {"hgf", "ehgf", "uhgf"}:
        raise ValueError("update_type must be hgf, ehgf, or uhgf")
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    levels = p.size / 8
    if levels != int(levels) or levels < 2:
        raise ValueError("Cannot determine JGET levels")
    l = int(levels)

    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[3 * l : 4 * l] = np.exp(p[3 * l : 4 * l])
        p[4 * l] = np.exp(p[4 * l])
        p[4 * l + 1 : 5 * l] = np.exp(p[4 * l + 1 : 5 * l])
        p[5 * l : 6 * l - 1] = np.exp(p[5 * l : 6 * l - 1])

    mux0 = p[:l]
    sax0 = p[l : 2 * l]
    mua0 = p[2 * l : 3 * l]
    saa0 = p[3 * l : 4 * l]
    kau = p[4 * l]
    kax = p[4 * l + 1 : 5 * l]
    kaa = p[5 * l : 6 * l - 1]
    omu = p[6 * l - 1]
    omx = p[6 * l : 7 * l]
    oma = p[7 * l : 8 * l]
    thx = np.exp(p[7 * l - 1])
    tha = np.exp(p[8 * l - 1])

    values = _first_input(inputs)
    ignored = np.isnan(values)
    if ignored_trials is not None:
        ignored = ignored.copy()
        for index in ignored_trials:
            if index < 0 or index >= values.size:
                raise IndexError(f"ignored trial index out of range: {index}")
            ignored[index] = True

    u = np.concatenate(([0.0], values))
    n = u.size
    t = np.ones(n, dtype=np.float64)

    mux = np.full((n, l), np.nan)
    pix = np.full((n, l), np.nan)
    mua = np.full((n, l), np.nan)
    pia = np.full((n, l), np.nan)
    muuhat = np.full(n, np.nan)
    piuhat = np.full(n, np.nan)
    muxhat = np.full((n, l), np.nan)
    pixhat = np.full((n, l), np.nan)
    muahat = np.full((n, l), np.nan)
    piahat = np.full((n, l), np.nan)
    daux = np.full(n, np.nan)
    daua = np.full(n, np.nan)
    wx = np.full((n, l - 1), np.nan)
    wa = np.full((n, l - 1), np.nan)
    dax = np.full((n, l), np.nan)
    daa = np.full((n, l), np.nan)

    mux[0] = mux0
    pix[0] = 1.0 / sax0
    mua[0] = mua0
    pia[0] = 1.0 / saa0

    for k in range(1, n):
        trial = k - 1
        if ignored[trial]:
            mux[k] = mux[k - 1]
            mua[k] = mua[k - 1]
            pix[k] = pix[k - 1]
            pia[k] = pia[k - 1]
            muuhat[k] = muuhat[k - 1]
            piuhat[k] = piuhat[k - 1]
            muxhat[k] = muxhat[k - 1]
            muahat[k] = muahat[k - 1]
            pixhat[k] = pixhat[k - 1]
            piahat[k] = piahat[k - 1]
            daux[k] = daux[k - 1]
            daua[k] = daua[k - 1]
            wx[k] = wx[k - 1]
            wa[k] = wa[k - 1]
            dax[k] = dax[k - 1]
            daa[k] = daa[k - 1]
            continue

        muuhat[k] = mux[k - 1, 0]
        piuhat[k] = 1.0 / np.exp(kau * mua[k - 1, 0] + omu)
        daux[k] = u[k] - muuhat[k]

        muxhat[k, 0] = mux[k - 1, 0]
        muahat[k, 0] = mua[k - 1, 0]
        pixhat[k, 0] = hgf_pihat(
            pix[k - 1, 0], t[k], kax[0], mux[k - 1, 1], omx[0]
        )
        piahat[k, 0] = hgf_pihat(
            pia[k - 1, 0], t[k], kaa[0], mua[k - 1, 1], oma[0]
        )
        pix[k, 0] = pixhat[k, 0] + piuhat[k]
        mux[k, 0] = muxhat[k, 0] + piuhat[k] / pix[k, 0] * daux[k]
        daua[k] = (
            (1.0 / pix[k, 0] + (mux[k, 0] - u[k]) ** 2) * piuhat[k] - 1.0
        )
        pia[k, 0] = piahat[k, 0] + 0.5 * kau**2 * (1.0 + daua[k])
        mua[k, 0] = muahat[k, 0] + 0.5 / pia[k, 0] * kau * daua[k]
        dax[k, 0] = hgf_volatility_pe(
            pix[k, 0], mux[k, 0], muxhat[k, 0], pixhat[k, 0]
        )
        daa[k, 0] = hgf_volatility_pe(
            pia[k, 0], mua[k, 0], muahat[k, 0], piahat[k, 0]
        )

        for j in range(1, l - 1):
            muxhat[k, j] = mux[k - 1, j]
            muahat[k, j] = mua[k - 1, j]
            pixhat[k, j] = hgf_pihat(
                pix[k - 1, j], t[k], kax[j], mux[k - 1, j + 1], omx[j]
            )
            piahat[k, j] = hgf_pihat(
                pia[k - 1, j], t[k], kaa[j], mua[k - 1, j + 1], oma[j]
            )
            pix[k, j], mux[k, j], wx[k, j - 1], _ = hgf_volatility_update(
                muxhat[k, j],
                pixhat[k, j],
                kax[j - 1],
                pixhat[k, j - 1],
                dax[k, j - 1],
                mux[k - 1, j],
                omx[j - 1],
                pix[k - 1, j - 1],
                pix[k, j - 1],
                mux[k, j - 1],
                muxhat[k, j - 1],
                t[k],
                update_type,
            )
            pia[k, j], mua[k, j], wa[k, j - 1], _ = hgf_volatility_update(
                muahat[k, j],
                piahat[k, j],
                kaa[j - 1],
                piahat[k, j - 1],
                daa[k, j - 1],
                mua[k - 1, j],
                oma[j - 1],
                pia[k - 1, j - 1],
                pia[k, j - 1],
                mua[k, j - 1],
                muahat[k, j - 1],
                t[k],
                update_type,
            )
            dax[k, j] = hgf_volatility_pe(
                pix[k, j], mux[k, j], muxhat[k, j], pixhat[k, j]
            )
            daa[k, j] = hgf_volatility_pe(
                pia[k, j], mua[k, j], muahat[k, j], piahat[k, j]
            )

        last = l - 1
        muxhat[k, last] = mux[k - 1, last]
        muahat[k, last] = mua[k - 1, last]
        pixhat[k, last] = hgf_pihat_last(pix[k - 1, last], t[k], thx)
        piahat[k, last] = hgf_pihat_last(pia[k - 1, last], t[k], tha)

        pix[k, last], mux[k, last], wx[k, last - 1], _ = hgf_volatility_update(
            muxhat[k, last],
            pixhat[k, last],
            kax[last - 1],
            pixhat[k, last - 1],
            dax[k, last - 1],
            mux[k - 1, last],
            omx[last - 1],
            pix[k - 1, last - 1],
            pix[k, last - 1],
            mux[k, last - 1],
            muxhat[k, last - 1],
            t[k],
            update_type,
        )
        pia[k, last], mua[k, last], wa[k, last - 1], _ = hgf_volatility_update(
            muahat[k, last],
            piahat[k, last],
            kaa[last - 1],
            piahat[k, last - 1],
            daa[k, last - 1],
            mua[k - 1, last],
            oma[last - 1],
            pia[k - 1, last - 1],
            pia[k, last - 1],
            mua[k, last - 1],
            muahat[k, last - 1],
            t[k],
            update_type,
        )
        dax[k, last] = hgf_volatility_pe(
            pix[k, last], mux[k, last], muxhat[k, last], pixhat[k, last]
        )
        daa[k, last] = hgf_volatility_pe(
            pia[k, last], mua[k, last], muahat[k, last], piahat[k, last]
        )

    mux = mux[1:]
    pix = pix[1:]
    mua = mua[1:]
    pia = pia[1:]
    muuhat = muuhat[1:]
    piuhat = piuhat[1:]
    muxhat = muxhat[1:]
    pixhat = pixhat[1:]
    muahat = muahat[1:]
    piahat = piahat[1:]
    wx = wx[1:]
    wa = wa[1:]
    daux = daux[1:]
    daua = daua[1:]
    dax = dax[1:]
    daa = daa[1:]

    if validate and update_type == "hgf":
        for state, precision in ((mux, pix), (mua, pia)):
            if np.any(~np.isfinite(state)) or np.any(~np.isfinite(precision)):
                raise ValueError("Variational approximation invalid")

    with np.errstate(divide="ignore", invalid="ignore"):
        lrx = np.full((values.size, l), np.nan)
        lra = np.full((values.size, l), np.nan)
        lrx[:, 0] = piuhat / pix[:, 0]
        lrx[:, 1:] = (kax / 2.0) * wx / pix[:, 1:]
        lra[:, 0] = 0.5 * kau / pia[:, 0]
        lra[:, 1:] = (kaa / 2.0) * wa / pia[:, 1:]

    traj = {
        "mux": mux,
        "mua": mua,
        "sax": 1.0 / pix,
        "saa": 1.0 / pia,
        "muuhat": muuhat,
        "muxhat": muxhat,
        "muahat": muahat,
        "sauhat": 1.0 / piuhat,
        "saxhat": 1.0 / pixhat,
        "saahat": 1.0 / piahat,
        "wx": wx,
        "wa": wa,
        "daux": daux,
        "daua": daua,
        "dax": dax,
        "daa": daa,
        "lrx": lrx,
        "lra": lra,
    }

    inf_states = np.full((values.size, 1, 10), np.nan, dtype=np.float64)
    inf_states[:, 0, 0] = muuhat
    inf_states[:, 0, 1] = 1.0 / piuhat
    inf_states[:, 0, 2] = muxhat[:, 0]
    inf_states[:, 0, 3] = 1.0 / pixhat[:, 0]
    inf_states[:, 0, 4] = muahat[:, 0]
    inf_states[:, 0, 5] = 1.0 / piahat[:, 0]
    inf_states[:, 0, 6] = mux[:, 0]
    inf_states[:, 0, 7] = 1.0 / pix[:, 0]
    inf_states[:, 0, 8] = mua[:, 0]
    inf_states[:, 0, 9] = 1.0 / pia[:, 0]
    return traj, inf_states


def hgf_jget(inputs, parameters, **kwargs):
    return hgf_jget_unified(inputs, parameters, update_type="hgf", **kwargs)


def ehgf_jget(inputs, parameters, **kwargs):
    return hgf_jget_unified(inputs, parameters, update_type="ehgf", **kwargs)


def uhgf_jget(inputs, parameters, **kwargs):
    return hgf_jget_unified(inputs, parameters, update_type="uhgf", **kwargs)
