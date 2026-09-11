# M18 horizon diagnosis — first reproducible result

Date: 2026-09-11. Matrix IDs: P02/P03/P04, C01/C04, O17.

## Scope and evidence

R0 prerequisites ran locally on Python 3.12 / NumPy 2.5.3 / JAX 0.11.1:

- frozen reference guard PASS: 334 MATLAB files, commit `2437f4dc241541072722a2695ddeca7b44d83dd3`;
- corrected M18B unit tests: 39 passed;
- baseline full regression: 136 passed, 4 physical-GPU skips (93.98 seconds);
- new horizon diagnostic tests: 4 passed (including duplicate-evidence rejection);
- corrected M18B full gate: **local PASS**, 27 datasets / 81 raw records / zero failures; independently recomputed from archived records. Raw output is `reference/validation/m18b_corrected_local.json.gz`; hashes and tested source are in the adjacent provenance JSON. CI run 34567774302 remains separately pending.

R1 reconstructs **all** 3 models × 3 trial counts (128/256/512) × 3 replicas × 2 points (prior/truth) from `225f565^`. It exports actual inputs and transformed parameters so MATLAB does not have to reproduce NumPy RNG. The historical failing CI log has not yet been matched to an exact cell; this is a reproduction from the historical protocol, not a claim of identical historical runtime execution.

## Concrete Python finding

For HGF, 512 trials, replica 0, prior point, seed `233100`:

- the normal compatibility forward call rejects the trajectory;
- the explicitly unchecked diagnostic trajectory has finite `mu` and `pi` at the checked levels 2–3 (level-1 precision is conventionally infinite);
- maximum mean jump/RMS ratio: approximately 3.7318;
- maximum precision jump/RMS ratio: approximately **19.6822**;
- precision jump destination: trial **2**, level **2** (one-based);
- the frozen standard-HGF trajectory guard threshold is **16**.

Thus this specific rejection is a finite precision-jump guard failure, not overflow. This does not explain every warning or failed fit. Overflow during derivative/profile exploration remains separate evidence.

For a column with N trials, each absolute difference divided by its RMS is bounded by `sqrt(N-1)` (when RMS is nonzero). Consequently, the strict `>16` jump test cannot fire at N ≤ 257 in exact arithmetic. Passing a 256-trial test does not exercise this rejection branch. This is a property of the reference rule, not grounds for removing or weakening it.

The reference `building_blocks/hgf_check_trajectories.m` contains the same rule. Direct MATLAB execution is still required before claiming shared runtime failure. The public compatibility implementation and original M18 thresholds are unchanged.

## Reproduction and paired execution

```bash
python scripts/reproduce_m18_horizon.py
python -m pytest tests/unit/test_m18_horizon_reproduction.py -q
```

In MATLAB, from repository root:

```matlab
addpath(fullfile(pwd,'reference','matlab'));
export_m18_horizon('benchmarks/results/m18_horizon_python.json', ...
                   'benchmarks/results/m18_horizon_matlab.json');
```

```bash
python tools/check_m18_horizon.py \
  benchmarks/results/m18_horizon_python.json \
  benchmarks/results/m18_horizon_matlab.json \
  --output benchmarks/results/m18_horizon_comparison.json
```

The new GitHub workflow performs this paired run with the unmodified frozen MATLAB source. It uses existing M4/M5/M6 forward tolerances: rtol=5e-11, atol=5e-13. Nonfinite masks and shape are compared separately. Unrelated MATLAB errors fail comparison.

A shared rejection is reported separately and never called complete raw-state parity. Comparing the intermediate states of rejected MATLAB trajectories remains an R1 task. The unchecked Python diagnostic is never used for fitting, gate acceptance or production output.

## Existing M18C branch

Commit `a8137b9` adds a horizon recovery runner outside main. It is useful exploratory work but lacks paired MATLAB execution and writes aggregate results only after the entire sweep. It does not replace R0/R1. This change leaves that branch intact.

## Next actions

1. Finish and archive corrected M18B full gate with source hashes.
2. Execute the paired MATLAB horizon workflow and inspect its raw artifact.
3. If both reject, compare rejected intermediate states before declaring the full failure mechanism shared; if they disagree, locate the first divergence before changing numerics.
4. Continue same-data objective/fitting comparison under R3; do not substitute unchecked trajectories or easier seeds to make M18 pass.

## Executed MATLAB result

Paired workflow 34568178526 at head `f2c32a4b93fc7bbf05f686eaf923d14b132db385` executed successfully. MATLAB agreed on 49 valid forward cases within existing tolerances and rejected the same 5 HGF 512-trial cases with `tapas:hgf:VarApproxInvalid`. No comparison mismatches were reported. The first case also successfully generated 512 responses in Python; the prior objective returned rval=-1 before optimization.

Artifact: `10186808228`, SHA256 reported by GitHub: `9785b2df36b995f9fb3e2971519c39acc3f9818170b596629f95a51be80adc48`. Job logs and artifact metadata confirm the result. Direct ZIP materialization returned HTTP 403, so no local rehash of that ZIP is claimed. See `reference/validation/m18_horizon_evidence.json`.

This establishes matching validation boundaries and valid-case trajectories, not equality of the rejected raw intermediates. R0 is locally complete; R1 is partially complete. R2 must preserve the reference guard; R3 paired inference remains open.

## Verified execution update — 2026-09-11 06:04 UTC

R0 corrected M18B gate is now PASS locally **and in CI** (run `34567774302`, artifact `10186837061`). See `reference/validation/m18b_corrected_ci_provenance.json` and the archived complete local records. This supersedes earlier pending-CI text. Paired MATLAB horizon run `34568178526` also passed within its explicit scope: 49 valid trajectories and 5 shared rejection boundaries. R1 rejected raw intermediates and R3 paired inference remain open. Historical M18 stays FAIL; no scientific release gate is waived.
