# M18 D08 reference-limitation disposition

Status: **REFERENCE_LIMITATION_MATCH — exact failing-seed D08 scope only**

Decision record: `../../reference/validation/m18_d08_reference_limitation/decision.json`

Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## What remains failed

The prospectively frozen D08 Level-2 holdout remains **FAIL** as a set. Seed `271828182` passed its original Level-2 gate; seed `314159265` remained `INFERENCE_EQUIVALENCE_FAIL`. That failed experiment is preserved and is not relabeled as PASS.

For v1 release accounting only, the exact failing-seed workflow (`314159265`) is accepted as `REFERENCE_LIMITATION_MATCH` under `MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.

This is not a generic uHGF fit PASS, not a replacement of the failed seed, and not permission to widen tolerances.

## Evidence chain

1. **Prospective failure preserved.** Repaired-product holdout run `34842943696`, job `103971934494`, artifact `10347616859`, SHA-256 `8cbb16de519204710662d8bf0b94c2510df8c2e53f9427897b9f55d7d0b499f1` remains `gate_pass=false`. Seed `314159265` still fails final/H/Sigma/Corr/model-quality/prediction/residual/trajectory requirements; exact MATLAB-endpoint replay has no mismatch.
2. **Shared-state semantics do not show a material HGFX-only defect.** Optimizer diagnostic run `34842943657`, job `103971934637`, artifact `10347682339`, SHA-256 `3d94f74c71e5bf6bcdd8971d647ddba31f5a087cb4f3cb9a933c6a6e3c33518a` classifies `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`: shared objective/gradient checks remain within the frozen diagnostic gate and exact-state quasi-Newton/BFGS transition replay agrees.
3. **The evidence-linked prior/placeholder mismatch was repaired separately.** The repaired USDCHF prior preparation has already been validated exactly; the hard seed still fails afterward, so the residual mechanism is not an unresolved prior-contract mismatch.
4. **The remaining selected source-likelihood sample is semantically exact where it matters.** Run `34842943607`, artifact `10346549885`, SHA-256 `4e763e9978cb409eca5c7b468d5798b3a832aa023e382731284b9af47fb61275` reproduces observation input, trial log-likelihood, `yhat/res`, and the reduction exactly for the selected sample; an unrelated internal state retains only a one-ULP residual.
5. **The frozen MATLAB reference is itself basin-sensitive for the same failing seed.** Protocol `m18-d08-holdout-matlab-self-sensitivity-1`, run `34846375826`, job `103983208684`, artifact `10348900752`, SHA-256 `42874a324ef408205452516f0abe7497b60d5f12b9f9bf2972df105845f907f6`, first reproduces the reference endpoint exactly. Then 13 of 14 independent `+/-eps(x)` start perturbations terminate outside the unchanged `rtol=3e-8`, `atol=3e-10` endpoint gate.

## Integrity interpretation

No official seed, dataset, model family, start, optimizer, tolerance, or validation grid was changed to obtain this disposition. Perturbed starts are diagnostic reference evidence only; they never replace the official holdout start.

The conclusion is narrow: the exact seed `314159265` workflow is an ill-conditioned numerical-basin reproducibility case in the MATLAB reference itself. HGFX still fails direct/prospective endpoint parity there, but the residual mechanism is not supported as an HGFX-only semantic defect after shared-state and source-level localization.

## Release consequence

D08 no longer counts as an unresolved HGFX-only blocker for this exact failing-seed scope. The failed Level-2 holdout remains visible in release/paper evidence. Any other seed, dataset, runtime, start, model configuration, or optimizer regime must be evaluated independently.
