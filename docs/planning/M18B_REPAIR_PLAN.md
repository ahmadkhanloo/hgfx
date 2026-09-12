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
6. **Done — rerun corrected validation.** Corrected evidence-integrity gate ran
   successfully on PR #20 merge validation, run `34497399365`, job
   `102939240184`. Frozen reference guard passed at HGF 8.2.0 commit
   `2437f4dc241541072722a2695ddeca7b44d83dd3` with 334 MATLAB files. M18B unit
   tests: 39 passed. Full regression: 136 passed, 4 physical-GPU-only skips.
   Final 27-dataset gate completed with `gate_pass=true` and zero failures.
   Artifact `m18b-identifiability-validation`, ID `10160948325`, SHA-256
   `5a997b3be06f12420a52086f42656ecd14ff132892d42bb69c20419de234f182`.
7. **Done — classify the historical 512-trial horizon against MATLAB.** The exact
   `hgf_binary` case was frozen at 512 trials, truth scale 0.35, replicate 0,
   cell seed `233100` (response seed `233101`) and run against frozen MATLAB HGF
   8.2.0 on the identical input/response/configuration. Workflow run
   `34683977567` completed successfully. Truth-parameter forward execution succeeds
   in both implementations; default-parameter forward execution fails in both with
   the same variational-approximation-invalid condition; both initial objectives
   return the realmax failure sentinel / `rval=-1`, so fitting is not entered in
   either implementation. Classification: `REFERENCE_LIMITATION_MATCH`; no
   MATLAB-vs-HGFX mismatch was observed. Artifact
   `m18-512-matlab-reference-evidence`, ID `10295261423`, SHA-256
   `8a538a1bc8cae206e1014b72a4de8495d9951ad2934845db1704d83ee743092c`.
   This closes the HGFX-defect question for this frozen case but is not a scientific
   PASS claim and does not imply arbitrary 512-trial designs are supported.
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

Steps 1–7 are complete. The evidence-integrity repair is closed and the historical
512-trial case is now classified against the frozen reference. Steps 8–9 remain the
product-level MATLAB-equivalence work required before v1.0 release.

M18 must not be converted from FAIL to PASS by weakening historical thresholds.
Instead, the final v1 decision is reference-aware:

- unresolved `IMPLEMENTATION_MISMATCH` or `MODEL_SELECTION_MISMATCH` in a required
  MATLAB workflow blocks v1.0;
- demonstrated `REFERENCE_LIMITATION_MATCH` is acceptable for v1.0 and must be
  documented explicitly;
- `INSUFFICIENT_REFERENCE_EVIDENCE` remains open and cannot be treated as PASS.

The corrected M18B protocol gate is PASS, but M18B PASS does not imply historical
M18 PASS. Joint recovery/model discrimination claims and complete MATLAB workflow/demo
parity remain separate acceptance questions.
