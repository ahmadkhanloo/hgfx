#!/usr/bin/env python3
"""Run frozen S9 on a physical GPU and append hardware/runtime provenance."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def capture(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def main(output: str, environment_note: str) -> int:
    output_path = Path(output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_m18_s9_backend_robustness.py"),
        "--output",
        str(output_path),
        "--require-gpu",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)

    if output_path.exists():
        import jax
        import jaxlib

        payload = json.loads(output_path.read_text(encoding="utf-8"))
        payload["physical_gpu_evidence"] = {
            "wrapper": "run_m18_s9_h100_revalidation.py",
            "exact_command": shlex.join(command),
            "wrapper_command": shlex.join(sys.argv),
            "git_head": capture(["git", "-C", str(ROOT), "rev-parse", "HEAD"]),
            "git_status_porcelain": capture(["git", "-C", str(ROOT), "status", "--porcelain"]),
            "python": platform.python_version(),
            "jax": jax.__version__,
            "jaxlib": jaxlib.__version__,
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "nvidia_smi_list": capture(["nvidia-smi", "-L"]),
            "nvidia_smi": capture(["nvidia-smi"]),
            "environment_note": environment_note,
            "core_exit_code": completed.returncode,
        }
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote physical GPU evidence: {output_path}")
    else:
        print("S9 core run did not produce an evidence JSON", file=sys.stderr)

    return completed.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="gpu_validation_results/m18_s9_h100_revalidation.json",
    )
    parser.add_argument(
        "--environment-note",
        required=True,
        help="Record shared-node/contention or other environment limitations explicitly.",
    )
    args = parser.parse_args()
    raise SystemExit(main(args.output, args.environment_note))
