# PERF-01C — Independent pre-freeze review handoff

Status: **OPEN / NOT FROZEN / INDEPENDENT REVIEW REQUIRED**  
Created 2026-11-04; this document is *not* an approval or independent-review verdict.

## Immutable evidence to inspect

- Prospective (unfrozen) protocol: `docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V1.md`; nine primary CPU cells, twelve conditional secondary cells, six throughput cells, one robustness cell. **Do not shrink, re-seed or silently replace failures.**
- Input/config code and checked datasets: `benchmarks/runtime_v1/{generate_inputs.py,inputs_manifest.json,export_release_configs.py,resolved_configs_manifest.json,inputs/,configs/}`.
- Frozen product `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` versus frozen MATLAB HGF 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Full trialwise paired evidence: `docs/research/PERF01D_DIAGNOSTIC_EVIDENCE_2026-11-04.md`, `benchmarks/runtime_v1/trialwise_results/summary-41854644533.json`, GitHub Actions [41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533). Raw independent MATLAB/HGFX exports linked by SHA-256.
- Full fitting paired evidence: `benchmarks/runtime_v1/fitting_results/summary-41855647245.json`, GitHub Actions [41855647245](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855647245); failed exporter attempt [41855569387](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855569387) retained.
- Source scientific gates: `docs/validation/MATLAB_EQUIVALENCE_POLICY.md`, `docs/architecture/NUMERICAL_POLICY.md`, `tools/check_m10_parity.py`, and frozen MATLAB `core/fitModel.m` + `building_blocks/hgf_check_trajectories.m`.

## Mandatory reviewer checks

- [ ] Verify **exact** SHA identities for HGFX v1.0.0 and MATLAB oracle and corresponding active function-path resolution, including the original/unified binary HGF ambiguity.
- [ ] Independently recompute SHA-256 for each canonical input/config file and verify every MATLAB/HGFX cell references the identical selected subject, trial mask, transformed start and fixed/free parameter definitions.
- [ ] Audit original MATLAB and HGFX trajectory/observation/optimizer code against model family, data, mask, priors and the returned end-to-end field set; do not infer scientific equivalence from matching scalar objectives.
- [ ] Independently recompute per-trial differences from archived **raw** exports, including all nonfinite/irregular entries, check first mismatched trial/level/state, and confirm sequential prefix failure lengths 348/346/349 without a false monotonicity assumption.
- [ ] Audit default fitting 128 for `final`, `H`, `Sigma`, `Corr`, `LME`, `AIC`, `BIC`, objective, complete trajectory, masks and residuals. Identify any numerical/optimizer limitation from reference evidence rather than a general label.
- [ ] Confirm that MATLAB 512/1024 **auto-resamples unstable starts** while HGFX compatibility currently rejects them; preserve `NOT_DIRECTLY_COMPARABLE` and the original nine CPU cells as ineligible where documented. No data/seed/start modifications to obtain faster outcomes.
- [ ] Verify **all** timing boundaries before freeze: MATLAB full `fitModel` versus HGFX full `fit_model`; JAX compile, transfers, synchronization, result materialization, postprocessing, CPU affinity/threads and GPU physical evidence must be separate.
- [ ] Review statistical analysis (paired order, warmups/repeats, bootstrap CI, multiple comparisons), pass/fail policy and all raw-data preservation rules **before** any final timing.
- [ ] Confirm historical paper protocol `hgfx-paper-protocol-1`, M18 FAIL and M17/M19 frozen evidence remain unchanged. Performance claims require a separate paper-protocol revision frozen **before** final experiments.

## Required reviewer output

Create a new `PERF01C_REVIEW_<date>.md` with:
- exact candidate source commit SHA and all reviewed evidence hashes;
- itemized findings (CRITICAL / HIGH / MEDIUM / LOW / INFO) with direct file/line references;
- explicit `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE` and justification;
- the predeclared per-cell eligibility matrix, including all blocked cells, and proposed **new-version-only** changes if necessary;
- reviewer identity and independence from the implementer (do not self-certify);
- unchanged frozen acceptance thresholds and timing contract.

**No green CI workflow alone counts as independent scientific review.** Until signed off and a versioned protocol lock is committed, `PERF-01C = OPEN`; `PERF-01E–H = NOT EXECUTED`. The benchmark has no validated speedup claim.
