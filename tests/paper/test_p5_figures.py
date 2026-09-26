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
    "fig_p3_horizon_diagnostics.png",
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
    out = tmp_path / "figures"
    first = generator.build(ROOT, output_dir=out)
    second = generator.build(ROOT, output_dir=out)
    assert first["protocol_id"] == "hgfx-paper-protocol-1"
    assert set(first["figures"]) == EXPECTED
    assert first["figures"] == second["figures"]
    for name, meta in first["figures"].items():
        path = out / Path(meta["path"]).name
        assert path.is_file()
        assert path.stat().st_size > 1000
        pdf = path.with_suffix(".pdf")
        assert pdf.is_file()
        assert pdf.stat().st_size > 1000
        assert meta["pdf_path"] == str(pdf.relative_to(ROOT))
        assert len(meta["pdf_sha256"]) == 64
    manifest = json.loads((out / "p5_figures_manifest.json").read_text(encoding="utf-8"))
    assert manifest["inputs"]
    assert (
        manifest["inputs"]["paper/reproducibility/p3_m18c2_aggregate_35272347167.json"]
        == "83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4"
    )
    assert "INSUFFICIENT_REFERENCE_EVIDENCE" in " ".join(manifest["notes"])
    assert "P4 performance" in " ".join(manifest["notes"])
