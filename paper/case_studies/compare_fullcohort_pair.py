"""All published participant-block fixed-vector parity at frozen M12B thresholds.

This intentionally does NOT implement the articles' response models, optimizer
or clinical/group inference. Only aggregate metrics are exported.
"""
import importlib.metadata
import json
import os
import sys
import warnings
from pathlib import Path
import numpy as np
import jax
from compare_realdata_pair import check_case

EXPECTED=324

def main():
    folder=Path(sys.argv[1]).resolve()
    target=Path(sys.argv[2]).resolve()
    assert importlib.metadata.version('hgfx')=='1.0.0'
    assert jax.config.jax_enable_x64 and all(d.platform=='cpu' for d in jax.devices())
    manifest=json.loads((folder/'all_cohort_manifest.json').read_text())
    assert manifest['actual_total_cases']==EXPECTED
    statuses=json.loads((folder/'matlab_all_cohort_status.json').read_text())
    lookup={row['id']:row for row in statuses['records']}
    output=[]
    for meta in manifest['cases']:
        rid=meta['id']
        item={'id':rid,'study':meta['study'],'status':None}
        if meta['status']!='INPUT_READY':
            item.update(status='BLOCKED_INPUT_SEMANTICS',reason=meta.get('reason','unknown'))
        elif rid not in lookup or lookup[rid]['status']!='MATLAB_FORWARD_DONE':
            item.update(status='MATLAB_FAILED',reason=lookup.get(rid,{}).get('reason','missing output'))
        else:
            try:
                with warnings.catch_warnings(record=True) as ws:
                    warnings.simplefilter('always')
                    actual=check_case(rid,folder)
                item.update(status=actual['status'],field_checks=actual['field_checks'],
                            warning_types=sorted(set(type(w.message).__name__ for w in ws)),
                            warning_count=len(ws),
                            ignored_trials=meta.get('ignored_trials',0))
            except Exception as exc:
                item.update(status='HGFX_OR_COMPARISON_FAILED',reason=f'{type(exc).__name__}: {str(exc)[:220]}')
        output.append(item)
    accepted=[o for o in output if o['status']=='PASS_FIXED_VECTOR_FORWARD_PARITY']
    all_fields=[f for o in output for f in o.get('field_checks',[])]
    abs_vals=[f['max_abs_diff'] for f in all_fields if f.get('max_abs_diff') is not None]
    rel_vals=[f['max_rel_diff_descriptive'] for f in all_fields if f.get('max_rel_diff_descriptive') is not None]
    counts={}
    for o in output: counts[o['status']]=counts.get(o['status'],0)+1
    summary={
        'interpretation':'Two public published studies; matched 8.2.0 forward-model fixed-vector numeric parity, NOT original published model-fitting reproduction',
        'matlab_oracle':'HGF 8.2.0 @2437f4dc241541072722a2695ddeca7b44d83dd3',
        'hgfx_wheel':'1.0.0','jax_version':jax.__version__,
        'device':['CPU'], 'criteria':{'rtol':2e-9,'atol':2e-11,'inherited_from':'tools/check_m12bc_parity.py'},
        'expected_cases':EXPECTED,'total_cases':len(output),
        'trials_in_source_grid':EXPECTED*80,
        'case_status_counts':counts,
        'expected_fields_per_case':12,
        'total_comparable_fields':len(all_fields),
        'total_elements_compared':sum(f.get('elements',0) for f in all_fields),
        'total_failed_elements':sum(f.get('failing_elements',0) for f in all_fields),
        'worst_max_abs_diff':max(abs_vals,default=None),
        'worst_max_rel_diff_descriptive':max(rel_vals,default=None),
        'warning_case_count':sum(bool(o.get('warning_count')) for o in output),
        'github_run_id':os.getenv('GITHUB_RUN_ID'),'github_sha':os.getenv('GITHUB_SHA'),
        'overall_status':'PASS_FIXED_VECTOR_PARITY_ALL_CASES' if len(accepted)==EXPECTED else 'FAIL_OR_INCONCLUSIVE_ALL_CASES',
        'per_case_statuses':[
            {'id':o['id'],'study':o['study'],'status':o['status'],
             'ignored_trials':o.get('ignored_trials'),'warnings':o.get('warning_count'),
             'failed_fields':[f['field'] for f in o.get('field_checks',[]) if f['status']!='PASS_NUMERIC_GATE'],
             'first_divergence':next((f.get('first_divergence_zero_based') for f in o.get('field_checks',[]) if f['status']=='FAIL_NUMERIC_GATE'),None),
             'reason':o.get('reason')}
            for o in output
        ],
    }
    target.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    public={key:val for key,val in summary.items() if key!='per_case_statuses'}
    print(json.dumps(public,indent=2))
    if summary['overall_status']!='PASS_FIXED_VECTOR_PARITY_ALL_CASES':
        raise SystemExit('Full cohort parity FAIL/INCONCLUSIVE; all case outcomes kept in report')

if __name__=='__main__':
    main()
