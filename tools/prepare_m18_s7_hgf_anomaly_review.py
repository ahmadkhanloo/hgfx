#!/usr/bin/env python3
"""Prepare the frozen exact-case input for the S7 HGF anomaly review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from hgfx.diagnostics.recovery import fit_binary_variant
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

PROTOCOL = "m18-s7-hgf-anomaly-review-1"
S7_PROTOCOL = "m18-s7-paired-recovery-1"
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
S7_EVIDENCE_HEAD = "2d274d358cc6fe94d08664d67b3d9287babb7b9d"

EXPECTED_SHARDS = {
    "hgf-t128-s015": "272431d73305be516b69ad233317ac69cb345c1eb9329ca340c44bb2f23a760f",
    "hgf-t256-s035": "0686d869c1a1660083b318b8411d722f87d9be12ec0a3c2d7be8e4dabd1d6606",
}

EXPECTED_CASES = {
    "PR-hgf_binary-T128-S0.15-R3": {
        "case_sha256": "e13c5efe72b43d951ed0ff6359b2f604cbd5bc8e4e333edfcc2519fba3b71fc0",
        "matlab_final": [-2.6150892895331053, -5.993242057216259, 4.463011892389776],
        "matlab_negLj": 6.622752693490324,
        "matlab_converged": False,
        "hgfx_final": [-2.615089289536023, -5.9932420572065235, 4.46301189238864],
        "hgfx_negLj": 6.6227526934902885,
        "hgfx_converged": True,
    },
    "PR-hgf_binary-T256-S0.35-R0": {
        "case_sha256": "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5",
        "matlab_final": [-1.681508358629877, -2.813834229811849, 4.040575231980671],
        "matlab_negLj": 13.292404684084028,
        "matlab_converged": True,
        "hgfx_final": [-1.6832085839490636, -2.807283698305754, 4.053638499739679],
        "hgfx_negLj": 13.294859618272989,
        "hgfx_converged": False,
    },
    "PR-hgf_binary-T256-S0.35-R4": {
        "case_sha256": "b2aeadf32705ff8cbbf90737611cf059d59f853b82ca44605dd6afe906e2aeca",
        "matlab_final": [-1.729182054270742, -3.756995925956133, 4.224706350948065],
        "matlab_negLj": 11.790436615859958,
        "matlab_converged": False,
        "hgfx_final": [-1.7009824622040677, -5.037546349956735, 4.208519462142309],
        "hgfx_negLj": 11.961671424898556,
        "hgfx_converged": False,
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest(path: Path, shard_id: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("protocol") != S7_PROTOCOL:
        raise ValueError(f"S7 protocol mismatch for {shard_id}")
    if payload.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError(f"MATLAB reference mismatch for {shard_id}")
    if payload.get("shard_sha256") != EXPECTED_SHARDS[shard_id]:
        raise ValueError(f"Frozen S7 shard hash mismatch for {shard_id}")
    return payload


def main(manifest_128: Path, manifest_256: Path, output_path: Path) -> int:
    manifests = {
        "hgf-t128-s015": _load_manifest(manifest_128, "hgf-t128-s015"),
        "hgf-t256-s035": _load_manifest(manifest_256, "hgf-t256-s035"),
    }
    by_case = {
        case["case_id"]: case
        for manifest in manifests.values()
        for case in manifest["parameter_cases"]
    }

    cases = []
    for case_id, expected in EXPECTED_CASES.items():
        case = by_case.get(case_id)
        if case is None:
            raise ValueError(f"Missing frozen anomaly case {case_id}")
        if case.get("case_sha256") != expected["case_sha256"]:
            raise ValueError(f"Case hash mismatch for {case_id}")
        if case.get("model") != "hgf_binary" or [int(i) for i in case["free_indices_zero_based"]] != [12, 13, 14]:
            raise ValueError(f"HGF/free-parameter contract mismatch for {case_id}")

        fit = fit_binary_variant(
            np.asarray(case["y"], dtype=np.float64),
            np.asarray(case["u"], dtype=np.float64),
            "hgf_binary",
            options=QuasiNewtonOptions(max_iter=100),
        )
        current = {
            "final_free": fit.final_free.tolist(),
            "negLj": float(fit.objective.neg_log_joint),
            "termination": fit.optimizer.termination,
            "converged": fit.optimizer.termination in {"tol_arg", "tol_grad"},
            "initial_free": fit.initial_full[np.asarray(fit.free_indices, dtype=np.int64)].tolist(),
            "free_indices_zero_based": list(fit.free_indices),
        }
        cases.append({
            "case_id": case_id,
            "case_sha256": case["case_sha256"],
            "seed": int(case["seed"]),
            "trial_count": int(case["trial_count"]),
            "truth_scale": float(case["truth_scale"]),
            "replicate": int(case["replicate"]),
            "u": case["u"],
            "y": case["y"],
            "free_indices_zero_based": [int(i) for i in case["free_indices_zero_based"]],
            "expected_s7": expected,
            "current_hgfx": current,
        })

    payload = {
        "protocol": PROTOCOL,
        "parent_protocol": S7_PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "s7_evidence_head": S7_EVIDENCE_HEAD,
        "source_manifest_sha256": {
            "hgf-t128-s015": _sha256(manifest_128),
            "hgf-t256-s035": _sha256(manifest_256),
        },
        "source_shard_sha256": EXPECTED_SHARDS,
        "existing_gate": {"rtol": 3e-8, "atol": 3e-10},
        "cases": cases,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"protocol": PROTOCOL, "cases": [c["case_id"] for c in cases]}))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_128", type=Path)
    parser.add_argument("manifest_256", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.manifest_128, args.manifest_256, args.output))
