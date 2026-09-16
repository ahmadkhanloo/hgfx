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


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True
    ).strip()


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


def test_frozen_m18_files_are_lf_enforced_and_hash_clean():
    """Git must materialize raw-hashed M18 evidence with canonical LF bytes."""

    for relative in (
        "scripts/run_m18_scientific_validation.py",
        "src/hgfx/diagnostics/recovery.py",
        "reference/validation/m18_scientific_validation.json",
    ):
        attr = _git(ROOT, "check-attr", "eol", "--", relative)
        assert attr.endswith(": eol: lf")
    assert verify_frozen_m18()


def test_reference_freeze_ignores_checkout_only_crlf(tmp_path, monkeypatch, capsys):
    """Submodule verification must ignore CRLF expansion but detect content changes."""

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

    # Simulate a Windows checkout without changing canonical source content.
    matlab.write_bytes(canonical.replace(b"\n", b"\r\n"))

    monkeypatch.setattr(reference_freeze, "SUB", sub)
    monkeypatch.setattr(reference_freeze, "REF", ref)
    monkeypatch.setattr(reference_freeze, "EXPECTED", head)

    reference_freeze.main()
    assert "Reference freeze verification: PASS" in capsys.readouterr().out

    # A semantic change must still fail after line-ending canonicalization.
    matlab.write_bytes(canonical.replace(b"x + 1", b"x + 2"))
    try:
        reference_freeze.main()
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("semantic MATLAB source change was not detected")
