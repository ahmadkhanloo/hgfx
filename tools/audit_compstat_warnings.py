#!/usr/bin/env python3
"""REV-1.3: source-pinned warning cross-tab, without running a forward model.

Archived 324-case status ZIP supplies warning counts. The original public Reed
MAT supplies ONLY trial NaN masks and source arm labels, independently checked
against the immutable archived per-case ignored-trial counts.

The output contains aggregates and hashes, NOT raw participant-level data.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
from zipfile import ZipFile

import numpy as np
from scipy.io import loadmat

RUN_ID = 41809919116
ARTIFACT_ID = 13311622738
ZIP_SHA256 = "1adfd1cd69b6f7d7a89ba2c8b9d564e774fd8a8841fa7243d6972605bd9f7391"
STATUS_SHA256 = "47432c35aa4914a652a8f1dc2aad81dc4d76fb5175dd0fc1fd47532b81756b70"
REED_SOURCE_SHA256 = "b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708"
REED_COMMIT = "39ccaca508b81ca610e7666a613e061c801faaf9"
STUDIES = ("suthaharan_2021", "reed_2020")
ARMS = ("804020", "905010")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def archived_statuses(zip_path: Path) -> tuple[list[dict], dict]:
    raw = zip_path.read_bytes()
    require(digest(raw) == ZIP_SHA256, "historical Actions ZIP SHA-256 mismatch")
    with ZipFile(BytesIO(raw)) as z:
        require(z.namelist() == ["fullcohort_summary.json"],
                "unexpected/missing status file in historical artifact")
        encoded = z.read("fullcohort_summary.json")
    require(digest(encoded) == STATUS_SHA256, "historical status SHA-256 mismatch")
    summary = json.loads(encoded)
    require(summary["github_run_id"] == str(RUN_ID), "wrong historical run")
    require(summary["overall_status"] == "PASS_FIXED_VECTOR_PARITY_ALL_CASES",
            "different historical forward evidence")
    require(summary["expected_cases"] == summary["total_cases"] == 324,
            "source cohort denominator modified")
    require(summary["trials_in_source_grid"] == 25920 and
            summary["total_failed_elements"] == 0, "historical grid/evidence modified")
    require(summary["hgfx_wheel"] == "1.0.0", "wrong released wheel")
    require(summary["warning_case_count"] == 48, "historical warning case count modified")
    rows = summary["per_case_statuses"]
    require(len(rows) == 324, "missing archived case statuses")
    expected_ids = ([f"suthaharan_2021_{i:04d}" for i in range(1, 261)] +
                    [f"reed_2020_{i:04d}" for i in range(1, 65)])
    require([x["id"] for x in rows] == expected_ids, "archived case ordering/IDs changed")
    for x in rows:
        require(x["study"] in STUDIES and
                x["status"] == "PASS_FIXED_VECTOR_FORWARD_PARITY" and
                not x["failed_fields"] and x["first_divergence"] is None,
                "historical case status changed")
        require(type(x["ignored_trials"]) is int and
                type(x["warnings"]) is int and
                0 <= x["ignored_trials"] <= 80 and x["warnings"] >= 0,
                "negative/invalid counts")
    return rows, summary


def reed_masks(mat_path: Path, rows: list[dict]) -> tuple[dict, dict]:
    raw = mat_path.read_bytes()
    require(len(raw) <= 1024*1024 and digest(raw) == REED_SOURCE_SHA256,
            "original Reed source bytes differ from the pinned data")
    source = loadmat(BytesIO(raw), squeeze_me=False)
    keys = []
    pattern = re.compile(r"^(P\d+)_choices_(804020|905010)$")
    for key in source:
        match = pattern.fullmatch(key)
        if match is not None:
            person, arm = match.groups()
            keys.append((person, arm))
    keys.sort(key=lambda x: (int(re.search(r"\d+", x[0]).group()), x[1]))
    require(len(keys) == 64 and len(set(keys)) == 64,
            "unexpected Reed 64-block source enumeration")
    persons = {person for person, arm in keys}
    require(len(persons) == 32, "Reed source has an unexpected person count")
    require(all({arm for p, arm in keys if p == person} == set(ARMS)
                for person in persons), "Reed source missing an arm")
    require(len(rows) == 64, "wrong original Reed status denominator")
    derived = {}
    source_detail = {"source_sha256": digest(raw), "source_commit": REED_COMMIT,
                     "expected_people": 32, "expected_blocks": 64}
    for i, (person, arm) in enumerate(keys):
        row = rows[i]
        expected_id = f"reed_2020_{i+1:04d}"
        require(row["id"] == expected_id, "source/status block order mismatch")
        outcome_key = f"{person}_outcomes_{arm}"
        choice_key = f"{person}_choices_{arm}"
        require(outcome_key in source and choice_key in source,
                "original source variable missing")
        outcome = np.asarray(source[outcome_key], dtype=np.float64)
        choice = np.asarray(source[choice_key], dtype=np.float64)
        require(outcome.shape == (80, 1) and choice.shape == (80, 1),
                "original source 80x1 shape changed")
        u, y = outcome[:, 0], choice[:, 0]
        require(not np.isinf(u).any() and not np.isinf(y).any() and
                np.all(np.isin(u[np.isfinite(u)], [0, 1])) and
                np.all(np.isin(y[np.isfinite(y)], [1, 2, 3])),
                "original source numeric coding changed")
        mask = np.flatnonzero(np.isnan(u) | np.isnan(y))
        require(len(mask) == row["ignored_trials"],
                f"archived missing-trial count differs from source for {expected_id}")
        derived[expected_id] = {
            "arm": arm,
            "first_index": int(mask[0]) if mask.size else None,
            "positions": [int(x) for x in mask],
        }
    return derived, source_detail


def table(rows: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row.get(field) for field in key_fields)
        if key not in grouped:
            grouped[key] = {**dict(zip(key_fields, key)),
                            "blocks": 0, "warning_blocks": 0, "warning_events": 0,
                            "ignored_trials_total": 0}
        group = grouped[key]
        group["blocks"] += 1
        group["warning_blocks"] += bool(row["warnings"])
        group["warning_events"] += row["warnings"]
        group["ignored_trials_total"] += row["ignored_trials"]
    return sorted(grouped.values(), key=lambda row:
                  tuple("" if row[f] is None else str(row[f]) for f in key_fields))


def audit(zip_path: Path, reed_mat_path: Path) -> dict:
    rows, summary = archived_statuses(zip_path)
    reed_rows = [r for r in rows if r["study"] == "reed_2020"]
    derived, reed = reed_masks(reed_mat_path, reed_rows)
    enriched = []
    for r in rows:
        d = derived.get(r["id"], None)
        enriched.append({
            "study": r["study"],
            "arm": d["arm"] if d else "unavailable_in_archived_status",
            "ignored_trials": r["ignored_trials"],
            "first_ignored_index_zero_based": d["first_index"] if d else None,
            "warnings": r["warnings"],
        })
    with_warning = [r for r in enriched if r["warnings"] > 0]
    warning_events = sum(r["warnings"] for r in enriched)
    mult = Counter(r["warnings"] for r in enriched)
    require(len(with_warning) == 48 and warning_events == 86 and
            mult == Counter({0: 276, 1: 29, 3: 19}),
            "original 48 case/86 event (29x1,19x3) count did not reproduce")
    require(sum(r["ignored_trials"] for r in enriched) == 293,
            "historical 293 ignored source trials did not reproduce")
    require(all(r["study"] == "reed_2020" and r["ignored_trials"] > 0
                for r in with_warning), "unexpected warning source/masking association")
    require(all(r["warnings"] == 0 for r in enriched if r["ignored_trials"] == 0),
            "warnings in a non-ignored source block")
    require(len([r for r in enriched if r["ignored_trials"] > 0]) == 48,
            "unexpected ignored-trial case count")
    require(all(r["ignored_trials"] == 0 for r in enriched
                if r["study"] == "suthaharan_2021"), "unreconstructed Suthaharan masks")
    # Include all ignored indices, not merely the first: aggregate position counts
    # without exposing participant-level response or mask arrays.
    idxs = Counter()
    arm_idxs = Counter()
    for key, record in derived.items():
        is_warning = next(x["warnings"] > 0 for x in reed_rows if x["id"] == key)
        for idx in record["positions"]:
            idxs[(idx, is_warning)] += 1
            arm_idxs[(record["arm"], idx, is_warning)] += 1
    require(sum(idxs.values()) == 293 and sum(arm_idxs.values()) == 293,
            "ignored position counts do not cover all original masks")
    position_counts = [{"index_zero_based": i, "index_one_based": i+1,
                        "ignored_occurrences": sum(count for (pos, warn), count
                                                   in idxs.items() if pos == i),
                        "in_warning_blocks": idxs[(i, True)]}
                       for i in range(80) if any(k[0] == i for k in idxs)]
    arm_positions = [
        {"arm": arm, "index_zero_based": i, "index_one_based": i+1,
         "ignored_occurrences": arm_idxs[(arm, i, True)] +
                                arm_idxs[(arm, i, False)]}
        for arm in ARMS for i in range(80)
        if arm_idxs[(arm, i, True)] or arm_idxs[(arm, i, False)]
    ]
    result = {
        "task": "REV-1.3",
        "scope": "archived 324-block fixed-vector perceptual-forward parity warnings; NOT study fitting",
        "status": "SOURCE_AUDITED_DESCRIPTIVE_ONLY",
        "no_forward_execution": True,
        "archive": {
            "github_run_id": RUN_ID, "artifact_id": ARTIFACT_ID,
            "archive_sha256": ZIP_SHA256,
            "status_member_sha256": STATUS_SHA256,
            "source_hgfx_wheel": summary["hgfx_wheel"],
            "frozen_m12b_criteria": summary["criteria"],
        },
        "reed_input": reed,
        "historical_source_gate": {
            "failed_pre_experiment_run": 41809479255,
            "original_plan_cases": 326,
            "source_verified_cases": 324,
        },
        "denominator": 324, "suthaharan_blocks": 260, "reed_blocks": 64,
        "trial_count_per_block": 80,
        "blocks_with_ignored_trials": 48,
        "ignored_trials_total": 293,
        "warning_blocks": 48, "warning_events": 86,
        "warning_count_distribution": {str(k):v for k,v in sorted(mult.items())},
        "all_warning_blocks_reed": True,
        "all_warning_blocks_have_ignored_trial": True,
        "all_ignored_trial_blocks_have_warning": True,
        "per_block_rows_published": False,
        "cross_tabs": {
            "study": table(enriched, ("study",)),
            "ignored_count": table(enriched, ("ignored_trials",)),
            "study_by_ignored_count": table(enriched, ("study","ignored_trials")),
            "reed_arm": table([r for r in enriched if r["study"] == "reed_2020"], ("arm",)),
            "reed_arm_by_ignored_count":
                table([r for r in enriched if r["study"] == "reed_2020"],
                      ("arm","ignored_trials")),
            "first_ignored_index_zero_based":
                table([r for r in enriched if r["study"] == "reed_2020"],
                      ("first_ignored_index_zero_based",)),
            "reed_arm_by_first_ignored_index":
                table([r for r in enriched if r["study"] == "reed_2020"],
                      ("arm", "first_ignored_index_zero_based")),
            "all_ignored_trial_position_occurrences": position_counts,
            "reed_arm_position_occurrences": arm_positions,
        },
        "interpretation_limits": [
            "Warning-count associations with ignored trials are descriptive only, not causes.",
            "The historical 324-block aggregate did not retain Python warning message categories.",
            "Numerical/overflow/masking mechanism remains unknown; investigate under REV-2.1 after D1.",
            "Original published HGF model fits and clinical/group findings were not reproduced.",
            "No individual participant choice/outcome or participant mask is included in this report.",
            "Source-arm labels are reconstructed only for original Reed blocks using pinned data.",
            "Suthaharan arm labels are unavailable from the historical status archive.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--reed-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    result = audit(a.archive, a.reed_source)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                   allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "warning_blocks": result["warning_blocks"],
                      "warning_events": result["warning_events"],
                      "source_sha256": result["reed_input"]["source_sha256"],
                      "output": str(a.output)}, indent=2))


if __name__ == "__main__":
    main()
