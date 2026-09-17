# PV1-02A — HGFX vs pyhgf input and masking semantics

Status: **P2A.6 COMPLETE — INPUT/MASKING SURFACE MAPPED**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step compares only the binary input representation, missing/ignored-trial semantics, observation masks, and time advancement for the frozen three-level binary HGF candidate carried forward from P2A.5.

It does not compare reported output quantities or floating-point/numerical guards. Those remain P2A.7–P2A.8. No HGFX↔pyhgf numerical trajectory was executed while choosing this mapping.

## Frozen sources

### HGFX

Immutable product source: `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

- `src/hgfx/models/hgf_binary.py` — input recursion and ignored-trial branch.
- `src/hgfx/models/_forward_common.py` — first-column input extraction and ignored mask.
- `src/hgfx/core/trials.py` — unit/irregular time-axis semantics.

### pyhgf

Comparator: `pyhgf==0.3.2`, tag `v0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.

- `pyhgf/model/network.py` — `input_data(...)`, default time steps, and `observed` mask.
- `pyhgf/updates/observation.py` — observation assignment.
- `pyhgf/updates/posterior/continuous/posterior_update_precision_continuous_node.py` — missing-observation precision aging.

## Fully observed binary inputs

HGFX reads the first input column as the binary observation sequence. For the standard binary HGF candidate, each non-ignored trial is consumed as the observed first-level value and the first-level prediction error is formed against the sigmoid prediction.

pyhgf's binary input node likewise receives one scalar observation per trial through `input_data(...)` / `set_observation(...)`.

For a fair common-scope run, the input contract is frozen prospectively to:

```text
input values: finite binary values only, exactly {0, 1}
input dimensionality: one scalar binary channel
number of trials: identical in both tools
```

Classification: **`MATCH_FOR_FINITE_BINARY_INPUTS`**.

The candidate will not rely on either implementation's behavior for non-binary numeric observations, because that is outside the scientific binary-HGF surface being compared.

## Default observed mask

pyhgf defaults `observed` to an all-ones mask when none is supplied. HGFX's ordinary finite-input path has no separate mask requirement; every finite trial not listed in `ignored_trials` is updated.

Therefore, for a sequence containing no `NaN` and no explicitly ignored trials:

```text
HGFX: every trial observed
pyhgf: observed == 1 for every trial
```

Classification: **`MATCH_FOR_FULLY_OBSERVED_SEQUENCE`**.

For reproducibility, the eventual empirical candidate must pass an explicit all-ones `observed` mask to pyhgf rather than relying only on the default.

## HGFX ignored / NaN semantics

HGFX builds the ignored mask as:

```text
ignored = isnan(first_input_column)
ignored |= explicit ignored_trials
```

When a trial is ignored, the frozen `hgf_binary` recursion does not perform a prediction or posterior update. Instead, it copies the previous values for `mu`, `pi`, `muhat`, `pihat`, `v`, `w`, and `da` into the current row.

Operationally, the scientific state is frozen across that trial.

Classification: **`HGFX_SKIP_AND_FREEZE`**.

## pyhgf missing-observation semantics

pyhgf represents a missing observation with `observed=0`. Its documentation explicitly states that when an input is unobserved, the corresponding prediction error is ignored, while parents with no other observations retain the same mean but their precision evolves with elapsed time.

The implementation confirms this: `precision_update_missing_values(...)` applies a random-walk aging step,

```text
posterior_precision = 1 / (1 / previous_precision + predicted_volatility)
```

using the current time step and volatility-parent contribution.

Thus a masked pyhgf trial is **not** equivalent to an HGFX ignored trial. pyhgf advances latent uncertainty through time; HGFX freezes the state row.

Classification: **`DIFFERENT`**.

## Raw NaN is not a common representation

Passing a raw `NaN` observation to pyhgf while leaving `observed=1` is not an acceptable way to emulate HGFX ignored trials: `set_observation(...)` assigns the supplied value to the input node, so a `NaN` is an observed `NaN`, not a skip/freeze command.

Classification: **`NOT_A_VALID_COMMON_MAPPING`**.

## Consequence for common scope

Missing, rejected, or ignored trials are excluded from the direct-comparison candidate. The frozen empirical input must satisfy all of the following:

```text
all input values finite
all input values in {0, 1}
HGFX ignored_trials = None / empty
HGFX input contains no NaN
pyhgf observed mask = all ones
```

This restriction is prospective and follows directly from source semantics; it is not chosen after inspecting cross-tool numerical outputs.

Classification: **`COMMON_SCOPE_RESTRICTED_TO_FULLY_OBSERVED_TRIALS`**.

## Time advancement

For the candidate, HGFX already freezes `irregular_intervals=False`, which yields unit time steps. pyhgf defaults `time_steps` to an all-ones vector when none is supplied.

The empirical configuration must make this explicit in both tools:

```text
HGFX irregular_intervals = False
pyhgf time_steps = ones(n_trials)
```

Classification: **`MATCH_FOR_UNIT_TIME`**.

Irregular-time behavior is not authorized for the direct comparison. This is deliberately narrower than saying the two packages have equivalent irregular-interval semantics.

## P2A.6 decision

```text
INPUT_MASKING_GATE = PASS_FOR_FULLY_OBSERVED_UNIT_TIME_CANDIDATE_ONLY
```

The frozen comparison candidate remains viable, but only under an explicit fully-observed, finite-binary, unit-time contract.

The following are **not directly comparable under the current protocol**:

1. `NaN` input trials;
2. HGFX `ignored_trials` versus pyhgf `observed=0`;
3. rejected/event-log-missing trials represented through masking;
4. irregular/non-unit time-step behavior.

`benchmark_authorized` remains **false** until P2A.7, P2A.8, and the final P2A.9 semantic-gate decision are complete.

## Next micro-step

**P2A.7 — Output quantity semantics.** Map only the trajectory quantities that have the same scientific meaning in both implementations (`mean`, predicted mean, variance/precision, prediction-error/surprise candidates) and define which are authorized for direct numerical comparison.