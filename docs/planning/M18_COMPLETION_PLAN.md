# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-15
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
| D08 exact failed-seed release disposition | **REFERENCE_LIMITATION_MATCH** | `M18_D08_REFERENCE_LIMITATION.md` |
| D09 official sampleModel workflow | **PASS** | run `34842943557` |
| D10/D11 analysis surfaces | **PASS** | run `34847266268` |
| D12 Bayesian parameter averaging | **PASS** | run `34854238549` |
| S7 paired parameter recovery | **REFERENCE_LIMITATION_MATCH — exact frozen grid** | run `34896442847`, artifact `10370615292` |
| S7 paired model selection | **PASS_PAIRED_MODEL_SELECTION** | 36/36 BIC winners match; BA `0.5833333333333334` both implementations |
| S8 evidence-backed repair | **DONE for current required S7 scope** | HGF oracle repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no unresolved S7 mismatch |
| v1 release | OPEN | issue #24 |

## Ordered work packages

| Step | Status | Exit condition |
|---|---|---|
| S1 policy/semantics | DONE | tiered equivalence + reference-limit policies frozen |
| S2 D04 official workflow | PASS | exact workflow validated |
| S3 remaining workflow contracts | DONE | D09-D12/source-output mapping implemented and validated |
| S4 binary demos | release-acceptable in current exact official scope | D01/D03/D05 direct PASS; D02 exact-scope reference limitation disclosed; D09 PASS |
| S5 continuous demos | release-acceptable in current exact official scope | D06/D07 healthy; D08 failed holdout preserved + exact failing-seed reference-limitation disposition |
| S6 analysis/output surfaces | PASS | D10/D11/D12 evidence-backed PASS |
| S7 paired recovery | **DONE / release-acceptable** | parameter criteria match MATLAB and are exact-grid `REFERENCE_LIMITATION_MATCH`; 36/36 model winners match |
| S8 evidence-backed repairs | **DONE / no open S7-derived mismatch** | demonstrated HGF semantic defect repaired/regression-backed; final paired evidence has no implementation/optimizer/model-selection mismatch |
| S9 robustness/backend | **NOW / IN PROGRESS** | robustness + CPU/JAX/physical-GPU applicability matrix closed |
| S10 release acceptance | OPEN/TODO | aggregate evidence, install/docs/examples/licenses/no-MATLAB-runtime complete |

## D02 and D08 dispositions

D02 remains a direct/inference failure but is release-acceptable only in the exact official scope as `REFERENCE_LIMITATION_MATCH`. D08's prospectively frozen Level-2 holdout remains failed; exact seed `314159265` is release-acceptable only as a scoped `REFERENCE_LIMITATION_MATCH`. Neither disposition changes historical evidence or generalizes.

## S7 disposition

Protocol `m18-s7-paired-recovery-1` was frozen before execution with HGF/eHGF/uHGF, `unitsq_sgm`, trial counts 128/256, truth scales 0.15/0.35, six parameter-recovery replicates and three model-recovery replicates per stratum, identical exported paired data/truth/config/starts, and BIC model selection.

Official run `34896442847` completed all 12 shards. Aggregate job `104163079125` produced artifact `10370615292`, SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92`.

Parameter recovery is not a scientific PASS: MATLAB and HGFX fail the same frozen recovery criteria with nearly identical metrics. Under `MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, that is accepted for v1 product equivalence as `REFERENCE_LIMITATION_MATCH` in this exact grid. Model recovery passes directly: all 36 BIC winners match and both implementations have balanced accuracy `0.5833333333333334`.

The historical M18 scientific FAIL remains preserved. A real standard-HGF oracle mismatch uncovered during localization was repaired in `0239f52f772825e0a4fc74cdf3559cafa18a603e`; it was not reclassified as a limitation. MATLAB termination measurement was corrected in `96daac8e8fe889deaf1c8c4b5f92f2c6f676262c` without changing fitting inputs/settings.

Decision: `../validation/M18_S7_REFERENCE_LIMITATION.md` and `../../reference/validation/m18_s7_reference_limitation/decision.json`.

## Anti-endless-patching rule

Do not chase floating-point micro-differences merely because they exist. Repair only when frozen evidence links a difference to a required semantic mismatch. Exact-scope reference sensitivity or a shared MATLAB/HGFX limitation may justify a disclosed `REFERENCE_LIMITATION_MATCH`; neither justifies global tolerance widening or post-hoc seed/start/grid changes.

## S9 — robustness/backend next

Freeze S9 before executing final evidence. Required matrix must separate:

1. **robustness behavior** — required trial horizons/regimes, missing/ignored trials and initialization perturbations;
2. **backend agreement** — compatibility vs JAX CPU on the same supported path;
3. **physical GPU applicability** — JAX CPU vs physical GPU using the same validated code/data path where supported.

Existing criteria from the frozen historical M18 protocol remain diagnostic anchors: compatibility-vs-JAX CPU final objective gap <= `0.10`, and JAX CPU-vs-GPU final objective gap <= `1e-7` where a GPU is visible. Do not invent broader scientific recovery PASS thresholds after observing S7.

Prior H100 evidence may be reused only if the code and data path exercised by S9 is demonstrated unchanged/applicable and hardware/runtime evidence is explicitly linked. Otherwise obtain a new physical-H100 result. Missing coverage remains OPEN rather than being inferred from CPU or mocked-device tests.

## Evidence contract

Every required result records reference/HGFX SHA, protocol version, data/config/seed/start, environment, command, raw outputs/failures, tolerances, classification, run/job/artifact IDs and artifact SHA-256. GPU claims additionally require physical device/runtime evidence.

## Release interpretation

M18/v1 remains OPEN. D02/D08 scoped dispositions, D09-D12, and S7/S8 closure remove their previous blockers. Remaining blockers are S9 robustness/backend applicability and S10 reproducible release acceptance before M19 evidence freeze and M20 v1 candidate.
