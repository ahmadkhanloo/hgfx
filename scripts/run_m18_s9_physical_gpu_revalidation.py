#!/usr/bin/env python3
"""Run frozen S9 on an eligible physical NVIDIA GPU and append provenance."""

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

    if not output_path.exists():
        print("S9 core run did not produce an evidence JSON", file=sys.stderr)
        return completed.returncode or 4

    import jax
    import jaxlib

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    smi_list = capture(["nvidia-smi", "-L"])
    smi_full = capture(["nvidia-smi"])
    nvidia_visible = not smi_list.startswith("unavailable:") and "GPU " in smi_list
    gpu_backend = jax.default_backend() == "gpu"
    hardware_eligibility_pass = bool(nvidia_visible and gpu_backend)

    payload["physical_gpu_evidence"] = {
        "wrapper": "run_m18_s9_physical_gpu_revalidation.py",
        "hardware_requirement": "physical NVIDIA CUDA-capable GPU; model not constrained",
        "hardware_eligibility_pass": hardware_eligibility_pass,
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
        "nvidia_smi_list": smi_list,
        "nvidia_smi": smi_full,
        "environment_note": environment_note,
        "core_exit_code": completed.returncode,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote physical GPU evidence: {output_path}")

    if completed.returncode != 0:
        return completed.returncode
    if not hardware_eligibility_pass:
        print(
            "Physical-GPU core passed, but eligible NVIDIA CUDA hardware was not verified.",
            file=sys.stderr,
        )
        return 3
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="gpu_validation_results/m18_s9_physical_gpu_revalidation.json",
    )
    parser.add_argument(
        "--environment-note",
        required=True,
        help="Record hosted/shared-node/contention or other environment limitations explicitly.",
    )
    args = parser.parse_args()
    raise SystemExit(main(args.output, args.environment_note))
