# REV-2.3 F/B prospective fixture decision — author/reviewer handoff

**Status: PROPOSED_ONLY / UNAPPROVED / NO INPUTS GENERATED / NO TIMING.** This document is a **new prospective choice proposal** for fields that the existing Computational Statistics plan left unspecified. It neither edits completed milestones nor retroactively amends the independent PERF-01 runtime protocol. The 11 original REV-2.3 workload sizes, four backend reporting surfaces, float64, one warm-up and five timed repetitions stay intact.

## Frozen reference facts, not author selections

- Actual frozen MATLAB HGF Toolbox 8.2.0 `core/fitModel.m` defaults to `ehgf_binary` whereas HGFX released v1.0.0 defaults to `hgf_binary`; explicitly select `hgf_binary_config` and `unitsq_sgm_config` for matched classic binary HGF fitting. Source evidence: [authentic MATLAB API audit](REV23_PINNED_MATLAB_API_AND_DEFAULTS_AUDIT_2026-11-11.md).
- A legitimate *actual* binary reference input `demo/example_binary_input.txt` exists at frozen MATLAB ref `2437f4dc241541072722a2695ddeca7b44d83dd3`, Git blob `d7eb0828b951d8d3a0f5ced8ef22d722917d9408`; direct repository file read counted **320 trials**, all 0/1. This source is insufficient to supply F1024/F8192/F65536 or B1024×256 without a **prospectively stated extension/re-use rule**. A Git blob SHA1 is not a SHA256 of canonical emitted input arrays.
- Published HGFX v1.0.0 exposes `fast_binary_hgf`, `fit_hgf_binary_unitsq_fast`, and `fit_hgf_binary_unitsq_batch`. Only the latter has a native 1D regular binary-HGF subject-array contract, with a JAX optimizer that is not MATLAB's compatibility quasi-Newton.
- D08 `uhgf + gaussian_obs` original USDCHF scientific failure and exhausted experiment cap are **unchanged**; this proposal never produces or replays a replacement D08 simulation.

## Explicit reviewer decision sheet — do not fill missing fields by assumption

| Group | Original fixed sizes | Concrete *proposed* model/observation | Data decision that MUST be prospectively made |
| --- | --- | --- | --- |
| Forward F | 128 / 1024 / 8192 / 65536 trials | **Candidate** `hgf_binary` classic, with no observation likelihood in pure forward timing; if a response model is needed for fixture compatibility, describe `unitsq_sgm` only as metadata | Either A: deterministic source-referenced binary synthetic generator whose algorithm, seed, NumPy version and all emitted file hashes are locked; or B: an explicitly approved expansion/re-sampling of the original 320-row MATLAB demo, with clear period/ordering policy. **Neither selected.** |
| Single subject S | 128 / 512 trials | **Original prescribed** `hgf_binary + unitsq_sgm`, full MATLAB and HGFX compatibility fit | Exact canonical `u`, `y`, ignored/irregular mask, transformed priors, fixed/free mask, one start and restart-count policy required. No replacement with fixed-vector objective or JAX fast BFGS. |
| Batch B | 1 / 32 / 256 / 1024 subjects, each 256 trials | **Candidate** `hgf_binary + unitsq_sgm` because it is the *released* native JAX batch-fit family; alternative families require a separately proven implementation | Is each subject independent or a repeated array? Specify generation/selection of all 1024 pairs and whether B subsets share identical subject prefixes (nested-design dependence). Freeze preselected response-generation model and seed if applicable; no algorithm-specific inputs or post-result exclusions. |
| D08 | Original 614 inputs, one fit | Unchanged `uhgf + gaussian_obs` | Original archived source/input and response hash only; existing `BLOCKED_SCIENTIFIC_PARITY`, no new science run without separate authority. |

**Recommended prospective design for review (NOT chosen):** use `hgf_binary` as the single scientific F/B family so all four backend candidates can be matched where the v1 release actually implements them; use a **single external deterministic binary64 fixture exporter**, verified arrays stored once in a canonical repo/artifact set then imported into MATLAB and Python; freeze a separately declared RNG seed/algorithm **before generating** those new performance-only arrays, independent of historical D08 seed `123456789`. Define response generation explicitly, and preserve both adverse and favorable scientific results. Do **not** borrow the older PERF-01 `PCG64(20261104)` seed as an implicit common experiment: the two proposals have different matrices and statistical policies.

## Exact choice must specify before generation

1. F/B family and observation metadata and whether F observation is intentionally `not_applicable`; update manifest schema to handle that distinction without silently replacing its original workload.
2. F/B data-construction algorithm, actual seed, source provenance and source identity, 128/1024/8192/65536 length policy, 1024-subject 256-trial subject-order policy and trial-by-trial ignored/irregular mask; **do not choose by examining outputs or runtimes**.
3. S128/S512 same-array/response origins, transformed/native fixed vectors and starts; MATLAB `fitModel` with *explicit* config. The source-only fixture integrity tool's dummy unit-test data are **never** eligible.
4. Canonical `.npy` binary64 files and JSON config with **actual** SHA256 over emitted bytes, exact source wheel/install SHA, MATLAB version/host/threading and full-output materialization.
5. Eligible scientific source/tolerance gate for each group, reviewer identity and signed approval, fail/blocked classification and the protocol SHA of the **prospectively frozen** revision; no PERF-01C bypass.

## Decision protocol

Current author D1=A is approval to continue the Computational Statistics **revision**, **not** approval for any specific missing source array/model/seed combination. Before generation, record an explicit F/B/S data decision in the repository as `APPROVED_PROSPECTIVE_CHOICE` with approver and commit, or retain `OPEN_AUTHOR_REVIEW`. The independent comparator/benchmark gate must separately authorize any eventual timed runs. The old PERF-01 benchmark remains distinct and blocked.

**Current outcome:** a specific candidate/model and data-decision menu has been prepared; 0 scientific arrays created, 0 source-backed canonical fixture SHA256 frozen, 44/44 cells not independently eligible; `REV-2.3=DRAFT_NOT_FROZEN`, `PERF-01C=BLOCK_FREEZE`, no MATLAB/JAX/GPU timed run.
