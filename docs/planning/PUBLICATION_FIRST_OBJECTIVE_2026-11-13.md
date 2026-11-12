# HGFX publication-first objective and execution authority (2026-11-13)

## Decision and precedence

**Primary project objective:** obtain publication of a scientifically defensible HGFX software/statistical-computing paper. The current author-selected submission target is *Computational Statistics* (D1=A, 2026-11-10), unless the author later changes the journal. Publication is the outcome; package features, higher performance, additional benchmarks, and perfect numerical parity are **means only when necessary to support defensible submitted claims**.

This prospective publication-priority decision supplements `AGENTS.md`, `COMPSTAT_REVISION_PLAN.md`, `COMPSTAT_SUBMISSION_READINESS_2026-11-12.md`, and `COMPSTAT_REVISION_LEDGER.md`. The strict scientific and historical gate rules remain in force. If these documents describe different dated snapshots, use the newest verified evidence and explicit author decision; never rewrite past evidence or retroactively alter milestone meanings.

## Current status (evidence-bounded)

| Workstream | Classification | Publication implication |
| --- | --- | --- |
| HGFX v1.0.0 release and distribution | DONE / historical | The released wheel and immutable reference provide the paper's software baseline, not blanket scientific parity |
| D1 venue decision | DONE: A / *Computational Statistics* | Prepare a software/package article to journal requirements |
| REV-3 revised manuscript and ESM | IN PROGRESS / provisional | Current 237-word abstract, six numbered tables, six figures; no current real-article compilation certificate |
| Published-input 324-block forward comparison | DONE, bounded one-vector scope | 260 Suthaharan + 64 Reed blocks; not replication of published fits or scientific findings |
| REV-2.4 objective/fit parity | NOT_GLOBAL_PASS / independent review still scoped | Claim only verified family/vector results; do not assert universal fitting equivalence |
| REV-2.2 D08 discrepancy | IN PROGRESS / unresolved; original failed comparisons retained | State objective/optimizer limitations; no optimizer-convergence or full parity assertion |
| REV-2.1 warning cause | BLOCKED / not causally classified | Record 48 warning-positive blocks and 86 events, not harmlessness |
| REV-2.3 and PERF-01C timing | NOT RUN / BLOCK_FREEZE respectively | No claim of MATLAB-vs-HGFX speed superiority or inferiority |
| D2 scientific claim approval and D3 final submission approval | BLOCKED / human decisions | A provisional draft is not an approved, submission-ready paper |

Details and source references: [revision ledger](COMPSTAT_REVISION_LEDGER.md), [revision plan](COMPSTAT_REVISION_PLAN.md), [readiness gate](COMPSTAT_SUBMISSION_READINESS_2026-11-12.md), [paper files](../../paper/computational_statistics/README.md), [PR #107](https://github.com/ahmadkhanloo/hgfx/pull/107), [independent review issue #108](https://github.com/ahmadkhanloo/hgfx/issues/108), [D08 issue #111](https://github.com/ahmadkhanloo/hgfx/issues/111).

## Publication critical path (ordered)

1. **Resolve the active manuscript's claims and scope.** Maintain a plain-language, auditable distinction between same-vector objective agreement, forward-trajectory comparison, each optimizer's own fit, model-selection/recovery, physical GPU correctness, and timing. Retain negative results; do not convert a matched reference limitation into an identification success.
2. **Complete the real active-source manuscript and ESM.** Use the actual manuscript, tables, figures and citations from the active branch; make all C1–C8 critiques explicitly answered or transparently limited. Present statistical-computing contribution without relying on unsupported novelty, speed, universal parity or replication.
3. **Verify exact numeric claims and build the *real* submission artifacts.** Achieve strict machine-readable claim/evidence coverage and regenerate real Manuscript/ESM PDFs, editable source, figures, references, hashes and a build manifest. Synthetic compilation smoke tests are not substitutes for real source builds.
4. **Record D2 human scientific-scope decision** on the specific remaining claim exceptions; do not mark it complete by inference from editorial progress. If a headline claim cannot be defended, narrow it rather than execute unbounded experiments.
5. **Complete venue and legal preflight.** Check current journal format/word-count/keywords, permissions and data reuse, authorship and declarations, licensing, citation/DOI archive, preprint overlap and actual author-payable charges. Subscription/no-APC wording alone does not prove zero total mandatory charges.
6. **Run independent manuscript-delta review, final checks and D3 author approval**, then prepare the upload-ready package. Submission or acceptance is not claimed before evidenced author action.

## Explicit deprioritization and stop rules

- Do not make performance optimisation, additional GPU scaling, 1.1 beta, speculative new model families, or recurring diagnostic guard/CI work a prerequisite for the paper unless a documented claim or submission gate actually requires it.
- Do not run fresh scientific experiments without a frozen protocol, proper source/runtime pairing, preserved failures, and an identified publication-relevant question. In particular, timing remains blocked under PERF-01C's independent eligibility requirements.
- Respect the existing REV attempt caps, scientific acceptance criteria, and D2/D3 human decisions. Do not silently mark REV-2 tasks `PASS` because manuscript sections are drafted.
- If critical evidence cannot be obtained within the bounded plan, document the limitation and submit only claims defensible from existing evidence; do not present unverified results as successes.

## Next concrete handoff

Proceed with **real manuscript artifact verification and strict claims coverage** on `compstat-revision`; then prepare a concise C1–C8 disposition and D2 decision packet. Keep `COMPSTAT_REVISION_LEDGER.md` updated with the exact input commit, build commands, pass/fail outputs, artifact hashes, and remaining human approvals. Update this document when the author changes the target journal or publication goal.
