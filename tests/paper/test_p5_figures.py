from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper" / "scripts" / "generate_p5_figures.py"
EXPECTED = {
    "fig_recovery_metrics.png",
    "fig_model_selection.png",
    "fig_pyhgf_common_scope.png",
    "fig_evidence_classes.png",
    "fig_gpu_applicability.png",
}


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p5_figures", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_p5_writes_manifest_and_pngs(tmp_path: Path) -> None:
    generator = load_generator()
    # generate into the real repo; hashes must be stable across two runs
    first = generator.build(ROOT)
    second = generator.build(ROOT)
    assert first["protocol_id"] == "hgfx-paper-protocol-1"
    assert set(first["figures"]) == EXPECTED
    assert first["figures"] == second["figures"]
    for name, meta in first["figures"].items():
        path = ROOT / meta["path"]
        assert path.is_file()
        assert path.stat().st_size > 1000
    manifest = json.loads((ROOT / "paper/figures/p5_figures_manifest.json").read_text(encoding="utf-8"))
    assert manifest["inputs"]
    assert "P4 performance" in " ".join(manifest["notes"])
