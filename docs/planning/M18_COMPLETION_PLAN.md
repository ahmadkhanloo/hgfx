# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-13
Status: **IN PROGRESS**
Current branch: `migration/m18-workflow-closure`
Last tested implementation/diagnostic head: `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`
Documentation-only head after paper sync: `5b37e7df2a4a47f5159c47c75517d3f404a75b31`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Objective and authority

Deliver a Python toolbox that reproduces the frozen MATLAB HGF Toolbox 8.2.0 model coverage, public workflows, demos and scientific outputs, without MATLAB as a user runtime dependency.

The compatibility target includes both MATLAB successes and MATLAB's demonstrated limitations/model-family choices. Apply `V1_PRODUCT_DEFINITION.md`, `V1_RELEASE_GATE.md`, `V1_TODO.md` and `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` together.

For current execution ordering, `V1_TODO.md` plus this 2026-09-13 plan supersede older 2026-09-12 notices in other planning files that still name D04 as the immediate next task. D04 is now validated PASS.

Required MATLAB functionality cannot be deferred beyond the initial v1.0 release. Beyond-reference improvements may be planned separately for v2.

## Current validated baseline

| Item | Status | Evidence / exact scope |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | Original thresholds/artifacts remain immutable; M18B protocol success does not rewrite it |
| M18B integrity-aware protocol | PASS recorded | Existing repository evidence; not equivalent to closing all v1 recovery requirements |
| Exact historical 512-trial case | REFERENCE_LIMITATION_MATCH | Exact paired MATLAB/HGFX case only; not arbitrary 512-trial support |
| D02 model-selection behavior | PASS_MODEL_SELECTION_PARITY | MATLAB/HGFX classic HGF fail correspondingly; eHGF succeeds in both |
| D04 uHGF -> AR(1) official workflow | PASS | run `34763542557` at `faf97bf...` |
| Official fit/Bayes closure set | IN PROGRESS — 7/9 PASS | run `34776952053`, job `103776700085`; D02_fit and D08_fit remain blocking |
| Latest official evidence artifact | RECORDED | `m18-official-workflows`, ID `10323968264`, SHA-256 `ac4d0094cfe49b5e5ee8d5c75f89311c35a2727b46ed433078412be63c3b5f9c` |
| Frozen reference verification | PASS | exact HGF commit `2437f4dc...`; 334 MATLAB files verified in latest run |
| Targeted M18 API/IEEE/numerical regressions | PASS | 7 tests passed in latest official run |
| v1 product acceptance | OPEN | issue #24; release criteria not yet fully closed |

The latest official closure run intentionally failed because D02_fit and D08_fit remain unresolved. No tolerance, seed, dataset, start, model-family or optimizer rule was relaxed.

## Ordered work packages and current status

| Step | Status | Work and exit gate |
|---|---|---|
| S1 — reconcile gate semantics | **DONE** | MATLAB-reference limitation/model-family policy is explicit; historical M18 FAIL and M18B protocol status remain distinct |
| S2 — close D04 official workflow | **PASS** | uHGF -> AR(1) workflow validated on current tested path; do not rerun merely because an older plan says it is next |
| S3 — freeze remaining workflow contracts | **IN PROGRESS** | Required fit/Bayes contracts are frozen; finish source-to-workflow mapping for remaining D09-D12/output surfaces before their execution |
| S4 — binary demo workflows | **IN PROGRESS** | D01/D03/D05 current official fit/Bayes checks pass; D02 fit remains blocking; D09 demo wrapper remains open |
| S5 — continuous demo workflows | **IN PROGRESS** | D06 Bayes/fit and D07 fit pass; D08 fit remains blocking |
| S6 — analysis/plot surfaces | **OPEN/TODO** | Close D10-D12 and remaining required output/plot semantics |
| S7 — paired recovery classification | **OPEN/TODO** | Run product-level paired MATLAB/HGFX parameter/model recovery; preserve historical experiments separately |
| S8 — repair demonstrated mismatches | **IN PROGRESS** | Current repair targets are D02/D08; only evidence-backed HGFX-only mismatches may be fixed |
| S9 — robustness/backend closure | **OPEN/TODO** | Required robustness matrix plus compatibility/JAX CPU/physical-GPU agreement; prior H100 evidence requires applicability audit |
| S10 — reproducible release acceptance | **OPEN/TODO** | Aggregate evidence checker/report, clean install, full demos/regression/docs/licenses/no-MATLAB-runtime, then M19/M20 |

## Immediate next action — D02 then D08

### D02_fit

The problem remains below the optimizer-control layer, but the numerical source is now more tightly localized.

Established evidence:
- MATLAB reference-point comparison: PASS.
- Initial Ridders gradient: PASS at the existing acceptance tolerance.
- MATLAB-path objective replay: PASS at the existing gate tolerance.
- Replaying quasi-Newton step normalization/backtracking/BFGS from exact MATLAB `x/grad/T` reproduces MATLAB at machine precision.
- Exact Ridders-coordinate decomposition shows perceptual and observation priors exact; remaining raw mismatch is in likelihood/forward numerics.
- A regression-first MATLAB-vs-default-runtime `exp` mismatch was frozen in commit `27bba3e44aae832e8805d25a631ebac15f81f40f`.
- The minimal MATLAB-compatible `exp` repair was applied in `7b43ae5e45f85f44d23a6e980200baca46609fbd` without changing the scientific gate; M3/M5 and other historical gates remained healthy.
- The latest selected residual probe (`parameter_2_first_ridders_minus`, trial 83) at diagnostic head `4e92ccf...` is classified **FORWARD_NUMERICAL_DIVERGENCE**.
- Selected residual differences: `inf_states` max abs `7.105427357601002e-15`; observation input max abs `1.1102230246251565e-16`; trial log-likelihood max abs `2.4868995751603507e-14`.
- Replaying the observation formula on exact MATLAB state gives zero log-likelihood difference. A tiny replay difference in `pow1mx` (`6.776263578034403e-21`) is therefore not currently evidenced as the causal scientific mismatch.
- Official `D02_fit` still diverges after amplification; latest reported first final split includes HGFX `-1.6252419364429298` vs MATLAB `-1.0185859753674815`.

Next sequence:
1. Export/compare eHGF forward intermediates at the exact frozen residual Ridders sample.
2. Identify the earliest trial/level/intermediate where the first nonzero state divergence appears.
3. Identify the responsible forward primitive/arithmetic ordering before changing code.
4. If HGFX-only and consequential, add a failing regression fixture first.
5. Apply the smallest compatibility repair and rerun the unchanged official gate.
6. Preserve all prior failed/diagnostic artifacts; do not rewrite them.

Do not change Ridders settings, quasi-Newton settings, tolerance, seed, dataset, starts or model family to force a pass.

### D08_fit

The latest frozen-gate mismatch is limited to `fit.traj.epsi` at index `(178,1)`:
- HGFX `-4.7887561410406825`;
- MATLAB `-4.788757533201755`;
- absolute difference about `1.392e-6`.

Reference-point, initial Ridders, optimizer-trace and MATLAB-path objective diagnostics otherwise pass; MATLAB-path objective replay covers 50 points.

Next sequence after D02:
1. Export/compare final free/full parameter vectors at full IEEE precision and ULP distance.
2. Replay trajectories at exact MATLAB and HGFX final vectors.
3. Decompose `epsi` around trials 177-179 into underlying states/intermediates.
4. Classify same-vector implementation mismatch vs endpoint numerical sensitivity.
5. Add a failing fixture before any repair and rerun the unchanged official gate.

## Recovery diagnosis decision procedure

1. Verify exact input/config/parameter/startpoint identity and frozen reference hashes.
2. Compare forward states and fixed-parameter objective first. On material mismatch, locate the first divergent trial/level/field/intermediate: `IMPLEMENTATION_MISMATCH`.
3. If those agree, compare optimizer path/termination, final objective, Hessian/statistics and restart selection: `OPTIMIZER_MISMATCH` when fitting semantics diverge materially.
4. If candidate families or observation models differ, use `MODEL_SELECTION_MISMATCH`; do not silently substitute eHGF/uHGF unless the MATLAB workflow does so.
5. Use `REFERENCE_LIMITATION_MATCH` only for an exact paired limitation with no earlier HGFX-only divergence.
6. If reference evidence is incomplete or ambiguous, retain `INSUFFICIENT_REFERENCE_EVIDENCE`.

A MATLAB failure is not something HGFX must repair for v1 compatibility. A MATLAB-success/HGFX-failure or materially divergent MATLAB-success/HGFX-result remains blocking until explained and, where appropriate, repaired.

## Evidence contract

For every required case retain: case ID; HGFX/reference SHA; protocol version/hash; exact data/config hashes; seeds/exported stochastic drivers; starts; environment; command; raw MATLAB/HGFX outputs including failures; per-field differences/tolerances; classification; run/job/artifact IDs or equivalent local provenance; artifact SHA-256; review decision.

GPU evidence additionally requires physical device, driver, CUDA/JAX versions and device residency. Shared/contended systems are acceptable when explicitly recorded and the acceptance criterion does not require uncontended peak performance.

Paper-facing evidence continuity is maintained in `../research/PAPER_EVIDENCE_MAP.md` and `../research/RESEARCH_LOG.md`. Those files summarize but never replace raw evidence/gates.

## Release interpretation

- **Historical M18 scientific result: FAIL** unless that exact historical gate genuinely passes in a documented later run; never rewrite failed evidence.
- **M18 v1 MATLAB-equivalence closure: OPEN** until every required workflow/surface is evidence-backed PASS or narrowly evidenced `REFERENCE_LIMITATION_MATCH`, and no required HGFX-only implementation/optimizer/model-selection mismatch remains.
- `REFERENCE_LIMITATION_MATCH` is acceptable product compatibility, not a scientific PASS claim for the underlying model.
- M19 retains its historical meaning, “Methods Paper Dataset Frozen”.
- M20 retains “v1.0 Candidate” and is reached only after S10 release acceptance.

## Operational checklist

The detailed, live checkbox list is `V1_TODO.md`. Update it, this plan, the affected validation matrix and `AGENT_HANDOFF.md` whenever a gate changes. For paper-relevant changes also update `../research/PAPER_EVIDENCE_MAP.md` / `RESEARCH_LOG.md`. Record tested implementation SHA separately from documentation-only SHA. Use only **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, or **OPEN/TODO**.
