from __future__ import annotations

import hashlib
import json
from pathlib import Path

SPEC_PATH = Path("paper/comparison/pyhgf_comparison_spec.json")
TABLE_PATH = "paper/tables/pyhgf_feature_design_matrix.md"
SEMANTIC_PATH = "paper/comparison/pyhgf_semantic_mapping.json"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _source_index(spec: dict) -> dict[str, dict]:
    return {item["id"]: item for item in spec["primary_sources"]}


def _evidence_links(ids: list[str], sources: dict[str, dict]) -> str:
    links = []
    for source_id in ids:
        source = sources[source_id]
        links.append(f'[{source_id}]({source["url"]})')
    return ", ".join(links)


def _build_table(spec: dict) -> str:
    sources = _source_index(spec)
    lines = [
        "# HGFX vs pyhgf 0.3.2 — feature/design matrix",
        "",
        f"Protocol: `{spec['protocol_id']}`  ",
        (
            "Comparator: "
            f"`{spec['comparator']['package']}=={spec['comparator']['version']}` / "
            f"`{spec['comparator']['git_tag']}` @ "
            f"`{spec['comparator']['git_commit']}`  "
        ),
        "",
        (
            "This matrix is descriptive, not a ranking. Different design objectives are "
            "reported as differences rather than strengths or defects. Direct numerical "
            "comparison is governed separately by the committed semantic gate."
        ),
        "",
        "| Dimension | HGFX v1.0.0 | pyhgf 0.3.2 | Comparability | Evidence |",
        "|---|---|---|---|---|",
    ]
    for item in spec["feature_dimensions"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    item["dimension"],
                    item["hgfx"],
                    item["pyhgf"],
                    item["comparability"],
                    _evidence_links(item["evidence"], sources),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            (
                "The feature matrix does not support a claim that either package is "
                "generally more accurate, faster, or better. The only direct numerical "
                "cell permitted by this P2A semantic gate is the narrowly frozen "
                "`fixed_parameter_three_level_binary_hgf_forward` cell; excluded "
                "surfaces remain `NOT_DIRECTLY_COMPARABLE`."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _build_semantic(spec: dict) -> str:
    mapping = dict(spec["semantic_mapping"])
    classification = mapping["classification"]
    payload = {
        "protocol_id": spec["protocol_id"],
        "candidate_surface": spec["candidate_surface"],
        "comparator": spec["comparator"],
        "hgfx": spec["hgfx"],
        "classification": classification,
        "empirical_comparison_permitted": classification == "PASS_FOR_COMMON_SCOPE",
        "scope_statement": mapping["scope_statement"],
        "not_directly_comparable_policy": mapping["not_directly_comparable_policy"],
        "configuration": mapping["configuration"],
        "checks": mapping["checks"],
        "excluded_direct_cells": mapping["excluded_direct_cells"],
        "primary_source_ids": [item["id"] for item in spec["primary_sources"]],
    }
    return _canonical_json(payload)


def build_outputs(root: Path) -> tuple[dict[str, str], dict]:
    spec_file = root / SPEC_PATH
    spec_text = spec_file.read_text(encoding="utf-8")
    spec = json.loads(spec_text)

    outputs = {
        TABLE_PATH: _build_table(spec),
        SEMANTIC_PATH: _build_semantic(spec),
    }
    manifest = {
        "protocol_id": spec["protocol_id"],
        "candidate_surface": spec["candidate_surface"],
        "comparator": {
            "package": spec["comparator"]["package"],
            "version": spec["comparator"]["version"],
            "git_tag": spec["comparator"]["git_tag"],
            "git_commit": spec["comparator"]["git_commit"],
            "sdist_sha256": spec["comparator"]["sdist_sha256"],
        },
        "classification": spec["semantic_mapping"]["classification"],
        "feature_dimensions": [item["id"] for item in spec["feature_dimensions"]],
        "inputs": [
            {
                "path": SPEC_PATH.as_posix(),
                "sha256": _sha256_text(spec_text),
            }
        ],
        "outputs": [
            {
                "path": relative,
                "sha256": _sha256_text(text),
            }
            for relative, text in sorted(outputs.items())
        ],
    }
    return outputs, manifest


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    outputs, manifest = build_outputs(root)
    for relative, text in outputs.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    manifest_path = root / "paper/comparison/p2a_manifest.json"
    manifest_path.write_text(_canonical_json(manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
