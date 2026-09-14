# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Objective

Deliver HGFX v1.0 as a functional/scientific Python replacement for MATLAB HGF Toolbox 8.2.0, with no MATLAB runtime dependency for users. Compatibility is judged under the frozen tiered equivalence and reference-limitations policies. Historical failures remain historical failures even when a later exact-scope limitation is accepted.

## Current baseline

| Item | Status | Evidence |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | immutable historical gate |
| M0-M17 | PASS in documented scopes | gate documents/evidence |
| D02 direct fit gate | FAIL, preserved | optimizer/inference mismatch |
| D02 exact official release disposition | **REFERENCE_LIMITATION_MATCH** | decision record + run `34837033370` evidence chain |
| D02 model selection | PASS_MODEL_SELECTION_PARITY | exact paired MATLAB/HGFX behavior |
| D04 uHGF→AR(1) | PASS | run `34763542557` |
| Historical 512 case | REFERENCE_LIMITATION_MATCH | exact case only |
| D08 prospective Level-2 holdout | **FAIL / BLOCKED** | one of two frozen seeds failed |
| v1 release | OPEN | issue #24 |

## Ordered work packages

| Step | Status | Exit condition |
|---|---|---|
| S1 policy/semantics | DONE | tiered equivalence + reference-limit policies frozen |
| S2 D04 official workflow | PASS | exact workflow validated |
| S3 remaining workflow contracts | IN PROGRESS | D09-D12/source-output mapping frozen |
| S4 binary demos | **release-acceptable in current exact official scope** | D01/D03/D05 direct PASS; D02 exact-scope reference limitation disclosed |
| S5 continuous demos | IN PROGRESS | D08 remains blocking; D06/D07 healthy |
| S6 analysis/output surfaces | OPEN/TODO | D10-D12 closed |
| S7 paired recovery | OPEN/TODO | paired MATLAB/HGFX parameter/model recovery completed |
| S8 evidence-backed repairs | IN PROGRESS | no required unresolved HGFX-only implementation/optimizer/model-selection mismatch |
| S9 robustness/backend | OPEN/TODO | robustness + CPU/JAX/physical-GPU applicability matrix closed |
| S10 release acceptance | OPEN/TODO | aggregate evidence, install/docs/examples/licenses/no-MATLAB-runtime complete |

## D02 — exact official workflow resolved as a reference limitation

D02 remains a direct parity failure and historical inference failure, but is no longer treated as an unresolved HGFX-only defect for the exact official workflow.

The evidence sequence was deliberately narrowed before acceptance:

1. corrected frozen 9-point same-vector classifier: `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`, all points pass;
2. exact-state quasi-Newton transition replay: machine-level agreement;
3. frozen optimizer-source probe: exact source objective; first off-centre difference `2.842170943040401e-14`, log-likelihood only; MATLAB-sample Ridders replay exact;
4. frozen source-likelihood probe: inference states exact; trial likelihood residuals at binary64 scale, max `8.881784197001252e-16`; MATLAB's own vector/scalar reductions differ at `1.1368683772161603e-13`;
5. prospectively frozen MATLAB self-sensitivity probe: official baseline replay exact; all six independent `+/-eps(x)` start perturbations (`4.440892098500626e-16`) produce endpoints outside the existing gate, with free-parameter displacement up to about `1.5077`.

Decision: `../validation/M18_D02_REFERENCE_LIMITATION.md` and `../../reference/validation/m18_d02_reference_limitation/decision.json` => **REFERENCE_LIMITATION_MATCH**, exact official scope only.

This does not change the original direct failure, widen a tolerance, or imply generic D02-family stability.

## D08 — active fit-workflow blocker

The prospectively frozen Level-2 holdout remains failed: seed `271828182` PASS, seed `314159265` `INFERENCE_EQUIVALENCE_FAIL`.

Localization now shows:

- exact shared-state objective/gradient and QN transition evidence around the failed path classify `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- the USDCHF placeholder/prior mismatch was a real implementation discrepancy and has been repaired/validated exactly (`NO_PRIOR_DIVERGENCE`, run `34836421030`);
- the repaired product still fails the hard holdout seed, so the remaining issue is optimizer/path conditioning rather than unresolved prior semantics.

Next decision branch:

- freeze and run a MATLAB-only self-sensitivity diagnostic on the failing seed without changing its official start or failed holdout record;
- if the reference itself demonstrates comparable binary64-scale basin sensitivity, evaluate exact-scope `REFERENCE_LIMITATION_MATCH` under the existing policy;
- otherwise continue regression-first localization of the earliest path-sensitive numerical operation;
- D08 remains **BLOCKED** until one release-acceptable route is actually evidenced.

## Anti-endless-patching rule

Do not chase a floating-point micro-difference merely because it exists. Repair it only when frozen evidence links it to a required semantic mismatch. D02 now demonstrates why: one-ULP-scale perturbations inside the MATLAB reference itself can move the optimizer to a different basin. That evidence supports an exact-scope reference limitation, not a global tolerance increase.

## After D08

Proceed in order: D09-D12 → paired recovery → evidence-backed repairs → robustness/backend applicability → aggregate evidence/release checks → M19 evidence freeze → M20 v1 candidate.

## Evidence contract

Every required result records reference/HGFX SHA, protocol version, data/config/seed/start, environment, command, raw outputs/failures, tolerances, classification, run/job/artifact IDs and artifact SHA-256. GPU claims additionally require physical device/runtime evidence.

## Release interpretation

M18/v1 remains OPEN until every required surface is evidence-backed under frozen policies. `REFERENCE_LIMITATION_MATCH` is release-acceptable only in its documented exact scope and never rewrites the corresponding historical/direct failure.
