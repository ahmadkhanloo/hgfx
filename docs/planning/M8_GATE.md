# M8 — Objective Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Objective source: frozen `fitModel.m`
- Validation workflow: `M8 Objective Parity`
- Passing workflow run: `34152468348`
- Numerical mode: CPU float64

## Gate definition

At fixed transformed parameter vectors, HGFX must match the frozen MATLAB objective decomposition before any optimizer is introduced.

The validated decomposition is:

```text
perceptual forward
    +
trial-wise observation log likelihoods
    ↓
remove exactly r.irr
    ↓
logLl / negLogLl
    +
perceptual Gaussian prior
    +
observation Gaussian prior
    ↓
negLogJoint
```

## Scope validated

- [x] generic optimizer-independent objective evaluator
- [x] vertical slice: standard `hgf_binary + unitsq_sgm`
- [x] regular fixed-vector case
- [x] ignored-input + irregular-response case
- [x] trial-wise log likelihoods
- [x] ignored input contributes to both ignored and irregular masks
- [x] NaN response contributes to irregular mask only
- [x] exactly irregular trials are removed before likelihood aggregation
- [x] regular-trial likelihood uses ordinary sum, not `nansum`
- [x] NaN regular likelihood maps `negLogLl` to `realmax`
- [x] perceptual prior index selection
- [x] observation prior index selection
- [x] zero prior variance means fixed/excluded
- [x] NaN prior variance is excluded from prior objective
- [x] Gaussian prior normalization matches `-0.5*log(2*pi*variance)`
- [x] Gaussian prior quadratic term matches MATLAB
- [x] full `negLogJoint`
- [x] perceptual failure path returns `realmax` and `rval=-1`
- [x] upstream HGF forward and observation regression tests preserved

## Numerical tolerance

- `rtol=2e-11`
- `atol=2e-13`

No tolerance was widened to obtain M8.

Two earlier CI attempts failed only because MATLAB `jsonencode` serializes singleton numeric vectors as scalar JSON values. The parity checker now normalizes scalar-vs-singleton-array representation before comparison. No scientific implementation changed because of those failures.

## Passing jobs

Workflow run `34152468348`:

- `python-objective-tests`: PASS
- `matlab-python-objective-parity`: PASS

## Scientific compatibility decisions frozen by M8

- Objective trial exclusion is defined by `r.irr`, not generic NaN dropping.
- An ignored input trial is also irregular; a missing response is irregular without being an ignored perceptual trial.
- Trial likelihood aggregation uses ordinary summation after explicit irregular-trial removal.
- If the remaining likelihood sum is NaN, frozen `negLogLl` becomes `realmax`; the raw joint expression is not silently repaired.
- Gaussian priors are evaluated only for prior variances that remain nonzero after MATLAB-style NaN-to-zero index selection.
- Prior densities are evaluated in transformed parameter space, matching `fitModel.m`.
- Perceptual forward failure uses the frozen `realmax` objective sentinel and `rval=-1`.

## Architecture decision

M8 freezes an optimizer-independent objective boundary. M9 must optimize this same compatibility objective rather than re-implementing likelihood or prior logic inside the optimizer.

## Next milestone

`M9 — Compatibility Fitting`
