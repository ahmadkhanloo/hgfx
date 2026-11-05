"""24-trial synthetic quickstart with released-wheel and CPU x64 checks."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import time

os.environ['JAX_ENABLE_X64'] = '1'
os.environ['JAX_PLATFORMS'] = 'cpu'

import jax
import numpy as np
import hgfx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if importlib.metadata.version('hgfx') != '1.0.0':
        raise RuntimeError('This example requires released hgfx==1.0.0')
    if not jax.config.x64_enabled or any(d.platform != 'cpu' for d in jax.devices()):
        raise RuntimeError('CPU float64 required')
    inputs = np.array([0,1,1,0,1,0,0,1,1,0,1,1,0,0,1,1,0,1,0,1,1,0,1,0], dtype=np.float64)
    responses = np.array([0,1,1,0,1,0,0,1,0,0,1,1,0,1,1,0,0,1,0,1,1,0,1,0], dtype=np.float64)
    start = time.perf_counter()
    result = hgfx.fit_model(responses, inputs)
    output = {'status': 'PASS_WORKFLOW_ONLY', 'data': 'synthetic existing quickstart vectors',
              'hgfx': importlib.metadata.version('hgfx'), 'module_path': str(Path(hgfx.__file__).resolve()),
              'python': platform.python_version(), 'jax': jax.__version__, 'numpy': np.__version__,
              'devices': [str(d) for d in jax.devices()], 'x64': bool(jax.config.x64_enabled),
              'input_sha256_float64_le': hashlib.sha256(inputs.astype('<f8').tobytes()).hexdigest(),
              'response_sha256_float64_le': hashlib.sha256(responses.astype('<f8').tobytes()).hexdigest(),
              'trials': len(inputs), 'seconds': time.perf_counter()-start,
              'LME': float(result.optim.LME), 'BIC': float(result.optim.BIC),
              'mu': np.asarray(result.traj.mu).tolist()}
    if not np.isfinite([output['LME'], output['BIC']]).all():
        raise RuntimeError('Nonfinite fit statistics; do not report workflow PASS')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=True)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in output.items() if k != 'mu'}, indent=2))


if __name__ == '__main__':
    main()
