# PERF-01D — matched-vector MATLAB/HGFX full HGF forward at original subject-7 fitted endpoints (2026-11-06)

**AUTHOR-SIDE SOURCE-MATCHED FORWARD DIAGNOSTIC REPRODUCED. Original complete public fitting 63/64 NON-PASS unchanged. No external review, timing, reference-limitation certification or speedup.**

Project tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87); [subject-7 scientific fitting #89](https://github.com/ahmadkhanloo/hgfx/issues/89); [PERF-01C external scientific review #88](https://github.com/ahmadkhanloo/hgfx/issues/88); [auxiliary numerical runner portability #90](https://github.com/ahmadkhanloo/hgfx/issues/90). Context: [complete fitting trajectory vs original MATLAB](PERF01D_SUBJECT7_COMPLETE_TRAJECTORY_2026-11-06.md) and [subject-7 BFGS/Armijo](PERF01D_SUBJECT7_BFGS_BRANCH_2026-11-06.md).

## Why a crossed fixed-vector forward experiment was needed

The original **full 64-subject public fitModel** oracle [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) compared **different, independently optimized** transformed parameters for MATLAB versus HGFX. The original scientifically unsuccessful case was zero-based **subject 7**, the original frozen `hgf_binary` perceptual + `unitsq_sgm` observation workflow, **128 trials**, only `traj.mu` and `traj.muhat` outside original numerical tolerances, four coordinate mismatches each. Re-running full HGFX fits with different OpenBLAS dispatched kernels confirmed optimizer-path sensitivity and **did not** cure full fitting non-PASS.

This NEW diagnostic asks a scientifically narrower question: *at **exactly the same** transformed HGF perceptual parameter vector and same observed original input, do the **unmodified source implementations** of HGF forward agree?* Three parameter vectors fixed in advance from the original historical raw evidence, not chosen after observing the new results:
1. Original full-public **HGFX fitted endpoint** from the unchanged original HGFX raw `optim.final`.
2. Original full-public **MATLAB fitted endpoint** from the unchanged original MATLAB raw `optim.final`.
3. Original frozen **initial** transformed full 15-vector from the original configuration snapshot and matching both source `optim.init`.

All are original 15-entry transformed full vectors (14 perceptual + 1 observation entries; 4 original undefined entries NaN); free indices zero-based `[12,13,14]`; 128 original subject-7 input trials. The forward methods use exactly the perceptual first **14** parameters, while preserving the full 15-vector's original identity and the original `unitsq_sgm` model family. **No optimizer is run** for this experiment.

## Source, identity and baseline verification

- Untouched HGFX **v1.0.0** release/source commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; untouched MATLAB HGF Toolbox **8.2.0** source `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2026a.
- Original 64-subject input and resolved configuration, original first 64 public full fits, original starting and fitted transformed 15-vectors. Exact original 64 raw source SHA-256 checked BEFORE both direct forward calculations:
  - HGFX `6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb`
  - MATLAB `2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98`
- Source and setup-checks prohibit changed model, trial horizon, subject, nRandInit/start, parameter split, free-index set, NaN mask, original status or 64-case **63/64** failure.
- MATLAB direct `hgf_binary(r,params(1:14),'trans')` with original `r.u,r.y,r.c_prc,r.c_obs,r.c_opt,r.ign,r.irr`; HGFX direct frozen `FORWARD['hgf_binary'](u,params[:14],transformed=True,ignored_trials=...)`. All **11** original trialwise fields, plus full **128×3×4** inference-state array; original `traj.w` has 128×2 while other 10 fields have 128×3. No modifications to MATLAB/HGFX source libraries.
- Precondition for interpreting any cross-engine comparison: each engine's *direct forward at its own archived fitted endpoint* must reproduce its **own original full-public-fit `fit.traj`** under the original numerical field tolerance, with **zero missing fields or suppressed failures**. This precondition passed in both engines for all 11 fields.
- Tolerances exactly the existing `compare_fit_cohort.py` trialwise `rtol=3e-8, atol=3e-10` as defined in original source. None modified or optimized for this experiment.

## Real CI provenance, failures retained, signed sources

- Successful dedicated [**CI 42204633161**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204633161), exact tested code SHA `690d00fcb1fcb3384aa23db92fba1df963be719e`, **11 new + 7 original cohort tests = 18/18**, full frozen input/config validation. Both original MATLAB/HGFX source checkout SHAs explicitly compared with frozen documented SHAs. No fresh full fit or CPU/GPU timing.
- Separate raw artifact includes fully reported `hgfx_raw.json`, `matlab_raw.json`, comparative `derived-crossed-forward-42204633161.json`. New exact raw SHA256: HGFX `dad3ab8dd47ceb855776be61cd5f160865d11455f18e506243337fb886bd0a30`; MATLAB `750c1895fd64a852cc1430ca4abecd0922b89297435bbd9f82829f514c6c0c05`.
- Separate **permanent machine-readable derived evidence** `benchmarks/runtime_v1/issue90_results/derived-crossed-forward-42204633161.json`, bot commit `4d97ba775194cbd71625308c8a50d19f0a6c45a6`. This is NEW evidence, not a rewrite of any historical failure.
- Three earlier CI failures explicitly preserved as TEST-HARNESS shape/fixture issues, not scientific results:
  - [42204160475](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204160475) **FAILURE**: new HGFX forward-export validation mistakenly expected `traj.w` to have 3 columns, but original frozen data correctly has 2.
  - [42204294988](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204294988) **FAILURE**: original `w` shape check in the newly written comparator still expected 3 columns; new raw forward outputs existed but comparison stopped fail-closed.
  - [42204303012](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204303012) **FAILURE**: newly written synthetic unit test incorrectly modeled `traj.w` as 3-column, correctly rejected by the strict comparator. Corrected fixture only, source and scientific gate untouched.

## Observed results for three identical transformed parameter vectors

| Exact shared parameter anchor | Original full fitting self-reproduction | HGFX-vs-MATLAB original 11 trajectory fields | `traj.mu` failing cells | `traj.muhat` failing cells | Inference-state numerical tolerance |
|---|---|---|---:|---:|---|
| Frozen original starting 15-vector | n/a | **11/11 within original tolerance** | **0** | **0** | within original tolerance |
| Original HGFX public fitted 15-vector | HGFX direct ↔ own historical `fit.traj`: **11/11** | **11/11 within original tolerance** | **0** | **0** | within original tolerance |
| Original MATLAB public fitted 15-vector | MATLAB direct ↔ own historical `fit.traj`: **11/11** | **11/11 within original tolerance** | **0** | **0** | within original tolerance |

At the HGFX original fitted endpoint, the *two engines' same-vector* `traj.mu` and `traj.muhat` have **max absolute difference exactly 0** in the recorded results, `traj.epsi` max `4.3021142204224816e-16`, `traj.psi` max `2.0605739337042905e-13`, and inference states max `1.1546319456101628e-14`. At the original MATLAB endpoint and original start, the recorded `mu/muhat/epsi/psi` max absolute differences were 0. All available **11 original trajectory fields**, not selected subsets, were checked at all three anchors; all are individually within unchanged old tolerances.

**Control:** reconstructing source-matched forward trajectories at each engine's **own** original fitted parameter vector reproduces all 11 trialwise fields of that engine's *original public fitting* output with no differences outside tolerance. Therefore the source-matched forward comparison is valid in this bounded sense; it is not merely comparing a different or accidentally simplified forward variant.

## Interpretation and original scientific gate

**Observed:** the direct `hgf_binary` perceptual forward engines agree under the originally frozen numerical tolerance at the original HGFX endpoint, original MATLAB endpoint, and original starting vector. Original full-public-fit HGFX↔MATLAB **still differs** at 4 cells each in `traj.mu` and `traj.muhat`, because the two independently optimized fitted full vectors are different. This strongly **supports** (but does not uniquely establish) the **optimizer numerical-path / different fitted parameter** explanation over an intrinsic forward-model mismatch *at the three tested vectors*.

**Not established:** complete fitting parity across the all-64 original subjects, equality of objective/gradient at every vector in optimization path, exact matching termination reason, scientific identifiability, unique optimizer root cause, approval to change BLAS/restarts/tolerance, or permission to classify MATLAB as reference-limited. Even exact source-matched forward reproduction is **not a full-fitting scientific PASS** or an externally adjudicated reference limitation.

The original scientific status is **63/64 NON-PASS**, with exact historic `traj.mu`/`traj.muhat` failures and no thresholds/data/seeds/subjects hidden or removed; 28-case inventory 16 pending review, 12 blocked, six of nine primary CPU cells ineligible. PERF-01C external independent review [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) **OPEN / NOT FROZEN**; subject-7 scientific mismatch [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) remains OPEN, [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) separately OPEN. **PERF-01E–H NOT EXECUTED, NO CPU/GPU RUNTIME/SPEEDUP CLAIM.**

### Next review task

Independent review must distinguish:
1. Full `fitModel` implementation parity and accepted fitted `traj.mu,muhat` results (still **NON-PASS**).
2. Source-matched isolated *forward* parity at these **three** vectors (author-side engineering evidence of within-tolerance, **not full fit**).
3. Optimizer/numerical sensitivity and reference-only model identifiability (requires external scientific adjudication).

Prospective benchmark freeze requires an independently approved scientific eligibility policy and exact sample/protocol lock; no ad hoc dispatch change can satisfy it.
