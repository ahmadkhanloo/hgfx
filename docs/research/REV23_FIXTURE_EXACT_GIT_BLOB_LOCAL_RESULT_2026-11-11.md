# REV-2.3 — exact Git-blob local fixture-test verification (2026-11-11)

**Outcome: 17/17 PASS in local source-only regression. GitHub Actions CI remains UNVERIFIED. No scientific/benchmark runs.**

## Why this supersedes only the local-source uncertainty

Earlier [synthetic local report](REV23_FIXTURE_INTEGRITY_SYNTHETIC_TEST_RESULT_2026-11-11.md) explicitly noted that local tests came from a reconstructed, not Git-blob-verified source. This follow-up **does not overwrite or erase that historical report**. In this test, the exact UTF-8 source contents were retrieved from the GitHub connector at PR #107 head `af9ebb305dd2efb35abae8bc5491011991561cfc`, reconstructed in the local container, and independently compared to the **repository-reported Git blob object IDs** with `git hash-object` before execution.

| Input file | GitHub returned Git blob SHA | Local `git hash-object` | Local SHA-256 of file bytes |
| --- | --- | --- | --- |
| `tools/rev23_fixture_integrity.py` | `09491b28b5c70fa887f7c6946b711849dccdfcf4` | `09491b28b5c70fa887f7c6946b711849dccdfcf4` | `9293d28b5be24575ad45870ffe09ab29e694c7ccc26c99e78dcbedcdfcd7b34e` |
| `tests/test_rev23_fixture_integrity.py` | `e21fc36351c9f4f8c76c7cf889865c72d3956cae` | `e21fc36351c9f4f8c76c7cf889865c72d3956cae` | `96a7ea61bb4e0bd69bf7eed66156c4689ec0a4ca3c8f1b07aa8ca16b1806114f` |

This is strong exact-file content evidence, **not** proof of a complete Git repository checkout, or an authoritative GitHub-hosted CI run.

## Actual local command, versions, output

```text
python --version
Python 3.13.5

python -m pytest --version
pytest 9.0.2

numpy 2.3.5

cd /mnt/data/rev23_exact
python -m pytest -q tests/test_rev23_fixture_integrity.py
.................                                                        [100%]
17 passed in 0.47s
```

Test inputs are **synthetic, test-only** arrays in temporary directories. They are not scientific trial data, model fits, MATLAB output or canonical frozen benchmark fixtures. The command did not import HGFX, MATLAB or a GPU backend. No timing measurement (other than pytest's own wall-clock duration) or performance ratio was taken.

## GitHub CI verification limitation

- Connector `fetch_commit_workflow_runs` applied to original PR head `af9ebb305dd2efb35abae8bc5491011991561cfc` returned an empty `workflow_runs` list; **the connector filters to PR-triggered Actions runs**, and thus cannot establish whether the branch's push-triggered `.github/workflows/rev23-fixture-integrity.yml` ran.
- External GitHub access from this environment failed (network DNS resolution), so neither the push-run ID nor its console log was independently obtained.
- The workflow's configured Python is 3.11, while this locally observed PASS used Python 3.13.5. **Python-3.11 CI PASS must not be inferred from this local result.**

## Remaining integrity work

1. Verify actual GitHub Actions workflow run and SHA (or independently execute the exact Git-blob source under Python 3.11); record run URL and terminal job outcome before official CI PASS.
2. Independently review scientific model/observation selection and immutable source arrays for all F/B rows; materialize real canonical fixture bytes and calculate actual SHA256, rather than mistaking synthetic test bytes for paper data.
3. Freeze validated data/starts/configs, complete MATLAB/Python timing boundaries, host/thread/device environment and reviewer approval **before** any timed paper science.

**Gate ledger:** `REV23_FIXTURE_TOOL_LOCAL_EXACT_SOURCE_TEST=PASS_17_OF_17`; `REV23_FIXTURE_TOOL_GITHUB_CI=UNVERIFIED`; `REV-2.3=DRAFT_NOT_FROZEN / BENCHMARK_NOT_RUN`; all 44 candidate cells `PENDING_INDEPENDENT_REVIEW`; `PERF-01C=BLOCK_FREEZE`; D2/D3 `BLOCKED`. No earlier scientific failures/tolerances/seeds were changed.
