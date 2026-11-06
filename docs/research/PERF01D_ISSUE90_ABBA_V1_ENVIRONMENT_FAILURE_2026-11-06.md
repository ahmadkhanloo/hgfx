# PERF-01D / Issue #90 — first ABBA control rejected by its own prespecified environment gate

**Run 42248605099: ENGINEERING CONTROL NONPASS, not scientific model failure, no retrospective protocol waiver.** Exact tested SHA `64031c63b034c16ba1d8bbd350e237d444fe2eba`; original v1 predeclared control `PERF01D_ISSUE90_ABBA_PRESPEC_2026-11-06.md`; original MATLAB 64-fit 63/64 NONPASS unchanged.

The workflow passed all existing/new regression tests, restored SHA-locked original MATLAB/HGFX 64-fit files, pinned the same logical CPU set `[0,1,2,3]` for all four Python processes, and ran four actual untouched frozen HGFX public fits without timers. Each raw record was preserved in original [artifact 13518434160](https://github.com/ahmadkhanloo/hgfx/actions/runs/42248605099/artifacts/13518434160).

**Unexpected controlled fact:** the effective OpenBLAS 0.3.30 kernel of *all four* processes was `Haswell`, including the two `OPENBLAS_CORETYPE`-unset auto processes. Source v1 explicitly required auto→SkylakeX; its fail-closed comparator stopped with `ValueError: Effective OpenBLAS mode/thread/version not verified: auto_1`, as intended. Therefore **the prespecified kernel contrast was not realized**; no 28-field derived result or scientific comparison can be certified from v1. CPU model/other environment fields remain in the retained artifact. Failed workflow [42248605099](https://github.com/ahmadkhanloo/hgfx/actions/runs/42248605099) is preserved rather than revised or reinterpreted.

Raw fit JSON SHA-256 on that same runner:
- `auto_1` = `2e6a0f63bbbe2e7ea20ff4405783fb261666b7cfdd98c6ca5d7a2dfaff443848`
- `Haswell_1` = `40e1a1fab41e54ce85b356bf5153b307efd3c7ed841f3ecd1ed658445d9808f5`
- `Haswell_2` = `40e1a1fab41e54ce85b356bf5153b307efd3c7ed841f3ecd1ed658445d9808f5`
- `auto_2` = `2e6a0f63bbbe2e7ea20ff4405783fb261666b7cfdd98c6ca5d7a2dfaff443848`

Matching raw hashes *within* each requested mode include distinct mode labels in the JSON; they are only a bounded observed byte-identity fact. With **the same actual BLAS core in all modes**, the run is not evidence of a kernel effect, numerical optimizer scientific parity, or universal determinism. The original complete public fitting scientific status remains **63/64 NONPASS** and PERF-01C is NOT FROZEN.

The separately preregistered **v2** explicitly requests `OPENBLAS_CORETYPE=SkylakeX` for A and `Haswell` for B and checks the actual effective kernels. If the host cannot execute a requested kernel safely, v2 must FAIL and retain its artifact; do not select another kernel retrospectively.
