# PV1-02A — HGFX vs pyhgf precision and numerical-guard policy

Status: **P2A.8 COMPLETE — PRECISION/GUARD POLICY FROZEN**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step freezes the numerical representation and guard policy for the candidate common-scope three-level binary HGF carried forward from P2A.7. It resolves the remaining equation-adjacent differences identified earlier:

1. floating-point precision / dtype;
2. pyhgf binary prediction clipping (`precision_clipping_value`);
3. pyhgf posterior precision cap (`max_posterior_precision`);
4. pyhgf binary-surprise probability clipping;
5. the treatment of numerical boundary cases.

No HGFX↔pyhgf trajectory, likelihood, or surprise result was executed or inspected while choosing this policy. The policy is prospective.

## Frozen sources

### HGFX

Immutable product source: `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

Relevant frozen source behavior:

- `src/hgfx/models/hgf_binary.py` constructs the standard compatibility recursion with NumPy `float64` arrays and passes `clamp_prediction=False` for the standard HGF branch.
- `src/hgfx/updates/binary_l1.py` computes the standard binary prediction without the legacy `[0.001, 0.999]` clamp and uses explicit `np.float64` arithmetic.
- `src/hgfx/responses/unitsq_sigmoid.py` evaluates the mapped response likelihood on NumPy `float64` arrays.
- the frozen standard-HGF forward equations do not impose a general `1e10` posterior-precision ceiling corresponding to pyhgf's constructor guard.

### pyhgf

Comparator: `pyhgf==0.3.2`, tag `v0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.

Relevant frozen source behavior:

- `pyhgf/model/network.py` exposes public constructor arguments `precision_clipping_value` (default `1e-6`) and `max_posterior_precision` (default `1e10`).
- `pyhgf/updates/prediction/binary.py` clips binary `expected_mean` to `[precision_clipping_value, 1-precision_clipping_value]` before forming its Bernoulli uncertainty term.
- `pyhgf/updates/posterior/continuous/continuous_node_posterior_update.py` writes `minimum(posterior_precision, max_posterior_precision)` on both the standard and standard mean-field paths.
- `pyhgf/math.py::binary_surprise(...)` exposes a public `clipping` argument; when `True` it clips probability to `[1e-6, 1-1e-6]`, and when `False` it evaluates the unclipped Bernoulli negative log probability.
- pyhgf's package metadata permits JAX/JAXLIB `>=0.4.26,<0.7` and Python `>=3.12,<3.14`; the package import path does not itself establish the paper's required x64 precision mode, so the common-scope run must do so explicitly.

## Precision mode

HGFX's frozen compatibility path is binary64-oriented. To avoid comparing HGFX `float64` trajectories against a lower-precision JAX run, the pyhgf common-scope execution is frozen to JAX x64.

The empirical process must start with:

```text
JAX_ENABLE_X64=1
JAX_PLATFORMS=cpu
```

before importing JAX/pyhgf or constructing arrays/JIT functions.

The execution harness must then assert:

```python
jax.config.read("jax_enable_x64") is True
jax.default_backend() == "cpu"
```

and record the actual dtypes of the mapped pyhgf trajectory arrays. The required mapped floating arrays are `float64`.

Classification: **`MATCHED_BINARY64_POLICY`**.

CPU is frozen for this direct numerical comparator cell because the purpose is semantic/numerical equivalence, not accelerator performance. This does not restrict either package's general GPU capabilities, and it does not alter the separate historical GPU evidence.

## Common environment constraint

The shared comparator environment must satisfy both packages:

```text
Python: 3.12.x
JAX:    >=0.4.30,<0.7
JAXLIB: >=0.4.30,<0.7
```

The exact Python/JAX/JAXLIB/NumPy versions must be resolved and recorded in the P2A.9 pre-execution environment manifest **before** any cross-tool numerical result is generated. A version may not be changed after seeing a result in order to obtain closer agreement.

## Binary prediction clipping

The frozen HGFX standard HGF intentionally has no probability clamp at level 1. Therefore pyhgf's default:

```text
precision_clipping_value = 1e-6
```

is not the common scientific equation surface.

pyhgf exposes this bound as a constructor argument and applies it directly through `jnp.clip`. For the common-scope comparison, freeze:

```python
precision_clipping_value = 0.0
```

which reduces the public clipping operation to the identity on probabilities in `[0,1]` and therefore preserves the unclipped canonical standard-HGF equation used by HGFX.

Classification: **`PUBLIC_GUARD_NEUTRALIZED_FOR_COMMON_SCOPE`**.

This setting is fixed prospectively. It must not be replaced by `1e-6`, `1e-3`, or another value after inspecting results.

## Posterior precision cap

The frozen HGFX standard-HGF equation has no matching general posterior ceiling. pyhgf applies:

```text
posterior_precision = min(raw_posterior_precision, max_posterior_precision)
```

with default `max_posterior_precision=1e10`.

For the common-scope comparison, freeze:

```python
max_posterior_precision = float("inf")
```

so the public guard is non-binding for every finite posterior precision and does not modify the canonical equation.

Classification: **`PUBLIC_GUARD_NEUTRALIZED_FOR_COMMON_SCOPE`**.

The run must record the maximum finite posterior precision actually produced, but that diagnostic may not be used to choose a new cap after the fact.

## Frozen pyhgf network numerical configuration

Combined with P2A.3/P2A.4, the common-scope network configuration is now:

```python
Network(
    volatility_updates="standard",
    mean_field_updates=True,
    precision_clipping_value=0.0,
    max_posterior_precision=float("inf"),
)
```

This is not the pyhgf default configuration. It is a deliberately selected public configuration representing the same canonical standard/mean-field HGF equation surface as the frozen HGFX standard-HGF candidate.

The paper must describe this explicitly; it must not imply that default pyhgf is being compared to default HGFX.

## Binary input surprise

P2A.7 identified first-level input surprise as a derived common scientific quantity:

```text
S_input = -log(p)     if u=1
          -log(1-p)   if u=0
```

pyhgf's `binary_surprise` defaults to `clipping=True`, which would introduce a `[1e-6,1-1e-6]` guard absent from the canonical derived HGFX quantity.

For the direct common quantity, freeze one of the equivalent implementation forms below:

```python
pyhgf.math.binary_surprise(u, p, clipping=False)
```

or an explicitly committed canonical formula using the same `float64` `u` and `p`.

The native convenience wrapper `first_level_binary_surprise(...)`, which invokes the default clipping behavior, is **not** the direct-equality oracle for this cell.

Classification: **`DERIVED_UNCLIPPED_COMMON_QUANTITY`**.

## Participant-response negative log likelihood

P2A.7 established the mathematical mapping between HGFX `unitsq_sgm` and pyhgf inverse-temperature binary-softmax surprise. For common predicted belief `p`, binary participant response `y`, and inverse temperature `ze`:

```text
q = p^ze / (p^ze + (1-p)^ze)
NLL = -[y*log(q) + (1-y)*log(1-q)]
```

HGFX reports `logp`, so the common quantity is `-HGFX logp`.

pyhgf's convenience response helper ultimately uses `binary_surprise` with its default clipping. Therefore the direct numerical oracle for the paper must use the same transformed `q` but evaluate:

```python
pyhgf.math.binary_surprise(y, q, clipping=False)
```

(or the same committed canonical `float64` formula), not the clipped convenience-wrapper result.

The convenience wrapper may be retained as a diagnostic showing the effect of pyhgf's default safeguard, but it is not a direct-equivalence metric.

Classification: **`ALGEBRAIC_COMMON_QUANTITY_WITH_UNCLIPPED_PUBLIC_PRIMITIVE`**.

## Numerical-boundary policy

Neutralizing guards means boundary behavior remains visible rather than being hidden.

The empirical harness must record, at minimum:

- minimum and maximum first-level predicted probability `p` in each implementation;
- whether any `p` equals exactly `0` or `1`;
- maximum finite posterior precision at levels 2 and 3;
- counts and coordinates of `NaN`, `+inf`, and `-inf` for every compared quantity;
- actual dtype for each mapped array.

If the frozen unclipped/common-scope calculation reaches a singular/non-finite boundary, the raw result is preserved. The protocol must **not** introduce a new clipping value, precision cap, dtype, input sequence, or package version after observing it.

If such a boundary prevents the intended scientific quantity from being compared fairly, the affected cell is classified `NOT_DIRECTLY_COMPARABLE` under the existing paper evidence taxonomy. It is not silently dropped or repaired post hoc.

## Tolerance policy remains prospective

P2A.8 freezes representation and guards, not the numerical PASS tolerance. Exact bitwise equality is not assumed across NumPy and JAX implementations.

P2A.9 must freeze, before execution:

- the exact common input/response sequence;
- exact resolved environment versions;
- compared fields;
- absolute/relative error metrics and tolerances;
- failure handling and raw-output schema.

No trajectory or likelihood result may be generated before that P2A.9 protocol is committed.

## P2A.8 decision

```text
PRECISION_NUMERICAL_GATE = PASS_FOR_EXPLICIT_X64_UNCLIPPED_COMMON_SCOPE
```

The remaining numerical-guard differences do **not** force `NOT_DIRECTLY_COMPARABLE` at the semantic level because pyhgf v0.3.2 exposes public controls that can make the relevant forward guards non-binding, and its public `binary_surprise` primitive exposes `clipping=False` for the derived surprise/response quantities.

The restrictions are strict:

1. CPU + JAX x64 is mandatory for the comparator cell.
2. pyhgf forward network uses `precision_clipping_value=0.0`.
3. pyhgf forward network uses `max_posterior_precision=inf`.
4. direct surprise/NLL quantities use `binary_surprise(..., clipping=False)` or the committed identical canonical formula.
5. native clipped convenience wrappers are not used as direct-equality oracles.
6. numerical boundaries remain visible; no post-result guard tuning is permitted.
7. `benchmark_authorized` remains **false** until P2A.9 freezes the final empirical protocol and semantic-gate decision.

## Next micro-step

**P2A.9 — Final semantic gate and pre-execution common-scope protocol.** Consolidate P2A.2–P2A.8 into one machine-readable candidate configuration, freeze the exact input/response sequence, environment lock, compared fields and error tolerances, then decide whether the first direct HGFX↔pyhgf numerical run is authorized.