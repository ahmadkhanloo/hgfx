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

## Subsequent author-side evidence for the independent reviewer (2026-11-04)

The exact 64-subject, three-horizon, three-model MATLAB/HGFX fixed-vector cohort comparison completed on the same CI CPU runner: [GitHub Actions 41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774). All **576** declared model–horizon–subject combinations were retained: **448 matched valid** and **128 invalid in both**, corresponding to all 64 standard-HGF subjects at 512 and all 64 at 1024 trials. No config or scalar objective discrepancy was detected under existing diagnostic thresholds. These are not 576 matched fits or per-subject full-trajectory parity certifications.

- Machine-readable cohort results and 27 one/16/64-subject strata: `benchmarks/runtime_v1/cohort_results/summary-41860187774.json` (SHA-256-provenance links to raw CI artifact).
- Original archived push-race failure: [run 41859496548](https://github.com/ahmadkhanloo/hgfx/actions/runs/41859496548), where numerical evaluation and comparison succeeded but the evidence commit was rejected as non-fast-forward. Do not delete or recategorize it as scientific failure.
- Complete prefreeze inventory with all **28 originally planned cases**, showing **16 diagnostic-concordant/review-pending** and **12 blocked**, with no claim of final eligibility or scientific PASS: `benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json`, generated by [run 41860891268](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860891268).
- Timeable API/host/stdout/restart policy hazards: [PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md](PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md).
- Independent review request: [issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88).

**Do not close PERF-01C:** this section is an implementer evidence handoff, not an independent approval. In particular, the original nine-cell primary CPU speedup headline is ineligible under the observed failed frozen cells; no threshold may be weakened or originally defined case silently replaced. A new prospective protocol for a genuinely different headline, if wanted, requires separately justified scope and prior independent approval.


## Mandatory follow-up independent review: full-cohort fitting and source-only MATLAB sensitivity

Evidence from this stage is no longer pending:

- Original 64 public full fits: [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json`; 63 concordant, 1 out-of-tolerance original subject 7; nested denominators **1/1, 15/16, 63/64**. Full workflow remains a scientific **non-PASS**.
- Exact two-endpoint replays: [41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514), `benchmarks/runtime_v1/subject7_results/summary-41868723514.json`; both exact frozen fitted endpoints have MATLAB/HGFX concordant trajectories, states and trial likelihood; differences occur between distinct optimizer endpoints.
- Frozen MATLAB **self-sensitivity**, not modified reference software: [41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069), `benchmarks/runtime_v1/matlab_sensitivity_results/summary-41870479069.json`. The independently scripted exact-form objective *first reproduces original MATLAB optimizer endpoint with zero discrepancy*, then holds data/model/priors fixed and perturbs each of three free start parameters by ±eps. One of six probes has a final shift `7.640946009246363e-7` outside original M10 fitting tolerance.
- Exact derived author-side ledger, **original evidence untouched**: `benchmarks/runtime_v1/eligibility_candidates/candidate_v2_fullfit41863441006.json`, [run 41869747776](https://github.com/ahmadkhanloo/hgfx/actions/runs/41869747776). All 28 original cases preserved, 16 review-pending and 12 blocked, with two blocked fitting reasons now supported by actual failed complete-fitting evidence.

The independent reviewer must **check the source-only MATLAB objective against `fitModel.m`**, the exact original baseline reconstruction, all six perturbation endpoints and original source-vector raw artifact hashes, and decide whether these meet the **narrow** `MATLAB_REFERENCE_LIMITATIONS_POLICY.md` requirements for an explicitly delimited numerical-basin classification. The implementer must **not self-certify**, change the frozen 63/64 outcome, silently exclude subject 7, or promote grouped fitting to benchmark eligibility. Check optimizer termination and iteration histories as a separate scientific limitation question. No performance timing has occurred.


## 2026-11-06 additional author-side reviewer evidence

The [six-source replay report](PERF01C_SIX_SOURCE_EVIDENCE_REPLAY_2026-11-06.md) links the exact tested commit (1dd22bc5eef4502136e6b61a586d2129be951a8d), [Actions run 42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894) and machine artifact. This regression directly downloads and SHA-256-checks original raw MAT/HGFX archives and the standalone MATLAB-only sensitivity export; replays scientific comparison programs on those files; checks both 28-case ledgers; independently recalculates all six +/-eps(start) reference probe step sizes and original M10 final-parameter tolerance decisions. **47/47 engineering tests passed.**

For independent scientific sign-off, do not simply cite the green CI: separately audit the original frozen MATLAB source function paths and full fitModel objective, optimizer termination/iteration regime, scientific model and mask, specific subject-7 basin explanation and the proposed timing-boundary/hardware contract. No reviewer identity, independent APPROVE_PROSPECTIVE_FREEZE, versioned lock or performance timing exists. The existing **63/64** fitting failure and **12 blocked cases** remain unchanged.
