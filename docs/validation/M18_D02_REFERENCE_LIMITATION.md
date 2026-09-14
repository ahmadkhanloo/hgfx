# M18 D02 reference-limitation disposition

Status: **REFERENCE_LIMITATION_MATCH — exact D02 scope only**

Decision record: `../../reference/validation/m18_d02_reference_limitation/decision.json`

Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## What is and is not being accepted

The historical/direct D02 fit still fails direct MATLAB parity and its `INFERENCE_EQUIVALENCE_FAIL` record is preserved. It is **not** relabeled as `PASS` or `PASS_INFERENTIAL_EQUIVALENCE`.

For v1 release accounting, the exact official D02 workflow is now accepted as `REFERENCE_LIMITATION_MATCH` under `MATLAB_REFERENCE_LIMITATIONS_POLICY.md`: the remaining endpoint/inference disagreement is explained by a numerical-basin instability that is demonstrably present in the frozen MATLAB reference itself.

This classification applies only to the exact official D02 data/model/config/seed/start/optimizer regime.

## Evidence chain

1. **Direct mismatch preserved.** Historical run `34823572071` and current-product run `34834368877` both retain D02 as `OPTIMIZER_MISMATCH`; exact MATLAB endpoint replay and sampled MATLAB-path objective replay pass.
2. **Same-vector objective surface agrees.** `m18-d02-basin-probe-1`, run `34829122057`, evaluates nine preregistered exact shared parameter vectors and classifies `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE` with all nine points inside the unchanged gate.
3. **Optimizer algebra is not the material split.** Exact MATLAB-state quasi-Newton/BFGS replays agree at machine level. The frozen optimizer-source probe, run `34835728961`, has an exact source objective and localizes the first off-centre sample residual to `2.842170943040401e-14` in log-likelihood only; replaying Ridders with MATLAB samples reproduces the MATLAB derivative/error.
4. **The residual is binary64 primitive/reduction scale.** Source-likelihood run `34836421105` has exact inference states. Trial log-likelihood differences are at most `8.881784197001252e-16`; the first is `2.220446049250313e-16`. MATLAB's own vector `sum` differs from its scalar-loop reduction by `1.1368683772161603e-13` on the frozen sample.
5. **The MATLAB reference is itself basin-sensitive at one-spacing scale.** Protocol `m18-d02-matlab-self-sensitivity-1`, run `34837033370`, first reproduces the official MATLAB endpoint exactly, then changes one of the three free starting coordinates at a time by only `+/-eps(x)` (`4.440892098500626e-16`). All six runs terminate outside the existing numerical gate relative to the baseline; free-parameter shifts reach about `1.5077`.

Artifact provenance is recorded machine-readably in the decision JSON.

## Integrity interpretation

No threshold, seed, dataset, start used by the official workflow, model family, optimizer, or acceptance grid was changed to obtain acceptance. The perturbed starts are diagnostic reference evidence only and are never substituted for the official fit.

The conclusion is narrower than "numerical differences do not matter": D02 is a demonstrably ill-conditioned optimizer/basin reproducibility case under binary64 perturbations. That limitation exists in MATLAB itself, while HGFX agrees on the shared objective/forward contract before the unstable path amplification.

## Release consequence

D02 no longer counts as an unresolved HGFX-only blocker for the exact official workflow. It remains a disclosed reference limitation and a paper case study. Any new D02-family seed/regime must be evaluated independently; this classification cannot be inherited automatically.
