# M18 S9 Robustness / Backend Closure Protocol

Protocol: **`m18-s9-robustness-backend-1`**
Status: **FROZEN BEFORE S9 REPAIR / FINAL EXECUTION**
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Protocol-freeze parent: `4973fed8997622ba76f6c864d92fbb466484bce9`

## Objective

Close the HGFX v1.0 robustness and backend-applicability gate after S7/S8 without redefining the historical M18 scientific recovery experiment.

S9 asks whether already-supported MATLAB-equivalent behavior remains consistent across the release-relevant input regimes and HGFX execution backends. It does **not** introduce new recovery thresholds and does not turn shared S7 identifiability limitations into a scientific PASS.

## Frozen scope

### Trial horizons

Release-grid horizons are `128` and `256`, matching the frozen S7 product grid.

The separately preregistered M18C.2 horizon extension (`128/256/512/1024`, issue #21) remains separate. S9 must not use 512/1024 evidence to alter S7 or silently add/remove release cases after results are observed.

### Perceptual paths

Forward robustness is checked for:

- `hgf_binary`
- `ehgf_binary`
- `uhgf_binary`

with the already-validated transformed parameter/config semantics.

The fitting/backend agreement surface is the implemented fast-fit product path:

- perceptual model: `hgf_binary`
- observation model: `unitsq_sgm`
- compatibility optimizer: frozen HGFX compatibility quasinewton
- fast backend optimizer: JAX BFGS as implemented by `fit_hgf_binary_unitsq_fast`

No eHGF/uHGF fast-fitting claim is made because no corresponding product fast-fit API exists in v1 scope.

## Frozen robustness cases

For each forward model at 128 and 256 trials, deterministic cases cover:

1. `regular` — ordinary binary input stream;
2. `ignored_missing` — deterministic NaN/ignored input positions, preserving frozen ignored-trial semantics;
3. `irregular` — deterministic positive inter-trial intervals in a two-column input matrix.

Additionally, a standard-HGF level-1 boundary fixture is frozen with transformed level-2 initial mean `mu_0[1] = 8.0`, which yields a standard-HGF prediction above `0.999`. Frozen MATLAB v8.2.0 standard HGF (`_original_models/hgf_binary.m`) does not clamp this prediction. eHGF retains its legacy `[0.001, 0.999]` clamp. This boundary is a semantic contract, not a new tolerance choice.

For `hgf_binary + unitsq_sgm` fitting at 128 and 256 trials:

- regular deterministic data are evaluated;
- a deterministic missing/ignored variant is evaluated;
- default transformed start is used for final fit comparison;
- shared-state objective/gradient probes are evaluated at default start and two preregistered perturbations.

Initialization probe offsets are frozen before execution as:

`delta_j = 1e-4 * (j + 1)` for zero-based free parameter index `j`, using `start`, `start + delta`, and `start - delta`.

These shared-state probes diagnose backend semantic disagreement; they do not substitute starts in the official compatibility fit or scientific recovery protocol.

## Frozen numerical criteria

No result-driven tolerance changes are allowed.

Reuse established project criteria:

- forward/trajectory CPU fast-vs-compatibility: existing M14 scale-aware tolerance (`rtol=3e-10`, `atol=3e-11`, equal-NaN semantics);
- shared objective/value parity: existing M14 tolerance (`rtol=3e-10`, `atol=3e-11`);
- shared gradient diagnostic: existing M15 finite-difference comparison (`rtol=2e-4`, `atol=2e-5`);
- compatibility-vs-JAX-CPU **final objective gap**: `<= 0.10` (historical M18 frozen criterion);
- JAX CPU-vs-physical-GPU **final objective gap**: `<= 1e-7` (historical M18 frozen criterion).

Parameter differences, termination and trajectory differences are retained diagnostically. No looser global tolerance may be introduced after observing S9.

## Backend classification

- `PASS_CPU_BACKEND_EQUIVALENCE`: all required current-head compatibility-vs-JAX-CPU cases satisfy the frozen criteria and semantic boundary fixtures.
- `BACKEND_IMPLEMENTATION_MISMATCH`: a required JAX CPU path disagrees materially with current compatibility semantics.
- `PASS_PHYSICAL_GPU_APPLICABILITY`: physical-GPU evidence exercises the same current code/data path and meets the frozen CPU-vs-GPU criterion plus device-residency requirements.
- `PHYSICAL_GPU_REVALIDATION_REQUIRED`: relevant current code/data path changed after prior physical validation, so old H100 evidence is not sufficient for the current release head.
- `INSUFFICIENT_BACKEND_EVIDENCE`: required cells are missing or mechanically invalid.

A CPU-only or mocked-device run can never yield `PASS_PHYSICAL_GPU_APPLICABILITY`.

## Physical H100 evidence reuse rule

Historical H100 evidence from source `e6f1740ec6cacc55323c6a4d4ca521430c9f3dbf` may be reused only if every numerically relevant code dependency for the claimed path is unchanged/applicable at the S9 release head.

If S9 repairs any file in the physical fast path (including `src/hgfx/gpu/engine.py` or a numerically relevant dependency), physical GPU status becomes `PHYSICAL_GPU_REVALIDATION_REQUIRED` until a new strict physical run records:

- source commit SHA;
- GPU hardware;
- driver/CUDA/JAX/JAXLIB/Python versions;
- exact command;
- CPU-vs-GPU result and device residency;
- environment limitations such as shared-node contention.

## Acceptance

S9 is DONE only when:

1. robustness cases are complete and current compatibility semantics remain internally consistent;
2. required compatibility-vs-JAX CPU cells pass or have a policy-supported scoped disposition;
3. no unresolved required backend implementation mismatch remains;
4. physical-GPU applicability is either validly inherited under the unchanged-path rule or revalidated on physical hardware;
5. all raw failures and historical hardware evidence remain preserved.

Until all five hold, S9 remains **IN PROGRESS/BLOCKED**, never PASS by inference.
