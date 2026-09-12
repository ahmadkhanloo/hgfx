# M18B repair plan

Scope: repair validation integrity before making further scientific recovery claims and align M18 with the product-level MATLAB-equivalence policy.
Matrix IDs: C01/C04 (fitting evidence), P02/P03/P04 (binary model recovery), O17.
The model equations, priors, optimizer and frozen historical M18 thresholds are unchanged.

Authoritative product rule: `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.

## Small steps and acceptance criteria

1. **Done — establish current baseline.** Read branch `db4662d`; download CI
   result `34411993098`. Runner and workflow already exist. Reproduce empty raw
   records plus plausible summary returning PASS in the old gate.
2. **Done — validate evidence.** Compute decisions from raw records; require
   exact model/parameter/trials/replicate coverage, valid per-record metrics,
   consistent unique seeds, and agreement with any supplied summary. Adversarial
   tests cover empty, duplicate, substituted, nonfinite and negative records.
3. **Done — freeze historical evidence.** Archive original M18 artifact
   `10111094151` from run `34362839798` byte-for-byte. Verify its SHA-256 and
   unchanged runner/recovery source hashes. Missing or altered evidence fails.
4. **Done — remove unsupported identification claim.** Replace
   `identifiable_recovery` with `low_error_recovery`. Conditional likelihood
   slices and small errors do not establish joint identifiability. No numerical
   acceptance threshold is relaxed.
5. **Done — make runs auditable.** Store inputs, diagnoses including profile
   arrays, source hashes, environment, seed and failures. Checkpoint atomically
   after each cell. An interrupted or smoke run cannot claim final PASS.
6. **In progress — rerun corrected validation.** Require targeted tests,
   reference-freeze guard, full regression, and the unchanged gate grid (27
   datasets / 81 parameter records). Publish corrected code and CI artifact.
7. **Active scientific follow-up — establish MATLAB reference limits before fixing HGFX.**
   Reproduce the 512-trial failure at its recorded seed/configuration and run the
   identical case against frozen MATLAB HGF Toolbox 8.2.0. If MATLAB is stable,
   locate the first HGFX-vs-MATLAB divergent trial/state and classify the case as
   `IMPLEMENTATION_MISMATCH`. If MATLAB fails comparably in the same regime, record
   `REFERENCE_LIMITATION_MATCH`; this is acceptable for MATLAB-equivalence v1.0 but
   is not a scientific PASS claim. If the evidence is ambiguous, retain
   `INSUFFICIENT_REFERENCE_EVIDENCE`. Do not select seeds, shrink the grid, change
   model family, or relax thresholds after observing results.
8. **Open — reference-aware model-family validation.** For each scientific case,
   establish which MATLAB model family/workflow is the valid reference. Base HGF
   is not required to solve cases where the MATLAB toolbox itself uses eHGF, uHGF,
   or a specialized perceptual/observation family. Compare HGFX against the same
   reference workflow and flag any required model-family divergence as
   `MODEL_SELECTION_MISMATCH`.
9. **Open — demo/workflow closure for v1.0.** Build Python equivalents of the
   required MATLAB demo workflows and include them in the v1 release gate. Demo
   parity must exercise model selection/configuration, fitting, trajectories,
   simulation and plotting/output semantics where present in the MATLAB reference.

## What completion means

Steps 1–6 close the evidence-integrity repair, not the whole HGFX scientific
validation program. Steps 7–9 close the product-level MATLAB-equivalence gaps.

M18 must not be converted from FAIL to PASS by weakening historical thresholds.
Instead, the final v1 decision is reference-aware:

- unresolved `IMPLEMENTATION_MISMATCH` or `MODEL_SELECTION_MISMATCH` in a required
  MATLAB workflow blocks v1.0;
- demonstrated `REFERENCE_LIMITATION_MATCH` is acceptable for v1.0 and must be
  documented explicitly;
- `INSUFFICIENT_REFERENCE_EVIDENCE` remains open and cannot be treated as PASS.

The 512-trial limitation therefore remains unresolved until frozen MATLAB evidence
classifies it. Joint recovery and model discrimination need their own acceptance
evidence and are not closed by a protocol-integrity PASS.
