# Agent Handoff

Last synchronized: 2026-09-13

## Current execution authority

Read these in order before continuing work:

1. `docs/planning/V1_TODO.md` — live operational checklist / exact next task.
2. `docs/planning/M18_COMPLETION_PLAN.md` — ordered S1-S10 dependency plan.
3. `docs/planning/V1_RELEASE_GATE.md` — v1 acceptance criteria.
4. `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` — reference-aware limitation/model-family rules.
5. Relevant validation matrices and gate evidence for the case being changed.

The 2026-09-13 live TODO and M18 completion plan supersede older 2026-09-12 notices elsewhere that still name D04 as the immediate next task. D04 is validated PASS.

## Project goal

HGFX v1.0 must be a functional and scientific Python/JAX replacement for frozen MATLAB HGF Toolbox 8.2.0, with zero MATLAB runtime dependency for users and validated CPU/GPU execution where applicable.

“Replacement” means reproducing MATLAB workflow behavior, including model-family choices and demonstrated limitations. HGFX is not required to make a case succeed when the same MATLAB workflow/model fails. An accepted limitation requires exact paired evidence and classification as `REFERENCE_LIMITATION_MATCH`.

Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## Repository state at this handoff

- Branch: `migration/m18-workflow-closure`
- Last tested implementation head: `faf97bfdbef1333a6a756749a8ab9d6a5be102b3`
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

### Official fit/Bayes closure set

Latest validated run:

- workflow: `M18 Official Workflow Closure`
- run: `34763542525`
- job: `103740409700`
- tested head: `faf97bfdbef1333a6a756749a8ab9d6a5be102b3`
- reference freeze verification: PASS
- targeted tests: 5 passed
- result: **7/9 PASS**
- blockers: `D02_fit`, `D08_fit`
- artifact: `m18-official-workflows`, ID `10319853691`
- artifact ZIP SHA-256: `2cb5b01bce11b900261a0e309e80bf4220d63ac655417d86bf32539bf1cbf773`

No scientific tolerance, seed, dataset, start or model-family rule was relaxed.

## Current blockers

### D02_fit — BLOCKING / IN PROGRESS

Established evidence:

- reference-point replay PASS;
- initial Ridders gradient PASS at current acceptance tolerance;
- MATLAB-path objective replay PASS at current gate tolerance;
- exact MATLAB-state replay reproduces quasi-Newton step/BFGS algebra at machine precision;
- exact MATLAB Ridders finite-difference coordinates reveal raw HGFX-vs-MATLAB objective differences around `1e-12`, which are later amplified by optimization.

**Next exact task:** decompose the objective at those exact `x+h/x-h` coordinates into per-trial likelihood, total likelihood, perceptual/observation priors, and required forward/observation intermediates. Locate the first primitive divergence before changing implementation. If HGFX-only, add a failing regression fixture first, then make the smallest compatibility fix and rerun the unchanged official gate.

### D08_fit — BLOCKING / queued after D02

Only current frozen-gate mismatch is `fit.traj.epsi` around trial index 178 (~`3e-6`); reference-point/initial-Ridders/optimizer-trace/MATLAB-path-objective diagnostics otherwise pass.

After D02, compare final fitted vectors at full IEEE precision, replay both final vectors, and decompose `epsi` around trials 177-179. Add a failing fixture before any repair.

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

When changing a gate, update `V1_TODO.md`, `M18_COMPLETION_PLAN.md`, the affected validation matrix and this handoff in the same planning sync. Record tested implementation SHA separately from documentation-only SHA.
