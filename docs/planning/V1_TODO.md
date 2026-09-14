# HGFX v1.0 Live TODO

## Continuation update — 2026-09-14

At head `ae063e7a866e2ab227110fd1a771d138fad2a274`, official run
`34821444138` still reports 7/9 PASS; D02/D08 remain optimizer mismatches.
D08 now first fails `epsi` at zero-based `(175,1)` (138.87836008346915
versus MATLAB 138.8783558587791). Older numerical values below are historical.

The D08 prior diagnostic run `34821444290` / job `103903714260` /
artifact `10338820786` exposes a prior-variance input mismatch:
HGFX `4.06248750000001e-05`, MATLAB `4.0624875000000105e-05`.
A local matched-input replay reproduces all MATLAB prior terms and their total
exactly. The first classification is therefore `PRIOR_INPUT_DIVERGENCE`, not
proof of a Gaussian quadratic-form defect. Original output is preserved in
`reference/validation/m18_d08_prior/` with hashes and the raw artifact ZIP.

Next D08 step: run the additive placeholder trace (window, mean, deviations,
squares, reduction, explicit variance and MATLAB var), locate the first
operation split, then write the core regression and repair only the evidenced
cause. No input override is used by fitting; no core/tolerance/seed changes.
The new exporter is IMPLEMENTED BUT NOT VALIDATED in MATLAB until CI runs.

D02's existing log-path regression fails in focused Python 3.11 / NumPy 2.4.6
run `34821444075`, but passes locally with Python 3.12.14 / NumPy 2.5.3;
local success does not close that cross-runtime blocker.
Historical M18 FAIL and v1 closure OPEN remain unchanged.


Last synchronized: 2026-09-13
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Last tested implementation/diagnostic head: `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`
Documentation-only head after paper sync: `5b37e7df2a4a47f5159c47c75517d3f404a75b31`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

This is the live operational TODO for reaching HGFX v1.0 MATLAB-equivalence. Use it together with:

- `M18_COMPLETION_PLAN.md` for ordered S1-S10 dependencies;
- `V1_RELEASE_GATE.md` for release acceptance;
- `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` for reference-aware failure classification.

For paper-facing continuity also use `../research/PAPER_EVIDENCE_MAP.md` and `../research/RESEARCH_LOG.md`.

For current work ordering, this file and the 2026-09-13 section of `M18_COMPLETION_PLAN.md` supersede older 2026-09-12 notices that still mention D04 as the immediate next task. D04 is validated PASS and must not be repeated unless its implementation/data path changes.

## Non-negotiable product rule

HGFX v1.0 must reproduce MATLAB HGF Toolbox behavior, including its model-family choices and demonstrated limitations. A case where MATLAB itself fails or requires eHGF/uHGF/specialized models does **not** have to be made artificially successful in HGFX. Such a limitation is acceptable only when exact paired MATLAB evidence supports `REFERENCE_LIMITATION_MATCH`.

Do not improve beyond MATLAB at the cost of compatibility in v1 compatibility mode. Do not relax thresholds, change seeds/datasets, shrink validation grids, or switch model family after seeing results.

## Current validated state

- M0-M17: completed according to their recorded gates/evidence.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY** — classic HGF fails in both MATLAB/HGFX and eHGF succeeds in both.
- D04 uHGF -> AR(1) workflow: **PASS** on run `34763542557` at `faf97bf...`.
- Historical exact 512-trial case: **REFERENCE_LIMITATION_MATCH**; this is not a general 512-trial scientific PASS.
- Latest official fit/Bayes workflow closure run `34776952053`, job `103776700085`: **7/9 PASS**.
- Artifact `m18-official-workflows`, ID `10323968264`, ZIP SHA-256 `ac4d0094cfe49b5e5ee8d5c75f89311c35a2727b46ed433078412be63c3b5f9c`.
- Frozen reference verification: PASS; targeted M18 API/IEEE/FDLibm regression tests: 7/7 PASS.
- Remaining official-workflow blockers: `D02_fit`, `D08_fit`.
- PR #26 remains draft/unmerged. M18 product closure remains **OPEN**.

## NOW — close D02 and D08

### D02_fit — IN PROGRESS / BLOCKING

Evidence already established:

- MATLAB reference-point replay: PASS.
- Initial Ridders gradient: PASS at existing acceptance tolerance.
- MATLAB-path objective replay: PASS at existing gate tolerance.
- Exact quasi-Newton state replay shows BFGS/step algebra reproduces MATLAB to machine precision when fed exact MATLAB state.
- Objective decomposition at exact Ridders coordinates shows priors exact and residual differences originate in likelihood/forward numerics.
- Regression-first commit `27bba3e44aae832e8805d25a631ebac15f81f40f` froze two MATLAB-vs-default-runtime `exp` divergences.
- Compatibility repair `7b43ae5e45f85f44d23a6e980200baca46609fbd` introduced MATLAB-compatible `exp` numerics on the evidenced D02 path without changing the scientific gate.
- Latest residual probe at head `4e92ccf...` classifies the selected case as **FORWARD_NUMERICAL_DIVERGENCE**: `inf_states` max abs diff `7.105427357601002e-15`, observation input diff `1.1102230246251565e-16`, per-trial likelihood diff `2.4868995751603507e-14`.
- Replaying the observation formula on exact MATLAB state yields zero log-likelihood difference. A tiny `pow1mx` replay primitive difference (`6.776263578034403e-21`) does not propagate to replayed log-likelihood.
- Official fit remains `OPTIMIZER_MISMATCH`; current final parameter divergence includes HGFX `-1.6252419364429298` vs MATLAB `-1.0185859753674815` at the first reported final-parameter split.

Completed diagnosis/repair steps:

- [x] Export objective decomposition at exact D02 finite-difference coordinates.
- [x] Compare per-trial likelihood, total likelihood and prior terms.
- [x] Split forward-state vs observation arithmetic at an exact Ridders sample.
- [x] Add regression-first MATLAB `exp` oracle fixture.
- [x] Apply the evidenced MATLAB-compatible `exp` repair.
- [x] Rerun the unchanged official gate and preserve the remaining failure.
- [x] Probe the largest remaining per-trial unitsq likelihood mismatch and replay observation arithmetic on exact MATLAB state.

TODO, in order:

- [ ] Locate the **first eHGF forward intermediate/trial/level** that produces the remaining `~1e-16` to `~1e-14` state divergence at the frozen parameter-2 first-Ridders-minus sample.
- [ ] Determine which forward primitive/arithmetic ordering causes that earliest divergence; do not assume the `pow1mx` observation micro-difference is causal because replayed log-likelihood is exact.
- [ ] If HGFX-only and consequential, add a failing regression fixture before changing implementation.
- [ ] Apply the smallest compatibility fix; do not change frozen Ridders/quasi-Newton settings, tolerances, seed, data, starts or model family.
- [ ] Rerun the unchanged official workflow gate and archive before/after evidence.
- [ ] Exit D02 only when the official unchanged `D02_fit` gate passes or exact paired evidence supports an allowed reference-equivalent limitation. MATLAB currently succeeds, so the latter is not presently supported.

### D08_fit — OPEN / BLOCKING

Latest frozen-gate mismatch remains limited to `fit.traj.epsi` at index `(178,1)`:
- HGFX: `-4.7887561410406825`;
- MATLAB: `-4.788757533201755`;
- absolute difference: about `1.392e-6`.

Reference-point replay PASS, initial Ridders PASS, optimizer trace PASS, and MATLAB-path objective replay PASS for 50 points.

TODO, in order:

- [ ] Export MATLAB/HGFX final free and full parameter vectors at full IEEE precision and compare ULP/absolute differences.
- [ ] Replay D08 trajectories at the exact MATLAB final vector and exact HGFX final vector.
- [ ] Decompose `epsi` around trials 177-179 into its underlying states/intermediates.
- [ ] Classify same-vector implementation mismatch vs endpoint numerical sensitivity.
- [ ] Add a failing regression fixture before any implementation repair.
- [ ] Rerun the unchanged official workflow gate.

### Official workflow closure exit gate

- [ ] Current required official workflow set reaches 9/9 PASS, or a case has exact paired evidence supporting an allowed reference-equivalent limitation. For D02/D08, MATLAB currently succeeds, so an HGFX-only divergence remains blocking.
- [ ] PR #26 evidence reviewed before merge.

## NEXT — complete MATLAB demo/output surface

### S3/S4/S5 remaining contract/demo work

- [ ] Finish source-to-workflow mapping for every remaining required demo/output surface.
- [ ] Close D09 prior-predictive sampling demo wrapper, preserving M11 semantics.
- [ ] Ensure D01/D03/D05 binary and D06-D08 continuous demo workflows have runnable Python examples plus frozen MATLAB evidence, not only core parity.

### S6 — analysis and plotting surfaces

- [ ] D10: Corr/Sigma inspection and equivalent plotting/example surface.
- [ ] D11: residual diagnostic workflow/output parity.
- [ ] D12: Bayesian parameter averaging workflow parity.
- [ ] Audit remaining required plotting/output surfaces for v1; require semantic/data/axis/label equivalence, not pixel identity.

## THEN — scientific/release closure

### S7 — paired recovery validation

- [ ] Run paired MATLAB/HGFX parameter recovery on the frozen product-validation protocol using identical data, seeds, model/observation family, priors, fixed/free parameters, starts and workflow.
- [ ] Run paired model recovery using the frozen candidate set and selection rule.
- [ ] Preserve the historical failed M18 experiment unchanged.
- [ ] Keep M18C.2 128/256/512/1024 horizon analysis as a separately frozen experiment.
- [ ] Classify every non-PASS case as implementation mismatch, optimizer mismatch, model-selection mismatch, reference limitation match, or insufficient reference evidence.

### S8 — repair only demonstrated HGFX-only mismatches

- [ ] For each required-scope mismatch, add a failing fixture first.
- [ ] Repair the smallest demonstrated equation/index/transform/numerical/model-selection defect.
- [ ] Rerun affected paired cases without changing scientific protocol.
- [ ] Exit with no unresolved implementation/optimizer/model-selection mismatch in required v1 scope.

### S9 — robustness/backend closure

- [ ] Freeze and run required trial-horizon/regime/missing/ignored-trial/initialization sweeps.
- [ ] Compare compatibility CPU, JAX CPU and physical GPU on the supported M18 paths.
- [ ] Reuse prior H100 evidence only where unchanged code/data-path applicability is explicitly documented; otherwise rerun physical GPU validation.
- [ ] Record device, driver, CUDA/JAX, command, SHA and limitations for new GPU evidence.

### S10 — release acceptance

- [ ] Implement aggregate evidence checker/report; it must reject missing, duplicate, substituted, partial or inconsistent evidence.
- [ ] Produce a durable evidence index with exact SHA/protocol/data/config/run/job/artifact/hash provenance.
- [ ] Run the complete applicable regression/demo suite.
- [ ] Verify clean install and independent examples.
- [ ] Verify documentation/API outputs/licenses.
- [ ] Verify MATLAB runtime dependency is zero for HGFX users.
- [ ] Close every mandatory criterion in `V1_RELEASE_GATE.md` / issue #24 with evidence.

## FINAL

- [ ] **M19 — Methods Paper Dataset Frozen:** freeze the accepted evidence package without rewriting historical failures; use `../research/PAPER_EVIDENCE_MAP.md` as the paper-facing index and generate final tables/figures from frozen machine-readable data.
- [ ] **M20 — v1.0 Candidate:** only after all v1 Definition-of-Done/release checks pass.

## Status vocabulary

Use only evidence-backed status terms: **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**. Never infer completion from implementation alone.
