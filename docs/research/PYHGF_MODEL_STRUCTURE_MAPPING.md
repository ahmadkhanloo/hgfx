# PV1-02A — HGFX vs pyhgf model-structure mapping

Status: **P2A.2 COMPLETE — MODEL STRUCTURE MAPPED**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step evaluates **model structure only** for the candidate common surface: a fixed-parameter three-level binary HGF forward trajectory.

It does **not** compare update equations, parameter transforms, initial-state semantics, masking, output quantities, precision, or numerical trajectories. Those remain separate P2A gates. A structural match alone does not authorize a direct empirical comparison.

## Frozen sources inspected

### HGFX

- repository/source revision used for this mapping: `6b1b3535201321d9c2e89a7c66e9cba20e6a0edd`
- candidate implementation: `src/hgfx/models/hgf_binary.py`
  - blob SHA: `e1aec3e8bbc8623f81532601a7d1c53e23278e12`
- compatibility configuration: `src/hgfx/compat/configs.py`
  - blob SHA: `76469aa702a3983c92bb48465ed084f16760f039`
- immutable product release remains `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

### pyhgf

- comparator: `pyhgf==0.3.2`
- tag: `v0.3.2`
- tag commit: `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`
- canonical three-level binary test fixture: `tests/test_nodes/test_binary.py`
  - blob SHA: `e9310a76971b3c3cdf78aa9610560b4cc9e758d3`
- network API/constructor: `pyhgf/model/network.py`
  - blob SHA: `36bd2cb10235e72d0185e2a8f104148a3e89852e`

## Candidate topology

### HGFX

`hgf_binary_config()` fixes `n_levels=3`. The forward recursion parses three-element `mu_0`, `sa_0`, and `rho` vectors and maintains trajectory arrays with `l=3` columns.

Structurally, the recursion is:

```text
observed binary input u
        |
        v
Level 1: binary state / binary prediction-error surface
        ^
        | value coupling (ka[0])
        |
Level 2: continuous state
        ^
        | volatility coupling (ka[1], om[1])
        |
Level 3: continuous volatility state
```

Evidence in the implementation:

- level 1 is updated by `hgf_binary_level1(...)` from the observed binary input and the prediction from level 2;
- level 2 is updated by `hgf_binary_level2(...)` and its predicted precision depends on level 3;
- the final/top level uses the top-level prediction/precision update and volatility update;
- the compatibility configuration explicitly freezes `n_levels: 3`.

### pyhgf v0.3.2

The canonical three-level binary fixture constructs:

```python
Network()
.add_nodes(kind="binary-state")
.add_nodes(kind="continuous-state", value_children=0, ...)
.add_nodes(kind="continuous-state", volatility_children=1, ...)
```

The source documents the topology explicitly as:

```text
Node 0: binary-state input node
Node 1: continuous-state, value parent of Node 0
Node 2: continuous-state, volatility parent of Node 1
```

The generic `Network.add_nodes(...)` API permits value and volatility parent/child edges and therefore represents this hierarchy as an explicit graph rather than a fixed ordered model function.

## Structural mapping table

| Structural item | HGFX `hgf_binary` | pyhgf `v0.3.2` candidate | P2A.2 classification | Consequence |
|---|---|---|---|---|
| Number of levels/nodes in candidate hierarchy | 3 levels | 3 nodes | `MATCH` | Candidate common topology exists. |
| Lowest level | Binary state driven by observed binary input | Node 0 `binary-state`, input node | `MATCH` | Same structural role; numerical semantics deferred. |
| Middle level | Continuous latent state | Node 1 `continuous-state` | `MATCH` | Same node type at structural level. |
| Middle-to-low relation | Level 2 acts as value parent of binary level through `ka[0]` | Node 1 has `value_children=0` | `MATCH` | Same value-coupling direction. |
| Top level | Continuous latent volatility state | Node 2 `continuous-state` | `MATCH` | Same structural node type. |
| Top-to-middle relation | Level 3 controls Level 2 predicted variance/precision through volatility coupling | Node 2 has `volatility_children=1` | `MATCH` | Same volatility-coupling direction. |
| Representation style | Fixed ordered toolbox-compatible hierarchy | General node/edge graph | `DIFFERENT_BUT_COMPATIBLE_FOR_CANDIDATE` | Abstraction differs but does not itself block this instantiated topology. |
| Candidate update-family default | `hgf_binary` freezes `update_type="hgf"` | `Network()` defaults to `volatility_updates="unbounded"` | `DIFFERENT_DEFER_TO_P2A_3` | Structural gate remains open; update-equation equivalence must be checked next. |
| Ability to instantiate the same three-node edge pattern without changing library architecture | Native fixed model | Native graph construction | `MATCH` | No structural workaround is required. |

## P2A.2 decision

```text
MODEL_STRUCTURE_GATE = PASS_FOR_TOPOLOGY_ONLY
```

The candidate fixed-parameter three-level binary HGF has a structurally corresponding topology in HGFX and pyhgf v0.3.2:

1. binary observed state at the bottom;
2. continuous value parent in the middle;
3. continuous volatility parent at the top;
4. value coupling from middle to bottom;
5. volatility coupling from top to middle.

This result is deliberately narrow. It does **not** establish that the two implementations perform the same mathematical updates.

A material unresolved difference is already visible: HGFX `hgf_binary` selects the standard/original `hgf` update branch, whereas a bare pyhgf `Network()` defaults to `unbounded` volatility updates. Whether pyhgf's `volatility_updates="standard"` gives the equation-level semantics needed for a fair candidate comparison is the subject of **P2A.3** and must be decided from source equations before any numerical run.

## Next micro-step

**P2A.3 — Update-equation mapping**

Compare only the prediction and posterior-update equations required by this three-level topology, including the explicit pyhgf update mode. The next step must classify the equation surface as `MATCH`, `DIFFERENT`, or `UNCERTAIN`; no trajectory benchmark is authorized yet.
