# REV-2.3 — PR-triggered synthetic CI visibility repair (2026-11-12)

**Scope:** source-only infrastructure. **No reported workflow PASS**, no model, simulator, MATLAB or runtime benchmark executed here.

## Why the change was needed

The established `.github/workflows/rev23-fixture-integrity.yml` workflow ran on `push`/manual dispatch only. The available GitHub connector's `fetch_commit_workflow_runs` explicitly enumerates only **pull_request-triggered** workflow runs. The empty connector results on recent push commits therefore had no power to establish success/failure, and the scientific team could not authoritatively cite a workflow run from this environment.

## Change

Commit [`26ba37971488c1504e45c090cc05a49cf9b740a5`](https://github.com/ahmadkhanloo/hgfx/commit/26ba37971488c1504e45c090cc05a49cf9b740a5) adds a `pull_request` event with the same five exact path filters as the existing `push` event, retaining the already established Python 3.11, Ubuntu, read-only token permissions and the exact two test modules. PR #107 is open and draft, targeting `main` from `compstat-revision`.

**No acceptance criterion, model parameter, trial count, seed, baseline or science workflow was changed.**

## Verification actually performed

GitHub connector reread PR #107 immediately after the commit and showed head SHA **`26ba37971488c1504e45c090cc05a49cf9b740a5`**, base `main`, head branch `compstat-revision`, state `open`. The connector's run lookup for that SHA returned **`workflow_runs: []`**, including a subsequent check. This is **not** a workflow run or a PASS; possible pending/disabled workflow state or permissions have not been independently diagnosed. There is no verified job ID, run URL, Python 3.11 log or terminal conclusion. Treat CI as **`UNVERIFIED`**.

Prior source-only *fixture integrity* tool 17/17 exact-blob local PASS is not a result for the *new* draft-ledger test module. The two modules currently define 17 + 19 = **36 test functions**, subject to actual pytest discovery.

## Next verified work required

Fetch the current run for PR #107 (from the Actions UI or a GitHub API capability that can enumerate `push` and `pull_request` runs). For an actual run, archive URL, run ID, runner OS, Python version, exact commit SHA, collected tests, terminal test results and first failing test if any. If no run appears, investigate repository Actions permissions and workflow file availability rather than asserting PASS.

**Status ledger:** `REV23_SYNTHETIC_CI=UNVERIFIED`; `REV23_DRAFT_LEDGER_TESTS=IMPLEMENTED_NOT_VALIDATED`; `REV-2.3=DRAFT_NOT_FROZEN`; 44/44 performance cells pending; `PERF-01C=BLOCK_FREEZE`; D08 previous FAIL and REV-2.4 `NOT_GLOBAL_PASS` preserved, no timing or speed claim.
