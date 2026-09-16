"""Regression tests for portability findings from the independent v1 review."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import numpy as np

from hgfx.diagnostics.identifiability_validation import verify_frozen_m18
from hgfx.math import matlab_exp
from hgfx.responses import unitsq_sigmoid

ROOT = Path(__file__).resolve().parents[2]


def _load_reference_freeze_module():
    path = ROOT / "scripts/verify_reference_freeze.py"
    spec = importlib.util.spec_from_file_location("hgfx_verify_reference_freeze", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_theta_exp_is_independent_of_host_expm1(monkeypatch):
    """The frozen theta oracle must not inherit platform CRT expm1 rounding."""

    monkeypatch.setattr(matlab_exp.math, "expm1", lambda _x: 8.767706089455684)
    assert matlab_exp.matlab_theta_exp_scalar(2.2790816472336535) == np.float64(
        9.767706089455686
    )


def test_unitsq_normalizer_is_independent_of_numpy_vector_log(monkeypatch):
    """The active denominator log must use the scalar MATLAB-compatible path."""

    native_log = np.log

    def divergent_log(value):
        return np.nextafter(native_log(value), np.inf)

    monkeypatch.setattr(unitsq_sigmoid.np, "log", divergent_log)
    logp, _, _ = unitsq_sigmoid._core(
        np.asarray([0.0], dtype=np.float64),
        np.asarray([0.3085140203090296], dtype=np.float64),
        np.float64(48.000000000000014),
        irregular_trials=None,
    )
    assert logp[0] == np.float64(0.0)


def test_frozen_m18_result_hash_accepts_crlf_checkout(tmp_path):
    """Git line-ending conversion must not invalidate frozen text evidence."""

    source = ROOT / "reference/validation/m18_scientific_validation.json"
    crlf_copy = tmp_path / "m18_scientific_validation.json"
    crlf_copy.write_bytes(source.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert verify_frozen_m18(crlf_copy)


def test_frozen_m18_source_hash_accepts_crlf_checkout(monkeypatch):
    """Frozen source checksums must be based on canonical LF text."""

    source_paths = {
        (ROOT / relative).resolve()
        for relative in (
            "scripts/run_m18_scientific_validation.py",
            "src/hgfx/diagnostics/recovery.py",
        )
    }
    native_read_bytes = Path.read_bytes

    def crlf_read_bytes(path: Path):
        data = native_read_bytes(path)
        if path.resolve() in source_paths:
            return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        return data

    monkeypatch.setattr(Path, "read_bytes", crlf_read_bytes)
    assert verify_frozen_m18()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True
    ).strip()


def test_reference_freeze_uses_git_tree_not_working_tree_eol(tmp_path, monkeypatch, capsys):
    """Reference verification must ignore checkout-only CRLF expansion."""

    reference_freeze = _load_reference_freeze_module()
    sub = tmp_path / "hgf-toolbox"
    ref = tmp_path / "reference"
    sub.mkdir()
    ref.mkdir()
    subprocess.check_call(["git", "init", "-q", str(sub)])
    _git(sub, "config", "user.email", "test@example.invalid")
    _git(sub, "config", "user.name", "HGFX portability test")

    matlab = sub / "demo.m"
    canonical = b"function y = demo(x)\ny = x + 1;\nend\n"
    matlab.write_bytes(canonical)
    _git(sub, "add", "demo.m")
    _git(sub, "commit", "-q", "-m", "fixture")
    head = _git(sub, "rev-parse", "HEAD")
    blob = _git(sub, "rev-parse", "HEAD:demo.m")

    (ref / "matlab_manifest.tsv").write_text(
        f"path\tblob\tsize\ndemo.m\t{blob}\t{len(canonical)}\n",
        encoding="utf-8",
    )

    # Simulate a Windows checkout without changing the committed tree object.
    matlab.write_bytes(canonical.replace(b"\n", b"\r\n"))

    monkeypatch.setattr(reference_freeze, "SUB", sub)
    monkeypatch.setattr(reference_freeze, "REF", ref)
    monkeypatch.setattr(reference_freeze, "EXPECTED", head)

    reference_freeze.main()
    assert "Reference freeze verification: PASS" in capsys.readouterr().out
