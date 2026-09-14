# Agent Handoff

Last synchronized: 2026-09-14
Branch: `migration/m18-workflow-closure`
Planning head immediately before this handoff update: `10b1e89033660c3127b308651ce33aec9fbd2f67`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Current milestone: **M18 v1 MATLAB-equivalence closure — IN PROGRESS / OPEN**
Historical M18 scientific experiment: **FAIL, preserved**

## Read in this order

1. `docs/planning/V1_TODO.md` — live operational checklist.
2. `docs/planning/M18_COMPLETION_PLAN.md` — ordered S1-S10 plan.
3. `docs/planning/V1_RELEASE_GATE.md` — release acceptance.
4. `docs/validation/MATLAB_EQUIVALENCE_POLICY.md` — frozen tiered exact/numerical/endpoint-sensitivity/inferential equivalence policy.
5. `docs/validation/M18_D02_BASIN_DIAGNOSTIC.md` — frozen D02 classifier protocol.
6. `docs/validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md` — case-level current evidence.
7. `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` — exact paired MATLAB limitation rules.
8. `docs/research/PAPER_EVIDENCE_MAP.md` / `RESEARCH_LOG.md` for paper-facing continuity.

## Project goal

HGFX v1.0 must be a functional and scientific Python/JAX replacement for the frozen MATLAB HGF Toolbox 8.2.0, with zero MATLAB runtime dependency for users and validated CPU/GPU execution where applicable.

Scientific/functional equivalence does **not** require bit-for-bit identity of every floating-point intermediate. It does require a frozen, prospective and scale-aware decision rule. Do not loosen a threshold, swap a seed, change a dataset/start/grid/model family/optimizer, or shrink a validation surface after seeing results to obtain PASS.

Historical failures remain immutable evidence. A later accepted-equivalence result is additional evidence, not a rewrite of an older direct gate.

## Completed historical milestones

M0-M17 are recorded complete in their documented scopes:

- M0 Reference Frozen
- M1 Golden Harness
- M2 Parameter/Config Parity
- M3 Scalar Numerical Parity
- M4 HGF Forward Parity
- M5 eHGF Forward Parity
- M6 uHGF Forward Parity
- M7 Observation Parity
- M8 Objective Parity
- M9 Compatibility Fitting
- M10 Hessian/LME Parity
- M11 Simulation Parity
- M12 Complete Model Coverage
- M13 API Compatibility
- M14 Native GPU Engine — physical H100 evidence
- M15 GPU Fitting — physical H100 evidence
- M16 Batch Engine — physical H100 evidence
- M17 Multi-GPU — physical correctness plus shared/contended-node scaling evidence

Do not reinterpret a historical PASS beyond its documented scope. Reuse GPU evidence only where unchanged code/data-path applicability is documented.

## Current official M18 evidence

Latest unchanged official direct gate:

- workflow: `M18 Official Workflow Closure`
- run: `34823572071`
- job: `103910417693`
- tested implementation head: `648c3f84905eb7fe952c070e5ee858e48de4a3fa`
- result: **7/9 direct PASS**
- passing: D01_bayes, D01_fit, D03_fit, D05_fit, D06_bayes, D06_fit, D07_fit
- failing direct cases: D02_fit, D08_fit
- artifact: `m18-official-workflows`, ID `10339454535`
- artifact SHA-256: `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`

Reference-aware established cases:

- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY**.
- D04 uHGF -> AR(1): **PASS**, run `34763542557`.
- exact historical 512-trial case: **REFERENCE_LIMITATION_MATCH** in that exact paired scope only.

PR #26 remains the integration path; do not merge on implementation alone.

## New frozen equivalence policy

Commit `3bea320ac6e9f0f7cef26e63ac18e50c422a834a` added `matlab-equivalence-policy-1`.

Decision layers:

1. exact contract equality;
2. existing scale-aware numerical tolerance (`abs(diff) <= atol + rtol*abs(reference)`), not decimal-place rules;
3. prospective endpoint-sensitivity numerical equivalence when exact endpoint replay/core inference/trace conditions are satisfied;
4. separately preregistered inferential equivalence covering fit, parameters/identifiability, uncertainty, predictive/residual behavior and model evidence/selection.

Existing M18 tolerances remain unchanged. Do not create a D02/D08-specific broader numeric threshold after observing a failure.

## D08 — IMPLEMENTED BUT NOT VALIDATED

Historical direct mismatch in run `34823572071`:

- `fit.traj.epsi`, first zero-based index `(175,1)`;
- HGFX `138.87836008346915`;
- MATLAB `138.8783558587791`;
- absolute difference `4.224690043130642e-6`.

Focused endpoint diagnostic:

- run `34823572192`;
- artifact `10339403480`;
- artifact SHA-256 `c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de`;
- largest fitted endpoint parameter abs diff `2.5768804867709605e-9` at zero-based index 8;
- HGFX replay at the exact MATLAB endpoint reproduces focused MATLAB `epsi` exactly;
- HGFX replay at the exact MATLAB endpoint reproduces MATLAB `negLj` exactly to the exported binary64 value;
- changing parameter 8 to MATLAB's endpoint substantially reduces the focused epsi discrepancy;
- optimizer trace and MATLAB-path objective diagnostics pass the frozen gate.

Interpretation: strong endpoint-sensitivity evidence, not a reason to increase global tolerance.

Frozen prospective holdout:

- seeds `271828182` and `314159265`, frozen before first execution;
- official USDCHF data, `uhgf + gaussian_obs`, official D08 params/default configs, quasinewton;
- unchanged existing field tolerances;
- exporter/checker/workflow implemented;
- latest observed run `34826235671` was **queued**.

Do not call D08 PASS until **both** frozen holdouts complete under the unchanged Level-2 rule. If both pass, record `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` with exact run/job/artifact/hash provenance while preserving the historical direct failure. If either fails, preserve the failure and keep D08 open; never replace its seed/rule.

Calibration record: `reference/validation/m18_d08_endpoint/decision.json`.

## D02 — BLOCKED / INFERENCE_EQUIVALENCE_FAIL

Current evidence:

- exact MATLAB endpoint replay in HGFX: PASS;
- initial Ridders gradient: PASS at frozen tolerance;
- MATLAB optimizer-path objective replay: PASS over 22 points;
- quasi-Newton step/BFGS replay from exact MATLAB state: machine-level agreement;
- optimizer path nevertheless diverges;
- representative endpoint/Hessian/covariance/correlation/model-evidence/prediction/residual values differ materially.

Key current differences from official evidence:

- final transformed parameter index 12: HGFX `-1.2520696012979948`, MATLAB `-1.0185859753674815`;
- H[0,0]: `0.30808977632407525` vs `0.9998054857037648`;
- Sigma[0,0]: `10.242002825962189` vs `1.0001982837227512`;
- Corr[0,1]: `-0.8242120336850707` vs `0.0015029079855196361`;
- LME: `-78.28285368561887` vs `-77.62115775483699`.

Therefore D02 cannot be accepted as harmless endpoint noise. Decision record: `reference/validation/m18_d02_inference/decision.json` => **INFERENCE_EQUIVALENCE_FAIL / BLOCKING**.

### Frozen next diagnostic

`m18-d02-basin-probe-1` is frozen before first execution in `docs/validation/M18_D02_BASIN_DIAGNOSTIC.md`.

It evaluates both MATLAB and HGFX negative log joint at the exact same 9 transformed-parameter vectors between their fitted endpoints:

`alpha = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1]`

with unchanged M18 default `rtol=3e-8`, `atol=3e-10`.

Implementation present:

- `reference/matlab/export_m18_d02_basin_reference.m`
- `tools/prepare_m18_d02_basin_probe.py`
- `reference/matlab/evaluate_m18_d02_basin_points.m`
- `tools/check_m18_d02_basin_probe.py`
- `.github/workflows/m18-d02-basin-diagnostic.yml`

Interpret only as:

- any shared-point objective failure => `SAME_VECTOR_IMPLEMENTATION_MISMATCH`;
- all shared-point objective passes => `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`.

Neither closes D02. D02 exits only via direct frozen-gate success, a separately preregistered Level-3 inferential-equivalence PASS, or a valid exact paired reference limitation (not currently supported because MATLAB succeeds).

Earlier `exp`, Ridders and tiny forward-state/likelihood diagnostics remain preserved history. Do not resume endless last-bit repair unless the frozen classifier/evidence demonstrates that a micro-difference is consequential to the required inference path.

## Immediate next actions

1. Inspect `M18 D08 Equivalence Holdout` execution. If completed, archive comparison, exact run/job/artifact/hash and update D08 decision/status without modifying the frozen protocol.
2. Inspect `M18 D02 Basin Diagnostic`. If completed, archive the classification and next evidence target without treating the diagnostic as PASS.
3. Only then continue D02 engineering along the classifier branch:
   - same-vector fail => localize/fix exact implementation point with regression-first change;
   - same-vector pass => investigate conditioning/gradient amplification/path/termination.
4. Keep D08 endpoint-sensitive last-bit repair off the critical path if the prospective Level-2 holdout passes.
5. After D02/D08 release-acceptable outcomes, continue D09-D12, paired recovery, robustness/backend closure, aggregate evidence, M19 then M20.

## Remaining post-D02/D08 work

Follow `V1_TODO.md` exactly:

- remaining source/demo contract coverage including D09;
- S6 D10 Corr/Sigma/plot surface, D11 residual diagnostics, D12 Bayesian parameter averaging;
- S7 paired MATLAB/HGFX parameter/model recovery under frozen protocols;
- S8 only evidence-backed HGFX-only repairs;
- S9 robustness plus CPU/JAX/physical-GPU closure and H100 applicability audit;
- S10 aggregate evidence checker/index, full applicable regression/demo suite, clean install, docs/API/licenses, zero MATLAB runtime dependency;
- M19 Methods Paper Dataset Frozen;
- M20 v1.0 Candidate only after release gate passes.

## Scientific/engineering integrity rules

- Never declare PASS without its documented gate/evidence.
- Never relax threshold/seed/data/start/grid/model/optimizer after observing results to obtain PASS.
- Never hide failed experiments or rewrite historical evidence.
- Never classify a scientific/reference limitation without matched MATLAB evidence.
- Distinguish implementation mismatch, optimizer/numerical mismatch, model-selection mismatch, reference limitation, insufficient reference evidence, endpoint-sensitivity equivalence and inferential equivalence.
- Compare same family/config/data/parameters/starts/workflow before blaming implementation.
- A MATLAB limitation may be acceptable for v1; an unresolved HGFX-only inference divergence where MATLAB succeeds is blocking.

## Status vocabulary

Use only: **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**.

When a gate changes, synchronize `V1_TODO.md`, `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, the validation matrix, this handoff and issue #24. For paper-relevant changes also update `docs/research/PAPER_EVIDENCE_MAP.md` and `RESEARCH_LOG.md`.