"""Hierarchical hidden Markov model (HHMM) compatibility implementation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from collections.abc import Sequence

import numpy as np

from hgfx.math.logistic import sigmoid


@dataclass
class HHMMNode:
    parent: int | None
    children: tuple[int, ...]
    V: float | None
    A: np.ndarray | None
    B: np.ndarray | None


def hhmm_default_config_tree() -> list[dict]:
    """Frozen tapas_hhmm_config.m tree, using zero-based node ids."""

    def logit(x: float) -> float:
        return float(np.log(x / (1.0 - x)))

    return [
        {"parent": None, "children": (1, 2), "V": None,
         "A_mu": np.array([[-np.inf, np.inf], [np.inf, -np.inf]]),
         "A_sa": np.zeros((2, 2)), "B": None},
        {"parent": 0, "children": (3, 4), "V_mu": logit(.5), "V_sa": 0.0,
         "A_mu": np.array([[logit(.9), logit(.05)], [logit(.05), logit(.9)]]),
         "A_sa": np.array([[0.0, .1], [.1, 0.0]]), "B": None},
        {"parent": 0, "children": (5, 6), "V_mu": logit(.5), "V_sa": 0.0,
         "A_mu": np.array([[logit(.6), logit(.35)], [logit(.35), logit(.6)]]),
         "A_sa": np.array([[0.0, .1], [.1, 0.0]]), "B": None},
        {"parent": 1, "children": (), "V_mu": logit(.5), "V_sa": 0.0,
         "A_mu": None, "A_sa": None, "B": np.array([.15, .85])},
        {"parent": 1, "children": (), "V_mu": logit(.5), "V_sa": 0.0,
         "A_mu": None, "A_sa": None, "B": np.array([.85, .15])},
        {"parent": 2, "children": (), "V_mu": logit(.5), "V_sa": 0.0,
         "A_mu": None, "A_sa": None, "B": np.array([.15, .85])},
        {"parent": 2, "children": (), "V_mu": logit(.5), "V_sa": 0.0,
         "A_mu": None, "A_sa": None, "B": np.array([.85, .15])},
    ]


def hhmm_prior_vectors(tree_config=None) -> tuple[np.ndarray, np.ndarray]:
    tree = hhmm_default_config_tree() if tree_config is None else tree_config
    mus: list[float] = []
    sas: list[float] = []
    for node in tree:
        if node.get("parent") is not None:
            mus.append(float(node["V_mu"]))
            sas.append(float(node["V_sa"]))
        if node.get("A_mu") is not None:
            # MATLAB A(:)' is column-major.
            mus.extend(np.asarray(node["A_mu"], dtype=np.float64).reshape(-1, order="F"))
            sas.extend(np.asarray(node["A_sa"], dtype=np.float64).reshape(-1, order="F"))
    return np.asarray(mus), np.asarray(sas)


def hhmm_transform(parameters, *, tree_config=None, transformed: bool = True) -> list[HHMMNode]:
    tree = hhmm_default_config_tree() if tree_config is None else deepcopy(tree_config)
    pv = np.asarray(parameters, dtype=np.float64).reshape(-1)
    if transformed:
        pv = np.asarray(sigmoid(pv, 1.0), dtype=np.float64)
    cursor = 0
    nodes: list[HHMMNode] = []
    for cfg in tree:
        parent = cfg.get("parent")
        children = tuple(int(x) for x in cfg.get("children", ()))
        if parent is not None:
            if cursor >= pv.size:
                raise ValueError("HHMM parameter vector does not match tree")
            v = float(pv[cursor]); cursor += 1
        else:
            v = None
        if cfg.get("A_mu") is not None:
            nc = len(children)
            count = nc * nc
            if cursor + count > pv.size:
                raise ValueError("HHMM parameter vector does not match tree")
            a = np.reshape(pv[cursor : cursor + count], (nc, nc), order="F")
            cursor += count
        else:
            a = None
        b = None if cfg.get("B") is None else np.asarray(cfg["B"], dtype=np.float64).copy()
        nodes.append(HHMMNode(parent=parent, children=children, V=v, A=a, B=b))
    if cursor != pv.size:
        raise ValueError("HHMM parameter vector does not match tree")
    return nodes


def _ancestors(nodes: list[HHMMNode], node_id: int) -> list[int]:
    result = [node_id]
    parent = nodes[node_id].parent
    while parent is not None:
        result.insert(0, parent)
        parent = nodes[parent].parent
    return result


def _common_ancestor(nodes: list[HHMMNode], a: int, b: int) -> int:
    aa = _ancestors(nodes, a)
    bb = _ancestors(nodes, b)
    common = aa[0]
    for x, y in zip(aa, bb):
        if x != y:
            break
        common = x
    return common


def _validate_tree(nodes: list[HHMMNode], n_outcomes: int) -> None:
    if nodes[0].V is not None:
        raise ValueError("Illegal entry probability for HHMM root")
    for idx, node in enumerate(nodes):
        if (node.A is None) == (node.B is None):
            raise ValueError(f"Illegal combination of A and B for node {idx}")
        if node.A is not None and len(node.children) != node.A.shape[1]:
            raise ValueError(f"Number of children inconsistent with A for node {idx}")
        if node.A is not None and np.any(np.sum(node.A, axis=1) > 1.0):
            raise ValueError(f"Illegal transition row sum at node {idx}")
        if node.A is not None:
            for cpos, child in enumerate(node.children):
                if nodes[child].children and node.A[cpos, cpos] != 0.0:
                    raise ValueError("Only production nodes may have self-transitions")
        if node.B is not None:
            if node.B.size != n_outcomes or not np.isclose(np.sum(node.B), 1.0):
                raise ValueError(f"Illegal outcome contingency at node {idx}")
        if node.children:
            total = sum(float(nodes[child].V) for child in node.children)
            if not np.isclose(total, 1.0):
                raise ValueError(f"Illegal vertical probabilities from node {idx}")


def _flatten_hhmm(nodes: list[HHMMNode], n_outcomes: int):
    _validate_tree(nodes, n_outcomes)
    production = [i for i, node in enumerate(nodes) if not node.children]
    d = len(production)
    bflat = np.full((n_outcomes, d), np.nan)
    for col, pid in enumerate(production):
        bflat[:, col] = nodes[pid].B

    aflat = np.full((d, d), np.nan)
    for i, source in enumerate(production):
        for j, target in enumerate(production):
            ps = nodes[source].parent
            pt = nodes[target].parent
            if ps == pt:
                assert ps is not None
                src_pos = nodes[ps].children.index(source)
                dst_pos = nodes[ps].children.index(target)
                aflat[i, j] = nodes[ps].A[src_pos, dst_pos]
                continue

            ca = _common_ancestor(nodes, source, target)
            tp = 1.0
            nid = source
            pid = nodes[nid].parent
            assert pid is not None
            nidx = nodes[pid].children.index(nid)
            while pid != ca:
                tp *= 1.0 - float(np.sum(nodes[pid].A[nidx, :]))
                nid = pid
                pid = nodes[nid].parent
                assert pid is not None
                nidx = nodes[pid].children.index(nid)

            target_anc = _ancestors(nodes, target)
            ca_pos = target_anc.index(ca)
            below = target_anc[ca_pos + 1 :]
            if not below:
                raise ValueError("Production target cannot equal common ancestor")
            caidxi = nidx
            caidxj = nodes[ca].children.index(below[0])
            tp *= nodes[ca].A[caidxi, caidxj]
            # Frozen source multiplies V starting after the child directly
            # below the common ancestor.
            for down_node in below[1:]:
                tp *= float(nodes[down_node].V)
            aflat[i, j] = tp

    prior = np.full(d, np.nan)
    for i, pid in enumerate(production):
        anc = _ancestors(nodes, pid)[1:]
        prob = 1.0
        for node_id in anc:
            prob *= float(nodes[node_id].V)
        prior[i] = prob
    if not np.isclose(np.sum(prior), 1.0):
        raise ValueError("Cannot calculate HHMM production-node priors")
    return production, bflat, aflat, prior


def hierarchical_hidden_markov_model(
    inputs,
    parameters,
    *,
    n_outcomes: int = 2,
    tree_config=None,
    transformed: bool = True,
    ignored_trials: Sequence[int] | None = None,
):
    """Usable port of frozen tapas_hhmm.m / internal htapas_hmm."""

    nodes = hhmm_transform(parameters, tree_config=tree_config, transformed=transformed)
    _, bflat, aflat, prior = _flatten_hhmm(nodes, n_outcomes)
    values = np.asarray(inputs, dtype=np.float64)
    if values.ndim == 2:
        values = values[:, 0]
    values = values.reshape(-1)
    ignored = np.isnan(values)
    if ignored_trials is not None:
        ignored = ignored.copy()
        for idx in ignored_trials:
            ignored[idx] = True
    outcomes = np.where(np.isnan(values), 1, values).astype(np.int64)
    valid = ~ignored
    if np.any((outcomes[valid] < 1) | (outcomes[valid] > n_outcomes)):
        raise ValueError("HHMM outcomes must be MATLAB-style 1..n_outcomes")

    n = values.size
    alpha = np.full((n, prior.size), np.nan)
    tmp = prior * bflat[outcomes[0] - 1]
    alpha[0] = tmp / np.sum(tmp)
    for k in range(1, n):
        if ignored[k]:
            alpha[k] = alpha[k - 1]
        else:
            tmp = bflat[outcomes[k] - 1] * (alpha[k - 1] @ aflat)
            alpha[k] = tmp / np.sum(tmp)
    alpha_hat = np.vstack((prior, alpha))[:-1]
    return {"alpr": alpha, "alprhat": alpha_hat}, alpha.copy()
