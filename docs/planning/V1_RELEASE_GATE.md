# HGFX v1.0 Release Gate

Last synchronized: 2026-09-15
Status: **OPEN — FRESH RC CI PASS; M20 FINALIZER PENDING ON SYNCHRONIZED REVISION**

## Product definition

HGFX v1.0 is a functional and scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0. Bitwise identity is not generally required, but every accepted equivalence/limitation must follow the frozen policies and preserve failed evidence. No post-hoc threshold, seed, dataset, start, grid, model-family or optimizer change may obtain PASS.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, and `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md` as acceptance policy.

## Mandatory acceptance criteria

- [x] Complete required MATLAB model/workflow coverage is accounted for under direct PASS / scoped reference-limitation policy
- [x] Fit workflow parity/equivalence/reference-limitation accounting under frozen policy
- [x] Simulation workflow parity/equivalence in documented required scopes
- [x] Trajectory output parity/equivalence in documented required scopes
- [x] Hessian/LME/statistical output parity/equivalence or exact-scope reference limitation in documented required scopes
- [x] Paired parameter recovery against same MATLAB oracle/workflow — exact frozen S7 grid is `REFERENCE_LIMITATION_MATCH`, not scientific PASS
- [x] Paired model recovery/model-selection validation — `PASS_PAIRED_MODEL_SELECTION`, 36/36 winners match
- [x] CPU/GPU numerical agreement on required supported paths — CPU and physical NVIDIA GPU applicability closed
- [x] Python reproduction/accounting of required MATLAB workflows accepted for release surface
- [x] Independent-use documentation/examples
- [x] Aggregate evidence/provenance freeze — M19 `FROZEN`, run `34966661492`
- [x] Zero MATLAB runtime dependency for users
- [x] Fresh candidate PR CI on `5cf17dcd13c9f30dbfcd500ad409d39d41296b20`: 10/10 active workflows PASS
- [ ] M20 finalizer returns `PASS_M20_CANDIDATE` on the synchronized release-document revision

## Current evidence snapshot

Historical evidence is preserved; fresh candidate runs are additive validation.

- M0-M17 completed in documented scopes.
- Historical M18 scientific result: **FAIL, preserved**.
- Official direct fit/Bayes gate remains **7/9 direct PASS**; D02_fit and D08_fit direct failures remain preserved.
- D02 exact official workflow: `REFERENCE_LIMITATION_MATCH` for release accounting only.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265`: `REFERENCE_LIMITATION_MATCH` for release accounting only.
- D09 sampleModel: historical PASS; fresh run `34984783710` PASS.
- D10/D11 analysis/output: historical PASS; fresh run `34984783669` PASS.
- D12 Bayesian parameter averaging: historical PASS; fresh run `34984783649` PASS.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS. Fresh run `34984783703` PASS for release accounting; aggregate artifact `10404477458`, SHA-256 `e62982fa32f61d66d3f8643d95354962944e969bc72868a3326cd816377203a2`.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, fresh 36/36 BIC winners match.
- S8: required-scope repair DONE at `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no unresolved required HGFX-only S7 mismatch.
- S9 CPU robustness/backend: `PASS_CPU_BACKEND_EQUIVALENCE`; fresh S9 run `34984783685` PASS.
- S9 physical GPU: **PASS_PHYSICAL_GPU_APPLICABILITY** on 2x Tesla T4, source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`. Maximum objective gap `1.4210854715202004e-14` against frozen `1e-7`.
- S10 release readiness: historical PASS; fresh run `34984783640` PASS, wheel artifact `10402688684`, SHA-256 `b65de6e4ba20a5637935f32010d8a150e7731b113a77ae9256c1f688697b118b`.
- M19/M20 preflight: fresh run `34984783642` PASS, artifact `10403445860`, SHA-256 `fdfd1e2a73df597a54b72d929191ca0d11e2eeb5ef8ed56bdb49327229d4b2eb`.
- Full CPU regression: fresh run `34984783677`, **171 passed, 4 physical-GPU skips, 5 warnings**.
- M19 evidence freeze: **PASS / FROZEN**, workflow run `34966661492`.
- Candidate metadata: `1.0.0rc1` in both `pyproject.toml` and `CITATION.cff`.
- M20: finalizer pending on the synchronized release-document/evidence revision.

## Physical-GPU acceptance

The hardware model itself is not a numerical gate. Per `M18_S9_PHYSICAL_GPU_AMENDMENT.md`, an eligible run may use a physical NVIDIA CUDA-capable GPU supported by the installed JAX/CUDA runtime.

The accepted run satisfies the unchanged frozen requirements: same repaired code/data path, actual GPU residency, CPU-vs-GPU final-objective gap `<= 1e-7`, recorded provenance, and no CPU/mock substitution. It establishes backend numerical applicability on the tested NVIDIA/JAX/CUDA path only, not H100-specific or cross-device performance.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: prospectively frozen Level-2 numerical protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited; acceptable for v1 MATLAB-equivalence but not a scientific PASS.
- `PASS_PHYSICAL_GPU_APPLICABILITY`: current numerical path executes resident on eligible physical NVIDIA hardware and satisfies the frozen CPU-vs-GPU criterion.
- `PASS_FROZEN`: M19 release evidence is committed in a machine-readable `FROZEN` manifest.
- `PASS_PREFLIGHT`: release machinery and non-blocked prerequisites pass; it is not final milestone PASS.
- `PASS_M20_CANDIDATE`: synchronized `1.0.0rc1` release-candidate accounting passes; it is not an independent final-review result.

Historical/direct/prospective failures remain immutable evidence.

## S7/S8 closure

The complete frozen S7 paired grid contains 72 parameter-recovery cases and 36 model-recovery datasets. Fresh run `34984783703` again shows MATLAB and HGFX have the same criterion outcomes across HGF/eHGF/uHGF and 36/36 model-selection winners.

The fresh raw S7 aggregate remains `gate_pass=false` and `scientific_pass=false`. The separately frozen exact-scope decision yields `REFERENCE_LIMITATION_MATCH` and `release_gate_pass=true`. Therefore no scientific failure is relabeled as scientific PASS.

S8 historical negative-precision localization probes remain historical/manual diagnostics and do not reopen completed S8 required-scope accounting.

## Current release blocker sequence

1. **M20 v1.0 RC finalization** — on the synchronized release-document revision, require `scripts/check_m20_candidate.py --mode finalize` / `m20-finalize.yml` to return `PASS_M20_CANDIDATE`.

S9, S10 and M19 are closed. No new scientific validation surface should be added during RC closure unless M20 exposes a genuine current-scope regression.

## Candidate versus final `1.0.0`

M20 is the `1.0.0rc1` candidate gate. After M20 PASS, PR #26 may be made ready/merged and the RC tag may be created.

Promotion from RC to final `1.0.0` remains governed by `CHAT_WORKFLOW.md`: freeze the candidate, obtain an independent frontier-agent review against `FINAL_REVIEW_CHECKLIST.md`, resolve all Critical/High findings, and rerun full validation. M20 PASS alone must not be reported as completion of that independent review.

## M18/v1 RC exit conditions

- [x] All required model families/workflows accounted for under frozen release semantics
- [x] Fit/simulation/trajectory/statistical outputs evidence-backed or exact-scope reference-limitation accounted
- [x] Official required workflows reproduced/accounted across release surface
- [x] Every current non-direct-PASS fit/recovery case has a supported release classification
- [x] Every accepted limitation has exact MATLAB evidence
- [x] No unresolved required HGFX-only implementation/optimizer/model-selection mismatch from S7/S8
- [x] Paired parameter/model recovery complete
- [x] Robustness/backend/physical-GPU applicability matrix complete
- [x] D09-D12 required output surfaces closed
- [x] Aggregate evidence freeze complete
- [x] Clean install/examples/docs/API/licenses verified
- [x] Zero MATLAB runtime dependency verified
- [x] Fresh candidate PR CI green
- [ ] M20 candidate final check complete on synchronized release docs

The RC remains **OPEN** only for the M20 candidate finalizer.
