# PERF-01D — subject-7 original omega2/omega3 forward counterfactual (2026-11-06)

**AUTHOR-SIDE SCIENTIFIC DIAGNOSTIC COMPLETED. Original full fitting 63/64 NON-PASS. No fitting, timing, independent reviewer verdict, release gate or speedup claim.**

Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [scientific subject 7 #89](https://github.com/ahmadkhanloo/hgfx/issues/89), [independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [auxiliary BLAS portability #90](https://github.com/ahmadkhanloo/hgfx/issues/90). Extends but NEVER supersedes the [original three-vector same-source HGF forward study](PERF01D_SUBJECT7_CROSSED_FORWARD_2026-11-06.md), the original full 64-subject public fit evidence or historical failed experiments.

## Locked question and original protocol

We use unchanged HGFX v1.0.0 source SHA **4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27**, original MATLAB HGF Toolbox 8.2.0 source SHA **2437f4dc241541072722a2695ddeca7b44d83dd3** (MATLAB R2026a), original **hgf_binary + unitsq_sgm**, zero-based subject **7**, original 128 binary trials, priors, input/config SHAs, and two exact archived fitted 15-vectors from the original [64-subject public fits, CI 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006).

Original complete scientific result: **63/64** within inherited tolerances, subject 7 **NON-PASS** with four original out-of-tolerance cells each in traj.mu and traj.muhat. Frozen original raw evidence SHA-256: HGFX **6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb**, MATLAB **2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98**. Both hashes and all 64 historical cases were verified before execution. The original test failure is preserved unchanged.

The free transformed fitted coordinates are zero-based **[12,13,14]**. The two *perceptual forward* free coordinates are **12 = om[1], omega level 2** and **13 = om[2], omega level 3**. Coordinate 14 is the fitted observation-model parameter logze, which **does not enter the isolated hgf_binary perceptual forward**, but does influence the original full fitting objective. The original HH/MM endpoints preserve original logze, and both mixed corners use the original MATLAB logze. Never extrapolate this to full fitting being insensitive to logze.

## Predeclared complete 2 x 2 original transformed parameter combinations

| Corner | omega2 | omega3 | logze |
|---|---|---|---|
| MM_original_matlab | Original MATLAB fitted | Original MATLAB fitted | Original MATLAB fitted |
| HM_hgfx_omega2_matlab_omega3 | Original HGFX fitted | Original MATLAB fitted | Original MATLAB fitted |
| MH_matlab_omega2_hgfx_omega3 | Original MATLAB fitted | Original HGFX fitted | Original MATLAB fitted |
| HH_original_hgfx | Original HGFX fitted | Original HGFX fitted | Original HGFX fitted |

All fixed/undefined perceptual parameters, NaN masks, model family and original observations remain identical. Both untouched HGF forward implementations were evaluated at **all four** identical shared transformed full 15-vectors; **no optimizer, seed change or timer** was involved.

Both source engines must reproduce all 11 fields of their OWN original full-public-fit trajectory at their own original fitted endpoint before interpretation; this precondition passed. At each of the four counterfactual corners, all original **11 trialwise fields** and 128 x 3 x 4 inference states were compared with existing frozen numerical **rtol=3e-8 / atol=3e-10**. Correct shapes: traj.w is 128 x 2, the other ten trialwise fields 128 x 3.

## Signed algebraic decomposition

For each trialwise element, let F be **the MATLAB perceptual HGF forward** at the four selected parameter vectors. The signed two-coordinate, equal-order Shapley terms are:

- omega2 effect = 0.5 * [(F(HM)-F(MM)) + (F(HH)-F(MH))]
- omega3 effect = 0.5 * [(F(MH)-F(MM)) + (F(HH)-F(HM))]

Their **signed sum** equals F(HH)-F(MM), including a symmetric allocation of interactions. The original complete-public-fit HGFX-MATLAB difference additionally has a same-vector forward-source and original-self-reproduction component. These are original-source forward counterfactual **attributions conditional on the archived fitted endpoint values**, NOT causality or source-operation attribution for the optimizer. Never add absolute terms as if they were independent contributions; signs can cancel.

## Real execution, raw proof, historical failures

[Successful source-locked CI **42213683575**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213683575), exact tested candidate SHA **f79f16003404f8060c5cfcec9e284f90f4e8862d**, **16 new tests + 7 existing 64-subject comparator tests = 23/23**, unchanged model/toolbox checkout SHAs, original full raw SHA checks, all four original corner vectors fixed and validated. Both engines produced complete untimed HGF forward outputs; all four shared-vector comparisons found **11/11 fields within unchanged original tolerance**, including zero mu/muhat failed cells at each common vector.

Raw output SHA256 for the new experiment:
- HGFX full four-corner raw: **baa28ef6ed440dfb21f2e698c237740b0c14d91dce8df48828b03476eaea4e1f**.
- MATLAB full four-corner raw: **f6ea95be0a3b6ffae51e3dcf2fab3f9a7958459082770039609c5b4dd67cda04**.

Complete new **machine-readable** original 11-field signed decomposition and all original failing coordinates: **benchmarks/runtime_v1/issue90_results/derived-omega-counterfactual-42213683575.json**, evidence commit **c55e451b92a81a3e31925944a8be06ac0c57755a**. Separately archived full original and new model outputs are retained in the run artifact. Original raw 64-subject data were never overwritten.

The initial [CI 42213536812](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213536812) **FAILED in 3/16 new synthetic test checks before MATLAB started**. The newly created JSON tree decoder had not accepted direct NumPy array inputs from negative controls. The utility was repaired to distinguish JSON lists from NumPy-array test inputs. **The failure remains documented**, and no frozen product/reference source, old evidence, threshold, random seed, subject or counterfactual grid was modified.

## Original subject-7 nonmatching mu cells, second perceptual level

All terms below are **signed**. The original corresponding muhat failing trials are one step later, at 85, 110, 118, 128, with the same signed values.

| mu one-based trial | Original HGFX-minus-MATLAB fit output | omega2 forward contribution | omega3 forward contribution | Original absolute tolerance bound |
|---|---:|---:|---:|---:|
| 84 | -7.841805399477764e-10 | -7.841769161104350e-10 | -3.623837341315550e-15 | 7.299856796816515e-10 |
| 109 | -7.501016509314784e-10 | -7.500996265091819e-10 | -2.024422296464934e-15 | 5.282733891438433e-10 |
| 117 | -5.624418569771805e-10 | -5.624395549991279e-10 | -2.301978052621223e-15 | 3.384168267912972e-10 |
| 127 | -6.203096508672346e-10 | -6.203084036010553e-10 | -1.247266179227324e-15 | 5.484480428789678e-10 |

For these original four failing mu points and the same four one-step-shifted muhat points, the signed omega2 term accounts for between **99.9995379% and 99.9997989%** of the signed observed difference, with omega3 around 1e-15 and same-vector source/reproduction plus arithmetic reconstruction residual recorded as zero **at these eight original failure coordinates**. This is not a global percentage of optimizer error, a scientific variance explained metric, or an independent eligibility criterion. The full fields may have larger omega3 effects elsewhere (for example max omega3 contribution across the entire mu field about 3.53e-13); full 11-field data remain archived.

## Scope and unresolved decisions

**Supported in this exact bounded case**: the original eight trialwise HGF output failures arise almost entirely through the difference in **original fitted transformed omega2**, not through a substantive source-forward mismatch at these four fixed endpoint combinations. The origin of that fitted omega2 difference **inside either optimizer remains unresolved**. It may involve accumulated floating-order, gradient, BFGS/line search/termination, or scientifically under-identified estimates. The experiment does not prove which.

**Scientific gate unchanged:** historical full 64 public fits remain **63/64 NON-PASS**, original 28 prospective workload cells **16 pending independent review / 12 blocked**, six of original nine primary CPU cases ineligible. Independent [PERF-01C review #88](https://github.com/ahmadkhanloo/hgfx/issues/88) OPEN; fitting mismatch [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) OPEN; numerical portability [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) OPEN. **PERF-01C NOT FROZEN; PERF-01E-H NOT RUN, NO CPU/GPU PERFORMANCE OR SPEEDUP.**

**Next bounded engineering investigation:** inspect archived 25 populated full fitting optimizer slots and specifically the original fitted omega2 coordinate, its per-slot delta, BFGS step clipping, line search and finite-difference gradient; do not change original full fitting acceptance or classify reference limitations without an independent scientific verdict.
