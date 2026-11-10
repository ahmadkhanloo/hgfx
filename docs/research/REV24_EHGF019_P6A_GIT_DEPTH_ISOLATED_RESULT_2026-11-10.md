# REV-2.4 — isolated P6A historical Git-depth diagnosis (2026-11-10)

**Final outcome: `ISOLATED_P6A_HISTORY_TEST=PASS` on BOTH Ubuntu 24.04 and Windows; original complete CPU suite `NOT_PASS`; corrected development `1.1.0b1` `IMPLEMENTED_BUT_NOT_FULL_CI_OR_SCIENTIFICALLY_VALIDATED`; REV-2.4 original scientific `NOT_GLOBAL_PASS`; D2/D3 BLOCKED.**

## Purpose / execution authority

This check is **not** another full-suite retry and is **not** an HGFX/MATLAB science run. It isolates exactly one previously failing frozen P6A test, unchanged, to establish whether shallow Git history was the CI failure mechanism.

- Original full-suite runs: [42800906817](https://github.com/ahmadkhanloo/hgfx/actions/runs/42800906817) (Linux and Windows FAILED before collection, missing `tools` module) and sole infrastructure retry [42801485168](https://github.com/ahmadkhanloo/hgfx/actions/runs/42801485168) (**302 PASS / 1 FAIL / 5 SKIPPED per OS**). The sole failing test on both platforms: `tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator`, attempted historical `git cat-file -e 897aed804901f9f49ad1d73ecfab6fa714d50098^{commit}` on a shallow checkout.
- **Precommitted distinct read-only diagnostic protocol:** [`REV-2.4_P6A_FULL_HISTORY_ISOLATED_DIAGNOSTIC_2026-11-10.md`](../../evidence/revision/protocols/REV-2.4_P6A_FULL_HISTORY_ISOLATED_DIAGNOSTIC_2026-11-10.md) commit `4ee11604e564e0b2d4a140ca9c75e0af9e5cc731`.
- Source-only workflow [`.github/workflows/compstat-rev24-p6a-history-isolated.yml`](../../.github/workflows/compstat-rev24-p6a-history-isolated.yml), preregistered before the kickoff; one explicit kickoff `983a1bf5a2975f50174d6f54ffd108332c829139` triggered [Actions run **42815782002**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42815782002). Trigger retired immediately after launch at commit `ce97931f32df78e912e88bb5e1928b941f964100`. No retries.

## Real results

| Platform | Git history gate | Frozen original MATLAB-source identity | The single unchanged P6A test | Workflow |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 | `SHALLOW=false`, `git cat-file` and `merge-base --is-ancestor` PASS | `Reference freeze verification: PASS` | **1 passed in 0.61s** | **success** |
| Windows latest | `SHALLOW=false`, `git cat-file` and `merge-base --is-ancestor` PASS | `Reference freeze verification: PASS` | **1 passed in 3.07s** | **success** |

The historical candidate `897aed804901f9f49ad1d73ecfab6fa714d50098` was confirmed as an actual ancestor in the full checkout on **both** systems. The exact original failing test ran with `python -m pytest -q tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator`; no testing code, source manifest, data, sample selection, thresholds, or frozen P8/P6A criteria were edited. Same development package install `python -m pip install -e '.[dev]'`, Python 3.11, `fetch-depth:0`, recursive frozen HGF submodule verification.

## Interpretation and independent reproducibility

The evidence **supports an environment/Git-checkout failure classification** for the single historical P6A manifest test. It is consistent with the two earlier full-suite failures being infrastructure, not a new numerical regression. The existing canonical regression workflow already has the necessary `fetch-depth:0` and `python -m pytest` corrections.

**DO NOT** label full CPU regression PASS: the only full Linux/Windows matrix results on this maintenance phase remain 302 PASS / 1 FAIL / 5 SKIPPED; this isolated 1/1 result is **not** the other 302 tests. The original complete-suite attempt and retry cap remains consumed and historical red results preserved. A new full CI run would require separate explicit authorization or standard event-driven PR CI and must report its own SHA/result. No physical GPU evidence or paired MATLAB/HGFX scientific revalidation of development fix was produced.

**Remaining gates:** independent human/domain-expert attribution of the eHGF-019 `np.maximum` vs MATLAB `max` causal hypothesis; prospective corrected maintenance 1.1.0b1 scientific validation under a newly documented protocol; availability and independent review of Panel E raw sources; missing original D02 HGFX full endpoint; eHGF/uHGF predeclared family objective gates; historical subject-7/63-of-64/M18/P3/PERF-01C NONPASS. Original HGFX v1.0.0 paired Panel G/E results and all old failures are unchanged; **REV-2.4 global science remains `NOT_GLOBAL_PASS` and D2/D3 BLOCKED**.
