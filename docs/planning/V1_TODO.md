# HGFX v1.0 Live TODO

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Latest unchanged official-gate implementation head: `648c3f84905eb7fe952c070e5ee858e48de4a3fa`
Current planning/diagnostic head at this synchronization: `054f5ce62ec933563a59398e18de8e9782294840` plus subsequent live commits as applicable.

## Authority

Use this live checklist together with:

- `M18_COMPLETION_PLAN.md` — ordered S1-S10 dependencies;
- `V1_RELEASE_GATE.md` — v1 release acceptance;
- `../validation/MATLAB_EQUIVALENCE_POLICY.md` — frozen exact/numerical/endpoint-sensitivity/inferential equivalence rules;
- `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` — exact paired MATLAB limitations;
- `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md` — current case evidence.

For paper-facing continuity also use `../research/PAPER_EVIDENCE_MAP.md` and `../research/RESEARCH_LOG.md`.

## Non-negotiable product rule

HGFX v1.0 must reproduce MATLAB HGF Toolbox behavior, including model-family choices and demonstrated limitations. Bitwise equality is not required where a prospectively frozen scientific/numerical equivalence protocol establishes equivalence, but no threshold, seed, dataset, start, validation grid, model family or optimizer setting may be changed after seeing results merely to obtain PASS.

Historical failed experiments remain historical failures. A later accepted-equivalence classification is additional evidence, not a rewrite of an older gate.

## Current validated state

- M0-M17: completed according to their recorded gates/evidence.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY** — classic HGF fails correspondingly in MATLAB/HGFX and eHGF succeeds in both.
- D04 uHGF -> AR(1) workflow: **PASS** on run `34763542557` at `faf97bf...`.
- Historical exact 512-trial case: **REFERENCE_LIMITATION_MATCH**; not a general 512-trial scientific PASS.
- Latest unchanged official fit/Bayes closure: run `34823572071`, job `103910417693`, **7/9 direct PASS**.
- Official artifact `m18-official-workflows`, ID `10339454535`, ZIP SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.
- Remaining historical direct-gate failures: `D02_fit`, `D08_fit`.
- Historical M18 scientific FAIL remains preserved; M18 product/v1 closure remains **OPEN**.
- PR #26 remains the integration path to `main`; do not merge on implementation alone.

## NOW — D08 prospective endpoint-sensitivity decision

### D08_fit — IMPLEMENTED BUT NOT VALIDATED

Focused endpoint diagnostic run `34823572192` established endpoint sensitivity without changing the frozen gate:

- historical official mismatch: `fit.traj.epsi` at zero-based `(175,1)`, HGFX `138.87836008346915`, MATLAB `138.8783558587791`, absolute difference `4.224690043130642e-6`;
- largest fitted endpoint difference: `2.5768804867709605e-9` at transformed parameter index 8;
- HGFX at the exact MATLAB endpoint reproduces focused MATLAB `epsi` exactly;
- HGFX at the exact MATLAB endpoint reproduces MATLAB `negLj` exactly to the exported binary64 value;
- optimizer trace and MATLAB-path objective evidence pass the frozen tolerance.

Completed:

- [x] Freeze `matlab-equivalence-policy-1` before prospective validation.
- [x] Preserve the original D08 official failure and focused endpoint evidence.
- [x] Record diagnostic-only D08 decision in `reference/validation/m18_d08_endpoint/decision.json`.
- [x] Freeze two prospective holdout seeds before execution: `271828182`, `314159265`.
- [x] Implement MATLAB holdout exporter, HGFX checker and Actions workflow.

TODO:

- [ ] Execute both frozen holdouts unchanged. Latest observed run: `M18 D08 Equivalence Holdout` `34826235671`, queued at last check.
- [ ] If either holdout fails scientifically, preserve the failure; do **not** replace the seed/grid/tolerance.
- [ ] If both pass the frozen Level-2 rule, record `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` with run/job/artifact/hash provenance.
- [ ] Keep the historical direct D08 failure visible even if the prospective equivalence path passes.

D08 must not be called PASS before the two frozen holdouts complete successfully.

## NOW — D02 inference blocker and classifier

### D02_fit — BLOCKED

Current inference-level evidence is materially different despite same-reference objective parity at important sampled points:

- exact MATLAB endpoint replay in HGFX: PASS;
- initial Ridders gradient: PASS under the existing gate;
- MATLAB optimizer-path objective replay: PASS over 22 points;
- exact quasi-Newton step/BFGS replay from MATLAB state: machine-level agreement;
- optimizer path nevertheless diverges;
- final endpoint, Hessian, covariance, correlation, LME, predictions and residuals differ materially.

`reference/validation/m18_d02_inference/decision.json` therefore records **INFERENCE_EQUIVALENCE_FAIL / BLOCKING**. D02 is not eligible for a D08-style trajectory-only endpoint exception.

Completed:

- [x] Preserve original direct-gate and numerical-diagnostic failures/evidence.
- [x] Freeze a classification-only cross-endpoint protocol in `../validation/M18_D02_BASIN_DIAGNOSTIC.md`.
- [x] Freeze the exact 9-point line grid `alpha=[0,0.125,...,1]` before execution.
- [x] Keep unchanged M18 default objective tolerance `rtol=3e-8`, `atol=3e-10`.
- [x] Implement MATLAB reference exporter, HGFX grid preparation, MATLAB same-vector evaluator, checker and Actions workflow.

TODO:

- [ ] Execute `M18 D02 Basin Diagnostic` unchanged and archive all outputs.
- [ ] If any shared line point fails: classify `SAME_VECTOR_IMPLEMENTATION_MISMATCH` and localize that exact point before optimizer work.
- [ ] If all shared line points pass: classify `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE` and investigate conditioning/gradient amplification/path sensitivity.
- [ ] In either case keep D02 **BLOCKED** until the direct gate passes or a separately preregistered Level-3 inferential-equivalence protocol genuinely passes required fit/parameter/uncertainty/prediction/model-evidence quantities.
- [ ] Never accept D02 based only on a small objective difference while Hessian/covariance/correlation/evidence outputs disagree materially.

## Official workflow closure exit gate

- [ ] D01/D03/D05/D06/D07 remain healthy on the affected implementation path.
- [ ] D02 has a release-acceptable outcome under the frozen policy.
- [ ] D08 has either direct PASS or prospectively validated Level-2 endpoint-sensitivity equivalence.
- [ ] Any accepted non-direct result has immutable run/job/artifact/hash evidence and does not rewrite the historical 7/9 direct-gate artifact.
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

- [ ] Run paired MATLAB/HGFX parameter recovery on a frozen product-validation protocol using identical data, seeds, model/observation family, priors, fixed/free parameters, starts and workflow.
- [ ] Run paired model recovery using a frozen candidate set and selection rule.
- [ ] Preserve the historical failed M18 experiment unchanged.
- [ ] Keep M18C.2 128/256/512/1024 horizon analysis as a separately frozen experiment.
- [ ] Apply the tiered equivalence/reference-limitation policies without post-hoc threshold/grid changes.

### S8 — repair only demonstrated HGFX-only mismatches

- [ ] For each required-scope mismatch, add a failing fixture first.
- [ ] Repair the smallest demonstrated equation/index/transform/numerical/model-selection defect.
- [ ] Rerun affected paired cases without changing scientific protocol.
- [ ] Exit with no unresolved implementation/optimizer/model-selection mismatch in required v1 scope.

### S9 — robustness/backend closure

- [ ] Freeze and run required trial-horizon/regime/missing/ignored-trial/initialization sweeps.
- [ ] Compare compatibility CPU, JAX CPU and physical GPU on supported M18 paths.
- [ ] Reuse prior H100 evidence only where unchanged code/data-path applicability is explicitly documented; otherwise rerun physical GPU validation.
- [ ] Record device, driver, CUDA/JAX, command, SHA and limitations for new GPU evidence.

### S10 — release acceptance

- [ ] Implement aggregate evidence checker/report; reject missing, duplicate, substituted, partial or inconsistent evidence.
- [ ] Produce durable evidence index with exact SHA/protocol/data/config/run/job/artifact/hash provenance.
- [ ] Run complete applicable regression/demo suite.
- [ ] Verify clean install and independent examples.
- [ ] Verify documentation/API outputs/licenses.
- [ ] Verify MATLAB runtime dependency is zero for HGFX users.
- [ ] Close every mandatory criterion in `V1_RELEASE_GATE.md` / issue #24 with evidence.

## FINAL

- [ ] **M19 — Methods Paper Dataset Frozen:** freeze accepted evidence without rewriting historical failures; generate paper tables/figures from frozen machine-readable data.
- [ ] **M20 — v1.0 Candidate:** only after all v1 Definition-of-Done/release checks pass.

## Status vocabulary

Use only evidence-backed status terms: **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**. Never infer completion from implementation alone.