# REV-2.4 / Panel G — original paired objective evidence (2026-11-10)

**Status: EXECUTED; scientific gate remains `NOT_GLOBAL_PASS`.** Original predeclared protocol `compstat-rev2-4-objective-cross-eval-v1` was committed at `d1986311b8a5ff97f088ebac35c612e16cbe89db` before execution. No subsequent changes to fixed inputs, model families, prior draws, seeds, tolerances, or exclusions were made to achieve a result.

## Original run, documented infrastructure failure, and sole allowed retry

- Original [Actions run 42776302837](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776302837) at `ae1adfbf5060ed3a2c64348a0119aca46088a851`: **failure** after generating the exact source manifest. The Python HGFX result serializer could not encode NumPy-backed `bool`, so the paired MATLAB and comparator legs did not run. The failed attempt and partial artifact `13743169745` are retained, not overwritten.
- Minimal output-only fix at `d3e74d0c417b2e0af53edec2b59748b92df59c45` casts the `valid` flag to native Python `bool`. Numeric evaluation path is unchanged.
- Synthetic regression CI [42776681727](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776681727): **24/24 tests PASS** (12 manifest, 9 paired comparator, 3 JSON output). No science claim from these synthetic tests.
- The **one protocol-permitted infrastructure retry**, with prospective record `evidence/revision/protocols/REV-2.4_INFRASTRUCTURE_RETRY_2026-11-10.md`, ran as [Actions 42776781367](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776781367) on source `c5c44d284a95b291c20d736e17bbb38ed1d865bd`; conclusion **success**. The one-shot triggers were removed after launch. This was the only scientific retry.

## Execution identity

- MATLAB HGF Toolbox **8.2.0**, frozen source `2437f4dc241541072722a2695ddeca7b44d83dd3`; MATLAB runtime **26.2.0.3433840 (R2026b) Update 1** on Actions Ubuntu 24.04 hosted CPU.
- Published HGFX **1.0.0** Wheel `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`, frozen Python source commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` source-byte checked against v1.0.0; Python **3.11.18**, NumPy **2.0.2**, JAX/JAXLIB **0.10.2** CPU float64. `JAX_ENABLE_X64=true`, `JAX_PLATFORMS=cpu`; no physical-GPU science claimed.
- Manifest fixed `200 × 3 = 600` cases, `T=128`, unchanged model-ordered per-family seeds `2026111000/001/002`, no resampling or exclusions. Manifest semantic SHA-256 `35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95`, identical between the original attempt and the permitted retry.
- Full original GitHub Actions evidence: [artifact 13743694091](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776781367/artifacts/13743694091), ZIP SHA-256 `faebd113e9ee050a2490d08e1d1fbc54ba589becd1015d41cab4e7879a785b1c`. Exact unmodified member-file SHA-256: `manifest.json` = `59d86cb1687944841b802a2d6f4d4f9e2851eb59ba28abf9edbf332668718cec`; `hgfx.json` = `70fd09db1efac4d8d4df2e441525216850d302bd9cd0ee315f5681597c701503`; `matlab.json` = `54df9fd43c1044f6a7dd6d2c485a9bd76c8da7757d1dee276a4003f31d5b2397`; `comparison.json` = `cfd0c7e9f66890c2873706b77518a721119b725a04393ad99ef71e573c780430`.
- These evidence objects are **new**, not replacements for v1.0.0/M18 archived evidence. Reproduce the numbers from the four original member files; do not create any new scientific run from this report.

## Complete, original 200-per-family denominators

| Family (all with unitsq_sgm) | Both valid | Both invalid | One-sided invalid | Numerically within pre-existing family objective gate | No such registered gate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `hgf_binary` | 164 | 36 | 0 | 164 of 200, for both-valid cases only | 0 |
| `ehgf_binary` | 198 | 1 | **1** | Not classified | 198 |
| `uhgf_binary` | 198 | 2 | 0 | Not classified | 198 |
| **Total** | **560** | **39** | **1** | **164 HGF both-valid evaluations only** | **396** |

Under the **pre-existing HGF M8 objective threshold only** (`rtol=2e-11, atol=2e-13`), all 164 HGF both-valid cases have within-gate negative log likelihood, negative log joint, log likelihood, and per-trial likelihood; max objective absolute difference `7.275957614183426e-12`. The other **36 HGF cases are both-invalid**, not numerical passes. For 198 both-valid eHGF and 198 both-valid uHGF cases, raw max absolute objective differences are `6.139089236967266e-12` and `1.2732925824820995e-10`, respectively, with median `0` for the measured aggregate objective fields. **These raw discrepancies are not acceptance verdicts:** no pre-existing family-specific objective tolerance was pinned for either model; the HGF threshold was not extrapolated.

## Asymmetric case requiring scientific adjudication

- Case: `REV24-G-ehgf_binary-019` (ordinal 19, zero-based), frozen source case SHA-256 `276d21f43a91fc8748438aafc6ec44f759f23dc2ae97dae8b4cc1274aba3fefb`, classification `ONE_SIDED_INVALID`.
- MATLAB: valid negative log likelihood `2607.6645961917793`, negative log joint `2616.3086647541677`, finite trial log likelihoods. HGFX: `rval=0` but `log_likelihood='NaN'`, `neg_log_joint='NaN'`, negative log likelihood finite sentinel `1.7976931348623157e+308`; `valid=false`.
- **First observable failure**: trial **11 zero-based** (twelfth trial), HGFX trial log likelihood `NaN`, MATLAB `-43.96492349971353`. At trial 10 the two log likelihood values were identical (`-3.597816489175898e-15`). This is **not** proof that the first causal latent-state divergence occurs on trial 11.
- Both implementations returned identical perceptual prior sum `-5.684306257480424` and observation prior sum `-2.9597623049080344` for this fixed vector. Latent trial/level/state/intermediate diagnosis is `NOT_EXPORTED`; distinguish objective implementation/numerical mismatch from scientific model limitation only after same-vector intermediate evidence is available. Do not invoke threshold relaxations or resampling.
- The scientific record also retains 39 both-invalid cases across families, all with original case IDs and status; shared invalidity is not a positive parity result. Runtime NumPy warnings are not silently filtered.

## Acceptance and next action

**Panel G is executed, evidence complete at the paired-objective output boundary, but REV-2.4 scientific gate is NOT PASS.** Existing HGF M8 valid-domain agreement is supported for precisely 164/200, while 39 jointly invalid, 1 asymmetrically invalid and 396 valid cases lacking family-specific gates prevent broad family parity claims. Gradient and causal latent-state comparisons are not established. No global fit, optimizer path, identifiability, LME or model-selection parity is inferred.

Panel E remains **OPEN**: D02 original HGFX full endpoint is missing, while D08 and 64 original subjects have both endpoint sources and a private 66-case input manifest was constructed by source CI [42775979436](https://github.com/ahmadkhanloo/hgfx/actions/runs/42775979436). No Panel E MATLAB/HGFX cross-evaluation has been run. The REV-1.4 `DOCUMENTED_LIMITATION`, original P3 FAIL, 63/64 original full-fit NONPASS, M18 recovery FAIL and PERF-01C `BLOCK_FREEZE` remain unchanged. Before any scientific gate promotion or manuscript claim, require independent review of the paired artifact, first-observed failure, source provenance, and missing objective family gates; D2/D3 remain human decisions.
