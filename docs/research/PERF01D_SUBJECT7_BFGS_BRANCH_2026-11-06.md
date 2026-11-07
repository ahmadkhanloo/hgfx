# PERF-01D: frozen subject-7 BFGS inverse-Hessian, curvature and line-search forensics — 2026-11-06

**Engineering evidence: REPRODUCED. Scientific decision: NOT PASSED / AUTHOR-SIDE DIAGNOSTIC ONLY / NO RUNTIME BENCHMARK.**

Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [independent scientific review #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [subject-7 fitting mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89), [overall PERF-01 #86](https://github.com/ahmadkhanloo/hgfx/issues/86). This report extends, without rewriting, [original subject-7 optimizer trajectory evidence](PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md) and [same-parameter objective/gradient evidence](PERF01D_SUBJECT7_GRADIENT_2026-11-06.md).

## A. Exactly preserved scientific source and inputs

- Product: `hgfx==1.0.0`, source SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Reference: MATLAB HGF Toolbox 8.2.0 source SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2026a.
- Identical canonical original `binary_128_s64` inputs, trial count **128**, subject **index 7 (zero based)**, model `hgf_binary`, observation `unitsq_sgm`, original prior/start/config, free parameters `[12,13,14]` zero based, `nRandInit=0`, `maxIter=100`, `maxStep=1`, `maxRegu=16`, `Ridders min_steps=10`.
- The original public 64-subject fitting [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) was downloaded and both original HGFX/MATLAB raw SHA-256 checks reverified **before** either new execution; the original one-failure outcome **63/64** was explicitly asserted. No original raw/summary file was modified.
- Original frozen `core/quasinewton_optim.m` and frozen `src/hgfx/optim/compat_quasinewton.py` were not patched. The **unmodified public** `fitModel` and `fit_model` returned original optimizer histories `iter.x`, `iter.val`, `iter.invH`, `iter.rst`. After full fitting, independently composed, source-matched objective and original Ridders calculation were evaluated at the **recorded own-engine vectors** for diagnosis. That composed MATLAB objective is not the private nested `fitModel.m` function and remains subject to independent review.

## B. Original real MATLAB/HGFX execution and audit artifact

- [PERF-01D BFGS run **42187240378**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378): **SUCCESS** at exact input code SHA `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d` (GitHub-hosted ubuntu-24.04, Python 3.11, NumPy 2.3.5, CPU-only, MATLAB R2026a); **10/10 author-side structural tests**.
- Archived [raw artifact **13488700272**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378/artifacts/13488700272), includes `hgfx_raw.json`, `matlab_raw.json`, original-comparison `comparison.json`, `summary.json`.
- Exact SHA-256 for the two raw files:
  - HGFX: `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`
  - MATLAB: `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.
- A new **distinct, immutable-derived** report [`benchmarks/runtime_v1/subject7_bfgs_results/derived-42187240378.json`](../../benchmarks/runtime_v1/subject7_bfgs_results/derived-42187240378.json) was committed at `59e9cd3caa769ad0ebbae654af04310ac03968dd`. It reverified both exact raw hashes, recomputed the whole original BFGS comparison and ensured none of its previous fields were rewritten.
- [Derived CI **42188247052**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052): **SUCCESS**, 10 original + 8 new synthetic negative/positive checks (**18/18 total**); **no new HGFX or MATLAB optimizer run, no timer**, no reference-limitation gate promotion.

## C. Recorded BFGS matrix and full-step results

| Observation | HGFX | MATLAB |
|---|---:|---:|
| Preallocated `iter.x` and `iter.val` buffer slots | 101 | 101 |
| Consecutive finite history slots | 25 | 25 |
| Recorded 3×3 inverse-Hessian matrices | 24 | 24 |
| Recorded reset indices | none | none |
| Reconstructed source curvature decisions, unambiguous slots 1–22 | 21 apply, 1 skip | 21 apply, 1 skip |
| Sole source curvature skip | record 11 | record 11 |
| Unambiguous reconstructed line-search transitions 0–21 | 22 full-step candidates, Armijo true | 22 full-step candidates, Armijo true |
| Frobenius norm of `T` at record 9 | `1.5349192293879397` | `1.5349192104409404` |
| Frobenius norm of `T` at record 10 | `281.76903538838` | `281.7688831325778` |
| Record-10/9 Frobenius amplification | **`183.5725489612489`×** | **`183.57245203259478`×** |

- Across the **22 source curvature-condition comparisons** (slots 1–22), the two engines had **zero branch-decision disagreements**. For both, the recomputed condition `dgrad·dx > sqrt(eps*(dgrad·dgrad)*(dx·dx))` agreed with whether the saved `T` matrix changed. Both skipped the update only at slot 11 (negative curvature). This is **source-derived**, not separately instrumented inside the unmodified MATLAB optimizer.
- For the **22 nonterminal transitions** (0→1 through 21→22), the saved next-point vector was reconstructed in both engines by **a candidate full step** `alpha=1` using `-T @ grad` (with the source `maxStep=1` clipping). The maximum componentwise reconstruction residual across the two engines was **`2.6645352591003757e-15`**. Both independently recorded objective values satisfied the source Armijo-style condition for the reconstructed full steps; **22/22 per engine**. Again, this reconstructs a mathematically compatible candidate, **not an instrumented public oracle acceptance event**.
- The last **two stored transitions 22→23 and 23→24 were excluded from BFGS/Armijo acceptance interpretation** because frozen MATLAB source overwrites the terminal history entry and both engines contain a duplicated terminal row. No exact MATLAB optimizer termination reason is exposed.
- The **first nonzero** MATLAB/HGFX inverse-Hessian component difference appears at zero-based record **1**, max `1.7252936275816144e-14`.
- The **largest** absolute inverse-Hessian component difference occurs at record **10**, `0.00015053299961209632`. At that record both BFGS matrix norms rise about 184×; the two matrices have very similar large scale, so the absolute component delta alone is not an implementation-parity verdict.
- Earlier paired objective and Ridders-gradient work found cross-engine **same-parameter** differences at selected history vectors as small as `1.4210854715202004e-14` for objective and `1.6621634624236492e-11` for gradient, while original fitted paths gradually separated. The new data show that a **curvature-branch mismatch or line-search half-step selection mismatch is not demonstrated on the nonterminal slots**; accumulated BFGS/direction floating differences remain a plausible explanation, not a confirmed unique root cause.

## D. Original and new failed runs explicitly preserved

- [Original BFGS attempt **42187123464**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187123464) **FAILURE**: the synthetic negative-control fixture reused the same list object for saved x and gradient-point x, so the intended tamper went undetected. Fixed synthetic aliasing at commit `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d`; source scientific code and data were untouched.
- [First derived-branch CI **42188145793**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188145793) **FAILURE**: the synthetic “negative curvature” fixture used `grad_new=+1` against `grad_old=-1`, inadvertently generating **positive**, not negative, curvature. Fixed synthetic test sign at `83533eee2504ddbacb1b3ccbd3be25f5b23d560b`; successful derived CI 42188247052 preserved and hash-checked the unaltered original BFGS evidence.
- These are **engineering test-fixture failures**, not numerical/scientific failures; neither run was erased or reinterpreted as a scientific PASS.

## E. Scientific limits and next review decision

**Observed:** both engines use the same initial parameters, the same saved BFGS branch decisions, the same reconstructed full-step fractions over 22 unambiguous transitions and the same absence of recorded resets. The large record-10 amplification of each inverse-Hessian matrix is **a plausible amplifier of otherwise small floating/numerical differences**.

**Not established:** an exact line-search acceptance event log; full optimizer internal operations/termination equivalence; an isolated underlying cause of the remaining fitted endpoint mismatch; prospective physical CPU/GPU benchmark eligibility; or independent classification as a permissible MATLAB reference limitation. The numerical difference at every supplied original subject still must be reported and the complete scientific acceptance gate is still unpassed.

Original scientific gate remains **63/64** (subject 7 `traj.mu` and `traj.muhat` mismatch); original 28-case workload **16 review pending / 12 blocked**, including **six scientifically ineligible cells among the original nine primary CPU workloads**. PERF-01C **OPEN / NOT FROZEN**; PERF-01E–H **NOT RUN**. No MATLAB/HGFX runtime speedup, GPU validation or paper-ready timing claim exists.

The independent reviewer must assess the source-equivalent objective composition, interpretation of terminal history/gradient/BFGS behavior, reference-limitation policy and full prospective timing/host protocol. **Machine-level reproduction is not independent scientific sign-off.**
