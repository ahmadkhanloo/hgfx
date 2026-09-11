#!/usr/bin/env python3
"""Compare paired forward evidence; never treat shared rejection as raw-state parity."""
import argparse
import json
from pathlib import Path

import numpy as np


def compare(python, matlab):
    if python['reference_commit'] != matlab['reference_commit']:
        raise ValueError('Reference SHA mismatch')
    if not python['cases'] or len(python['cases']) != len(matlab['cases']):
        raise ValueError('Missing cases')
    mismatches = []
    shared_rejections = []
    for i, (p, m) in enumerate(zip(python['cases'], matlab['cases'], strict=True)):
        for key in ('model', 'trials', 'replicate', 'seed', 'point'):
            if p[key] != m[key]:
                raise ValueError(f'Case identity mismatch: {i}/{key}')
        if p['status'] != m['status']:
            mismatches.append({'case': i, 'field': 'status', 'python': p['status'], 'matlab': m['status']})
            continue
        if p['status'] not in ('valid', 'rejected'):
            raise ValueError('Unknown case status')
        if p['status'] == 'rejected':
            # Unrelated MATLAB errors cannot be accepted as matching numerical rejection.
            if m.get('error_id') != 'tapas:hgf:VarApproxInvalid':
                mismatches.append({'case': i, 'field': 'error_id', 'matlab': m.get('error_id')})
            else:
                shared_rejections.append(i)
            continue
        for field, a in p['trajectory'].items():
            b = m['trajectory'][field]
            shape = tuple(a['shape'])
            if shape != tuple(b['shape']):
                mismatches.append({'case': i, 'field': field, 'kind': 'shape'})
                continue
            valid = True
            for mask in ('nan', 'posinf', 'neginf'):
                valid &= np.array_equal(np.asarray(a[mask]).reshape(shape), np.asarray(b[mask]).reshape(shape))
            x = np.asarray(a['values']).reshape(shape)
            y = np.asarray(b['values']).reshape(shape)
            # Existing M4 forward tolerance; this diagnostic does not recalibrate it.
            bad = ~np.isclose(x, y, atol=5e-13, rtol=5e-11)
            if not valid or np.any(bad):
                idx = np.argwhere(bad)
                mismatches.append({'case': i, 'field': field, 'kind': 'numeric_or_nonfinite',
                                   'first_index_0based': idx[0].tolist() if len(idx) else None})
    return {'mismatches': mismatches, 'shared_rejections': shared_rejections,
            'complete_raw_parity': not mismatches and not shared_rejections,
            'scope': 'valid trajectory parity and validation boundary; shared rejected raw states remain unverified'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('python'); ap.add_argument('matlab'); ap.add_argument('--output', required=True)
    args = ap.parse_args()
    result = compare(json.loads(Path(args.python).read_text()), json.loads(Path(args.matlab).read_text()))
    Path(args.output).write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    if result['mismatches']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
