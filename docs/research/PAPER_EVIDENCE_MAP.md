# Paper Evidence Map

Last synchronized: 2026-09-14
Status: **LIVE / PRE-M19**

Final manuscript results remain provisional until M19. Historical failures and prospective FAIL outcomes must remain visible.

## Claim-to-evidence map

| Candidate claim | Status | Evidence / restriction |
|---|---|---|
| HGFX targets a Python replacement of MATLAB HGF Toolbox 8.2.0 | READY | product definition + frozen reference `2437f4dc...` |
| HGF/eHGF/uHGF forward behavior is reproduced | READY/PROVISIONAL | M4-M6; final aggregate rerun at M19 |
| Observation/objective parity exists | READY/PROVISIONAL | M7-M8 |
| MATLAB-compatible fitting is fully reproduced | **BLOCKED** | official run `34823572071` is 7/9; D02/D08 unresolved |
| Hessian/covariance/correlation/LME compatibility | PROVISIONAL | M10 historical scope; final workflow claim depends on fit closure |
| Simulation compatibility | READY/PROVISIONAL | M11/M12; D09 wrapper still open |
| Model/source coverage | READY/PROVISIONAL | M12 + final mapping audit |
| Compatibility API | READY/PROVISIONAL | M13 + S10 install/examples/docs |
| Physical GPU execution exists | READY for historical M14-M17 scope | final broad claim requires S9 applicability audit |
| Parameter recovery is strong/complete | **BLOCKED** | historical M18 FAIL; paired product recovery still required |
| Model selection is preserved | PROVISIONAL | D02 model-selection parity + future full candidate matrix |
| Exact 512 historical limitation matches MATLAB | READY for exact case only | no generalization |
| uHGF→AR(1) official workflow reproduced | READY | run `34763542557` |
| Endpoint sensitivity alone explains D08 generally | **REJECTED by prospective evidence** | one frozen D08 holdout seed passed and one failed inference-level requirements |
| Floating-point/optimizer path sensitivity can amplify tiny differences | PROVISIONAL case-study claim | D02 diagnostics + D08 failed holdout; do not claim compatibility solved |
| Final release has zero MATLAB runtime dependency | OPEN/PROVISIONAL | S10 acceptance required |

## Official workflow snapshot

Latest unchanged official gate: run `34823572071`, job `103910417693`, artifact `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`, **7/9 direct PASS**. D02_fit and D08_fit remain blockers.

## D08 paper-facing interpretation

The calibration case showed exact MATLAB-endpoint replay and a tiny endpoint difference that could amplify a derived trajectory quantity. A prospectively frozen test was then run rather than changing tolerance.

Prospective holdout run `34826235671`, job `103918945542`, artifact `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1`:

- seed 271828182: PASS;
- seed 314159265: `INFERENCE_EQUIVALENCE_FAIL`;
- same-endpoint replay still matched, but optimizer path/final/H/Sigma/Corr/predictions/residuals did not satisfy Level-2 requirements.

Paper consequence: **do not claim generic endpoint-sensitivity equivalence for D08.** The scientifically useful result is that exact shared-endpoint implementation can agree while optimizer-path sensitivity still produces material fitted-inference divergence for another frozen case. D08 remains unresolved.

## D02 paper-facing interpretation

D02 remains `INFERENCE_EQUIVALENCE_FAIL / BLOCKED`. Reference endpoint/initial-gradient/sampled-path objective/quasi-Newton algebra evidence shows substantial shared-state compatibility, but fitted inference diverges materially.

The preregistered 9-point same-vector basin classifier is awaiting corrected CI execution. First run `34827198731` was a harness failure from NaN-unsafe checking; scientific protocol was not changed. Commit `942ca86...` fixes only the harness. Corrected run `34829122057` is queued.

Paper consequence: tiny upstream numerical differences are a plausible amplification mechanism, but the paper may not call D02 solved until inference compatibility is evidence-backed.

## Historical GPU evidence

Recorded shared/contended H100 scaling snapshot remains eligible only in its tested scope: 1 GPU median 81.719055 s; 2 GPU 73.838342 s; 4 GPU 58.860710 s, corresponding speedups 1.000, 1.107, 1.388. Final headline performance claims require S9/M19 applicability freeze.

## Before M19

Close D02/D08; D09-D12; paired parameter/model recovery; robustness/backend applicability; aggregate evidence; clean install/examples/docs/no-MATLAB-runtime. At M19 freeze exact code/reference SHAs, datasets/configs/seeds/protocols, machine-readable outputs, run/job/artifact/hash provenance and table/figure regeneration scripts.