# PERF-01 deterministic input preparation (NOT frozen)

Protocol: [runtime comparison protocol](../../docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V1.md), issue [#86](https://github.com/ahmadkhanloo/hgfx/issues/86).

**Status 2026-11-04:** input **generator implemented and unit-tested**, but source arrays, per-model full configurations/priors, starts and acceptance-tolerance mapping are **not yet committed and locked together**. This is **not** completion of PERF-01B or PERF-01C. No HGFX/MATLAB fitting, timing or scientific parity was tested.

## How to generate / verify

With Python 3.11+ and NumPy (producer tested on Python 3.13.5, `numpy==2.3.5`):

```bash
python benchmarks/runtime_v1/generate_inputs.py --output /tmp/hgfx-perf01
python benchmarks/runtime_v1/generate_inputs.py --output /tmp/hgfx-perf01 --check
python -m unittest discover -s tests -p 'test_perf01_inputs.py' -v
```

Produces `inputs/binary_128_s64.json`, `inputs/binary_512_s64.json`, `inputs/binary_1024_s64.json`, and `inputs_manifest.json`. The generator **refuses to overwrite** a changed input or manifest. `--check` validates byte-for-byte determinism without overwriting.

Tested local input-file SHA-256s, not a frozen paper manifest:

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

## Remaining PERF-01B requirements (blocking)

1. In an isolated, verified `hgfx==1.0.0` environment, serialize default `hgf_binary`, `ehgf_binary`, `uhgf_binary` and `unitsq_sgm` configs, *resolved* priors, fixed/free masks and transformed start vectors; verify against frozen MATLAB 8.2.0 for the same inputs. Do not copy configs from current `main` (currently beta).
2. Define the runner's exact forward/objective fitting boundaries, MATLAB `fitModel` postprocessing scope, optimizer configuration and fixed tolerance policy; mark non-comparable fast-fit results instead of forcing numerical parity.
3. Review and commit the **actual** canonical input JSON files and complete manifest with hashes, scripts and environment lock; the current locally tested SHA-256 values are diagnostic until that happens. Do not time any case whose input file is missing or has an unexpected hash.
4. Independently review and freeze protocol+manifest as PERF-01C before final comparative measurements.

Do not label this gate PASS based on the successful generator unit tests. Historical M17 speed and T4 GPU applicability remain separate.
