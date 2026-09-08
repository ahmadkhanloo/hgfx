# M12 — Specialized Model Coverage Matrix

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Status semantics

- **DONE** — Python implementation exists and is covered by a frozen MATLAB parity gate (or an earlier completed gate).
- **REFERENCE_ONLY** — the frozen MATLAB family is inventoried and retained as a scientific reference, but HGFX does **not** claim a compatible implementation for it in v1 compatibility scope.
- No perceptual/observation family may remain unclassified.

The machine gate is `tools/check_m12_inventory.py`.

Current exhaustive inventory result:

- DONE files: **146**
- REFERENCE_ONLY files: **113**
- DONE families: **32**
- REFERENCE_ONLY families: **21**

## Perceptual / latent-state families

| Family | Status | Evidence / reason |
|---|---|---|
| Standard continuous HGF | DONE | M4 MATLAB golden forward parity |
| Standard binary HGF | DONE | M4 MATLAB golden forward parity |
| Standard continuous eHGF | DONE | M5 MATLAB golden forward parity |
| Standard binary eHGF | DONE | M5 MATLAB golden forward parity |
| Standard continuous uHGF | DONE | M6 MATLAB golden forward parity |
| Standard binary uHGF | DONE | M6 MATLAB golden forward parity |
| Binary PU HGF | DONE | M12 MATLAB forward oracle |
| Binary PU eHGF | DONE | M12 MATLAB forward oracle |
| Binary PU uHGF | DONE | M12 MATLAB forward oracle |
| Binary PU-TBT HGF | DONE | M12 MATLAB forward oracle |
| Binary PU-TBT eHGF | DONE | M12 MATLAB forward oracle |
| Binary PU-TBT uHGF | DONE | M12 MATLAB forward oracle |
| AR1 binary HGF | DONE | M12 MATLAB forward oracle |
| AR1 binary eHGF | DONE | M12 MATLAB forward oracle |
| AR1 binary uHGF | DONE | M12 MATLAB forward oracle |
| Rescorla-Wagner binary | DONE | M12 MATLAB forward oracle |
| Dual Rescorla-Wagner | DONE | M12 MATLAB forward oracle |
| Pearce-Hall binary | DONE | M12 MATLAB forward oracle |
| Sutton K1 binary | DONE | M12 MATLAB forward oracle |
| Scalar Kalman filter | DONE | M12 MATLAB forward oracle |
| HMM | DONE | M12 MATLAB forward oracle |
| Continuous AR1 HGF | REFERENCE_ONLY | distinct continuous AR1 parameter layout; outside the P1 binary specialized gate |
| Binary MAB | REFERENCE_ONLY | multi-arm state tensors and reward-coded inputs require a dedicated compatibility API |
| Continuous AR1 MAB | REFERENCE_ONLY | multi-arm continuous tensor semantics require a dedicated compatibility API |
| AR1 binary MAB HGF | REFERENCE_ONLY | multi-arm reward/state tensor semantics require dedicated fixtures |
| AR1 binary MAB eHGF | REFERENCE_ONLY | multi-arm reward/state tensor semantics require dedicated fixtures |
| AR1 binary MAB uHGF | REFERENCE_ONLY | multi-arm reward/state tensor semantics require dedicated fixtures |
| JGET HGF | REFERENCE_ONLY | specialized JGET recursion/parameterization requires an independent scientific fixture |
| JGET eHGF | REFERENCE_ONLY | specialized JGET recursion/parameterization requires an independent scientific fixture |
| JGET uHGF | REFERENCE_ONLY | specialized JGET recursion/parameterization requires an independent scientific fixture |
| Categorical HGF | REFERENCE_ONLY | multinomial tensor recursion is outside binary/continuous core |
| Categorical normalized HGF | REFERENCE_ONLY | multinomial tensor recursion is outside binary/continuous core |
| WhatWorld HGF | REFERENCE_ONLY | high-dimensional transition/world latent-state semantics require dedicated fixtures |
| WhichWorld HGF | REFERENCE_ONLY | world-mixture latent-state semantics require dedicated fixtures |
| HHMM | REFERENCE_ONLY | frozen `tapas_hhmm.m` declares `htapas_hmm` and uses nontrivial tree flattening; source repair/fixture required before a compatibility claim |
| Bayes-optimal auxiliary families | REFERENCE_ONLY | located under `perceptual/` but implement auxiliary likelihoods rather than an independent latent-state recursion |
| Response-surprise auxiliary families | REFERENCE_ONLY | auxiliary belief/precision/surprise analysis models |
| Squared prediction-error auxiliary | REFERENCE_ONLY | deterministic auxiliary analysis model, not compatibility-core forward recursion |

## Observation families

### DONE through M7

- beta observation
- CDF Gaussian
- Gaussian / Gaussian offset
- binary logRT / minimal binary logRT
- categorical softmax
- two-beta softmax
- binary softmax
- mu3 softmax
- unit-square sigmoid
- mu3 unit-square sigmoid

### REFERENCE_ONLY

| Family | Reason |
|---|---|
| Conditional hallucination 1/2/3 | P2 family coupled to specialized conditional-hallucination integrations |
| WhatWorld logRT | depends on reference-only WhatWorld state layout |
| World softmax | depends on reference-only world state layout |
| World mu3 softmax | depends on reference-only world state layout |

## M12 implemented Python modules

- `src/hgfx/models/hgf_binary_pu.py`
- `src/hgfx/models/hgf_ar1_binary.py`
- `src/hgfx/models/legacy.py`

Public exports are available through `hgfx.models`.

## PyHGF dependency/fork decision

**Decision: do not fork PyHGF and do not make it a required compatibility-core runtime dependency.**

Reasoning from the parity work through M12:

1. HGFX already has a frozen MATLAB-compatible scientific core with explicit source-specific semantics.
2. Several compatibility details are deliberately source-specific, including ignored-trial state copying, binary level-2 unit-time behavior, uHGF approximation/fallback details, and compatibility fitting/Hessian semantics.
3. Introducing PyHGF underneath the compatibility layer now would add a second semantic translation boundary after the MATLAB parity gates have already been established.
4. A fork would create upstream-maintenance cost without evidence that it improves frozen-toolbox parity.
5. PyHGF remains useful as an **optional interoperability/research comparison target**, not as HGFX's source of truth.

Therefore:

```text
HGF Toolbox 8.2.0 frozen source = compatibility specification
HGFX implementation            = compatibility runtime
PyHGF                           = optional external comparison/interoperability
```

This decision can be revisited for native APIs, but changes to the compatibility core must continue to be judged against frozen MATLAB golden tests.
