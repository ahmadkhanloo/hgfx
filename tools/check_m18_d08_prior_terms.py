#!/usr/bin/env python3
"""Compare D08 Gaussian perceptual-prior terms against frozen MATLAB."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array

from hgfx.compat.objective import gaussian_log_prior
from hgfx.compat.workflows import resolve_config
from hgfx.core.placeholders import compute_placeholder_values


def array_cmp(actual, expected):
    a = np.asarray(actual, dtype=np.float64).reshape(-1)
    e = np.asarray(expected, dtype=np.float64).reshape(-1)
    if a.size != e.size:
        raise ValueError('Diagnostic array length mismatch')
    same = (a == e) | (np.isnan(a) & np.isnan(e))
    different = np.flatnonzero(~same)
    first = None
    if different.size:
        i = int(different[0])
        first = {"index": i, "hgfx": float(a[i]), "matlab": float(e[i]), "abs_diff": float(abs(a[i]-e[i]))}
    finite = np.isfinite(a) & np.isfinite(e)
    max_abs = float(np.max(np.abs(a[finite]-e[finite]))) if np.any(finite) else 0.0
    return {"exact": bool(not different.size), "first_difference": first, "max_abs_diff": max_abs}


def scalar_cmp(actual, expected):
    a = np.float64(actual); e = np.float64(expected)
    return {"hgfx": float(a), "matlab": float(e), "abs_diff": float(abs(a-e)), "exact": bool(a == e)}


def compare_placeholder(inputs, reference):
    if reference is None:
        return {"status": "UNAVAILABLE"}
    window = np.asarray(inputs, dtype=np.float64).reshape(-1)[:20]
    mean = np.float64(np.mean(window, dtype=np.float64))
    deviations = window - mean
    squared = deviations ** 2
    sequential_sum = np.float64(0.0)
    for value in squared:
        sequential_sum = np.float64(sequential_sum + value)
    values = compute_placeholder_values(inputs)
    actual = {
        'window': window,
        'mean': mean,
        'deviations': deviations,
        'squared_deviations': squared,
        'sum_squared_deviations': sequential_sum,
        'explicit_variance': sequential_sum / np.float64(window.size),
        'variance': values.var_first_20,
        'log_variance': values.log_var_first_20,
    }
    comparisons = {key: array_cmp(value, _array(reference[key])) for key, value in actual.items()}
    first = next((key for key, value in comparisons.items() if not value['exact']), None)
    return {'status': 'COMPARED', 'first_divergent_operation': first, 'operations': comparisons}


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d08-prior-terms-1":
        raise ValueError("Diagnostic protocol mismatch")

    u = _array(reference["inputs"]).reshape(-1)
    prc = resolve_config("uhgf").resolve_placeholders(u)
    free = _array(reference["sample_free"]).reshape(-1)
    free_full = _array(reference["free_full_indices_1based"]).astype(int).reshape(-1) - 1
    full = prc.priormus.copy()
    perceptual_free_count = sum(int(i) < len(prc.parameters) for i in free_full)
    for idx, value in zip(free_full[:perceptual_free_count], free[:perceptual_free_count], strict=True):
        full[int(idx)] = value

    matlab = reference["prior"]
    indices = _array(matlab["indices_1based"]).astype(int).reshape(-1) - 1
    parameters = full[indices]; means = prc.priormus[indices]; variances = prc.priorsas[indices]
    matlab_parameters = _array(matlab["parameters"]).reshape(-1)
    matlab_means = _array(matlab["means"]).reshape(-1)
    matlab_variances = _array(matlab["variances"]).reshape(-1)
    matlab_norm = _array(matlab["normalization_terms"]).reshape(-1)
    matlab_quad = _array(matlab["quadratic_terms"]).reshape(-1)
    matlab_terms = _array(matlab["terms"]).reshape(-1)
    matlab_total = np.float64(_array(matlab["total"]).reshape(-1)[0])

    current = gaussian_log_prior(full, prc.priormus, prc.priorsas)
    current_terms = np.asarray(current.terms, dtype=np.float64)
    current_norm = -np.float64(0.5) * np.log(np.float64(2.0) * np.pi * variances)
    current_quad = -np.float64(0.5) * (parameters-means) ** 2 / variances
    scalar_norm = np.asarray([-0.5*math.log(8.0*math.atan(1.0)*float(v)) for v in variances], dtype=np.float64)
    scalar_quad = np.asarray([-0.5*((float(p)-float(m))**2)/float(v) for p,m,v in zip(parameters,means,variances,strict=True)], dtype=np.float64)
    scalar_terms = scalar_norm + scalar_quad

    term_cmp = array_cmp(current_terms, matlab_terms)
    norm_cmp = array_cmp(current_norm, matlab_norm)
    quad_cmp = array_cmp(current_quad, matlab_quad)
    scalar_term_cmp = array_cmp(scalar_terms, matlab_terms)
    input_comparison = {
        "parameters": array_cmp(parameters, matlab_parameters),
        "means": array_cmp(means, matlab_means),
        "variances": array_cmp(variances, matlab_variances),
    }
    replay = gaussian_log_prior(matlab_parameters, matlab_means, matlab_variances)
    matched_input_replay = {"combined_terms": array_cmp(replay.terms, matlab_terms), "total": scalar_cmp(replay.total, matlab_total)}

    if not all(item['exact'] for item in input_comparison.values()):
        classification = "PRIOR_INPUT_DIVERGENCE"
    elif not term_cmp["exact"]:
        first = term_cmp["first_difference"]["index"]
        if not norm_cmp["exact"] and norm_cmp["first_difference"]["index"] == first:
            classification = "NORMALIZATION_TERM_DIVERGENCE"
        elif not quad_cmp["exact"] and quad_cmp["first_difference"]["index"] == first:
            classification = "QUADRATIC_TERM_DIVERGENCE"
        else:
            classification = "TERM_COMBINATION_DIVERGENCE"
    elif not scalar_cmp(current.total, matlab_total)["exact"]:
        classification = "PRIOR_REDUCTION_DIVERGENCE"
    else:
        classification = "NO_PRIOR_DIVERGENCE"

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D08_fit",
        "classification": classification,
        "constant_8atan1": scalar_cmp(np.float64(8.0*math.atan(1.0)), _array(matlab["constant_8atan1"]).reshape(-1)[0]),
        "inputs": input_comparison,
        "matched_input_replay": matched_input_replay,
        "placeholder": compare_placeholder(u, reference.get('placeholder')),
        "normalization_terms": norm_cmp,
        "quadratic_terms": quad_cmp,
        "combined_terms": term_cmp,
        "scalar_math_combined_terms": scalar_term_cmp,
        "total": scalar_cmp(current.total, matlab_total),
        "numpy_sum_matlab_terms": scalar_cmp(np.sum(matlab_terms, dtype=np.float64), matlab_total),
        "python_sequential_sum_matlab_terms": scalar_cmp(np.float64(sum(float(v) for v in matlab_terms)), matlab_total),
        "matlab_terms": [float(v) for v in matlab_terms],
        "hgfx_terms": [float(v) for v in current_terms],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
