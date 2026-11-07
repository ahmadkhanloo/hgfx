# PERF-01 paired HGFX–MATLAB preflight: evidence and limits

Date: 2026-11-04. Protocol: `hgfx-matlab-runtime-1` (**NOT FROZEN**).  
Status: **IMPLEMENTED / DIAGNOSTIC EVIDENCE AVAILABLE / NOT A SCIENTIFIC-PARITY OR PERFORMANCE PASS**.

## Exact source identity

- HGFX: isolated `1.0.0` checkout, commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- MATLAB oracle: HGF Toolbox `8.2.0`, commit `2437f4dc241541072722a2695ddeca7b44d83dd3`, executed on MATLAB **R2026a** via the public-project MathWorks GitHub action.
- Candidate inputs: actual immutable-byte JSON under `benchmarks/runtime_v1/inputs/`; three horizons (128/512/1024) × 64 subjects each; all 28 predeclared registry entries retained. Exported configuration/priors/transformed starts under `configs/`, 9 files (three models × three horizons); SHA-256 manifests included.
- This is the **same scientific input/start and model/observation mapping**, but HGFX and MATLAB computations happened in independent GitHub-hosted CI jobs, **not a controlled paired same-host speed test**.

## Reproducible raw/provenance links

1. HGFX-only source, status and objective: `benchmarks/runtime_v1/preflight_runs/github-41851191076.json` — CI [41851191076](https://github.com/ahmadkhanloo/hgfx/actions/runs/41851191076). Red because the predeclared, **retained** cases fail at default start; the JSON was committed nevertheless.
2. MATLAB reference-only: `benchmarks/runtime_v1/matlab_preflight_runs/github-41852401008.json` — CI [41852401008](https://github.com/ahmadkhanloo/hgfx/actions/runs/41852401008). Workflow PASS means **script execution and evidence archival**, not a scientific equivalence PASS.
3. Analysis script: `benchmarks/runtime_v1/compare_preflights.py`; complete machine-generated paired classification: `benchmarks/runtime_v1/paired_preflight_runs/hgfx41851191076_matlab41852401008.json`, CI [41852827627](https://github.com/ahmadkhanloo/hgfx/actions/runs/41852827627).
4. A preceding MATLAB CI attempt [41851949869](https://github.com/ahmadkhanloo/hgfx/actions/runs/41851949869) successfully invoked MATLAB but failed only at archiving because the branch advanced concurrently. Its workflow artifact remains preserved. The MATLAB wrapper's vector-orientation preflight defect was corrected before run 41852401008. Do **not** erase this execution history.

## Complete 28-cell account

| Preliminary status | Count | Meaning |
|---|---:|---|
| `BOTH_COMPLETED_NUMERICAL_PARITY_NOT_ASSESSED` | 14 | 7 fixed-parameter forward and 7 objective HGFX cells executed; the corresponding MATLAB model/horizon executions completed |
| `BOTH_FAILED_UNCLASSIFIED` | 5 | 4 HGF 512/1024 forward/objective stage records plus masked HGF 512; MATLAB and HGFX both fail |
| `NOT_RUN_FITTING_UNASSESSED` | 9 | 3 complete-fit cells and 6 batch-throughput cells intentionally unexecuted pending their own gates |
| **TOTAL** | **28** | No cell dropped or replaced |

The seven cross-implementation **negative-log-joint scalar** comparisons, at the exact declared start:

| Model | Trials | Absolute delta |
|---|---:|---:|
| hgf_binary | 128 | 0 |
| ehgf_binary | 128 | 0 |
| ehgf_binary | 512 | 0 |
| ehgf_binary | 1024 | 0 |
| uhgf_binary | 128 | 0 |
| uhgf_binary | 512 | 2.7284841053187847e-12 |
| uhgf_binary | 1024 | 1.0913936421275139e-11 |

These are **descriptive fixed-vector diagnostics** from the machine-generated comparison and do not validate full trajectories, trial-by-trial likelihoods, fitted parameters, Hessians, or inferential equivalence. No numerical tolerance was adjusted.

For standard HGF at 512 and 1024 trials and the 512-trial masked case, MATLAB reports exactly `tapas:hgf:VarApproxInvalid`; HGFX likewise reports the invalid variational-approximation condition, with objective `rval=-1` on the failed objective cells. All 9 (3 models × 3 horizons) cross-implementation initial-prior/start checks in the MATLAB report were true. **Do not classify an exact `REFERENCE_LIMITATION_MATCH` from just the error label**: a first-divergent-trial/intermediate check and full exact-scope evidence are still required. For performance eligibility, these cells remain **BLOCKED_SCIENTIFIC_PARITY / INSUFFICIENT_REFERENCE_EVIDENCE**.

## Updated gate status

- **PERF-01A:** `PARTIAL` — exact code identities and **real MATLAB CI access now verified**; full controlled same-host CPU/thread policy and actual physical GPU environment still must be captured.
- **PERF-01B:** `IMPLEMENTED / REVIEW_PENDING` — canonical files and full HGFX 1.0.0 configs/starts are committed, hashed and reproducible; the source-to-source contract has only been checked for the first subject of each horizon. Full cross-language review / tolerance and runner-lock work remains. **NOT FROZEN**.
- **PERF-01C:** `OPEN` — independent review and prospective protocol freeze must precede final timing.
- **PERF-01D:** `IN PROGRESS` — exact same-start/prior and total fixed-vector objective diagnostic done; trial-level/trajectory and fitter/postprocessing parity not yet gated. Five failed stage records preserved.
- **PERF-01E, F, G, H:** `OPEN / NOT EXECUTED`.
- **Claim 'HGFX faster than MATLAB': NOT TESTED.** No timing data here.

## Next action (no artificial PASS)

1. Reconcile all exact-scope configurations, per-trial trajectories, likelihood, masks, and first-invalid-trial diagnostics for the 14 completed and five failed cells against the unchanged original inputs. Do **not** change seeds, subjects, horizons or starts to make a previously failed cell pass.
2. Audit complete-fit workflows on the unmodified 128/512/1024 inputs and explicitly label reference limitations. The same MATLAB `fitModel` and HGFX `fit_model` postprocessing boundaries are required. A failed/failing fit remains in the table.
3. Have an independent reviewer verify the frozen mapping, scientific acceptance criteria and precisely timed API boundaries, then freeze a **new** performance protocol revision. Do not reopen historical M19 or silently modify `hgfx-paper-protocol-1`.
4. Only then measure matched CPU wall time on **one host**, separating JAX first-use compilation, warm execution, device transfer, complete fitting/statistics and failures. A GPU benchmark requires physical-GPU device/residency evidence.

No paper performance results, figures or headline should be generated from these diagnostics.
