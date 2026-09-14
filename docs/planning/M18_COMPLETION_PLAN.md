# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Objective

Deliver HGFX v1.0 as a functional/scientific Python replacement for MATLAB HGF Toolbox 8.2.0, with no MATLAB runtime dependency for users. Compatibility is judged under the frozen tiered equivalence and reference-limitations policies. Historical and prospective failures remain immutable even when a later exact-scope limitation is release-acceptable.

## Current baseline

| Item | Status | Evidence |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | immutable historical gate |
| M0-M17 | PASS in documented scopes | gate documents/evidence |
| D02 direct fit gate | FAIL, preserved | optimizer/inference mismatch |
| D02 exact official release disposition | **REFERENCE_LIMITATION_MATCH** | `M18_D02_REFERENCE_LIMITATION.md` |
| D08 prospective Level-2 holdout | **FAIL, preserved** | repaired-product run `34842943696` |
| D08 exact failed-seed release disposition | **REFERENCE_LIMITATION_MATCH** | `M18_D08_REFERENCE_LIMITATION.md`; MATLAB self-sensitivity run `34846375826` |
| D09 official sampleModel workflow | **PASS** | run `34842943557`, artifact `10346184455`, SHA-256 `6c754cc02ce621c66d67224884c5347c61468cdfb6f3de81dffb03898d02b85c` |
| D10/D11 analysis surfaces | **PASS** | run `34847266268`, artifact `10348099156`, SHA-256 `a69045cc4e1ad388c64dec7235f8c9d2ad42f6885c6210d31b979d2284b48317` |
| D12 Bayesian parameter averaging | **PASS** | run `34854238549`, job `104009543024`, artifact `10352486569`, SHA-256 `14ab041b2473a13496377f63d6d1897578d1785128406eadbc1d6d44ae119883` |
| v1 release | OPEN | issue #24 |

## Ordered work packages

| Step | Status | Exit condition |
|---|---|---|
| S1 policy/semantics | DONE | tiered equivalence + reference-limit policies frozen |
| S2 D04 official workflow | PASS | exact workflow validated |
| S3 remaining workflow contracts | **DONE** | D09-D12/source-output mapping implemented and validated |
| S4 binary demos | **release-acceptable in current exact official scope** | D01/D03/D05 direct PASS; D02 exact-scope reference limitation disclosed; D09 PASS |
| S5 continuous demos | **release-acceptable in current exact official scope** | D06/D07 healthy; D08 failed holdout preserved + exact failing-seed reference-limitation disposition |
| S6 analysis/output surfaces | **PASS** | D10/D11/D12 evidence-backed PASS |
| S7 paired recovery | **NOW / IN PROGRESS** | paired MATLAB/HGFX parameter/model recovery completed on frozen protocol |
| S8 evidence-backed repairs | OPEN/conditional | repair only demonstrated required-scope HGFX-only mismatches from S7 |
| S9 robustness/backend | OPEN/TODO | robustness + CPU/JAX/physical-GPU applicability matrix closed |
| S10 release acceptance | OPEN/TODO | aggregate evidence, install/docs/examples/licenses/no-MATLAB-runtime complete |

## D02 disposition

D02 remains a direct/inference failure but is release-acceptable only in the exact official scope as `REFERENCE_LIMITATION_MATCH`. Shared-vector objectives pass, optimizer transition replay agrees, localized residuals are binary64-scale, and the frozen MATLAB reference itself leaves the existing endpoint gate for all six preregistered one-spacing start perturbations. See `../validation/M18_D02_REFERENCE_LIMITATION.md`.

## D08 disposition

The prospective Level-2 holdout remains failed and visible: seed `271828182` passed; seed `314159265` remained `INFERENCE_EQUIVALENCE_FAIL` after the evidence-linked USDCHF prior repair.

For the exact failing seed only, release accounting is now `REFERENCE_LIMITATION_MATCH` because:

- exact MATLAB-endpoint replay has no mismatch;
- shared-state objective/gradient and quasi-Newton transition localization does not demonstrate a material HGFX-only semantic defect;
- source-likelihood localization is exact in the observation outputs/reduction used by the selected diagnostic sample;
- MATLAB self-sensitivity run `34846375826` reproduces the baseline endpoint exactly, then 13/14 independent `+/-eps(x)` start perturbations leave the unchanged endpoint gate.

See `../validation/M18_D08_REFERENCE_LIMITATION.md` and `../../reference/validation/m18_d08_reference_limitation/decision.json`.

This does **not** convert the holdout to PASS and does not generalize beyond seed `314159265` in the frozen workflow.

## Anti-endless-patching rule

Do not chase floating-point micro-differences merely because they exist. Repair only when frozen evidence links a difference to a required semantic mismatch. Exact-scope reference sensitivity can justify a disclosed `REFERENCE_LIMITATION_MATCH`; it never justifies global tolerance widening or post-hoc seed/start/grid changes.

## S7 — paired recovery next

Use a separately frozen paired product protocol, not the historical M18 gate as a substitute. MATLAB and HGFX must receive the same truth/data/config/free-fixed parameter semantics/starts/candidate models and selection rule. Preserve all failed fits and classifications. The historical M18 scientific FAIL remains untouched.

Required paired work:

1. parameter recovery for `hgf_binary`, `ehgf_binary`, `uhgf_binary` on the frozen original 128/256-trial and 0.15/0.35 prior-SD grid;
2. candidate-model recovery with the same generated datasets and BIC winner rule, retaining AIC as diagnostic;
3. classify each material mismatch as implementation, optimizer/numerical, model-selection, reference limitation, or insufficient evidence;
4. keep issue #21 / M18C.2 as a separate preregistered 128/256/512/1024 horizon extension rather than changing the original grid.

## Evidence contract

Every required result records reference/HGFX SHA, protocol version, data/config/seed/start, environment, command, raw outputs/failures, tolerances, classification, run/job/artifact IDs and artifact SHA-256. GPU claims additionally require physical device/runtime evidence.

## Release interpretation

M18/v1 remains OPEN. D02/D08 exact-scope reference limitations and D09-D12 completion remove the previous workflow-surface blockers, but paired recovery, robustness/backend applicability, aggregate evidence, clean install/examples/docs/API/licenses and no-MATLAB-runtime verification are still required before M19 evidence freeze and M20 v1 candidate.
