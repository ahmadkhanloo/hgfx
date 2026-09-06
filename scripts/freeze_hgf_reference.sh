#!/usr/bin/env bash
set -euo pipefail
git submodule sync -- external/hgf-toolbox
git submodule update --init external/hgf-toolbox
python scripts/verify_reference_freeze.py
