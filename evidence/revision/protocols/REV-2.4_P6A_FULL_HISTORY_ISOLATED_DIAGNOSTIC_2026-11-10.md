# REV-2.4 maintenance — isolated historical P6A Git-depth proof (2026-11-10)

**Category:** READ-ONLY / SOURCE & CI INFRASTRUCTURE DIAGNOSTIC, **NOT** scientific validation, not an extra execution of the exhausted original full CPU suite. This distinct check evaluates only the one historically failed **P6A manifest test**, not the whole suite.

## Preexisting immutable record

- Original maintenance full Linux+Windows [run 42800906817](https://github.com/ahmadkhanloo/hgfx/actions/runs/42800906817) failed test collection (`ModuleNotFoundError: tools`) from `pytest` entrypoint.
- Single infrastructure retry [run 42801485168](https://github.com/ahmadkhanloo/hgfx/actions/runs/42801485168) used `python -m pytest` and completed **302 passed / 1 failed / 5 skipped per OS**. The only failure on both OSes was `tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator`, because a Git `cat-file` lookup for historical candidate commit `897aed804901f9f49ad1d73ecfab6fa714d50098` failed on the shallow checkout.
- GitHub Compare confirms that original candidate is a real ancestor of the executed retry source `ba442bbb05698d3d8d5ae7f52443a998ebc5aa01`, 192 commits ahead and zero behind. The **existing canonical** `.github/workflows/regression.yml` uses `fetch-depth: 0`. The historical two-run full suite remains **NOT PASS**; its cap remains consumed. [Original full regression report](../../../docs/research/REV24_EHGF019_FULL_REGRESSION_RESULT_2026-11-10.md).

## Exact limited hypothesis and test (frozen before run)

**Hypothesis:** running just the unchanged P6A test with **real full Git history** instead of a shallow checkout resolves the missing-object collection/manifest failure on both Ubuntu and Windows.

- Execute a **single workflow invocation**, matrix Ubuntu24.04 + Windows-latest, checkout `fetch-depth: 0`, original nested HGF submodule initialized, Python3.11, editable development `.[dev]` dependencies, **unchanged exact historical test** with `python -m pytest -q tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator`.
- Before the test, require `git cat-file -e 897aed804901f9f49ad1d73ecfab6fa714d50098^{commit}` and `git merge-base --is-ancestor <candidate> HEAD`. Print exact run head SHA, expected candidate and complete remote-tracking HEAD. No repository test, source code, data, threshold, protocol or historical artifact is modified.
- This is **NOT a full 303-test suite rerun**, a replacement for red JUnit, a new MATLAB/HGFX run, GPU verification, reference scientific parity or human approval.
- **One initial isolated check only.** A new failure is recorded as such; no repeat-until-green. Retire the one-shot trigger as soon as launch is confirmed.
- Potential output: `P6A_ANCHOR_WITH_FULL_HISTORY=PASS` (read-only historical source gate only), or `FAIL` (investigate separately). Even if PASS, **full CPU suite remains NOT PASS on archived attempts**, original release 1.0.0 Panel G/E scientific `NOT_GLOBAL_PASS`, eHGF 019 original failure retained, corrected development 1.1.0b1 **not scientifically validated**, D2/D3 BLOCKED. The canonical PR CI can later perform normal full regression under its own event permissions; no new full run is authorized by this document.

## Reporting

Document exact original run, original one retry, isolated case proof run ID/commit, both OS status/logs, unchanged historical candidate SHA, and any remaining CI/human/scientific blockers in a dated, append-only report and revision ledger. Do not downgrade or rewrite historical failures.
