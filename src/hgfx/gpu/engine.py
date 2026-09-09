"""JAX fast-mode forward and objective engine for binary HGF models.

The M14 path is intentionally separate from compatibility orchestration. Trial
recursion is expressed with jax.lax.scan and compiled by an explicit HGFX
signature. Scientific semantics are cross-validated against M4-M8 compatibility
oracles before this path is used by later GPU fitting milestones.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Literal

import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp
from jax import lax

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config

from .batching import pad_mask, pad_trials, trial_length_bucket
from .compile_cache import CompileSignature, GLOBAL_COMPILE_CACHE

UpdateType = Literal["hgf", "ehgf", "uhgf"]


@dataclass(frozen=True)
class FastForwardResult:
    trajectory: dict[str, jax.Array]
    inf_states: jax.Array
    valid: jax.Array
    n_trials: int
    bucket: int


@dataclass(frozen=True)
class FastObjectiveResult:
    trial_log_likelihoods: jax.Array
    log_likelihood: jax.Array
    neg_log_likelihood: jax.Array
    perceptual_prior: jax.Array
    observation_prior: jax.Array
    neg_log_joint: jax.Array
    rval: jax.Array


@dataclass(frozen=True)
class FastObjectiveBatchResult:
    trial_log_likelihoods: jax.Array
    log_likelihood: jax.Array
    neg_log_likelihood: jax.Array
    perceptual_prior: jax.Array
    observation_prior: jax.Array
    neg_log_joint: jax.Array
    rval: jax.Array


def _lambert_w0(z):
    z = jnp.asarray(z, dtype=jnp.float64)

    def positive(value):
        def regular(_):
            w0 = lax.cond(
                value > 3.0,
                lambda __: jnp.log(value) - jnp.log(jnp.log(value)),
                lambda __: jnp.float64(1.0),
                operand=None,
            )

            def body(_, w):
                ew = jnp.exp(w)
                f = w * ew - value
                fp = ew * (1.0 + w)
                fpp = ew * (2.0 + w)
                return w - (2.0 * f * fp) / (2.0 * fp * fp - f * fpp)

            return lax.fori_loop(0, 8, body, w0)

        return lax.cond(value < 1e-10, lambda _: value, regular, operand=None)

    return lax.cond(z < 0.0, lambda _: jnp.nan, positive, operand=z)


def _volatility_update(
    muhat,
    pihat,
    ka,
    pihat_lower,
    da_lower,
    mu_prev,
    om,
    pi_prev_lower,
    pi_lower,
    mu_lower,
    muhat_lower,
    t,
    *,
    update_type: UpdateType,
):
    v_lower = t * jnp.exp(ka * mu_prev + om)
    w_lower = v_lower * pihat_lower

    if update_type == "hgf":
        pi = pihat + 0.5 * ka**2 * w_lower * (
            w_lower + (2.0 * w_lower - 1.0) * da_lower
        )
        mu = muhat + 0.5 * (1.0 / pi) * ka * w_lower * da_lower
        return pi, mu, v_lower, w_lower, pi > 0.0

    if update_type == "ehgf":
        mu = muhat + 0.5 * (1.0 / pihat) * ka * w_lower * da_lower
        vv = t * jnp.exp(ka * mu + om)
        pimhat = 1.0 / (1.0 / pi_prev_lower + vv)
        ww = vv * pimhat
        rr = (vv - 1.0 / pi_prev_lower) * pimhat
        dd = (1.0 / pi_lower + (mu_lower - muhat_lower) ** 2) * pimhat - 1.0
        correction = 0.5 * ka**2 * ww * (ww + rr * dd)
        pi = pihat + jnp.maximum(0.0, correction)
        return pi, mu, v_lower, w_lower, jnp.bool_(True)

    if update_type != "uhgf":
        raise ValueError(f"unsupported update_type: {update_type}")

    v_lower = t * jnp.exp(ka * muhat + om)
    w_lower = jnp.where(
        jnp.isinf(v_lower),
        1.0,
        1.0 / (1.0 + 1.0 / (pi_prev_lower * v_lower)),
    )
    pi1 = pihat + 0.5 * ka**2 * w_lower * (1.0 - w_lower)
    mu1 = muhat + 0.5 * (1.0 / pi1) * ka * w_lower * da_lower

    al_aux = 1.0 / pi_prev_lower
    be_aux = 1.0 / pi_lower + (mu_lower - muhat_lower) ** 2
    gamma_c = jnp.log(t) + ka * muhat + om
    pihat_y = pihat / ka**2
    log_w_arg = (
        jnp.log(be_aux)
        - jnp.log(2.0 * pihat_y)
        + 0.5 / pihat_y
        - gamma_c
    )
    max_log = jnp.log(jnp.finfo(jnp.float64).max)
    w_arg = jnp.exp(jnp.minimum(log_w_arg, max_log))
    v_w = _lambert_w0(w_arg)
    y_star = gamma_c + v_w - 0.5 / pihat_y
    x_star = (y_star - jnp.log(t) - om) / ka

    s2 = t * jnp.exp(ka * x_star + om)
    w2 = jnp.where(jnp.isinf(s2), 1.0, 1.0 / (1.0 + al_aux / s2))
    da2 = jnp.where(jnp.isinf(s2), -1.0, be_aux / (al_aux + s2) - 1.0)
    pi2 = pihat + 0.5 * ka**2 * w2 * (
        w2 + (2.0 * w2 - 1.0) * da2
    )
    pi2 = jnp.where(
        pi2 <= 0.0,
        pihat + 0.5 * ka**2 * w2 * (1.0 - w2),
        pi2,
    )
    mu2 = x_star + (
        0.5 * ka * w2 * da2 - pihat * (x_star - muhat)
    ) / pi2

    bad_second = ~(jnp.isfinite(pi2) & jnp.isfinite(mu2))
    pi2 = jnp.where(bad_second, pi1, pi2)
    mu2 = jnp.where(bad_second, mu1, mu2)

    ey1 = t * jnp.exp(ka * mu1 + om)
    i1 = (
        -0.5 * jnp.log(al_aux + ey1)
        - 0.5 * be_aux / (al_aux + ey1)
        - 0.5 * pihat * (mu1 - muhat) ** 2
    )
    ey2 = t * jnp.exp(ka * mu2 + om)
    i2 = (
        -0.5 * jnp.log(al_aux + ey2)
        - 0.5 * be_aux / (al_aux + ey2)
        - 0.5 * pihat * (mu2 - muhat) ** 2
    )
    blend = 1.0 / (1.0 + jnp.exp(i1 - i2))
    mu = (1.0 - blend) * mu1 + blend * mu2
    sig2 = (
        (1.0 - blend) / pi1
        + blend / pi2
        + blend * (1.0 - blend) * (mu1 - mu2) ** 2
    )
    pi = 1.0 / sig2
    valid = jnp.isfinite(pi) & jnp.isfinite(mu) & (pi > 0.0)
    return pi, mu, v_lower, w_lower, valid


def _binary_forward_impl(
    inputs,
    parameters,
    ignored,
    *,
    update_type: UpdateType,
    transformed: bool,
    irregular_intervals: bool,
):
    x = jnp.asarray(inputs, dtype=jnp.float64)
    p = jnp.asarray(parameters, dtype=jnp.float64).reshape(-1)
    ignored = jnp.asarray(ignored, dtype=jnp.bool_)

    if x.ndim == 1:
        if irregular_intervals:
            raise ValueError("irregular_intervals=True requires a 2D input matrix")
        values = x
        times = jnp.ones(values.shape[0], dtype=jnp.float64)
    elif x.ndim == 2:
        values = x[:, 0]
        times = x[:, -1] if irregular_intervals else jnp.ones(x.shape[0], dtype=jnp.float64)
    else:
        raise ValueError("inputs must be a 1D sequence or 2D matrix")

    levels = (p.shape[0] + 1) // 5
    if 5 * levels - 1 != p.shape[0] or levels < 3:
        raise ValueError("Cannot determine a valid binary HGF level count")

    if transformed:
        p = p.at[levels : 2 * levels].set(jnp.exp(p[levels : 2 * levels]))
        p = p.at[3 * levels : 4 * levels - 1].set(
            jnp.exp(p[3 * levels : 4 * levels - 1])
        )

    mu_0 = p[0:levels]
    sa_0 = p[levels : 2 * levels]
    rho = p[2 * levels : 3 * levels]
    ka = p[3 * levels : 4 * levels - 1]
    om = p[4 * levels - 1 : 5 * levels - 2]
    theta = jnp.exp(p[5 * levels - 2])

    mu_init = jnp.full((levels,), jnp.nan, dtype=jnp.float64)
    pi_init = jnp.full((levels,), jnp.nan, dtype=jnp.float64)
    mu_init = mu_init.at[0].set(jax.nn.sigmoid(mu_0[0]))
    pi_init = pi_init.at[0].set(jnp.inf)
    mu_init = mu_init.at[1:].set(mu_0[1:])
    pi_init = pi_init.at[1:].set(1.0 / sa_0[1:])

    muhat_init = jnp.full((levels,), jnp.nan, dtype=jnp.float64)
    pihat_init = jnp.full((levels,), jnp.nan, dtype=jnp.float64)
    v_init = jnp.full((levels,), jnp.nan, dtype=jnp.float64)
    w_init = jnp.full((levels - 1,), jnp.nan, dtype=jnp.float64)
    da_init = jnp.full((levels,), jnp.nan, dtype=jnp.float64)

    initial = (
        mu_init,
        pi_init,
        muhat_init,
        pihat_init,
        v_init,
        w_init,
        da_init,
        jnp.bool_(True),
    )

    def step(carry, trial):
        mu_prev, pi_prev, muhat_prev, pihat_prev, v_prev, w_prev, da_prev, valid_prev = carry
        u_k, t_k, ignored_k = trial

        def copy_branch(_):
            return carry

        def update_branch(_):
            mu = jnp.full_like(mu_prev, jnp.nan)
            pi = jnp.full_like(pi_prev, jnp.nan)
            muhat = jnp.full_like(muhat_prev, jnp.nan)
            pihat = jnp.full_like(pihat_prev, jnp.nan)
            v = jnp.full_like(v_prev, jnp.nan)
            w = jnp.full_like(w_prev, jnp.nan)
            da = jnp.full_like(da_prev, jnp.nan)
            valid = valid_prev

            muhat2 = mu_prev[1] + t_k * rho[1]
            muhat = muhat.at[1].set(muhat2)
            muhat1 = jnp.clip(jax.nn.sigmoid(ka[0] * muhat2), 0.001, 0.999)
            pihat1 = 1.0 / (muhat1 * (1.0 - muhat1))
            mu = mu.at[0].set(u_k)
            pi = pi.at[0].set(jnp.inf)
            muhat = muhat.at[0].set(muhat1)
            pihat = pihat.at[0].set(pihat1)
            da = da.at[0].set(u_k - muhat1)

            pihat2 = 1.0 / (
                1.0 / pi_prev[1] + jnp.exp(ka[1] * mu_prev[2] + om[1])
            )
            pi2 = pihat2 + ka[0] ** 2 / pihat1
            mu2 = muhat2 + ka[0] / pi2 * da[0]
            da2 = (1.0 / pi2 + (mu2 - muhat2) ** 2) * pihat2 - 1.0
            pihat = pihat.at[1].set(pihat2)
            pi = pi.at[1].set(pi2)
            mu = mu.at[1].set(mu2)
            da = da.at[1].set(da2)

            def middle_body(j, state):
                mu_m, pi_m, muhat_m, pihat_m, v_m, w_m, da_m, valid_m = state
                muhat_j = mu_prev[j] + t_k * rho[j]
                pihat_j = 1.0 / (
                    1.0 / pi_prev[j]
                    + t_k * jnp.exp(ka[j] * mu_prev[j + 1] + om[j])
                )
                pi_j, mu_j, v_lower, w_lower, valid_j = _volatility_update(
                    muhat_j,
                    pihat_j,
                    ka[j - 1],
                    pihat_m[j - 1],
                    da_m[j - 1],
                    mu_prev[j],
                    om[j - 1],
                    pi_prev[j - 1],
                    pi_m[j - 1],
                    mu_m[j - 1],
                    muhat_m[j - 1],
                    t_k,
                    update_type=update_type,
                )
                da_j = (1.0 / pi_j + (mu_j - muhat_j) ** 2) * pihat_j - 1.0
                return (
                    mu_m.at[j].set(mu_j),
                    pi_m.at[j].set(pi_j),
                    muhat_m.at[j].set(muhat_j),
                    pihat_m.at[j].set(pihat_j),
                    v_m.at[j - 1].set(v_lower),
                    w_m.at[j - 1].set(w_lower),
                    da_m.at[j].set(da_j),
                    valid_m & valid_j,
                )

            state = (mu, pi, muhat, pihat, v, w, da, valid)
            state = lax.fori_loop(2, levels - 1, middle_body, state)
            mu, pi, muhat, pihat, v, w, da, valid = state

            last = levels - 1
            muhat_last = mu_prev[last] + t_k * rho[last]
            pihat_last = 1.0 / (1.0 / pi_prev[last] + t_k * theta)
            v = v.at[last].set(t_k * theta)
            source_mu = muhat_last if update_type == "uhgf" else mu_prev[last]
            v = v.at[last - 1].set(
                t_k * jnp.exp(ka[last - 1] * source_mu + om[last - 1])
            )
            pi_last, mu_last, _, w_lower, valid_last = _volatility_update(
                muhat_last,
                pihat_last,
                ka[last - 1],
                pihat[last - 1],
                da[last - 1],
                mu_prev[last],
                om[last - 1],
                pi_prev[last - 1],
                pi[last - 1],
                mu[last - 1],
                muhat[last - 1],
                t_k,
                update_type=update_type,
            )
            da_last = (
                1.0 / pi_last + (mu_last - muhat_last) ** 2
            ) * pihat_last - 1.0
            mu = mu.at[last].set(mu_last)
            pi = pi.at[last].set(pi_last)
            muhat = muhat.at[last].set(muhat_last)
            pihat = pihat.at[last].set(pihat_last)
            w = w.at[last - 1].set(w_lower)
            da = da.at[last].set(da_last)
            return mu, pi, muhat, pihat, v, w, da, valid & valid_last

        new_carry = lax.cond(ignored_k, copy_branch, update_branch, operand=None)
        return new_carry, new_carry

    _, history = lax.scan(step, initial, (values, times, ignored))
    mu, pi, muhat, pihat, v, w, da, valid_history = history

    mu_full = jnp.concatenate((mu_init[jnp.newaxis, :], mu), axis=0)
    u_full = jnp.concatenate((jnp.asarray([0.0], dtype=jnp.float64), values))
    sgmmu2 = jax.nn.sigmoid(ka[0] * mu_full[:, 1])
    dasgmmu2 = u_full - sgmmu2
    lr1 = jnp.diff(sgmmu2) / dasgmmu2[1:]
    lr1 = jnp.where(da[:, 0] == 0.0, 0.0, lr1)

    sa = 1.0 / pi
    sahat = 1.0 / pihat
    psi = jnp.full_like(mu, jnp.nan)
    psi = psi.at[:, 1].set(1.0 / pi[:, 1])
    psi = psi.at[:, 2:levels].set(pihat[:, 1 : levels - 1] / pi[:, 2:levels])
    epsi = jnp.full_like(mu, jnp.nan)
    epsi = epsi.at[:, 1:levels].set(psi[:, 1:levels] * da[:, 0 : levels - 1])
    wt = jnp.full_like(mu, jnp.nan)
    wt = wt.at[:, 0].set(lr1)
    wt = wt.at[:, 1].set(psi[:, 1])
    wt = wt.at[:, 2:levels].set(
        0.5 * (v[:, 1 : levels - 1] * ka[1 : levels - 1]) * psi[:, 2:levels]
    )

    trajectory = {
        "mu": mu,
        "sa": sa,
        "muhat": muhat,
        "sahat": sahat,
        "v": v,
        "w": w,
        "da": da,
        "ud": mu - muhat,
        "psi": psi,
        "epsi": epsi,
        "wt": wt,
    }
    inf_states = jnp.stack((muhat, sahat, mu, sa), axis=2)
    return trajectory, inf_states, jnp.all(valid_history)


def _levels_from_parameters(parameters) -> int:
    size = int(jnp.asarray(parameters).size)
    levels = (size + 1) // 5
    if 5 * levels - 1 != size or levels < 3:
        raise ValueError("Cannot determine a valid binary HGF level count")
    return levels


def _prepare_inputs(inputs, ignored_trials):
    x = jnp.asarray(inputs, dtype=jnp.float64)
    if x.ndim not in {1, 2}:
        raise ValueError("inputs must be a 1D sequence or 2D matrix")
    values = x if x.ndim == 1 else x[:, 0]
    mask = jnp.isnan(values)
    if ignored_trials is not None:
        for index in ignored_trials:
            if index < 0 or index >= x.shape[0]:
                raise IndexError(f"ignored trial index out of range: {index}")
            mask = mask.at[index].set(True)
    return x, mask


def _signature(
    *,
    update_type: UpdateType,
    levels: int,
    observation_model: str | None,
    dtype: str,
    bucket: int,
    transformed: bool,
    irregular_intervals: bool,
    batched: bool = False,
) -> CompileSignature:
    return CompileSignature(
        model=f"{update_type}_binary",
        levels=levels,
        observation_model=observation_model,
        dtype=dtype,
        trial_length_bucket=bucket,
        static_options=(
            ("update_type", update_type),
            ("transformed", transformed),
            ("irregular_intervals", irregular_intervals),
            ("batched", batched),
        ),
    )


def fast_binary_hgf(
    inputs,
    parameters,
    *,
    update_type: UpdateType = "hgf",
    transformed: bool = True,
    irregular_intervals: bool = False,
    ignored_trials=None,
    device=None,
    use_jit: bool = True,
) -> FastForwardResult:
    """Run a device-resident binary HGF/eHGF/uHGF forward pass."""

    if update_type not in {"hgf", "ehgf", "uhgf"}:
        raise ValueError("update_type must be 'hgf', 'ehgf', or 'uhgf'")
    x, mask = _prepare_inputs(inputs, ignored_trials)
    if irregular_intervals and x.ndim != 2:
        raise ValueError("irregular_intervals=True requires a 2D input matrix")

    p = jnp.asarray(parameters, dtype=jnp.float64)
    n_trials = int(x.shape[0])
    bucket = trial_length_bucket(n_trials)
    x_pad = pad_trials(x, bucket)
    mask_pad = pad_mask(mask, bucket)
    if device is not None:
        x_pad = jax.device_put(x_pad, device)
        p = jax.device_put(p, device)
        mask_pad = jax.device_put(mask_pad, device)

    levels = _levels_from_parameters(p)
    if use_jit:
        signature = _signature(
            update_type=update_type,
            levels=levels,
            observation_model=None,
            dtype=str(p.dtype),
            bucket=bucket,
            transformed=transformed,
            irregular_intervals=irregular_intervals,
        )

        def factory():
            def run(x_value, p_value, mask_value):
                return _binary_forward_impl(
                    x_value,
                    p_value,
                    mask_value,
                    update_type=update_type,
                    transformed=transformed,
                    irregular_intervals=irregular_intervals,
                )
            return jax.jit(run)

        runner = GLOBAL_COMPILE_CACHE.get_or_create(signature, factory)
    else:
        runner = partial(
            _binary_forward_impl,
            update_type=update_type,
            transformed=transformed,
            irregular_intervals=irregular_intervals,
        )

    trajectory, inf_states, valid = runner(x_pad, p, mask_pad)
    trajectory = {key: value[:n_trials] for key, value in trajectory.items()}
    return FastForwardResult(
        trajectory=trajectory,
        inf_states=inf_states[:n_trials],
        valid=valid,
        n_trials=n_trials,
        bucket=bucket,
    )


def fast_binary_hgf_vmap(
    inputs_batch,
    parameters_batch,
    *,
    update_type: UpdateType = "hgf",
    transformed: bool = True,
    irregular_intervals: bool = False,
):
    """Vectorize equal-shape forwards; scheduling remains an M16 concern."""

    x = jnp.asarray(inputs_batch, dtype=jnp.float64)
    p = jnp.asarray(parameters_batch, dtype=jnp.float64)
    if x.ndim not in {2, 3}:
        raise ValueError("inputs_batch must be (batch, trial) or (batch, trial, column)")
    if p.ndim != 2 or p.shape[0] != x.shape[0]:
        raise ValueError("parameters_batch must have one vector per batch item")

    values = x if x.ndim == 2 else x[:, :, 0]
    masks = jnp.isnan(values)

    def one(x_value, p_value, mask_value):
        return _binary_forward_impl(
            x_value,
            p_value,
            mask_value,
            update_type=update_type,
            transformed=transformed,
            irregular_intervals=irregular_intervals,
        )

    return jax.jit(jax.vmap(one, in_axes=(0, 0, 0)))(x, p, masks)


def _gaussian_prior(parameters, means, variances):
    mask = (~jnp.isnan(variances)) & (variances != 0.0)
    safe_variances = jnp.where(mask, variances, 1.0)
    safe_means = jnp.where(mask, means, 0.0)
    safe_parameters = jnp.where(mask, parameters, 0.0)
    terms = (
        -0.5 * jnp.log(2.0 * jnp.pi * safe_variances)
        - 0.5 * (safe_parameters - safe_means) ** 2 / safe_variances
    )
    return jnp.sum(jnp.where(mask, terms, 0.0))


def _binary_unitsq_objective_impl(
    responses,
    inputs,
    perceptual_parameters,
    observation_parameters,
    ignored,
    prc_means,
    prc_variances,
    obs_means,
    obs_variances,
    *,
    irregular_intervals: bool,
):
    _, inf_states, valid = _binary_forward_impl(
        inputs,
        perceptual_parameters,
        ignored,
        update_type="hgf",
        transformed=True,
        irregular_intervals=irregular_intervals,
    )
    y_array = jnp.asarray(responses, dtype=jnp.float64)
    y = y_array if y_array.ndim == 1 else y_array[:, 0]
    input_values = inputs if inputs.ndim == 1 else inputs[:, 0]
    irregular = jnp.isnan(input_values) | jnp.isnan(y)
    regular = ~irregular

    x = inf_states[:, 0, 0]
    ze = jnp.exp(jnp.asarray(observation_parameters, dtype=jnp.float64).reshape(-1)[0])
    logx = jnp.where((1.0 - x) < 1e-4, jnp.log1p(x - 1.0), jnp.log(x))
    log1mx = jnp.where(x < 1e-4, jnp.log1p(-x), jnp.log(1.0 - x))
    logp = (
        y * ze * (logx - log1mx)
        + ze * log1mx
        - jnp.log((1.0 - x) ** ze + x**ze)
    )
    trial_logp = jnp.where(regular, logp, jnp.nan)
    log_likelihood = jnp.sum(jnp.where(regular, logp, 0.0))
    prc_prior = _gaussian_prior(
        perceptual_parameters, prc_means, prc_variances
    )
    obs_prior = _gaussian_prior(
        observation_parameters, obs_means, obs_variances
    )
    realmax = jnp.finfo(jnp.float64).max
    neg_ll = jnp.where(valid, -log_likelihood, realmax)
    neg_joint = jnp.where(
        valid, -(log_likelihood + prc_prior + obs_prior), realmax
    )
    rval = jnp.where(valid, jnp.int32(0), jnp.int32(-1))
    return trial_logp, log_likelihood, neg_ll, prc_prior, obs_prior, neg_joint, rval


def fast_binary_unitsq_objective(
    responses,
    inputs,
    perceptual_parameters,
    observation_parameters,
    *,
    irregular_intervals: bool = False,
    device=None,
    use_jit: bool = True,
) -> FastObjectiveResult:
    """Evaluate the M8 binary-HGF + unit-square objective on the JAX path."""

    x, ignored = _prepare_inputs(inputs, None)
    y = jnp.asarray(responses, dtype=jnp.float64)
    if y.shape[0] != x.shape[0]:
        raise ValueError("responses and inputs must contain the same number of trials")
    if irregular_intervals and x.ndim != 2:
        raise ValueError("irregular_intervals=True requires a 2D input matrix")

    p_prc = jnp.asarray(perceptual_parameters, dtype=jnp.float64).reshape(-1)
    p_obs = jnp.asarray(observation_parameters, dtype=jnp.float64).reshape(-1)
    n_trials = int(x.shape[0])
    bucket = trial_length_bucket(n_trials)
    x_pad = pad_trials(x, bucket)
    y_pad = pad_trials(y, bucket)
    ignored_pad = pad_mask(ignored, bucket)

    prc = hgf_binary_config()
    obs = unitsq_sgm_config()
    prc_mu = jnp.asarray(prc.priormus, dtype=jnp.float64)
    prc_sa = jnp.asarray(prc.priorsas, dtype=jnp.float64)
    obs_mu = jnp.asarray(obs.priormus, dtype=jnp.float64)
    obs_sa = jnp.asarray(obs.priorsas, dtype=jnp.float64)

    if device is not None:
        arrays = [x_pad, y_pad, p_prc, p_obs, ignored_pad, prc_mu, prc_sa, obs_mu, obs_sa]
        arrays = [jax.device_put(value, device) for value in arrays]
        x_pad, y_pad, p_prc, p_obs, ignored_pad, prc_mu, prc_sa, obs_mu, obs_sa = arrays

    signature = _signature(
        update_type="hgf",
        levels=_levels_from_parameters(p_prc),
        observation_model="unitsq_sgm",
        dtype=str(p_prc.dtype),
        bucket=bucket,
        transformed=True,
        irregular_intervals=irregular_intervals,
    )

    if use_jit:
        def factory():
            def run(y_value, x_value, pp, po, mask, pmu, psa, omu, osa):
                return _binary_unitsq_objective_impl(
                    y_value,
                    x_value,
                    pp,
                    po,
                    mask,
                    pmu,
                    psa,
                    omu,
                    osa,
                    irregular_intervals=irregular_intervals,
                )
            return jax.jit(run)

        runner = GLOBAL_COMPILE_CACHE.get_or_create(signature, factory)
    else:
        runner = partial(
            _binary_unitsq_objective_impl,
            irregular_intervals=irregular_intervals,
        )

    output = runner(
        y_pad,
        x_pad,
        p_prc,
        p_obs,
        ignored_pad,
        prc_mu,
        prc_sa,
        obs_mu,
        obs_sa,
    )
    return FastObjectiveResult(
        trial_log_likelihoods=output[0][:n_trials],
        log_likelihood=output[1],
        neg_log_likelihood=output[2],
        perceptual_prior=output[3],
        observation_prior=output[4],
        neg_log_joint=output[5],
        rval=output[6],
    )



def fast_binary_unitsq_objective_vmap(
    responses,
    inputs,
    perceptual_parameters_batch,
    observation_parameters_batch,
    *,
    irregular_intervals: bool = False,
):
    """Vectorize the fixed-data objective across restart/parameter candidates."""

    x, ignored = _prepare_inputs(inputs, None)
    y = jnp.asarray(responses, dtype=jnp.float64)
    p_prc = jnp.asarray(perceptual_parameters_batch, dtype=jnp.float64)
    p_obs = jnp.asarray(observation_parameters_batch, dtype=jnp.float64)
    if p_prc.ndim != 2 or p_obs.ndim != 2:
        raise ValueError("parameter batches must be two-dimensional")
    if p_prc.shape[0] != p_obs.shape[0]:
        raise ValueError("perceptual and observation batches must have equal length")
    if y.shape[0] != x.shape[0]:
        raise ValueError("responses and inputs must contain the same number of trials")

    prc = hgf_binary_config()
    obs = unitsq_sgm_config()
    prc_mu = jnp.asarray(prc.priormus, dtype=jnp.float64)
    prc_sa = jnp.asarray(prc.priorsas, dtype=jnp.float64)
    obs_mu = jnp.asarray(obs.priormus, dtype=jnp.float64)
    obs_sa = jnp.asarray(obs.priorsas, dtype=jnp.float64)

    def one(pp, po):
        return _binary_unitsq_objective_impl(
            y,
            x,
            pp,
            po,
            ignored,
            prc_mu,
            prc_sa,
            obs_mu,
            obs_sa,
            irregular_intervals=irregular_intervals,
        )

    output = jax.jit(jax.vmap(one, in_axes=(0, 0)))(p_prc, p_obs)
    return FastObjectiveBatchResult(
        trial_log_likelihoods=output[0],
        log_likelihood=output[1],
        neg_log_likelihood=output[2],
        perceptual_prior=output[3],
        observation_prior=output[4],
        neg_log_joint=output[5],
        rval=output[6],
    )


__all__ = [
    "FastForwardResult",
    "FastObjectiveResult",
    "FastObjectiveBatchResult",
    "fast_binary_hgf",
    "fast_binary_hgf_vmap",
    "fast_binary_unitsq_objective",
    "fast_binary_unitsq_objective_vmap",
]
