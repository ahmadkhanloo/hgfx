# PV1-02A — HGFX vs pyhgf parameter mapping

Status: **P2A.4 COMPLETE — PARAMETER SURFACE MAPPED**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step maps only the parameters required by the candidate fixed-parameter three-level binary HGF identified in P2A.2/P2A.3. It does not validate first-trial initialization order, masking, reported output quantities, or floating-point/numerical guards; those remain P2A.5–P2A.8.

No HGFX↔pyhgf numerical trajectory was executed while choosing this mapping.

## Frozen sources

### HGFX

Immutable product source: `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

- `src/hgfx/compat/configs.py` — blob `76469aa702a3983c92bb48465ed084f16760f039`
- `src/hgfx/models/hgf_binary.py` — blob `e1aec3e8bbc8623f81532601a7d1c53e23278e12`
- `src/hgfx/models/_forward_common.py` — blob `9b3f390fe219f7c489782371fcdeae59cc378b94`
- `src/hgfx/core/parameters.py` — blob `c0c7df63dc6e4246ece5a63bfff39d789cb7c07c`

### pyhgf

Comparator: `pyhgf==0.3.2`, tag `v0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.

- `pyhgf/model/network.py` — blob `36bd2cb10235e72d0185e2a8f104148a3e89852e`
- `pyhgf/model/add_nodes.py` — blob `a30d1ac89ea0e26a7114abf2dc8e0b776e2003c4`
- `pyhgf/updates/prediction/binary.py` — blob `fc7af2568d1171b6bacdbde98ee215fa9b75d5cc`
- `pyhgf/updates/prediction/continuous.py` — blob `dc90d17d10bf869411b5d077473314cde2790a19`
- `pyhgf/updates/posterior/continuous/posterior_update_precision_continuous_node.py` — blob `25ba9a1006ebe81cfe2dcc6a867a5236a9ff8941`

## Frozen HGFX candidate values

The candidate uses the frozen `hgf_binary_config()` prior means as fixed forward parameters; no parameter is tuned from cross-tool output.

```text
mu_0 = [NaN, 0.0, 1.0]
sa_0 = [NaN, 0.1, 1.0]
rho  = [NaN, 0.0, 0.0]
ka   = [1.0, 1.0]
om   = [NaN, -3.0, -6.0]
```

HGFX fitting-space names are `mu_0`, `logsa_0`, `rho`, `logka`, and `om`. `logsa_0` and `logka` are exponentiated into native `sa_0` and `ka`; `om` remains in log-volatility space. In the standard binary forward recursion, the top-level diffusion is derived internally as `theta = exp(om[2])`.

Although `om[1]` and `om[2]` have non-zero prior variance in the fitting configuration, P2A uses their frozen prior means (`-3`, `-6`) as fixed forward values. This comparison is not a fitting experiment.

## Parameter mapping

| HGFX parameter | HGFX transformed/native rule | Frozen candidate | pyhgf v0.3.2 target | Classification | Constraint / interpretation |
|---|---|---:|---|---|---|
| `mu_0[0]` | undefined placeholder | `NaN` | binary-node prior mean is represented separately | `NO_DIRECT_EQUIVALENT` | HGFX level-1 initial placeholder is not a scientific free parameter for this candidate; timing relevance is deferred to P2A.5. |
| `mu_0[1]` | identity | `0.0` | Node 1 `mean=0.0` | `MATCH` | Same continuous level-2 initial location value. |
| `mu_0[2]` | identity | `1.0` | Node 2 `mean=1.0` | `MATCH` | Same continuous level-3 initial location value. |
| `logsa_0[0]` / `sa_0[0]` | undefined placeholder | `NaN` | no required common-scope parameter | `NO_DIRECT_EQUIVALENT` | Binary first-level variance placeholder is not used as a continuous prior variance. |
| `logsa_0[1]` → `sa_0[1]` | `sa=exp(logsa)` | `0.1` | Node 1 `precision=10.0` | `TRANSFORM_REQUIRED` | pyhgf stores precision, so `precision = 1 / sa_0`. From HGFX fitting space: `precision = exp(-logsa_0)`. |
| `logsa_0[2]` → `sa_0[2]` | `sa=exp(logsa)` | `1.0` | Node 2 `precision=1.0` | `TRANSFORM_REQUIRED` | Same reciprocal variance→precision mapping. |
| `rho[0]` | undefined placeholder | `NaN` | no required common-scope parameter | `NO_DIRECT_EQUIVALENT` | No continuous drift parameter exists at the observed binary level. |
| `rho[1]` | identity | `0.0` | Node 1 `tonic_drift=0.0` | `MATCH` | Requires `autoconnection_strength=1.0`. |
| `rho[2]` | identity | `0.0` | Node 2 `tonic_drift=0.0` | `MATCH` | Requires `autoconnection_strength=1.0`. |
| `logka[0]` → `ka[0]` | `ka=exp(logka)` | `1.0` | value edge Node 1 → Node 0, coupling strength `1.0` | `FIXED_FOR_COMMON_SCOPE` | **Critical restriction:** pyhgf binary prediction computes `sigmoid(sum(parent expected_mean))` without multiplying by the value-edge strength. Therefore arbitrary HGFX `ka[0]` is not semantically mapped; the common scope is valid only at the frozen unit coupling. |
| `logka[1]` → `ka[1]` | `ka=exp(logka)` | `1.0` | volatility edge Node 2 → Node 1, coupling strength `1.0` | `TRANSFORM_REQUIRED` | pyhgf edge strength is native `ka`; the equation surface supports the same volatility-coupling role. |
| `om[0]` | undefined placeholder | `NaN` | no required common-scope parameter | `NO_DIRECT_EQUIVALENT` | No first-level tonic volatility parameter is required for the observed binary node. |
| `om[1]` | identity log-volatility | `-3.0` | Node 1 `tonic_volatility=-3.0` | `MATCH` | Both implementations exponentiate this log-volatility inside continuous precision prediction. |
| `om[2]` | identity log-volatility; HGFX derives `theta=exp(om[2])` | `-6.0` | Node 2 `tonic_volatility=-6.0` | `MATCH` | pyhgf likewise exponentiates top-node tonic volatility internally; user-level mapping stays in log-volatility space. |

## pyhgf-only settings required by the common scope

These are not additional HGFX scientific parameters; they select the pyhgf representation that P2A.3 showed is compatible with the canonical frozen-HGF equation surface.

| pyhgf setting | Frozen common-scope value | Classification | Reason |
|---|---:|---|---|
| `volatility_updates` | `"standard"` | `FIXED_FOR_COMMON_SCOPE` | `unbounded` is a different update family. |
| `mean_field_updates` | `True` | `FIXED_FOR_COMMON_SCOPE` | Required to remove piHGF/Laplace corrections absent from frozen MATLAB/HGFX equations. |
| Node 1 `autoconnection_strength` | `1.0` | `FIXED_FOR_COMMON_SCOPE` | Recovers HGFX Gaussian-random-walk mean prediction `mu_prev + t*rho`. |
| Node 2 `autoconnection_strength` | `1.0` | `FIXED_FOR_COMMON_SCOPE` | Same. |
| value coupling function Node 1 → Node 0 | linear / `None` | `FIXED_FOR_COMMON_SCOPE` | Candidate uses canonical linear value coupling. |
| volatility coupling Node 2 → Node 1 | native strength `1.0` | `FIXED_FOR_COMMON_SCOPE` | Frozen HGFX `ka[1]=1`. |

`precision_clipping_value` and `max_posterior_precision` are numerical guards, not scientific model parameters. They remain intentionally unresolved until P2A.8.

## Candidate pyhgf parameterization carried forward

Conceptually, before the later initialization/masking/precision gates, the mapped candidate is:

```python
Network(
    volatility_updates="standard",
    mean_field_updates=True,
    # precision_clipping_value: freeze in P2A.8
    # max_posterior_precision: freeze in P2A.8
)
.add_nodes(kind="binary-state")
.add_nodes(
    kind="continuous-state",
    value_children=([0], [1.0]),
    mean=0.0,
    precision=10.0,
    tonic_drift=0.0,
    tonic_volatility=-3.0,
    autoconnection_strength=1.0,
)
.add_nodes(
    kind="continuous-state",
    volatility_children=([1], [1.0]),
    mean=1.0,
    precision=1.0,
    tonic_drift=0.0,
    tonic_volatility=-6.0,
    autoconnection_strength=1.0,
)
```

This is a parameter mapping, not yet an authorized benchmark configuration: P2A.5–P2A.8 still have to pass.

## P2A.4 decision

```text
PARAMETER_MAPPING_GATE = PASS_FOR_FROZEN_DEFAULT_CANDIDATE_ONLY
```

The frozen default three-level HGFX candidate can be parameterized natively in pyhgf v0.3.2 without fitting or outcome-dependent tuning. Initial means, variances/precisions, drifts, middle/top tonic volatilities, and the top→middle volatility coupling all have a defined mapping.

The common scope is deliberately narrower than the full HGFX parameter family: **non-unit `ka[0]` is not authorized for direct comparison**, because pyhgf's binary prediction does not apply the value-edge coupling strength inside the sigmoid while HGFX does. This limitation must remain visible in the paper/evidence record.

## Machine-readable mapping

The same mapping is recorded in `paper/reproducibility/pyhgf_parameter_mapping.json` for later input/config generation and claim auditing.

## Next micro-step

**P2A.5 — Initial-state semantics.** Verify first-trial state construction and prediction/update ordering only. No numerical cross-tool trajectory comparison is authorized yet.
