# PERF-01D — subject-7 same-vector objective and Ridders-gradient diagnostic (2026-11-06)

**Engineering execution: SUCCESS. Scientific interpretation: DIAGNOSTIC ONLY / NOT INDEPENDENTLY REVIEWED / NO SPEED CLAIM / NO NEW SCIENTIFIC PASS.**

Tracking: [PERF-01 PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [subject-7 scientific mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89). This is a *new, untimed* follow-up to [the frozen public fit optimizer-trace audit](PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md). Do not reclassify the original failed cohort or change its thresholds, model, parameter vectors, seeds, or reference source.

## Exact source and method

- MATLAB HGF Toolbox 8.2.0 source SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2026a, source utility `utilities/riddersgradient.m` / `utilities/riddersdiff.m`, `min_steps=10`.
- HGFX 1.0.0 frozen source SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, `src/hgfx/optim/ridders.py`, `hgfx.compat.fitting.hgf_binary_unitsq_fit_problem`; Python 3.11 and NumPy 2.3.5, `JAX_PLATFORMS=cpu`.
- Original **128-trial binary HGF + unitsq_sgm** subject zero-based **7**, original canonical input/config and free parameter indices `[12,13,14]`. Both exact frozen checkouts were verified by CI; the original paired raw optimizer trace from [42115887599](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599) was downloaded and its raw SHA-256 values checked against the earlier archive.
- Five fixed original history-record indices `[0,1,13,14,23]` from **each of the two original fitted optimizer paths** were used. For every one of the ten original archived parameter vectors, MATLAB and HGFX evaluated the exact **same transformed free-parameter vector**. No fitting/parameter update was run in this follow-up; every objective evaluation and gradient was a fresh independent model computation at a frozen input point.
- MATLAB objective is an external exact-form composition of `hgf_binary`, `unitsq_sgm` and the unchanged Gaussian priors, as in the previously validated unperturbed MATLAB reference-only sensitivity experiment; it is **not** a public callable `fitModel.m` nested `negLogJoint`. This distinction still requires external source-level reviewer scrutiny.
- These anchors are *post-hoc diagnostic points selected from prior observed trace positions*; they are **not** a prospectively approved benchmark subset, a proof covering all 25 populated trace rows or a per-gradient acceptance gate.

Implementation files: `benchmarks/runtime_v1/subject7_gradient_probes_hgfx.py`, `matlab/subject7_gradient_probes_matlab.m`, `compare_subject7_gradient_probes.py`; `tests/test_perf01_subject7_gradient.py`; workflow `.github/workflows/perf01-subject7-gradient.yml`.

## Executed workflows and immutable raw evidence

- [Run **42120354558**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120354558): **SUCCESS**, exact candidate SHA `7809d1375a5f3691362e88329c069e156e68cdba`, nine targeted tests passed, ten paired gradients computed.
- [Run **42120381058**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120381058): **SUCCESS**, exact candidate SHA `b9e1982fb7fee931ea907f5a25d3bc7a7cbbd1e1`, **11/11 targeted tests passed**, ten paired gradients recomputed. [Raw report artifact 13457889610](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120381058/artifacts/13457889610).
- Both successful runs produced **identical SHA-256 of each raw file**: HGFX `hgfx_raw.json` = `17582f684f9db815dbd1986e5f67f2105c82f3ccf53f76d0e555cc16e2fd4057`, MATLAB `matlab_raw.json` = `bea60b75cedf3bea6152f118f149d3ddeb8e8310793c55b9f4fcaf3dc09ec5d1`.
- The original reference trace files remain `hgfx_raw.json` SHA-256 `6fe10be1dd1860612859e6efbe7bee13717e4787aed4a62f0e6b67a2072aac7a` and `matlab_raw.json` SHA-256 `ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f` from 42115887599.

## Numerical observations, not a predeclared gradient gate

All **10 of 10** archived same-vector objective/gradient pairs evaluated without missing anchors or metadata mismatches. Across the ten matched parameter vectors:

- Maximum absolute MATLAB vs HGFX **objective** difference: `1.4210854715202004e-14`. Several anchor pairs were exactly equal at binary64 precision.
- Maximum absolute MATLAB vs HGFX **Ridders-gradient component** difference: `1.6621634624236492e-11`, at the HGFX-origin vector from history record 1.
- **Zero gradient components** were outside the **previous fitting FINAL-parameter** numerical tolerance `atol=3e-10, rtol=3e-8` *when applied as a descriptive diagnostic lens*. It is **not** independently validated as a statistical or scientific gradient equivalence threshold.
- The gradient comparison covers all three free coordinates at each original anchor and preserves the original Ridders error estimates and gradient vectors in the raw artifact; no endpoints or cases were excluded.
- Objective values evaluated by each frozen implementation also reproduce the selected previously recorded own-history scalar values to within `1.4210854715202004e-14` at worst.

Previous source-specific [optimizer trace 42115887599](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599) found initial objective/parameters equal, first nonzero binary64-level path difference at history record 1, first **descriptive inherited-final-parameter tolerance crossing** at record 14, and **25 finite recorded slots** of 101 allocated on both sides; the exact MATLAB optimizer termination reason is not exported by the public API.

**Narrow evidence-based interpretation:** where the two implementations are evaluated at the *identical* original parameter vectors in the selected ten cases, their objective and Ridders-gradient computations are highly concordant numerically. Nonetheless, the actual optimizers follow slightly different paths that grow apart during fitting, consistent with roundoff/line-search/BFGS-path sensitivity as a **candidate mechanism**. This does **not** prove equivalent full optimizer trajectories, identical line-search acceptance, a reference-only numerical limitation, identical convergence behavior, all-vector gradient parity, or scientific identifiability. Additional matched-point BFGS and step-acceptance analysis remains a reviewer-relevant open question.

## Failed engineering executions were retained

- [Run **42119938618**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42119938618) completed the model/gradient calculations but failed when MATLAB attempted to encode a struct field containing a period (`hgfx_raw.json`). The raw partial artifact is retained; the exporter was corrected to use legal MATLAB fields while preserving both exact SHA values.
- [Run **42120320841**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120320841) exported all ten MATLAB probes but failed the comparator on MATLAB's legal normalized underscore key names; the comparator was fixed to canonicalize only those two expected keys, while still **rejecting any altered hash**. The eleven synthetic regression tests in the final run include explicit tamper rejection.
- These are **reporting/format engineering failures**, not numerical mismatch verdicts. Neither failed run was deleted or misrepresented as scientific PASS.

## Unchanged scientific gates

- Original unchanged all-64 public fitting [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006): **63/64** numerical/trajectory diagnostic concordance with zero-based subject 7 out of tolerance in `traj.mu` and `traj.muhat`. Original first-16 complete-fit numerator is still **15/16**. No tolerance or subject denominator was changed.
- Original 28 planned cases remain **16 diagnostic-concordant/review-pending and 12 blocked**, including six invalid original nine-primary CPU comparison cells.
- **PERF-01C OPEN / NOT FROZEN**, **PERF-01D fitting 16/64 NOT PASS**, **PERF-01E–H NOT EXECUTED**. No MATLAB-vs-HGFX CPU/GPU runtime or speedup has been measured.
- An **independent reviewer** still must investigate optimizer/BFGS/termination path evidence, exact MATLAB nested objective and source resolution, possible very narrow reference-limitation disposition under `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, and the prospective timing protocol before a frozen benchmark is allowed.
