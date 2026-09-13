# HGFX v1.0 Live TODO

Last synchronized: 2026-09-13
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Last tested implementation head: `faf97bfdbef1333a6a756749a8ab9d6a5be102b3`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

This is the live operational TODO for reaching HGFX v1.0 MATLAB-equivalence. Use it together with:

- `M18_COMPLETION_PLAN.md` for ordered S1-S10 dependencies;
- `V1_RELEASE_GATE.md` for release acceptance;
- `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` for reference-aware failure classification.

For current work ordering, this file and the 2026-09-13 section of `M18_COMPLETION_PLAN.md` supersede older 2026-09-12 notices that still mention D04 as the immediate next task in legacy planning documents. D04 is validated PASS and must not be repeated unless its implementation/data path changes.

## Non-negotiable product rule

HGFX v1.0 must reproduce MATLAB HGF Toolbox behavior, including its model-family choices and demonstrated limitations. A case where MATLAB itself fails or requires eHGF/uHGF/specialized models does **not** have to be made artificially successful in HGFX. Such a limitation is acceptable only when exact paired MATLAB evidence supports `REFERENCE_LIMITATION_MATCH`.

Do not improve beyond MATLAB at the cost of compatibility in v1 compatibility mode. Do not relax thresholds, change seeds/datasets, shrink validation grids, or switch model family after seeing results.

## Current validated state

- M0-M17: completed according to their recorded gates/evidence.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY** — classic HGF fails in both MATLAB/HGFX and eHGF succeeds in both.
- D04 uHGF -> AR(1) workflow: **PASS** on run `34763542557` at `faf97bf...`.
- Historical exact 512-trial case: **REFERENCE_LIMITATION_MATCH**; this is not a general 512-trial scientific PASS.
- Official fit/Bayes workflow closure run `34763542525`, job `103740409700`: **7/9 PASS**.
- Artifact `m18-official-workflows`, ID `10319853691`, ZIP SHA-256 `2cb5b01bce11b900261a0e309e80bf4220d63ac655417d86bf32539bf1cbf773`.
- Remaining official-workflow blockers: `D02_fit`, `D08_fit`.
- PR #26 remains draft/unmerged. M18 product closure remains **OPEN**.

## NOW — close D02 and D08

### D02_fit — IN PROGRESS / BLOCKING

Evidence already established:

- MATLAB reference-point replay: PASS.
- Initial Ridders gradient: PASS at existing acceptance tolerance.
- MATLAB-path objective replay: PASS at existing gate tolerance.
- Exact quasi-Newton state replay shows BFGS/step algebra reproduces MATLAB to machine precision when fed exact MATLAB state.
- Exact MATLAB Ridders `x+h/x-h` objective probes show raw cross-runtime objective differences around `4.5e-13` to `1.1e-12`; central finite-difference differences reach about `1.62e-12` and are amplified by later optimization.

TODO, in order:

- [ ] Export objective decomposition at the exact D02 finite-difference coordinates: per-trial log likelihood, total log likelihood, perceptual prior terms, observation prior terms, forward/inference states and observation intermediates required to locate the first primitive divergence.
- [ ] Compare MATLAB and HGFX decomposition and identify the earliest primitive numerical mismatch.
- [ ] If it is HGFX-only, add a failing regression fixture **before** changing implementation.
- [ ] Apply the smallest compatibility fix; do not change frozen optimizer settings, tolerances, seed, data, starts or model family.
- [ ] Rerun the unchanged official workflow gate and archive evidence.

### D08_fit — OPEN / BLOCKING

Current frozen-gate mismatch: `fit.traj.epsi` near trial index 178, absolute difference about `3e-6`; reference-point, initial Ridders, optimizer trace and MATLAB-path objective diagnostics otherwise pass.

TODO, in order:

- [ ] Export MATLAB/HGFX final free and full parameter vectors at full IEEE precision and compare ULP/absolute differences.
- [ ] Replay D08 trajectories at the exact MATLAB final vector and exact HGFX final vector.
- [ ] Decompose `epsi` around trials 177-179 into its underlying states/intermediates.
- [ ] Classify as implementation mismatch vs optimizer numerical sensitivity.
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

- [ ] **M19 — Methods Paper Dataset Frozen:** freeze the accepted evidence package without rewriting historical failures.
- [ ] **M20 — v1.0 Candidate:** only after all v1 Definition-of-Done/release checks pass.

## Status vocabulary

Use only evidence-backed status terms: **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**. Never infer completion from implementation alone.
