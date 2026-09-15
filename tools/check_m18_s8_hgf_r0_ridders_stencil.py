#!/usr/bin/env python3
"""Compare exact MATLAB Ridders stencil evaluations for the frozen S8 HGF R0 case."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.objective import evaluate_objective
from hgfx.models.hgf_binary import hgf_binary
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

PROTOCOL = "m18-s8-hgf-r0-ridders-stencil-1"
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CASE_ID = "PR-hgf_binary-T256-S0.35-R0"
CASE_SHA = "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5"


def _normalise(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def _array(value: Any) -> np.ndarray:
    if isinstance(value, dict) and value.get("hgfx_numeric") == "ieee-strings-v1":
        return np.asarray(_normalise(value["data"]), dtype=np.float64).reshape(value["shape"], order="F")
    return np.asarray(_normalise(value), dtype=np.float64)


def _scalar(value: Any) -> float:
    return float(_array(value).reshape(-1)[0])


def _diff(actual, expected) -> dict:
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    if a.shape != e.shape:
        return {"shape_mismatch": [list(a.shape), list(e.shape)]}
    mask = np.isfinite(a) & np.isfinite(e)
    d = np.abs(a-e)
    exact = (a == e) | (np.isnan(a) & np.isnan(e))
    first = None
    if not np.all(exact):
        idx = tuple(int(i) for i in np.argwhere(~exact)[0]) if np.ndim(exact) else ()
        first = {
            "index_zero_based": list(idx),
            "hgfx": float(a[idx] if idx else a.item()),
            "matlab": float(e[idx] if idx else e.item()),
            "abs_diff": float(d[idx] if idx else d.item()),
        }
    return {
        "exact": bool(np.all(exact)),
        "max_abs": float(np.max(d[mask])) if np.any(mask) else float("nan"),
        "different_count": int(np.size(exact) - np.count_nonzero(exact)),
        "first_difference": first,
    }


def _python_eval(case: dict, free: np.ndarray) -> dict:
    u = np.asarray(case["u"], dtype=np.float64)
    y = np.asarray(case["y"], dtype=np.float64)
    prc = hgf_binary_config().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    idx = np.asarray(case["free_indices_zero_based"], dtype=np.int64)
    full[idx] = np.asarray(free, dtype=np.float64).reshape(-1)
    n_prc = len(prc.parameters)
    p_prc = full[:n_prc]
    p_obs = full[n_prc:]

    # Frozen fitModel/Ridders semantics map perceptual failures at trial-invalid
    # stencil points to realmax.  The diagnostic must preserve that behavior
    # rather than aborting while it inspects the same x +/- h vectors.
    try:
        _, inf_states = hgf_binary(u, p_prc, transformed=True)
    except Exception:
        return {
            "neg_joint": float(np.finfo(np.float64).max),
            "neg_log_likelihood": float(np.finfo(np.float64).max),
            "prc_prior": float("nan"),
            "obs_prior": float("nan"),
            "trial_log_likelihoods": np.full(y.shape, np.nan, dtype=np.float64),
            "inf_states": np.asarray(np.nan, dtype=np.float64),
        }

    trial, _, _ = unitsq_sgm(
        y,
        inf_states,
        p_obs,
        predorpost=int(obs.options.get("predorpost", 1)),
    )
    objective = evaluate_objective(
        responses=y,
        inputs=u,
        perceptual_parameters=p_prc,
        observation_parameters=p_obs,
        perceptual_config=prc,
        observation_config=obs,
        perceptual_function=hgf_binary,
        observation_function=unitsq_sgm,
        observation_kwargs={"predorpost": int(obs.options.get("predorpost", 1))},
    )
    return {
        "neg_joint": objective.neg_log_joint,
        "neg_log_likelihood": objective.neg_log_likelihood,
        "prc_prior": objective.perceptual_prior.total,
        "obs_prior": objective.observation_prior.total,
        "trial_log_likelihoods": np.asarray(trial, dtype=np.float64),
        "inf_states": np.asarray(inf_states, dtype=np.float64),
    }


def main(fixture_path: Path, matlab_path: Path, output_path: Path) -> int:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    ref = json.loads(matlab_path.read_text(encoding="utf-8"))
    if ref.get("protocol") != PROTOCOL or ref.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Frozen stencil protocol/reference mismatch")
    if ref.get("case_id") != CASE_ID or ref.get("case_sha256") != CASE_SHA:
        raise ValueError("Frozen R0 case mismatch")
    cases = [c for c in fixture.get("cases", []) if c.get("case_id") == CASE_ID]
    if len(cases) != 1 or cases[0].get("case_sha256") != CASE_SHA:
        raise ValueError("Immutable R0 fixture missing or changed")
    case = cases[0]

    rows = []
    first_inf = None
    first_trial = None
    first_likelihood_total = None
    first_prior = None
    first_joint = None
    largest_joint = {"abs_diff": -1.0}
    for sample in ref.get("samples", []):
        step = int(round(_scalar(sample["step_1based"])))
        h = _scalar(sample["h"])
        row = {"step_1based": step, "h": h, "sides": {}}
        for side in ("plus", "minus"):
            expected = sample[side]
            free = _array(expected["free"]).reshape(-1)
            actual = _python_eval(case, free)
            cmp = {
                "neg_joint": _diff([actual["neg_joint"]], [_scalar(expected["neg_joint"])]),
                "neg_log_likelihood": _diff([actual["neg_log_likelihood"]], [_scalar(expected["neg_log_likelihood"])]),
                "prc_prior": _diff([actual["prc_prior"]], [_scalar(expected["prc_prior"])]),
                "obs_prior": _diff([actual["obs_prior"]], [_scalar(expected["obs_prior"])]),
                "trial_log_likelihoods": _diff(actual["trial_log_likelihoods"], _array(expected["trial_log_likelihoods"]).reshape(-1)),
                "inf_states": _diff(actual["inf_states"], _array(expected["inf_states"])),
            }
            row["sides"][side] = cmp
            tag = {"step_1based": step, "side": side, "h": h}
            if first_inf is None and not cmp["inf_states"].get("exact", True):
                first_inf = {**tag, **cmp["inf_states"]}
            if first_trial is None and not cmp["trial_log_likelihoods"].get("exact", True):
                first_trial = {**tag, **cmp["trial_log_likelihoods"]}
            if first_likelihood_total is None and not cmp["neg_log_likelihood"].get("exact", True):
                first_likelihood_total = {**tag, **cmp["neg_log_likelihood"]}
            if first_prior is None and (
                not cmp["prc_prior"].get("exact", True)
                or not cmp["obs_prior"].get("exact", True)
            ):
                first_prior = {
                    **tag,
                    "prc_prior": cmp["prc_prior"],
                    "obs_prior": cmp["obs_prior"],
                }
            if first_joint is None and not cmp["neg_joint"].get("exact", True):
                first_joint = {**tag, **cmp["neg_joint"]}
            jd = cmp["neg_joint"].get("max_abs", 0.0)
            if np.isfinite(jd) and jd > largest_joint["abs_diff"]:
                largest_joint = {**tag, "abs_diff": float(jd)}
        rows.append(row)

    if first_inf is not None:
        classification = "PERCEPTUAL_STENCIL_NUMERICS_DIVERGE"
    elif first_trial is not None:
        classification = "OBSERVATION_STENCIL_NUMERICS_DIVERGE"
    elif first_likelihood_total is not None:
        classification = "LIKELIHOOD_REDUCTION_STENCIL_DIVERGES"
    elif first_prior is not None:
        classification = "PRIOR_STENCIL_NUMERICS_DIVERGE"
    elif first_joint is not None:
        classification = "JOINT_ASSEMBLY_STENCIL_DIVERGES"
    else:
        classification = "STENCIL_EVALUATIONS_EXACT"

    payload = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": CASE_ID,
        "case_sha256": CASE_SHA,
        "classification": classification,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "matlab_optimizer_row_1based": int(ref["matlab_optimizer_row_1based"]),
        "free_component_1based": int(ref["free_component_1based"]),
        "matlab_ridders_gradient": _scalar(ref["ridders_gradient"]),
        "matlab_ridders_error": _scalar(ref["ridders_error"]),
        "first_inference_state_difference": first_inf,
        "first_trial_likelihood_difference": first_trial,
        "first_likelihood_total_difference": first_likelihood_total,
        "first_prior_difference": first_prior,
        "first_joint_difference": first_joint,
        "largest_joint_difference": largest_joint,
        "samples": rows,
        "note": "Diagnostic only. Exact Ridders stencil vectors are inherited from the immutable S7 R0 case; no scientific input or acceptance criterion is changed.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, allow_nan=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                k: payload[k]
                for k in [
                    "classification",
                    "first_inference_state_difference",
                    "first_trial_likelihood_difference",
                    "first_likelihood_total_difference",
                    "first_prior_difference",
                    "first_joint_difference",
                    "largest_joint_difference",
                ]
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("matlab", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.fixture, args.matlab, args.output))
