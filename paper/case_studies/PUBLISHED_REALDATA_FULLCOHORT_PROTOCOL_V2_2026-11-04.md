# Source-inventory correction to full-cohort protocol — v2, 2026-11-04

**Prospective scientific change recorded before the full-grid MATLAB/HGFX evaluation.**

## Prior protocol and failed pre-execution gate, preserved

The original [full-cohort protocol](PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_2026-11-04.md) conjectured 130 Suthaharan participants and 33 Reed participants, two task blocks per person, hence 326 cases (26,080 trials). [Actual GitHub source gate run 41809479255](https://github.com/ahmadkhanloo/hgfx/actions/runs/41809479255) stopped **before installing/running MATLAB**, reporting exactly 130 Suthaharan persons/260 blocks, but only 32 Reed persons/64 blocks. It has status **BLOCKED_UNEXPECTED_SOURCE_COHORT_SIZE**, **not PASS**, and must remain cited.

A deeper read of source `IRL_Data.mat` variable headers, obtained in independently successful [structure audit 41808176346](https://github.com/ahmadkhanloo/hgfx/actions/runs/41808176346), revealed 197 top-level variables; only 32 distinct `P[0-9]+_` participant prefixes, 64 named choice half-blocks. The misleading 33rd name was a generic MATLAB workspace variable **`ans`**, not a participant. There is no basis to fabricate two missing participant blocks. This discrepancy is source-schema accounting, established **without inspecting any new full-cohort model results**.

## Amended source-defined full population (v2)

- Suthaharan: all existing 130 published person prefixes × both original 80-trial blocks = 260 cases.
- Reed: all existing 32 published person prefixes × both original 80-trial condition halves = 64 cases.
- **324 cases, 25,920 original trials, no exclusion or subsampling.** One missing observation in the original first Reed pilot was masked and preserved; all missing trials must remain and be treated identically.
- Both originally published inputs and their SHA256 digests, native coding, HGFX1.0 version, frozen MATLAB8.2 oracle, model family, pre-selected M12B 17-parameter native vector and tolerances are unchanged.
- This is a transparent **new v2 denominator**, not a claim that the original v1 326-case planning gate passed. Link to the failed v1 run in all final reports.
- All original per-source subject pair names must be enumerated by source structure and kept regardless of numerical result. Any additional unexpected schema differences or invalid response coding must be counted as failures and reported.

**Acceptance criterion v2:** parity PASS only when all **324** original-source blocks complete the complete 12-field numerical comparison within **rtol=2e-9, atol=2e-11**, including missingness and nonfinite masks, on real MATLAB8.2 and released HGFX1.0. Otherwise FAIL/INCONCLUSIVE, with all failures retained.

As in original protocol, this is still only a *published-data perceptual-forward compatibility validation*, not a reproduction of published participant-level parameter estimates, response likelihoods, statistical associations or the manuscripts' conclusions. Original old HGF versions A remain not reproduced.

Status at creation: **NO full-cohort scientific model run performed yet.** Original source gate failure archived; v2 authorized for physical comparison.
