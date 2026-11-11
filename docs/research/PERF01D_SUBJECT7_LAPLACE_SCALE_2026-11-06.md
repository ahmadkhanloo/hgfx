# PERF-01D — post-hoc local Hessian and fitted Laplace-scale audit, subject 7 (2026-11-06)

**AUTHOR-SIDE DESCRIPTIVE EVIDENCE: REPRODUCED. ORIGINAL PUBLIC FIT SCIENCE: 63/64 NONPASS. Independent science review: NOT RECEIVED. PERF-01C: NOT FROZEN. MATLAB-vs-HGFX timing: NOT RUN.**

## Why this is a distinct post-hoc follow-up

Earlier real [matched-runner full fitting](PERF01D_SUBJECT7_MATCHED_RUNNER_RESULTS_2026-11-06.md) produced **four frozen HGFX fits** (two SkylakeX, two Haswell) and **two MATLAB R2026a HGF Toolbox 8.2.0 public fits** on the same GitHub Actions VM for original 128-trial subject index **7**. All **eight** old-tolerance 28-field MATLAB/HGFX pairs remain **SCIENTIFICALLY NONPASS** in `traj.mu/muhat`, with Haswell additionally failing `traj.epsi/psi`. Two MATLAB reruns and repeated HGFX reruns were internally bitwise reproducible.

This *post-hoc*, **not preregistered**, analysis asks whether the observed small differences in three free optimizer coordinates are numerically large or small **relative to the fitted local Laplace covariance scale** (the `optim.H`, `optim.Sigma` matrices returned by the **original public fits**). This is a *descriptive scale calculation only*: the original per-cell error tolerance remains binding. The derived data neither establish an accepted source reference limitation, nor test scientific model identifiability, nor authorize choosing the best BLAS mode. No new fitting, seeds, starts, model, data, hypothesis-confirming dataset, benchmark sampling or timing occurs.

## Exact executed machine evidence

- Source six **real unmodified** public fits (Actions [42268256755](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268256755), source commit `331bb639dd65f3a3e2620b34f736a9b5156b8725`, [raw artifact 13528955307](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268256755/artifacts/13528955307), archive SHA-256 `ea9b37bd18b2fc25265268a0adf1002a504ddae278f627946f2976e5b4cc242c`). MATLAB original JSON SHA-256 **`2133b60ca7dcd51b85d93dfad109f715bd8fe35fa71c2bd84ff4a63cac672139`**; HGFX two mode-specific raw hashes unchanged from original ABBA ([source details](PERF01D_SUBJECT7_MATCHED_RUNNER_RESULTS_2026-11-06.md)).
- Original eight **unchanged 28-field** scientific comparisons: [derived-only Actions 42268990557](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268990557), [artifact 13527858098](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268990557/artifacts/13527858098), full previous comparison JSON SHA-256 **`3c90a24b94921b90e80f1967dfaaaaff821b809d893b5939b5a314ed8635b327`**.
- New [GitHub Actions **42282108311**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282108311), source **`fa6dcc0e77b244f483482b7ef8e01429d6884c4c`**, **SUCCESS**, **24/24 focused tests** (10 new spectral/negative tests, 14 previously executed same-runner tests), plus **3 explicit end-to-end tamper controls**: reject one original HGFX raw-byte edit, reject 64/64 fake scientific pass, reject omission of one of eight failed comparisons.
- [Complete newly derived eight-pair machine data artifact **13536250592**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282108311/artifacts/13536250592), ZIP SHA-256 `e2257c4c1b637cb7bcddcfdbb73fde18bd94d69a3f8e21986b9e6c3734210a2c`, contained report SHA-256 **`4ead097fe2958229176cdb3c610a02dd1b8746ca3b338e3c87bac3624b45c889`**. Original 63/64 scientific failure and 8/8 original 28-field mismatch pairs were required and reproduced before this new scale calculation.
- Code: `benchmarks/runtime_v1/derive_subject7_laplace_scales.py`; tests `tests/test_perf01_subject7_laplace_scales.py`; workflow `.github/workflows/perf01-subject7-laplace-scales.yml`.

## Calculation (no tolerance redefinition)

For each of the **eight** HGFX–MATLAB comparisons with same frozen input and full original public workflow, use original free-coordinate indices `[12,13,14]`, already exported by both fitters. With the *exported* MATLAB reference local numerical Hessian `H` and its Laplace covariance `Sigma`:

- `delta = x_HGFX_free - x_MATLAB_free`.
- `||delta||_2`: dimensioned Euclidean separation of the original three transformed free optimizer coordinates.
- `sqrt(delta.T @ H_matlab @ delta)`: **conditional local Hessian quadratic distance**, if both fitted `H` and `Sigma` are positive definite; record NULL otherwise.
- `delta_j / sqrt(Sigma_matlab[j,j])`: componentwise separation **in the scale of the same fitted Laplace covariance**, *not* a frequentist z-score.
- Eigenvalues and 2-norm condition number of the symmetrized exported 3×3 fitted `H`; matrix symmetry and `H @ Sigma - I` residuals recorded. This is **not an algorithm convergence proof**, independent uncertainty calibration or scientific gate.

The new code does **not** use these distances as acceptance conditions. It verifies the exact raw SHA-256, original eight **28-field** decisions, unchanged trajectory `atol=3e-10, rtol=3e-8`, the original 63/64 NONPASS, and all four HGFX/two MATLAB original subject-7 public fit identities. It retains every pair rather than selecting one MATLAB/BLAS mode.

## Results from original same-runner public outputs

| Numerical property | Frozen MATLAB_1/2 | HGFX SkylakeX_1/2 | HGFX Haswell_1/2 |
|---|---:|---:|---:|
| Exported local 3×3 fitted H eigenvalues (ascending, approx) | 0.06250117, 0.38300814, 6.55045608 | 0.06250117, 0.38300814, 6.55045605 | 0.06250117, 0.38300813, 6.55045600 |
| Local H condition number (2-norm, approx) | **104.805336** | **104.805335** | **104.805334** |
| Two repeated full outputs within source/BLAS mode | bitwise identical | bitwise identical | bitwise identical |
| Norm of 3-dimensional free endpoint delta vs fresh MATLAB | — | **3.78639×10⁻⁸** | **8.36361×10⁻⁸** |
| Conditional local H quadratic distance vs fresh MATLAB | — | **1.60196×10⁻⁸** | **3.53197×10⁻⁸** |
| Original MATLAB/HGFX unmatched fields per full 28-field pair | — | `traj.mu, traj.muhat` (4 + 4 cells) | `traj.epsi, traj.mu, traj.muhat, traj.psi` (5 + 14 + 14 + 40 cells) |

All six exported `H` and `Sigma` matrices are locally positive definite; MATLAB fitted `Sigma` has original coordinatewise scale `sqrt(diag(Sigma)) ≈ [1.60536, 3.99996, 0.43172]`. The largest absolute normalized free-coordinate component delta vs MATLAB is `1.18071×10⁻⁸` for SkylakeX and `2.60080×10⁻⁸` for Haswell. Every original eight-pair comparison continues to have at least two originally failing **trialwise** fields.

**Interpretation:** These particular frozen numerical endpoints are very close on their *fitted local Laplace covariance scale* despite failing the unaltered strict trialwise floating-tolerance criteria. The **local exported Hessian condition ≈105 and strictly positive eigenvalues do not establish a singular local Hessian**. None of this proves global model identifiability, a scientifically negligible difference, optimizer correctness, equal Hessian source computation under all conditions, external reference parity or statistical significance. A numerical diagnostic cannot override the preregistered strict output gate after observing a fail.

## Unresolved external decisions

The unchanged original 64 public full fits are **63/64 SCIENTIFIC NONPASS**, subject zero-based 7. The original 28 predeclared benchmark cells remain **16 REVIEW PENDING / 12 BLOCKED**, with six of nine original CPU primary cells ineligible. Independent reviewer signature/verdict in [issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88) is **NOT RECEIVED**, source scientific mismatch [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) OPEN, numerical repeatability [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) OPEN. PERF-01C **NOT FROZEN**, PERF-01E–H **NOT RUN**, no MATLAB-vs-HGFX speedup claim.

A reviewer must separately decide whether the complete original-source numerical discrepancy is an implementation mismatch, optimizer numerical mismatch, reference limitation with **actual independent reference evidence**, or another scientific limitation. The new post-hoc Hessian-scale numbers are provided **as evidence to examine**, not as an approved decision or a relaxation of old criteria.
