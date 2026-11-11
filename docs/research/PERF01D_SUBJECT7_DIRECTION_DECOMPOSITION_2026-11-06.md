# PERF-01D — frozen subject-7 BFGS direction decomposition and maxStep clipping (2026-11-06)

**Status: AUTHOR-SIDE DERIVED NUMERICAL DIAGNOSTIC. NOT A CAUSAL RESULT, NOT A SCIENTIFIC PASS, NOT TIMED.**

Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87); [review #88](https://github.com/ahmadkhanloo/hgfx/issues/88); [subject-7 fitting issue #89](https://github.com/ahmadkhanloo/hgfx/issues/89); [new cross-run bitwise replay issue #90](https://github.com/ahmadkhanloo/hgfx/issues/90). This does not modify or replace [the original BFGS/Armijo report](PERF01D_SUBJECT7_BFGS_BRANCH_2026-11-06.md), [original optimizer history](PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md), or [paired same-vector gradients](PERF01D_SUBJECT7_GRADIENT_2026-11-06.md).

## Authority, data and source

- Product: unchanged HGFX v1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; MATLAB HGF Toolbox 8.2.0 reference `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2026a.
- Model: 128-trial original binary HGF + unitsq_sgm, original zero-based subject 7, unchanged priors/optimizer/input/seeds/parameters.
- Original **real full-public-fit BFGS** [run **42187240378**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) was restored and **both exact original SHA-256** checked: HGFX `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`; MATLAB `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.
- Original **10 same-parameter Ridders gradient evaluations** from [run **42120381058**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120381058) were independently restored and checked against exact SHA-256: HGFX `17582f684f9db815dbd1986e5f67f2105c82f3ccf53f76d0e555cc16e2fd4057`; MATLAB `bea60b75cedf3bea6152f118f149d3ddeb8e8310793c55b9f4fcaf3dc09ec5d1`.
- The unchanged successful historical source-branch replay from [CI **42188247052**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052) was validated using `subject7_bfgs_results/derived-42187240378.json`, preserving **22** source-curvature decisions and **22** nonterminal candidate full steps.
- New derived calculation: [CI **42194769569**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194769569) **SUCCESS** with **39/39 focused tests** (10+8+10+11), no new fitting, no time measurement, no hardware GPU claim. Separate auto-committed machine-readable `benchmarks/runtime_v1/subject7_bfgs_results/derived-direction-42187240378-42120381058.json` at `ce6f1705e552ea422f37f1403e2db48e636cc8ab`. Derived source `benchmarks/runtime_v1/derive_subject7_direction_decomposition.py`; CI `.github/workflows/perf01-direction-decomposition.yml`, synthetic negative controls `tests/test_perf01_direction_decomposition.py`.

## Mathematical decomposition (descriptive, NOT unique causal attribution)

With `T_H,T_M` the saved approximate inverse Hessians and `g_H,g_M` the Ridders gradients evaluated by their own engines at their **different** saved parameters `x_H,x_M`, the difference in raw quasi-Newton directions is:

```
d_H - d_M = -(T_H g_H - T_M g_M)
          = -(T_H - T_M) g_M - T_H (g_H - g_M)
```

This is an algebraic partition, not an intervention that identifies which source expression **caused** an optimizer divergence. At the five post-hoc diagnostic anchors `[0,1,13,14,23]`, the previously exported cross-engine **same-x** gradient `g_M(x_H)` permits a further partition:

```
d_H - d_M = -(T_H - T_M) g_M(x_M)
          - T_H [g_H(x_H) - g_M(x_H)]
          - T_H [g_M(x_H) - g_M(x_M)]
```

The middle term measures the *direct same-parameter gradient-engine numerical difference* at those particular anchor vectors. The last term measures the gradient difference associated with **distinct parameter states** using one chosen implementation. Norms of terms cannot be simply added; vectors can oppose and cancel. Both partitions are nonunique in a causal sense.

### Observed BFGS record 10

| Quantity | Value |
|---|---:|
| `||T_H||_F`, record 9 → 10 | `1.5349192294 → 281.7690353884` |
| `||T_M||_F`, record 9 → 10 | `1.5349192104 → 281.7688831326` |
| SPD spectral condition, HGFX record 9 → 10 | `22.202 → 45198.342` |
| SPD spectral condition, MATLAB record 9 → 10 | `22.202 → 45198.306` |
| `||d_H-d_M||_2`, raw BFGS directions | `6.569361905386501e-5` |
| `||-(T_H-T_M)g_M||_2`, descriptive matrix term | `6.504746640799335e-5` |
| `||-T_H(g_H-g_M)||_2`, descriptive own-gradient term | `6.461557912477602e-7` |
| `||d_H^clipped-d_M^clipped||_2`, after frozen `maxStep=1` | `1.6207306067271615e-9` |
| clipped-to-raw difference ratio | `2.467105070582662e-5` |
| raw direction lengths, HGFX and MATLAB | `120.78523001088773` and `120.78516431756034` |
| observed next-point componentwise reconstruction residual, max | `8.881784197001252e-16` |

Both source directions here are clipped by the unchanged reference `maxStep=1`. Consequently, **very large raw directional differences do not translate proportionately into applied-step differences** at this record. The clipped-vector difference is about **0.002467%** of the raw-vector difference. This is a mathematical observation for this specific slot, not a general guarantee about convergence.

### Same-vector gradient information at record 14

From the algebraic **three-term** breakdown at HGFX's original record-14 point:

| Descriptive term (L2 norm) | Value |
|---|---:|
| Matrix-difference term | `1.5554583646351223e-7` |
| Gradient-state-difference term in MATLAB | `7.745282723490671e-8` |
| HGFX-vs-MATLAB gradient at identical HGFX point | `6.299323553659936e-12` |
| Total raw direction difference | `7.853345305796937e-8` |

At this selected vector, gradient differences attributable purely to the two numerical implementations **at identical x** are small compared with the algebraic terms involving the saved BFGS matrices and already-diverged parameter states. That fact does **not** prove the original source of the state divergence or give a general ranking over all 25 records. Record 23 is a terminal-history slot and **must not** be interpreted as an accepted step.

## Strict bitwise replay on different runners: additional OPEN engineering issue

- The earlier [strict derived replay 42188247052](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052) succeeded.
- New-host [attempts 42194275053](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194275053) and [42194481974](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194481974) **FAILED** the old exact equality of recomputed floating diagnostic scalars. Diagnostic logs show only `line_search_candidates` differed; examples include same raw vector norm recorded as `1448.9525498739686` originally and `1448.9525498739683` in the new replay. In both cases the raw evidence hashes were unchanged. Numerical reductions/host dependence are a plausible explanation **not yet confirmed**.
- A separate intermediate CI [42194741392](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194741392) failed because the workflow omitted a required historical report-path argument.
- The **original strict reporter is preserved unmodified**; its new-host failed replays remain historical evidence, and [Issue #90](https://github.com/ahmadkhanloo/hgfx/issues/90) explicitly tracks that repeatability problem. The successful new analysis **does not claim an identical-bitwise rerun**. It verifies the immutable original report and comparison JSON are exactly equal after stripping only the recorded workflow metadata, verifies original raw SHA-256, verifies the **already-successful and previously committed author-side derived** calculation record, and computes a **different, separately labeled** algebraic dataset. No scientific threshold or denominator is relaxed, and no failed experiment is silently converted to PASS.

## What this does NOT establish

- It does **not** identify a unique causal bug in MATLAB or HGFX; the decomposition uses frozen, previously diverged `x` and `T` states and five **post-hoc** same-parameter anchors per source engine.
- It does **not** certify optimizer termination parity, a MATLAB reference limitation, identity of every source-internal operation, or identifiability.
- It does **not** change original frozen workload eligibility: historical **63/64** complete-fit diagnostics (subject 7 `traj.mu` and `traj.muhat` fail), 28-cell inventory **16 review pending / 12 blocked**, six ineligible cells among original nine primary CPU workloads.
- The original source overwrites terminal iteration history, so reconstructed acceptance analysis excludes **transitions 22 and 23**. Only **22 nonterminal** transitions are considered.
- **PERF-01C NOT FROZEN, PERF-01D fitting NON-PASS, PERF-01E–H NOT EXECUTED. No physical GPU validation, CPU runtime comparison or speedup.** Independent reviewer remains required for any release claim or protocol lock.
