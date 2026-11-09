#!/usr/bin/env python3
"""Fail-closed REV-2.4 *paired-output* auditor, not an oracle or simulation.

Reads two independently executed, provenance-pinned results from one frozen
600-row input manifest. Never performs HGFX/MATLAB science or changes the
precommitted sample selection. Missing/invalid cases are retained, not dropped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

PROTOCOL = 'compstat-rev2-4-objective-cross-eval-v1'
RELEASE_SHA = '4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27'
MATLAB_SHA = '2437f4dc241541072722a2695ddeca7b44d83dd3'
FAMILIES = ('hgf_binary', 'ehgf_binary', 'uhgf_binary')
HGF_M8_ATOL = 2e-13
HGF_M8_RTOL = 2e-11
FIELDS = ('neg_log_likelihood', 'neg_log_joint', 'log_likelihood')


def check(ok, message):
    if not ok:
        raise ValueError(message)


def digest(doc):
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode('utf-8')).hexdigest()


def scalar(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        if value in ('NaN', '+Inf', '-Inf', 'Inf', 'Infinity', '-Infinity'):
            return None
        return None
    if not isinstance(value, (int, float)):
        return None
    v = float(value)
    return v if math.isfinite(v) else None


def config_fingerprint(group):
    return digest({k: group[k] for k in (
        'model', 'observation_model', 'free_indices_zero_based',
        'prior_means_full', 'prior_variances_full_ieee')})


def first_error(a, b, *, atol, rtol):
    """Never treat equal NaNs as a pass; numeric array order is trial order."""
    if (not isinstance(a, list) or not isinstance(b, list) or
            len(a) != len(b) or len(a) != 128):
        return {'reason': 'UNAVAILABLE_OR_SHAPE_MISMATCH'}
    for trial, (x, y) in enumerate(zip(a, b)):
        left, right = scalar(x), scalar(y)
        if left is None or right is None:
            return {'trial_zero_based': trial, 'reason': 'NONFINITE_OR_MISSING'}
        err = abs(left-right)
        limit = atol + rtol*abs(left)
        if err > limit:
            return {'trial_zero_based': trial, 'matlab': left, 'hgfx': right,
                    'abs_difference': err, 'allowed_difference': limit}
    return None


def verify_manifest(manifest):
    check(manifest.get('protocol') == PROTOCOL, 'Wrong manifest protocol')
    check(manifest.get('release_source_commit_declared') == RELEASE_SHA,
          'Wrong pinned released software source')
    check(manifest.get('matlab_reference_commit') == MATLAB_SHA,
          'Wrong pinned MATLAB source')
    check(manifest.get('n_per_model') == 200 and manifest.get('trials') == 128,
          'Frozen sample/horizon changed')
    check(manifest.get('manifest_sha256') == digest({k:v for k,v in manifest.items()
                                                  if k != 'manifest_sha256'}),
          'Manifest SHA256 invalid')
    expected = []
    for model, group in zip(FAMILIES, manifest['strata'], strict=True):
        check(group['model'] == model and len(group['rows']) == 200,
              'Missing/reordered/fewer model cases')
        for i, row in enumerate(group['rows']):
            check(row['case_id'] == f'REV24-G-{model}-{i:03d}',
                  'Incorrect frozen case identifier')
            check(row['model'] == model and row['observation_model'] == 'unitsq_sgm',
                  'Wrong model or observation pair')
            check(row['case_sha256'] == digest({k:v for k,v in row.items()
                                               if k != 'case_sha256'}),
                  'Corrupted frozen case hash')
            expected.append((row['case_id'],row['case_sha256'],model))
    check(len(expected) == 600, 'Expected exactly 600 source cases')
    return expected


def verify_output(output, source, manifest, expected):
    check(output.get('protocol') == PROTOCOL, f'{source}: wrong protocol')
    check(output.get('source') == source, f'{source}: wrong output source label')
    check(output.get('manifest_sha256') == manifest['manifest_sha256'],
          f'{source}: manifest input identity mismatch')
    check(output.get('matlab_reference_commit') == MATLAB_SHA and
          output.get('release_source_commit') == RELEASE_SHA,
          f'{source}: frozen version identity mismatch')
    check(output.get('inputs_binary64_le_sha256') == manifest['inputs_binary64_le_sha256']
          and output.get('responses_binary64_le_sha256') == manifest['responses_binary64_le_sha256'],
          f'{source}: trial-data hashes mismatch')
    rows = output.get('cases')
    check(isinstance(rows, list) and len(rows) == 600,
          f'{source}: must retain all 600 original cases')
    result = {}
    for (case_id, case_sha, model), row in zip(expected, rows, strict=True):
        check(row.get('case_id') == case_id and row.get('case_sha256') == case_sha,
              f'{source}: case ID/hash/order mismatch: {case_id}')
        check(row.get('model') == model, f'{source}: model mismatch')
        check(isinstance(row.get('valid'), bool), f'{source}: missing explicit validity')
        check('rval' in row and isinstance(row['rval'], int),
              f'{source}: missing integer rval')
        if row['valid']:
            check(row['rval'] == 0, f'{source}: valid row with nonzero rval')
        result[case_id] = row
    return result


def audit(manifest, matlab, hgfx):
    expected = verify_manifest(manifest)
    lm = verify_output(matlab, 'matlab', manifest, expected)
    lh = verify_output(hgfx, 'hgfx', manifest, expected)
    fingerprints = {group['model']: config_fingerprint(group)
                    for group in manifest['strata']}
    records = []
    summary = {model: {'denominator':200, 'both_valid':0,
                       'one_sided_invalid':0, 'both_invalid':0,
                       'within_existing_gate':0, 'outside_existing_gate':0,
                       'no_predeclared_gate':0, 'incomplete_numeric_fields':0}
               for model in FAMILIES}
    for case_id, case_sha, model in expected:
        ref, test = lm[case_id], lh[case_id]
        s = summary[model]
        check(ref.get('config_sha256') == fingerprints[model] and
              test.get('config_sha256') == fingerprints[model],
              f'{case_id}: unmatched model/prior/free-index configuration identity')
        r = {'case_id':case_id, 'case_sha256':case_sha, 'model':model,
             'matlab_valid':ref['valid'], 'hgfx_valid':test['valid'],
             'matlab_rval':ref['rval'], 'hgfx_rval':test['rval']}
        if not ref['valid'] and not test['valid']:
            r['classification']='SHARED_INVALID_OBJECTIVE';s['both_invalid']+=1
        elif ref['valid'] != test['valid']:
            r['classification']='ONE_SIDED_INVALID';s['one_sided_invalid']+=1
        else:
            s['both_valid']+=1
            discrepancies={}
            complete=True
            for field in FIELDS:
                a,b=scalar(ref.get(field)),scalar(test.get(field))
                if a is None or b is None:
                    complete=False
                    discrepancies[field]={'status':'MISSING_OR_NONFINITE'}
                else:
                    discrepancies[field]={'matlab':a,'hgfx':b,
                                          'abs_difference':abs(a-b)}
                    if model=='hgf_binary':
                        limit=HGF_M8_ATOL+HGF_M8_RTOL*abs(a)
                        discrepancies[field]['allowed_difference']=limit
                        discrepancies[field]['within_gate']=abs(a-b)<=limit
                        if abs(a-b)>limit:complete=False
            r['objective_differences']=discrepancies
            if model=='hgf_binary':
                # Frozen M8 validation also tested per-trial likelihoods.
                # Missing trial arrays MUST NOT silently yield a scalar-only PASS.
                first=first_error(ref.get('trial_log_likelihoods'),
                                  test.get('trial_log_likelihoods'),
                                  atol=HGF_M8_ATOL,rtol=HGF_M8_RTOL)
                r['first_likelihood_divergence']=first
                if first is not None:complete=False
                if any(x.get('status')=='MISSING_OR_NONFINITE'
                       for x in discrepancies.values()):
                    r['classification']='INCOMPLETE_NUMERIC_FIELDS'
                    s['incomplete_numeric_fields']+=1
                elif complete:
                    r['classification']='SHARED_OBJECTIVE_WITHIN_EXISTING_GATE'
                    s['within_existing_gate']+=1
                else:
                    r['classification']='SHARED_OBJECTIVE_MISMATCH'
                    s['outside_existing_gate']+=1
            else:
                r['classification']='NO_PREDECLARED_FAMILY_OBJECTIVE_GATE'
                s['no_predeclared_gate']+=1
        # A scalar objective comparison cannot locate a latent-state first cause.
        r['first_causal_state']='NOT_EXPORTED'
        records.append(r)
    check(len(records)==600,'All 600 cases must be retained')
    return {'protocol':PROTOCOL, 'manifest_sha256':manifest['manifest_sha256'],
            'source_matlab_result_sha256':digest(matlab),
            'source_hgfx_result_sha256':digest(hgfx),
            'scope':'PANEL_G_600_PAIRS_ONLY__NO_PANEL_E',
            'scientific_gate':'NOT_GLOBAL_PASS',
            'summary':summary,'cases':records,
            'preserved_historical_failures':True}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--matlab',type=Path,required=True)
    p.add_argument('--hgfx',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    check(not a.output.exists(),'Refusing to overwrite original comparison')
    manifest=json.loads(a.manifest.read_text())
    # This validates frozen u/y, free masks, full row hashes and all 600
    # generated vectors, not merely the top-level manifest digest.
    from tools.compstat_rev24_manifest import validate_manifest
    validate_manifest(manifest)
    matlab=json.loads(a.matlab.read_text())
    hgfx=json.loads(a.hgfx.read_text())
    result=audit(manifest,matlab,hgfx)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'status':result['scientific_gate'],'summary':result['summary'],
                      'cases':len(result['cases'])},sort_keys=True))


if __name__=='__main__':
    main()
