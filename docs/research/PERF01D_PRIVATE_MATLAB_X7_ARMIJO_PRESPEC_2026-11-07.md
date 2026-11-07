# PERF-01D — frozen private-MATLAB objective at two original x6/T6 source candidates (2026-11-07)

**PRE-EXECUTION EXPERIMENT CONTRACT. This follow-up is post-result-selected exploratory research, not a scientific acceptance gate, fitness waiver, or prospective timing protocol.** Commit this contract before running the new real MATLAB evaluations. No new private-candidate values have been observed under this contract at protocol creation.

## Locked incident, provenance, and selection

- Original public 64-subject `fitModel`/`fit_model` is **63/64 NONPASS**, zero-based subject **7**: four `traj.mu` and four `traj.muhat` entries exceed the *original* tolerance. Preserve [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), 15/16 NONPASS, and every later failed paired experiment unchanged.
- HGFX v1.0.0 frozen commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; HGF Toolbox 8.2.0 frozen commit `2437f4dc241541072722a2695ddeca7b44d83dd3`; use **MATLAB R2026a**, unchanged `hgf_binary` / `unitsq_sgm`, original subject-7 128 trials, original priors/masks/free indices `[12,13,14]` and start `[-3,-6,3.871201010907891]`.
- Original full BFGS history [run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), HGFX raw SHA-256 `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`, MATLAB raw SHA-256 `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.
- Same-x genuine private MATLAB Ridders observations [run 42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614), paired source report SHA-256 `2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d`.
- Single-step *HGFX-objective* algebraic candidate archive [run 42366705874](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874), member `source-same-state-two-gradient-candidates.json`, SHA-256 **`b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144`**. Its origin was the already-inspected and post-hoc-selected maximum gradient discrepancy, original **HGFX-own** record 6. This is not an independent selection.
- Original source x6 exactly `[-1.1621811570388512,-6.37816839506084,-0.23738383160834042]`; original `f(x6)=108.28848680066957`. **Do not substitute MATLAB-own record-6 x/T6**, which are different.

## Single new source-only experiment: three private-objective calls

1. Download the **exact immutable one-step candidate artifact** and verify its SHA-256, frozen source SHA strings, original failed-fit identity, x6, `T6`, index 6, and two keys under `same_T6_and_x6_one_step_directions`. Verify pinned original failed evidence and other linked raw SHA as available; never regenerate candidate coordinates using an altered algorithm.
2. Invoke unchanged frozen MATLAB `fitModel` with the original original `quasinewton_optim_config` and temporary *harness-side* `opt_algo` callback that receives the **actual private nested objective**. Inside the callback evaluate the original objective, without any gradients or optimization at the candidates, at exactly **three** binary64 vectors and in fixed order:
   - archived original HGFX-own `x6`;
   - candidate `source_next_full_step_free_x` produced from original HGFX gradient and saved HGFX `T6`;
   - candidate `source_next_full_step_free_x` produced from measured genuine private MATLAB gradient **at that same original HGFX x6/T6**.
   Then delegate exactly once to the unmodified native optimizer. Do not patch frozen MATLAB/HGFX sources, numerical options, starts, or trial inputs.
3. Separately execute the same native MATLAB public fit with no callback; compare the stable original public output fields with `isequaln` as a strict neutrality test. Failure of callback neutrality invalidates the *new probe*, **not** historical scientific evidence.
4. For each candidate, report raw MATLAB-private `f(x_candidate)`, exact baseline `f(x6)`, original cached **unclipped** `gradient' * (-T6*gradient)` Armijo delta RHS (`1e-4 * slope`), delta LHS `f(x_candidate)-f(x6)`, and strict original `lhs < rhs` Boolean. Also retain prior *HGFX*-objective candidate values distinctly, never claim that prior HGFX evaluations were private-MATLAB evaluations. Log numerical finite/realmax/nonfinite/exception status for **all three calls**, including any failing case, without filtering.
5. Record host/software versions, exact commit/run ID and SHA-256 of the newly produced full raw report in an uploaded artifact regardless of success/failure. Fail closed on any missing/changed source candidate, non-neutral public fit, wrong callback count or modified source identity.

## Interpretation controls and gate status

This is a **new observation** at *post-result-chosen* coordinates. Descriptive Armijo Booleans on the actual private MATLAB objective may agree or differ; record **both**, even if that contradicts earlier HGFX-objective algebraic Armijo results. They are still **counterfactual candidate evaluations on HGFX-own x6/T6**, **not** the recorded original MATLAB-own BFGS private internal branch decisions. The original MATLAB-own x6/T6 and subsequent optimization path are distinct.

No fitting tolerance, workload, optimizer, data, reference source, or acceptance policy may change after observing the outcomes. No path-basin claim is to be promoted from this local study into a proven causal explanation. Retain original source **63/64 SCIENTIFIC NONPASS**, PERF-01C **OPEN / NOT FROZEN**, PERF-01E–H **NOT RUN**, independent review **NOT RECEIVED**, and **no CPU speedup / GPU / paper-performance claims**. Independent reviewer #88 must adjudicate provenance, one-step source formula, numerical interpretation, and original failed evidence before any gate change.
