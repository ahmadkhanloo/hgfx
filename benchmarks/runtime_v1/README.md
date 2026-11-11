# PERF-01 deterministic input preparation (NOT frozen)

Protocol: [runtime comparison protocol](../../docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V1.md), issue [#86](https://github.com/ahmadkhanloo/hgfx/issues/86).

**Current status, 2026-11-04:** canonical candidate JSON arrays and nine HGFX 1.0.0 configuration/start snapshots are **committed, hashed and reproducible**. Public GitHub Actions executed the frozen HGF 8.2.0 MATLAB reference on R2026a and checked its default start/prior identity for the first subject of each model/horizon. Five predeclared stage records fail in **both** implementations; this is preserved, not repaired by changing data. **PERF-01B/C are NOT FROZEN; scientific parity, fitting equivalence and all speed claims remain OPEN.** See [paired preflight report](../../docs/research/PERF01_PAIRED_PREFLIGHT_2026-11-04.md).

## How to generate / verify

With Python 3.11+ and NumPy (producer tested on Python 3.13.5, `numpy==2.3.5`):

```bash
python benchmarks/runtime_v1/generate_inputs.py --output /tmp/hgfx-perf01
python benchmarks/runtime_v1/generate_inputs.py --output /tmp/hgfx-perf01 --check
python -m unittest discover -s tests -p 'test_perf01_inputs.py' -v
```

Produces `inputs/binary_128_s64.json`, `inputs/binary_512_s64.json`, `inputs/binary_1024_s64.json`, and `inputs_manifest.json`. The generator **refuses to overwrite** a changed input or manifest. `--check` validates byte-for-byte determinism without overwriting.

Candidate SHA-256s verified both locally and in the fixture-materialization CI (NOT a frozen paper manifest):

| File | SHA-256 from local producer test |
|---|---|
| `binary_128_s64.json` | `6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae` |
| `binary_512_s64.json` | `6c58eac5626be96d475a12f0f1f18c16abfc8abbaa2e1eaf30e9369e0ba7be07` |
| `binary_1024_s64.json` | `83fc36d7d7a08a10400d47b17f4ae410d9046e1c957a4a54e0d15989b153887b` |

## Input and matrix contract

- NumPy `PCG64(SEED+trial_count)`, `SEED=20261104`; binary stimuli `u` and noise-flipped binary responses `y`. Synthetic input is **not** a ground-truth HGF model recovery dataset.
- 64 stable, ordered subject rows for each horizon; first 1/16/64 subject rows are shared across single-subject and throughput cells.
- Primary: 9 cells (forward, fixed objective and complete compatibility fit × 128/512/1024).
- Secondary: 12 conditional cells (eHGF/uHGF forward and objective × the three horizons).
- Throughput: 6 cells (1/16/64 subjects × 128/512 trials).
- Robustness: one separate 512-trial masked cell, predeclared 0-based positions `ignored_input_and_response=[31,127]`, `irregular_response_only=[63,255]`. Runner must map these to MATLAB `NaN` and HGFX mask semantics and independently validate the mapping before timing.
- Data are encoded as JSON integers 0/1 for portable exact interchange; all scientific computations load them as **binary64**. MATLAB and HGFX must consume the *same committed exported bytes* rather than independently sample random streams.

## Completed preparation and remaining gates

- The nine resolved config files, their checksums, source IDs, fixed/free indices, prior vectors, and transformed starts were exported from an isolated `hgfx==1.0.0` installation (not beta). CI [41850645631](https://github.com/ahmadkhanloo/hgfx/actions/runs/41850645631) passed.
- MATLAB R2026a with HGF Toolbox 8.2.0 was executed on exact canonical inputs; 9/9 first-subject start/prior identities passed. CI [41852401008](https://github.com/ahmadkhanloo/hgfx/actions/runs/41852401008) passed.
- HGFX-only preflight CI [41851191076](https://github.com/ahmadkhanloo/hgfx/actions/runs/41851191076) captured retained failures; see the [full paired evidence](../../docs/research/PERF01_PAIRED_PREFLIGHT_2026-11-04.md) and the generated `paired_preflight_runs/` record.
- Exact matched CPU thread/hardware/runtime identity, optimizer/postprocessing boundaries, 64-subject MATLAB config coverage, trialwise numerical tolerance policy, independent review and prospective evidence freeze **remain open**. This first-subject preflight must not be misrepresented as full scientific equivalence.
- Full fitting, throughput and speedup have **not** been measured. Existing invalid-approximation cases remain recorded; no replacement data or start vectors are permitted to erase them.

Do not label PERF-01B or PERF-01C PASS based on generator success. Historical M17 speed, T4 GPU applicability, M18 failures, M19 and the paper protocol 1 freeze remain separate.
