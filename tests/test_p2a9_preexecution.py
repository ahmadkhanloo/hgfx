from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.check_p2a9_preexecution import canonical_bit_hash, validate_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "paper" / "reproducibility" / "pyhgf_common_scope_case.json"


def _load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_canonical_bit_hash_is_stable() -> None:
    assert canonical_bit_hash([0, 1, 0, 1]) == (
        "5b4415d7f76d878bd3f75318f9a44c7f2bac69f1807a72add77f1fa424aa28bd"
    )


def test_frozen_manifest_validates() -> None:
    validate_manifest(_load())


def test_manifest_freezes_exact_case_and_versions() -> None:
    data = _load()
    assert data["case_id"] == "p2a9-binary-hgf-common-scope-001"
    assert data["trial_contract"]["n_trials"] == 128
    assert len(data["inputs"]) == len(data["responses"]) == 128
    assert set(data["inputs"]) <= {0, 1}
    assert set(data["responses"]) <= {0, 1}
    assert data["environment"] == {
        "os": "ubuntu-24.04",
        "backend": "cpu",
        "python": "3.12.14",
        "numpy": "2.3.3",
        "jax": "0.6.2",
        "jaxlib": "0.6.2",
        "environment_variables": {
            "JAX_ENABLE_X64": "1",
            "JAX_PLATFORMS": "cpu",
        },
        "required_dtype": "float64",
        "full_resolved_environment_must_be_captured": True,
    }
    assert data["identities"]["hgfx_package"] == "hgfx==1.0.0"
    assert data["identities"]["pyhgf_package"] == "pyhgf==0.3.2"
    assert data["response_contract"]["inverse_temperature_native_ze"] == 48.0
    assert data["benchmark_authorized"] is False


def test_manifest_freezes_prospective_tolerances() -> None:
    data = _load()
    assert data["tolerances"]["trajectory_and_per_trial_quantities"] == {
        "atol": 1e-10,
        "rtol": 1e-8,
    }
    assert data["tolerances"]["participant_response_nll_total"] == {
        "atol": 1e-7,
        "rtol": 1e-8,
    }


def test_hash_change_is_rejected() -> None:
    data = _load()
    data["inputs"][0] = 1 - data["inputs"][0]
    with pytest.raises(ValueError, match="inputs_sha256"):
        validate_manifest(data)


def test_tolerance_change_is_rejected() -> None:
    data = _load()
    data["tolerances"]["trajectory_and_per_trial_quantities"]["rtol"] = 1e-4
    with pytest.raises(ValueError, match="tolerance"):
        validate_manifest(data)
