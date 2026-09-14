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
7. `../validation/M18_D08_HOLDOUT_OPTIMIZER_DIAGNOSTIC.md`
8. `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
9. `../research/PAPER_EVIDENCE_MAP.md` and `RESEARCH_LOG.md`

## Current official evidence

Direct fit/Bayes gate remains 7/9 PASS. D02_fit and D08_fit remain direct failures; direct failures are never rewritten.

Release accounting differs:

- **D02 exact official fit: REFERENCE_LIMITATION_MATCH**; no longer an unresolved HGFX-only blocker in that exact scope.
- **D08: BLOCKED** after failed prospective Level-2 holdout.
- D02 model selection: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS, run `34763542557`.
- exact historical 512 case: `REFERENCE_LIMITATION_MATCH` only in exact scope.

## D02 — resolved exact-scope reference limitation

Decision record: `../../reference/validation/m18_d02_reference_limitation/decision.json`.

Evidence:

- `34829122057` / `103928016949` / artifact `10342907205`: 9/9 same-vector objectives pass; `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`;
- `34835728961` / `103948983708` / artifact `10344290559`: source objective exact; first off-centre log-likelihood residual `2.842170943040401e-14`; MATLAB-sample Ridders replay exact;
- `34836421105` / `103951170207` / artifact `10344591868`: inference states exact; trial-likelihood differences at <= `8.881784197001252e-16`; primitive/reduction residual only;
- `34837033370` / `103953084600` / artifact `10344991786`: MATLAB baseline exact; all six independent `+/-eps(x)` start perturbations (`4.440892098500626e-16`) end outside the existing gate, with parameter displacement up to ~`1.5077`; `MATLAB_START_ULP_BASIN_SENSITIVE`.

Interpretation: direct D02 inference mismatch remains visible, but the exact workflow's failure mechanism is a numerical-basin limitation demonstrated in MATLAB itself. Do not generalize this disposition to other D02-family cases.

## D08 — active blocker

Prospective Level-2 holdout remains failed and immutable. Failing seed: `314159265`.

Current localization:

- optimizer diagnostic `34829121895` / `103928015484` / artifact `10343726427`: `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- USDCHF prior repair validation `34836421030` / `103951169992` / artifact `10343484736`: `NO_PRIOR_DIVERGENCE`, exact prior inputs/terms/totals;
- repaired product still fails the hard holdout seed.

## Immediate continuation

1. Freeze a diagnostic-only MATLAB self-sensitivity protocol for D08 failing seed `314159265`, preserving the failed prospective holdout and official start.
2. Run it unchanged. It cannot itself confer PASS.
3. If MATLAB demonstrates comparable microscopic-perturbation basin sensitivity, evaluate exact-scope reference-limitation criteria without changing tolerances or holdout seeds.
4. If MATLAB is stable, continue regression-first localization of the earliest remaining path-sensitive numeric operation.
5. Once D08 has a release-acceptable outcome, continue D09-D12, paired recovery, robustness/backend closure, aggregate evidence, M19, then M20.

## Integrity rules

Never declare PASS without documented gate evidence; never tune thresholds/seeds/data/starts/grids/model/optimizer after results; never hide failures; never call a reference limitation without exact paired evidence; distinguish direct parity, accepted exact-scope limitation, implementation mismatch, optimizer/numerical mismatch, model-selection mismatch and insufficient evidence.
