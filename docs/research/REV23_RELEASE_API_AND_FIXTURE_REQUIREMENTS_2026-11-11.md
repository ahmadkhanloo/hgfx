# REV-2.3 — released 1.0.0 API mapping and canonical-input requirements

**2026-11-11 | STATIC SOURCE REVIEW ONLY | IMPLEMENTATION MAP PARTIAL; FIXTURES NOT FROZEN.** Current candidate benchmark draft: [protocol](../../evidence/revision/protocols/REV-2.3_PROTOCOL.md) and [44-cell eligibility matrix](../../evidence/revision/REV-2.3_ELIGIBILITY_MATRIX_DRAFT.json). Nothing in this report authorizes timed or scientific runs.

## Immutable code version

All claims below are about actual GitHub source at published release `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, **not** the current branch's `1.1.0b1`. GitHub source was fetched at the pinned release ref. There was **no runtime import**, dynamic signature validation, installed wheel hash verification, MATLAB licensing/hardware probe or functional experiment.

## 1. Verified Python source/API candidates

| Operation | Actual source at v1.0.0 | Candidate entrypoint and exact limitation |
| --- | --- | --- |
| Full MATLAB-style compatibility fit, default binary config | `src/hgfx/compat/fit.py` (blob `ab58036142993757ed9144a8dd16df74dc27a832`) | `fit_model(responses, inputs, perceptual_config="hgf_binary_config", observation_config="unitsq_sgm_config", optimization_config="quasinewton_optim_config", restart_free_parameters=...)`. It explicitly dispatches alternative models/configs to `fit_workflow`; not a blanket assumption every family shares one route. For REV-2.3 S128/S512 the original plan says **binary HGF default config**. |
| Other full compatibility fit (e.g. D08 uHGF) | `src/hgfx/compat/workflows.py` (blob `9e37d086a945f22823aabb89ee3423c29af947f0`) | `fit_workflow(...)`, reached via `fit_model` for nondefault model families. `FORWARDS` dispatch contains hgf, ehgf, uhgf, hgf_binary, ehgf_binary, uhgf_binary, rw_binary. D08 default setup, exact original config object and scientific eligibility must be pinned from original original-oracle artifacts before any timing. |
| Compatibility binary-HGF forward | `src/hgfx/models/hgf_binary.py` | `hgf_binary(...)` calls `hgf_binary_unified`; parameters and missing/ignored-trial handling must be sourced from the exact release API; this is a source candidate, **not** a frozen forward benchmark fixture. |
| JAX binary HGF forward | `src/hgfx/gpu/engine.py` (release blob `52d466eefe76d0010ff3225c235c2011f8ae6476`) | `fast_binary_hgf(...)` with JAX scan/compile signature, explicit x64 enable and `FastForwardResult`. A separate engine, not MATLAB compatibility code. Avoid claiming it handles continuous HGF or unsupported observation families. |
| JAX binary-HGF fixed-vector objective | `src/hgfx/gpu/engine.py` | `fast_binary_unitsq_objective(...)`: only the binary-HGF / unitsq-sigmoid applicability is verified from this source; objective is **not** a substitute for forward or full-fit timing. |
| JAX single subject optimizer | `src/hgfx/gpu/fitting.py` (release blob `ef44b280ee59ff82697f9a14e66206c8ee40e68a`) | `fit_hgf_binary_unitsq_fast(...)` uses a separate `BFGSOptimizer`, which calls `jax.scipy.optimize.minimize(method="BFGS")`. **Do not call this the same algorithm** as MATLAB `quasinewton_optim`; no proof of equivalent restart, termination, Hessian, LME, BIC or full workflow. |
| Native JAX batch-fit path | `src/hgfx/gpu/batch_engine.py` (release blob `a9e2ce763252eb1179039732802fe420e8e4a3f4`) | `plan_hgf_binary_unitsq_batches(...)` and `fit_hgf_binary_unitsq_batch(...)`, grouping by trial bucket/restart count; inputs are per-subject 1D regular binary-HGF inputs/responses, equal length; at least one subject required; default start from `hgf_binary_unitsq_fit_problem`. Strictly no implication of eHGF/uHGF batch fitness or direct MATLAB `fitModel` complete-statistics equivalence. |

MATLAB-side execution entrypoints `fitModel` (complete fit) and model-specific forward routines are referenced in the frozen oracle/protocol source. **Actual MATLAB function file/content signatures and timed call boundaries were not independently inspected in this task**, so they are `PENDING_SOURCE_INSPECTION`, not verified matches.

## 2. Workload and fixture design locks

| Planned row | Native source surface | Unresolved *before* input generation or execution |
| --- | --- | --- |
| F128, F1024, F8192, F65536 | `hgf_binary` and `fast_binary_hgf` are code candidates **only**; original REV-2.3 plan does not pin a family | Authoritative model/observation, exact fixed vector and array source, masks, trial handling, full output contract, MATLAB matching path |
| S128, S512 | `fit_model` with binary default config; JAX `fit_hgf_binary_unitsq_fast` is **a different optimizer** | Original paired responses and starts, config/prior/mask hashes, restart semantics, full fit stats and termination, separate algorithm statuses |
| B1, B32, B256, B1024 | `fit_hgf_binary_unitsq_batch` supports batch of 1D regular binary-HGF subjects in v1.0.0 | Original article task lacks an exact model/observation designation for batch; if selecting the supported binary HGF workflow, document it as a **prospective author-reviewed choice**; do not invent fixture responses, starts, repetition seeds, or MATLAB-equivalent parallelism |
| D08 | `fit_model` dispatch to `fit_workflow` for `uhgf + gaussian_obs` | Same 614 official USDCHF input/seed `123456789` *in archived provenance*; original A/B own-fit `traj.epsi` failures 4/1228 and 3/1228, nonidentical fitting endpoints, no convergence field recorded: **benchmark eligibility currently blocked**, and the old science run cap is not reopened |

### Canonical input format to freeze before execution

- Each **immutable** workload array file must carry actual byte SHA256, shape, dtype `float64`, explicit endianness and serialized independent MATLAB/Python input/response/mask vectors; retain any true NaNs at exact positions. Do not assume identical RNG streams between implementations.
- Each case needs model family, observation model, original config file/provenance, prior means/variances, transformed/native parameter ordering, mask/fixed/free definitions, defaults vs non-default choices, single start and restart count, source fixture identity, and scientific acceptance contract **before timed results**.
- Forward result contract includes all requested trajectory and inferred-state outputs and explicit materialization; compare no-op/drop-output paths neither as complete forward work nor as matched fit workloads.
- Complete fit contract includes returned outputs (trajectory, fitted parameters, objective, Hessian/uncertainty, fit statistics and actual stop/termination status) and full failure counts; optimizer-only measurements can be separate rows only with separate names, not substitutes for original S/D08 rows.
- Batch input is a list of equal-shape-per-subject 1D binary input and response pairs per the v1.0.0 source. No synthetic array files, seed, provenance hash or model parameters are fabricated in this record.
- `hgfx==1.0.0` must be proven by verified wheel SHA and isolated import path at execution, rather than by a Git source path alone.

## 3. Eligibility and immediate decisions

- **Static source path existence**: `SOURCE_CANDIDATE_VERIFIED` for only the named Python entrypoints above; **not** `SCIENTIFIC_PARITY_PASS`.
- **MATLAB entrypoint match and same-host CPU timing policy**: `OPEN`.
- **F/B model/observation + input fixture selection**: `OPEN_AUTHOR_REVIEW`, because the article plan does not uniquely specify them.
- **S128/S512 scientific-output contract and convergence policy**: `OPEN`; historical PERF-01C longer-fit block does not become PASS.
- **D08**: `BLOCKED_SCIENTIFIC_PARITY` for any unqualified fit speedup, with existing dual-run deviation; do not rerun as an accidental science repeat.
- **All scientific timing**: `NOT_RUN`; no test or hardware benchmark carried out. `PERF-01C=BLOCK_FREEZE`; `REV-2.3=DRAFT_NOT_FROZEN`.

**Next reproducible engineering step:** create fully validated canonical input fixtures and their computed SHA256 **only after** freezing the proposed F/B model choice and exact data provenance; document MATLAB entrypoint/return signature from original toolbox. Provide these along with code timing boundaries and environment manifest to an independent reviewer, who must record an explicit verdict. Preserve all 44 planned candidate cells, blocked cases and original evidence.
