# Paper Evidence Map

Last synchronized: 2026-09-13
Status: **LIVE / PRE-M19**

Purpose: map every candidate manuscript claim to repository evidence. This file is paper-facing continuity, not a replacement for raw artifacts or milestone gate documents.

Status vocabulary:
- **READY:** evidence is currently sufficient for a narrowly worded claim.
- **PROVISIONAL:** useful evidence exists but final v1/M19 closure can still change the manuscript wording.
- **BLOCKED:** a required gate remains unresolved.
- **OPEN:** evidence has not yet been produced/frozen for the paper.

## Evidence-source priority

For any claim, use:
1. frozen reference and current product/release definitions;
2. gate/validation documents;
3. machine-readable raw outputs and paired MATLAB/HGFX artifacts;
4. CI run/job/artifact provenance;
5. generated paper tables/figures after M19.

Never source a numerical claim only from chat text.

## Claim-to-evidence matrix

| Candidate paper claim | Status | Primary evidence | Required before final manuscript |
|---|---|---|---|
| HGFX targets a Python replacement of MATLAB HGF Toolbox 8.2.0 | READY | `docs/planning/V1_PRODUCT_DEFINITION.md`; frozen reference files | Keep exact reference SHA in Methods |
| Frozen MATLAB oracle is reproducible | READY | M0/reference freeze; `reference/REFERENCE_FREEZE.md`; `scripts/verify_reference_freeze.py` | M19 provenance index should include reference manifest/hash |
| Parameter/config semantics are reproduced | READY/PROVISIONAL | M2 gate and golden tests; M12 config coverage | Aggregate final evidence index |
| Scalar CPU float64 numerics match calibrated MATLAB reference | READY/PROVISIONAL | M3 gate/workflow | Confirm final code still passes at M19 |
| HGF forward trajectory parity | READY/PROVISIONAL | M4 | Final aggregate rerun |
| eHGF forward trajectory parity | READY/PROVISIONAL | M5 | Final aggregate rerun; D02 fitting sensitivity does not invalidate fixed-path M5 evidence |
| uHGF forward trajectory parity | READY/PROVISIONAL | M6 | Final aggregate rerun |
| Observation likelihood parity | READY/PROVISIONAL | M7 | Final aggregate rerun |
| Fixed-parameter objective parity | READY/PROVISIONAL | M8 | Final aggregate rerun |
| MATLAB-compatible fitting behavior is reproduced broadly | BLOCKED | M9 plus M18 official workflow closure | D02_fit and D08_fit must close under unchanged gate or valid matched reference classification |
| Hessian/covariance/correlation/AIC/BIC/LME compatibility | READY/PROVISIONAL at historical gate; final product claim depends on fit closure | M10; M18 workflow outputs | Revalidate on final required workflow surface |
| Simulation behavior is reproduced | READY/PROVISIONAL | M11 | Close remaining required demo/workflow wrappers such as D09 |
| Frozen MATLAB model/source coverage is represented | READY/PROVISIONAL | M12 coverage/config/model-family gates | Final source-to-workflow mapping and release audit |
| Downstream compatibility API exists | READY/PROVISIONAL | M13 | Clean-install/examples/docs acceptance at S10 |
| HGFX has physical-GPU execution evidence | READY for historical M14–M17 scope | M14–M17 gate docs; H100 evidence docs | M18 S9 applicability audit before broad paper claim |
| CPU/GPU scientific agreement holds on required final v1 surface | OPEN/PROVISIONAL | M14–M16 historical evidence | M18 S9 final compatibility/backend matrix |
| Batch execution preserves repeated-single-fit results | READY/PROVISIONAL | M16 | Final applicability audit |
| Multi-GPU execution scales on tested H100 workload | READY for the recorded workload only | M17 H100 evidence | Do not generalize beyond tested workload; include contention caveat |
| HGFX shows strong/complete parameter recovery | BLOCKED | historical M18 FAIL; M18A/M18B diagnosis | Product-level paired MATLAB/HGFX recovery in M18 S7/S8; historical FAIL remains visible |
| HGFX preserves model recovery/model selection | PROVISIONAL | D02 model-selection parity; M18 future paired recovery | Full candidate-set paired model-recovery matrix |
| Exact 512-trial historical limitation matches MATLAB | READY for exact case only | M18 512 paired reference classification | Wording must remain case-specific; no general 512-trial claim |
| Official uHGF→AR(1) demo/workflow is reproduced | READY | D04 run `34763542557` at `faf97bf...` | Include final aggregate provenance if used in paper |
| Official fit/Bayes workflow set is fully reproduced | BLOCKED | run `34776952053`, job `103776700085`; artifact `10323968264` | Current result 7/9; D02/D08 unresolved |
| Cross-runtime elementary floating-point differences can affect fitting paths | PROVISIONAL case-study claim | D02 regression/diagnostic commits and run `34776952053` | Close D02 and preserve exact before/after evidence; determine whether it belongs in main paper or supplement |
| HGFX final release requires no MATLAB runtime | OPEN/PROVISIONAL | product definition/S10 plan | Clean-install/full-example/no-MATLAB-runtime release acceptance |

## Current M18 workflow evidence snapshot

Latest diagnostic/official closure evidence:
- HGFX diagnostic head: `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`;
- run: `34776952053`;
- job: `103776700085`;
- artifact: `m18-official-workflows`, ID `10323968264`;
- artifact SHA-256: `ac4d0094cfe49b5e5ee8d5c75f89311c35a2727b46ed433078412be63c3b5f9c`;
- frozen MATLAB reference verification: PASS;
- targeted M18 regression/API tests: 7 passed;
- official nine-case closure: **7/9 PASS**;
- blockers: `D02_fit`, `D08_fit`.

Passing cases:
- `D01_bayes`;
- `D01_fit`;
- `D03_fit`;
- `D05_fit`;
- `D06_bayes`;
- `D06_fit`;
- `D07_fit`.

### D02 paper-facing interpretation — PROVISIONAL

Current classification at official gate: `OPTIMIZER_MISMATCH`.

Evidence chain:
- MATLAB reference-point evaluation: PASS;
- initial Ridders comparison: PASS at existing acceptance criteria;
- objective replay along MATLAB optimizer path: PASS;
- prior decomposition at selected Ridders samples: exact;
- regression-first evidence identified MATLAB-vs-default-runtime `exp` differences and a MATLAB-compatible repair was added;
- after that repair, the selected residual probe in run `34776952053` is classified `FORWARD_NUMERICAL_DIVERGENCE`;
- selected residual `inf_states` max absolute difference: `7.105427357601002e-15`;
- selected observation input max absolute difference: `1.1102230246251565e-16`;
- selected per-trial log-likelihood difference: `2.4868995751603507e-14`;
- replayed observation log-likelihood on exact MATLAB state: zero difference.

Paper implication: the current evidence supports a statement that tiny upstream floating-point differences can be amplified by finite-difference/optimization paths. It does **not** yet support a claim that D02 compatibility is solved.

### D08 paper-facing interpretation — PROVISIONAL/BLOCKED

Current official mismatch is limited to `fit.traj.epsi` near index `(178,1)`:
- HGFX in run `34776952053`: approximately `-4.7887561410406825`;
- MATLAB: approximately `-4.788757533201755`.

Reference point PASS, initial Ridders PASS, optimizer trace PASS and MATLAB-path objective replay PASS (50 points). Final classification remains `OPTIMIZER_MISMATCH` until the endpoint/state source of the discrepancy is resolved.

## Historical GPU evidence eligible for later paper audit

M17 shared H100 scaling snapshot:

| GPUs | Median s | Subjects/s | Fits/s | Speedup | Efficiency |
|---:|---:|---:|---:|---:|---:|
| 1 | 81.719055 | 0.783 | 1.566 | 1.000 | 1.000 |
| 2 | 73.838342 | 0.867 | 1.734 | 1.107 | 0.553 |
| 4 | 58.860710 | 1.087 | 2.175 | 1.388 | 0.347 |

Do not present these values as final v1 benchmark headline numbers until S9/M19 confirms applicability to the final validated implementation and freezes the benchmark protocol.

## Final paper deliverables still OPEN

Before M19:
- close D02/D08 official workflow blockers;
- complete remaining required D09–D12 demo/analysis surfaces;
- execute paired product-level parameter recovery;
- execute paired model recovery/model-selection matrix;
- close robustness/backend applicability matrix;
- create aggregate evidence checker/report;
- complete clean-install/examples/docs/no-MATLAB-runtime release acceptance.

At M19:
- freeze exact HGFX code version;
- freeze datasets/configs/seeds/protocol hashes;
- freeze machine-readable result set;
- freeze figure/table generation scripts;
- record run/job/artifact IDs and SHA-256 hashes;
- generate the manuscript result tables/figures only from the frozen evidence.

## Maintenance rule

Whenever a paper-relevant gate changes state, update this file and `RESEARCH_LOG.md` in the same or immediately following documentation commit. Do not mark a claim READY because implementation exists; READY requires evidence satisfying the documented gate.
