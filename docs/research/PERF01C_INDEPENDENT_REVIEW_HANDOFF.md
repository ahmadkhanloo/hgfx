# PERF-01C — Independent pre-freeze review handoff

Status: **OPEN / NOT FROZEN / INDEPENDENT REVIEW REQUIRED**  
Created 2026-11-04; this document is *not* an approval or independent-review verdict.

## Immutable evidence to inspect

- Prospective (unfrozen) protocol: `docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V1.md`; nine primary CPU cells, twelve conditional secondary cells, six throughput cells, one robustness cell. **Do not shrink, re-seed or silently replace failures.**
- Input/config code and checked datasets: `benchmarks/runtime_v1/{generate_inputs.py,inputs_manifest.json,export_release_configs.py,resolved_configs_manifest.json,inputs/,configs/}`.
- Frozen product `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` versus frozen MATLAB HGF 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Full trialwise paired evidence: `docs/research/PERF01D_DIAGNOSTIC_EVIDENCE_2026-11-04.md`, `benchmarks/runtime_v1/trialwise_results/summary-41854644533.json`, GitHub Actions [41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533). Raw independent MATLAB/HGFX exports linked by SHA-256.
- Full fitting paired evidence: `benchmarks/runtime_v1/fitting_results/summary-41855647245.json`, GitHub Actions [41855647245](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855647245); failed exporter attempt [41855569387](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855569387) retained.
- Source scientific gates: `docs/validation/MATLAB_EQUIVALENCE_POLICY.md`, `docs/architecture/NUMERICAL_POLICY.md`, `tools/check_m10_parity.py`, and frozen MATLAB `core/fitModel.m` + `building_blocks/hgf_check_trajectories.m`.

## Mandatory reviewer checks

- [ ] Verify **exact** SHA identities for HGFX v1.0.0 and MATLAB oracle and corresponding active function-path resolution, including the original/unified binary HGF ambiguity.
- [ ] Independently recompute SHA-256 for each canonical input/config file and verify every MATLAB/HGFX cell references the identical selected subject, trial mask, transformed start and fixed/free parameter definitions.
- [ ] Audit original MATLAB and HGFX trajectory/observation/optimizer code against model family, data, mask, priors and the returned end-to-end field set; do not infer scientific equivalence from matching scalar objectives.
- [ ] Independently recompute per-trial differences from archived **raw** exports, including all nonfinite/irregular entries, check first mismatched trial/level/state, and confirm sequential prefix failure lengths 348/346/349 without a false monotonicity assumption.
- [ ] Audit default fitting 128 for `final`, `H`, `Sigma`, `Corr`, `LME`, `AIC`, `BIC`, objective, complete trajectory, masks and residuals. Identify any numerical/optimizer limitation from reference evidence rather than a general label.
- [ ] Confirm that MATLAB 512/1024 **auto-resamples unstable starts** while HGFX compatibility currently rejects them; preserve `NOT_DIRECTLY_COMPARABLE` and the original nine CPU cells as ineligible where documented. No data/seed/start modifications to obtain faster outcomes.
- [ ] Verify **all** timing boundaries before freeze: MATLAB full `fitModel` versus HGFX full `fit_model`; JAX compile, transfers, synchronization, result materialization, postprocessing, CPU affinity/threads and GPU physical evidence must be separate.
- [ ] Review statistical analysis (paired order, warmups/repeats, bootstrap CI, multiple comparisons), pass/fail policy and all raw-data preservation rules **before** any final timing.
- [ ] Confirm historical paper protocol `hgfx-paper-protocol-1`, M18 FAIL and M17/M19 frozen evidence remain unchanged. Performance claims require a separate paper-protocol revision frozen **before** final experiments.

## Required reviewer output

Create a new `PERF01C_REVIEW_<date>.md` with:
- exact candidate source commit SHA and all reviewed evidence hashes;
- itemized findings (CRITICAL / HIGH / MEDIUM / LOW / INFO) with direct file/line references;
- explicit `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE` and justification;
- the predeclared per-cell eligibility matrix, including all blocked cells, and proposed **new-version-only** changes if necessary;
- reviewer identity and independence from the implementer (do not self-certify);
- unchanged frozen acceptance thresholds and timing contract.

**No green CI workflow alone counts as independent scientific review.** Until signed off and a versioned protocol lock is committed, `PERF-01C = OPEN`; `PERF-01E–H = NOT EXECUTED`. The benchmark has no validated speedup claim.

## Subsequent author-side evidence for the independent reviewer (2026-11-04)

The exact 64-subject, three-horizon, three-model MATLAB/HGFX fixed-vector cohort comparison completed on the same CI CPU runner: [GitHub Actions 41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774). All **576** declared model–horizon–subject combinations were retained: **448 matched valid** and **128 invalid in both**, corresponding to all 64 standard-HGF subjects at 512 and all 64 at 1024 trials. No config or scalar objective discrepancy was detected under existing diagnostic thresholds. These are not 576 matched fits or per-subject full-trajectory parity certifications.

- Machine-readable cohort results and 27 one/16/64-subject strata: `benchmarks/runtime_v1/cohort_results/summary-41860187774.json` (SHA-256-provenance links to raw CI artifact).
- Original archived push-race failure: [run 41859496548](https://github.com/ahmadkhanloo/hgfx/actions/runs/41859496548), where numerical evaluation and comparison succeeded but the evidence commit was rejected as non-fast-forward. Do not delete or recategorize it as scientific failure.
- Complete prefreeze inventory with all **28 originally planned cases**, showing **16 diagnostic-concordant/review-pending** and **12 blocked**, with no claim of final eligibility or scientific PASS: `benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json`, generated by [run 41860891268](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860891268).
- Timeable API/host/stdout/restart policy hazards: [PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md](PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md).
- Independent review request: [issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88).

**Do not close PERF-01C:** this section is an implementer evidence handoff, not an independent approval. In particular, the original nine-cell primary CPU speedup headline is ineligible under the observed failed frozen cells; no threshold may be weakened or originally defined case silently replaced. A new prospective protocol for a genuinely different headline, if wanted, requires separately justified scope and prior independent approval.


## Mandatory follow-up independent review: full-cohort fitting and source-only MATLAB sensitivity

Evidence from this stage is no longer pending:

- Original 64 public full fits: [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json`; 63 concordant, 1 out-of-tolerance original subject 7; nested denominators **1/1, 15/16, 63/64**. Full workflow remains a scientific **non-PASS**.
- Exact two-endpoint replays: [41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514), `benchmarks/runtime_v1/subject7_results/summary-41868723514.json`; both exact frozen fitted endpoints have MATLAB/HGFX concordant trajectories, states and trial likelihood; differences occur between distinct optimizer endpoints.
- Frozen MATLAB **self-sensitivity**, not modified reference software: [41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069), `benchmarks/runtime_v1/matlab_sensitivity_results/summary-41870479069.json`. The independently scripted exact-form objective *first reproduces original MATLAB optimizer endpoint with zero discrepancy*, then holds data/model/priors fixed and perturbs each of three free start parameters by ±eps. One of six probes has a final shift `7.640946009246363e-7` outside original M10 fitting tolerance.
- Exact derived author-side ledger, **original evidence untouched**: `benchmarks/runtime_v1/eligibility_candidates/candidate_v2_fullfit41863441006.json`, [run 41869747776](https://github.com/ahmadkhanloo/hgfx/actions/runs/41869747776). All 28 original cases preserved, 16 review-pending and 12 blocked, with two blocked fitting reasons now supported by actual failed complete-fitting evidence.

The independent reviewer must **check the source-only MATLAB objective against `fitModel.m`**, the exact original baseline reconstruction, all six perturbation endpoints and original source-vector raw artifact hashes, and decide whether these meet the **narrow** `MATLAB_REFERENCE_LIMITATIONS_POLICY.md` requirements for an explicitly delimited numerical-basin classification. The implementer must **not self-certify**, change the frozen 63/64 outcome, silently exclude subject 7, or promote grouped fitting to benchmark eligibility. Check optimizer termination and iteration histories as a separate scientific limitation question. No performance timing has occurred.


## 2026-11-06 additional author-side reviewer evidence

The [six-source replay report](PERF01C_SIX_SOURCE_EVIDENCE_REPLAY_2026-11-06.md) links the exact tested commit (1dd22bc5eef4502136e6b61a586d2129be951a8d), [Actions run 42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894) and machine artifact. This regression directly downloads and SHA-256-checks original raw MAT/HGFX archives and the standalone MATLAB-only sensitivity export; replays scientific comparison programs on those files; checks both 28-case ledgers; independently recalculates all six +/-eps(start) reference probe step sizes and original M10 final-parameter tolerance decisions. **47/47 engineering tests passed.**

For independent scientific sign-off, do not simply cite the green CI: separately audit the original frozen MATLAB source function paths and full fitModel objective, optimizer termination/iteration regime, scientific model and mask, specific subject-7 basin explanation and the proposed timing-boundary/hardware contract. No reviewer identity, independent APPROVE_PROSPECTIVE_FREEZE, versioned lock or performance timing exists. The existing **63/64** fitting failure and **12 blocked cases** remain unchanged.


## 2026-11-06 — original subject-7 optimizer-history caveat and evidence

**Important correction:** 101 saved values in earlier cohort diagnostics is merely `maxIter+1` **preallocation**, not confirmed 100 steps or matching optimizer convergence; the exact frozen reference `core/quasinewton_optim.m` initializes NaN-padded arrays and may overwrite terminal slots.

The exact-source fresh, untimed [subject-7 public-fitting trace 42115887599](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599) stored the entire paired `iter.x`/`iter.val` arrays and confirmed 25 finite slots per side. Original initial parameters/objective match; earliest nonzero numerical drift is at zero-based record 1 (`9.769962616701378e-15` max free-vector delta) and first inherited-final-tolerance crossing is at record 14 (`9.962832248078257e-8` max parameter delta). The last two filled records are duplicated on both sides, but **no MATLAB machine-readable termination reason is available**. The per-record use of the final-parameter numeric tolerance is a *descriptive diagnostic*, not a new acceptance gate.

The original full 64-fit discrepancy is not waived. Review details, source hashes, source model paths, raw artifact [13457295710](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599/artifacts/13457295710) and derived immutable analysis: [PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md](PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md). The separate derived report was verified by [42117014225](https://github.com/ahmadkhanloo/hgfx/actions/runs/42117014225). Independent reviewer must still check exact termination and source-level numerical choices before any reference-limitation classification. No PERF-01C freeze or speed results.


## 2026-11-06 — ten frozen same-vector objective and Ridders-gradient probes

The author-side [matched objective/gradient diagnostic CI 42120381058](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120381058) executed on exact tested commit `b9e1982fb7fee931ea907f5a25d3bc7a7cbbd1e1`: **11/11 regression tests** and **10/10 complete MATLAB/HGFX identical-parameter probes**. It used the unchanged original subject-7 dataset and five selected historical optimizer records from EACH source, original Ridders `min_steps=10`. Independent reproducibility and actual raw hashes: [PERF01D_SUBJECT7_GRADIENT_2026-11-06.md](PERF01D_SUBJECT7_GRADIENT_2026-11-06.md). Maximum exact-pair objective delta `1.4210854715202004e-14`; gradient component delta `1.6621634624236492e-11`. No missing anchors, no gradient discrepancy under the *inherited FINAL-parameter tolerance as a diagnostic lens*, **not** a separately established per-gradient scientific threshold.

Reviewer must check MATLAB's separately composed source-identical objective against the nested original `fitModel.m` objective and the Ridders method, as well as BFGS inverse-Hessian updates/line-search/termination and any accumulated small floating difference. Identical objective/gradient evaluations on ten **post-hoc selected** points do not prove full-fitting scientific agreement; **63/64** original full fits, subject 7 `traj.mu` and `traj.muhat` mismatch, lack of signed scientific disposition and **PERF-01C NOT FROZEN** persist. No timing run authorized.


## 2026-11-06 — bounded BFGS/full-step source audit for independent reviewer

**New author-side evidence, not a signed review.** [Paired real run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) exports full `iter.invH` from untouched frozen MATLAB/HGFX public fitting at original zero-based subject 7. [Derived run 42188247052](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052) rechecks immutable raw SHA-256 and source-curvature formula with **18/18** structural tests and no fresh optimization. Review exact source SHA `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d` for the original BFGS run and latest PR SHA separately.

- 101 allocated history slots, 25 finite; 24 recorded 3×3 inverse-Hessian matrices in each implementation; zero recorded resets.
- All **22 unambiguous saved BFGS curvature conditions** have matched branch outcomes (21 apply, one skip at index 11) and matched recorded T-change behavior.
- All **22 nonterminal candidate step reconstructions** use `alpha=1` and satisfy source Armijo with max residual `2.6645352591003757e-15`; this is **source-derived candidate** evidence, not an instrumented MATLAB line-search acceptance log.
- Record-10 T norm amplification ~183.57× in BOTH; cross-engine matrix difference `0.00015053299961209632` (largest absolute matrix component delta in this experiment). Potential numerical amplification mechanism; cannot infer its unique cause.
- Terminal source history overwrites stored entries; exclude transitions 22→23 and 23→24 from step-acceptance claims. Original complete fitting **63/64 still NOT PASS**. Original 28 and nine-primary CPU eligibility unchanged.

Use [PERF01D_SUBJECT7_BFGS_BRANCH_2026-11-06.md](PERF01D_SUBJECT7_BFGS_BRANCH_2026-11-06.md) for raw hashes, full numeric table, historical failures and reviewer limitations. Independent reviewer must check source-to-source objective and convergence handling, as well as protocol/clock/hardware semantics, before ANY separate prospective freeze. **No external approval has been provided by these computations.**


## 2026-11-06 — bounded direction-algebra, original maxStep clipping and bitwise portability

Review the source-anchored independent arithmetic reconstruction [42194769569](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194769569) (39/39 tests), using unchanged immutable archived MATLAB/HGFX public optimizer `iter.invH`, own-state Ridders gradients, and 10 earlier **same-parameter** matched Ridders evaluations. [Full reviewer-bound numerical report](PERF01D_SUBJECT7_DIRECTION_DECOMPOSITION_2026-11-06.md). The calculations are strictly algebraic **and not a causal intervention**:

- Record 10 BFGS spectral condition ~45198 in both sources, raw direction delta `6.569361905386501e-5`, **clipped actual-direction candidate** delta `1.6207306067271615e-9`, as both obey reference `maxStep=1`; no instrumented acceptance log.
- Source-record 14 same-x engine-gradient term L2 `6.299323553659936e-12`, much smaller than stored-T and different-x terms under this chosen nonunique decomposition. This does **not** certify an implementation defect or reference-only limitation. Last two terminal transitions are excluded from acceptance conclusions.
- Unexpected cross-run bitwise reproducibility failure for auxiliary norm/scalar diagnostic fields (original raw hashes unchanged) is documented as **OPEN Issue #90**; new report does not claim this engineering replay PASS. Historical strict failure CI runs are preserved; independent reviewer should decide whether any new host-independent exact replay protocol is needed prospectively.
- Original 64 full-fit outcome **63/64 NON-PASS**; no changes to thresholds, original denominators, seed/dataset/model, science, or release gate. **PERF-01C NOT FROZEN** and speed benchmarking not authorized.


## 2026-11-06 — same-host BLAS ULP isolation and real HGFX fitting dependency (Issue #90)

**New bounded author-side evidence, not external review approval:** [CI 42197971370](https://github.com/ahmadkhanloo/hgfx/actions/runs/42197971370) (22/22 tests) ran three independent processes on an identical AMD EPYC Linux runner, pinned NumPy 2.3.5; original 48 historic BFGS saved states, 96 scalar norm/slope values. Effective auto/SkylakeX had 3/48 norm and 13/48 slope one-ULP mismatches relative to original; forced Haswell matched 96/96 **original archived bit patterns**. Thus the within-host **OpenBLAS dispatch** mechanism is demonstrated for post hoc scalar diagnostics. Historical bitwise failures and exact-source comparator are preserved, and the original 42187240378 runner's effective BLAS path was **not logged**. [Full immutable evidence](PERF01D_ISSUE90_OPENBLAS_SAME_HOST_2026-11-06.md).

[CI 42199013326](https://github.com/ahmadkhanloo/hgfx/actions/runs/42199013326), 10/10 tests, untimed full original frozen **HGFX v1.0.0 public fits** on one runner with unchanged data/model/start/optimizer but auto vs Haswell OpenBLAS kernels, changed `iter.x` (max `4.4914698094089545e-7`), `iter.val` (max `2.6154653198773303e-7`), `iter.invH` (max `1.8149043592075031e-4`) and final full parameter vector (max `3.968255768427298e-8`). This documents environmental numerical optimizer sensitivity but **does not re-run MATLAB or evaluate full trialwise `traj.mu`/`muhat`**. Historical MATLAB endpoint comparison was *less close* under Haswell; changing BLAS to chase a desired PASS is prohibited. [Detailed full fit evidence](PERF01D_ISSUE90_FULL_FIT_DISPATCH_2026-11-06.md), [Open Issue #90](https://github.com/ahmadkhanloo/hgfx/issues/90), subject-7 mismatch [#89](https://github.com/ahmadkhanloo/hgfx/issues/89).

**Reviewer MUST retain original 63/64 non-PASS and original sample denominators**. The exact original MATLAB same-model reference and full trajectory acceptance fields need scientific comparison before reference-limitation classification, and the independent prospective PERF-01C benchmark freeze approval is still **NOT GIVEN**. This engineering run measures no speed/CPU/GPU performance.


## 2026-11-06 — original-sample COMPLETE 28-field subject-7 trialwise comparisons, no updated scientific gate

[Run **42203036203**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42203036203), **SUCCESS**, exact tested SHA `c4d858bcdc090ff6590d99ca7f9c6f9609d1884a`, 12 new + 7 existing cohort unit tests. Two new real *frozen full public HGFX v1.0.0* fits under auto/SkylakeX and Haswell on the same runner. All original 64-subject HGFX/MATLAB fit raw SHA-256 checks first, original 63/64 non-PASS and subject-7 failed fields reproduced exactly, including all four exact trial indices and the original numeric field tolerances. **Every original 28 fit/traj field was compared**, not just two selected fields. Fresh auto versus originally archived MATLAB repeats 4 failing coordinates each for `traj.mu`/`traj.muhat`; fresh Haswell **increases** mismatch to 4 fields: `traj.epsi` (5 failing coordinates), `traj.mu` (14), `traj.muhat` (14), `traj.psi` (40). In new paired HGFX modes, `traj.mu` and `traj.muhat` each differ in four out-of-tolerance cells. Complete data/hashes/source indices in [PERF01D_SUBJECT7_COMPLETE_TRAJECTORY_2026-11-06.md](PERF01D_SUBJECT7_COMPLETE_TRAJECTORY_2026-11-06.md).

**Independent-review action:** This is a **same-runner environment control for HGFX**, but historical MATLAB reference came from a DIFFERENT CI run. No inference that forcing a kernel repairs scientific fitting; no reference-only limitation certification, no removal of subject 7, no new threshold, no prospective runtime benchmark freeze. A next **crossed same-vector full HGF forward-trajectory** diagnostic at both original fitted endpoints would more directly separate model-forward/source discrepancy from optimizer-path effects. Original all-64 scientific **63/64 NON-PASS**, PERF-01C NOT FROZEN, trialwise timing withheld.


## 2026-11-06 — original HGF model family same-parameter HGFX/MATLAB full forward concordance, NOT fit acceptance

[**CI 42204633161**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204633161), exact executed code SHA `690d00fcb1fcb3384aa23db92fba1df963be719e`, **18/18** synthetic/original cohort tests, frozen HGF Toolbox 8.2.0 MATLAB R2026a SHA `2437f4dc241541072722a2695ddeca7b44d83dd3` and HGFX 1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, full original 64-fit raw SHA control. **Three and only three** original identical transformed full 15-parameter source vectors (old HGFX full fit endpoint, old MATLAB full fit endpoint, old frozen start). Both models direct forward `hgf_binary` return 11/11 original `fit.traj` fields and inference states **within exact inherited numeric tolerances** at all three original vectors, including `mu/muhat` zero failing trial indices. Each direct forward additionally reproduces all 11 trialwise fields of its own original public `fitModel` output at its own fitted vector. Read [PERF01D_SUBJECT7_CROSSED_FORWARD_2026-11-06.md](PERF01D_SUBJECT7_CROSSED_FORWARD_2026-11-06.md) and derived `benchmarks/runtime_v1/issue90_results/derived-crossed-forward-42204633161.json` for every field, source SHA, failed attempts and exact trial indices.

**Important external scientific distinction:** three-point same-vector forward source concordance **is NOT the original full fitting parity**. The original two independently optimized endpoints are different; the original all-64 **63/64 scientific non-PASS** remains, with four failing original subject-7 `traj.mu` cells and four `traj.muhat` cells. The crossed experiment supports optimizer numerical-path sensitivity as a specific hypothesis but cannot uniquely classify it as an acceptable reference limitation, show equivalence over the full parameter domain, or independently approve inclusion in prospective runtime comparisons. No case selection, tolerance relaxation, algorithm change, GPU evidence or timing has been done. Independent reviewer verdict and original prospective PERF-01C scientific-eligibility lock still REQUIRED.


## 2026-11-06 — immutable 2×2 omega2/omega3 crossed-forward causal-scope clarification, still NO fit PASS

[Successful MATLAB/HGFX source-locked CI **42213683575**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213683575), exact executed source SHA **f79f16003404f8060c5cfcec9e284f90f4e8862d**, 23/23 tests (16 new, 7 original 64-subject). Original full 64 public fitting raw SHA256 and original 63/64 failed subject-7 trialwise coordinates checked **before** any source-matched forward. Four prespecified original fitted **2×2 omega2 (index12) × omega3 (index13)** parameter combinations evaluated by both original unmodified MATLAB HGF Toolbox 8.2.0 and HGFX v1.0.0, original subject 7/128 trials, no optimizer and no timings. All 11 HGF perceptual trajectory fields and full inference states were within unchanged v1 tolerances for **all four** exactly matched forward vectors. Each forward source reproduces own original fitting endpoint's 11 trialwise fields. New complete signed decomposition across ALL 11 fields attributes **99.9995379–99.9997989%** of original failing mu/muhat signed differences at exactly original failed coordinates to the **changed fitted omega2 forward input**, with omega3 ~1e-15 and direct source-forward/reconstruction components zero there. Read [full per-cell report](PERF01D_SUBJECT7_OMEGA_COUNTERFACTUAL_2026-11-06.md) and immutable [machine-readable result](../../benchmarks/runtime_v1/issue90_results/derived-omega-counterfactual-42213683575.json).

**REVIEWER: Do not confuse counterfactual forward-input attribution with why either optimizer generated that omega2**. The original independent MATLAB/HGFX *fitted omega2 values differ*, original full 64 fitting result is still **63/64 NON-PASS** (subject 7 four mu, four muhat failed coordinates). Strict original existing tolerances/samples/failed raw artifacts remain unchanged. Mixed-corner observation parameter logze does not enter perceptual hgf_binary forward but DOES affect original joint fitting objective. This is **not** general identifiability proof, reference-only scientific limitation, whole-model full fit parity, allowable BLAS switch, eligibility approval, or an independent scientific reviewer decision. Independent PERF-01C gate #88 remains OPEN, no timings/speedup. Review the signed param effects separately from separate optimizer/BFGS and BLAS sensitivity evidence.
