# PERF-01D — actual frozen private MATLAB objective at both original x6/T6 candidates (2026-11-07)

**AUTHOR-SIDE DIAGNOSTIC EXECUTED / 3 ACTUAL PRIVATE NESTED OBJECTIVE CALLS RECORDED. Original 64-public-fit scientific evidence 63/64 NONPASS. PERF-01C NOT FROZEN; independent review NOT RECEIVED; no benchmark timing, GPU or speedup. This is NOT a prospective scientific acceptance PASS.**

## Pre-execution contract and post-result selection

New private-objective experiment was specified in [PERF01D_PRIVATE_MATLAB_X7_ARMIJO_PRESPEC_2026-11-07.md](PERF01D_PRIVATE_MATLAB_X7_ARMIJO_PRESPEC_2026-11-07.md), committed **before new private x7 observations** at **`a79cd7a0f83f14b4959b16dadbb1c696960c96bc`**. The *choice of the anomalous HGFX-own original record 6* was explicitly **post-result selected**, based on an already-observed 50-point Ridders gradient discrepancy and preliminary source algebra. New measurement was prospectively specified relative to those prior results, but the overall sample choice is not preregistered or independent.

Frozen reference: HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2026a; HGFX v1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; `hgf_binary` / `unitsq_sgm`, subject zero-based **7**, original 128 trials, free indices [12,13,14], start [-3,-6,3.871201010907891]. Original public fitting [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) remains **63/64 scientific NONPASS**; first subject-7 failure includes **4 `traj.mu` and 4 `traj.muhat` values** beyond the original tolerances. Source nested 15/16 NONPASS and all later eight real same-runner fitting failures remain unchanged.

Prior source BFGS raw [42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378): SHA-256 `hgfx_raw.json=060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`, `matlab_raw.json=4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`. Prior 50-anchor private MATLAB gradient report [42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614), paired report SHA-256 `2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d`. EXACT selected one-step candidate report [42366705874](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874), SHA-256 **`b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144`**; verified before measuring the new private objective. No altered or reselected candidate permitted.

## Complete run accounting, including the first failure

- First actual-private [run 42375242431](https://github.com/ahmadkhanloo/hgfx/actions/runs/42375242431) at `0ed8c898f195495a34bb450d77aae03c58ed4efe` **FAILED at MATLAB report serialization**, after reaching the three-call callback: unequal fields among the base/candidate struct records made `[rows{:}]` invalid. The run did **not** yield a verified new private-objective report or Armijo conclusion. Workflow failure and artifact remain visible; recorded on [PR #91](https://github.com/ahmadkhanloo/hgfx/pull/91).
- Serialization-only repair `b3821627e787380766843660a36ae04017535987` retained the original heterogeneous records as a cell array before `jsonencode`; source candidates, MATLAB/HGFX, frozen optimizer settings, scientific threshold and dataset untouched.
- Final source [GitHub Actions run **42375431029**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42375431029) at exact tested SHA **`b3821627e787380766843660a36ae04017535987`** **SUCCESS**: **9/9** fail-closed synthetic controls, both original BFGS SHA-256 checks, original 63/64 and 4+4 failure proof, exact candidate member SHA-256, and **3/3** actual finite frozen private MATLAB objective observations. Callback delegated to original optimizer exactly once, and **26/26 explicitly compared stable public MATLAB fit fields** were strictly identical between native and instrumented runs (15 `optim`, 11 `traj`). No runtime timing.
- Immutable [artifact **13575801232**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42375431029/artifacts/13575801232), ZIP SHA-256 **`2b5bf6daabdfbf00902a0134f53886f3dcb7eddba1a7a168512f546eceb32f65`**. Raw `private-matlab-three-candidate-objectives.json` SHA-256 **`b901486c9f8a17cc414f60b284ecc707c0fb314652e1089db29a91ae208fadd7`**; verified derived `derived-private-matlab-armijo-summary.json` SHA-256 **`f42274c7f284edaa19bbb5ff09e69887471be9e04bbb615e9effca3a35a75275`**. Full provenance and source file hashes saved in artifact.

## Actual private objective observations (original fixed x6/T6)

Original fixed **HGFX-own** record 6 free x: `[-1.1621811570388512,-6.37816839506084,-0.23738383160834042]`. The saved frozen **HGFX-owned inverse Hessian T6** was held fixed; each candidate came from a different gradient at this **same x6**. The real original MATLAB-own x6/T6 is **different** and is not substituted here.

| Evaluated source point | Genuine frozen MATLAB private nested negative-log-joint | Previous frozen HGFX objective at same candidate | Original Armijo full-step on **private MATLAB objective** |
|---|---:|---:|---|
| Original HGFX-own source x6 | `108.28848680066957` | `108.28848680066957` | Not applicable |
| Next candidate from original HGFX gradient with original x6/T6 | `105.8665439753067` | `105.8665439753067` | **TRUE** |
| Next candidate from actual private MATLAB gradient at same HGFX x6/T6 | `105.8665440308226` | `105.8665440308226` | **TRUE** |

All **three** private MATLAB values are finite and **exactly numerically equal** (after binary64 JSON round trip) to the archived corresponding frozen HGFX objective values; zero scalar disagreement at these particular three points. Previous same-x Ridders stencil did find 33/245 1–2 ULP unequal values at *other perturbation points*, and the full original 63/64 fitting failure remains unaffected. No blanket objective-surface equality follows.

Both candidates satisfy the unchanged original Armijo `lhs < 1e-4 * (gradient' * original_unclipped_direction)` against actual measured MATLAB-private `f(x6)`; the two original slopes/normalized BFGS directions remain separately recorded in the source candidate JSON. This tests **full-step eligibility on this one fixed HGFX-owned T6/x6**, not actual original **MATLAB-owned** optimizer branch selection. It reveals **no reconstructed Armijo Boolean branch flip** between these two local hypothetical candidates, notwithstanding the already measured **1.0444791836983214e-08** difference in their next-step candidate coordinates.

## Interpretation, unresolved gates and independent review

This strengthens the bounded claim that small numerical Ridders differences can generate different BFGS next-step *coordinates* while the frozen private MATLAB objective accepts **both** hypothetical full-step candidates in an Armijo check. It **does not** establish that MATLAB's actual historical optimizer used the HGFX-own x6/T6, or that either hypothetical point caused the original full-path divergence, or that either derivative is uniquely correct.

The original source **63/64 SCIENTIFIC NONPASS** persists; the direct full public trajectory fit was **not re-run** here. PERF-01C **NOT FROZEN**, 28 original candidate workloads **16 REVIEW-PENDING / 12 BLOCKED**, independent review [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) **NOT RECEIVED**, PERF-01E–H **NOT RUN**, no GPU evidence and no speedup/paper claim.

Required next adjudication: independently examine the real private objective, recorded original vs hypothetical x6/T6 distinction, source Armijo algebra and archived SHA evidence, before deciding whether the demonstrated local numerical sensitivity is sufficient to classify the original full-fit deviation. The responsible classification remains **optimizer/numerical-sensitivity candidate / scientific-fit NONPASS**. No tolerance changes, new protocol exception or independent signoff are implied by this successful author-side probe.
