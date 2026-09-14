# Agent Handoff

Last synchronized: 2026-09-14
Branch: `migration/m18-workflow-closure`
Head before this synchronization: `942ca86eea1fe52e8326c14f8fe175a5faa3db84`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`
Milestone: **M18 v1 MATLAB-equivalence closure — IN PROGRESS / OPEN**
Historical M18 scientific experiment: **FAIL, preserved**

## Read first

1. `V1_TODO.md`
2. `M18_COMPLETION_PLAN.md`
3. `V1_RELEASE_GATE.md`
4. `../validation/MATLAB_EQUIVALENCE_POLICY.md`
5. `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`
6. `../validation/M18_D02_BASIN_DIAGNOSTIC.md`
7. `../validation/M18_D08_HOLDOUT_OPTIMIZER_DIAGNOSTIC.md`
8. `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
9. `../research/PAPER_EVIDENCE_MAP.md` and `RESEARCH_LOG.md`

## Current official evidence

Official fit/Bayes direct gate: run `34823572071`, job `103910417693`, head `648c3f84905eb7fe952c070e5ee858e48de4a3fa`, **7/9 direct PASS**. Artifact ID `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.

Passing direct cases: D01_bayes, D01_fit, D03_fit, D05_fit, D06_bayes, D06_fit, D07_fit. Blockers: D02_fit, D08_fit.

Established paired evidence: D02 model selection `PASS_MODEL_SELECTION_PARITY`; D04 uHGF→AR(1) PASS run `34763542557`; exact historical 512 case `REFERENCE_LIMITATION_MATCH` only in exact scope.

## D08 — BLOCKED after failed prospective holdout

The Level-2 holdout was frozen before execution with seeds 271828182 and 314159265 and unchanged official data/model/config/optimizer/tolerances.

Run `34826235671`, job `103918945542`, head `57cd9216fde5b36dd3a6ef033df2b2369e96b022`, artifact ID `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1`:

- seed 271828182 PASS;
- seed 314159265 `INFERENCE_EQUIVALENCE_FAIL`;
- same MATLAB endpoint replay has no mismatches;
- fitted optimizer path and core inference diverge beyond Level-2 requirements.

Preserved decision: `reference/validation/m18_d08_holdout/decision.json`.

Do **not** broaden tolerance, replace seed, or reinterpret this failed prospective protocol. D08 remains BLOCKED.

Next exact task is diagnostic only: run `m18-d08-holdout-optimizer-probe-1` on frozen seed 314159265, comparing full traces and exact MATLAB shared-state objective/gradient/inverse-Hessian around rows 38-44. Current queued run: `34829121895`. If shared-state numerics fail, localize implementation/primitive; if they pass while path diverges, investigate optimizer finite-difference/state/conditioning/termination sensitivity.

## D02 — BLOCKED / INFERENCE_EQUIVALENCE_FAIL

Shared-state evidence is strong at several reference points, but actual fitted endpoint, H/Sigma/Corr/LME/predictions/residuals differ materially. D02 cannot be accepted as harmless decimal noise.

Frozen diagnostic `m18-d02-basin-probe-1` uses 9 fixed line points and unchanged `rtol=3e-8`, `atol=3e-10`.

First run `34827198731` failed mechanically because structural NaN fixed slots were checked with NaN-unsafe equality. Preserve that run as **HARNESS EXECUTION FAILURE**, not scientific evidence. Commit `942ca86eea1fe52e8326c14f8fe175a5faa3db84` fixes only NaN-aware checking and free-coordinate interpolation; protocol values are unchanged. Corrected run `34829122057` is queued.

Interpret corrected result only as:

- shared-point failure => `SAME_VECTOR_IMPLEMENTATION_MISMATCH`;
- all shared points pass => `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`;
- neither closes D02.

## Immediate continuation

1. Read D02 run `34829122057` when it completes; archive run/job/artifact/hash and diagnostic classification.
2. Read D08 optimizer diagnostic run `34829121895` when it completes; archive run/job/artifact/hash and classification.
3. Follow the resulting evidence branch without modifying frozen scientific inputs.
4. Keep historical failures and failed prospective D08 holdout visible.
5. After D02/D08 release-acceptable outcomes, continue D09-D12, paired recovery, robustness/backend closure, aggregate evidence, M19, M20.

## Integrity rules

Never declare PASS without documented gate evidence; never tune thresholds/seeds/data/starts/grids/model/optimizer after results; never hide failures; never call a scientific/reference limitation without exact paired evidence; distinguish implementation, optimizer/numerical, model-selection, reference limitation, insufficient evidence and accepted equivalence.

Use statuses only: **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**.