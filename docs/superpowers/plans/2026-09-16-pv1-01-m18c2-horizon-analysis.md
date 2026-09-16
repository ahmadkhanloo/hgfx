# PV1-01 M18C.2 Horizon Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and execute the preregistered paired MATLAB/HGFX M18C.2 trial-horizon experiment at 128/256/512/1024 trials and produce reproducible identifiability evidence without altering historical M18/v1 acceptance criteria.

**Architecture:** Preserve all historical M18/S7 files and add a separate post-v1 research pipeline. A small pure Python diagnostic module owns frozen constants and interpretation rules; dedicated preparer/checker/aggregator scripts handle immutable shard generation, paired fitting evidence, and final classification. A separate MATLAB runner consumes the exact exported shards. GitHub Actions performs fast protocol tests on pull requests and the full paired 24-shard experiment only when the explicit execution trigger is committed or the workflow is manually dispatched.

**Tech Stack:** Python 3.11+, NumPy, pytest, HGFX compatibility fitter, MATLAB HGF Toolbox 8.2.0 frozen at `2437f4dc241541072722a2695ddeca7b44d83dd3`, GitHub Actions, `matlab-actions`.

**Spec:** `docs/validation/M18C2_TRIAL_HORIZON_PROTOCOL.md`

## Global Constraints

- Protocol ID: `m18c2-trial-horizon-identifiability-1`.
- Trial horizons: exactly `128, 256, 512, 1024`.
- Models/candidate order: exactly `hgf_binary, ehgf_binary, uhgf_binary`.
- Truth scales: exactly `0.15, 0.35`.
- Parameter replicates: exactly `6` per model × horizon × scale.
- Model-recovery replicates: exactly `3` per generating-model × horizon × scale.
- Frozen optimizer budget: `QuasiNewtonOptions(max_iter=100)` / MATLAB `quasinewton_optim_config`.
- Frozen scientific thresholds: convergence `>=0.80`, median correlation `>=0.50`, median standardized RMSE `<=1.00`, model balanced accuracy `>=0.50`.
- Historical M18/S7/S8/S9/M19/M20/v1 evidence must not be modified or reclassified.
- No failed case, shard, candidate, seed, truth scale, or replicate may be dropped or replaced after results are observed.

---

### Task 1: Freeze protocol constants and horizon interpretation

**Files:**
- Create: `src/hgfx/diagnostics/horizon.py`
- Test: `tests/unit/test_m18c2_horizon_analysis.py`

**Interfaces:**
- Produces: `PROTOCOL`, `TRIAL_HORIZONS`, `TRUTH_SCALES`, `PARAM_REPLICATES`, `MODEL_REPLICATES`, `CRITERIA`, `parameter_check_flags(summary)`, and `classify_horizon_evidence(...)`.
- Consumes: plain mappings only; no file I/O.

- [ ] **Step 1: Write failing protocol-grid and interpretation tests**

Create tests that first assert `hgfx.diagnostics.horizon` exists, then verify the frozen constants. Add three classification cases: 256 failure resolving at 1024 => `DATA_HORIZON_LIMITATION_SUPPORTED`; 256 failure persisting at 1024 => persistent classification; any paired criterion mismatch => `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m pytest tests/unit/test_m18c2_horizon_analysis.py -q`

Expected: FAIL because `hgfx.diagnostics.horizon` does not yet exist.

- [ ] **Step 3: Implement the minimal pure diagnostic module**

Implement immutable tuple/dict constants, a helper that converts numeric parameter summaries into the three frozen boolean checks, and a deterministic classification function that follows `M18C2_TRIAL_HORIZON_PROTOCOL.md` exactly. Do not add thresholds beyond the four frozen M18 criteria.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m pytest tests/unit/test_m18c2_horizon_analysis.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "test: freeze M18C.2 horizon interpretation"`

### Task 2: Add immutable M18C.2 shard generation

**Files:**
- Create: `scripts/prepare_m18c2_horizon_shard.py`
- Modify: `tests/unit/test_m18c2_horizon_analysis.py`

**Interfaces:**
- Consumes: `hgfx.diagnostics.recovery.BINARY_VARIANTS`, `_truth_vector`, `deterministic_binary_inputs`, `simulate_binary_variant`; Task 1 frozen constants.
- Produces: `build_shard(model: str, trials: int, scale: float) -> dict` and CLI `--model --trials --scale --output`.

- [ ] **Step 1: Add a failing generator test**

Load the script module from its repository path and call `build_shard("hgf_binary", 512, 0.15)`. Assert protocol ID, 6 parameter cases, 3 model cases, exact seed formula, immutable case hashes, and rejection of any horizon outside the frozen four.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m pytest tests/unit/test_m18c2_horizon_analysis.py -q`

Expected: FAIL because the M18C.2 preparer does not yet exist.

- [ ] **Step 3: Implement the generator by preserving S7 semantics**

Copy no historical files in place. Add a new preparer that uses the exact S7 seed and truth-vector rules, only widening `TRIAL_COUNTS` to the four frozen horizons and changing the protocol/case namespace to M18C.2.

- [ ] **Step 4: Verify GREEN**

Run the focused test and generate one 512-trial shard to a temporary path. Confirm JSON is deterministic across two runs by SHA-256.

- [ ] **Step 5: Commit**

`git commit -m "feat: add immutable M18C.2 shard generator"`

### Task 3: Add paired MATLAB and HGFX shard evaluation

**Files:**
- Create: `reference/matlab/run_m18c2_horizon_shard.m`
- Create: `tools/check_m18c2_horizon_shard.py`
- Modify: `tests/unit/test_m18c2_horizon_analysis.py`

**Interfaces:**
- MATLAB runner consumes one manifest JSON and writes raw MATLAB parameter/model fit JSON.
- Python checker consumes manifest + MATLAB JSON and writes one paired comparison JSON.
- Checker retains per-fit endpoint, objective, termination, iterations/resets, BIC/AIC, MATLAB LME where exposed, and HGFX inverse-Hessian spectrum/rank/condition diagnostics.

- [ ] **Step 1: Add failing checker normalization/curvature tests**

Use small synthetic raw fit dictionaries to verify IEEE numeric decoding, free-index contract checking, and symmetric inverse-Hessian spectral diagnostics. The test must not run expensive fitting.

- [ ] **Step 2: Run focused tests and verify RED**

Expected: FAIL because checker functions are absent.

- [ ] **Step 3: Implement the MATLAB runner**

Preserve S7 fitting semantics exactly, change only the protocol ID/output namespace, and retain raw failures rather than aborting a shard.

- [ ] **Step 4: Implement the Python checker**

Use `fit_binary_variant(..., QuasiNewtonOptions(max_iter=100))`; capture all success/failure outputs. Compute HGFX inverse-Hessian diagnostics from the symmetrized final inverse-Hessian. Do not create acceptance cutoffs for curvature diagnostics.

- [ ] **Step 5: Verify focused tests GREEN**

Run: `python -m pytest tests/unit/test_m18c2_horizon_analysis.py -q`

- [ ] **Step 6: Commit**

`git commit -m "feat: add paired M18C.2 shard evaluation"`

### Task 4: Add complete-horizon aggregation and preregistered classification

**Files:**
- Create: `tools/aggregate_m18c2_horizon.py`
- Modify: `tests/unit/test_m18c2_horizon_analysis.py`

**Interfaces:**
- Consumes: directory containing 24 `*-comparison.json` files.
- Produces: aggregate JSON with coverage, per-model/per-horizon parameter summaries, scale diagnostics, per-horizon model confusion matrices/balanced accuracy, BIC winner agreement, curvature summaries, per-model classifications, and overall classification.

- [ ] **Step 1: Add failing aggregate tests with synthetic complete evidence**

Construct miniature synthetic rows through pure helper calls rather than 360 fits. Verify coverage constants (`24`, `144`, `72`), per-horizon summaries, no duplicate case IDs, winner mismatch handling, and final interpretation.

- [ ] **Step 2: Run tests and verify RED**

Expected: FAIL because aggregate helpers are absent.

- [ ] **Step 3: Implement aggregate calculations**

Reuse the S7 summary formulas exactly for bias/RMSE/correlation/standardized RMSE. Aggregate parameter criteria per model × horizon across both truth scales. Aggregate model recovery per horizon. Require exact complete coverage before interpretation.

- [ ] **Step 4: Implement preregistered classification**

Call Task 1 classification logic; never infer a scientific limitation if paired criterion outcomes or BIC winners disagree.

- [ ] **Step 5: Verify GREEN**

Run the focused unit suite, then `python -m pytest tests/unit/test_m18_scientific_validation.py tests/unit/test_m18c2_horizon_analysis.py -q`.

- [ ] **Step 6: Commit**

`git commit -m "feat: aggregate M18C.2 horizon evidence"`

### Task 5: Add CI smoke validation and full paired execution workflow

**Files:**
- Create: `.github/workflows/pv1-01-m18c2-horizon.yml`
- Create: `reference/validation/m18c2_trial_horizon/README.md`

**Interfaces:**
- Pull requests run only focused protocol/unit tests and a cheap manifest-generation smoke check.
- Full paired execution runs on `workflow_dispatch` or a push that changes `reference/validation/m18c2_trial_horizon/EXECUTE`.
- Full matrix contains exactly 24 shards: 3 models × 4 horizons × 2 scales, `max-parallel: 4`.

- [ ] **Step 1: Add workflow path and matrix tests to the focused unit file**

Parse the workflow as text and assert all four horizons/models/scales are represented, the full job is gated by the explicit trigger, and the aggregate job expects all shards.

- [ ] **Step 2: Verify RED**

Expected: FAIL because the workflow does not exist.

- [ ] **Step 3: Implement the workflow**

Mirror the proven S7 MATLAB setup/verification pattern. Each full shard must: verify reference freeze, generate immutable manifest, run MATLAB, run HGFX paired checker, and upload all three JSON artifacts. Aggregate must always download all shard artifacts, reject incomplete coverage, write the aggregate report, and upload it even when the scientific classification is not a PASS.

- [ ] **Step 4: Add evidence-directory README**

Document protocol ID, expected artifact names, exact execution trigger semantics, and the rule that raw failed evidence is retained.

- [ ] **Step 5: Verify GREEN on PR CI**

Run the focused test job and inspect the GitHub Actions run for the exact PR head SHA.

- [ ] **Step 6: Commit**

`git commit -m "ci: add M18C.2 paired horizon workflow"`

### Task 6: Execute the frozen experiment and close PV1-01 evidence

**Files:**
- Create after execution: `reference/validation/m18c2_trial_horizon/EXECUTE`
- Create from downloaded/verified evidence: `reference/validation/m18c2_trial_horizon/aggregate.json`
- Create: `docs/validation/M18C2_TRIAL_HORIZON_RESULT.md`
- Modify: `docs/planning/V1_TODO.md`
- Update: GitHub issue #21

**Interfaces:**
- Full workflow run is the execution oracle for this task.

- [ ] **Step 1: Commit the explicit execution trigger**

The trigger file records protocol ID, branch/head SHA, and a statement that the protocol is frozen before results.

- [ ] **Step 2: Inspect the full workflow**

Require all 24 shard jobs and aggregate job to complete. Failed fits are valid evidence; infrastructure/test failures are not.

- [ ] **Step 3: Retrieve and verify aggregate/raw artifacts**

Record workflow run ID, exact tested SHA, artifact IDs/names, and coverage counts. Do not omit failing scientific cases.

- [ ] **Step 4: Commit the aggregate evidence and result report**

The report must distinguish: implementation mismatch, optimizer mismatch, model-selection mismatch, data-horizon evidence, persistent weak/structural-identifiability evidence, and insufficient evidence. It must state that historical M18 remains FAIL regardless of the post-v1 result.

- [ ] **Step 5: Synchronize tracking**

Set PV1-01 to `DONE / RESEARCH COMPLETE` only if the required paired evidence package is complete. Otherwise leave it `IN PROGRESS` or `BLOCKED` with the exact missing evidence. Update issue #21 with the run ID, tested SHA, aggregate classification, and evidence paths.

- [ ] **Step 6: Run final regression/review checks**

Run focused tests plus the repository regression workflow on the final PR head. Confirm no frozen v1 evidence files were modified.

- [ ] **Step 7: Commit and merge only after CI evidence is green**

Record final commit SHA and workflow run IDs in the result report and issue.
