# Agent Handoff

Last synchronized: 2026-09-14
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`
Milestone: **M18 v1 MATLAB-equivalence closure — IN PROGRESS / OPEN**
Historical M18 scientific experiment: **FAIL, preserved**

## Read first

1. `V1_TODO.md`
2. `M18_COMPLETION_PLAN.md`
3. `V1_RELEASE_GATE.md`
4. `../validation/MATLAB_EQUIVALENCE_POLICY.md`
5. `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`
6. `../validation/M18_D02_REFERENCE_LIMITATION.md`
7. `../validation/M18_D08_REFERENCE_LIMITATION.md`
8. `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
9. `../validation/M18_RECOVERY_RUNBOOK.md`
10. `../research/PAPER_EVIDENCE_MAP.md` and `RESEARCH_LOG.md`

## Current release-accounting state

Direct fit/Bayes gate remains **7/9 PASS**. D02_fit and D08_fit remain direct failures; these failures are never rewritten.

Release accounting:

- **D02 exact official fit: REFERENCE_LIMITATION_MATCH**; direct/inference FAIL preserved.
- **D08 exact failed holdout seed `314159265`: REFERENCE_LIMITATION_MATCH**; prospective Level-2 holdout FAIL preserved.
- D02 model selection: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS, run `34763542557`.
- exact historical 512 case: `REFERENCE_LIMITATION_MATCH` only in exact scope.
- D09: PASS, run `34842943557`.
- D10/D11: PASS, run `34847266268`.
- D12: PASS, run `34854238549`.

## D02 exact-scope reference limitation

Decision: `../../reference/validation/m18_d02_reference_limitation/decision.json`.

The direct mismatch is preserved. Shared-vector objective, exact-state optimizer algebra, binary64 source localization and MATLAB one-spacing self-sensitivity establish an exact-workflow numerical-basin limitation. Never generalize this to other D02-family cases.

## D08 exact failed-seed reference limitation

Decision: `../../reference/validation/m18_d08_reference_limitation/decision.json`.

Prospective holdout remains FAIL. The failing seed `314159265` is release-acceptable only in the exact frozen scope because:

- repaired-product holdout `34842943696` still fails but exact MATLAB-endpoint replay has no mismatch;
- optimizer diagnostic `34842943657` => `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- the evidence-linked prior preparation defect was repaired independently and selected source-likelihood observation outputs/reduction are exact;
- MATLAB self-sensitivity `34846375826` reproduces baseline exactly and 13/14 independent one-local-spacing start perturbations leave the unchanged endpoint gate.

Do not call this Level-2 PASS, do not replace the seed/start, and do not widen tolerances.

## D09-D12 closed

- D09 artifact `10346184455`, SHA `6c754cc02ce621c66d67224884c5347c61468cdfb6f3de81dffb03898d02b85c`.
- D10/D11 artifact `10348099156`, SHA `a69045cc4e1ad388c64dec7235f8c9d2ad42f6885c6210d31b979d2284b48317`.
- D12 artifact `10352486569`, SHA `14ab041b2473a13496377f63d6d1897578d1785128406eadbc1d6d44ae119883`; scalar-vs-singleton MATLAB prior-vector compatibility repaired in product commit `21a6e9cc38c9c480745b6eade8ed9ec3bb1e9a56`.

## Immediate continuation — S7 paired recovery

Do **not** return to D02/D08 ULP chasing unless a new frozen required-scope regression shows a material semantic defect. The next unresolved product gate is paired recovery.

Freeze a new paired same-oracle protocol before execution:

- models `hgf_binary`, `ehgf_binary`, `uhgf_binary`;
- trials `128`, `256`;
- truth scales `0.15`, `0.35` prior SD;
- 6 parameter-recovery replicates per stratum;
- 3 model-recovery replicates per stratum;
- identical exported inputs/responses/truth vectors for MATLAB and HGFX; never rely on cross-language RNG identity;
- exact same configs, priors, free/fixed parameter order, transformed/native semantics, starts and default quasinewton workflow;
- candidate set identical; BIC winner rule frozen, AIC diagnostic retained;
- raw fits/failures archived and classified rather than filtered.

Original-grid workload is 72 parameter-recovery fits plus 108 model-recovery candidate fits = 180 fits. Shard execution if needed, but do not shrink the grid.

Issue #21 / M18C.2 is a separate 128/256/512/1024 horizon extension. Do not use it to redefine or rescue S7 post-hoc.

## After S7

1. S8 repair only demonstrated HGFX-only implementation/optimizer/model-selection mismatches, with regression first.
2. S9 close robustness and CPU/JAX/physical-GPU applicability; earlier H100 evidence may be reused only if code/data path applicability is documented.
3. S10 aggregate evidence/provenance, clean install, examples, docs/API/licenses and no-MATLAB-runtime checks.
4. M19 evidence freeze; M20 v1 candidate only after the release gate is truly satisfied.

## Integrity rules

Never declare PASS without documented gate evidence; never tune thresholds/seeds/data/starts/grids/model/optimizer after results; never hide failures; never call a reference limitation without exact paired evidence; distinguish direct parity, exact-scope limitation, implementation mismatch, optimizer/numerical mismatch, model-selection mismatch and insufficient evidence.
