# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Objective

Deliver HGFX v1.0 as a functional/scientific Python replacement for MATLAB HGF Toolbox 8.2.0, with no MATLAB runtime dependency for users. Compatibility is judged under the frozen tiered policy in `../validation/MATLAB_EQUIVALENCE_POLICY.md`; it is not bitwise identity and it is not permission for post-hoc threshold/seed/grid changes.

## Current baseline

| Item | Status | Evidence |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | immutable historical gate |
| M0-M17 | PASS in documented scopes | gate documents/evidence |
| D02 model selection | PASS_MODEL_SELECTION_PARITY | exact paired MATLAB/HGFX behavior |
| D04 uHGF→AR(1) | PASS | run `34763542557` |
| Historical 512 case | REFERENCE_LIMITATION_MATCH | exact case only |
| Official fit/Bayes closure | 7/9 direct PASS / OPEN | run `34823572071`, job `103910417693` |
| D08 prospective Level-2 holdout | **FAIL / BLOCKED** | run `34826235671`, one of two frozen seeds failed |
| D02 inferential equivalence | **FAIL / BLOCKED** | endpoint/statistical outputs differ materially |
| v1 release | OPEN | issue #24 |

Official artifact: `m18-official-workflows`, ID `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.

## Frozen equivalence semantics

1. Exact contract equality: reference/data/model/config/parameter ordering/fixed-free mask/transforms/starts/drivers.
2. Scale-aware numerical equivalence: existing `atol + rtol*|reference|` field tolerances; no decimal-place-only rule.
3. Endpoint-sensitivity equivalence: only under a prospectively frozen protocol; D08's first prospective Level-2 protocol has now failed and may not be rewritten.
4. Inferential equivalence: separately preregistered fit/parameter/uncertainty/prediction/model-evidence criteria when appropriate.

Historical failures remain historical failures even if later evidence supports a different accepted-equivalence classification.

## Ordered work packages

| Step | Status | Exit condition |
|---|---|---|
| S1 policy/semantics | DONE | tiered equivalence + reference-limit policies frozen |
| S2 D04 official workflow | PASS | exact workflow validated |
| S3 remaining workflow contracts | IN PROGRESS | D09-D12/source-output mapping frozen |
| S4 binary demos | IN PROGRESS | D02 still blocking; D01/D03/D05 healthy |
| S5 continuous demos | IN PROGRESS | D08 blocked after failed prospective holdout; D06/D07 healthy |
| S6 analysis/output surfaces | OPEN/TODO | D10-D12 closed |
| S7 paired recovery | OPEN/TODO | paired MATLAB/HGFX parameter/model recovery completed |
| S8 evidence-backed repairs | IN PROGRESS | no required unresolved implementation/optimizer/model-selection mismatch |
| S9 robustness/backend | OPEN/TODO | robustness + CPU/JAX/physical-GPU applicability matrix closed |
| S10 release acceptance | OPEN/TODO | aggregate evidence, install/docs/examples/licenses/no-MATLAB-runtime complete |

## D08 — failed prospective Level-2 experiment

The original D08 calibration showed exact replay at the MATLAB endpoint, motivating a prospective endpoint-sensitivity test. The test was frozen before execution with seeds `271828182` and `314159265`.

Run `34826235671`, job `103918945542`, artifact `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1` produced:

- seed 271828182: PASS;
- seed 314159265: `INFERENCE_EQUIVALENCE_FAIL`;
- exact MATLAB-endpoint replay: no mismatch;
- fitted optimizer path diverges and final/H/Sigma/Corr/yhat/res/resAC exceed the Level-2 requirements.

Decision: **D08 remains BLOCKED.** The prospective protocol is immutable and cannot be rescued by replacing the seed or widening tolerance.

Next diagnostic `m18-d08-holdout-optimizer-probe-1` is frozen only to localize the failed seed. It compares full optimizer traces and objective/gradient/inverse-Hessian behavior at exact MATLAB rows 38-44 around the first observed path split. It has no acceptance effect. Current queued run: `34829121895`.

Decision tree after diagnostic:

- shared-state objective/gradient diverges => localize implementation/numerical primitive and add regression before repair;
- shared-state objective/gradient passes while path diverges => focus on finite-difference/optimizer state/conditioning/termination sensitivity;
- insufficient evidence => version a new diagnostic while preserving this result.

## D02 — inference blocker

D02 has same-reference endpoint/objective evidence at important sampled states, but materially different fitted endpoint and statistical inference outputs. It remains **INFERENCE_EQUIVALENCE_FAIL / BLOCKED**.

Frozen `m18-d02-basin-probe-1` evaluates both implementations at the same 9 transformed vectors between their fitted endpoints using unchanged M18 tolerance `rtol=3e-8`, `atol=3e-10`.

First run `34827198731` was a harness execution failure because structural `NaN` fixed slots were compared with non-NaN-aware equality. Commit `942ca86eea1fe52e8326c14f8fe175a5faa3db84` fixes only this harness defect using `equal_nan=True` and interpolating only free coordinates. The frozen scientific grid and rules are unchanged. Corrected run `34829122057` is queued at this synchronization.

Classifier meaning:

- `SAME_VECTOR_IMPLEMENTATION_MISMATCH`: localize exact shared-vector implementation difference first;
- `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`: same-vector objectives pass, so investigate path/conditioning/gradient amplification/termination;
- neither result is PASS.

## Anti-endless-patching rule

Do not chase a floating-point micro-difference merely because it exists. Repair it only when frozen evidence links it to required workflow/scientific inference. D08's failed holdout shows that broader optimizer-path behavior matters; D02's material inference disagreement requires a real explanation rather than a tolerance exception.

## After D02/D08

Proceed in order: D09-D12 → paired recovery → evidence-backed repairs → robustness/backend applicability → aggregate evidence/release checks → M19 evidence freeze → M20 v1 candidate.

## Evidence contract

Every required result records reference/HGFX SHA, protocol version, data/config/seed/start, environment, command, raw outputs/failures, tolerances, classification, run/job/artifact IDs and artifact SHA-256. GPU claims additionally require physical device/runtime evidence.

## Release interpretation

M18/v1 remains OPEN until every required surface is evidence-backed under frozen policies and there is no unresolved required HGFX-only implementation/optimizer/model-selection mismatch. `REFERENCE_LIMITATION_MATCH` requires exact paired MATLAB evidence. Failed prospective experiments remain visible.