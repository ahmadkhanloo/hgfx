# PV1-02A — HGFX vs pyhgf final semantic gate

Status: **P2A.9 COMPLETE — PASS FOR ONE FROZEN COMMON-SCOPE CASE**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Decision

```text
FINAL_SEMANTIC_GATE = PASS_FOR_FROZEN_COMMON_SCOPE
benchmark_authorized = true
scope = p2a9-binary-hgf-common-scope-001 only
```

This decision authorizes the **first direct numerical HGFX v1.0.0 ↔ pyhgf 0.3.2 comparison only for the exact committed case** in `paper/reproducibility/pyhgf_common_scope_case.json`.

It is not evidence that the two packages already agree numerically. No cross-tool trajectory, likelihood, surprise, or error result was inspected before this authorization. It is also not a general equivalence, feature-superiority, fitting, or performance claim.

## Why authorization is now valid

P2A.2–P2A.8 were deliberately completed before numerical execution:

| Gate | Result carried forward | Final restriction |
|---|---|---|
| P2A.2 model structure | `PASS_FOR_TOPOLOGY_ONLY` | Three-level binary topology only. |
| P2A.3 equations | `CONDITIONAL_MATCH` | pyhgf `volatility_updates="standard"`, `mean_field_updates=True`. |
| P2A.4 parameters | `PASS_FOR_FROZEN_DEFAULT_CANDIDATE_ONLY` | Frozen HGFX default mapping; binary value coupling fixed at 1. |
| P2A.5 initialization/order | `PASS_FOR_FROZEN_DEFAULT_CANDIDATE_ONLY` | Frozen initial means/precisions and zero top-level drift. |
| P2A.6 input/masking | `PASS_FOR_FULLY_OBSERVED_UNIT_TIME_CANDIDATE_ONLY` | Finite `{0,1}` inputs, no ignored/missing trials, all-ones observed mask, unit time. |
| P2A.7 output quantities | mapped trajectory/response quantities pass semantically | No direct comparison of binary first-level precision internals or implementation-specific weighting intermediates. |
| P2A.8 numerical policy | `PASS_FOR_EXPLICIT_X64_UNCLIPPED_COMMON_SCOPE` | CPU/x64/float64; pyhgf prediction clipping disabled, precision cap set to `inf`, derived surprise evaluated unclipped. |
| P2A.9 environment/API preflight | `PASS` | Exact versions and public configuration verified before scientific execution. |

## Frozen empirical case

Case ID:

```text
p2a9-binary-hgf-common-scope-001
```

The authoritative input and participant-response vectors are explicit arrays in `paper/reproducibility/pyhgf_common_scope_case.json`. They are not to be regenerated for the first run.

```text
n_trials          = 128
inputs_sha256     = 502c5ea2344d42d72a853a4a438a95c010c9c7a42a696815a03314b61ece0062
responses_sha256  = c2a910ff2ff4fd35cf3b4b7e8eb0cc69d41b80fd6239750812d5f56687d0bae2
inverse temperature ze = 48.0
```

Hash serialization is comma-separated ASCII `0`/`1` with no whitespace.

## Frozen model configuration

HGFX is the immutable public release:

```text
hgfx==1.0.0
source SHA 4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27
model hgf_binary
mu_0 = [NaN, 0, 1]
sa_0 = [NaN, 0.1, 1]
rho  = [NaN, 0, 0]
ka   = [1, 1]
om   = [NaN, -3, -6]
irregular_intervals = false
ignored_trials = none
```

pyhgf is the frozen comparator:

```text
pyhgf==0.3.2
source SHA ccd43db5ee5abe4a5a35077d098e53cce2c070c2
sdist SHA256 8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d
volatility_updates = "standard"
mean_field_updates = true
precision_clipping_value = 0.0
max_posterior_precision = inf
observed mask = all ones
time steps = all ones
```

The mapped continuous-node initial means, precisions, drifts, tonic volatilities, and coupling strengths are frozen in the case manifest and P2A.4 mapping.

## Successful environment/API preflight

Dedicated GitHub Actions workflow:

```text
Workflow: P2A.9 Comparator Preflight
Run:      #4
Run ID:   35265386637
Job ID:   105351252916
Result:   success
PR:       #43
Head SHA: 94209537691df032e93e71d886b2fda0995932e1
Runner merge-ref SHA recorded by environment: 995fdd3a78ac538c7f70362bb924001d348d5c7a
```

The workflow installed the public/frozen packages rather than an editable HGFX checkout for the comparator preflight. It verified:

```text
Python   3.12.14
NumPy    2.3.3
JAX      0.6.2
jaxlib   0.6.2
HGFX     1.0.0
pyhgf    0.3.2
backend  cpu
x64      true
NumPy dtype probe  float64
JAX dtype probe    float64
```

Captured hardware/runtime evidence:

```text
CPU      AMD EPYC 7763 64-Core Processor
machine  x86_64
kernel   6.17.0-1022-azure
memory   16373452 KiB
```

The preflight record explicitly states:

```text
scientific_execution_performed = false
cross_tool_numerical_outputs_inspected = false
```

The exact generated environment record is preserved as:

`paper/reproducibility/pyhgf_preflight_environment_35265386637.json`

GitHub artifact provenance:

```text
Artifact ID:     10516800718
Artifact:        p2a9-comparator-preflight-35265386637
Artifact digest: sha256:6cc5cfd7f5bb264ed7a8cac34783b82fbb6245a56fb8e10e28a7ee42422a3e9f
environment JSON SHA256: 6a3833d6cd63ea0baf002454d5a9dab2e118d54d1e5759c3c68e0ad4235d9ab6
pip-freeze SHA256:        ea927b9e643095d51f060026a0e2cc144afa8a99bd0e415028ef2bb1f9cb130e
```

## Frozen direct-comparison quantities

The authorized run compares only:

1. first-level predicted probability;
2. level-2 posterior mean and predicted mean;
3. level-2 posterior precision and predicted precision;
4. level-3 posterior mean and predicted mean;
5. level-3 posterior precision and predicted precision;
6. canonical first-level prediction error `u - p`;
7. canonical first-level input surprise from the mapped `p`, without clipping;
8. participant-response NLL per trial and total, using the same response vector and `ze=48`.

Observed input equality is an exact integrity check. Binary first-level precision/variance internals, `v`, `w`, `psi`, `epsi`, `wt`, HGFX standardized residuals, and pyhgf default-clipped surprise wrappers are outside the direct comparison.

## Frozen metrics and tolerances

For trajectory and per-trial quantities:

```text
max absolute error
max relative error
finite/nonfinite mask agreement
atol = 1e-10
rtol = 1e-8
```

For total participant-response NLL:

```text
atol = 1e-7
rtol = 1e-8
```

These thresholds were committed before the first authorized scientific result. They must not be loosened after seeing the result to obtain a PASS.

## Boundary and failure policy

Every compared field must retain its raw per-implementation array and record dtype plus all `NaN`, `+inf`, and `-inf` coordinates. The run must also record predicted-probability extrema and exact 0/1 coordinates and maximum finite posterior precisions at levels 2 and 3.

Classification is frozen as follows:

- finite mapped trajectory/state disagreement outside tolerance → `IMPLEMENTATION_MISMATCH`;
- trajectory nonfinite-mask disagreement → `IMPLEMENTATION_MISMATCH`;
- a derived surprise/NLL quantity that hits an unclipped mathematical boundary in either implementation → `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`, preserving the raw result;
- wrong environment/package/configuration → `INVALID_RUN_DO_NOT_INTERPRET`;
- an external/reference limitation must not be relabeled as implementation parity.

No failed trial or field may be silently dropped.

## Immutability after authorization

After the first numerical result is generated, the following may not be changed under `hgfx-paper-protocol-1`:

- input vector or response vector;
- inverse temperature;
- model parameters or mapping;
- pyhgf guard settings;
- Python/NumPy/JAX/JAXLIB/HGFX/pyhgf versions;
- CPU/x64/float64 policy;
- compared fields;
- tolerances.

A scientifically necessary change requires a new protocol/case version, preservation of the original result, and explicit explanation. It cannot overwrite this case.

## P2A.9 exit decision

```text
P2A.9 = DONE / PASS
FINAL_SEMANTIC_GATE = PASS_FOR_FROZEN_COMMON_SCOPE
benchmark_authorized = true
```

The authorization is narrow and prospective. **No HGFX↔pyhgf numerical agreement claim exists yet.**

## Next step

Execute exactly `p2a9-binary-hgf-common-scope-001`, persist the raw HGFX and pyhgf outputs and boundary diagnostics under a versioned paper-evidence path, hash the raw result before interpretation, then classify each frozen comparison quantity using the thresholds above.
