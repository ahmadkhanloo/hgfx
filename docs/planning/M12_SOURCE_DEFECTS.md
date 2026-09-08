# M12 — Frozen Source Defect Register

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

These are defects in the frozen MATLAB reference that prevent a direct clean execution of otherwise scientific model code. HGFX does not silently rewrite them. Each repair is minimal, documented, and applied only in the MATLAB oracle copy or explicitly in the Python compatibility implementation.

## D1 — continuous AR1 irregular intervals

File: `perceptual/hgf_ar1.m`

The source first creates `u = [0; r.u(:,1)]`, discarding interval columns, and then checks `size(u,2)` inside a try/catch. With `irregular_intervals=true`, the explicit single-column error is caught by the broad catch, whose fallback sets unit intervals.

Compatibility decision: preserve the frozen behavior. HGFX continuous AR1 uses unit intervals even when the incoming matrix contains an interval column.

## D2 — continuous AR1 MAB dummy choice

File: `perceptual/hgf_ar1_mab.m`

The source prepends a dummy choice:

```matlab
y = [0; r.u(:,2)];
```

but removes the dummy rows from trajectories without removing `y(1)`. The later `sub2ind` calls therefore receive vectors of different lengths and the canonical function errors while constructing `psi`.

Oracle repair: execute an exact temporary copy of the frozen file with the minimal addition `y(1)=[]` immediately after removal of dummy trajectory values.

## D3 — WhichWorld undefined variable

File: `perceptual/hgf_whichworld.m`

The learning-rate cleanup uses:

```matlab
lr1(da(2:n,1)==0) = 0;
```

but the model defines `da1` and `da2`, not `da`.

Oracle/Python repair: interpret this line as `da1(2:n,1)`. All recursion before that line remains frozen-source identical.

## D4 — HHMM function/file naming

Files:

- `perceptual/tapas_hhmm.m` declares `htapas_hmm`
- `perceptual/tapas_hhmm_config.m` declares `hhmm_config`
- `perceptual/tapas_hhmm_transp.m` declares `hhmm_transp`

The filenames and public handles use the `tapas_*` naming surface, while the declared functions do not match it. The native call path also assumes `pstruct` although it is only constructed by the transform path.

Oracle repair: temporary copies align function names with filenames and call the transform explicitly. HGFX exposes a usable `hierarchical_hidden_markov_model` plus tree/config transformation helpers.

## D5 — world softmax likelihood parameter reuse

File: `observation/softmax_wld.m`

The transform declares three parameters: beta, win distortion, and loss distortion. The likelihood then uses:

```matlab
be    = exp(ptrans(1));
la_wd = ptrans(1);
la_ld = ptrans(2);
```

so `ptrans(1)` controls both beta and win distortion and `ptrans(3)` is ignored.

Compatibility decision: HGFX preserves this likelihood behavior exactly.

## D6 — world softmax simulation/likelihood mismatch

File: `observation/softmax_wld_sim.m`

The simulation receives native parameters but assigns `be = p`, then also uses `p(1)` and `p(2)` as win/loss distortion. This differs from the likelihood's scalar-beta behavior.

Compatibility decision: simulation keeps its own frozen semantics rather than being normalized to the likelihood semantics.

## D7 — Bayes-optimal WhatWorld irregular tensor deletion

File: `perceptual/bayes_optimal_whatworld.m`

The source obtains a three-dimensional prediction tensor and then deletes irregular trials using:

```matlab
pred(r.irr,:) = [];
```

With a non-empty irregular-trial set, MATLAB collapses trailing dimensions under this two-subscript deletion. The later three-subscript access `pred(k,to,from)` can then exceed the remaining third dimension.

Oracle repair: preserve the tensor rank explicitly with `pred(r.irr,:,:) = []`. HGFX already removes irregular trials without collapsing the transition dimensions.

## Gate rule

A frozen source defect does not exempt a scientific family from implementation. A repaired family is DONE only when:

1. the defect is documented here;
2. the repair is minimal and traceable;
3. the unaffected frozen equations remain unchanged;
4. MATLAB repaired-oracle ↔ HGFX parity passes;
5. the complete regression suite stays green.
