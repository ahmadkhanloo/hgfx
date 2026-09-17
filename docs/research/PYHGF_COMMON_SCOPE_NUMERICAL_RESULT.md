# PV1-02A — HGFX vs pyhgf frozen common-scope numerical result

Status: **P2A.10 COMPLETE — PARTIAL MATCH WITH RESPONSE-NLL NDC**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Case: `p2a9-binary-hgf-common-scope-001`  
Tracking: issue #33  
Date: 2026-09-17

## Decision

```text
COMMON_SCOPE_NUMERICAL_RESULT = PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES
perceptual_and_trajectory_quantities = 11 / 11 PASS_FOR_EXECUTED_QUANTITY
participant_response_nll_per_trial = NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY
participant_response_nll_total = NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY
```

This is a deliberately narrow result for the single prospectively frozen three-level binary-HGF case. It is **not** a claim of general HGFX↔pyhgf equivalence, general superiority, or performance advantage.

## Frozen execution provenance

- HGFX: `hgfx==1.0.0`, source identity `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- pyhgf: `pyhgf==0.3.2`, source identity `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.
- Python `3.12.14`; NumPy `2.3.3`; JAX/JAXLIB `0.6.2`.
- Ubuntu 24.04 CPU; `JAX_ENABLE_X64=1`; `JAX_PLATFORMS=cpu`; float64.
- Scientific workflow: `P2A.10 Frozen Common-Scope Execution`.
- Workflow run: `35268575414`; job: `105361841212`.
- Scientific workflow head: `af9000f59ecb156a92cae6fcd063b8b8b9730dd1`.
- Artifact: `10517407320`.
- Artifact archive SHA-256: `ca449164064a2f345f73ee08098fe1c6e5aa8f4b7d45166723ed850f177d5e53`.
- Raw artifact file SHA-256: `5bf1fc203da4a6692193dc2e5bd6a0c31d51444dec93e021d3d836585f4cc0b2`.
- Comparison artifact file SHA-256: `6928e459419da76d0df5ae822f808bdd8a04cec68b8fe340aff6b91d6012bf14`.
- Resolved-environment (`pip freeze`) SHA-256: `ea927b9e643095d51f060026a0e2cc144afa8a99bd0e415028ef2bb1f9cb130e`.
- Embedded canonical raw-result SHA-256: `202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b`.

The artifact was independently downloaded after the scientific run. The embedded canonical raw-result hash was recomputed before the comparison artifact was interpreted and matched exactly. A separate evidence-ingest workflow then downloaded the same immutable artifact, verified the archive/file hashes and embedded raw hash, and committed byte-for-byte copies to `paper/reproducibility/`.

## Prospective tolerance policy

The following tolerances were committed before the first numerical result was inspected:

- trajectory and per-trial quantities: `atol=1e-10`, `rtol=1e-8`;
- participant-response total NLL: `atol=1e-7`, `rtol=1e-8`;
- observed binary input: exact identity.

No tolerance, input, response, model parameter, inverse temperature, dtype, guard, package version, or compared-field list was changed after the result.

## Executed comparison

| Frozen quantity | Classification | Maximum absolute error | Maximum relative error |
|---|---|---:|---:|
| first-level predicted probability | `PASS_FOR_EXECUTED_QUANTITY` | `1.1102230246251565e-16` | `4.398297788315473e-16` |
| level-2 posterior mean | `PASS_FOR_EXECUTED_QUANTITY` | `4.440892098500626e-16` | `6.10894723045687e-15` |
| level-2 predicted mean | `PASS_FOR_EXECUTED_QUANTITY` | `4.440892098500626e-16` | `6.10894723045687e-15` |
| level-2 posterior precision | `PASS_FOR_EXECUTED_QUANTITY` | `6.661338147750939e-16` | `4.616876670111438e-16` |
| level-2 predicted precision | `PASS_FOR_EXECUTED_QUANTITY` | `6.661338147750939e-16` | `5.504358933166012e-16` |
| level-3 posterior mean | `PASS_FOR_EXECUTED_QUANTITY` | `1.1102230246251565e-16` | `1.1425234718806022e-16` |
| level-3 predicted mean | `PASS_FOR_EXECUTED_QUANTITY` | `1.1102230246251565e-16` | `1.1425234718806022e-16` |
| level-3 posterior precision | `PASS_FOR_EXECUTED_QUANTITY` | `1.5543122344752192e-15` | `9.227265334738466e-16` |
| level-3 predicted precision | `PASS_FOR_EXECUTED_QUANTITY` | `1.5543122344752192e-15` | `9.265792883082711e-16` |
| derived first-level prediction error | `PASS_FOR_EXECUTED_QUANTITY` | `1.1102230246251565e-16` | `3.909751290281609e-16` |
| derived first-level input surprise | `PASS_FOR_EXECUTED_QUANTITY` | `4.440892098500626e-16` | `6.647587541504817e-16` |
| participant-response NLL per trial | `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` | finite-overlap max `0.378164539754998` | finite-overlap max `1.0` |
| participant-response NLL total | `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` | n/a | n/a |

Observed-input integrity was `PASS_EXACT`.

## Boundary diagnostics

Neither implementation produced an exact `0` or `1` first-level predicted probability in the perceptual trajectory. The predicted-probability ranges were:

- HGFX: `0.23085027433109492` to `0.8212887461337505`;
- pyhgf: `0.23085027433109498` to `0.8212887461337505`.

Maximum finite posterior precisions also agreed at binary64 scale:

- level 2: `4.499256576603398` for both implementations;
- level 3: HGFX `1.9852960592560553`, pyhgf `1.985296059256055`.

The response surface behaved differently at the numerical probability boundary. With the prospectively frozen inverse temperature `ze=48`, the explicit power-ratio softmax construction on the pyhgf side rounded the derived response probability to an exact boundary on 13 trials. The unclipped binary-surprise evaluation therefore returned `+Inf` on coordinates:

```text
48, 50, 54, 62, 64, 104, 107, 109, 116, 119, 120, 122, 123
```

HGFX's `unitsq_sgm` log-domain formulation remained finite on those trials; its total response NLL was `1808.855415351429`, while the pyhgf-derived total was `+Inf` under the frozen construction.

Crucially, P2A.9 had already frozen the rule that a derived surprise/response-NLL boundary nonfinite is classified as `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`. We therefore do **not** change clipping, inverse temperature, formula, dtype, or tolerance after seeing this result, and we do not relabel it as a direct implementation PASS or FAIL.

## Interpretation

For this exact common-scope three-level binary HGF, the mapped perceptual/inference trajectory surface agrees to approximately binary64 rounding scale and comfortably satisfies the prospectively frozen tolerances. This supports a narrow common-scope numerical-equivalence statement for the 11 executed perceptual/trajectory quantities.

The participant-response NLL comparison does not support a direct equality claim under the frozen protocol because the two retained numerical constructions differ at the extreme response-probability boundary. The appropriate result is `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`, as specified before execution.

This result does not establish that HGFX is generally more accurate, faster, or better than pyhgf. pyhgf and HGFX retain different design centers and broader non-overlapping capabilities documented in `PYHGF_FEATURE_DESIGN_MATRIX.md`.

## Preserved machine-readable evidence

- `paper/reproducibility/p2a10_raw_numeric_result_35268575414.json` — byte-for-byte raw artifact, still marked `RAW_UNINTERPRETED` with `comparison=null`.
- `paper/reproducibility/p2a10_comparison_35268575414.json` — post-hash comparison/classification artifact.
- `paper/reproducibility/p2a10_pip_freeze_35268575414.txt` — exact resolved package environment.
- `paper/reproducibility/p2a10_workflow_provenance_35268575414.json` — workflow/artifact/hash provenance.
- `paper/reproducibility/pyhgf_common_scope_case.json` — immutable prospectively frozen case.
- `paper/reproducibility/pyhgf_final_semantic_gate.json` — pre-execution authorization record.

## P2A status consequence

The empirical common-scope requirement of issue #33 is now satisfied for the semantically authorized case. The remaining P2A closeout work is documentary: synchronize the manuscript, evidence map and execution plan with this observed scoped result and complete the claim audit. No post-result scientific retuning is required or permitted.
