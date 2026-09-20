# PV1-02A — HGFX vs pyhgf update-equation mapping

Status: **P2A.3 COMPLETE — EQUATION SURFACE MAPPED**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step compares only the prediction, prediction-error, and posterior-update equations required by the candidate fixed-parameter three-level binary HGF surface identified in P2A.2.

It does **not** freeze parameter values/transforms, initial states, masking, output quantity, or floating-point precision. It does not execute a numerical HGFX↔pyhgf comparison.

## Frozen sources inspected

### HGFX

Repository state at start of P2A.3: `c22c32e4c7b51ca09f22b089e443395a09636262`.

- `src/hgfx/models/hgf_binary.py`
- `src/hgfx/updates/prediction.py` — blob `a24ca94220fbf13e8bf9545984b63763b0cf195e`
- `src/hgfx/updates/precision_prediction.py` — blob `89b6fc1e59a9d4208ab35890b1031e32355eee87`
- `src/hgfx/updates/binary_l1.py` — blob `fc6aac923a8cad83c522380a5da594906ada19a6`
- `src/hgfx/updates/binary_l2.py` — blob `bfcbb6a8afac691c1c87f333fff20b5e0be12876`
- `src/hgfx/updates/volatility.py` — blob `afdbdcb5b4ae15926a7526cc604f6ca8f6fe7a76`
- `src/hgfx/updates/volatility_pe.py` — blob `3130c58d00a1eb13fa68f94acad68c13c06a560a`

Immutable product release remains `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

### pyhgf

Comparator: `pyhgf==0.3.2`, tag `v0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.

- `pyhgf/model/network.py` — blob `36bd2cb10235e72d0185e2a8f104148a3e89852e`
- `pyhgf/utils/get_update_sequence.py` — blob `3113e67ca02c8c0e0f5a590be843d7737420969b`
- `pyhgf/updates/prediction/binary.py` — blob `fc7af2568d1171b6bacdbde98ee215fa9b75d5cc`
- `pyhgf/updates/prediction/continuous.py` — blob `dc90d17d10bf869411b5d077473314cde2790a19`
- `pyhgf/updates/prediction_error/binary.py` — blob `75c0a5d09157cd6d400b272ae823bf7508ee0356`
- `pyhgf/updates/prediction_error/continuous.py` — blob `0068b262288f2eedeaaabf2399dfa59beb46bc4a`
- `pyhgf/updates/posterior/continuous/continuous_node_posterior_update.py` — blob `e83654a69776e0cd205b719f9722cc8eac39e519`
- `pyhgf/updates/posterior/continuous/posterior_update_precision_continuous_node.py` — blob `25ba9a1006ebe81cfe2dcc6a867a5236a9ff8941`
- `pyhgf/updates/posterior/continuous/posterior_update_mean_continuous_node.py` — blob `3234464fef5e75550fbdbeb19f0f0af9416dea96`

## Critical mode distinction in pyhgf v0.3.2

A bare `Network()` is **not** equation-equivalent to HGFX `hgf_binary`:

```python
Network()
```

uses:

```text
volatility_updates = "unbounded"
mean_field_updates = False
precision_clipping_value = 1e-6
max_posterior_precision = 1e10
```

Furthermore, changing only

```python
Network(volatility_updates="standard")
```

is still insufficient for the frozen MATLAB/HGFX candidate. With `mean_field_updates=False`, pyhgf v0.3.2 uses its improved piHGF prediction step and relaxed/smoothing posterior update. Those deliberately include uncertainty-marginalisation corrections that are absent from the frozen MATLAB HGF 8.2.0 equations reproduced by HGFX.

For the equation-level candidate, the relevant pyhgf route is therefore:

```python
Network(
    volatility_updates="standard",
    mean_field_updates=True,
    ...
)
```

The remaining numerical guards (`precision_clipping_value`, `max_posterior_precision`) are documented below and are deferred to the later precision/numerical-policy micro-step rather than silently ignored.

## Equation mapping

### 1. Continuous-state mean prediction

HGFX standard HGF uses

```text
muhat_j = mu_prev_j + t * rho_j
```

for the non-AR candidate (`phi=0`).

pyhgf `predict_mean` uses

```text
expected_mean = autoconnection_strength * mean + t * driftrate
```

with optional value-parent terms in `driftrate`.

For the candidate random-walk nodes, setting the native pyhgf random-walk semantics (`autoconnection_strength=1`) and mapping tonic drift to HGFX `rho` reduces to the same equation. The frozen HGFX binary configuration fixes the relevant `rho` entries to zero; exact parameter/value mapping is deferred to P2A.4.

Classification: **`MATCH_UNDER_PARAMETER_MAPPING`**.

### 2. Continuous-state predicted precision

HGFX uses

```text
pihat_j = 1 / (1/pi_prev_j + t * exp(kappa_j * mu_upper + omega_j))
```

and, at the top level,

```text
pihat_L = 1 / (1/pi_prev_L + t * theta)
```

where the top diffusion term is represented as `theta` in the frozen toolbox compatibility implementation.

pyhgf with `mean_field_updates=True` uses

```text
predicted_volatility = t * exp(tonic_volatility + sum(kappa * expected_mean_parent))
expected_precision = 1 / (1/precision + predicted_volatility)
```

without the piHGF MGF correction and without the value-parent Laplace variance term.

For the three-level candidate, this is the canonical HGF form. The top level has no volatility parent, so the same expression reduces to the HGFX top-level random-walk precision after the tonic-volatility / `theta` parameter representation is mapped.

Classification: **`MATCH_UNDER_PARAMETER_MAPPING`**.

Important negative result: pyhgf `mean_field_updates=False` is **`DIFFERENT`** here because v0.3.2 adds the piHGF MGF volatility-parent correction and Laplace value-parent uncertainty term.

### 3. Binary prediction

HGFX standard `hgf_binary` computes

```text
p = sigmoid(kappa_1 * muhat_2)
pihat_1 = 1 / (p * (1-p))
delta_1 = u - p
```

and deliberately does not apply the legacy `[0.001, 0.999]` clamp for the frozen standard-HGF oracle.

pyhgf computes

```text
p = sigmoid(sum(value_parent_expected_mean))
q = p * (1-p)
delta_scaled = (u - p) / q
```

where the attribute named `expected_precision` on a binary node stores `q`, explicitly documented by pyhgf as the inverse of the usual continuous-state precision convention.

The two internal representations differ, but their use in the level-2 update is algebraically equivalent (next section).

Classification: **`DIFFERENT_INTERNAL_REPRESENTATION / ALGEBRAIC_MATCH`**, subject to value-coupling and clipping configuration.

### 4. Binary-to-level-2 posterior update

HGFX:

```text
pi_2 = pihat_2 + kappa_1^2 / pihat_1
     = pihat_2 + kappa_1^2 * q

mu_2 = muhat_2 + (kappa_1 / pi_2) * (u-p)
```

pyhgf mean-field standard path for a linear binary child adds

```text
pi_2 = expected_pi_2 + kappa_1^2 * q
```

and its mean term is

```text
(kappa_1 * q / pi_2) * ((u-p)/q)
= (kappa_1 / pi_2) * (u-p)
```

Therefore the different binary precision convention cancels exactly in the parent update.

Classification: **`ALGEBRAIC_MATCH`**.

### 5. Volatility prediction error

HGFX computes

```text
Delta = (1/pi + (mu-muhat)^2) * pihat - 1
      = pihat/pi + pihat*(mu-muhat)^2 - 1
```

pyhgf computes the same expression:

```text
Delta = expected_precision / precision
      + expected_precision * (mean-expected_mean)^2
      - 1
```

For this candidate each relevant node has a single volatility parent, so pyhgf's generalized division by the number of volatility parents is a division by one and does not change the result.

Classification: **`MATCH`**.

### 6. Standard volatility-parent posterior precision

Define

```text
gamma = predicted_volatility * predicted_precision
```

which is HGFX `w` and pyhgf `effective_precision` on the mean-field path.

HGFX standard HGF:

```text
pi_parent = pihat_parent
          + 0.5 * kappa^2 * gamma
            * (gamma + (2*gamma - 1) * Delta)
```

Expanding the increment gives

```text
0.5*kappa^2*gamma^2
+ kappa^2*gamma^2*Delta
- 0.5*kappa^2*gamma*Delta
```

pyhgf `_standard_volatility_increment` implements exactly that expanded expression.

Classification: **`ALGEBRAIC_MATCH`**.

### 7. Standard volatility-parent posterior mean

HGFX:

```text
mu_parent = muhat_parent
          + 0.5 * (1/pi_parent) * kappa * gamma * Delta
```

pyhgf mean-field standard mean update adds

```text
(kappa * effective_precision * Delta) / (2 * node_precision)
```

to `expected_mean`, where `node_precision` is the just-updated posterior precision in the standard schedule.

Classification: **`MATCH`**.

### 8. Dependency/update order

HGFX computes the lower-level binary prediction error before integrating it into level 2, then uses the resulting level-2 volatility prediction error for the level-3 posterior update.

pyhgf's generated update sequence enforces the same dependency rule: children compute prediction errors before their parent posterior update, and children are updated before their own prediction errors are passed upward.

Classification: **`MATCH_FOR_CANDIDATE_DEPENDENCIES`**.

## Residual equation-adjacent numerical guards

Two pyhgf safeguards remain material and are **not** silently declared equivalent in P2A.3:

1. `precision_clipping_value` clips the binary predicted probability; default is `1e-6`, whereas frozen HGFX standard HGF deliberately uses no clamp.
2. `max_posterior_precision` caps posterior precision; default is `1e10`, whereas the frozen HGFX equation has no corresponding general cap.

The pyhgf constructor exposes both controls. Whether the common-scope protocol can neutralize these guards without changing intended model semantics (for example, zero binary clipping and an unbounded precision cap) is deferred to P2A.8 precision/numerical policy. No empirical run is authorized before that policy is frozen.

## P2A.3 classification table

| Surface | Bare pyhgf v0.3.2 default | `standard`, non-mean-field | `standard` + mean-field | P2A.3 result |
|---|---|---|---|---|
| Continuous mean prediction | generalized form | generalized form | canonical form under parameter mapping | `CONDITIONAL_MATCH` |
| Predicted precision | unbounded/piHGF route | piHGF improved prediction | canonical mean-field HGF prediction | `CONDITIONAL_MATCH` |
| Binary prediction | sigmoid + default clipping | same | same | `MATCH_FORMULA`, numerical guard pending |
| Binary PE / level-2 update | different representation | different representation | algebraically canonical | `ALGEBRAIC_MATCH` |
| Volatility PE | generalized HGF expression | same | canonical for one parent | `MATCH` |
| Volatility-parent precision update | unbounded update | standard increment + relaxed posterior context | standard canonical mean-field increment | `ALGEBRAIC_MATCH` |
| Volatility-parent mean update | unbounded update | standard but relaxed context | standard canonical mean-field update | `MATCH` |
| Overall equation surface | `DIFFERENT` | `DIFFERENT` | candidate canonical surface exists | `CONDITIONAL_MATCH` |

## P2A.3 decision

```text
UPDATE_EQUATION_GATE = CONDITIONAL_MATCH
```

Interpretation:

- **Default pyhgf v0.3.2 is not directly equation-equivalent to HGFX `hgf_binary`.**
- **`volatility_updates="standard"` alone is still not sufficient.**
- pyhgf v0.3.2 exposes a canonical mean-field standard route whose required three-level binary HGF equations are algebraically compatible with the frozen HGFX standard-HGF equations, subject to the still-open parameter, initialization, masking, output, and precision/numerical-policy gates.
- This is not a numerical equivalence result and does not authorize a benchmark yet.

The candidate pyhgf configuration carried forward to the next gates is therefore conceptually:

```python
Network(
    volatility_updates="standard",
    mean_field_updates=True,
    # precision_clipping_value: P2A.8 must freeze
    # max_posterior_precision: P2A.8 must freeze
)
```

No default has been silently changed after observing empirical outputs; no cross-tool empirical output has been generated in P2A.3.

## Next micro-step

**P2A.4 — Parameter mapping**

Map HGFX/MATLAB `mu_0`, `sa_0`, `rho`, `kappa`, `omega`, and top diffusion parameterization to the corresponding pyhgf node attributes/couplings. Classify every parameter as `MATCH`, `TRANSFORM_REQUIRED`, `FIXED_FOR_COMMON_SCOPE`, or `NO_DIRECT_EQUIVALENT`. Do not execute trajectories yet.
