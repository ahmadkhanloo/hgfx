"""Synthetic-only comparison contract tests; no MATLAB/HGFX objective executed."""
from __future__ import annotations

import copy
import unittest
from tools.compstat_rev24_compare import audit,digest,first_error,scalar,config_fingerprint


def dummy_pair():
    families=('hgf_binary','ehgf_binary','uhgf_binary')
    manifest={'protocol':'compstat-rev2-4-objective-cross-eval-v1',
              'release_source_commit_declared':'4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27',
              'matlab_reference_commit':'2437f4dc241541072722a2695ddeca7b44d83dd3',
              'n_per_model':200,'trials':128,'inputs_binary64_le_sha256':'a'*64,
              'responses_binary64_le_sha256':'b'*64, 'strata':[]}
    cases=[]
    for model in families:
        group={'model':model,'observation_model':'unitsq_sgm',
               'free_indices_zero_based':[0], 'prior_means_full':[0.0],
               'prior_variances_full_ieee':[1.0], 'rows':[]}
        for i in range(200):
            c={'case_id':f'REV24-G-{model}-{i:03d}', 'model':model,
               'observation_model':'unitsq_sgm'}
            c['case_sha256']=digest(c)
            group['rows'].append(c)
            cases.append((model,c))
        manifest['strata'].append(group)
    manifest['manifest_sha256']=digest(manifest)
    fingerprints={g['model']:config_fingerprint(g) for g in manifest['strata']}
    def make(source):
        return {'protocol':manifest['protocol'],'source':source,
                'manifest_sha256':manifest['manifest_sha256'],
                'release_source_commit':manifest['release_source_commit_declared'],
                'matlab_reference_commit':manifest['matlab_reference_commit'],
                'inputs_binary64_le_sha256':manifest['inputs_binary64_le_sha256'],
                'responses_binary64_le_sha256':manifest['responses_binary64_le_sha256'],
                'cases':[{**{k:c[k] for k in ('case_id','case_sha256')},
                          'model':model,'config_sha256':fingerprints[model],
                          'rval':0,'valid':True,
                          'neg_log_likelihood':42.,'neg_log_joint':43.,
                          'log_likelihood':-42.,
                          'trial_log_likelihoods':[-0.125]*128}
                         for model,c in cases]}
    return manifest,make('matlab'),make('hgfx')


class Rev24CompareContractTests(unittest.TestCase):
    def test_600_denominators_no_fabricated_family_gate(self):
        m,ref,h=a=dummy_pair()
        result=audit(m,ref,h)
        self.assertEqual(len(result['cases']),600)
        self.assertEqual(result['summary']['hgf_binary']['within_existing_gate'],200)
        self.assertEqual(result['summary']['ehgf_binary']['no_predeclared_gate'],200)
        self.assertEqual(result['summary']['uhgf_binary']['no_predeclared_gate'],200)
        self.assertEqual(result['scientific_gate'],'NOT_GLOBAL_PASS')

    def test_one_sided_invalid_is_not_dropped(self):
        m,ref,h=dummy_pair()
        h['cases'][1]['valid']=False
        h['cases'][1]['rval']=-1
        result=audit(m,ref,h)
        self.assertEqual(result['cases'][1]['classification'],'ONE_SIDED_INVALID')
        self.assertEqual(result['summary']['hgf_binary']['denominator'],200)

    def test_missing_rows_rejected(self):
        m,ref,h=dummy_pair()
        h['cases'].pop(1)
        with self.assertRaisesRegex(ValueError,'600 original cases'):
            audit(m,ref,h)

    def test_tampered_source_rejected(self):
        m,ref,h=dummy_pair()
        h['manifest_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'manifest input identity'):
            audit(m,ref,h)

    def test_config_drift_is_rejected(self):
        m,ref,h=dummy_pair()
        h['cases'][0]['config_sha256']='d'*64
        with self.assertRaisesRegex(ValueError,'unmatched model'):
            audit(m,ref,h)

    def test_per_trial_error_and_nan_not_parity(self):
        m,ref,h=dummy_pair()
        h['cases'][0]['trial_log_likelihoods'][7]=-2.0
        result=audit(m,ref,h)
        self.assertEqual(result['cases'][0]['classification'],'SHARED_OBJECTIVE_MISMATCH')
        self.assertEqual(result['cases'][0]['first_likelihood_divergence']['trial_zero_based'],7)
        self.assertIsNone(scalar('NaN'))
        self.assertEqual(first_error(['NaN']*128,['NaN']*128,atol=2e-13,rtol=2e-11)['reason'],'NONFINITE_OR_MISSING')

    def test_absent_likelihood_never_passes(self):
        m,ref,h=dummy_pair()
        del h['cases'][0]['trial_log_likelihoods']
        result=audit(m,ref,h)
        self.assertNotEqual(result['cases'][0]['classification'],'SHARED_OBJECTIVE_WITHIN_EXISTING_GATE')

    def test_short_trial_likelihood_never_passes(self):
        m,ref,h=dummy_pair()
        h['cases'][0]['trial_log_likelihoods']=[]
        r=audit(m,ref,h)
        self.assertNotEqual(r['cases'][0]['classification'],'SHARED_OBJECTIVE_WITHIN_EXISTING_GATE')

    def test_no_nan_numeric_fields_pass(self):
        m,ref,h=dummy_pair()
        ref['cases'][0]['neg_log_joint']='NaN'
        r=audit(m,ref,h)
        self.assertEqual(r['cases'][0]['classification'],'INCOMPLETE_NUMERIC_FIELDS')


if __name__=='__main__':unittest.main()
