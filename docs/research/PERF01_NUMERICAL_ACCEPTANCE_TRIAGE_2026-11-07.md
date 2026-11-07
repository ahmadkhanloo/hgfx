# PERF-01 — numerical tolerance triage and return to benchmark gates (2026-11-07)

**Decision: STOP further bitwise-only MATLAB/HGFX first-gradient investigations as a prerequisite to benchmark planning. Use the existing, frozen scale-aware numerical tolerances. The original failed 64-subject scientific case is NOT waived and remains 63/64 NONPASS. Independent PERF-01C review is still BLOCKED.**

## Authority and exact scope

This is an **interpretation and work-prioritization decision**, not a threshold amendment or a replacement scientific acceptance experiment. It implements the already frozen [MATLAB scientific and numerical equivalence policy](../validation/MATLAB_EQUIVALENCE_POLICY.md) (`matlab-equivalence-policy-1`, frozen 2026-09-14): bitwise floating-point identity is generally **not** the target. Check field-by-field numerical agreement using `abs(HGFX-MATLAB) <= atol + rtol * abs(MATLAB)` with the **existing family-specific tolerances and exact Level-0 contracts**. Do not use one absolute threshold for every quantity; source, dataset, model/config, start, fixed/free mask, precision and observation workflow must still agree exactly.

Authoritative research reference: untouched frozen HGFX v1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` versus MATLAB HGF Toolbox v8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`. This note does **not** rewrite the historical completed v1.0.0 release gate, M18 original scientific FAIL, prior reference-limitation records, the paper protocol, the all-28 planned PERF-01 workload denominator or any failed run.

### What we can reasonably stop investigating

- First-gradient true-source objective differences around `1e-14`–`1e-13`, and native `unitsq_sgm` per-trial computational differences around `1e-15` or machine ULPs **need not be eliminated solely to manufacture bitwise equality** when the applicable already-frozen numerical acceptance gate passes.
- Extensive original-source forensics (draft [PR #92](https://github.com/ahmadkhanloo/hgfx/pull/92), [#97](https://github.com/ahmadkhanloo/hgfx/pull/97), [#98](https://github.com/ahmadkhanloo/hgfx/pull/98), [#99](https://github.com/ahmadkhanloo/hgfx/pull/99)) have localized source differences to observation `unitsq_sgm`, and the [original 71×128×2 source stages](PERF01D_UNITSQ_INTERMEDIATE_ARITHMETIC_RESULTS_2026-11-07.md) were independently re-read from immutable raw files [run 42409218383](https://github.com/ahmadkhanloo/hgfx/actions/runs/42409218383). Their *per-intermediate bitwise* differences do not constitute a new scientific failure or a new tolerance threshold.
- Cross-host reruns are **NOT universally bitwise reproducible**: 1/4 exact and 3/4 tiny numerical NONMATCH in the [four-host 71×128 trial audit 42405702582](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405702582). Keep issue [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) and failed artifacts, but do not require universal CPU bitwise parity as an undocumented prerequisite for accepting already numerically equivalent outputs. This decision neither proves nor dismisses a particular CPU instruction/library defect.

**STOP RULE:** No further unbounded `log`, `log1p`, `pow`, ULP or private Ridders/BFGS branch experiments without a predeclared testable link to a **documented original failed output gate** or a concrete independent-review question. A newly discovered differing float bit **by itself** is not justification for another expensive MATLAB experiment or new PR. The original source and failed numerical evidence remain accessible, not discarded.

### What cannot be waived under the existing rule

The **original** [64-subject end-to-end fitting run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), archived unchanged in `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json`, assessed full outputs at pre-existing family-specific tolerances:

| Quantity | Pre-existing tolerance | Original outcome |
| --- | --- | --- |
| `final` fitted parameters | `atol=3e-10`, `rtol=3e-8` | **WITHIN**; max absolute delta `3.277081539465598e-8` (scale-dependent) |
| `H`, `Sigma`, `Corr`, `LME`, full selected objective, other required fit fields | Their **distinct original field-family** tolerances, not the trajectory threshold applied indiscriminately | **WITHIN** on subject 7 |
| `traj.mu` | `atol=3e-10`, `rtol=3e-8` | **FAIL, four cells**; first zero-based `[83,1]` |
| `traj.muhat` | `atol=3e-10`, `rtol=3e-8` | **FAIL, four cells**; first zero-based `[84,1]` |

Maximum original `traj.mu`/`traj.muhat` absolute delta `1.5704625655477145e-9`. The correct cell-specific tolerance is `3e-10 + 3e-8*abs(reference_value)`; **some original cells violate this bound** despite their small absolute difference. The already executed SHA-locked [original-tolerance margin audit 42266125766](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766) [report](PERF01D_SUBJECT7_ORIGINAL_TOLERANCE_MARGINS_2026-11-06.md) found a **maximum 1.66198× exceedance** in the original SkylakeX-vs-MATLAB failed cells; changing CPU BLAS dispatch can produce **14** different failed `mu` cells and a **3.66090×** original-tolerance exceedance on another host. These source comparisons are host/run-sensitive; they neither justify cherry-picking the passing host nor establish MATLAB scientific reference limitation.

Original public full-fit count remains **1/1, 15/16, 63/64**, with the eighth subject (index 7) still `FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH`. Original summary contains **exactly four** `traj.mu` and **four** `traj.muhat` out-of-tolerance cells, while all other compared fields passed their inherited gates. Re-labeling the whole fit `64/64` based on `1e-9` alone would be a **post-hoc change of the acceptance rule** and is not authorized. This note changes no comparator, input, seed, source, threshold or historical classification.

## What the frozen policy already allows (conditional, not claimed as PASS)

The frozen equivalence policy defines the *existing* **Level 2 endpoint-sensitivity** route. This cannot be self-certified: same-vector replay at the MATLAB final endpoint must pass original full-field tolerances, final and inference fields must pass, demonstrated numerical sensitivity must explain the remaining derived trajectory cells, and **the original optimizer trace/MATLAB objective must show no unresolved material semantic divergence**. The independent reviewer must adjudicate that last condition against original source evidence and earlier sensitivity records. Earlier [same-vector endpoint 41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514) and [original MATLAB self-sensitivity 41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069) are pertinent *author-side diagnostic evidence*, not an automatic prospective Level 2 pass. A previously failed source row cannot be retroactively overwritten even if a **new prospective protocol and holdout** are later approved.

## Next actual acceptance work / hard stop on performance claims

1. **PERF-01D:** retain the original 63/64 + 4+4 scientific mismatch as an open, bounded issue. Stop spending project time optimizing unrequired bitwise identity. Reviewer may classify endpoint sensitivity or unresolved optimizer semantics under the frozen policy, using actual same-vector and MATLAB-path source evidence; without complete support, status stays BLOCKED.
2. **PERF-01C:** deliver an explicit **independent reviewer decision on the existing 28-cell matrix**: 16 diagnostic-concordant/review-pending and 12 blocked, **all retained**. Independently verify the scientific eligible scope, original 64-subject failure, CPU timing boundaries, optimizer compatibility, hardware, and SHA provenance. Require an identified independent reviewer and signed `APPROVE_PROSPECTIVE_FREEZE` **or** `BLOCK_FREEZE`, reviewed commit SHA/raw artifact hashes and any proposed prospective *new-version* lock. The author/CI cannot sign this decision.
3. **PERF-01E–H:** **NOT AUTHORIZED as paper-speedup claims** until the review is approved and a prospective versioned freeze records eligibility/boundaries. No timing of the original nine primary cells as a single valid headline while scientific blockers exist. If needed, a separately approved restricted claim may consider only its explicitly eligible cells, while displaying all 28 original cells and retaining blocked/incomparable rows.
4. **No new scientific/runtimes now** solely to restate a `1e-15` bit gap. The next effective step after this note is **external independent review**, not another 71-node MATLAB source microscope.

## State after this decision

| Gate | Status |
| --- | --- |
| Frozen v1.0.0 release | Historical PASS / CLOSED (not revalidated here) |
| PERF-01D original 64-subject scientific parity | **NONPASS 63/64**, original subject 7 4+4 cells preserved |
| PERF-01D bitwise first-gradient source localization | Author-side **DONE/STOP** as a non-blocking diagnostic for tolerance-based comparisons |
| PERF-01C eligibility, timing boundary and prospective freeze | **OPEN / BLOCKED_PENDING_INDEPENDENT_REVIEW** |
| Original 28 benchmark cells | **16 REVIEW-PENDING; 12 BLOCKED; none removed** |
| Paper-ready HGFX-versus-MATLAB speedup | **NOT ESTABLISHED** |
| Physical GPU for new PERF-01 benchmark | **NOT RUN** (historical v1 T4 applicability is separately evidenced) |
| Cross-CPU bitwise reproducibility | **NONPASS** for prior strict bitwise experiment; not silently waived or called scientifically false |

*This record closes a repetitive investigative workstream, not a scientific acceptance gate.*
