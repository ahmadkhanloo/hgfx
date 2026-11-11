# PERF-01A — source/runtime audit (2026-11-04)

> **Subsequent evidence update, 2026-11-04:** The audit below is the original pre-CI snapshot, kept for provenance. MATLAB **R2026a** is now confirmed runnable on a public GitHub Actions host and exact HGF Toolbox 8.2.0 checkout succeeded. Candidate arrays and full nine HGFX config/start snapshots were committed. The fixed-vector paired diagnostic now finds **14 corresponding completed stage records, 5 matching unsuccessful stage records, and 9 fit/batch cells not run**. See [the current paired preflight and gate status](PERF01_PAIRED_PREFLIGHT_2026-11-04.md). This is NOT a scientific-parity or timing PASS; the earlier local-sandbox blocker remains a true historical observation but not a universal MATLAB-access blocker.

**Status: IN PROGRESS / BLOCKED_ENVIRONMENT.** This report covers repo inspection and the available authoring sandbox; it is **not** evidence that MATLAB, HGFX 1.0.0 or NVIDIA GPU has been run on the eventual benchmark host.

## Source and status checked

- Repository: `ahmadkhanloo/hgfx`; inspected `main` at `44353387ab2578339174f0d8252aecb737654ae7` before making a scoped research branch.
- Product for paper: `v1.0.0` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Source checked by reading `src/hgfx/compat/{configs,fit,fitting}.py` and `src/hgfx/optim/compat_quasinewton.py` **at v1.0.0**, not at `main`.
- Frozen MATLAB oracle: HGF Toolbox `8.2.0` commit `2437f4dc241541072722a2695ddeca7b44d83dd3`, matching `reference/HGF_VERSION` and `reference/HGF_COMMIT` at v1.0.0.
- `main`'s `pyproject.toml` reports `1.1.0b1`. It is **not** the immutable paper implementation. A runner importing the live checkout must abort rather than silently benchmark the beta.
- The v1 source provides `fit_model` / `fitModel`, the validated compatibility fitting path, binary HGF config, `unitsq_sgm_config`, and `QuasiNewtonOptions`; its default optimization settings include `max_iter=100`, `tol_grad=1e-3`, and `tol_arg=1e-3`. Verify exact MATLAB defaults and complete end-to-end results on the execution host before timing.
- The fast JAX fitting path uses a distinct BFGS implementation; cross-algorithm fits must be separately labeled. Its batch API cannot be assumed to include the same post-fit statistics/time boundary as MATLAB's full `fitModel`.

## Available authoring sandbox check (NOT candidate benchmark hardware)

| Item | Observed |
|---|---|
| Python | 3.13.5 |
| NumPy | 2.3.5 |
| JAX | 0.9.0.1 |
| MATLAB executable | Not available |
| NVIDIA GPU / `nvidia-smi` | Not available |
| installed `hgfx` package | Not available |
| Repository clone access by `git ls-remote` | Unable to resolve `github.com` from sandbox; GitHub connector can read/write files |

**Crucial:** This check says nothing about the user's lab/H100 or MATLAB license. Historical H100 evidence from M17 is on another recorded machine and commit; it cannot substitute for matched MATLAB/HGFX timing.

## Findings that must close before timing

1. **Environment identity:** provision a common CPU host with MATLAB and isolated HGFX 1.0.0. Capture actual CPU model, operating system, MATLAB release, toolbox SHA, HGFX wheel/source hash, CPU/thread affinity, numerical libraries, Python/JAX/JAXLIB versions and process isolation. For GPU record actual physical device, driver, CUDA, x64 support, utilization and residency.
2. **Timed API contract:** implement MATLAB and HGFX wrappers with matched initial data, parameter vectors, `NaN` masks, results and statistics. Check that `fitModel` and `fit_model` really include comparable Hessian/LME/selection and result materialization; otherwise reclassify as a separately labeled optimizer-only experiment **before** protocol freeze.
3. **Algorithm family:** CPU compatibility vs MATLAB is primary; JAX-fast optimizer is *different* and cannot be represented as a matched-optimizer speedup. The fast-mode 1/2-GPU throughput comparison must include attempts, failures and objective/trajectory concordance.
4. **Scientific gate:** existing release coverage does not establish parity for the new synthetic samples, especially eHGF/uHGF and masked data. Commit mapping and tolerances before performance tests, then validate each cell.
5. **Data/version pin:** export and commit the same immutable canonical data, priors and starts to both implementations; do not use mutable main defaults or cross-language RNG assumptions.
6. **Protocol lock:** before starting final time runs, complete an independent review and store the protocol-lock hash. The current `hgfx-matlab-runtime-1` remains `NOT FROZEN`; the historical paper protocol explicitly excludes headline speed claims.

## PERF-01B local preparation outcome

- A deterministic Python/NumPy fixture producer was added in `benchmarks/runtime_v1/generate_inputs.py`.
- **2/2** producer unit tests passed locally: the full 28-case registry (9 primary + 12 secondary + 6 throughput + 1 robustness), exact-size binary inputs, byte-repeatability and tamper rejection.
- Generation + `--check` passed locally; candidate SHA-256s appear in the adjacent `README.md`.
- Inputs were generated in a disposable authoring workspace; **they have not been committed to the repository or exported/checked against HGFX+MATLAB**. Per-model configurations, prior/free indices, start vectors, and tolerance locks are still pending.
- This is **IMPLEMENTED BUT NOT SCIENTIFICALLY VALIDATED**, not `PASS_PERF01B`.

## Decision

- `PERF-01A = BLOCKED_ENVIRONMENT / PARTIAL_AUDIT`
- `PERF-01B = IN_PROGRESS / GENERATOR_TESTED / INPUTS_NOT_FROZEN`
- `PERF-01C..H = OPEN`
- `MATLAB_VS_HGFX_SPEEDUP = NOT_RUN`

No frozen v1 release/paper evidence was changed. No MATLAB, HGFX numerical or physical-GPU experiment was executed.
