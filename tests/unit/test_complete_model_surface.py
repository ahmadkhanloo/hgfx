from __future__ import annotations

import numpy as np

from hgfx.models import (
    hgf_ar1,
    hgf_binary_mab,
    hgf_ar1_mab,
    hgf_ar1_binary_mab,
    ehgf_ar1_binary_mab,
    uhgf_ar1_binary_mab,
    hgf_jget,
    ehgf_jget,
    uhgf_jget,
    hgf_categorical,
    hgf_categorical_norm,
    hgf_whatworld,
    hgf_whichworld,
    hhmm_default_config_tree,
    hhmm_prior_vectors,
    hierarchical_hidden_markov_model,
)
from hgfx.responses import (
    bayes_optimal,
    bayes_optimal_binary,
    bayes_optimal_categorical,
    squared_pe,
    rs_belief,
    rs_precision,
    rs_surprise,
    condhalluc_obs,
    condhalluc_obs2,
    condhalluc_obs3,
)


def test_complete_specialized_perceptual_surface_executes() -> None:
    binary = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)
    choices3 = np.array([1, 2, 3, 1, 2, 3, 1, 2], dtype=float)

    p_binary_mab = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, 0, 1, 1, np.nan, -3, -6],
        dtype=float,
    )
    traj, inf = hgf_binary_mab(
        binary, p_binary_mab, choices=choices3, n_bandits=3, validate=False
    )
    assert inf.shape == (binary.size, 3, 3, 4)
    assert traj["mu"].shape == (binary.size, 3, 3)

    continuous = np.array([.2, .4, .1, .7, .6, .3, .9, .2], dtype=float)
    p_ar_mab = np.array([.2, 1, .3, .1, .1, 0, .2, 1, 1, -3, -6, .2], dtype=float)
    traj, inf = hgf_ar1_mab(
        continuous, p_ar_mab, choices=choices3, n_bandits=3, validate=False
    )
    assert inf.shape == (continuous.size, 2, 3, 4)

    p_ar_bin = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, .2, np.nan, 0, 1, 1, 1, np.nan, -2, -6],
        dtype=float,
    )
    p_ar_bin_ext = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, .45, np.nan, 0, 1,
         np.nan, 0, 0, 1, 1, np.nan, -3, 2],
        dtype=float,
    )
    for fn, p in (
        (hgf_ar1_binary_mab, p_ar_bin),
        (ehgf_ar1_binary_mab, p_ar_bin_ext),
        (uhgf_ar1_binary_mab, p_ar_bin_ext),
    ):
        _, inf = fn(binary, p, choices=choices3, n_bandits=3, validate=False)
        assert inf.shape == (binary.size, 3, 3, 4)

    p_jget = np.array(
        [.3, 1, .5, .2, -2, -2, 1, 1, 1, 1, 1, 0, -3, -6, -3, -6],
        dtype=float,
    )
    for fn in (hgf_jget, ehgf_jget, uhgf_jget):
        traj, inf = fn(continuous, p_jget, validate=False)
        assert inf.shape == (continuous.size, 1, 10)
        assert traj["mux"].shape == (continuous.size, 2)

    logit_third = np.log((1 / 3) / (2 / 3))
    p_cat = np.array(
        [logit_third] * 3 + [1, 1, 1] + [1, .1, 1, -4, .05],
        dtype=float,
    )
    categorical = np.array([1, 2, 3, 2, 1, 3, 3, 1], dtype=float)
    for fn in (hgf_categorical, hgf_categorical_norm):
        traj, inf = fn(categorical, p_cat, n_outcomes=3)
        assert inf.shape == (categorical.size, 3, 3, 4)
        assert traj["mu"].shape == (categorical.size, 3, 3)

    states = np.array([1, 2, 2, 1, 2, 1, 1, 2], dtype=float)
    p_what = np.array([0] * 4 + [1] * 4 + [1, .1, 1, -4, .05], dtype=float)
    traj, inf = hgf_whatworld(states, p_what, n_states=2)
    assert inf.shape == (states.size, 3, 2, 2, 4)

    p_which = np.array([0, 0, 1, 1, 1, .1, 1, -4, .05, 0, .1], dtype=float)
    traj, inf = hgf_whichworld(binary, p_which)
    assert inf.shape == (binary.size, 3, 2, 4)

    tree = hhmm_default_config_tree()
    mus, _ = hhmm_prior_vectors(tree)
    traj, inf = hierarchical_hidden_markov_model(
        np.array([1, 2, 1, 2, 2, 1, 1, 2], dtype=float),
        mus,
        tree_config=tree,
        transformed=True,
    )
    assert inf.shape == (8, 4)
    np.testing.assert_allclose(np.sum(inf, axis=1), 1.0)


def test_auxiliary_and_conditioned_response_surface_executes() -> None:
    n = 8
    inputs = np.column_stack((
        np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float),
        np.array([0, .25, .5, .75, 0, .25, .5, .75], dtype=float),
    ))
    states = np.zeros((n, 3, 4), dtype=float)
    states[:, 0, 0] = np.linspace(.2, .8, n)
    states[:, 0, 1] = .2
    states[:, 1, 0] = np.linspace(-1, 1, n)
    states[:, 2, 0] = np.linspace(-2, 1, n)

    for fn in (bayes_optimal, bayes_optimal_binary):
        out = fn(inputs[:, 0], states)
        assert all(np.asarray(x).shape == (n,) for x in out)

    out = squared_pe(inputs[:, 0], states, [np.log(.2)])
    assert all(np.asarray(x).shape == (n,) for x in out)

    responses = np.linspace(.01, .02, n)
    p_rs = np.log([.0052, .0052, .0006, .001])
    for fn in (rs_belief, rs_precision, rs_surprise):
        out = fn(responses, inputs[:, 0], states, p_rs)
        assert all(np.asarray(x).shape == (n,) for x in out)

    binary_responses = np.array([0, 1, 1, 0, 1, 0, 1, 1], dtype=float)
    for fn, p in (
        (condhalluc_obs, [np.log(48)]),
        (condhalluc_obs2, [np.log(48), 0]),
        (condhalluc_obs3, [np.log(48)]),
    ):
        out = fn(binary_responses, inputs, states, p)
        assert all(np.asarray(x).shape == (n,) for x in out)


def test_bayes_optimal_categorical_surface() -> None:
    n, choices = 6, 3
    inf = np.zeros((n, 1, choices, 1), dtype=float)
    inf[:, 0, :, 0] = np.array([.2, .3, .5])
    u = np.array([1, 2, 3, 1, 3, 2], dtype=float)
    logp, yhat, res = bayes_optimal_categorical(u, inf)
    assert logp.shape == yhat.shape == res.shape == (n,)
    assert np.all(np.isfinite(logp))
