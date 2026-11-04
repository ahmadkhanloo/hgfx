# Prospective FULL-SOURCE cohort extension — published-input fixed-vector parity

**Recorded 2026-11-04 after successful first-case pilot and BEFORE running full cohort.**
This extension does not change any of the first-case protocol's native parameters, input coding, numerical thresholds, reference software or failure handling. It changes only the *predeclared population coverage* from one first-case pilot per published source to **every available person × study block in the two already pinned files**, not a selection of high-agreement cases. No outcomes from other cases have been inspected.

## Immutable inputs and models

Read [pilot protocol](PUBLISHED_REALDATA_PAIR_PROTOCOL_2026-11-04.md) for exact SHA256, MATLAB8.2 SHA, HGFX1.0 wheel, model `hgf_ar1_binary_mab`, the unchanged 17-element `p_hgf` vector and existing criteria `rtol=2e-9, atol=2e-11`.

Enumerate **without checking output quality**:
- Suthaharan 2021: every matched `TP<id>_V3_outcomes_1/2` + `TP<id>_V3_choices_1/2`; expect exactly 130 source person prefixes × 2 blocks = **260 80-trial cases**, according to previously obtained structural inventory.
- Reed 2020: every matched `P<id>_outcomes_804020/905010` + `P<id>_choices_804020/905010`; expect exactly 33 person prefixes × 2 conditions = **66 80-trial cases**, based on earlier structural inventory.
- Total planned **326 cases (26,080 trials)**. If the expected raw schema does not have exactly those cases, block before the fit and report the actual inventory; do not silently reduce any denominator. Ignored/missing trials stay present, with the same masks in MATLAB and HGFX.

Data remains original, no categorization changes. As in pilot, model family is 8.2.0 common-scope fixed-vector perception, not a faithful fit of the older paper's model-response or published inference.

## All-case execution and acceptance

- Freeze source manifest with hash of original MAT bytes, sorted pair identity and valid data coding. Input files and raw trajectories remain ephemeral and are NEVER uploaded.
- MATLAB R2025b with pinned 8.2.0 HGF submodule and HGFX 1.0.0 CPU x64 evaluate *each* case with exactly `p_hgf` used in pilot. No fitting or optimizer, no priors tweaked and no subject selection by observed numeric agreement.
- Preserve all case failures, invalid codings, warnings and incomplete pairings. For every succeeded case, compare all 12 fields including `infStates`. Report case denominator, number PASS/FAIL, total matching/compared elements, worst maximum absolute/relative difference, failed field names and first divergence trial/level. No post-hoc tolerance change or omit-missing.
- A full-source **PASS_FIXED_VECTOR_PARITY_ALL_CASES** requires all 326 expected source cases to have valid input coding, a real MATLAB output, a real HGFX output, the same finite/nonfinite masks and all fields within the inherited gate. Otherwise report **FAIL/INCONCLUSIVE** with all failures, not a success ratio stripped of failures.
- This still must not be termed “we reproduced both published papers” or “better than MATLAB”: no published response model, fit, trial exclusions of original study, Bayes model comparison or group-level scientific result has been replicated. A full original-paper replication would require separate reviewed study-specific semantic and optimization protocol(s) and original reference versions.

No historical HGFX paper results, source code, software package, or frozen validation evidence may be changed by this extension.
