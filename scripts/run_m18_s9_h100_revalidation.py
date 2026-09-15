#!/usr/bin/env python3
"""Backward-compatible alias for the generic S9 physical-GPU revalidation wrapper.

The S9 release gate is no longer H100-specific. New evidence should use
`scripts/run_m18_s9_physical_gpu_revalidation.py`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_m18_s9_physical_gpu_revalidation.py"),
        *sys.argv[1:],
    ]
    raise SystemExit(subprocess.call(command, cwd=ROOT))
