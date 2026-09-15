# M18 D02 source-likelihood diagnostic

Status: **DIAGNOSTIC ONLY — NO ACCEPTANCE EFFECT**

Protocol: `m18-d02-source-likelihood-probe-1`

## Why this diagnostic exists

The frozen D02 optimizer-source probe (`m18-d02-optimizer-source-probe-1`) localized the first exact finite-difference mismatch at MATLAB optimizer trace row 7 (1-based), free component 1, Ridders step 2, plus side. The source objective itself is exact, but this sample differs by `2.842170943040401e-14`, entirely in the log-likelihood term. MATLAB-sample Ridders replay is exact, so optimizer algebra must not be changed before the likelihood residual is localized.

## Frozen sample

This diagnostic therefore fixes, before execution:

- case: `D02_fit`
- reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- input: `demo/example_binary_input.txt`
- simulation seed: `123456789`
- simulation: `ehgf_binary + unitsq_sgm`
- simulation native parameters: `[NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3]`
- fit: `ehgf_binary + unitsq_sgm`
- observation prior variance: `0.5`
- optimizer: frozen default `quasinewton_optim_config`
- MATLAB source trace row: `7` (1-based)
- free component: `1` (1-based; full transformed index 13)
- Ridders step: `2` (1-based), `h = 1/1.2`
- side: `plus`

No seed, dataset, start, model, optimizer, tolerance, or acceptance criterion is changed.

## What is compared

At the exact frozen MATLAB finite-difference vector, export and compare:

1. full transformed vector and inference states;
2. observation probability input and transformed response parameter;
3. every trial log-likelihood;
4. MATLAB `sum` and explicit scalar-loop reductions;
5. the workflow log-likelihood produced by HGFX;
6. unit-square-sigmoid primitive arrays, including the active log paths, powers, denominator, and formula terms;
7. a replay of the HGFX observation formula on the exact MATLAB observation state.

The focused trial is selected mechanically as the first trial whose log-likelihood differs at this already-frozen sample.

## Diagnostic classifications

- `FORWARD_NUMERICAL_DIVERGENCE`: exact sample reaches different inference states.
- `OBSERVATION_PRIMITIVE_DIVERGENCE`: inference states match but one or more trial likelihoods differ.
- `LIKELIHOOD_REDUCTION_DIVERGENCE`: trial likelihoods match but the aggregate workflow likelihood differs.
- `NO_LIKELIHOOD_DIVERGENCE_AT_SELECTED_SAMPLE`: the selected sample is exact at this level; the residual must be above/below this probe boundary.

None of these classifications is a milestone PASS. D02 remains **BLOCKED** until its documented release gate is satisfied.
