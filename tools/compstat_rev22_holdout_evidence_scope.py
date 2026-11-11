#!/usr/bin/env python3
"""Original D08 Ridders/BFGS artifact provenance audit. NO model/optimizer imports.

Read-only, fail closed. The historic seed-314159265 holdout cannot be promoted
to a seed-123456789 official D08 causal explanation. Original decisions retained.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

REF = "2437f4dc241541072722a2695ddeca7b44d83dd3"
SOURCES = {
    "official": {
        "id": 10339403480, "seed": 123456789,
        "protocol": "m18-d08-endpoint-diagnostic-2",
        "zip": "c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de",
        "source": ("m18_d08_endpoint.json", "d6c0182e60bdc3c418df533cf1f0077bd45114fb9df33cbcae248399f52448c2"),
        "comparison": ("m18_d08_endpoint_comparison.json", "f112129c29c36d208042fe9215b16147bedfd69a796a50a18fac59df4c25b409"),
    },
    "optimizer": {
        "id": 10347682339, "seed": 314159265,
        "protocol": "m18-d08-holdout-optimizer-probe-1",
        "zip": "3d94f74c71e5bf6bcdd8971d647ddba31f5a087cb4f3cb9a933c6a6e3c33518a",
        "source": ("m18_d08_holdout_optimizer_probe.json", "3299c36ef79d96b935ae3e0ef9a7d0ee037839e8b2bffb4bd8cf36cb2a192a31"),
        "comparison": ("m18_d08_holdout_optimizer_probe_comparison.json", "89020ab7313cac126cca36b43eeea4f264cd6bf3097dae9b3cf8a4e3a3a7bb61"),
    },
    "likelihood": {
        "id": 10346549885, "seed": 314159265,
        "protocol": "m18-d08-source-likelihood-probe-1",
        "zip": "4e763e9978cb409eca5c7b468d5798b3a832aa023e382731284b9af47fb61275",
        "source": ("m18_d08_source_likelihood_probe.json", "f5271f9d81556025659f29ce1f694992381fdcb34f78be675357f2774127afd9"),
        "comparison": ("m18_d08_source_likelihood_probe_comparison.json", "96f58fc0248ca5d0c5cf11c17fd4fab05ebeec5435f02ae628bc95b74dfd54b7"),
    },
    "sensitivity": {
        "id": 10348900752, "seed": 314159265,
        "protocol": "m18-d08-holdout-matlab-self-sensitivity-1",
        "zip": "42874a324ef408205452516f0abe7497b60d5f12b9f9bf2972df105845f907f6",
        "source": ("m18_d08_holdout_matlab_self_sensitivity.json", "d6144e5cef3631b889d4150e24b6e9f99eaacb9842810c633c289f95f906a1ab"),
        "comparison": ("m18_d08_holdout_matlab_self_sensitivity_comparison.json", "cb77f410e86b608778be7c59617713b8b03a982b7af233d772fb1456df05e2e7"),
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def read_source(path: Path, category: str) -> tuple[dict, dict]:
    spec = SOURCES[category]
    require(sha(path.read_bytes()) == spec["zip"], category + " ZIP SHA changed")
    with ZipFile(path) as z:
        require(set(z.namelist()) == {spec["source"][0], spec["comparison"][0]},
                category + " original members changed")
        parsed = []
        for name, expected in (spec["source"], spec["comparison"]):
            raw = z.read(name)
            require(sha(raw) == expected, category + " original member SHA changed")
            parsed.append(json.loads(raw))
    source, comparison = parsed
    require(source["protocol"] == comparison["protocol"] == spec["protocol"],
            category + " protocol mismatch")
    require(int(source["seed"]) == spec["seed"], category + " seed mismatch")
    if "seed" in comparison:
        require(int(comparison["seed"]) == spec["seed"],
                category + " comparison seed mismatch")
    require(source["reference_commit"] == comparison["reference_commit"] == REF,
            category + " reference commit mismatch")
    require(len(source["inputs"]) == len(source["responses"]) == 614,
            category + " original 614-response horizon changed")
    return source, comparison


def analyze(paths: dict[str, Path]) -> dict:
    records = {name: read_source(paths[name], name) for name in SOURCES}
    official, oldcmp = records["official"]
    optimizer, optcmp = records["optimizer"]
    likelihood, lhcmp = records["likelihood"]
    sensitivity, sncmp = records["sensitivity"]
    require(all(raw["inputs"] == official["inputs"] for raw, _ in records.values()),
            "Not the same public USDCHF source inputs")
    require(all(raw["responses"] != official["responses"]
                for name, (raw, _) in records.items() if name != "official"),
            "Holdout simulated responses identical to official: cannot assume distinct")
    require(oldcmp["classification"] == "ENDPOINT_SENSITIVITY",
            "Original official historical decision changed")
    trace = oldcmp["optimizer_trace"]
    exact = trace["first_exact_x_difference"]
    require(exact["index"] == [3, 0] and
            exact["abs_diff"] == 3.552713678800501e-15 and
            trace["first_gate_x_difference"] is None and
            trace["first_exact_rst_difference"] is None,
            "Official original historical trace no longer matches")
    require(optcmp["classification"] == "SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES",
            "Original holdout optimizer diagnosis was changed")
    trace = optcmp["full_trace"]
    require(trace["x"]["first_divergence"]["index_zero_based"] == [41, 4] and
            trace["val"]["first_divergence"]["index_zero_based"] == [56] and
            trace["rst"]["shape_mismatch"] is True and
            trace["rst"]["actual_shape"] == [9] and
            trace["rst"]["expected_shape"] == [7],
            "Holdout original fit path divergence changed")
    shared = optcmp["shared_state_window"]
    require([r["matlab_row_1based"] for r in shared] == list(range(38, 45)),
            "Shared holdout diagnostic window changed")
    require(all(r["objective_at_exact_matlab_x"]["gate_close"] and
                r["gradient_at_exact_matlab_x"]["gate_close"] for r in shared),
            "Holdout shared-state objective/gradient gate result changed")
    replay = optcmp["quasinewton_state_replay"]
    require(len(replay) == 6 and
            all(r["step_replay"]["gate_close"] and
                r["inverse_hessian_replay"]["gate_close"] for r in replay),
            "Holdout original quasi-Newton state replay changed")
    require(lhcmp["classification"] == "FORWARD_STATE_DIVERGENCE",
            "Original holdout internal-state non-bitwise failure must be preserved")
    internal = lhcmp["inf_states"]
    require(internal["exact"] is False and
            internal["max_abs_diff"] == 2.220446049250313e-16 and
            internal["first_difference"]["index"] == [400, 1, 2],
            "Holdout original internal-state first mismatch changed")
    require(all(lhcmp[k]["exact"] for k in
                ("observation_x", "trial_log_likelihoods", "yhat", "res")) and
            all(k["exact"] for k in lhcmp["primitives"].values()),
            "Original selected holdout likelihood primitive result changed")
    reduction = lhcmp["reductions"]
    require(reduction["numpy_vs_matlab_vector_abs_diff"] == 3.637978807091713e-12
            and reduction["compat_vs_matlab_vector_abs_diff"] == 0.0
            and reduction["scalar_loop_vs_matlab_scalar_abs_diff"] == 0.0,
            "Original holdout selected likelihood reduction result changed")
    require(sncmp["classification"] == "MATLAB_START_ULP_BASIN_SENSITIVE"
            and sncmp["baseline_reproduces_reference_final"] is True
            and sncmp["existing_gate"] == {"rtol": 3e-8, "atol": 3e-10}
            and len(sncmp["variants"]) == 14
            and sncmp["material_variant_count"] == 13
            and sum(v["final_within_existing_gate"] is False
                    for v in sncmp["variants"]) == 13,
            "Original holdout MATLAB 14-start ULP sensitivity outcome changed")
    return {
        "protocol": "REV22_D08_RIDDERS_HOLDOUT_PROVENANCE_READONLY_2026_11_11",
        "science_models_or_fits_executed": 0,
        "archives": {k: {"id": v["id"], "zip_sha256": v["zip"], "seed": v["seed"]}
                     for k, v in SOURCES.items()},
        "matlab_reference": REF,
        "same_public_usdchf_input_614": True,
        "same_simulated_responses_official_vs_holdout": False,
        "official": {"seed": 123456789, "first_exact_old_optimizer_x_index": exact["index"],
                     "first_exact_abs_difference": exact["abs_diff"],
                     "gate_level_optimizer_x_divergence": False,
                     "new_A_B_full_HGFX_trace_available": False},
        "holdout_optimizer": {
            "seed": 314159265,
            "original_classification": optcmp["classification"],
            "first_gate_x_index": [41, 4],
            "first_gate_val_index": [56],
            "original_reset_trace_lengths_hgfx_matlab": [9, 7],
            "shared_state_matlab_rows_one_based": list(range(38, 45)),
            "shared_state_max_gradient_abs_gap": max(
                r["gradient_at_exact_matlab_x"]["max_abs"] for r in shared),
            "shared_state_objectives_and_gradients_within_diagnostic_gate": True,
            "step_and_BFGS_replays_within_gate": 6,
        },
        "holdout_likelihood": {
            "original_classification": lhcmp["classification"],
            "first_internal_state_difference_index": [400, 1, 2],
            "max_internal_state_abs_gap": internal["max_abs_diff"],
            "observation_and_per_trial_loglikelihoods_exact_for_selected_sample": True,
            "normal_numpy_sum_matlab_vector_abs_gap": 3.637978807091713e-12,
            "compat_sum_matlab_vector_abs_gap": 0.0,
            "selected_off_center_sample_only": True,
        },
        "holdout_matlab_reference_sensitivity": {
            "original_classification": sncmp["classification"],
            "baseline_replayed_exact": True,
            "material_differences_one_ulp": 13,
            "total_one_ulp_start_variants": 14,
            "only_for_seed": 314159265,
        },
        "cross_seed_policy": {
            "classification": "HOLDOUT_EVIDENCE_NOT_TRANSFERABLE_TO_OFFICIAL_SEED",
            "first_causal_official_A_B_Ridders_or_BFGS_decision": "OPEN_NO_NEW_STEPWISE_TRACE",
            "new_D08_fits_allowed": False,
            "published_original_own_fit_failures_A_B": [4, 3],
            "original_M18_D08_direct_fail_preserved": True,
            "original_holdout_fail_preserved": True,
            "holdout_reference_limitation_only_exact_seed_314159265": True,
        },
        "scientific_status": "REV22_UNRESOLVED_DISCREPANCY",
        "rev24": "NOT_GLOBAL_PASS",
        "D2_D3": "BLOCKED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in SOURCES:
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Cannot overwrite derived scientific audit")
    result = analyze({k: getattr(args, k) for k in SOURCES})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                       allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({
        "classification": result["cross_seed_policy"]["classification"],
        "source_only": True,
        "official_seed": 123456789, "holdout_seed": 314159265,
        "holdout_BFGS_step_replays": 6, "MATLAB_one_ULP_material": "13/14",
        "new_official_BFGS_first_cause": "OPEN",
        "output_sha256": sha(args.output.read_bytes()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
