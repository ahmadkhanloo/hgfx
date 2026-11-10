# REV-2.4 D019 — execution of the sole infrastructure retry (2026-11-10)

This document authorizes **the single infrastructure-only retry** explicitly recorded in `REV-2.4_EHGF019_DIAGNOSTIC_RETRY_2026-11-10.md` (source `2a1c7665eff9501e001a2516594ba37aa3f14f50`), after the original D019 diagnosis [run 42796827923](https://github.com/ahmadkhanloo/hgfx/actions/runs/42796827923) stopped **before numerical execution** on an incorrect three-of-four ZIP member inventory check.

Only the original member inventory map was fixed and tested (complete source archive includes `comparison.json`), synthetic contract CI [42797274300](https://github.com/ahmadkhanloo/hgfx/actions/runs/42797274300) PASS. Preserve original failed job and its exact SHA/step. **No parameter, input, seed, numerical method, family, threshold, model or dataset changed.**

Use the same original single synthetic `REV24-G-ehgf_binary-019` vector and exactly 128 trials, frozen original Wheel/HGF 8.2.0, no optimizer, no full 600-case rerun. Retain first finite-state asymmetry and raw diagnostic traces; any observed outcome is *not* a global scientific parity PASS. Upon launching this workflow, retire the one-shot trigger. No further diagnostic attempts are authorized by this protocol.
