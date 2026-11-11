# REV-2.3 (C4) — prospective performance and resource study

**Protocol status: DRAFT / NOT FROZEN / NOT AUTHORIZED FOR SCIENTIFIC TIMING**  
**Date:** 2026-11-11  
**Study identity:** `compstat-rev23-performance-1`  
**Authority:** [Computational Statistics revision plan](../../../docs/planning/COMPSTAT_REVISION_PLAN.md), section REV-2.3. [Preflight](../../../docs/research/REV23_PERFORMANCE_SOURCE_PREFLIGHT_2026-11-11.md). Human independent eligibility/benchmark-method approval required before final timing. No numerical measurement is made by creation of this document.

## 1. Scientific questions and null interpretation

- Q1: For the **same validated task** on the **same CPU host**, what are MATLAB HGF Toolbox 8.2.0 and HGFX 1.0.0 compatibility-CPU observed runtime and memory distributions?
- Q2: For the specified forward, fitting and batch workloads, what are HGFX JAX CPU vs physical one-device GPU timing, compilation and transfer costs *when the scientific output is eligible*?
- Q3: Are any completed cross-backend differences credible given fixed input identity, scientific parity, optimizer identity, start and termination/restart semantics, and physical resource variation?
- A result that is slower, unavailable, scientifically invalid or inconclusive is recorded without suppression. No prior hypothesis that HGFX is faster is accepted as fact.

## 2. Immutable versions and strict provenance

MATLAB oracle: HGF Toolbox 8.2.0 Git `2437f4dc241541072722a2695ddeca7b44d83dd3`; record actual MATLAB release and toolbox resolved path. HGFX publication source: `v1.0.0` Git `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; verify installed package and *wheel content hash* in an isolated environment. The revision working tree declares `1.1.0b1` and **must not** be imported for a claimed v1.0.0 benchmark.

The earlier `hgfx-matlab-runtime-1` proposal [RUNTIME_PERFORMANCE_PROTOCOL_V1.md](../../../docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V1.md) belongs to separate PERF-01 gates. It specifies a **different** 9-primary-cell matrix, extra batch sizes and 10×2 repeat scheme. It is **not** silently satisfied or revised by this protocol, and its independently required `PERF-01C=BLOCK_FREEZE` is still active. Explicit independent clearance of comparability/benchmark gate and author confirmation of this separate plan are prerequisites to final measurement.

## 3. Frozen *requested* REV-2.3 workload skeleton — no row removal

| Workload ID(s) | Operation | Original planned size | Mandatory data/parameter mapping before freeze |
| --- | --- | --- | --- |
| `F128,F1024,F8192,F65536` | One forward/filter with full requested outputs | T = 128, 1,024, 8,192, 65,536 | Exact HGF family, observation model, fixed transformed/native parameter vector, masks, reference inputs and full output collection |
| `S128,S512` | One full single-subject **fit** | T = 128, 512 | **Binary HGF default config**, same data, priors, fixed/free mask, start/restarts, optimizer/termination and returned statistics; no replacing complete fit with objective-only timing |
| `B1,B32,B256,B1024` | Batch workflow | B = 1, 32, 256, 1,024, each T = 256 | Native advertised package batch path; same model/obs/config/starts per subject, same output completeness. Compare MATLAB CPU only for matched *completed workflow*; differing algorithm/hardware explicitly labeled |
| `D08` | USD/CHF full fitting workflow | Original 614-observation case | Exact frozen public USD/CHF inputs, frozen official synthetic response seed `123456789` when using original D08 oracle, model `uhgf + gaussian_obs`, priors/start and version; scientific eligibility unresolved, **do not rerun exhausted REV-2.2 D08 science protocol** |

**The plan does not uniquely specify the forward/batch model configuration, source arrays, starts, warm-up state or per-cell output contract.** These fields must be determined from pre-existing reference fixtures / approved scientific scope and frozen prospectively; no fabricated fixture/seed can be treated as the original data. No selection after timing outcomes. Current rows are placeholders, **not an executable freeze**.

Per workload, candidate implementations are `M-CPU` (authentic MATLAB CPU 8.2.0), `H-COMP` (released HGFX 1.0.0 compatibility CPU), `H-JCPU` (released HGFX 1.0.0 JAX CPU), `H-GPU1` (released HGFX 1.0.0 JAX on **one physical GPU**, with device-resident proof). These are four *reporting surfaces*, **not** a guarantee each is implemented or scientifically comparable. Every unavailable/inapplicable cell stays in the report with its reason. The accompanying [proposed eligibility manifest](../../revision/REV-2.3_ELIGIBILITY_MATRIX_DRAFT.json) enumerates all 44 candidate cells.

## 4. Frozen-before-execution controls (all currently PENDING)

1. Pin real **canonical arrays** per workload with SHA256 (inputs, responses, masks, configs/priors, transformed/native parameter order and fixed/free masks, starts, output selection); verify byte-identical paired arrays. The 614-case D08 original evidence cannot be modified or recast as a new timing authorization.
2. Pin exact installation artifacts including HGFX Wheel SHA, MATLAB toolbox SHA, MATLAB release, Python/JAX/JAXLIB/NumPy, OS, CPU socket/model, RAM, GPU device model/driver/CUDA, BLAS/OpenMP/MKL/JAX/XLA environment, CPU affinity and actual MATLAB process thread policy. Same-host CPU is essential for any cross-language speed ratio; when not possible report separated raw times without ratios.
3. Specify one implementation *entrypoint* per workload and backend plus consistent timing boundary. Include data loading/result materialization or exclude on **both** sides with a separately defined name; distinguish full fitting, optimization-only, fixed-vector forward and JIT compilation. Synchronize all asynchronous JAX/GPU device work before stopping a timer. Report host↔device transfers separately.
4. Check scientific eligibility **before observing any runtime ratio**, with frozen historical field-specific tolerances for any available matched model/observation/family. If no applicable family gate exists, label `BLOCKED_NO_FAMILY_GATE` rather than invent one. Check masks, nonfinite location, objective and trajectory output, optimizer route, start/restart and termination; same final objective with different algorithms is not automatically matched scientific fitting.
5. Require independent method/parity reviewer verdict and author approval with references to manifest/protocol **exact commit IDs**. A draft document, preliminary unit test or GPU device listing does not make a comparator eligible.

## 5. Timing/statistics plan, fixed by the article task (no retrospective mixing)

For each scientifically eligible cell: **one warm-up and five timed repetitions** on the stated backend, preserving their individual values, exact order and failures. Report median, IQR, sample count, peak memory if actually measurable; record compile/JIT first-use separately from steady-state; device transfer and synchronization boundaries named. Use **binary64** for all scientific rows. Report sustained contention and resulting uncertainty; no silent outlier removal. Do **not** claim the five repeats as independent hardware replications or reuse PERF-01's 10-paired-block/95% bootstrap decision rules as though this study had followed them.

No exclusion policy: preserve every planned workload/candidate cell and every execution attempt (including invalid scientific data, software exceptions, unavailable GPU/MATLAB, nonconvergence and out-of-memory). A failed cell may be marked `BLOCKED_SCIENTIFIC_PARITY`, `BLOCKED_ENVIRONMENT`, `NOT_SUPPORTED`, `NOT_DIRECTLY_COMPARABLE` or `FAILED_EXECUTION` with trace and denominator; never convert it to a passing smaller workload.

Compare CPU MATLAB/HGFX median ratios **only** for same host, same workflow and scientifically eligible matching operations. A GPU/CPU ratio is explicitly a *cross-hardware* observation. Differences in optimizers/stop reasons/failure rate mean no single unqualified fit speedup. The article must report raw timing and intervals, not just a point ratio; with n=5, IQR is descriptive and does not establish broad generality. Any confidence-interval or material-improvement rule beyond the original revision task requires **prospective reviewer-approved specification before execution**, not a post-result selection.

## 6. Stop conditions, historical failures and failure reporting

- **Hard stop before timed science:** protocol/manifest not frozen; original fixture or source hash absent; independent PERF-01C comparison review still BLOCK_FREEZE without a distinct approved override; host/comparator unresolved; model configuration incomplete; or output gate unproven.
- **At runtime:** unexpected data/config/version hash, missing physical GPU, invalid/mismatched fields, unhandled exception, JAX asynchronous timing ambiguity or changed hardware requires a recorded failed/blocked cell, **not** an improvised replacement. One warm-up + five measurements is a maximum planned scientific execution schedule, not authorization to tune/retry until a favorable result appears.
- **D08:** REV-2.2 own-optimum trajectory `epsi` FAIL (A 4/1228, B 3/1228) and the concurrent original protocol deviation remain. A new *performance* D08 invocation cannot be presented as completing the exhausted REV-2.2 scientific oracle; it additionally requires a new permitted experiment scope, prior method approval and applicable scientific eligibility.
- **Fallbacks from original REV-2.3 plan:** no physical GPU ⇒ keep GPU rows `BLOCKED_ENVIRONMENT`, remove unsupported manuscript GPU claims; MATLAB on a different host ⇒ report times separately and **no cross-hardware language speed ratio**. Neither fallback alters row counts.

## 7. Required raw fields and deliverables

Each attempt: protocol ID + SHA256, final frozen manifest SHA256, exact commit/release/wheel hashes, original input/config/mask/start SHA256s, model/observation, workload ID, backend, complete output contract, CPU/GPU environment, run ID, timestamp, hardware contention, dtype, thread policy, first-compile/warmup/repetition index, wall time (monotonic timer and sync policy), peak memory and methodology or explicit unavailable reason, optimizer identity, convergence/termination, scientific parity verdict, exceptions and immutable log location.

Deliverable set after authorized execution: machine-readable `evidence/revision/benchmark_*.json` with complete 11×4 eligibility/results accounting, one figure and table displaying per-cell median/IQR and resource/compilation limitations, plus an independently audited claims map. Empty/blocked cells are displayed, not deleted.

**Current gate:** `DRAFT_NOT_FROZEN`; `REV-2.3=PLANNED_NOT_RUN`; `PERF-01C=BLOCK_FREEZE`; `REV-2.4=NOT_GLOBAL_PASS`; D2/D3 remain `BLOCKED`. This document is **not** an execution request.
