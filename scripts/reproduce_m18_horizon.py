#!/usr/bin/env python3
"""Export the historical M18B horizon grid for paired, RNG-independent MATLAB replay.

This is a forward/validation diagnostic, not a recovery or final parity gate.
The old grid/seed formula comes from 225f565^; all replicas are retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np

from hgfx import enable_x64
from hgfx.diagnostics.identifiability_validation import informative_binary_inputs
from hgfx.diagnostics.recovery import BINARY_VARIANTS, _truth_vector, _variant_components

FIELDS = ('mu', 'sa', 'muhat', 'sahat', 'v', 'w', 'da')


def encode_array(value):
    """Keep nonfinite kinds distinct; MATLAB jsondecode maps plain null to NaN."""
    a = np.asarray(value, dtype=float)
    return {'shape': list(a.shape), 'values': np.where(np.isfinite(a), a, 0).tolist(),
            'nan': np.isnan(a).tolist(), 'posinf': np.isposinf(a).tolist(),
            'neginf': np.isneginf(a).tolist()}


def jump_diagnostics(traj):
    rows = {}
    for field, a in (('mu', traj['mu'][:, 1:]), ('pi', 1 / traj['sa'][:, 1:])):
        delta = np.diff(a, axis=0)
        rms = np.sqrt(np.mean(delta**2, axis=0))
        ratio = np.divide(np.abs(delta), rms, out=np.zeros_like(delta), where=rms > 0)
        index = np.unravel_index(np.argmax(ratio), ratio.shape)
        rows[field] = {'all_finite': bool(np.isfinite(a).all()),
                       'max_jump_ratio': float(ratio[index]),
                       'destination_trial_1based': int(index[0] + 2),
                       'level_1based': int(index[1] + 2)}
    return rows


def build_cases(trial_counts=(128, 256, 512)):
    rows = []
    for mi, model in enumerate(BINARY_VARIANTS):
        factory, forward = _variant_components(model)
        for n in trial_counts:
            for replicate in range(3):
                seed = 181900 + mi * 1_000_000 + n * 100 + replicate
                u = informative_binary_inputs(n, seed)
                cfg = factory().resolve_placeholders(u)
                truth, _, _ = _truth_vector(model, u, replicate=replicate, scale=.35)
                for point, p in (('prior', cfg.priormus),
                                 ('truth', truth[:len(cfg.parameters)])):
                    row = dict(model=model, trials=n, replicate=replicate, seed=seed,
                               point=point, inputs=u.tolist(),
                               ptrans=[None if np.isnan(v) else float(v) for v in p])
                    try:
                        traj, _ = forward(u, p, transformed=True)
                        row.update(status='valid', trajectory={k: encode_array(traj[k]) for k in FIELDS})
                    except ValueError as exc:
                        row.update(status='rejected', error=str(exc))
                        # Explicitly diagnostic; never passed to fitting or used as valid evidence.
                        raw, _ = forward(u, p, transformed=True, validate=False)
                        row['unchecked_python_diagnostic'] = jump_diagnostics(raw)
                    rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='benchmarks/results/m18_horizon_python.json')
    args = parser.parse_args()
    enable_x64()
    root = Path(__file__).resolve().parents[1]
    payload = {'schema_version': 1, 'purpose': 'forward/validation diagnostic only',
               'reference_commit': (root / 'reference/HGF_COMMIT').read_text().strip(),
               'historical_protocol_commit': subprocess.check_output(
                   ['git', 'rev-parse', '225f565^'], cwd=root, text=True).strip(),
               'hgfx_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
               'python': platform.python_version(), 'numpy': np.__version__,
               'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'cases': build_cases()}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False))
    print(json.dumps({'output': str(path), 'cases': len(payload['cases']),
                      'rejected': sum(c['status'] == 'rejected' for c in payload['cases'])}))


if __name__ == '__main__':
    main()
