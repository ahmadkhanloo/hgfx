# PERF-01: Proposed prospective scoped benchmark protocol v2 (REVIEW DRAFT)

Authored: 2026-11-04  
Proposed protocol ID: `hgfx-matlab-runtime-2` (**NOT A LOCKED PROTOCOL**)  
Status: **DRAFT / UNAPPROVED / NOT FROZEN / NOT TIMED**  
Prerequisites: [original v1 specification](RUNTIME_PERFORMANCE_PROTOCOL_V1.md), [PERF-01D evidence](PERF01D_DIAGNOSTIC_EVIDENCE_2026-11-04.md), [all-subject evidence](../../benchmarks/runtime_v1/cohort_results/summary-41860187774.json), [independent review issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88).

This document is a **new, explicitly narrower prospective research question after scientific diagnostics but before any measured MATLAB–HGFX runtime outcome**. It does **not** rewrite, excuse or pass the original nine-case protocol; it may not be timed as final evidence until an independent reviewer verifies and freezes the complete protocol, case ledger, all runner sources and acceptance rules. It is not an amendment to the historical `hgfx-paper-protocol-1`.

## 1. Why a separate version is necessary

The original `hgfx-matlab-runtime-1` primary design predeclared nine standard HGF binary CPU cells: three stages (forward, fixed-vector objective, complete compatibility fitting) × three trial lengths (128, 512, 1024). The fixed input and prior start are invalid for **all 64** HGF subjects at **512** and **1024** trials **in both** implementations. MATLAB `fitModel` automatically resamples unstable starts, whereas HGFX 1.0.0 compatibility `fit_model` rejects the invalid default start.

Therefore **six of the original nine primary comparisons are ineligible**, so the original 9-cell aggregate `all eligible` speedup gate is **BLOCKED** before timing. This is a genuine recorded scientific eligibility result and may not be hidden, relabeled as a scientific pass or repaired by changing seeds, subjects, starts or horizons after observing it.

Independent frozen evidence establishing the original scopes:
- Trialwise 10 cells: [run 41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533).
- Full 128-trial fit, two other fit blocks: [run 41855647245](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855647245).
- 576 fixed-vector source cases: [run 41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774): 448 matched successful scalar objectives and 128 matching invalid paths.
- Exact 28-case author-side eligibility inventory: `benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json`: 16 diagnosis-compatible/review pending and 12 blocked. This inventory is not independent sign-off.

No MATLAB–HGFX speed was observed to inform the proposed narrower matrix. Scientific compatibility, not favorable runtime, is the stated basis for proposing it.

## 2. Scientific questions (distinct claims and explicit limitations)

**RQ2-A — One-horizon standard HGF CPU:** On the **unchanged 128-trial binary HGF subject zero**, does `hgfx==1.0.0` compatibility mode execute each exactly matched scientific task (forward, objective, complete fitting) faster, slower, or comparably to frozen MATLAB HGF 8.2.0 on the *same physical CPU host* with verified thread policy? No extrapolation to HGF 512 or 1024 trials.

**RQ2-B — eHGF/uHGF CPU workload:** Across **all twelve previously specified**, valid secondary `ehgf_binary` and `uhgf_binary` forward and fixed-objective cases at horizons **128, 512, 1024**, determine per-case runtime ratios on the *same physical CPU host*. No inference from these variants to standard HGF or to full fitting.

**RQ2-C — Cohort fit capacity (conditional):** On unchanged standard HGF **128-trial** first `1, 16, 64` subjects, compare MATLAB serial `fitModel` and HGFX serial compatibility `fit_model` **only if** every fitted subject in each denominator passes a prospectively specified exact-scope output, optimizer and failure-accounting gate. Track attempted, failed, converged and accepted fits separately, and do not replace subjects. No throughput speedup if scientific fitting parity differs or fails.

**RQ2-D — Accelerated different-algorithm pipeline (separate extension):** A real physical-GPU and JAX CPU batch experiment can only be reported as **cross-execution-engine/hardware scientific workflow throughput**, with a new self-contained locked acceptance and deployment manifest, matched model outputs and complete materialization. It is not a same-optimizer algorithm speedup and is **NOT AUTHORIZED** for this draft's CPU-only primary gate.

**Scope excluded:** standard HGF 512/1024 primary cells (remain visible as blocked in the v1 ledger), masked HGF 512, any paper case study without a separately completed replication gate, and Python/JAX `main` newer than `v1.0.0`. No `pyhgf` benchmark under this proposed version.

## 3. Locked **candidate** data and code identities

No runtime experiment may change:

- HGFX release tag `v1.0.0` / SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- MATLAB HGF Toolbox 8.2.0 / SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`; run MATLAB R2026a or record any prospectively reviewed release change as separate stratum.
- **Original unmodified** `benchmarks/runtime_v1/inputs/`, `inputs_manifest.json`, `configs/`, `resolved_configs_manifest.json`; checked SHA-256 in existing evidence. **Do not reconstruct a favorable new dataset for the original failed matrix.**
- Identical prior and transformed start vectors for forward/objective/fit; full free/fixed-index, observation, mask and precision contract verified.
- Same source-to-source *scientific* model family in each cell. `ehgf_binary` and `uhgf_binary` are not synthetic variants that count as extra standard-HGF data points.

## 4. Proposed primary and secondary status ledger (no speed claim)

| Stratum | Model/stage | Trials | Subjects | Prerequisite |
|---|---|---:|---:|---|
| A1 | Standard HGF forward | 128 | subject 0 | full trialwise evidence, independent review |
| A2 | Standard HGF fixed objective | 128 | subject 0 | exact MATLAB composition vs HGFX API, complete inputs/outputs |
| A3 | Standard HGF complete compatibility fit | 128 | subject 0 | full numerical/optimizer/postprocessing parity, same start and policy |
| B1–B6 | eHGF forward/objective | 128 / 512 / 1024 | subject 0 | exact same-model trajectory and objective parity, independent review |
| B7–B12 | uHGF forward/objective | 128 / 512 / 1024 | subject 0 | same as eHGF |
| C1 | HGF full fit, first 1 subject | 128 | subject 0 | fitted numerics and restart/termination match |
| C2 | HGF full fit, first 16 subjects | 128 | subjects 0–15 | 16/16 full scientific fit gates, no failures hidden |
| C3 | HGF full fit, all 64 subjects | 128 | subjects 0–63 | 64/64 full scientific fit gates, no failures hidden |

All A/B rows remain **REVIEW PENDING**, even though preliminary diagnostics are concordant. C2/C3 remain **BLOCKED PENDING FIT PARITY** until the all-64 full-fit experiment is actually assessed. The original 28-case ledger remains alongside this version's additional scoped questions; this version never changes the total or outcome of the original 28.

## 5. Matched timeable operations and CPU host policy (require reviewer sign-off)

Before any final timing, freeze runnable MATLAB and Python entry points, their exact source code SHA, measurement region, input initialization and output materialization:

- **Forward:** frozen MATLAB named perceptual model `(r,theta,'trans')` and matching HGFX compatibility `(u,theta,transformed=True)`, *both returning entire trajectory and inference-state arrays*, not cheap scalar proxies. Inputs, priors, config resolution and masks constructed outside both timers.
- **Objective:** MATLAB frozen perceptual + frozen observation `unitsq_sgm` + frozen `negLogJoint` prior/reduction terms versus HGFX `evaluate_objective`. MATLAB `negLogJoint` is a *nested private* function in frozen `core/fitModel.m`. The proposed independently scripted equivalent composition must be reviewed for equal numerical operations and output materialization. No calling a MATLAB full fit as the objective baseline.
- **Fit:** MATLAB public `fitModel` and HGFX public `fit_model` with the same optimizer compatibility policy, all fit statistics (including Hessian, covariance, LME, AIC/BIC, residuals, predictions and trajectories), no extra starts or narrowed end-point selection. The MATLAB implementation prints parameter/results text unconditionally whereas HGFX does not. Reviewer must choose **before timing** either literal public-workflow wall time with this asymmetry **disclosed**, or a separately implemented and parity-checked output-neutral *full computational task*; do not quietly use MATLAB `evalc` while leaving Python stdout unchanged and call it matched algorithm compute time.
- **CPU:** both processes on the identical runner/hardware with recorded CPU model, core/affinity, microcode, RAM, OS, Python, MATLAB, binary64 dtype, NumPy/BLAS/OpenMP/MKL/JAX/XLA versions, exact threading environment, warmup, thermal/power policy, and background contention. Do not assume `maxNumCompThreads(1)` proves complete thread equality.
- JAX first-use compilation, synchronization and transfer overhead belong to separately labeled exploratory strata, not a fake faster compatibility CPU runtime.

The existing `PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md` is the source audit; no runnable timed wrappers exist or are approved under this candidate.

## 6. Prospective sampling and thresholds (retain v1 policy)

Only after PERF-01C independent review, SHA-locked runners and a versioned protocol lock:

- Three **untimed** warmups, then **ten paired blocks**, two samples from each implementation per block, in a reproducible ABBA / BAAB arrangement with block-order seed `20261104`. Do not discard slow/noisy samples ex post.
- Cold/startup and JAX compilation must be in separate experiments, five independent fresh-process samples; no asymmetrically included process startup.
- Per-block paired median MATLAB/HGFX ratio, then median ratio and paired **10,000-resample** percentile-bootstrap **95% CI**, bootstrap seed `20261104`.
- Preserve the v1 **1.10x** material speed threshold and frozen unchanged rule: positive per-cell `FASTER_WITHIN_VALIDATED_SCOPE` only when objective scientific eligibility passes, point ratio >1.10 and lower 95% CI >1.10; `SLOWER_WITHIN_VALIDATED_SCOPE` if CI upper <1/1.10, otherwise qualified result / insufficient precision.
- Do not compute a **new combined fifteen-cell headline aggregate** by cherry-picking compatible cells after seeing the original failures. Model-specific A and B summaries (if proposed) require an independently preregistered full family-wide decision rule and multiplicity policy **before** final measurements. Otherwise report **all 15 individual results, no pooled faster claim**.
- C1/C2/C3 are overlapping nested subject cohorts; do not treat them as 81 independent subjects or independent confirmations.
- Preserve every failed attempt and all paired time blocks; positive and negative outcomes get the same report prominence.

## 7. Not-yet-satisfied scientific / statistical / software gates

1. **Independent reviewer** must verify original evidence and this *new scope*, exact API boundaries, MATLAB version, noise/affinity controls and frozen eligibility before any timer.
2. All-64 **complete fitting** review must classify every subject, including optimizer iteration/termination, numerical trajectory and inference results and reference sensitivity, not just per-subject objective. Proposed evidence: a separate diagnostic script/CI; **no speed**.
3. Freeze immutable **candidate v2 protocol + source hashes + runner scripts + case manifest + predeclared analysis + independent reviewer approval** in one new linked lock. No changes to old `hgfx-matlab-runtime-1`, old M17/M18/M19 evidence, or `hgfx-paper-protocol-1`.
4. Every gate must report `PASS`, `IMPLEMENTED_NOT_VALIDATED`, `BLOCKED`, `OPEN` or `NOT_RUN`; a green code-execution CI does not itself establish scientific equivalence.
5. If no independent reviewer is available, mark PERF-01C `BLOCKED_PENDING_EXTERNAL_REVIEW`, not `PASS`. If matched hardware/threading cannot be established, retain environment blocker rather than relying on incomparable host timings.

**Current verdict: DRAFT ONLY — no scientific-performance gate passed, no timings executed, and no CPU/GPU speedup established.**
