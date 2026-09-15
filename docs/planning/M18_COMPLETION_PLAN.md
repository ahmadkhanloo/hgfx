# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-15
Status: **IN PROGRESS — ONLY PHYSICAL H100 + FINAL FREEZE/CANDIDATE REMAIN**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Objective

Deliver HGFX v1.0 as a functional/scientific Python replacement for MATLAB HGF Toolbox 8.2.0, with no MATLAB runtime dependency for users. Compatibility is judged under the frozen equivalence/reference-limitation policies. Historical and prospective failures remain immutable even when an exact-scope limitation is release-acceptable.

## Current baseline

| Item | Status | Evidence |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | immutable historical gate |
| M0-M17 | PASS in documented scopes | milestone evidence |
| D02 direct fit | FAIL, preserved | historical/direct evidence |
| D02 exact official release disposition | `REFERENCE_LIMITATION_MATCH` | `M18_D02_REFERENCE_LIMITATION.md` |
| D08 prospective Level-2 holdout | FAIL, preserved | repaired-product run `34842943696` |
| D08 exact failed-seed disposition | `REFERENCE_LIMITATION_MATCH` | `M18_D08_REFERENCE_LIMITATION.md` |
| D09 official sampleModel | PASS | run `34842943557` |
| D10/D11 analysis surfaces | PASS | run `34847266268` |
| D12 Bayesian parameter averaging | PASS | run `34854238549` |
| S7 paired parameter recovery | `REFERENCE_LIMITATION_MATCH` — exact frozen grid | run `34896442847`, artifact `10370615292` |
| S7 paired model selection | `PASS_PAIRED_MODEL_SELECTION` | 36/36 BIC winners match |
| S8 evidence-backed repair | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no open required-scope S7 mismatch |
| S9 CPU/backend | `PASS_CPU_BACKEND_EQUIVALENCE` | run `34901924475`, job `104169632034`, artifact `10371308067` |
| S9 physical GPU | BLOCKED / DEFERRED | fresh H100 evidence still required |
| S10 release readiness | PASS | current-head rerun `34934079865`, artifact `10383235791` |
| M19 evidence freeze | PREPARED / BLOCKED BY H100 | preflight run `34934079973` |
| M20 v1 candidate | PREPARED / BLOCKED BY H100 + M19 | preflight run `34934079973` |

## Ordered work packages

| Step | Status | Exit condition |
|---|---|---|
| S1 policy/semantics | DONE | frozen equivalence + reference-limit policies |
| S2 D04 official workflow | PASS | exact workflow validated |
| S3 remaining workflow contracts | DONE | D09-D12/source-output mapping validated |
| S4 binary demos | RELEASE-ACCEPTABLE | D01/D03/D05 direct PASS; D02 exact limitation disclosed; D09 PASS |
| S5 continuous demos | RELEASE-ACCEPTABLE | D06/D07 healthy; D08 holdout FAIL preserved + exact limitation disposition |
| S6 analysis/output surfaces | PASS | D10/D11/D12 evidence-backed |
| S7 paired recovery | DONE / RELEASE-ACCEPTABLE | exact-grid recovery limitation + 36/36 model-selection parity |
| S8 evidence-backed repairs | DONE | no open required-scope S7-derived mismatch |
| S9 robustness/backend | CPU PASS; PHYSICAL GPU BLOCKED/DEFERRED | same frozen S9 path must pass physical H100 applicability |
| S10 release acceptance | PASS | clean wheel/install/example/docs/API/licenses/zero-MATLAB-runtime |
| M19 evidence freeze | PREPARED / BLOCKED BY H100 | final manifest status `FROZEN` only after H100 PASS |
| M20 v1.0 candidate | PREPARED / BLOCKED BY H100 + M19 | final candidate checker PASS after M19 freeze |

## S7/S8 closure discipline

S7 protocol `m18-s7-paired-recovery-1` is frozen. MATLAB and HGFX share the same parameter-recovery failures in the exact paired grid; these remain `REFERENCE_LIMITATION_MATCH`, not scientific PASS. All 36 BIC model-selection winners match. Historical M18 FAIL remains preserved.

The real standard-HGF semantic defect found during S7/S8 was repaired at `0239f52f772825e0a4fc74cdf3559cafa18a603e`. S8 is closed for the required v1 scope. Historical localization probes that deliberately enter invalid negative-posterior-precision regions are retained for provenance but are manual diagnostics, not ordinary PR/release gates. Do not reopen S7/S8 merely because those historical probes reproduce the documented invalid-region failure in MATLAB/HGFX.

## Anti-endless-patching rule

Do not chase floating-point micro-differences merely because they exist. Repair only when frozen evidence links a difference to a required semantic mismatch. A shared MATLAB/HGFX limitation may be a scoped `REFERENCE_LIMITATION_MATCH`; this never authorizes global tolerance widening or post-hoc changes to seed, start, dataset, grid, model family or optimizer.

## S9 final external evidence

Frozen protocol: `m18-s9-robustness-backend-1`.

CPU/backend evidence is closed and PASS. The only unexecuted S9 cell is physical GPU applicability. A fresh H100 run must use the current numerical path, record device/runtime/command/source evidence, demonstrate actual GPU residency, and satisfy the frozen JAX CPU-vs-GPU final-objective gap `<= 1e-7`. CPU or mocked-device evidence cannot substitute.

No `src/hgfx` file changed between numerical repair `9c53af707a60d27ee3d9d37e5122e7a0ba7d5460` and the release-preparation head, so the deferred H100 run validates the same repaired numerical path.

## S10 evidence

S10 is closed. Latest release-readiness rerun on release-preparation head `87e3b01fdbdbe5f157ba8dc7f1309335408a165a` passed: run `34934079865`, wheel artifact `10383235791`, SHA-256 `8abf4488e91c6ae28983c318670f4a92dfab57c4acc8caad494be02fca47eb2b`.

## M19/M20 preparation

M19/M20 preflight passed on `87e3b01fdbdbe5f157ba8dc7f1309335408a165a`: run `34934079973`, job `104268154143`, artifact `10383425031`, SHA-256 `3f711a260f68ff0454d18b2b09b3645d28ab5b370384c8729d4fd431bee5e7cf`.

This is **preflight PASS only**. M19 may not be called PASS until the physical-H100 record is present and `scripts/build_v1_evidence_manifest.py --mode finalize` produces a `FROZEN` manifest. M20 may not be called PASS until M19 is frozen, release version metadata is promoted, and `scripts/check_m20_candidate.py --mode finalize` succeeds.

## Next action

Physical H100 evidence is the only external input still missing. It is explicitly deferred by the user and does not block preparation work. Once supplied: validate it without changing frozen criteria, finalize M19, promote release-candidate metadata, execute M20 finalize, then make PR #26 ready/merge/tag only if all final gates pass.
