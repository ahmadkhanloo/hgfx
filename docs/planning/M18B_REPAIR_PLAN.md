# M18B repair plan

Scope: repair validation integrity before making further scientific recovery claims.
Matrix IDs: C01/C04 (fitting evidence), P02/P03/P04 (binary model recovery), O17.
The model equations, priors, optimizer and frozen M18 thresholds are unchanged.

## Active continuation

See [MATLAB parity recovery plan](MATLAB_PARITY_RECOVERY_PLAN.md). Steps 1–5 below remain implemented history; step 6 maps to R0; step 7 is expanded into R1–R5 with paired MATLAB evidence and explicit exit criteria. No new scientific PASS is established by this documentation update.

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
6. **Local PASS — corrected validation rerun.** Targeted tests (39), reference
   guard and baseline regression (136 passed / 4 GPU skips) passed. The unchanged
   gate completed with 27 datasets / 81 records / zero failures; a second raw-record
   evaluation passed. Complete local output is archived with source/hash provenance.
   Corrected CI artifact remains separately pending in run 34567774302.
7. **Open scientific follow-up — numerical horizon and experimental design.**
   Reproduce the 512-trial failure at its recorded seed, identify the first
   divergent trial/state against frozen MATLAB, and only then correct any
   demonstrated implementation mismatch. Compare bounded-run inputs with a
   preregistered stable/volatile design; do not select seeds or shrink the grid
   after observing results. Joint recovery and model discrimination need their
   own acceptance evidence. They are not closed by a protocol-integrity PASS.

## What completion means

Steps 1–6 close the evidence-integrity repair, not the whole HGFX scientific
validation program. M18 remains FAIL, M19/M20 remain open, and the 512-trial
limitation remains unresolved until reference evidence supports a correction.

## Execution update — 2026-09-11

See [first horizon diagnosis](M18_HORIZON_DIAGNOSIS.md): 39 corrected-gate tests and baseline regression pass. Corrected M18B local gate PASS: 27 datasets, 81 records, zero failures; complete raw output and hashes archived in reference/validation. Paired MATLAB workflow 34568178526 confirms 49 valid cases and the same 5 rejection boundaries. Rejected raw intermediates and R3 paired inference remain open. M18 historical FAIL is unchanged.
