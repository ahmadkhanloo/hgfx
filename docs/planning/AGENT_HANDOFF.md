# Agent Handoff

## Continuation update — 2026-09-14

At head `ae063e7a866e2ab227110fd1a771d138fad2a274`, official run
`34821444138` still reports 7/9 PASS; D02/D08 remain optimizer mismatches.
D08 now first fails `epsi` at zero-based `(175,1)` (138.87836008346915
versus MATLAB 138.8783558587791). Older numerical values below are historical.

The D08 prior diagnostic run `34821444290` / job `103903714260` /
artifact `10338820786` exposes a prior-variance input mismatch:
HGFX `4.06248750000001e-05`, MATLAB `4.0624875000000105e-05`.
A local matched-input replay reproduces all MATLAB prior terms and their total
exactly. The first classification is therefore `PRIOR_INPUT_DIVERGENCE`, not
proof of a Gaussian quadratic-form defect. Original output is preserved in
`reference/validation/m18_d08_prior/` with hashes and the raw artifact ZIP.

Next D08 step: run the additive placeholder trace (window, mean, deviations,
squares, reduction, explicit variance and MATLAB var), locate the first
operation split, then write the core regression and repair only the evidenced
cause. No input override is used by fitting; no core/tolerance/seed changes.
The new exporter is IMPLEMENTED BUT NOT VALIDATED in MATLAB until CI runs.

D02's existing log-path regression fails in focused Python 3.11 / NumPy 2.4.6
run `34821444075`, but passes locally with Python 3.12.14 / NumPy 2.5.3;
local success does not close that cross-runtime blocker.
Historical M18 FAIL and v1 closure OPEN remain unchanged.


Last synchronized: 2026-09-13

## Current execution authority

Read these in order before continuing work:

1. `docs/planning/V1_TODO.md` — live operational checklist / exact next task.
2. `docs/planning/M18_COMPLETION_PLAN.md` — ordered S1-S10 dependency plan.
3. `docs/planning/V1_RELEASE_GATE.md` — v1 acceptance criteria.
4. `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` — reference-aware limitation/model-family rules.
5. Relevant validation matrices and gate evidence for the case being changed.
6. For paper-facing continuity: `docs/research/PAPER_EVIDENCE_MAP.md` and `docs/research/RESEARCH_LOG.md`.

The 2026-09-13 live TODO and M18 completion plan supersede older 2026-09-12 notices elsewhere that still name D04 as the immediate next task. D04 is validated PASS.

## Project goal

HGFX v1.0 must be a functional and scientific Python/JAX replacement for frozen MATLAB HGF Toolbox 8.2.0, with zero MATLAB runtime dependency for users and validated CPU/GPU execution where applicable.

“Replacement” means reproducing MATLAB workflow behavior, including model-family choices and demonstrated limitations. HGFX is not required to make a case succeed when the same MATLAB workflow/model fails. An accepted limitation requires exact paired evidence and classification as `REFERENCE_LIMITATION_MATCH`.

Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## Repository state at this handoff

- Branch: `migration/m18-workflow-closure`
- Last tested implementation/diagnostic head: `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`
- Paper-documentation sync commit: `5b37e7df2a4a47f5159c47c75517d3f404a75b31`
- PR: #26, draft/open/unmerged
- Current milestone: M18 v1 MATLAB-equivalence closure — **IN PROGRESS / OPEN**
- Historical M18 scientific experiment: **FAIL, preserved**
- M18B protocol/integrity gate: recorded PASS in its own scope; not a replacement for product closure

## Completed historical milestones

M0-M17 are recorded complete according to their gate documents/evidence:

- M0 Reference Frozen
- M1 Golden Harness
- M2 Parameter/Config Parity
- M3 Scalar Numerical Parity
- M4 HGF Forward Parity
- M5 eHGF Forward Parity
- M6 uHGF Forward Parity
- M7 Observation Parity
- M8 Objective Parity
- M9 Compatibility Fitting
- M10 Hessian/LME Parity
- M11 Simulation Parity
- M12 Complete Model Coverage
- M13 API Compatibility
- M14 Native GPU Engine — physical H100 evidence
- M15 GPU Fitting — physical H100 evidence
- M16 Batch Engine — physical H100 evidence
- M17 Multi-GPU — physical correctness plus shared/contended-node scaling evidence

Do not reinterpret a historical PASS beyond its documented scope. Reuse GPU evidence only when unchanged code/data-path applicability is documented.

## Current validated M18 evidence

### Reference-aware cases

- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY**. On the exact official regime, classic HGF fails in MATLAB and HGFX; eHGF succeeds in both with trajectory/state parity.
- D04 uHGF -> AR(1): **PASS** on workflow run `34763542557` at `faf97bf...`.
- Exact historical 512-trial case: **REFERENCE_LIMITATION_MATCH**; not arbitrary 512-trial support and not scientific recovery PASS.

### Latest official fit/Bayes closure set

- workflow: `M18 Official Workflow Closure`
- run: `34776952053`
- job: `103776700085`
- tested implementation/diagnostic head: `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`
- reference freeze verification: PASS (`2437f4dc...`, 334 MATLAB files)
- targeted M18 API/IEEE/FDLibm tests: 7 passed
- result: **7/9 PASS**
- blockers: `D02_fit`, `D08_fit`
- artifact: `m18-official-workflows`, ID `10323968264`
- artifact ZIP SHA-256: `ac4d0094cfe49b5e5ee8d5c75f89311c35a2727b46ed433078412be63c3b5f9c`

Passing official cases: D01_bayes, D01_fit, D03_fit, D05_fit, D06_bayes, D06_fit, D07_fit.

No scientific tolerance, seed, dataset, start, model-family or optimizer rule was relaxed.

## Current blockers

### D02_fit — BLOCKING / IN PROGRESS

Established evidence:

- reference-point replay PASS;
- initial Ridders gradient PASS at current acceptance tolerance;
- MATLAB-path objective replay PASS at current gate tolerance;
- exact MATLAB-state replay reproduces quasi-Newton step/BFGS algebra at machine precision;
- exact Ridders-coordinate objective decomposition shows priors exact and residual differences in likelihood/forward numerics;
- regression-first commit `27bba3e44aae832e8805d25a631ebac15f81f40f` froze MATLAB-vs-default-runtime `exp` divergence;
- repair `7b43ae5e45f85f44d23a6e980200baca46609fbd` added MATLAB-compatible `exp` numerics on the evidenced D02 path without changing the gate;
- latest residual selected case (`parameter_2_first_ridders_minus`, trial 83) is classified **FORWARD_NUMERICAL_DIVERGENCE**;
- selected `inf_states` max abs diff `7.105427357601002e-15`;
- selected observation input diff `1.1102230246251565e-16`;
- selected per-trial log-likelihood diff `2.4868995751603507e-14`;
- observation replay on exact MATLAB state has zero log-likelihood difference;
- tiny replay `pow1mx` difference `6.776263578034403e-21` is not evidenced as causal because the replayed final likelihood is exact.

Official D02 still classifies `OPTIMIZER_MISMATCH`; current first reported final split includes HGFX `-1.6252419364429298` vs MATLAB `-1.0185859753674815`.

**Next exact task:** at the frozen residual Ridders sample, export/compare eHGF forward intermediates and find the first trial/level/primitive where the nonzero state divergence appears. Add a regression fixture before any implementation repair, then rerun the unchanged official gate.

Do not return to optimizer/BFGS diagnosis unless new evidence contradicts the current forward-numerics localization.

### D08_fit — BLOCKING / queued after D02

Latest frozen mismatch is only `fit.traj.epsi` at `(178,1)`:
- HGFX `-4.7887561410406825`;
- MATLAB `-4.788757533201755`;
- abs diff ~`1.392e-6`.

Reference point PASS, initial Ridders PASS, optimizer trace PASS and MATLAB-path objective replay PASS (50 points).

After D02, compare final fitted vectors at full IEEE precision, replay both final vectors, and decompose `epsi` around trials 177-179. Add a failing fixture before any repair.

## Paper/research documentation state

Paper-facing documentation is now synchronized with the v1 MATLAB-equivalence objective:
- `docs/research/LEVEL2_PAPER_PLAN.md` — revised research questions/experiments;
- `docs/research/PAPER_EVIDENCE_MAP.md` — live claim-to-evidence matrix;
- `docs/research/RESEARCH_LOG.md` — backfilled major decisions and current D02/D08 interpretation;
- `docs/research/BENCHMARK_PLAN.md` — paired-reference, provenance, GPU and M19 freeze rules;
- `paper/README.md` — manuscript readiness and freeze policy.

M19 is **OPEN/TODO**. The manuscript may be outlined, but final numerical tables/figures/results must not be frozen before M19.

## Work remaining after D02/D08

Follow `V1_TODO.md` exactly:

- finish remaining demo/source contract coverage, including D09;
- S6: D10 Corr/Sigma + plotting surface, D11 residual diagnostics, D12 Bayesian parameter averaging, remaining output surfaces;
- S7: paired MATLAB/HGFX parameter and model recovery using frozen protocols;
- S8: repair only demonstrated HGFX-only required-scope mismatches;
- S9: robustness plus CPU/JAX/physical-GPU closure with applicability audit of prior H100 evidence;
- S10: aggregate evidence checker/report, durable provenance index, full regression/demo suite, clean install, docs/API/licenses, no MATLAB runtime dependency;
- M19 evidence/dataset freeze;
- M20 v1.0 candidate only after release gate passes.

## Scientific/engineering integrity rules

- Never declare PASS without the documented gate and evidence.
- Never relax thresholds after seeing results.
- Never change seeds/datasets or shrink grids to obtain PASS.
- Never hide failed experiments or rewrite historical evidence.
- Never call a problem a scientific/model limitation without matched MATLAB evidence.
- Distinguish implementation mismatch, optimizer mismatch, model-selection mismatch, reference limitation and insufficient reference evidence.
- When MATLAB is the compatibility oracle, compare the same family/config/data/parameters/starts/workflow first.
- A MATLAB limitation may be acceptable for v1 compatibility; an HGFX-only divergence where MATLAB succeeds is blocking.

## Status vocabulary

Use only: **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**.

When changing a gate, update `V1_TODO.md`, `M18_COMPLETION_PLAN.md`, the affected validation matrix and this handoff in the same planning sync. For paper-relevant changes update `docs/research/PAPER_EVIDENCE_MAP.md` and `RESEARCH_LOG.md` as well. Record tested implementation SHA separately from documentation-only SHA.
