"""Execute the preregistered USD/CHF demonstration using the released wheel."""
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
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert importlib.metadata.version('hgfx') == '1.0.0'
    assert jax.config.x64_enabled and all(d.platform == 'cpu' for d in jax.devices())
    source = args.input.read_bytes()
    inputs = np.loadtxt(args.input, dtype=np.float64)
    assert inputs.ndim == 1 and np.isfinite(inputs).all()
    report = {'status': 'STARTED', 'protocol': 'REVISION_PROTOCOL.md',
              'hgfx': '1.0.0', 'module_path': str(Path(hgfx.__file__).resolve()),
              'python': platform.python_version(), 'jax': jax.__version__, 'numpy': np.__version__,
              'x64': bool(jax.config.x64_enabled), 'devices': [str(d) for d in jax.devices()],
              'input_sha256': hashlib.sha256(source).hexdigest(), 'observations': len(inputs),
              'perceptual': 'hgf_config', 'response': 'bayes_optimal_config',
              'optimizer': 'quasinewton_optim_config', 'responses': 'empty; likelihood of empirical inputs',
              'independent_matlab_parity': 'NOT_TESTED_IN_THIS_EXECUTION', 'forecast_validation': 'NOT_TESTED'}
    start = time.perf_counter()
    try:
        fit = hgfx.fit_model([], inputs, 'hgf_config', 'bayes_optimal_config', 'quasinewton_optim_config')
        report.update({key: float(getattr(fit.optim, key)) for key in ['negLl', 'negLj', 'LME', 'AIC', 'BIC']})
        report['mu'] = np.asarray(fit.traj.mu).tolist()
        report['muhat'] = np.asarray(fit.traj.muhat).tolist()
        report['sa'] = np.asarray(fit.traj.sa).tolist()
        report['sahat'] = np.asarray(fit.traj.sahat).tolist()
        report['transformed_parameters'] = np.asarray(fit.optim.final).tolist()
        report['optimizer_fields'] = list(fit.optim.keys())
        report['status'] = 'COMPLETED_DESCRIPTIVE_WORKFLOW' if np.isfinite([report[k] for k in ['negLl','negLj','LME','BIC']]).all() else 'NONFINITE_STATISTICS'
    except Exception as exc:
        report.update(status='FAILED', error=f'{type(exc).__name__}: {exc}')
    report['seconds'] = time.perf_counter()-start
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['mu','muhat','sa','sahat']},indent=2))


if __name__ == '__main__':
    main()
