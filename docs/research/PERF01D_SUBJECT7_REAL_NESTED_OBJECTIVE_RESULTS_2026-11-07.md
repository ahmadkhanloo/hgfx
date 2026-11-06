# PERF-01D — real frozen MATLAB nested fitModel objective, 50-anchor results (2026-11-07)

**ENGINEERING DONE / EXECUTION PASS. Scientific full fitting: 63/64 NONPASS. Independent reviewer: NOT RECEIVED. PERF-01C: OPEN / NOT FROZEN. Performance timing: NOT RUN.**

## Scope and exact source contract

An unmodified frozen MATLAB HGF Toolbox 8.2.0 function handle to the **actual private fitModel negative-log-joint objective** was intercepted via the public optimization-config callback. Frozen source fitModel.m constructs its nested negative-log-joint and restrictfun handle, then invokes c_opt.opt_algo(obj_fun, ...). A wrapper on a copy of the original quasinewton optimizer config evaluates the **50 source-locked anchor occurrences** and delegates once to the unchanged quasinewton_optim. The reference checkout and HGFX v1.0.0 source were not patched. The entire instrumented fitting was compared to a previous uninstrumented native MATLAB public fit across **all 28 output fields**.

[Prespecification](PERF01D_FITMODEL_NESTED_OBJECTIVE_PRESPEC_2026-11-06.md) was committed as **addce9238e87f1a359c963d0b2990c0f9cb9eedf** before observing any new objective output: all 25 finite optimizer-history records from each of two real native MATLAB fits (50 occurrences), fixed binary HGF / unitsq_sgm, original zero-based subject index **7**, 128 trials, frozen exact data and all 15 configured transformed parameter values (free indices 12,13,14), no random restarts and unchanged optimization policies. The two 25-record histories are identical and each contains one repeated coordinate: **24 distinct parameter vectors**, yet all **50 specified occurrences are retained**.

Frozen HGFX SHA **4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27**, frozen MATLAB Toolbox SHA **2437f4dc241541072722a2695ddeca7b44d83dd3**, MATLAB R2026a Update 5. Original source six-real-fit run [42268256755](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268256755), genuine native MATLAB raw SHA-256 **2133b60ca7dcd51b85d93dfad109f715bd8fe35fa71c2bd84ff4a63cac672139**.

## Execution history (failed experiments preserved)

- [42289559328](https://github.com/ahmadkhanloo/hgfx/actions/runs/42289559328) at source SHA fc9064b1abf0bd410b0aba47cb832227d959b0c9: **FAILED before the nested callback** because MATLAB JSON parsing gave a different row/column orientation for the predeclared index array. All 12 synthetic tests, source hashes and 50-anchor generation passed. Partial artifact 13538034790. Commit bf58dfafc78045e53ea61d964ad69b586b76d3db normalized array orientation **without changing indices**.
- [42290004888](https://github.com/ahmadkhanloo/hgfx/actions/runs/42290004888) at source SHA bf58dfafc78045e53ea61d964ad69b586b76d3db: **FAILED before the nested callback** when MATLAB evalc attempted to create output variable fit in a nested-function static workspace. All original preflight checks still passed. Partial [artifact 13540248359](https://github.com/ahmadkhanloo/hgfx/actions/runs/42290004888/artifacts/13540248359). Commit **7cb33c660097112b53e11314beb783636e975cf4** predeclared the output variable; no model/optimizer/tolerance change.
- [42295760572](https://github.com/ahmadkhanloo/hgfx/actions/runs/42295760572) at exact source SHA **7cb33c660097112b53e11314beb783636e975cf4**: **SUCCESS**; 12/12 synthetic tests, 50/50 actual MATLAB private nested objective evaluations, hook called once, original optimizer delegated, complete 28-field instrumented-vs-native comparison passed. Both MATLAB and HGFX original source SHAs and fixed input bytes were verified. No timers.

[Complete artifact 13542495603](https://github.com/ahmadkhanloo/hgfx/actions/runs/42295760572/artifacts/13542495603), ZIP SHA-256 **c004076e22678c71559d4e1c571315017d6dc02665fc917c8b4401dcbaf46db5**. Exact file hashes:

| Archived file | SHA-256 |
|---|---|
| prespecified-50-original-anchors.json | 29d49a925660a64c4333e40866ef80c4f0bc871dea20b019b6fa224d4ca18c0f |
| real-matlab-nested-objective.json | 37be7f7a30fe62ce2e59cc8fd4483100ad6e59eb79791826478c31586736a5dd |
| nested-vs-hgfx-50-pair-diagnostic.json | f1d295ecf10fd88e3d6639c107d1fe05004423169de4b6261e22a25a3a228e42 |

## Observed direct private MATLAB objective vs frozen HGFX evaluate_free

| Observation | Result |
|---|---:|
| Predeclared / successfully evaluated anchor occurrences | **50 / 50** |
| Distinct free vectors (no duplicate discarded) | 24 |
| Exactly zero scalar objective differences | 36 / 50 |
| Nonzero scalar objective differences | 14 / 50 |
| Largest scalar objective absolute difference | **2.842170943040401e-14** |
| Largest difference in MATLAB-output ULPs | **2 ULPs** |
| Maximum ratio to pre-existing **final-parameter** tolerance as a *descriptive lens only* | **9.022305120778346e-09** |
| Actual fresh MATLAB nested objective vs stored original MATLAB optimizer objective history | **50 / 50 equal** |
| Instrumented vs native MATLAB public 28-field output tolerance | **0 failed fields** |
| Instrumented vs native MATLAB 28-field bitwise binary64 | **all 28 exactly equal** |

For each original 25-anchor history individually, 7 pairs differ by at most 2.842170943040401e-14. The old final-vector tolerance shown above was NOT a predefined objective-value acceptance threshold; it was used solely as a scale. The 28-field **binary64 equality** shows that in this instance instrumentation did not alter the original MATLAB public fitting outputs.

## Scientific interpretation and exact outstanding gate

This provides direct source-faithful evidence that the actual frozen MATLAB fitModel nested scalar objective and HGFX evaluation **nearly coincide at all 24 original saved free vectors**. It makes a large objective-formula disagreement at those points an unlikely explanation, but **does not prove** equality for gradient, BFGS, line-search candidate vectors not in the saved history, nor prove global optimizer or scientific-model equivalence. It neither establishes reference-science limitation nor grants a retrospective protocol relaxation.

Historical original public 64-subject full fitting remains **63/64 SCIENTIFIC NONPASS**, subject index 7 with 4 traj.mu and 4 traj.muhat failures. All eight previous real same-runner MATLAB/HGFX fitting comparisons still violate original trialwise tolerances; 28 original benchmark workloads remain **16 review-pending / 12 blocked**, with six originally primary CPU cells ineligible. There is **no independent scientific reviewer verdict** on issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88). PERF-01C **NOT FROZEN**, PERF-01E–H **NOT RUN**, no benchmark timing, speedup or physical GPU claim.

**Next scientific step:** an independent reviewer must examine the original objective/gradient/BFGS/termination and new real nested-objective source evidence, decide implementation vs numerical optimizer vs scientifically supported reference limitation, and prospectively approve or block revised eligible workload/timing contract. This author-side result is an engineering diagnostic, NOT an independent sign-off.
