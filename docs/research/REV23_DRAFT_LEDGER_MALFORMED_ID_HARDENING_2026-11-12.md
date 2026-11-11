# REV-2.3 — draft ledger guard: malformed JSON identity fail-closed (2026-11-12)

**Status: IMPLEMENTED BUT NOT VALIDATED IN GITHUB ACTIONS.** This is a small engineering hardening of the *draft-only* metadata validator, not scientific validation or a new benchmark protocol. It does not change `COMPSTAT_REVISION_PLAN.md`, any existing fit result, acceptance tolerance, trial/subject grid, dataset, seed, frozen evidence or gate.

## Issue found by direct source inspection

The initial `tools/rev23_draft_ledger_audit.py` performed `set(names)` / `set(ids)` before verifying each JSON ID was a string. A malformed candidate manifest can contain a list/dictionary as the workload/cell ID, causing unhandled Python `TypeError: unhashable type` rather than the stated fail-closed `BLOCKED_DRAFT_LEDGER` verdict. Also Python `False == 0`, so a boolean `eligible_cell_count=false` could pass the numeric denominator equality check.

This was an **implementation input-validation defect identified by static source inspection**. There is no claim of a prior CI failure or observed scientific mismatch.

## Corrective commits

- [`72913617a137833ca80df59af01b1a1d5d75b909`](https://github.com/ahmadkhanloo/hgfx/commit/72913617a137833ca80df59af01b1a1d5d75b909): require string IDs before set comparison, reject malformed workload objects, require actual Python integer types for the three 44/0/44 denominator fields, include `TypeError` in CLI fail-closed exception handling.
- [`efeb7f372121eeb790cb245348cc706a52ed4068`](https://github.com/ahmadkhanloo/hgfx/commit/efeb7f372121eeb790cb245348cc706a52ed4068): five extra tests for list-valued workload/cell IDs, malformed workload record, boolean denominator and incorrect MATLAB default family. The draft audit test suite now **contains 19 test functions**; do not infer any PASS from mere presence.

## Verification actually performed

- Read the current exact `compstat-revision` branch source and fetched the updated code/test Git blobs using GitHub API; audit tool Git blob `0904b8d4e60e9def2421b276cd0aa1e638cc2906`, test Git blob `f50f26a5a0780fba59471397738286a1701d0e21`, observed PR #107 head `efeb7f372121eeb790cb245348cc706a52ed4068`.
- Previous current draft ledger inspection showed 11 workloads, 44 unique cells, all 44 pending and 0 timed values. No manifest edit in this task; the source cannot silently turn cells eligible.
- GitHub connector `fetch_commit_workflow_runs` returned empty for this commit; this API filters to PR-triggered runs and does **not** prove ordinary `push` workflow has not run. Public web Actions page access was blocked. **No exact-file pytest result for this new 19-test suite and no Actions run ID/log were retrieved or executed in this task.** Correct status: code/tests `IMPLEMENTED_BUT_NOT_VALIDATED`, CI `UNVERIFIED`.
- Earlier 17/17 local exact-blob **fixture** tests remain separate historical evidence; they do not count as these new ledger audit tests.

## Next required gate and boundary

Reproduce from exact branch checkout with `python -m pytest -q tests/test_rev23_fixture_integrity.py tests/test_rev23_draft_ledger_audit.py`, independently record Python versions, Git commit, counts, and GitHub Actions log. A syntactic/draft-ledger PASS cannot authorize model timing.

The F/B model/fixture choice remains **OPEN_AUTHOR_REVIEW**, prior F/B 320-trial demo insufficient to derive entire prospective data grid without approval. `REV-2.3=DRAFT_NOT_FROZEN`, `PERF-01C=BLOCK_FREEZE`, 44/44 ineligible pending review, `REV-2.4=NOT_GLOBAL_PASS`, historical D08 direct FAIL and exhausted protocol unchanged; no published HGFX speed claim.
