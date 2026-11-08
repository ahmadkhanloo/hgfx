#!/usr/bin/env python3
"""REV-1.1: audit the original twelve S7 shard records; no fitting or resampling.

Accepts original GitHub Actions ZIPs or files extracted by actions/download-artifact.
Checks raw member hashes, input/case integrity, candidate BIC argmin, complete
coverage, and the committed evidence ledger. No scientific tolerance is changed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
from zipfile import ZipFile

MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
PROTOCOL = "m18-s7-paired-recovery-1"
EXPECTED = {(m, n, s) for m in MODELS for n in (128, 256) for s in (0.15, 0.35)}


def check(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def digest(b: bytes) -> str:
    return sha256(b).hexdigest()


def canonical(obj: object) -> str:
    return digest(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def read_pairs(directory: Path):
    zips = sorted(directory.rglob("m18-s7-shard-*.zip"))
    if zips:
        check(len(zips) == 12, f"expected 12 shard archives; found {len(zips)}")
        for archive in zips:
            with ZipFile(archive) as z:
                for ending in ("-manifest.json", "-comparison.json"):
                    check(sum(n.endswith(ending) for n in z.namelist()) == 1, "ambiguous ZIP member")
                mn = next(n for n in z.namelist() if n.endswith("-manifest.json"))
                cn = next(n for n in z.namelist() if n.endswith("-comparison.json"))
                yield (archive.name, z.read(mn), z.read(cn), digest(archive.read_bytes()))
    else:
        comps = sorted(directory.rglob("*-comparison.json"))
        check(len(comps) == 12, f"expected 12 extracted comparisons; found {len(comps)}")
        for comparison in comps:
            manifest = comparison.with_name(comparison.name.replace("-comparison.json", "-manifest.json"))
            check(manifest.exists(), f"missing matching manifest: {manifest}")
            yield (comparison.name.replace("-comparison.json", ".zip"),
                   manifest.read_bytes(), comparison.read_bytes(), None)


def winner(candidates: dict) -> tuple[str, float]:
    check(set(candidates) == set(MODELS), "candidate model set changed")
    valid = []
    for model in MODELS:
        item = candidates[model]
        if item["success"] and isinstance(item["BIC"], (float, int)) and math.isfinite(item["BIC"]):
            valid.append((model, float(item["BIC"])))
    check(bool(valid), "all candidate fits have invalid BIC")
    # Python's min preserves the reference candidate order on exact ties.
    return min(valid, key=lambda x: x[1])


def audit(directory: Path, expected: dict) -> dict:
    listed = {x["artifact"] : x for x in expected["raw_artifacts"]}
    rows = []
    inputs = {}
    strata = set()
    for name, manifest_bytes, comparison_bytes, zip_sha in read_pairs(directory):
        manifest = json.loads(manifest_bytes)
        comparison = json.loads(comparison_bytes)
        shard = manifest["shard"]
        key = (shard["model"], shard["trial_count"], shard["truth_scale"])
        check(key in EXPECTED and key not in strata, f"duplicate/invalid stratum {key}")
        strata.add(key)
        check(manifest["protocol"] == comparison["protocol"] == PROTOCOL, "protocol drift")
        check(shard == comparison["shard"], "comparison shard not identical")
        check(comparison["shard_contract_pass"] is True, "shard contract failed")
        check(manifest["shard_sha256"] ==
              canonical({k: v for k, v in manifest.items() if k != "shard_sha256"}),
              "stored manifest checksum mismatch")
        check(comparison["input_shard_sha256"] == manifest["shard_sha256"], "comparison input digest mismatch")
        check(name in listed, f"unknown raw archive {name}")
        pin = listed[name]
        check(digest(manifest_bytes) == pin["manifest_sha256"], "manifest SHA-256 drift")
        check(digest(comparison_bytes) == pin["comparison_sha256"], "comparison SHA-256 drift")
        if zip_sha is not None:
            check(zip_sha == pin["archive_sha256"], "artifact ZIP SHA-256 drift")
        cases = {case["case_id"]: case for case in manifest["model_cases"]}
        check(len(cases) == len(comparison["model_results"]) == 3, "missing model-recovery cases")
        check(len(comparison["parameter_results"]) == 6, "missing parameter-recovery cases")
        for row in comparison["model_results"]:
            cid = row["case_id"]
            check(cid in cases, f"unrecognized case {cid}")
            case = cases[cid]
            check(case["case_sha256"] == row["case_sha256"] ==
                  canonical({k: v for k, v in case.items()
                             if k not in {"case_sha256", "case_id", "generating_model", "candidate_models"}}),
                  f"case hash differs: {cid}")
            check(row["generating_model"] == case["generating_model"] == case["model"] == key[0],
                  f"generator mismatch: {cid}")
            check(case["candidate_models"] == list(MODELS), f"candidates changed: {cid}")
            check(case["trial_count"] == row["trial_count"] == key[1], "horizon mismatch")
            check(case["truth_scale"] == row["truth_scale"] == key[2], "scale mismatch")
            check(case["replicate"] == row["replicate"] in (0, 1, 2), "replicate mismatch")
            seed = 518018 + round(10000 * key[2]) + 1000000 * MODELS.index(key[0]) + 100 * key[1] + case["replicate"]
            check(case["seed"] == row["seed"] == seed and case["simulation_seed"] == seed + 1,
                  "model-specific deterministic seeds mismatch")
            check(len(case["u"]) == len(case["y"]) == len(case["response_probabilities"]) == key[1],
                  "input, response, or probability record truncated")
            mw, mb = winner(row["matlab_candidates"])
            hw, hb = winner(row["hgfx_candidates"])
            check(mw == row["matlab_selected_model"] and hw == row["hgfx_selected_model"], f"BIC argmin mismatch: {cid}")
            check(row["winner_match"] == (mw == hw), f"winner-match flag mismatch: {cid}")
            rows.append([cid, mw, hw])
            inputs[(key[0], key[1], key[2], case["replicate"])] = case

    check(strata == EXPECTED, f"incomplete original S7 grid: {EXPECTED - strata}")
    check(len(rows) == len(set(r[0] for r in rows)) == 36, "missing/duplicate selection record")
    rows.sort(key=lambda r: (MODELS.index(r[0].split("-")[1]), int(r[0].split("-T")[1].split("-")[0]),
                             float(r[0].split("-S")[1].split("-")[0]), int(r[0].rsplit("-R", 1)[1])))
    # The raw-case order is canonical; the evidence file stores every selected label.
    check(rows == expected["case_selections"], "published case-by-case selections do not match raw records")
    matrix = {}
    for idx, implementation in ((1, "matlab"), (2, "hgfx")):
        count = Counter((row[0].split("-")[1], row[idx]) for row in rows)
        a = [[count[(actual, chosen)] for chosen in MODELS] for actual in MODELS]
        check(all(sum(line) == 12 for line in a), "unbalanced or incomplete generating classes")
        matrix[implementation] = a
    paired = sum(r[1] == r[2] for r in rows)
    same = Counter()
    for n in (128, 256):
        for scale in (0.15, 0.35):
            for rep in range(3):
                a = inputs[("hgf_binary", n, scale, rep)]
                b = inputs[("uhgf_binary", n, scale, rep)]
                for label, key in (("same_seed", "seed"), ("same_input", "u"), ("same_response", "y"),
                                   ("same_truth_free", "truth_free"), ("same_probs", "response_probabilities")):
                    same[label] += int(a[key] == b[key])
                a_win = next(row[2] for row in rows if row[0] == a["case_id"])
                b_win = next(row[2] for row in rows if row[0] == b["case_id"])
                same["same_selected"] += int(a_win == b_win)
    check(matrix["matlab"] == expected["matlab_confusion_matrix_counts"], "MATLAB confusion mismatch")
    check(matrix["hgfx"] == expected["confusion_matrix_counts"], "HGFX confusion mismatch")
    check(paired == expected["paired_winners_match"], "paired winners mismatch")
    check(dict(same) == expected["paired_hgf_uhgf_diagnostics"], "HGF/uHGF raw-pair check mismatch")
    bacc = sum(matrix["hgfx"][i][i]/12 for i in range(3))/3
    check(bacc == expected["balanced_accuracy"], "balanced accuracy differs")
    return {"model_datasets": len(rows), "candidate_fits_per_implementation":len(rows)*3,
            "paired_winners":paired,"confusion_matrix":matrix,"balanced_accuracy":bacc,
            "pair_diagnostics":dict(same), "raw_shards":len(strata)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shard-dir", type=Path, required=True)
    ap.add_argument("--expected", type=Path,
                    default=Path("evidence/revision/confusion_audit.json"))
    args = ap.parse_args()
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    result = audit(args.shard_dir, expected)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("REV-1.1 raw-case reconstruction PASS; historical scientific M18 FAIL unchanged")


if __name__ == "__main__":
    main()
