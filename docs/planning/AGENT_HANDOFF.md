# Agent Handoff

Last synchronized: 2026-09-15
Branch: `migration/m18-workflow-closure`

Read [V1_TODO](V1_TODO.md) first for the ordered remaining work, then
[V1_RELEASE_GATE](V1_RELEASE_GATE.md), [M20_GATE](M20_GATE.md),
[CI_MAINTENANCE](CI_MAINTENANCE.md), and
[the evidence index](../validation/V1_EVIDENCE_INDEX.md).

S9 physical NVIDIA GPU evidence is accepted on 2x Tesla T4; it is no longer
blocked or deferred. M19 is frozen and package/citation metadata are `1.0.0rc1`.
M20 candidate closure and fresh CI remain to be verified. Do not infer final
release PASS from an old S10 run or a queued workflow.

Historical M18 scientific FAIL and D02/D08/S7 scoped reference limitations stay
unchanged. Do not reopen historical ULP diagnostics without a genuine mandatory
current-scope regression. CPU tests cannot substitute for physical GPU evidence.
The current maintenance change touches CI/docs only, not numerical code.

Record continuation evidence in the repository, including commands, source SHA,
results and blockers. Follow AGENTS.md and the frozen validation policies.
