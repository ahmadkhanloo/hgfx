# PV1-02A — HGFX vs pyhgf initial-state semantics

Status: **P2A.5 COMPLETE — INITIAL-STATE SEMANTICS MAPPED**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step compares only the initial continuous states, first-trial time step, and the prediction/observation/prediction-error/posterior-update ordering for the frozen three-level binary HGF candidate carried forward from P2A.4.

It does not compare missing-data semantics, output naming/alignment, precision mode, clipping, posterior-precision caps, or numerical trajectories. Those remain P2A.6–P2A.8.

No HGFX↔pyhgf numerical trajectory was executed while choosing this mapping.

## Frozen sources

### HGFX

Immutable product source: `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

- `src/hgfx/models/hgf_binary.py` — initializes continuous posterior states and performs the frozen recursion.
- `src/hgfx/core/trials.py` — unit-interval time-axis semantics.
- P2A.4 machine-readable parameter mapping: `paper/reproducibility/pyhgf_parameter_mapping.json`.

### pyhgf

Comparator: `pyhgf==0.3.2`, tag `v0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.

- `pyhgf/model/add_nodes.py` — node initial attributes.
- `pyhgf/model/network.py` — `input_data(...)` and default unit time steps.
- `pyhgf/utils/beliefs_propagation.py` — prediction → observation → inference ordering.
- `pyhgf/utils/get_update_sequence.py` — dependency-derived prediction/update schedule.
- `pyhgf/updates/observation.py` — observation assignment.

## Initial continuous states

For the frozen P2A candidate, HGFX initializes the latent continuous levels before trial 1 as:

```text
level 2: mu = 0.0, precision = 1 / 0.1 = 10.0
level 3: mu = 1.0, precision = 1 / 1.0 = 1.0
```

The P2A.4 pyhgf construction sets exactly the same posterior state attributes:

```text
node 1: mean = 0.0, precision = 10.0
node 2: mean = 1.0, precision = 1.0
```

Classification: **`MATCH`**.

pyhgf's cached `expected_mean` / `expected_precision` defaults need not equal those posterior values before the first scan iteration because `beliefs_propagation(...)` runs the complete prediction sequence before the first observation or prediction error. The expected quantities used by inference are therefore overwritten from the mapped posterior state before they are consumed.

Classification: **`DIFFERENT_UNUSED_CACHE / NON_BLOCKING`**.

## Binary level before trial 1

HGFX allocates a dummy pre-trial row. Its level-1 initial mean comes from the undefined `mu_0[0]` placeholder and is not used to determine the first binary prediction; trial 1 recomputes the binary prediction from the level-2 prediction.

pyhgf creates the binary node with implementation defaults, but on each scan step it likewise recomputes `expected_mean` from the value parent's predicted mean before assigning the external observation. `set_observation(...)` then overwrites the binary node's posterior `mean` with the observed input.

Therefore the two packages do not need a numerically identical pre-trial binary posterior state for this candidate.

Classification: **`NO_DIRECT_EQUIVALENT / NON_BLOCKING_FOR_CANDIDATE`**.

## First-trial time step

HGFX with `irregular_intervals=False` constructs a unit time axis, so the first observed trial uses `t=1`.

pyhgf `input_data(...)` defaults to `time_steps = ones(n_trials)`, so the first scan iteration also uses `t=1`.

Classification: **`MATCH`**.

## Dependency order

### pyhgf v0.3.2

For the mapped three-node graph, `get_update_sequence(...)` produces the following dependency order conceptually:

```text
prediction:
  node 2 continuous prediction
  node 1 continuous prediction
  node 0 binary prediction

observation:
  assign u[k] to node 0

inference:
  node 0 binary prediction error
  node 1 posterior update
  node 1 volatility prediction error
  node 2 posterior update
```

This follows the source invariants that parents are predicted only after their parents are ready, children produce prediction errors before parent posterior updates, and a child is posterior-updated before its own prediction error is passed upward.

### HGFX

For each observed trial, the frozen recursion performs the equivalent scientific dependencies in a more specialized sequence:

```text
level-2 mean prediction
binary prediction + observed binary prediction error
level-2 predicted precision
level-2 posterior update
level-3 mean / precision prediction
level-2 volatility prediction error
level-3 posterior update
```

The implementation order is not textually identical, because HGFX is a fixed toolbox-oriented recursion while pyhgf generates a graph schedule.

## Top-level timing restriction

One schedule difference is scientifically material outside the frozen candidate:

- pyhgf predicts node 2 before node 1, so node 1's predicted volatility can see node 2's **predicted** mean;
- HGFX standard `hgf_binary` computes the level-2 predicted precision using the previous level-3 posterior mean (`mu[k-1,2]`) before it later computes the explicit level-3 prediction.

For the P2A candidate this difference is neutralized prospectively, not post-hoc, because P2A.4 already froze:

```text
rho[2] = 0.0
node[2].tonic_drift = 0.0
node[2].autoconnection_strength = 1.0
```

Thus pyhgf's level-3 predicted mean equals the previous level-3 posterior mean at every trial, which is exactly the quantity used by the HGFX level-2 precision prediction.

Consequently, this initial/order gate does **not** authorize a common-scope comparison with non-zero top-level drift. That broader parameter family remains outside the direct-comparison surface.

Classification: **`CONDITIONAL_MATCH_FOR_FROZEN_TOP_DRIFT_ZERO`**.

## P2A.5 decision

```text
INITIAL_STATE_GATE = PASS_FOR_FROZEN_DEFAULT_CANDIDATE_ONLY
```

The frozen candidate has matched continuous posterior initial states, matched first-trial unit timing, and an inference dependency order that is semantically compatible for the already-frozen parameterization.

The gate remains deliberately narrow:

1. the pre-trial binary state is represented differently but is not consumed as a scientific prior in the first-trial candidate calculation;
2. pyhgf's initial expected-state cache differs from the mapped posterior state but is overwritten by prediction before use;
3. non-zero top-level drift is **not authorized** for direct comparison because the two implementations expose different prediction scheduling around the level-2 volatility calculation.

`benchmark_authorized` remains **false** until P2A.6, P2A.7, P2A.8, and the final P2A.9 semantic-gate decision are complete.

## Next micro-step

**P2A.6 — Input and masking semantics.** Compare only binary input representation, ignored/missing trials, observation masks, and time advancement. No cross-tool trajectory benchmark is authorized yet.
