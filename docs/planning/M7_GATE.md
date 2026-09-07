# M7 — Observation Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Validation workflow: `M7 Observation Parity`
- Passing workflow run: `34143177077`
- Numerical mode: CPU float64

## Gate definition

M7 passes only when all P0/P1 observation families match the frozen MATLAB implementation for trial-wise likelihoods and total likelihood.

## P0/P1 scope validated

| ID | MATLAB family | Priority | Status |
|---|---|---|---|
| O01 | `beta_obs` | P1 | PASS |
| O02 | `cdfgaussian_obs` | P1 | PASS |
| O06 | `gaussian_obs` | P1 | PASS |
| O07 | `gaussian_obs_offset` | P1 | PASS |
| O08 | `logrt_linear_binary` | P1 | PASS |
| O09 | `logrt_linear_binary_minimal` | P1 | PASS |
| O11 | `softmax` | P1 | PASS |
| O12 | `softmax_2beta` | P1 | PASS |
| O13 | `softmax_binary` | P0 | PASS |
| O14 | `softmax_mu3` | P1 | PASS |
| O17 | `unitsq_sgm` | P0 | PASS |
| O18 | `unitsq_sgm_mu3` | P1 | PASS |

## Quantities compared

For each deterministic oracle case:

- [x] trial-wise `logp`
- [x] `yhat`
- [x] residual `res`
- [x] total regular-trial log likelihood
- [x] irregular trial positions remain NaN
- [x] transformed positive parameters use MATLAB `exp(ptrans)` semantics
- [x] prediction/posterior selection where applicable
- [x] MATLAB-style categorical choice indexing
- [x] special softmax-2beta tensor layout

## Numerical tolerance

- `rtol=2e-11`
- `atol=2e-13`

No model-specific relaxed tolerance was introduced.

## Oracle design

Observation equations are tested on deterministic synthetic `infStates`, independently from perceptual forward recursion. This isolates observation parity from M4–M6 and prevents a perceptual-model error from being masked by the response layer.

The fixture includes an explicit irregular trial and records total likelihood after excluding NaN trials.

## Passing jobs

Workflow run `34143177077`:

- `python-observation-tests`: PASS
- `matlab-python-observation-parity`: PASS

## Architecture decision

Observation functions live under `hgfx.responses` and consume MATLAB-compatible inferred states plus transformed response parameters. Objective aggregation is deliberately left for M8 so that M7 establishes a clean likelihood boundary.

## Next milestone

`M8 — Objective Parity`
