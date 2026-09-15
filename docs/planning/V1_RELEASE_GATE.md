# HGFX v1.0 Release Gate

Last synchronized: 2026-09-15
Status: **OPEN / IN PROGRESS — S9 PHYSICAL GPU PASS; M19/M20 FINALIZATION REMAINS**

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
- [ ] Aggregate evidence/provenance final freeze — preflight passes; final M19 now ready to execute
- [x] Zero MATLAB runtime dependency for users

## Current evidence snapshot

- M0-M17 completed in documented scopes.
- Historical M18 scientific result: **FAIL, preserved**.
- Official direct fit/Bayes gate remains **7/9 direct PASS**; D02_fit and D08_fit direct failures remain preserved.
- D02 exact official workflow: `REFERENCE_LIMITATION_MATCH` for release accounting only.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265`: `REFERENCE_LIMITATION_MATCH` for release accounting only.
- D09 sampleModel: PASS, run `34842943557`.
- D10/D11 analysis/output: PASS, run `34847266268`.
- D12 Bayesian parameter averaging: PASS, run `34854238549`.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`; model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8: required-scope repair DONE at `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no unresolved required HGFX-only S7 mismatch.
- S9 CPU robustness/backend: `PASS_CPU_BACKEND_EQUIVALENCE`, run `34901924475`, job `104169632034`, artifact `10371308067`, SHA-256 `875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826`.
- S9 physical GPU: **PASS_PHYSICAL_GPU_APPLICABILITY** on 2x Tesla T4, source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`. All four required CPU-vs-GPU fit cells pass; maximum objective gap `1.4210854715202004e-14` against the frozen `1e-7` threshold. Repository evidence commit `7179484ce782c25d6edde34cc56a0d689831e1cc`; raw JSON SHA-256 `6cd35c82be1e542830c06f6b7b7e444fda0ff4fe93773f080e6c13725212dfdf`.
- S10 release readiness: **PASS**. Latest release-preparation-head rerun: run `34934079865`, wheel artifact `10383235791`, SHA-256 `8abf4488e91c6ae28983c318670f4a92dfab57c4acc8caad494be02fca47eb2b`.
- M19 evidence-freeze preflight: **PASS_PREFLIGHT**, run `34934079973`, job `104268154143`; finalization is now unblocked by S9.
- M20 candidate preflight: **PASS_PREFLIGHT**, same run/job; finalization still depends on M19 freeze and version promotion.
- M19/M20 preflight artifact: `10383425031`, SHA-256 `3f711a260f68ff0454d18b2b09b3645d28ab5b370384c8729d4fd431bee5e7cf`.

## Physical-GPU acceptance

The hardware model itself is not a numerical gate. Per `M18_S9_PHYSICAL_GPU_AMENDMENT.md`, an eligible run may use T4, L4, A10/A10G, A100, H100, H200, or another physical NVIDIA CUDA-capable GPU supported by the installed JAX/CUDA runtime.

The unchanged frozen requirements are:

- same repaired S9 code/data path;
- actual GPU residency;
- JAX CPU-vs-physical-GPU final-objective gap `<= 1e-7`;
- exact GPU model, driver/CUDA/JAX/JAXLIB/Python, command, source commit, git status and environment limitations recorded;
- CPU/mock evidence cannot substitute for physical GPU evidence.

The accepted run satisfies these requirements. It used a hosted/shared Kaggle environment with 2x Tesla T4, JAX/JAXLIB `0.11.1`, Python `3.12.13`, and recorded physical process residency. This supports backend numerical applicability on the tested NVIDIA/JAX/CUDA path only; it does not create an H100-specific or cross-device performance claim.

The captured `git status --porcelain` entry `?? gpu_validation_results/` is expected from the validation wrapper, which creates its output directory before capturing provenance. The source HEAD recorded by the run is exactly `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: prospectively frozen Level-2 numerical protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited; acceptable for v1 MATLAB-equivalence but not a scientific PASS.
- `PASS_PHYSICAL_GPU_APPLICABILITY`: current numerical path executes resident on eligible physical NVIDIA hardware and satisfies the frozen CPU-vs-GPU criterion.
- `PASS_PREFLIGHT`: release machinery and non-blocked prerequisites pass; it is not final milestone PASS.

Historical/direct/prospective failures remain immutable evidence.

## S7/S8 closure

The complete frozen S7 paired grid contains 72 parameter-recovery cases and 36 model-recovery datasets. MATLAB and HGFX have identical criterion outcomes for HGF/eHGF/uHGF and nearly identical aggregate recovery metrics. Shared parameter-recovery failures remain `REFERENCE_LIMITATION_MATCH`; all 36 BIC winners match directly.

S8 historical negative-precision localization probes are retained for provenance/manual reproduction. They deliberately enter a parameter region where frozen MATLAB can itself raise `Negative posterior precision`; they are not ordinary PR/release gates after required-scope S8 closure and do not reopen S7/S8.

## Current release blocker sequence

1. **M19 final evidence freeze** — physical GPU prerequisite is now PASS; run final manifest generation and require `FROZEN`.
2. **M20 v1.0 candidate** — finalize only after M19 and release-version metadata promotion.

S9 and S10 are closed. No new scientific validation surface should be added during release closure unless a mandatory final gate demonstrates a genuine current-scope regression.

## M18/v1 exit conditions

- [x] All required model families/workflows accounted for under frozen release semantics
- [x] Fit/simulation/trajectory/statistical outputs evidence-backed or exact-scope reference-limitation accounted
- [x] Official required workflows reproduced/accounted across release surface
- [x] Every current non-direct-PASS fit/recovery case has a supported release classification
- [x] Every accepted limitation has exact MATLAB evidence
- [x] No unresolved required HGFX-only implementation/optimizer/model-selection mismatch from S7/S8
- [x] Paired parameter/model recovery complete
- [x] Robustness/backend/physical-GPU applicability matrix complete
- [x] D09-D12 required output surfaces closed
- [ ] Aggregate evidence final freeze complete — final M19 execution pending
- [x] Clean install/examples/docs/API/licenses verified
- [x] Zero MATLAB runtime dependency verified

The release remains **OPEN** only for M19 evidence freeze and dependent M20 candidate finalization.
