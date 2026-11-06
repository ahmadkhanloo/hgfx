# PERF-01D — original subject-7 fitted omega2 25-record optimizer-path forensic (2026-11-06)

**Status: AUTHOR-SIDE ORIGINAL RAW SOURCE-DERIVED ENGINEERING DIAGNOSTIC. NO SCIENTIFIC FIT PASS. NO OPTIMIZER TERMINATION-CAUSE VERDICT, NO TIMING.**

Follows the [all-original-endpoint 2×2 HGF omega2/omega3 crossed counterfactual](PERF01D_SUBJECT7_OMEGA_COUNTERFACTUAL_2026-11-06.md), which found that the **original eight failing subject-7 trialwise mu/muhat positions were dominated by the change in fitted perceptual omega2**. This report asks where that parameter difference appeared in the historical optimizer trace, using NO NEW fits or unarchived data. Does not supersede any historical raw or failed experiment.

## Locked sources, provenance and protocol

- Source is the original MATLAB/HGFX complete public-fit BFGS record [CI 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), exact tested experimental SHA **5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d**, original v1.0.0 HGFX SHA **4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27**, MATLAB HGF Toolbox 8.2.0 SHA **2437f4dc241541072722a2695ddeca7b44d83dd3**, original zero-based subject 7 and 128 trials, original HGF binary + unitsq_sgm. Original all-64 scientific fitting **63/64 NON-PASS**.
- Immutable original raw BFGS SHA256 verified: HGFX **060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce**, MATLAB **4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a**. Original source summary and comparison JSON identity verified, plus previous successfully committed source-branch derived report and its historical [CI 42188247052](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052) evidence. Separately preserved cross-host strict bitwise scalar discrepancy remains [OPEN Issue #90](https://github.com/ahmadkhanloo/hgfx/issues/90).
- Original optimizer history buffer is **101 allocated slots, 25 actually populated**. Zero-based original free-coordinate order [omega2 / om[1], omega3 / om[2], observation logze]. Original initial free vector preserved identically for both sources. There are **22 unambiguous nonterminal transitions**, indexed 0..21. Original saved terminal transitions **22,23** cannot be interpreted as accepted steps, because frozen MATLAB overwrites terminal history slots. Original 23rd and 24th zero-based states are duplicated in both sources.
- Retain original per-coordinate transformed final fitted parameter numerical tolerance **rtol=3e-8, atol=3e-10**, but applying that FINAL-parameter acceptance lens to intermediate optimizer points is **DESCRIPTIVE ONLY**. NO new intermediate optimizer acceptance threshold is introduced.

## Real CI and evidence

[**CI 42214972548**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42214972548) **SUCCESS**: 9 new omega2-history tests + 8 existing BFGS original-branch tests + 10 existing direction-decomposition tests = **27/27**. New code SHA **ca50e37b26a9d4c271136acc43d76ee9cee51c3b**, original complete archived fitting raw checked. Original BFGS matrix/Ridders at own original saved points reused, without fresh scientific reference or optimization.

Machine-readable **all 25 source omega2/omega3/logze signed pairwise differences**, all **22 source-verifiable clipped directions/next-step arithmetic**, and **two explicitly excluded terminal slots**: **benchmarks/runtime_v1/subject7_bfgs_results/derived-omega2-history-42187240378.json**. Bot evidence commit **fa525b569943e2060e0792ba01c65b3acd620369**. Original first and last point, every other intermediate point, original raw source SHA and original failures preserved.

## Results: original signed HGFX minus MATLAB omega2

| Original optimizer record, zero-based | omega2 difference | Interpretation |
|---|---:|---|
| 0 | 0 | Exactly identical original source optimizer start |
| 1 | -3.552713678800501e-15 | First **bitwise** nonzero omega2 separation; no scientific mismatch gate at this iteration |
| 20 | -3.1033044933792553e-7 | First omega2 difference beyond the *inherited FINAL parameter tolerance applied descriptively at each intermediate state*; not an optimizer iteration acceptance criterion |
| 21 | -3.1051412108240584e-7 | One of the 22 nonterminal verified saved states |
| 22 | +3.7255962581639324e-7 | **Maximum recorded omega2 difference**; reached via verified nonterminal transition 21, but transition from record 22 is NOT interpretable as an accepted source step |
| 23 / 24 | -1.890746936794585e-8 | Repeated terminal saved fitted parameter, with source historical final vector matching record 23 |

Source final fitted full-vector differences:
- omega2 (index 12): **-1.890746936794585e-8**;
- omega3 (index 13): **+3.291654060433302e-8**;
- observation logze (index 14): **-6.787941320141044e-10**.

At final historical omega2, original MATLAB fitted omega2 is **-8.223463945398366** and HGFX fitted omega2 is **-8.223463964305836**. Inherited FINAL parameter tolerance at that **MATLAB** value is approximately **2.47003918361951e-7**, substantially larger than the observed final omega2 difference **1.890746936794585e-8**. Thus the original comparison of the final fitted parameter vector can be numerically within its historical tolerance **while original fitted trialwise mu/muhat near-zero coordinates fail the distinct fixed trialwise absolute tolerance**. This is a **sensitivity of different measured outputs and tolerances**, not evidence permitting a new relaxation.

First exact source discrepancy (index 1) is tiny at ~1e-15, whereas the source difference can grow to several 1e-7 at intermediate saved states. This temporal pattern and the previously documented BLAS/BFGS numerical amplification **are consistent** with accumulating numerical path effects, but do NOT identify the unique source operation, precise source line-search acceptance/termination event, genuine optimization model degeneracy or scientific reference limitation. At index 21, the source-derived clipped omega2 step difference is **+6.830737466767545e-7**, and the observed next point omega2 signed difference moves to **+3.7255962581639324e-7** with small binary64 arithmetic residual, but that calculation is a **source-reconstructed step** and NOT an instrumented optimizer trace.

## Honest gating and next action

All original 64 public fitting results remain **63/64 NON-PASS**, subject 7 four mu plus four muhat failures. The new source-only analysis used no alternative datasets, seeds, priors, optimizers, tolerances, excluded trials, new MATLAB/HGFX source builds, timing or GPUs. The original performance grid **28 cases (16 review pending / 12 blocked), six of nine original primary CPU cells scientifically ineligible** is unchanged.

Independent [PERF-01C review #88](https://github.com/ahmadkhanloo/hgfx/issues/88) is still OPEN/NOT FROZEN; subject-7 scientific fitting [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) OPEN; cross-host numerical replay [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) OPEN. **PERF-01E–H NOT EXECUTED, NO SCIENTIFIC FITTING PASS, NO TIMED SPEEDUP.**

The external reviewer must decide scientific identifiability/acceptable optimizer output compatibility from same-source, same-model and exact full-public-fit comparisons before any prospective benchmark eligibility freeze. Existing candidate numerical explanations and tiny endpoint shift are **NOT** grounds for silently replacing the original failed case with PASS.
