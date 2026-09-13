#!/usr/bin/env python3
"""Compare MATLAB/HGFX D02 objective components at exact Ridders coordinates."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config

THRESHOLDS = (0.0, 1e-15, 1e-14, 1e-13, 1e-12)


def stats(actual, expected):
    actual = np.asarray(actual, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if actual.shape != expected.shape:
        return {"shape_mismatch": [list(actual.shape), list(expected.shape)]}
    diff = np.abs(actual - expected)
    finite = np.isfinite(diff)
    out = {
        "max_abs": float(np.max(diff[finite])) if np.any(finite) else float("nan")
    }
    for threshold in THRESHOLDS:
        mask = diff > threshold
        key = f"first_gt_{threshold:.0e}"
        if np.any(mask):
            idx = tuple(int(i) for i in np.argwhere(mask)[0])
            out[key] = {
                "index": list(idx),
                "hgfx": float(actual[idx]),
                "matlab": float(expected[idx]),
                "abs_diff": float(diff[idx]),
            }
        else:
            out[key] = None
    return out


def stack(results, getter):
    return np.stack([np.asarray(getter(r), dtype=np.float64) for r in results])


def compare_side(results, matlab):
    return {
        "neg_log_joint": stats(
            [r.neg_log_joint for r in results], _array(matlab["neg_log_joint"]).reshape(-1)
        ),
        "log_likelihood": stats(
            [r.log_likelihood for r in results], _array(matlab["log_likelihood"]).reshape(-1)
        ),
        "perceptual_prior_total": stats(
            [r.perceptual_prior.total for r in results],
            _array(matlab["perceptual_prior_total"]).reshape(-1),
        ),
        "observation_prior_total": stats(
            [r.observation_prior.total for r in results],
            _array(matlab["observation_prior_total"]).reshape(-1),
        ),
        "trial_log_likelihoods": stats(
            stack(results, lambda r: r.regular_trial_log_likelihoods),
            _array(matlab["trial_log_likelihoods"]),
        ),
        "perceptual_prior_terms": stats(
            stack(results, lambda r: r.perceptual_prior.terms),
            _array(matlab["perceptual_prior_terms"]),
        ),
        "observation_prior_terms": stats(
            stack(results, lambda r: r.observation_prior.terms),
            _array(matlab["observation_prior_terms"]),
        ),
    }


def evaluate_side(problem, x0, parameter_index, coordinates):
    results = []
    for coordinate in _array(coordinates).reshape(-1):
        candidate = x0.copy()
        candidate[parameter_index] = coordinate
        results.append(problem.evaluate_full(problem.expand(candidate)))
    return results


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d02-objective-decomposition-1":
        raise ValueError("Diagnostic protocol mismatch")
    if reference["case_id"] != "D02_fit":
        raise ValueError("Unexpected case")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("ehgf_binary")
    obs = resolve_config("unitsq_sgm")
    obs = replace(
        obs,
        parameters=(
            replace(
                obs.parameters[0],
                prior_variance=float(reference["obs_prior_variance"]),
            ),
        ),
    )
    problem = WorkflowFitProblem(
        y, u, prc.resolve_placeholders(u), obs.resolve_placeholders(u)
    )
    x0 = _array(reference["initial_free"]).reshape(-1)

    parameters = []
    for sample in reference["samples"]:
        parameter_index = int(sample["parameter_index_1based"]) - 1
        plus_results = evaluate_side(problem, x0, parameter_index, sample["x_plus"])
        minus_results = evaluate_side(problem, x0, parameter_index, sample["x_minus"])
        item = {
            "parameter_index_1based": parameter_index + 1,
            "steps": int(sample["stop_step"]),
            "plus": compare_side(plus_results, sample["plus"]),
            "minus": compare_side(minus_results, sample["minus"]),
        }
        parameters.append(item)
        print(
            json.dumps(
                {
                    "parameter": parameter_index + 1,
                    "plus_joint": item["plus"]["neg_log_joint"]["max_abs"],
                    "plus_log_likelihood": item["plus"]["log_likelihood"]["max_abs"],
                    "plus_trial_log_likelihoods": item["plus"]["trial_log_likelihoods"]["max_abs"],
                    "plus_perceptual_prior_terms": item["plus"]["perceptual_prior_terms"]["max_abs"],
                    "plus_observation_prior_terms": item["plus"]["observation_prior_terms"]["max_abs"],
                    "minus_joint": item["minus"]["neg_log_joint"]["max_abs"],
                    "minus_log_likelihood": item["minus"]["log_likelihood"]["max_abs"],
                    "minus_trial_log_likelihoods": item["minus"]["trial_log_likelihoods"]["max_abs"],
                    "minus_perceptual_prior_terms": item["minus"]["perceptual_prior_terms"]["max_abs"],
                    "minus_observation_prior_terms": item["minus"]["observation_prior_terms"]["max_abs"],
                }
            ),
            flush=True,
        )

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "classification": "DIAGNOSTIC_ONLY",
        "note": (
            "Exact-coordinate decomposition only; this does not alter any frozen M18 gate. "
            "If per-trial likelihoods and prior terms match while totals differ, investigate "
            "reduction/arithmetic order. Otherwise localize the first primitive component."
        ),
        "parameters": parameters,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
