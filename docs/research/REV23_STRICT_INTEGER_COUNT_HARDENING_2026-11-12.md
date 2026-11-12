# REV-2.3 strict numeric counts: static hardening record (2026-11-12)

**Disposition: SOURCE CHANGES COMMITTED / PYTEST AND GITHUB ACTIONS NOT VERIFIED.**

## Identified implementation bug

Before this change, the draft-only ledger checker compared JSON numeric values with Python equality: `True == 1`, `False == 0`, `128.0 == 128` and `5.0 == 5` could allow incorrectly typed trial counts, subject counts, warmup/repeat policy or purported recorded speedup counts to satisfy the nominal immutability checks. This is **a metadata integrity defect** found in source review; it is not evidence of a previously executed invalid paper experiment.

## Traceable changes

1. [`cf77c064c8d419051e02659d0a1533a4f7253bcc`](https://github.com/ahmadkhanloo/hgfx/commit/cf77c064c8d419051e02659d0a1533a4f7253bcc) makes the source-only draft checker require `type(...) is int` for the original trial/subject counts, one warmup and five timed repeats, and the zero recorded-speedup count. This supplements the previous fix of strict 44/0/44 denominator types.
2. [`356530cb4eee75efa12f4652c77f2642a47156f0`](https://github.com/ahmadkhanloo/hgfx/commit/356530cb4eee75efa12f4652c77f2642a47156f0) adds parametrized negative tests for malformed trial/subject counts (`true`, `128.0`), warmups/repeats (`true`, `5.0`) and speedup-count impostors (`false`, `0.0`). The existing tests and historical evidence are preserved.

## Evidence actually obtained

The GitHub source connector was used to reread latest branch files and Git object blob SHAs:
- `tools/rev23_draft_ledger_audit.py` Git blob: `f6cdc1ea8b161a07be3da118a14bd5de07f6de18`
- `tests/test_rev23_draft_ledger_audit.py` Git blob: `69047fb5f5b63104d33eb359a0a5aaf74b28ff6c`
- `tests/test_rev23_fixture_integrity.py` Git blob: `e21fc36351c9f4f8c76c7cf889865c72d3956cae`

Static counting found 17 unparametrized fixture tests, 22 draft-ledger test functions and three parametrization groups with case counts 3/2/2. Therefore pytest should **collect 43 cases** (`17 + 22 + (3-1) + (2-1) + (2-1) = 43`). This is **an expected collection count**, *not* an observed pytest collection or a PASS verdict.

The GitHub connector returned zero PR-triggered workflow run records for latest prior branch head `0fbdbb78aebb372a8b0a65e80602c72361a022ac`; public GitHub Actions HTML access and local GitHub DNS resolution were unavailable. No run URL, CI logs or terminal outcome was obtained. **The 43 updated cases were not executed from exact-file bytes in this step.** Local exact-blob 17-case source-only PASS from an earlier commit remains historically true but does not validate the new code.

## Unchanged project gate

No scientific arrays were selected, no benchmark started, no thresholds/seeds/fit results were modified. The authentic frozen MATLAB source 320-trial demo does not cover all REV-2.3 trial lengths without prospectively approved input policy. Forward/batch model/fixture selection remains `OPEN_AUTHOR_REVIEW`; 44/44 candidate performance cells remain `PENDING_INDEPENDENT_REVIEW`; `REV-2.3=DRAFT_NOT_FROZEN / NOT_RUN`, `PERF-01C=BLOCK_FREEZE`, and REV-2.4 `NOT_GLOBAL_PASS` remain unchanged.

**Next engineering task:** obtain an actual GitHub Actions run ID/log or run the two test modules from verified exact-source bytes and record Python/NumPy/pytest versions and the commit. If no Actions runs exist, diagnose workflow settings/permissions; do not infer a PASS from an empty run listing.
