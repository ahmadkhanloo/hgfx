#!/usr/bin/env python3
"""Read-only SHA-guarded official-seed D08 historical Ridders/Armijo audit.

No hgfx, JAX, MATLAB, gradient, forward, Ridders or optimizer import/call.
Audit precommitted in REV-2.2_D08_OFFICIAL_RIDDERS_ARMIJO_ARCHIVE_AUDIT_PROTOCOL_2026-11-11.md.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

REF = "2437f4dc241541072722a2695ddeca7b44d83dd3"
OLD_DEV_HEAD = "d360fcd45c996c21ab482d1cd6b45dea6d65574f"
WHEEL = "5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90"
INPUT_SHA = "4516d5906a115817386e63ae8b4bb2a97618c90a867965176f6364833eb7d2bc"
RESPONSE_SHA = "a9dbfefc6cabe51ef26f0669838d0d57b4ed8bf35e7c9d90b5cc8407c2347307"
SRC = {
    "endpoint": {
        "run": 34823572192, "artifact": 10339403480,
        "sha": "c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de",
        "reference": ("m18_d08_endpoint.json",
                      "d6c0182e60bdc3c418df533cf1f0077bd45114fb9df33cbcae248399f52448c2"),
        "comparison": ("m18_d08_endpoint_comparison.json",
                       "f112129c29c36d208042fe9215b16147bedfd69a796a50a18fac59df4c25b409"),
    },
    "ridders": {
        "run": 34839730540, "artifact": 10345886333,
        "sha": "9ab1f959e8cc3b73db96876cdb0b5a909525e0290da475e9ea1e7c1904795441",
        "reference": ("m18_d08_ridders_probe.json",
                      "63b965a4573d712987e20674827ebc9dca08db0315e473a93f68d89e3ea989c7"),
        "comparison": ("m18_d08_ridders_probe_comparison.json",
                       "14fe5598b667ebf0f1d2fe76b5e37b379639b6e9a1db5b70adb1f477de2786e6"),
    },
    "transition": {
        "run": 34839730793, "artifact": 10345846351,
        "sha": "2e501c383b6d07b38334088ae87b8bf633e9469d140f1c491d2fef98de386167",
        "reference": ("m18_d08_transition.json",
                      "1fa74e64b134af041951a98d332b25554150e781efc5f534ef2fb174dfc60cd4"),
        "comparison": ("m18_d08_transition_comparison.json",
                       "89d15ce3b0e016e1932f441f766fd8cc2ab85fd091a1bbade55f22eb1602c39d"),
    },
    "sensitivity": {
        "run": 34839730880, "artifact": 10346050821,
        "sha": "6a913f5ac4646c44a056a9dba78deaf9db8aae5abc78c900e8451620c37cb4e4",
        "reference": ("m18_d08_official_matlab_self_sensitivity.json",
                      "2e70cd5146fd69c10f1194d7092197267b3a9401e950f7ed81c57894c8f11c61"),
        "comparison": ("m18_d08_official_matlab_self_sensitivity_comparison.json",
                       "4613bfe1bb1d8ce6d4f6de60667f618d5b35e98f2e70b6433ee8242a480433f2"),
    },
    "new_A": {
        "run": 42910756224, "artifact": 13808150860,
        "sha": "a2864f8729d9e856eb3454cf1fbf4c26c08cd217695e58b79950cec2ac5b3534",
        "reference": ("matlab_reference.json",
                      "5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165"),
        "hgfx": ("hgfx_published_wheel.json",
                 "d06a2f961a27f73a9c38621a86fe2204aebb481f2857ce45368e176111a9f37d"),
        "cross": ("matlab_cross_evaluation.json",
                  "8bdcad1f1c2c6bc628eb6622c258188343025136df9a345e7fb2a84da5d9f9b9"),
        "comparison": ("paired_d08_comparison.json",
                       "0304d8366c497d1e03cf9b75da1670a8a2d09e06979c064098cdd4e062595440"),
    },
}


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(raw):
    return sha256(raw).hexdigest()


def get_source(path, label):
    record = SRC[label]
    check(digest(path.read_bytes()) == record["sha"], label + ": archive SHA drift")
    manifest = {pair[0]: pair[1] for name, pair in record.items()
                if name in ("reference", "comparison", "hgfx", "cross")}
    with ZipFile(path) as z:
        check(set(z.namelist()) == set(manifest), label + ": archive members changed")
        result = {}
        for name, hashvalue in manifest.items():
            raw = z.read(name)
            check(digest(raw) == hashvalue, label + ": " + name + " SHA drift")
            result[name] = json.loads(raw)
    return result


def number_array(value):
    if isinstance(value, dict):
        check(value.get("hgfx_numeric") == "ieee-strings-v1",
              "Unsupported MATLAB IEEE transport")
        shape = tuple(int(v) for v in value["shape"])
        data = np.asarray(value["data"], dtype=np.float64)
        check(np.prod(shape) == data.size, "MATLAB shape/array corruption")
        return data.reshape(shape, order="F")
    return np.asarray(value, dtype=np.float64)


def binary64_sha(value):
    values = number_array(value).reshape(-1, order="F")
    check(values.size == 614 and np.all(np.isfinite(values)),
          "Wrong/incomplete 614 input/response array")
    return digest(np.asarray(values, dtype="<f8").tobytes())


def float_exact(a, b):
    return float(a) == float(b)


def audit(paths):
    data = {key: get_source(paths[key], key) for key in SRC}
    official = data["endpoint"]["m18_d08_endpoint.json"]
    historic_cmp = data["endpoint"]["m18_d08_endpoint_comparison.json"]
    ridders = data["ridders"]["m18_d08_ridders_probe.json"]
    rc = data["ridders"]["m18_d08_ridders_probe_comparison.json"]
    trans = data["transition"]["m18_d08_transition.json"]
    tc = data["transition"]["m18_d08_transition_comparison.json"]
    sensitivity = data["sensitivity"]["m18_d08_official_matlab_self_sensitivity.json"]
    sc = data["sensitivity"]["m18_d08_official_matlab_self_sensitivity_comparison.json"]
    newref = data["new_A"]["matlab_reference.json"]
    newest = data["new_A"]["hgfx_published_wheel.json"]
    latest_cmp = data["new_A"]["paired_d08_comparison.json"]
    original_sets = [official, ridders, trans, sensitivity, newref]
    for name, item in zip(SRC, original_sets):
        check(item.get("reference_commit") == REF and int(item["seed"]) == 123456789,
              name + ": wrong official seed or MATLAB version/source")
        check(binary64_sha(item["inputs"]) == INPUT_SHA and
              binary64_sha(item["responses"]) == RESPONSE_SHA,
              name + ": 614 input/response identity mismatch")
        check(item.get("matlab_version", "").find("R2026a") >= 0 if name != "new_A"
              else "R2026b" in item.get("matlab_version", ""),
              name + ": MATLAB source runtime mismatch")
    check(historic_cmp["protocol"] == "m18-d08-endpoint-diagnostic-2" and
          historic_cmp["optimizer_trace"]["first_exact_x_difference"]["index"] == [3, 0] and
          float_exact(historic_cmp["optimizer_trace"]["first_exact_x_difference"]["abs_diff"],
                      3.552713678800501e-15) and
          historic_cmp["optimizer_trace"]["first_gate_x_difference"] is None,
          "Preserved official M18 exact/gate-level divergence changed")
    check(rc["protocol"] == ridders["protocol"] == "m18-d08-ridders-probe-1" and
          rc["classification"] == "NO_RIDDERS_DIVERGENCE" and
          rc["source_trace_row_zero_based"] == 2 and
          rc["component_free_index_zero_based"] == 0 and
          rc["stop_step"] == 11 and len(rc["samples"]) == 11,
          "Frozen selected official Ridders scope/status changed")
    for step in rc["samples"]:
        for side in ("plus", "minus"):
            check(step[side]["objective"]["exact"] is True and
                  all(component["exact"] is True
                      for component in step[side]["decomposition"].values()),
                  "Original Ridders sample objective/decomposition differs")
    check(rc["first_objective_difference"] is None and
          rc["max_objective_difference"]["abs_diff"] == 0 and
          all(rec["exact"] is True
              for group in ("selected_derivative", "selected_error")
              for key, rec in rc[group].items() if isinstance(rec, dict) and "exact" in rec) and
          rc["diagonal_replay"]["matlab_samples"]["max_abs_vs_exported"] == 0.0 and
          rc["diagonal_replay"]["hgfx_samples_max_abs_vs_matlab_exported"] == 0.0,
          "Ridders selected derivative/error or extrapolation mismatch")
    check(tc["protocol"] == trans["protocol"] == "m18-d08-transition-diagnostic-1" and
          tc["classification"] == "NO_TRANSITION_DIVERGENCE" and
          tc["source_trace_row_zero_based"] == 2 and
          tc["target_trace_row_zero_based"] == 3,
          "Frozen official transition scope/result changed")
    check(all(tc["source"][field]["exact"] is True
              for field in ("x", "stored_val", "objective_replay_at_exact_matlab_x",
                            "inverse_hessian", "gradient", "gradient_error")),
          "Historical selected BFGS state differs from original source")
    check(tc["target_live_trace"]["x"]["exact"] is True and
          tc["target_live_trace"]["val"]["exact"] is True and
          len(tc["matlab_candidate_objective_replay"]) == 17 and
          all(item["exact"] is True for item in tc["matlab_candidate_objective_replay"]),
          "Historical Armijo source candidates or accepted live target changed")
    check(len(tc["transition_variants"]) == 4 and
          all(case["accepted_j"]["exact"] and case["accepted_j"]["hgfx"] == 2
              and case["accepted_x_vs_stored_target"]["exact"]
              and case["accepted_val_vs_stored_target"]["exact"]
              for case in tc["transition_variants"].values()),
          "Original 4 transition variants must accept identical j=2 target")
    check(sc["classification"] == "NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED" and
          sc["protocol"] == sensitivity["protocol"] ==
          "m18-d08-official-matlab-self-sensitivity-1" and
          sc["seed"] == 123456789 and sc["baseline_reproduces_official_final"] is True
          and sc["existing_gate"] == {"rtol": 3e-8, "atol": 3e-10}
          and sc["material_variant_count"] == 0 and
          sc["material_variants"] == [] and len(sc["variants"]) == 14 and
          all(v["start_contract_ok"] and v["final_within_existing_gate"]
              for v in sc["variants"]),
          "Official seed MATLAB self-start ULP sensitivity original status changed")
    check(newest["wheel_sha256"] == WHEEL and
          newest["termination"] == "NOT_EXPORTED" and
          "iter" not in newest and
          latest_cmp["classification"] == "UNRESOLVED_DISCREPANCY" and
          latest_cmp["direct_existing_scope_pass"] is False,
          "New released-Wheel D08 A original failure/trace status changed")
    return {
        "protocol": "REV22_D08_OFFICIAL_RIDDERS_ARMIJO_ARCHIVES_READONLY_2026_11_11",
        "new_scientific_evaluations": 0,
        "original_artifact_provenance": {
            key: {"run": value["run"], "artifact": value["artifact"],
                  "zip_sha256": value["sha"]}
            for key, value in SRC.items()
        },
        "source_data": {
            "matlab_reference_commit": REF,
            "official_seed": 123456789,
            "input_sha256_binary64": INPUT_SHA,
            "response_sha256_binary64": RESPONSE_SHA,
            "n_inputs_responses": 614,
            "historical_matlab": "R2026a Update 5",
            "new_A_matlab": "R2026b Update 1",
        },
        "historical_editable_development_source": {
            "git_head_for_three_diagnostics": OLD_DEV_HEAD,
            "not_the_published_v1_0_0_wheel": True,
            "source_release_cross_version_inference_permitted": False,
        },
        "official_historical_Ridders_single_selected_state": {
            "selected_source_row_zero_based": 2,
            "selected_free_component_zero_based": 0,
            "steps": 11,
            "exact_objective_plus_minus_samples": 22,
            "max_abs_objective_sample_difference": 0.0,
            "selected_derivative_and_error_exact": True,
            "classification": rc["classification"],
            "scope": "ONE_SELECTED_POINT_AND_ONE_FREE_COMPONENT_NOT_ALL_ITERATIONS",
        },
        "official_historical_Armijo_BFGS_selected_transition": {
            "source_row_zero_based": 2, "target_row_zero_based": 3,
            "exact_matlab_candidate_objectives": 17,
            "all_four_stored_transition_variants_accepted_j": 2,
            "accepted_points_and_values_exact": True,
            "source_x_value_invH_gradient_and_error_exact": True,
            "some_intermediate_arithmetic_nonbitwise_possible": True,
            "classification": tc["classification"],
        },
        "official_historical_MATLAB_start_ULP": {
            "variants": 14,
            "material_outside_original_yardstick": 0,
            "max_gate_ratio": max(float(item["final_comparison"]["max_gate_ratio"])
                                  for item in sc["variants"]),
            "classification": sc["classification"],
            "holdout_13_of_14_must_not_be_transferred_to_official_seed": True,
        },
        "original_M18_historical_first_exact_optimizer_x_diff": {
            "index_zero_based": [3, 0],
            "abs_diff": 3.552713678800501e-15,
            "gate_level_x_divergence": False,
            "different_original_archived_execution_from_selected_state_probe": True,
        },
        "new_published_wheel": {
            "wheel_sha256": WHEEL,
            "A_own_fit_original_direct_status": "UNRESOLVED_DISCREPANCY",
            "A_original_eps_bad_count": 4,
            "B_original_eps_bad_count": 3,
            "new_A_B_full_stepwise_HGFX_optimizer_history_available": False,
            "first_causal_new_A_B_gradient_Armijo_BFGS_decision": "NOT_OBSERVED",
        },
        "scientific_claim": "HISTORICAL_OFFICIAL_SELECTED_STEPS_MATCH_ONLY__NEW_BFGS_CAUSE_OPEN",
        "rev22": "IN_PROGRESS_UNRESOLVED_DISCREPANCY",
        "rev24": "NOT_GLOBAL_PASS",
        "d2_d3": "BLOCKED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for label in SRC:
        parser.add_argument("--" + label.replace("_", "-").lower(),
                            dest=label, type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists(), "Refuse overwrite of immutable derived audit")
    source_paths = {key: getattr(args, key) for key in SRC}
    result = audit(source_paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                       allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["scientific_claim"],
        "historical_official_Ridders_exact_samples": 22,
        "historical_official_Armijo_exact_candidates": 17,
        "official_matlab_one_ULP_material": "0/14",
        "source_versions_not_equated": True,
        "new_model_executions": 0,
        "sha256": digest(args.output.read_bytes()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
