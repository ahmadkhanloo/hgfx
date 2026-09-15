# CI maintenance — 2026-09-15

## Reason and scope

Audit baseline: `a032ca5d1779a5d7f61673969e16f2025c0037ed`, PR #26.
The repository had 62 workflow files. Completed milestone workflows repeatedly
ran full pytest and regenerated MATLAB fixtures on every PR, including docs-only
changes. Closed D02/D08/S8 probes and historical recovery diagnostics also fired
on routine changes, despite the current release policy forbidding unnecessary
reopening of those investigations. README/handoff/TODO still claimed GPU was
blocked after the T4 evidence and M19 freeze were committed.

Automatic PR-triggered workflows: 58 before, 10 after. Of the 51 manual
replay workflows, two were already manual; 49 automatic triggers were retired.

## Routine validation

- `regression.yml`: one full CPU pytest run plus frozen-reference guard on every
  PR, main push, or manual request. No test exclusions or tolerance changes.
- S7 paired recovery, S9 backend, D04/D09–D12 and demo model selection retain
  their existing path-triggered oracle/backend checks.
- S10 packaging and M19/M20 release preflight retain their automatic checks.
- Automatic PR runs superseded by a new revision are cancelled per workflow;
  manual evidence runs remain independent.
- Physical GPU remains an explicit hardware gate. CPU skips are not GPU PASS.

## Manual replay policy

The following workflows retain their jobs, commands, inputs and evidence logic,
but no longer run automatically. M1–M17 replay establishes a new MATLAB oracle
when needed; historical diagnostics are investigation tools, not routine gates.
Before accepting numerical changes, run the affected oracle families explicitly
and retain evidence at that revision. A CPU regression alone does not establish
new MATLAB or GPU parity. Do not retune or suppress historical failures.

- `m1-golden-harness.yml`
- `m10-hessian-lme-parity.yml`
- `m11-simulation-parity.yml`
- `m12-complete-model-coverage.yml`
- `m12-config-parity.yml`
- `m12-specialized-model-coverage.yml`
- `m12a-continuous-ar1.yml`
- `m12bc-parity.yml`
- `m12de-parity.yml`
- `m12fg-parity.yml`
- `m13-api-compatibility.yml`
- `m14-gpu-engine.yml`
- `m15-gpu-fitting.yml`
- `m16-batch-engine.yml`
- `m17-multi-gpu.yml`
- `m18-512-reference.yml`
- `m18-d02-basin-diagnostic.yml`
- `m18-d02-matlab-self-sensitivity.yml`
- `m18-d02-numerical-regression.yml`
- `m18-d02-optimizer-source-probe.yml`
- `m18-d02-source-likelihood-diagnostic.yml`
- `m18-d02-theta-diagnostic.yml`
- `m18-d08-endpoint-diagnostic.yml`
- `m18-d08-equivalence-holdout.yml`
- `m18-d08-holdout-matlab-self-sensitivity.yml`
- `m18-d08-holdout-optimizer-diagnostic.yml`
- `m18-d08-holdout-source-probe.yml`
- `m18-d08-matlab-self-sensitivity.yml`
- `m18-d08-official-matlab-self-sensitivity.yml`
- `m18-d08-prior-terms.yml`
- `m18-d08-ridders-probe.yml`
- `m18-d08-source-likelihood-diagnostic.yml`
- `m18-d08-transition-diagnostic.yml`
- `m18-s7-hgf-anomaly-review.yml`
- `m18-s8-hgf-r0-negative-precision-probe.yml`
- `m18-s8-hgf-r0-optimizer-localization.yml`
- `m18-s8-hgf-r0-precheck-trajectory.yml`
- `m18-s8-hgf-r0-ridders-stencil.yml`
- `m18-s8-hgf-r0-validity-reduction-inline.yml`
- `m18-scientific-validation.yml`
- `m18-workflow-closure.yml`
- `m18a-parameter-recovery-diagnosis.yml`
- `m18b-identifiability-validation.yml`
- `m2-parameter-config-parity.yml`
- `m3-scalar-numerical-parity.yml`
- `m4-hgf-forward-parity.yml`
- `m5-ehgf-forward-parity.yml`
- `m6-uhgf-forward-parity.yml`
- `m7-observation-parity.yml`
- `m8-objective-parity.yml`
- `m9-compatibility-fitting.yml`

## Review and limitations

No workflow, test, fixture or historical result is deleted. No old branch/PR is
deleted or closed without checking its unique content. Main remains behind PR
#26 until its release gates pass. Repository required-check configuration must
be inspected before merge; removed automatic job names may need migration to
`HGFX Regression / regression`. Do not bypass a required check.

Count reduction is an execution-trigger change, not a measured runtime saving.
Fresh regression, candidate packaging and final manifest checks must be recorded
before claiming completion. MATLAB oracle tests are intentionally not regenerated
for this CI/documentation-only maintenance.

Repository rulesets API returned an empty list. Classic branch-protection read
returned 403 (integration permission), so required classic checks are unverified.
