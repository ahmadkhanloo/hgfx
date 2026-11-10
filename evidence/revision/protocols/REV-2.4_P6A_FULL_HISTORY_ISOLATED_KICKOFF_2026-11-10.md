# REV-2.4 P6A history-only proof — one CI kickoff (2026-11-10)

Launch **only** the precommitted isolated history proof under [REV-2.4_P6A_FULL_HISTORY_ISOLATED_DIAGNOSTIC_2026-11-10.md](REV-2.4_P6A_FULL_HISTORY_ISOLATED_DIAGNOSTIC_2026-11-10.md), protocol commit `4ee11604e564e0b2d4a140ca9c75e0af9e5cc731`. This is distinct from and **not an additional attempt of** the original full CPU regression; those original failure records `42800906817`, `42801485168` remain intact.

Validate `git cat-file` and `git merge-base` of original P6A candidate `897aed804901f9f49ad1d73ecfab6fa714d50098` with `fetch-depth: 0`, run exactly one existing `test_committed_p6a_manifest_matches_generator` with unchanged source on Ubuntu and Windows. No full-suite, no MATLAB numerical science, no frozen threshold changes. One invocation and no automatic retries.

Even if isolated historical test PASS, full regression and original HGFX science remain **NOT PASS**, D2/D3 **BLOCKED**.
