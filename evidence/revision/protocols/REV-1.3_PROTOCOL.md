# REV-1.3 protocol — historical forward-warning cross-tab

**Frozen before executing REV-1.3 source-only extraction, 2026-11-09.**
Parent: `docs/planning/COMPSTAT_REVISION_PLAN.md` §REV-1.3.
This audit **does not** rerun an HGF filter, optimizer or scientific experiment.
It does not change the frozen 324-case parity result or any acceptance tolerance.

## Immutable sources / joins

1. GitHub Actions run `41809919116`, artifact ID `13311622738`,
   `two-published-study-fullcohort-aggregate-parity`. Pin ZIP
   SHA-256 `1adfd1cd69b6f7d7a89ba2c8b9d564e774fd8a8841fa7243d6972605bd9f7391`
   and embedded `fullcohort_summary.json` SHA-256
   `47432c35aa4914a652a8f1dc2aad81dc4d76fb5175dd0fc1fd47532b81756b70`.
   This historical record has 324 case statuses, warning counts and counts of
   ignored trials. It **does not** record warning messages, arm, exact ignored
   positions, or per-case trial data.
2. For missing positions/arm only, derive the mask and source arm from the
   original **public, pinned** Reed et al. (2020) MAT input:
   `ModelDBRepository/258631@39ccaca508b81ca610e7666a613e061c801faaf9/IRL_Data.mat`,
   SHA-256 `b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708`.
   Do not download or examine participant outcomes beyond NaN masks.
   Freeze the original `prepare_fullcohort_pair.py` ID convention from
   `paper/published-input-validation-20261108`: select
   `^(P\\d+)_choices_(804020|905010)$`, sort numerically by participant
   and then arm code; label rows `reed_2020_0001` … `reed_2020_0064`.
   Determine ignored trials with `isnan(outcomes)|isnan(choices)` on the
   80-trial arrays. Validate every derived ignored **count** against the
   corresponding archived status. Abort on unmatched IDs, missing variables,
   unexpected shapes/coding, duplicates or SHA mismatches.
3. Suthaharan's 260 archived rows all have zero ignored trials and zero
   warning events. Record their arm as `unavailable_in_archived_status`
   (the source participant-block label is deliberately **not** inferred
   from an unverified status ID), rather than reconstruct participant
   choices or silently invent an arm.

## Locked aggregation / no outcome-dependent selection

- Include exactly 260 Suthaharan and 64 Reed source-defined 80-trial
  blocks. Report total warning **events** (sum of per-case warning counts)
  separately from blocks with >=1 warning. Expected historical audit:
  48 warning blocks = 29 with one event + 19 with three, 86 total events.
  These are **checks of a claimed source fact**, not substituted data.
- Produce cross-tabs of all statuses and warning-positive rows by
  study, ignored-trial count, Reed arm code and first ignored-trial index
  (zero-based and one-based). Include a count for rows with no ignored
  trial; do not invent a first index for such rows.
  Output only aggregate counts and raw source provenance. Never commit or
  upload participant-level input vectors or case-level derived positions.
- Record whether every warning-positive row has at least one ignored trial
  and whether any warning-free row does. This is an **association**, not
  a causal or mechanistic classification.
- Warning message categories (invalid, divide, overflow or other) are
  **not recoverable from the archived per-case statuses**; explicitly
  label `warning_type_unavailable` and leave numerical/masking mechanism
  to prospectively precommitted REV-2.1.
- Preserve the original v1 source-inventory gate (326 expected)
  `41809479255` as a failed historical pre-execution check;
  v2 source-defined denominator remains 324. No truncation.

## Evidence and quality gates

- Script `tools/audit_compstat_warnings.py` must fail on tampered
  archived counts, duplicate/missing case IDs, source hash mismatch,
  or disagreement of case-level ignored counts between the original
  public Reed data and the immutable archived statuses.
- Output `evidence/revision/warning_crosstab.json`, with member and
  input SHA-256, methods, complete aggregate cross-tabs, and explicit
  limits. One targeted CI execution is sufficient. Do not assert
  `EXPLAINED` until its independent CI and provenance checks pass.
- Any unavailable source, discordant observation or failed hash is
  a **BLOCKER / DOCUMENTED_LIMITATION**. Do not alter, drop or impute
  original records to make the audit pass.
