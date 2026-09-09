#!/usr/bin/env bash
set -euo pipefail

# HGFX physical-GPU validation harness for M14-M17.
#
# Usage:
#   CUDA_VISIBLE_DEVICES=0,1 ./scripts/run_gpu_validation.sh
#
# For final 8-GPU validation after infrastructure is healthy:
#   CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 ./scripts/run_gpu_validation.sh
#
# JAX logical GPU ids are renumbered from zero inside CUDA_VISIBLE_DEVICES.

OUT_DIR="${HGFX_GPU_RESULTS_DIR:-gpu_validation_results}"
mkdir -p "$OUT_DIR"

export XLA_PYTHON_CLIENT_PREALLOCATE="${XLA_PYTHON_CLIENT_PREALLOCATE:-false}"
export HGFX_REQUIRE_GPU=1

{
  echo "=== DATE ==="
  date -Is
  echo
  echo "=== GIT ==="
  git branch --show-current || true
  git rev-parse HEAD
  echo
  echo "=== PYTHON/JAX ==="
  python --version
  python - <<'PY'
import jax, jaxlib
print("jax:", jax.__version__)
print("jaxlib:", jaxlib.__version__)
print("backend:", jax.default_backend())
print("devices:", jax.devices())
PY
  echo
  echo "=== CUDA_VISIBLE_DEVICES ==="
  echo "${CUDA_VISIBLE_DEVICES:-<unset>}"
  echo
  echo "=== NVIDIA-SMI ==="
  nvidia-smi
} 2>&1 | tee "$OUT_DIR/environment.txt"

run_test() {
  local name="$1"
  shift
  echo
  echo "=== $name ==="
  pytest "$@" -q -s 2>&1 | tee "$OUT_DIR/$name.txt"
}

run_test m14_gpu   tests/cpu_gpu/test_m14_fast_engine.py::test_real_gpu_forward_and_objective_parity_when_available

run_test m15_gpu   tests/cpu_gpu/test_m15_gpu_fitting.py::test_real_gpu_fitting_parity_when_available

run_test m16_gpu   tests/cpu_gpu/test_m16_batch_engine.py::test_real_gpu_batch_parity_when_available

VISIBLE_COUNT="$(python - <<'PY'
import jax
print(len(jax.devices("gpu")))
PY
)"

if [ "$VISIBLE_COUNT" -ge 2 ]; then
  run_test m17_2gpu     tests/cpu_gpu/test_m17_multi_gpu.py::test_real_two_gpu_multi_device_parity_when_available
else
  echo "M17 strict two-GPU test requires >=2 visible GPUs; found $VISIBLE_COUNT"     | tee "$OUT_DIR/m17_2gpu.txt"
  exit 2
fi

run_test m14_m17_full   tests/cpu_gpu/test_m14_fast_engine.py   tests/cpu_gpu/test_m15_gpu_fitting.py   tests/cpu_gpu/test_m16_batch_engine.py   tests/cpu_gpu/test_m17_multi_gpu.py

tar -czf hgfx_gpu_validation_results.tar.gz "$OUT_DIR"
echo
echo "Validation complete: hgfx_gpu_validation_results.tar.gz"
