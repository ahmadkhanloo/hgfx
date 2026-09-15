# Paper Evidence Map

Last synchronized: 2026-09-14
Status: **LIVE / PRE-M19**

Final manuscript results remain provisional until M19. Historical failures and prospective FAIL outcomes must remain visible.

## Claim-to-evidence map

| Candidate claim | Status | Evidence / restriction |
|---|---|---|
| HGFX targets a Python replacement of MATLAB HGF Toolbox 8.2.0 | READY | product definition + frozen reference `2437f4dc...` |
| HGF/eHGF/uHGF forward behavior is reproduced | READY/PROVISIONAL | M4-M6; final aggregate rerun at M19 |
| Observation/objective parity exists | READY/PROVISIONAL | M7-M8; D02 shared-vector/reference evidence |
| MATLAB-compatible fitting is fully reproduced | **BLOCKED** | D08 remains unresolved; D02 is an exact-scope reference limitation, not direct fit parity |
| Hessian/covariance/correlation/LME compatibility | PROVISIONAL | M10 historical scope; D02 limitation disclosed; D08 open |
| Simulation compatibility | READY/PROVISIONAL | M11/M12; D09 wrapper still open |
| Model/source coverage | READY/PROVISIONAL | M12 + final mapping audit |
| Compatibility API | READY/PROVISIONAL | M13 + S10 install/examples/docs |
| Physical GPU execution exists | READY for historical M14-M17 scope | final broad claim requires S9 applicability audit |
| Parameter recovery is strong/complete | **BLOCKED** | historical M18 FAIL; paired product recovery still required |
| Model selection is preserved | PROVISIONAL | D02 model-selection parity + future full candidate matrix |
| Exact 512 historical limitation matches MATLAB | READY for exact case only | no generalization |
| Exact official D02 optimizer/basin limitation is present in MATLAB itself | READY for exact case only | self-sensitivity run `34837033370`; 6/6 +/- one-spacing starts materially change endpoint |
| uHGF→AR(1) official workflow reproduced | READY | run `34763542557` |
| Endpoint sensitivity alone explains D08 generally | **REJECTED by prospective evidence** | one frozen D08 holdout seed passed and one failed inference-level requirements |
| Floating-point/optimizer path sensitivity can amplify tiny differences | **READY as D02 exact-case study / PROVISIONAL generally** | D02 shared-vector/source/self-sensitivity evidence; do not generalize beyond tested scope |
| Final release has zero MATLAB runtime dependency | OPEN/PROVISIONAL | S10 acceptance required |

## D02 paper-facing interpretation

D02 is now a strong numerical reproducibility case study, while its direct failure remains visible. The exact objective/forward contract agrees at shared states, the first localized off-centre likelihood residual is binary64-scale, and the frozen MATLAB reference is itself highly start-sensitive: changing one free start coordinate by only `4.440892098500626e-16` sends all six diagnostic reruns outside the existing endpoint gate, with shifts up to ~`1.5077`.

Paper consequence: it is defensible to report the exact D02 workflow as `REFERENCE_LIMITATION_MATCH`, not as direct or inferential parity. The scientific claim must be scope-limited: finite-difference quasi-Newton fitting on this exact case is numerically basin-sensitive in the MATLAB oracle itself.

## D08 paper-facing interpretation

The prospective Level-2 holdout remains failed. Same-endpoint/shared-state evidence can agree while the actual optimizer path produces material fitted-inference divergence on seed `314159265`. The USDCHF prior-input discrepancy has been repaired and now compares exactly, but the hard seed still fails. Do not claim generic D08 endpoint-sensitivity equivalence.

## Historical GPU evidence

Recorded shared/contended H100 scaling snapshot remains eligible only in its tested scope: 1 GPU median 81.719055 s; 2 GPU 73.838342 s; 4 GPU 58.860710 s, corresponding speedups 1.000, 1.107, 1.388. Final headline performance claims require S9/M19 applicability freeze.

## Before M19

Resolve D08; close D09-D12; paired parameter/model recovery; robustness/backend applicability; aggregate evidence; clean install/examples/docs/no-MATLAB-runtime. At M19 freeze exact code/reference SHAs, datasets/configs/seeds/protocols, machine-readable outputs, run/job/artifact/hash provenance and table/figure regeneration scripts.
