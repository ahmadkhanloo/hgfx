# REV-2.4 / Panel E — original paired cross-endpoint evidence (2026-11-10)

**Scientific gate: `NOT_GLOBAL_PASS`.** This is same-vector objective evaluation at historical fitted endpoints, **not** reproduction of optimizer paths, trajectories, Hessians, model selection, identifiability or fit-level equivalence.

## Frozen execution and provenance

- Preregistered protocol `compstat-rev2-4-objective-cross-eval-v1`, committed at `d1986311b8a5ff97f088ebac35c612e16cbe89db` before execution. Explicit [Panel E kickoff](../../evidence/revision/protocols/REV-2.4_PANEL_E_KICKOFF_2026-11-10.md), source commit `4708518b0304eabb16fd0840f75d368cddb4710d`.
- **One original Panel E paired run:** [GitHub Actions 42786519173](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786519173), conclusion **success**, on Ubuntu 24.04 hosted CPU with Python 3.11, NumPy 2.0.2, JAX x64 CPU, original MATLAB HGF Toolbox 8.2.0 source SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, published HGFX 1.0.0 Wheel SHA-256 `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`, frozen Python source `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. No new fitting, RNG, optimizer, parameter substitutions or GPU validation.
- Independent Panel E synthetic / source preflight [run 42786175954](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786175954): **22/22 contract tests PASS**, original three archived source digests and 66-case input coverage verified. Synthetic contracts do not count as objective science.
- Original D02 artifact `10339454535` / 320 trials / **`ehgf_binary+unitsq_sgm`**, original observation prior variance `0.5`; original D08 `10339403480` / 614 trials / **`uhgf+gaussian_obs`**, original observation prior variance `0.1`; original 64-subject `13341288055` / 64 × 128 trials / **`hgf_binary+unitsq_sgm`**, original observation prior variance `1.0`. Original cohort inputs pinned to `81ae256b318e18ea08b03ab6fcb69100ac6c836d`, content SHA-256 `6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae`. See [source coverage](REV24_PANEL_E_COVERAGE_2026-11-10.md).
- Sanitized result artifact: [13749028134](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786519173/artifacts/13749028134), ZIP SHA-256 `41e2aca61afb0d1961c653b87db3b36a1edd204f7b68ee0b362c958474fb96bb`. Inside: `panel_e_comparison.json` SHA-256 `051aea43a11f7788b85d64a9cb8e82a59a274a70aa347f1927920d991a8ce86d`; `input_source_audit.json` SHA-256 `fad8d25354ea0a367fb901fe7c4111db4a4e3390274494269662e8755001890d`. Private original data, full vectors and per-trial raw results were deliberately removed, not made public. The source archive hashes, complete source comparison code and sanitized per-case objective-difference table enable independent source reconstruction **subject to original artifact retention**. Source result semantic SHA-256: HGFX `a3ef20ffff7a67f7c7784803b1111b1256581a0367aa857da5efcb2587b8da40`, MATLAB `46261d34fafb984bc669488c90a091cd18a91bd83f9c7b2232326caca80c1308`.

## Original 132 endpoint slots, no exclusions

| Original case family | Endpoint slots per implementation | Valid matched MATLAB/HGFX evaluations | Status |
| --- | ---: | ---: | --- |
| D02, eHGF binary/unitsq | 2 | 1 | Original HGFX **fitted endpoint 15-vector MISSING** in archival source; no family-specific objective gate |
| D08, uHGF continuous/Gaussian | 2 | 2 | Both vectors present, both sides valid; **no registered uHGF objective gate** |
| Original 64 HGF binary subjects | 128 | 128 | All paired evaluations valid and **within the original HGF M8 same-vector gate** |
| **Total** | **132** | **131** | **1 original missing endpoint** (never reconstructed or omitted) |

- The two execution paths produced **131 valid** original endpoint objective evaluations **each**, plus the explicitly missing D02-HGFX endpoint. No invalid return or malformed trial vectors in this observed Panel E run. This is **not** a 132/132 scientific PASS.
- Across 128 original HGF cohort endpoint slots, maximum absolute MATLAB-vs-HGFX **negative log joint** difference is `2.842170943040401e-14`, median `0`; the same maximum applies to negative log likelihood and log likelihood, with zero prior-sum differences. All valid 128 have within-gate scalar and full trial-level likelihood under the pre-existing `rtol=2e-11, atol=2e-13`. No thresholds were altered.
- Original cohort subject 7: at its MATLAB endpoint, negative-log-joint difference `1.4210854715202004e-14`; at its HGFX endpoint `0`. Both 128-trial same-vector comparisons are within M8. **Original 8 trajectory violations remain out of gate and 63/64 historical diagnostic NONPASS remains unchanged**.
- D02 at its **original MATLAB endpoint**: cross-implementation aggregate likelihood/joint and prior sums match exactly in the archived decimal output; first non-bitwise-identical per-trial likelihood at index 5 has absolute difference `4.440892098500626e-16`. No eHGF family PASS classification without the registered family gate. Missing original HGFX endpoint prevents the other D02 slot.
- D08 at both original endpoints: archived aggregate objective and reported trial likelihoods agree numerically to the exposed precision; `uhgf+gaussian_obs` is **not** substituted with the binary uHGF Panel G. No uHGF family gate has been inferred from HGF.
- `first_causal_state=NOT_EXPORTED`, `gradient=NOT_AVAILABLE` are explicit for all rows. Paired endpoint **same-vector gaps** are measured, but the sanitized artifact **does not retain the within-implementation objective gap between the two different endpoints**; do not claim such a gap was measured or use objective closeness as proof of inference equivalence.

## Scientific interpretation and remaining gates

1. Panel E establishes **128/128 original HGF same-vector objective agreement within the established M8 family criterion**, including subject 7; it does **not** reverse optimizer endpoint, Hessian/covariance, model-selection or trajectory failures.
2. D02 full original HGFX endpoint remains `INSUFFICIENT_REFERENCE_EVIDENCE`. D02/eHGF and D08/uHGF objectives are **raw observations**, not family-specific PASS.
3. Panel G still has original 39 jointly invalid and 1 one-sided-invalid `REV24-G-ehgf_binary-019`, with first observed nonfinite trial 11 (zero-based), but first latent cause not exported. **No third Panel G experiment** is permitted under the current frozen protocol.
4. Independent scientific review and registered family-specific threshold search are OPEN. M18 scientific recovery FAIL, P3 integrity FAIL, PERF-01C `BLOCK_FREEZE` and original 63-of-64 full-fit NONPASS remain preserved. Paper D2/D3 approval and journal submission are **BLOCKED**. Original Panel E run cap has been consumed; no unrecorded rerun is authorized.

**Next non-replay work:** analyze existing original fitting endpoint `negLj` values alongside the Panel E same-vector absolute-gap table to derive bounded, explicitly labeled *posthoc numerical constraints* without any additional objective evaluation; preserve source hashes and don't treat posthoc bounds as a registered acceptance criterion. Separately seek source-verifiable original D02 HGFX final vector and independent review.
