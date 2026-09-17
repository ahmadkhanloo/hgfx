# PV1-02A — HGFX vs pyhgf output-quantity semantics

Status: **P2A.7 COMPLETE — OUTPUT QUANTITIES MAPPED; NUMERICAL GUARDS DEFERRED**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope

This micro-step maps the scientific meaning of the candidate output quantities for the frozen, fully observed, unit-time three-level binary-HGF surface carried forward from P2A.6.

It answers four questions before any cross-tool numerical execution:

1. which posterior/predicted trajectories have the same scientific meaning;
2. which first-level binary quantities are representation-specific and must not be compared directly;
3. how pyhgf's binary input surprise relates to HGFX forward predictions;
4. how HGFX `unitsq_sgm` response log-likelihood relates to pyhgf's inverse-temperature binary-softmax surprise.

Floating-point precision, clipping, posterior-precision caps, and dtype policy remain P2A.8. No HGFX↔pyhgf numerical trajectory or surprise benchmark was executed while choosing this mapping.

## Frozen sources

### HGFX

Immutable product source: `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

- `src/hgfx/models/hgf_binary.py` — blob `e1aec3e8bbc8623f81532601a7d1c53e23278e12`; defines `traj` and `inf_states = stack(muhat, sahat, mu, sa)`.
- `src/hgfx/responses/unitsq_sigmoid.py` — blob `4860d3f7f85886b89ca94783d0ef6133f16a5474`; defines `unitsq_sgm` log probability, returned belief prediction, and standardized residual.

### pyhgf

Comparator: `pyhgf==0.3.2`, tag `v0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.

- `pyhgf/model/network.py` — blob `36bd2cb10235e72d0185e2a8f104148a3e89852e`; records `node_trajectories` during belief propagation.
- `pyhgf/response.py` — blob `44dd8bf37d546b4f285007c993285f08faf60d10`; defines first-level binary surprise and binary-softmax response surprise.
- `pyhgf/math.py` — blob `148e940c3b0e61dc4a823366540d32fa21a0ee8f`; defines `binary_surprise(...)` and its default probability clipping.

## Canonical trajectory-name mapping

For the continuous latent levels (HGFX levels 2 and 3; pyhgf continuous nodes 1 and 2), the following quantities have the same scientific interpretation under the already-frozen P2A.3–P2A.6 equation/parameter/initialization/input restrictions:

| Scientific quantity | HGFX | pyhgf | Classification | Direct-comparison rule |
|---|---|---|---|---|
| posterior mean | `traj["mu"][:, j]` | node `mean` | `MATCH_IN_MEANING` | Authorized candidate for levels 2–3, pending P2A.8 numerical policy. |
| predicted/expected mean | `traj["muhat"][:, j]` | node `expected_mean` | `MATCH_IN_MEANING` | Authorized candidate for levels 2–3, pending P2A.8. |
| posterior precision | `1 / traj["sa"][:, j]` (internally `pi`) | node `precision` | `MATCH_IN_MEANING` | Authorized candidate for levels 2–3, pending P2A.8. |
| predicted/expected precision | `1 / traj["sahat"][:, j]` (internally `pihat`) | node `expected_precision` | `MATCH_IN_MEANING` | Authorized candidate for levels 2–3, pending P2A.8. |
| posterior variance | `traj["sa"][:, j]` | reciprocal of node `precision` | `TRANSFORM_REQUIRED` | Compare only after reciprocal conversion. |
| predicted variance | `traj["sahat"][:, j]` | reciprocal of node `expected_precision` | `TRANSFORM_REQUIRED` | Compare only after reciprocal conversion. |

This mapping does not claim that every implementation-specific intermediate array is identical. It defines only common scientific quantities.

## Binary first-level trajectory

HGFX standard `hgf_binary` stores the observed binary first level as the posterior mean and stores its Bernoulli prediction as `muhat[:, 0]`. In `inf_states`, index `[..., 0, 0]` is the predicted first-level belief and index `[..., 0, 2]` is the posterior/observed value.

pyhgf's binary input node similarly exposes:

- `expected_mean`: predicted probability of outcome `1` before observing the current binary input;
- `mean`: the observed binary value after observation assignment.

Therefore:

```text
HGFX muhat[:, 0]  <->  pyhgf binary-node expected_mean
HGFX mu[:, 0]     <->  pyhgf binary-node mean / observed input
```

Classification: **`MATCH_IN_MEANING_PENDING_P2A8`**.

The posterior first-level value is scientifically trivial for this observed-node surface because it is the supplied input itself; it may be retained as an integrity check but is not a headline numerical metric.

## First-level binary precision is not a direct output metric

HGFX represents the observed binary level with `pi = inf` and hence `sa = 0` after observation. pyhgf carries binary-node uncertainty/precision through its own Bernoulli prediction representation and numerical clipping policy.

P2A.3 already established that the level-2 update can be algebraically equivalent despite this different internal binary-precision representation.

Consequently:

```text
HGFX level-1 pi / sa  X  pyhgf binary-node precision-like internals
```

Classification: **`NOT_DIRECTLY_COMPARABLE_AS_REPORTED_INTERNALS`**.

No paper table may present these internal first-level precision fields as if they were the same quantity.

## Prediction-error quantities

The canonical first-level value prediction error is unambiguous:

```text
PE1 = observed_binary_input - predicted_probability
```

For HGFX this is the scientific content of `da[:, 0]`. For the cross-tool comparison, the authorized form is the **derived canonical quantity** constructed from each implementation's mapped observed input and predicted probability, rather than relying on implementation-specific prediction-error field names or storage conventions.

Classification: **`DERIVED_COMMON_QUANTITY`**.

Higher-level volatility-prediction-error and weighting intermediates are not required by the paper's candidate common surface and are excluded from the direct comparison unless a later protocol explicitly activates them.

## pyhgf first-level binary surprise

`pyhgf.response.first_level_binary_surprise(...)` computes binary surprise from the observed binary input and the binary input node's `expected_mean`. Ignoring numerical clipping for the moment, the mathematical quantity is:

```text
S_input = -log(p)       if u = 1
S_input = -log(1 - p)   if u = 0
```

with `p = binary-node expected_mean`.

HGFX does not expose this exact perceptual input-surprise quantity as a dedicated `hgf_binary` response helper. However, the same scientific quantity can be derived without introducing a new model assumption from:

```text
u = input sequence
p = traj["muhat"][:, 0]
```

Thus first-level **input surprise** is a valid derived common quantity, but native wrapper equality is not yet authorized because pyhgf's `binary_surprise` clips its probability argument by default. That clipping is a P2A.8 numerical-policy question.

Classification: **`DERIVED_COMMON_QUANTITY_PENDING_CLIPPING_POLICY`**.

## Do not confuse input surprise with participant-response likelihood

pyhgf's `first_level_binary_surprise` measures surprise of the **input observation under the perceptual model**. HGFX `unitsq_sgm` instead models a **participant binary response conditional on the model belief**.

These are distinct scientific quantities and must not be compared merely because both involve a binary negative log probability.

Classification:

```text
pyhgf first_level_binary_surprise  X  HGFX unitsq_sgm response logp
= DIFFERENT_QUANTITY
```

## HGFX `unitsq_sgm` versus pyhgf inverse-temperature binary softmax

HGFX `unitsq_sgm` uses the predicted first-level belief by default (`predorpost=1`) and transforms it with native inverse temperature

```text
ze = exp(logze)
```

For predicted belief `p`, participant response `y in {0,1}`, and inverse temperature `ze`, define

```text
q = p^ze / (p^ze + (1-p)^ze)
```

HGFX returns the per-trial response log probability

```text
logp = y*log(q) + (1-y)*log(1-q)
```

expressed algebraically in a numerically compatible form.

pyhgf `binary_softmax_inverse_temperature(...)` applies the same power/log-odds transform to the binary node's `expected_mean`, then returns `binary_surprise(response, q)`, i.e. the negative log probability of the participant response.

Therefore, before pyhgf's probability-clipping guard is considered:

```text
pyhgf binary_softmax_inverse_temperature surprise = - HGFX unitsq_sgm logp
```

provided all of the following are matched:

```text
same predicted first-level probability p
same participant response y
pyhgf response_function_parameters == HGFX native ze
HGFX predorpost == 1
```

Classification: **`ALGEBRAIC_MATCH_WITH_SIGN_CONVERSION_PENDING_CLIPPING_POLICY`**.

The simpler pyhgf `binary_softmax(...)` corresponds only to the special case `ze = 1`; it is not the general common-scope observation function.

## `yhat` and residual are not additional common response outputs

HGFX `unitsq_sgm` returns `(logp, yhat, res)`, but its `yhat` is the untransformed input belief `p`, not the temperature-transformed response probability `q`. pyhgf's response helper returns surprise only.

Accordingly:

- HGFX `yhat` is redundant with the mapped first-level predicted belief and should be compared there, not treated as pyhgf's response probability;
- HGFX standardized residual has no directly returned pyhgf counterpart in this response helper and is outside the common scope.

Classification: **`NO_ADDITIONAL_NATIVE_RESPONSE_OUTPUT_MATCH`**.

## Authorized P2A candidate outputs after this step

Subject to P2A.8 precision/numerical policy, the direct empirical candidate may compare:

1. first-level predicted probability (`muhat[:,0]` / binary `expected_mean`);
2. continuous level-2 posterior mean and predicted mean;
3. continuous level-3 posterior mean and predicted mean;
4. continuous level-2 posterior and predicted precision (or reciprocal variance after explicit transform);
5. continuous level-3 posterior and predicted precision (or reciprocal variance after explicit transform);
6. canonical first-level prediction error derived as `u - predicted_probability`;
7. canonical first-level input surprise derived from the mapped predicted probability and input, **only under the clipping policy frozen in P2A.8**;
8. participant-response negative log likelihood using HGFX `-logp` versus pyhgf inverse-temperature binary-softmax surprise, **only under the clipping policy frozen in P2A.8** and with the same fixed inverse temperature and response sequence.

The candidate must not directly compare:

- first-level binary precision/variance internals;
- higher-level implementation-specific PE/weighting intermediates (`v`, `w`, `psi`, `epsi`, `wt`) as if names implied semantic identity;
- pyhgf first-level input surprise against HGFX `unitsq_sgm` response likelihood;
- HGFX standardized response residual against a non-existent pyhgf returned residual.

## P2A.7 decision

```text
OUTPUT_QUANTITY_GATE = PASS_FOR_MAPPED_TRAJECTORY_AND_RESPONSE_QUANTITIES_PENDING_P2A8
```

The candidate remains viable. The important semantic distinction is now frozen: **perceptual input surprise and participant-response surprise are separate quantities**. The response-model surface does have a mathematical common scope through HGFX `unitsq_sgm` and pyhgf `binary_softmax_inverse_temperature`, with a sign conversion, but native numerical equivalence remains conditional on P2A.8 clipping/precision policy.

`benchmark_authorized` remains **false**.

## Next micro-step

**P2A.8 — Precision and numerical-guard policy.** Freeze dtype/precision mode and resolve the material guard differences already identified: pyhgf binary `precision_clipping_value`, `binary_surprise` probability clipping, and `max_posterior_precision`. Determine prospectively whether they can be configured or bounded without changing the intended common scientific semantics.