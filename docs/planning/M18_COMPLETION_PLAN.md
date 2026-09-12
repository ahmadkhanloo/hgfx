# M18 completion plan — MATLAB-equivalent v1.0

Date: 2026-09-12
Baseline inspected: `81fd65a8bc61d9d996ec232a917e81a6397b47ff` (main).
Status: **IN PROGRESS**. This is a planning change, not new validation evidence.

## Objective and authority

Deliver a Python toolbox that reproduces the frozen MATLAB HGF Toolbox 8.2.0
(`2437f4dc241541072722a2695ddeca7b44d83dd3`) model coverage, public workflows,
demos and scientific outputs, without MATLAB as a user runtime dependency.
Apply `V1_PRODUCT_DEFINITION.md`, `V1_RELEASE_GATE.md` and
`../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` together.
GPU acceleration must preserve validated compatibility behavior.
Required MATLAB functionality cannot be deferred beyond the initial v1.0 release.
Beyond-reference improvements may be planned separately for v2.

## Verified planning baseline

| Item | Status | Evidence / exact scope |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | `M18B_GATE.md`; original thresholds and artifacts remain immutable |
| M18B integrity repair | PASS recorded in repository | run 34497399365; 39 targeted tests; 136 regression tests, 4 GPU skips; not M18 scientific PASS |
| Historical 512-trial case | REFERENCE_LIMITATION_MATCH | run 34683977567; only the exact seed/configuration in `M18B_GATE.md` |
| D02 classic HGF failure / eHGF success | PASS recorded in repository | run 34684401843; forward/model-selection scope only |
| D04 uHGF → AR1 checker/exporter/workflow | IMPLEMENTED BUT NOT VALIDATED | commits 3bff98b and 81fd65a; current-head workflow lookup returned no runs on 2026-09-12 |
| Other required demo surfaces | OPEN | D01, D03, D05–D12; inherited numerical parity is not an executable demo |
| M18 workload GPU evidence | OPEN pending applicability audit | previous M14–M17 H100 evidence remains valid for its original scope |
| v1 product acceptance | OPEN | issue #24; no release closure from M18B alone |

Historical evidence above is reported from committed documents; this planning pass did
not download/revalidate those old artifacts. Recheck their provenance before final closure.
Issue #21 already names M18C.2 (trial horizon analysis); preserve that identifier.
The S identifiers below are execution steps, not renumbered milestones.

## Ordered work packages

Work in small commits. Start at the first unfinished step and record evidence before
advancing a dependent gate. Owner roles identify responsibility, not a staffing request.

| Step | Owner | Work and deliverable | Exit gate / dependency |
|---|---|---|---|
| S1 — reconcile gate semantics | Maintainer | Link this plan from roadmap, handoff, milestone and release documents; preserve historical M18 and M18A/B meanings | Planning consistency reviewed; no historical thresholds/status rewritten |
| S2 — close the current D04 attempt | Validation owner | Inspect runs for 3bff98b/81fd65a; if absent run existing `m18-demo-uhgf-ar1.yml`; retain MATLAB JSON, comparison JSON, job logs and hashes | Both official paths succeed and match within existing tolerances; otherwise classify and diagnose first divergence. No claim for D03 or fit/sim from this forward-only checker |
| S3 — freeze the remaining workflow contracts | Reference analyst | Audit frozen demo/source inventory against D01–D12 and M12 coverage; record source locations, exact configs, inputs, outputs and existing fixture IDs per row; add omitted required workflows without deleting rows | Complete source-to-workflow mapping; datasets, seeds, starts, metrics and tolerances fixed before execution; depends on S1 |
| S4 — reproduce binary demo workflows | Implementation + validation owners | Close D01, D03, D05, D09 with runnable Python examples, MATLAB exporters/fixtures and comparison checks; reuse D02/D04 evidence within its scope | Same fit/sim/sample workflow, parameter semantics, trajectories and applicable statistics; reproducible stochastic drivers rather than assumed MATLAB/NumPy RNG identity; depends on S3 |
| S5 — reproduce continuous demo workflows | Implementation + validation owners | Close D06–D08, including official USD/CHF input, Bayes-optimal fit, simulation and fit-back where present | MATLAB-equivalent outputs with first-divergence reports and frozen tolerances; depends on S3 |
| S6 — close analysis and plot surfaces | Implementation + validation owners | Close D10–D12: Corr/Sigma inspection, residual diagnostics and Bayesian parameter averaging; audit all required plotting/output surfaces | Numerical data, axes/labels and scientific interpretation match reference; runnable examples and visual review, not pixel identity; depends on relevant S4/S5 fits |
| S7 — classify recovery failures against the same oracle | Scientific + validation owners | Run paired MATLAB/HGFX parameter and candidate-model recovery on the frozen original grid; preserve original BIC winner rule, AIC diagnostic, all failures and raw fits; extend M18C.2 per issue #21 as a separately frozen 128/256/512/1024 experiment | Complete coverage and one supported classification per failed case; same data, models, priors, free/fixed parameters, starts and workflow; no inference of structural non-identifiability from persistent error alone; depends on S3 |
| S8 — repair demonstrated mismatches | Numerical implementation + independent reviewer | Fix only demonstrated equation/index/transform, optimizer/numerical or model-selection mismatches; add a failing regression fixture first; rerun affected paired cases | No unresolved implementation, optimizer or model-selection mismatch in required scope; depends on any failure from S2/S4–S7; preserve failed artifacts |
| S9 — robustness and backend closure | Validation + GPU owners | Freeze sweeps over required trial horizons, regimes, missing/ignored trials and initialization; compare compatibility vs JAX CPU and physical GPU on supported M18 paths; record backend coverage | Existing tolerances met; missing coverage remains OPEN. Prior H100 evidence reused only with documented unchanged code/data-path applicability; otherwise run physical H100; depends on S7/S8 |
| S10 — reproducible release acceptance | Maintainer + independent reviewer | Build aggregate v1 acceptance report; run complete applicable regression and all required demo checks; verify clean-install examples, docs, API outputs, licenses and no MATLAB runtime dependency | Every required row has evidence-backed acceptance and zero unknowns/mismatches; complete M19 evidence freeze, then M20 candidate; depends on S2–S9 |

## Immediate next action (S2)

Read `reference/matlab/export_m18_demo_uhgf_ar1_reference.m`,
`tools/check_m18_demo_uhgf_ar1.py` and `.github/workflows/m18-demo-uhgf-ar1.yml`.
Look up the run for the actual tested commit, including the preceding implementation
commit if needed. Use `workflow_dispatch` if available. If dispatch/Actions is unavailable,
run the same commands on an authorized MATLAB host and archive equivalent provenance;
otherwise record BLOCKED with the actual API/runtime error. An empty run lookup does
not establish an account restriction and is not a reason to create repeated trigger commits.

The existing workflow executes:

```bash
python scripts/verify_reference_freeze.py
# In MATLAB with reference/matlab on the path:
# export_m18_demo_uhgf_ar1_reference('reference/generated/m18_demo_uhgf_ar1_matlab.json')
python tools/check_m18_demo_uhgf_ar1.py reference/generated/m18_demo_uhgf_ar1_matlab.json --output reference/generated/m18_demo_uhgf_ar1_classification.json
```

Reference checkout and the development environment must be prepared as in the workflow.
Update the D04 matrix row only after inspecting the resulting raw evidence.

## Recovery diagnosis decision procedure

1. Verify exact input/config/parameter/startpoint identity and frozen reference hashes.
2. Compare forward states and fixed-parameter objective first. On mismatch, locate the
   first divergent trial, level, field and intermediate value: IMPLEMENTATION_MISMATCH.
3. If those agree, compare optimization termination, final objective, Hessian/statistics
   and restart selection: OPTIMIZER_MISMATCH when fitting semantics diverge.
4. If candidate families or observations differ, use MODEL_SELECTION_MISMATCH; do not
   silently substitute eHGF/uHGF to improve recovery unless the reference workflow does so.
5. Use REFERENCE_LIMITATION_MATCH only for an exact paired limitation with no earlier
   HGFX-only divergence. The 512-trial example cannot exempt other seeds or horizons.
6. If the reference evidence is incomplete or ambiguous, retain
   INSUFFICIENT_REFERENCE_EVIDENCE. More data may be needed; no scientific PASS follows.

The original recovery script remains an immutable historical scientific experiment.
A new paired product-validation protocol/report must have its own version, frozen input
manifest and acceptance rules before execution. Poor joint recovery, low error and
model discrimination are separate questions. Do not change seeds, select successful
subsets, reduce grids or relax thresholds after seeing results.

## Evidence contract and release aggregation

For each case retain: case ID; HGFX/reference SHA; protocol version/hash; exact data and
configuration hashes; seeds and exported stochastic drivers; starts; environment; command;
raw MATLAB and HGFX outputs including failures; per-field diff and tolerances; classification;
workflow run/job/artifact identifiers or equivalent local-run provenance; artifact SHA-256;
review decision. GPU cases additionally require physical device, driver, CUDA/JAX versions
and device residency. Shared-server limitations are acceptable when recorded.

Persist a durable evidence index in the repository. Expiring CI artifact links alone are
insufficient: archive the underlying immutable evidence with retrievable locations/hashes.
The aggregate checker/report is **TODO**, not implemented by this documentation change.
It must reject absent, duplicate, substituted, partial and inconsistent evidence and must
check exact required-row coverage rather than trusting summary `gate_pass` fields.

Keep two explicit outcomes:

- **Historical M18 scientific result: FAIL** unless that unchanged gate actually passes on
  a documented subsequent run; never overwrite original failed evidence.
- **M18 v1 reference-equivalence closure: OPEN** until all required rows are PASS or a
  narrowly evidenced REFERENCE_LIMITATION_MATCH, all workflow requirements are delivered,
  and regression/backend/release checks are satisfied. Matching limitations do not become
  scientific recovery PASS claims.

M19 retains its historical name, “Methods Paper Dataset Frozen”: freeze the evidence
package required by the existing roadmap without making manuscript acceptance a v1 gate.
M20 retains “v1.0 Candidate”. Optional research extensions do not replace v1 functionality.

## Completion updates after every step

Update this step status, the affected gate and demo matrix, `AGENT_HANDOFF.md`, and the
release evidence index in the same change. Record tested SHA separately from documentation
SHA. Report DONE/PASS, IMPLEMENTED BUT NOT VALIDATED, IN PROGRESS, BLOCKED or OPEN/TODO
explicitly. Never close an entire parent milestone from a single child gate.
