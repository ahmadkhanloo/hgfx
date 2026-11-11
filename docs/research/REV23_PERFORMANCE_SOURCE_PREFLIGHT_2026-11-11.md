# REV-2.3 — performance and resource benchmark source-only preflight (2026-11-11)

**Classification: PREPARATORY SOURCE AUDIT COMPLETE; REV-2.3 SCIENCE / TIMING NOT RUN; PERF-01C BLOCK_FREEZE remains unchanged.** This is an author-side documentation audit, not a signed independent benchmark review and not an amendment or execution authorization for either benchmark protocol.

## 1. Current authoritative scopes

- [Computational Statistics revision plan](../planning/COMPSTAT_REVISION_PLAN.md), REV-2.3 (C4), is the active article revision task because author D1=A supersedes the prior software-venue retarget. The plan calls for: forward T={128,1024,8192,65536}, single compatibility fit T={128,512}, batch B={1,32,256,1024} at T=256, and the USD/CHF fit. MATLAB 8.2.0 CPU, HGFX compatibility CPU, JAX CPU and one physical JAX GPU; one warm-up and five timed repeats, median/IQR, separately measured compilation, memory and float64.
- An **independent, older, non-frozen proposal**, [RUNTIME_PERFORMANCE_PROTOCOL_V1.md](RUNTIME_PERFORMANCE_PROTOCOL_V1.md), protocol ID `hgfx-matlab-runtime-1`, requests *different* experimental cohorts: nine primary binary HGF CPU cells (forward/objective/fit, T={128,512,1024}); 12 additional eHGF/uHGF forward/objective cells, six batch-throughput cells (B={1,16,64}, T={128,512}), and ten paired blocks of two repeats with CPU affinity/threading and 1- and 2-GPU modes.
- These are **not interchangeable protocol revisions**. Their workload sets, repetitions and backend matrices differ. A 5-repeat REV-2.3 result must **not** be silently presented as the 10-block / 20-repeat PERF-01E experiment, and an eligibility failure on one protocol cannot be disguised by selecting cells from the other.
- Existing [PERF-01 Issue #86](https://github.com/ahmadkhanloo/hgfx/issues/86) and [PERF-01C Issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88) require independent parity/eligibility, resource boundary and protocol freeze **before** final comparative timing; `PERF-01C=BLOCK_FREEZE` remains in force. REV-2.3 is therefore **not authorized for paper-speed timing** by this source audit.

## 2. Frozen software identities and evidence status

| Item | Verified source reference / current implication |
| --- | --- |
| MATLAB reference | HGF Toolbox **8.2.0**, frozen Git commit `2437f4dc241541072722a2695ddeca7b44d83dd3`; actual MATLAB release and same-host CPU capabilities must be recorded at a future run |
| Published HGFX | `v1.0.0`, source commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; only its verified Wheel can support claims about this release |
| Mutable revision checkout | `pyproject.toml` on `compstat-revision` declares **1.1.0b1**; running its import path would be *development-line* evidence and cannot be substituted for a v1.0.0 benchmark |
| Existing GPU evidence | `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` documents physical GPU numeric backend checks, not elapsed-time comparisons or verified 1.0.0 paper-speed evidence; do not equate GPU correctness with GPU acceleration |
| Existing PERF-01 scientific evidence | Issue #88 records some fixed-vector eligible CPU comparisons but blocked long-horizon/fit cells; independent PERF-01C review is still OPEN/BLOCKED |
| Existing REV-2.2 USDCHF | Two concurrent released-v1.0.0 MATLAB/HGFX paired D08 runs had direct `traj.epsi` FAIL (4/1228, 3/1228), incomplete stop/warning data and exhausted their original D08 science execution budget; they supply **no** automatic benchmark-timing eligibility |
| Historical manuscript protocol | `paper/reproducibility/PAPER_PROTOCOL.md` stays frozen; previous non-performance evidence is not a speedup estimate |

**Path verification limitation:** the revision branch has no file at `evidence/revision/protocols/REV-2.3_PROTOCOL.md` at the time of this audit. Expected standalone exact-input benchmark manifests and timing outputs have **not been verified** on this branch. The historical issue references some artifacts under other branches/Actions; their availability or completeness is **not independently audited in this task**, so no universal absence claim is made.

## 3. Mandatory next steps before REV-2.3 timing

1. **Resolve protocol precedence prospectively:** adopt a distinct, explicitly named `REV-2.3` scientific protocol implementing its entire original fixed task matrix, or formally document a separately author-approved change to that scope. Keep PERF-01's independent 9-primary/6-batch design separately identified; do not merge protocols retrospectively. The REV-2.3 plan's one-warmup/five-repeat rule and existing PERF-01 plan's ten paired blocks must both retain their historical identities.
2. **Freeze actual comparability:** define per-cell scientific model, observation model, priors, fixed/free masks, data, starts, output parity contract and **complete** timing boundaries. Especially mark same-optimizer compatibility fits separately from different-optimizer JAX acceleration and the unresolved USDCHF D08 fitting discrepancy. Do not use pure optimizer time as if it were full `fitModel` on only one side.
3. **Freeze canonical inputs/manifest:** write exact arrays, seeds, SHA-256, configurations, software build/install verification, parameter ordering, exclusions (none), per-cell blocked/fail outcomes, and fixed timing order before execution. Predeclare missing MATLAB/GPU fallback without pruning planned rows.
4. **Independent eligibility review:** obtain explicit reviewer approval of protocol, runner methods, environment, thread/BLAS affinity, synchronization (JAX device blocking), transfer timing, JIT warmup vs steady state and resource logging. Resolve or retain PERF-01C `BLOCK_FREEZE`; do not bypass that gate by calling the same measurement REV-2.3.
5. **Execute exactly one frozen study only after authorization:** collect one warm-up/five timed repeats per eligible REV-2.3 cell (the original plan), median and IQR, compilation, peak memory, runtime hardware and version metadata. If MATLAB and Python CPU are on different hosts, report separately **without** a hardware-confounded speedup ratio. An unavailable physical GPU means `NOT_RUN/BLOCKED_ENVIRONMENT`, not simulated GPU validation.
6. **Preserve all ineligible cells and adverse results:** no speedup or paper figure until source/response scientific gate, fixed timing boundary, outlier policy, per-cell denominator and raw artifacts are independently reviewed. Existing failed/blocked PERF-01, REV-2.2, REV-2.4, M18/P3/PERF-01C outcomes remain unchanged.

## 4. Disposition

- **REV-2.3 PREPARATION:** source-and-scope audit performed; final execution protocol **OPEN / NOT FROZEN**; no timed experiments conducted in this task.
- **PERF-01C:** `BLOCK_FREEZE`; no reinterpretation of older tests.
- **Performance paper claim:** `NOT_ESTABLISHED` (neither faster nor slower).
- **Overall REV-2:** in progress; REV-2.1 human design gate open, REV-2.2 direct D08 fit discrepancy unresolved, REV-2.4 global NOT PASS, D2/D3 BLOCKED.
- **Review provenance:** repository documents, issue text, package metadata and archived GPU summary were inspected using GitHub file/issue access. No code or scientific input was executed, no actual hardware/runtime was probed, no full benchmark artifact hashes were recomputed and no signed independent reviewer approval was obtained.

This record prevents conflation of the two legitimate but scientifically different benchmark designs. It does not authorize numerical experimentation; the next concrete engineering artifact is a **prospective frozen REV-2.3 protocol and eligibility matrix**, subject to the existing author/reviewer gates.
