# MATLAB scientific and numerical equivalence policy

Status: **FROZEN FOR PROSPECTIVE VALIDATION**
Protocol: `matlab-equivalence-policy-1`
Frozen on: 2026-09-14
Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

HGFX v1.0 targets scientific and functional equivalence to the frozen MATLAB HGF Toolbox, not bit-for-bit identity of every floating-point intermediate. This policy prevents both extremes: requiring meaningless bitwise identity and relaxing a threshold after seeing a failure merely to obtain PASS.

Historical gates and failed artifacts remain immutable. This policy is prospective and versioned; it does not rewrite the result of `official-demo-workflows-1` or any earlier M18 experiment.

## Level 0 — exact contract equality

The following must match exactly before any numerical-equivalence rule can be used:

- reference commit and source workflow;
- input data and its hash/identity;
- model family and observation model;
- configuration semantics;
- parameter ordering;
- fixed/free parameter mask;
- transformed/native parameter convention;
- deterministic simulation drivers, seeds, and starts when the reference workflow fixes them.

A Level-0 mismatch is not numerical tolerance. It is `IMPLEMENTATION_MISMATCH`, `MODEL_SELECTION_MISMATCH`, or `INSUFFICIENT_REFERENCE_EVIDENCE` as appropriate.

## Level 1 — scale-aware numerical equivalence

For a scalar or every element of an array, the default numerical decision is

`abs(HGFX - MATLAB) <= atol + rtol * abs(MATLAB)`.

A decimal-place rule is not used because it is not scale aware. Existing output-family tolerances in the frozen M18 official checker remain unchanged. In particular, adopting this policy does **not** globally increase `rtol` or `atol`.

Simulation paths and exact-contract quantities may retain stricter tolerances than fitted statistical quantities. Any future tolerance change requires a new protocol version, an explicit numerical/scientific justification, and prospective validation evidence.

## Level 2 — endpoint-sensitivity numerical equivalence

A fit may be accepted as `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` without relaxing the frozen pointwise tolerance only when **all** of the following are true:

1. Level 0 exact contract equality passes.
2. Replaying HGFX at the exact MATLAB final parameter vector reproduces the required MATLAB objective and trajectory outputs within the existing frozen Level-1 tolerances. This is the same-vector implementation-parity check.
3. The HGFX final parameter vector itself passes the existing frozen `final` tolerance; no new endpoint tolerance is introduced.
4. All core inference outputs pass their existing frozen tolerances: `H`, `Sigma`, `Corr`, `negLl`, `negLj`, `LME`, `AIC`, `BIC`, `yhat`, `res`, and `resAC` when present.
5. Any remaining mismatch is restricted to a derived trajectory/output whose sensitivity to the tiny endpoint perturbation is demonstrated by a focused diagnostic; a same-vector implementation mismatch is disqualifying.
6. The optimizer trace and MATLAB-path objective evidence show no material semantic divergence under the frozen gate, or any divergence is separately resolved before acceptance.
7. The original mismatch, its magnitude, and the diagnostic evidence remain preserved and visible. The case is not relabeled as bitwise or exact parity.

This rule is intentionally stricter than simply increasing `rtol` until a failing trajectory passes.

## Level 3 — inferential equivalence

Different optimizer paths or endpoints can only be accepted as `PASS_INFERENTIAL_EQUIVALENCE` when the scientific inference is demonstrably equivalent under a separately preregistered protocol. At minimum the protocol must cover:

- fit quality / objective and likelihood;
- final parameter estimates or an explicitly justified identifiable parameterization;
- Hessian/covariance/correlation or other uncertainty representation;
- predictive outputs/residual behavior;
- model comparison quantities and model-selection conclusion where applicable.

A small objective difference alone is insufficient. Material disagreement in Hessian, covariance, correlation, uncertainty, model evidence, or model-selection result blocks inferential-equivalence acceptance unless an exact MATLAB-reference limitation explains it.

## Anti-post-hoc rule

A protocol may be designed using diagnostic/calibration evidence, but that same evidence cannot by itself be the prospective validation that justifies the new rule. The sequence is:

1. preserve the original failed evidence;
2. diagnose and document the mechanism;
3. freeze the new decision rule and any holdout seeds/data before execution;
4. run the prospective holdout unchanged;
5. retain PASS and FAIL outcomes alike;
6. never change the frozen holdout seed, data, starts, model family, or thresholds after observing the result.

## D08 prospective holdout frozen here

The existing D08 endpoint evidence is calibration/diagnostic evidence, not the prospective holdout. The following two simulation seeds are frozen before their first validation execution:

- `271828182`
- `314159265`

Both use the official `example_usdchf.txt`, `uhgf + gaussian_obs`, the official D08 native parameter vector, default MATLAB configs, and the same quasinewton fitting workflow. The checker must apply the unchanged official field tolerances and the Level-2 rule above.

D08 can be closed as `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` only if **both** holdouts are acceptable under the frozen Level-2 rule. A failed holdout remains evidence and D08 stays open; seeds/thresholds may not be replaced to obtain PASS.

## Current interpretation at freeze time

### D08

Calibration evidence supports the endpoint-sensitivity hypothesis: same-vector replay at the MATLAB endpoint is exact at the focused `epsi` value; the official final parameter/statistical outputs otherwise pass; the residual official mismatch is a derived `epsi` value amplified from a tiny endpoint difference. Therefore D08 is a **candidate** for Level-2 acceptance, pending the prospective holdout above.

### D02

D02 is **not** eligible for Level-2 acceptance and currently fails Level-3 inferential equivalence. The latest official evidence contains material disagreements in the final endpoint, Hessian, covariance, correlation, LME, predictions/residuals, and fitted trajectories. Reference-point replay and MATLAB-path objective parity do not erase those inference-level differences.

D02 remains a blocking optimizer/numerical-path problem until the inference outputs converge, a valid preregistered inferential-equivalence protocol passes, or exact paired MATLAB evidence establishes a reference limitation.

## Release semantics

Accepted release classifications under this policy are explicit:

- `PASS` — existing frozen numerical gate passed directly;
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` — Level 2 passed prospectively;
- `PASS_INFERENTIAL_EQUIVALENCE` — Level 3 passed under its own preregistered protocol;
- `REFERENCE_LIMITATION_MATCH` — exact paired MATLAB limitation under the separate reference-limitations policy.

None of the latter three may be described as bitwise equality. Historical failures remain historical failures.