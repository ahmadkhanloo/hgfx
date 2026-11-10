# REV-2.4 Panel G — authorized infrastructure retry 1/1 (2026-11-10)

**Protocol ID:** `compstat-rev2-4-objective-cross-eval-v1`; originally preregistered at commit `d1986311b8a5ff97f088ebac35c612e16cbe89db`. Its one-run policy expressly permits **at most one** repeat for an independently documented infrastructure failure.

## Original attempt — permanent failure record

- Original run: [42776302837](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776302837), source `ae1adfbf5060ed3a2c64348a0119aca46088a851`, conclusion **failure**.
- Frozen MATLAB toolbox checkout verified; released HGFX 1.0.0 Wheel downloaded, SHA-256 verified; manifest generated once and archived, reported manifest hash `35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95`.
- HGFX fixed-vector evaluation reached result serialization; Python `json.dumps(..., allow_nan=False)` raised `TypeError: Object of type bool is not JSON serializable` at `tools/compstat_rev24_hgfx_eval.py:165`. The `result['valid']` expression included `numpy.bool_`, which is not Python's JSON Boolean.
- No complete HGFX result JSON, no MATLAB 600-vector run, no paired comparison or scientific PASS occurred. Original attempt artifact `13743169745` retained; original failure must not be overwritten or hidden.
- Numeric warnings observed in the released runtime are retained as runtime warnings; not interpreted or excluded based on the failed attempt.

## Bounded correction and pre-retry validation

- Code patch `d3e74d0c417b2e0af53edec2b59748b92df59c45`: cast only the output validity flag to native Python `bool(...)`; mathematical evaluation, inputs, random generator, optimizer, source release and tolerances unchanged.
- Synthetic output regression `tests/paper/test_compstat_rev24_hgfx_output.py` checks valid, invalid, and exception paths, preserving all cases and JSON serializability.
- Independent no-science CI run [42776681727](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776681727) **success**, 12 manifest + 9 comparator + 3 JSON output contract tests PASS. This is not numeric parity evidence.
- This retry uses the **same** frozen original protocol, model families, 200×3 vector definition, per-family RNG seeds, NumPy 2.0.2, pinned HGFX 1.0.0 Wheel, MATLAB reference and pre-existing objective tolerances; no exclusions, resampling, output rewrites or reinterpretation.

**Authorization:** latest author instruction was to continue execution; only the existing preregistered **one** infrastructure rerun is now used. If any additional failure occurs, stop, retain complete evidence, and escalate; no third run without a prospective, separately authorized protocol change. Panel E D02/D08/64 cross-endpoints remain distinct and unexecuted.
