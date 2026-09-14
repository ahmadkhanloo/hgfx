# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Current branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Latest unchanged official-gate implementation head: `648c3f84905eb7fe952c070e5ee858e48de4a3fa`

## Objective and authority

Deliver a Python toolbox that reproduces the frozen MATLAB HGF Toolbox 8.2.0 model coverage, public workflows, demos and scientific outputs without MATLAB as a user runtime dependency.

“Equivalent” means scientific and functional equivalence under explicit frozen rules; it does not mean requiring bitwise equality of every floating-point intermediate. Conversely, equivalence cannot be declared by moving a threshold after seeing a failure.

Apply together:

- `V1_PRODUCT_DEFINITION.md`;
- `V1_RELEASE_GATE.md`;
- `V1_TODO.md`;
- `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`;
- `../validation/MATLAB_EQUIVALENCE_POLICY.md` (`matlab-equivalence-policy-1`);
- `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.

Required MATLAB functionality cannot be deferred beyond the initial v1.0 replacement release. Beyond-reference improvements may be planned separately for v2.

## Frozen equivalence semantics

The current decision policy has four layers:

1. **Exact contract equality** — reference commit, data, model/observation family, configuration semantics, parameter ordering/fixed/free mask/transforms and deterministic drivers/starts must match exactly.
2. **Scale-aware numerical equivalence** — use `abs(HGFX-MATLAB) <= atol + rtol*abs(MATLAB)` with existing output-family tolerances; do not use decimal-place-only rules.
3. **Endpoint-sensitivity numerical equivalence** — permitted only when exact MATLAB-endpoint replay passes, HGFX fitted endpoint/core inference outputs already pass their existing tolerances, any residual mismatch is restricted to a derived endpoint-sensitive trajectory/output, and a prospectively frozen holdout passes unchanged.
4. **Inferential equivalence** — requires a separately preregistered protocol covering fit quality, parameters/identifiability, uncertainty representation, predictive/residual behavior, and model evidence/selection where applicable. A small objective difference alone is insufficient.

Historical direct-gate failures are preserved even if a later prospectively validated accepted-equivalence classification is added.

## Current validated baseline

| Item | Status | Evidence / exact scope |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | Original thresholds/artifacts remain immutable; M18B protocol evidence does not rewrite it |
| M18B integrity-aware protocol | PASS recorded | Existing repository evidence; not equivalent to closing all v1 recovery requirements |
| Exact historical 512-trial case | REFERENCE_LIMITATION_MATCH | Exact paired MATLAB/HGFX case only; not arbitrary 512-trial support |
| D02 model-selection behavior | PASS_MODEL_SELECTION_PARITY | MATLAB/HGFX classic HGF fail correspondingly; eHGF succeeds in both |
| D04 uHGF -> AR(1) official workflow | PASS | run `34763542557` |
| Official fit/Bayes closure set | IN PROGRESS — 7/9 direct PASS | run `34823572071`, job `103910417693`; D02_fit/D08_fit failed unchanged direct gate |
| Latest official evidence artifact | RECORDED | `m18-official-workflows`, ID `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b` |
| D08 endpoint mechanism | DIAGNOSED | run `34823572192`; same-MATLAB-endpoint replay exact at focused epsi/negLj; prospective holdout pending |
| D02 inference result | BLOCKED | `INFERENCE_EQUIVALENCE_FAIL`; endpoint/H/Sigma/Corr/LME/predictions/residuals materially differ |
| v1 product acceptance | OPEN | issue #24; release criteria not yet fully closed |

No tolerance, seed, dataset, start, model-family or optimizer rule was relaxed to obtain this state.

## Ordered work packages and current status

| Step | Status | Work and exit gate |
|---|---|---|
| S1 — reconcile gate semantics | **DONE** | Reference-limitation and tiered-equivalence policies are explicit; historical M18 FAIL and protocol outcomes remain distinct |
| S2 — close D04 official workflow | **PASS** | uHGF -> AR(1) validated; do not repeat because an older plan names it next |
| S3 — freeze remaining workflow contracts | **IN PROGRESS** | Fit/Bayes contracts frozen; finish source-to-workflow mapping for D09-D12/output surfaces before execution |
| S4 — binary demo workflows | **IN PROGRESS** | D01/D03/D05 direct checks pass; D02 fit remains blocking; D09 wrapper open |
| S5 — continuous demo workflows | **IN PROGRESS** | D06 Bayes/fit and D07 fit pass; D08 is prospective endpoint-equivalence candidate |
| S6 — analysis/plot surfaces | **OPEN/TODO** | Close D10-D12 and remaining required output/plot semantics |
| S7 — paired recovery classification | **OPEN/TODO** | Run product-level paired MATLAB/HGFX parameter/model recovery under frozen prospective protocol |
| S8 — repair demonstrated mismatches | **IN PROGRESS** | D02 may require optimizer/numerical or implementation repair depending on frozen diagnostic; do not repair D08 merely to chase endpoint-sensitive last bits if Level-2 evidence passes |
| S9 — robustness/backend closure | **OPEN/TODO** | Robustness matrix + compatibility/JAX CPU/physical-GPU agreement; prior H100 evidence needs applicability audit |
| S10 — reproducible release acceptance | **OPEN/TODO** | Aggregate evidence checker/report, clean install, demos/regression/docs/licenses/no-MATLAB-runtime, then M19/M20 |

## Immediate sequence A — D08 prospective endpoint-sensitivity gate

### Historical direct failure

Official run `34823572071` records one remaining D08 direct-gate mismatch in `fit.traj.epsi`: first zero-based index `(175,1)`, HGFX `138.87836008346915`, MATLAB `138.8783558587791`, absolute difference `4.224690043130642e-6`.

### Focused mechanism evidence

Endpoint diagnostic run `34823572192` established:

- largest final transformed-parameter absolute difference `2.5768804867709605e-9` at zero-based index 8;
- exact MATLAB-endpoint replay in HGFX reproduces the focused MATLAB `epsi` value exactly (`138.8783558587791`);
- exact MATLAB-endpoint replay reproduces MATLAB `negLj` (`-2323.459762013518`);
- replacing parameter 8 alone reduces focused epsi discrepancy from `4.713810909606764e-6` to `4.3272243033243285e-7`;
- optimizer trace and MATLAB-path objective pass the unchanged gate.

This is calibration/diagnostic evidence, not prospective acceptance.

### Frozen prospective gate

Before first execution, `matlab-equivalence-policy-1` froze two holdout seeds:

- `271828182`
- `314159265`

Both use the official USDCHF input, `uhgf + gaussian_obs`, official D08 native parameters/default configs and quasinewton workflow. Existing field tolerances remain unchanged.

Implementation completed:

- MATLAB holdout exporter;
- HGFX Level-2 checker;
- Actions workflow;
- immutable calibration decision record.

Current status: **IMPLEMENTED BUT NOT VALIDATED**. `M18 D08 Equivalence Holdout` run `34826235671` was queued at the last observed check.

Exit rule:

- if both frozen holdouts satisfy the unchanged Level-2 rule, record `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` with exact provenance;
- if either fails, preserve it and keep D08 open; do not replace seeds, thresholds, data, start, model or optimizer;
- never relabel the historical direct-gate artifact as direct PASS.

## Immediate sequence B — D02 inference blocker

### Current evidence

D02 cannot use the D08 endpoint-sensitivity exception because inference-level quantities differ materially.

Established evidence:

- MATLAB endpoint replay in HGFX: PASS;
- initial Ridders gradient: PASS at the existing gate;
- MATLAB optimizer-path objective replay: PASS across 22 sampled points;
- exact quasi-Newton state replay reproduces MATLAB step/BFGS algebra to machine precision;
- optimizer trace nevertheless diverges, first current reported x split at zero-based `(7,0)`: HGFX `0.33948935870343205`, MATLAB `0.33948938811282225`;
- final endpoint differs materially; representative final split at index 12: HGFX `-1.2520696012979948`, MATLAB `-1.0185859753674815`;
- `H[0,0]`: HGFX `0.30808977632407525`, MATLAB `0.9998054857037648`;
- `Sigma[0,0]`: HGFX `10.242002825962189`, MATLAB `1.0001982837227512`;
- `Corr[0,1]`: HGFX `-0.8242120336850707`, MATLAB `0.0015029079855196361`;
- LME: HGFX `-78.28285368561887`, MATLAB `-77.62115775483699`;
- predictions/residuals also differ.

Therefore D02 is **INFERENCE_EQUIVALENCE_FAIL / BLOCKED**. Earlier micro-numerical investigations (`exp`, forward-state, observation replay) remain preserved historical diagnostics; they are not by themselves a release criterion and should not lead to endless last-bit patching without evidence of inference consequence.

### Frozen cross-endpoint classifier

Protocol `m18-d02-basin-probe-1` is frozen in `../validation/M18_D02_BASIN_DIAGNOSTIC.md` before its first execution.

It evaluates MATLAB and HGFX negative log joint at the exact same 9 transformed-parameter vectors

`theta(alpha)=(1-alpha)*theta_MATLAB + alpha*theta_HGFX`

for `alpha=[0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1]`, using unchanged M18 default `rtol=3e-8`, `atol=3e-10`.

Implementation completed:

- MATLAB reference exporter;
- HGFX endpoint/grid generator and objective evaluator;
- MATLAB same-vector grid evaluator;
- classifier;
- Actions workflow.

Diagnostic outcomes:

1. `SAME_VECTOR_IMPLEMENTATION_MISMATCH` — at least one frozen shared vector fails same-objective parity. Next work localizes that exact point before optimizer changes.
2. `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE` — all shared points pass same-objective parity while fitted inference remains different. Next work targets conditioning/gradient amplification/path/termination behavior.
3. `INSUFFICIENT_REFERENCE_EVIDENCE` — frozen experiment incomplete.

None of these classifications closes D02. D02 exits only when direct inference outputs pass the frozen gate, a separately preregistered Level-3 inferential-equivalence protocol passes all required scientific quantities, or exact paired evidence supports an allowed reference limitation. MATLAB currently succeeds, so no reference limitation is established.

## Why this avoids endless numerical patching

A micro-difference is only worth implementation work when a frozen diagnostic demonstrates that it is an HGFX-only divergence relevant to the required workflow or scientific inference. The project must not chase every last-bit runtime difference merely because it exists.

For D08, current evidence supports testing endpoint-sensitivity equivalence prospectively instead of globally loosening tolerance or chasing identical optimizer endpoints.

For D02, current evidence shows scientifically material inference differences, so the project cannot dismiss them as harmless decimal noise. The cross-endpoint classifier narrows the next engineering target without redefining success around the observed result.

## Recovery diagnosis decision procedure

1. Verify exact input/config/parameter/startpoint identity and frozen reference hashes.
2. Test same-vector forward/objective behavior using preregistered points. Material mismatch => `IMPLEMENTATION_MISMATCH`.
3. If same-vector behavior agrees but fitting paths/endpoints differ, investigate optimizer/path/conditioning/termination => `OPTIMIZER_MISMATCH` or more specific frozen diagnostic classification.
4. If endpoint/core inference directly passes and only a derived endpoint-sensitive value remains, apply Level-2 only under a preregistered prospective holdout.
5. If endpoints differ materially but scientific inference is claimed equivalent, require a separately preregistered Level-3 protocol; small objective differences alone are insufficient.
6. If candidate families/observation models differ, use `MODEL_SELECTION_MISMATCH`; do not silently substitute eHGF/uHGF unless MATLAB workflow does so.
7. Use `REFERENCE_LIMITATION_MATCH` only for an exact paired MATLAB limitation with no earlier HGFX-only divergence.
8. If reference evidence is incomplete/ambiguous, retain `INSUFFICIENT_REFERENCE_EVIDENCE`.

## Remaining work after D02/D08

### S3-S5 — remaining demo/workflow contracts

- finish source-to-workflow mapping for all required remaining surfaces;
- close D09 prior-predictive sampling wrapper with frozen MATLAB evidence;
- ensure required D01/D03/D05 and D06-D08 examples are runnable Python workflows, not only core parity fixtures.

### S6 — analysis/output surfaces

- D10 Corr/Sigma inspection and equivalent plotting/example surface;
- D11 residual diagnostic workflow/output parity;
- D12 Bayesian parameter averaging workflow parity;
- remaining plotting/output audit requires semantic/data/axis/label equivalence, not pixel identity.

### S7 — paired recovery validation

Freeze before execution and run paired MATLAB/HGFX parameter and model recovery using identical data, seeds, model/observation family, priors, fixed/free masks, starts and selection rule. Preserve historical M18/M18A/M18B experiments separately; do not rewrite them.

### S8 — minimal evidence-backed repairs

For every required mismatch: failing fixture first, smallest demonstrated fix, unchanged scientific protocol rerun, before/after evidence retained.

### S9 — robustness/backend closure

Freeze and run required horizon/regime/missing/ignored-trial/initialization sweeps. Compare compatibility CPU, JAX CPU and physical GPU on applicable paths. Prior H100 evidence can be reused only where unchanged-path applicability is documented; otherwise record new physical device/driver/CUDA/JAX/command/SHA evidence.

### S10 — release acceptance

Implement an aggregate evidence checker/report rejecting missing, duplicate, substituted, partial or inconsistent evidence; produce durable provenance index; run clean install/full applicable regression+demos/docs/licenses/API checks; verify zero MATLAB runtime dependency for end users; close every mandatory criterion in `V1_RELEASE_GATE.md` / issue #24.

## Evidence contract

For every required case retain: case ID; HGFX/reference SHA; protocol version/hash; exact data/config hashes; seeds/exported stochastic drivers; starts; environment; command; raw MATLAB/HGFX outputs including failures; per-field differences/tolerances; classification; run/job/artifact IDs or equivalent local provenance; artifact SHA-256; review decision.

GPU evidence additionally requires physical device, driver, CUDA/JAX versions and device residency. Shared/contended systems are acceptable when explicitly recorded and the acceptance criterion does not require uncontended peak performance.

## Release interpretation

- **Historical M18 scientific result: FAIL** — preserved unless that exact historical gate genuinely passes in a documented later run; never rewrite failed evidence.
- **M18 v1 MATLAB-equivalence closure: OPEN** until every required workflow/surface is evidence-backed under the frozen policies and no unresolved required HGFX-only mismatch remains.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` and `PASS_INFERENTIAL_EQUIVALENCE` are explicit accepted-equivalence classifications, not bitwise/direct historical PASS.
- `REFERENCE_LIMITATION_MATCH` is acceptable product compatibility only for exact paired evidence, not a scientific PASS claim for the model.
- M19 retains “Methods Paper Dataset Frozen”.
- M20 retains “v1.0 Candidate” and is reached only after S10 acceptance.

## Operational checklist

`V1_TODO.md` is the live checkbox list. Update it, this plan, `V1_RELEASE_GATE.md`, the validation matrix and `AGENT_HANDOFF.md` whenever a gate changes. Record tested implementation SHA separately from documentation/diagnostic-only SHA. Use only **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, or **OPEN/TODO**.