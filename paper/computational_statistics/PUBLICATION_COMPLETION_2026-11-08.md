# Publication completion: author-review handoff

Baseline and branch: `edaf2a46583837bf664093ca3a7362a90b878871`, `paper/published-input-validation-20261108`. The worktree was clean; no later paper commits existed at execution start. Eight required scientific documents were read. No core code, API, tolerance or frozen result changed.

## Warning audit

The retained 324-case aggregate was recounted: 48 warning cases, all Reed; 86 events (29 cases with one, 19 with three). All 48 have ignored trials. This association is not a causal diagnosis. The aggregate does not retain messages, filenames, line numbers or warning categories. The comparator records warning types internally but omits them from its public per-case status projection. No fresh released-wheel/MATLAB execution was performed in this audit. Original nonfinite masks and warning mechanism cannot be newly certified from this summary. Current manuscript wording already discloses the 48 cases and uncharacterized mechanism; it is retained. Source-count audit: evidence/publication_completion_audit_20261108.json. Original evidence is unchanged.

## Bounded application outcome

Oberwelland was checked first. Public run_analysis.m was fetched and SHA-256 recorded in evidence/publication_completion_sources_20261108.json; lines 71/74/77 use tapas_softmax_binary_config. Immutable HGFX 1.0.0 observation_for supports unitsq_sgm, gaussian_obs and Bayes-optimal workflows, not softmax_binary. A silent substitution is prohibited. OSF file metadata returned HTTP 410 in this attempt. Outcome: BLOCKED before fitting under the no-core-development rule.

Gao was checked second. OSF file API returned HTTP 401; the browser retrieval was also unavailable. Critical data/code/config inspection was not possible. This is an access failure in this session, not proof the deposit is permanently private or missing. Outcome: BLOCKED_SOURCE_ACCESS. No model correctness or likelihood-equivalence claim is made for Gao.

No candidate qualified. No new participant fit, no protocol-triggered full run, and no new participant replication figure were produced. No further study search, Pain/SPIRL reopening, MAB migration or cohort shrinking was undertaken. The five-day conditional phase was not activated; there was no need to exhaust the two-day ceiling after terminal gates were established.

## Claim disposition and author gates

Keep: fixed-vector 324-block compatibility; descriptive 614-observation example; separate implementation agreement and model recovery. Keep 63/64 diagnostic fitting limitation and frozen failed recovery/P3 classifications. PERF-01C is separate; it is not made PASS or closed.

Before submission: final scientific claim approval, secondary-data reuse/ethics assessment, unresolved warning mechanism where stronger interpretation is sought, comprehensive mandatory-fee and institutional/portal review. Existing declarations confirmed in prior chat are not requested again. No author, editor or external reviewer approval is inferred from software checks.

Official policy checked 8 November: https://link.springer.com/journal/180/how-to-publish-with-us states subscription has no APC; https://link.springer.com/journal/180/submission-guidelines requires editable source, permissions and human accountability. These pages do not independently close all possible charges or IPM/institutional conditions. No submission or contact occurred.

Reproduce package checks from repository root:

```sh
python paper/computational_statistics/build_submission.py
python paper/computational_statistics/verify_revision.py
python -m pytest tests/paper/test_compstat_revision.py tests/paper/test_compstat_documentation.py tests/paper/test_frozen_audit.py tests/paper/test_p5_figures.py -q
```

Tests/build are local artifact checks, not fresh MATLAB reproduction or publication approval. Final exact results are appended to EXECUTION_LOG.md.

Count reproduction (run from the candidate directory, using Python standard library):

```python
import json
from collections import Counter
d = json.load(open('evidence/published_input_41809919116.json'))
w = [r for r in d['per_case_statuses'] if r.get('warnings')]
print(len(w), sum(r['warnings'] for r in w))
print(Counter(r['study'] for r in w))
print(Counter(r['warnings'] for r in w))
print(sum(bool(r.get('ignored_trials')) for r in w))
```

The audit JSON records the normalized source digest. Review by a separate agent independently confirmed counts and frozen dispatch scope; live retrieval, warning mechanism and fresh numerical execution were not independently reproduced. No blocking text findings were reported.
