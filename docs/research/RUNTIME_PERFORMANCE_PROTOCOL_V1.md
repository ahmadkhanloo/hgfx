# HGFX–MATLAB Runtime Benchmark Protocol (prospective)

Date authored: 2026-11-04  
Protocol ID: `hgfx-matlab-runtime-1`  
Status: **SPECIFIED / NOT FROZEN / NOT EXECUTED**  
Purpose: determine whether, where, and by how much HGFX is faster than the frozen MATLAB HGF Toolbox, without converting historical scaling or numerical-parity evidence into a performance claim.

## 0. Authority and boundaries

- Product under test: immutable `hgfx==1.0.0`, tag `v1.0.0`, commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Run from a verified isolated install rather than importing the mutable `main` checkout. If future 1.1.x performance is investigated, use a distinct comparator row and versioned protocol.
- MATLAB oracle: **HGF Toolbox 8.2.0**, commit `2437f4dc241541072722a2695ddeca7b44d83dd3`; capture the **actual** MATLAB release, OS, CPU and toolbox path at execution.
- Prior paper protocol `paper/reproducibility/PAPER_PROTOCOL.md` (`hgfx-paper-protocol-1`) is frozen and explicitly excludes a headline performance claim. **This document does not amend or retroactively activate that paper protocol.** If results are to be used as a headline in the computational-statistics manuscript, first freeze a separate revised paper protocol and link it to the benchmark evidence.
- Historical M17 H100 timing, M18 recovery failures, M19 release freeze, T4 correctness evidence, historical CI artifacts and case-study experimental records are immutable. M17 recorded *HGFX GPU scaling*, **not** MATLAB-vs-HGFX acceleration.
- This is **new post-v1 research**, with a separate gate `PERF-01`; historical milestone numbering and meanings do not change.
- No comparative runtime result has been generated or validated by authoring this plan.

## 1. Questions and claims, decided before observing results

**RQ-P1 — matched CPU execution:** On exactly matched model/data/precision/workflow, how does the MATLAB CPU implementation compare with HGFX compatibility CPU (and, only where parity is verified, JAX fast CPU)?

**RQ-P2 — practical acceleration:** On one host, what are wall time and fits/second for MATLAB's supported CPU workflow versus a scientifically validated HGFX JAX CPU/GPU batch workflow? This is an **end-to-end workflow/hardware comparison**, not a claim that equal optimizers or CPU/GPU hardware have equal resources.

**RQ-P3 — compilation and scaling:** What are first-use startup/compile costs, subsequent steady-state latency, host/device transfer costs, and batch throughput on 1 and 2 physical GPUs?

**RQ-P4 — real-case applicability (conditional):** Can a separately validated, complete published case study be repeated on both packages using the actual paper's model, response, data and preprocessing? Do **not** import Pain/SPIRL/other case studies into this benchmark before their scientific replication gate passes.

Permitted end-state labels: `FASTER_WITHIN_VALIDATED_SCOPE`, `SLOWER_WITHIN_VALIDATED_SCOPE`, `MIXED_RESULTS`, `NO_CLEAR_DIFFERENCE`, `NOT_DIRECTLY_COMPARABLE`, `BLOCKED_ENVIRONMENT`, `BLOCKED_SCIENTIFIC_PARITY`, or `NOT_RUN`. No general, unqualified statement that “HGFX is faster than MATLAB” follows from one favorable cell.

## 2. Comparators and strict semantic scope

| ID | Implementation / hardware | Question | Valid comparison |
|---|---|---|---|
| M-CPU | MATLAB Toolbox 8.2.0 on CPU, binary64 | Frozen reference baseline | M-CPU versus H-COMP on an identical workload |
| H-COMP | HGFX 1.0.0 compatibility mode on **same CPU** and binary64 | Reference-compatible CPU cost | Only exactly matched operations and returned outputs |
| H-JCPU | HGFX 1.0.0 JAX fast mode on **same CPU**, JIT enabled, binary64 | Effect of different execution engine | Forward/objective only after exact-scope scientific output gate |
| H-GPU1 | HGFX 1.0.0 JAX fast mode on one physical GPU, binary64 | Accelerator workflow | Label cross-device; also compare to H-JCPU |
| H-GPU2 | HGFX 1.0.0 on two physical GPUs, binary64 | Scaling | Compare to H-GPU1 on same host and data |

Existing source surfaces to audit before runner implementation: `src/hgfx/compat/fit.py` (`fit_model`), `src/hgfx/compat/fitting.py`, `src/hgfx/gpu/engine.py` (forward/objective, hgf/ehgf/uhgf update types), `src/hgfx/gpu/fitting.py`, `src/hgfx/gpu/batch_engine.py`, `scripts/benchmark_m17_multi_gpu.py`, and MATLAB `fitModel` / `quasinewton_optim`.

**Optimizer caveat:** MATLAB `quasinewton_optim` and HGFX's JAX fast BFGS are different algorithms; neither matching a fixed iteration budget nor matching the final objective establishes optimizer identity. Matched-optimizer comparison must use the validated **compatibility** route. Fast fitting is separately reported as a *different-algorithm completed-workflow comparison*, only if output/parity, converged-case and failure-accounting gates pass. Otherwise mark `NOT_DIRECTLY_COMPARABLE`, not “fast fit speedup.”

`pyhgf==0.3.2` is **out of scope** for the MATLAB-vs-HGFX speed claim. It may receive its own prospective protocol only after the frozen pyhgf semantic mapping gate is satisfied.

## 3. Frozen-candidate workload matrix (must not be trimmed after results)

Dataset construction, exact model configs, start vectors and serialized file hashes must be committed in a versioned `benchmarks/runtime_v1/inputs_manifest.json` **before timed runs**. Do not derive inputs in timed regions. A deterministic generator may use NumPy `Generator(PCG64(seed=20261104))`, but the **exported files**, not an assumption of cross-language RNG stream equivalence, are authoritative. Both MATLAB and HGFX load the same canonical arrays. Required columns/arrays: trial-by-trial input `u`, response `y`, mask, parameter/prior/config serialization, start vector, subjects, model ID, observation ID, and SHA-256. First dry-run checks all workload sizes, stable objectives and semantics; failures remain in the manifest.

### Primary CPU matrix — exactly 9 cases

| Scientific model / observation | Trials | Stage | MATLAB vs HGFX |
|---|---|---|---|
| `hgf_binary` + `unitsq_sgm` | **128, 512, 1024** | forward/trajectory (3 cases) | M-CPU / H-COMP; H-JCPU if output gate passes |
| same | **128, 512, 1024** | fixed-parameter full objective and per-trial likelihood (3 cases) | M-CPU / H-COMP; H-JCPU if output gate passes |
| same | **128, 512, 1024** | single-start complete compatibility fitting (3 cases) | M-CPU / H-COMP, not fast BFGS |

All nine primary cases are predeclared. No post hoc selection of only favorable horizons or stages is allowed. If `fitModel` and `fit_model` differ in Hessian/LME/statistics returned, add identical postprocessing or clearly split `optimizer-only` from `full fitModel`; **do not compare a full MATLAB fit to an HGFX objective-only or optimizer-only call**. The exact timed boundaries and code entry points are frozen in the runner manifest.

### Secondary scientific coverage (not substituted for primary failures)

- `ehgf_binary` and `uhgf_binary` with the matching `unitsq_sgm` observation, at **128, 512, 1024 trials** for forward and objective, on matched CPU and eligible fast mode, **only when the exact model mapping and parity gate are satisfied**. All 12 predeclared cells retain an explicit status even when blocked.
- Robustness: at least one predeclared ignored/irregular-trial pattern for `hgf_binary` at 512 trials. Treat as a separate stratum; do not replace the regular trial results.
- Published real-data case study is an *extension* behind its own complete scientific gate and independent protocol amendment; source, model, original software environment, license, data and participant denominator must be known. No case-study runtime is promised before eligibility is established.

### Practical throughput matrix

For `hgf_binary + unitsq_sgm`, exactly **1, 16, 64 subjects × 128, 512 trials** (6 cells). Each subject has one fixed start (zero extra random restarts); all subjects, failures, total attempts and successes must be counted. Report MATLAB serial `fitModel`-loop and HGFX compatibility serial loop as the matched-workflow baseline. Report H-JCPU, H-GPU1 and H-GPU2 batched **only if relevant fitting parity gates pass**, with their different optimizer clearly labeled. Optionally report MATLAB `parfor` as a **separate** licensed/validated baseline, never silently substitute it for the serial baseline. Report full result materialization and fit statistics consistently.

Resource policy: MATLAB and HGFX CPU use the **same physical host**, fixed CPU affinity and measured threading; the primary CPU comparison fixes **one computational thread** for both where verified possible, with a separately labeled realistic/default multi-thread run if resources permit. Capture BLAS/OpenMP/MKL/JAX/XLA and MATLAB worker/thread settings. Do not call `-singleCompThread` and then describe MATLAB as its default performance. GPU tests use the same host, CPU and system storage as far as possible, with model, VRAM, driver, CUDA, JAX/JAXLIB and device assignment recorded.

## 4. Scientific integrity gate — must precede timing interpretation

Every cell is classified **before looking at its relative speed**:

1. Same scientific model and observation model, identical data/masks/trial count, parameter order/transforms/prior values, fixed/free indices, optimizer initial points and restart/selection rules when applicable.
2. Binary64 MATLAB and HGFX JAX x64. Capture the actual dtype and active backend; no f32 substitutions.
3. MATLAB-versus-HGFX fixed-parameter trajectories, likelihood and objective are compared against **existing relevant frozen numerical policies/golden tests**, with a prospective exact-cell tolerance map committed *before* benchmarking. No threshold relaxation to obtain performance eligibility.
4. Fitting: compare final objective and trajectories, termination, iterations, fitted parameters and convergence/failure status. Respect documented reference limitations and model-selection limitations; do not require identical optimization paths unless a compatible optimizer is the tested claim.
5. Verify all outputs are finite where expected and every result is synchronized/materialized before a timer ends. On GPU use `block_until_ready()` on all relevant result leaves.
6. If differences or incomplete correspondence remain, classify the cell as `BLOCKED_SCIENTIFIC_PARITY`, `NOT_DIRECTLY_COMPARABLE` or `INSUFFICIENT_REFERENCE_EVIDENCE` and preserve its timing **only as diagnostic**. Never publish it as a validated speedup.

The current v1 scientific acceptance status does **not** automatically prove parity on newly generated workloads; each new cell requires its own check. Reference limitations never become scientific PASS just because runtimes agree.

## 5. Timing contract

**Never conflate these numbers:**

- **Startup/environment**: clean subprocess (MATLAB startup + toolbox path; Python startup + imports); isolated and shown separately. Do not include process startup in only one implementation.
- **Cold JAX first invocation and compilation**: use a fresh process or verified cache reset; separate Python import, `jit` compile, execution and transfer as observable. Repeat **5 independent fresh-process samples**. MATLAB's corresponding first-call overhead reported alongside but **not mislabeled JIT**.
- **Warm execution**: load canonical inputs and prepare configuration outside timers; **3 untimed warmups per case and implementation**, followed by **10 paired blocks**, two observed samples per implementation per block (**20 observations per implementation/cell**). Alternate order via ABBA / BAAB, using the predeclared block-order seed `20261104`. `time.perf_counter_ns` on Python, `tic/toc` on MATLAB; retain every raw elapsed time and block pairing. Benchmark hosts should be idle or background contention logged; noisy blocks are **not discarded** after inspecting speed.
- **Transfer**: one measured host→GPU transfer and one GPU→host result materialization per matching workload; keep device-resident `compute-only` and **end-to-end** timing separate.
- **Full fit**: complete all optimizer/statistics/result-materialization steps included in the matched workflow; separately measure forward, fixed-objective, optimizer core and postprocessing only when APIs expose consistent boundaries. Report unsuccessful attempts; never calculate throughput using only successful results without also reporting attempted fits.
- **Throughput**: subjects/sec = all submitted subjects / complete wall-clock seconds; fits/sec = all attempted starts / complete wall-clock seconds. Include schedulers, launch, synchronization and result materialization; report memory usage/peak RSS and GPU peak allocation if measurable.

Each paired block runs on the same machine, in a controlled order without concurrently benchmarking the two implementations. Pin power/CPU governor if feasible, and record turbo/frequency and temperature policy. A shared/contended system is allowed if labeled and its limitation is quantified; a controlled idle repeat is preferred for paper claims.

## 6. Statistics and predeclared decision rule

For every eligible paired cell, report MATLAB median wall time, HGFX median wall time, IQR, all measurements, attempts/failures, and speedup `S = T_MATLAB / T_HGFX` (values above 1 favor HGFX). Estimate speedup from the **median of paired-block ratios**, where each block's ratio uses the median of its two measured MATLAB times divided by the median of its two measured HGFX times. Compute **paired, block-resampled 95% percentile bootstrap intervals** with exactly 10,000 resamples and `seed=20261104`; report raw count 10 blocks. Flag the bootstrap intervals as descriptive and uncertainty-limited for such a small block count.

Predeclare **10%** as the minimum material runtime improvement, not as a scientific-correctness threshold:

- Per-cell `FASTER_WITHIN_VALIDATED_SCOPE` only if exact-scope scientific gate passes, ratio point estimate is greater than 1.10 and the **95% bootstrap lower bound is greater than 1.10**.
- Per-cell `SLOWER_WITHIN_VALIDATED_SCOPE` only if scientific gate passes and the **95% upper bound is below 1/1.10**; otherwise `NO_CLEAR_DIFFERENCE` or a qualified smaller effect.
- Mixed status/uncertainty is not silently relabeled PASS.
- The **predeclared primary CPU summary** is an **equal-cell-weighted geometric mean** of the nine primary M-CPU / H-COMP speedup ratios. Block-resample the entire paired nine-cell matrix (preserving block alignment where executable) to obtain a 95% CI. A narrow, explicit headline “HGFX compatibility CPU faster on the preregistered standard binary HGF matrix” is permitted only when: **all nine cases are eligible**, summary lower CI > 1.10, at least **7 of 9** cell lower CIs > 1.00, and no primary cell has an upper CI < 1.00. Otherwise the headline is `MIXED_RESULTS` / `NO_CLEAR_DIFFERENCE` / blocked, with the full table shown.
- These 95% per-cell intervals are **descriptive**, not multiplicity-controlled familywise significance. If inferential p-values or multiple positive cell claims are added to the paper, apply and disclose a **prospectively specified** multiple-testing procedure (e.g. Holm); do not represent uncorrected CIs as multiplicity-adjusted.

A GPU speedup (MATLAB CPU / HGFX GPU) must be explicitly labeled **cross-hardware workflow speedup**; do not call it “HGFX algorithm is X times faster than MATLAB on the same CPU.” Speedups for different algorithms, different successful-fit rates, or materially different outputs have no valid single-number performance interpretation.

## 7. Phased execution and acceptance gates

- [ ] **PERF-01A / audit**: verify exact v1 source installation, MATLAB version/license/toolbox commit, CPU/GPU host access, supported public entry points and matching output scope. Record known blockers, particularly any MATLAB/H100 access gap.
- [ ] **PERF-01B / fixture freeze**: write input/export scripts, deterministic canonical datasets, fixed configs/starts/threshold mapping, environment and SHA-256 manifest. Verify all primary and secondary workload cells exist in manifest; separate exploratory smoke results, clearly labeled `NON-PAPER`.
- [ ] **PERF-01C / protocol freeze**: independent scientific and benchmarking-method review; commit immutable versioned protocol, input hashes, runner code and workload registry to Git **before any final comparative timing**. Record SHA and change-control policy. This authored version is **NOT** frozen yet.
- [ ] **PERF-01D / preflight**: prove source identity, byte-identical paired inputs, model/workflow mapping, objective/forward scientific gates, and fitting parity/failure accounting; fail-closed for ineligible cells.
- [ ] **PERF-01E / matched CPU**: execute 9 primary and 12 secondary cells as predeclared; preserve all failures and raw logs; analyze independently.
- [ ] **PERF-01F / accelerator**: run six batch cells and 1-/2-GPU scaling only on actual physical GPUs with explicit allocation/residency, GPU-load snapshot and synchronization.
- [ ] **PERF-01G / reproducibility**: on a clean environment rerun an a priori selected representative cell (the 512-trial objective) and the 16-subject/512-trial fit; log version changes, exact reproduction match and any uncertainty. Do not re-pick the check cell after seeing results.
- [ ] **PERF-01H / paper evidence**: independently review logs, failure counts, classification and script-generated plots; freeze `RESULTS_MANIFEST` and append a new paper protocol revision if headline performance is included. Do not edit `hgfx-paper-protocol-1` in place.

No gate is a PASS solely because the scripts run. Missing MATLAB, absent x64 GPU support, missing paired mapping, or unstable scientific outputs mean **BLOCKED**, not success.

## 8. Required artifacts and schema

Suggested paths (new; do not overwrite frozen v1 or previous paper evidence):

```text
benchmarks/runtime_v1/
  README.md
  inputs_manifest.json                 # frozen canonical inputs and hashes
  protocol_lock.json                   # version/SHA and fixed decision policy
  generate_inputs.py
  matlab/run_benchmark.m
  python/run_benchmark.py
  validate_paired_parity.py
  analyze_benchmark.py
  raw/<run-id>/{matlab,hgfx_compat,hgfx_jax_cpu,hgfx_gpu}.jsonl
  environment/<run-id>.json
  results/<run-id>/summary.csv
  results/<run-id>/summary.json
  results/<run-id>/fig_runtime_by_stage.{pdf,png}
  results/<run-id>/fig_speedup_ci.{pdf,png}
  results/<run-id>/fig_batch_throughput.{pdf,png}
  results/<run-id>/fig_cold_vs_warm.{pdf,png}
  RESULTS_MANIFEST.json
```

Each raw record requires at least:
`protocol_id`, `protocol_sha256`, `hgfx_source_sha`, `matlab_toolbox_sha`, `matlab_release`, `run_id`, `timestamp_utc`, `host_id`, `hardware`, `runtime_versions`, `input_sha256`, `model`, `observation`, `stage`, `trials`, `subjects`, `optimizer_name`, `optimizer_settings`, `start_sha256`, `device`, `dtype`, `timing_mode`, `warmup_count`, `block_id`, `order`, `elapsed_ns`, `wall_seconds`, `sync_policy`, `iterations`, `termination`, `objective`, `parity_status`, `status`, and `error` when applicable. Use `null` and a reason when a field is not applicable; never fabricate numbers.

Outputs must include:
1. complete eligible/blocked matrix with denominators and checksums;
2. wall time, speedup and 95% intervals by stage/horizon/implementation;
3. compiler/startup and transfer overhead, warmup cost and per-subject throughput;
4. GPU device residency, memory and actual contention;
5. matched-optimizer versus different-optimizer and same-device versus cross-device labels;
6. machine-generated paper tables/plots with command and artifact SHA-256;
7. an independent review report verifying every numerical manuscript claim against raw results.

## 9. Decision and change-control policy

- The benchmark may be **executed only after PERF-01C is frozen**; currently `NOT_FROZEN / NOT_EXECUTED`.
- Pre-freeze feasibility modifications must be explicitly logged and committed; after final results start, changing matrix, starts, random data, thread policy, warmups, repetitions, outlier policy, thresholds or definition of a timed step requires `hgfx-matlab-runtime-2` and preservation of all v1 evidence.
- An ineligible/missing cell remains present with its failure reason. No model/horizon can be removed because it is slow or scientifically inconvenient.
- The final manuscript must distinguish **scientific parity**, **implementation execution time**, **optimization algorithm choice**, and **hardware acceleration**. No paper figure/result is added before its evidence is executed and frozen.

**Current outcome: protocol authored; no benchmark timing or MATLAB-vs-HGFX speedup claim exists yet.**
