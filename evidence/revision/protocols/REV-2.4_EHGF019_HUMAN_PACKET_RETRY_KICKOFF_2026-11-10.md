# REV-2.4 eHGF019 HUMAN review packet — single non-science packaging retry kickoff

This document launches the **one and only** source/ZIP packaging retry described in [REV-2.4_EHGF019_HUMAN_PACKET_INFRA_RETRY_2026-11-10.md](REV-2.4_EHGF019_HUMAN_PACKET_INFRA_RETRY_2026-11-10.md), commit `f6bb254d0350cc2e2b5489c0d1417682f6cc929a`.

Original packaging [Actions 42820014023](https://github.com/ahmadkhanloo/hgfx/actions/runs/42820014023) failed when `py_compile` created an unlisted bytecode cache after the frozen bundle file digests were counted. Fix `b74b7134a0042ec5d464b4c25f825175439a179d` replaces **only** that syntax check with `ast.parse`; it adds no numerical work and does not alter any source, evidence, statistical threshold or source-revision acceptance gate.

Launch one Ubuntu source-only packaging run; confirm SHA256SUMS, original synthetic three artifacts, original MATLAB/released/dev source Git blobs, original eHGF019 trial 8/11 archived divergence and output ZIP integrity. Retire the one-shot trigger immediately. This is not a new paired MATLAB/HGFX science run, full CI or human sign-off. **Original REV-2.4 NOT_GLOBAL_PASS, D2/D3 BLOCKED.**
