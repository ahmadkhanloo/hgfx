# MATLAB Reference Limitations Policy

## Purpose

HGFX v1.0 targets functional and scientific equivalence with the frozen MATLAB HGF Toolbox 8.2.0 reference (`2437f4dc241541072722a2695ddeca7b44d83dd3`).

Scientific validation must therefore reproduce both the **capabilities** and the **known limitations / model-selection behavior** of the MATLAB toolbox. HGFX is not required to make a base HGF pass a scientific case that the MATLAB reference itself cannot solve with that same model.

## Governing rule

For every M18 validation scenario, the reference question is:

> What model family, observation model, workflow, parameterization, and validated operating regime does the MATLAB toolbox use successfully for this scientific case?

HGFX passes the product-level equivalence criterion when it reproduces that reference behavior within the established numerical/scientific tolerances.

Examples:

- if the MATLAB reference succeeds with `hgf_binary`, HGFX must reproduce the corresponding HGF workflow;
- if the MATLAB reference requires `ehgf_binary`, HGFX is not required to force `hgf_binary` to pass the same case;
- if the MATLAB reference requires `uhgf_binary` or a specialized observation model, the equivalent HGFX model path is the required path;
- if the MATLAB reference exhibits a documented identifiability or numerical-horizon limitation for the same workflow and regime, a matching HGFX limitation may be classified as **REFERENCE_LIMITATION_MATCH** rather than an HGFX defect.

## Required classification

Every non-PASS M18 result must be classified into exactly one primary class:

1. `IMPLEMENTATION_MISMATCH` — HGFX differs materially from the frozen MATLAB reference where MATLAB provides valid comparable output.
2. `OPTIMIZER_MISMATCH` — equations/forward behavior agree but fitting behavior diverges from the MATLAB reference.
3. `REFERENCE_LIMITATION_MATCH` — the same scientific/numerical limitation is demonstrated in the frozen MATLAB reference for the same workflow and operating regime.
4. `MODEL_SELECTION_MISMATCH` — HGFX uses or requires a different model family / observation model than the MATLAB reference for the case.
5. `INSUFFICIENT_REFERENCE_EVIDENCE` — MATLAB behavior has not yet been established strongly enough to classify the HGFX result.

`REFERENCE_LIMITATION_MATCH` is acceptable for MATLAB-equivalence v1.0. It is not a scientific PASS claim for the underlying model.

## Evidence required for REFERENCE_LIMITATION_MATCH

This classification may be used only when all of the following are recorded:

- frozen MATLAB reference commit;
- exact demo/script/config/model family;
- input dataset or deterministic generator and seed;
- trial count / operating regime;
- MATLAB result or failure mode;
- HGFX result or failure mode;
- evidence that both failures are scientifically/numerically comparable;
- no earlier divergence indicating an HGFX-only implementation error.

Without this evidence, the result remains `INSUFFICIENT_REFERENCE_EVIDENCE`.

## Model-family rule

M18 must never use a universal requirement of the form "base HGF must pass all scientific scenarios".

The validated unit is the MATLAB toolbox **workflow**, which may legitimately select among HGF, eHGF, uHGF, specialized perceptual models, and specialized observation models.

## Numerical horizon

Long-sequence instability (for example the currently observed 512-trial extension) must not be labeled an acceptable reference limitation until the same case is run against the frozen MATLAB reference and the first divergence/failure is compared.

Outcomes:

- MATLAB stable, HGFX unstable -> `IMPLEMENTATION_MISMATCH`;
- MATLAB and HGFX fail comparably in the same regime -> `REFERENCE_LIMITATION_MATCH`;
- evidence ambiguous -> `INSUFFICIENT_REFERENCE_EVIDENCE`.

## Release interpretation

HGFX v1.0 product acceptance requires:

- no unresolved `IMPLEMENTATION_MISMATCH` in required MATLAB workflows;
- no unresolved `MODEL_SELECTION_MISMATCH` in required MATLAB workflows;
- every accepted limitation to have explicit frozen-reference evidence;
- MATLAB demo/workflow parity across the supported reference surface;
- reference-equivalent limitations documented rather than hidden or silently relaxed.

Scientific extensions that improve beyond MATLAB may be introduced later, but they are not required for MATLAB-equivalence v1.0.
