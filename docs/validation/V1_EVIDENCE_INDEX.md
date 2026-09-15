# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-15
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Release branch: `migration/m18-workflow-closure`

This index preserves historical failures and distinguishes direct PASS, scoped reference limitations, physical-GPU applicability, frozen release evidence, fresh candidate validation, and the final candidate gate.

## M18/v1 closure evidence

| Surface | Classification | Evidence |
|---|---|---|
| M0-M17 | PASS_IN_DOCUMENTED_SCOPES | milestone evidence |
| Historical M18 scientific experiment | FAIL_PRESERVED | historical evidence |
| D02 exact official scope | REFERENCE_LIMITATION_MATCH | decision JSON |
| D08 exact failed seed | REFERENCE_LIMITATION_MATCH | decision JSON |
| D04 uHGF -> AR1 | PASS | historical run `34763542557`; fresh candidate workflow set green at `5cf17dcd...` |
| D09 sampleModel | PASS | historical run `34842943557`; fresh run `34984783710` |
| D10/D11 analysis surfaces | PASS | historical run `34847266268`; fresh run `34984783669` |
| D12 BPA | PASS | historical run `34854238549`; fresh run `34984783649` |
| S7 paired parameter recovery | REFERENCE_LIMITATION_MATCH | historical run `34896442847`; fresh run `34984783703`, aggregate artifact `10404477458`, SHA-256 `e62982fa32f61d66d3f8643d95354962944e969bc72868a3326cd816377203a2` |
| S7 paired model selection | PASS_PAIRED_MODEL_SELECTION | fresh 36/36 BIC winners match |
| S8 required repair scope | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU robustness/backend | PASS_CPU_BACKEND_EQUIVALENCE | historical run `34901924475`; fresh S9 run `34984783685` PASS |
| S9 physical GPU | PASS_PHYSICAL_GPU_APPLICABILITY | source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`; 2x Tesla T4; repository record `7179484ce782c25d6edde34cc56a0d689831e1cc`; raw JSON SHA-256 `6cd35c82be1e542830c06f6b7b7e444fda0ff4fe93773f080e6c13725212dfdf` |
| S10 release readiness | PASS | historical run `34934079865`; fresh run `34984783640`, wheel artifact `10402688684`, SHA-256 `b65de6e4ba20a5637935f32010d8a150e7731b113a77ae9256c1f688697b118b` |
| M19/M20 preflight | PASS_PREFLIGHT | fresh run `34984783642`, artifact `10403445860`, SHA-256 `fdfd1e2a73df597a54b72d929191ca0d11e2eeb5ef8ed56bdb49327229d4b2eb` |
| M19 evidence freeze | PASS_FROZEN | run `34966661492`; manifest commit `b71301b978e07cb0fa5ac2ad14cc92235fadc5ee`; `status=FROZEN`, `failures=[]` |
| Fresh CPU regression | PASS | run `34984783677`; 171 passed, 4 physical-GPU skips, 5 warnings |
| M20 candidate | FINALIZER_PENDING | fresh candidate CI green at `5cf17dcd13c9f30dbfcd500ad409d39d41296b20`; synchronized revision finalizer pending |

## Fresh S7 interpretation

Fresh S7 run `34984783703` re-executed the complete frozen grid. The raw aggregate remains scientifically failing where the MATLAB oracle fails: raw `gate_pass=false`, raw `scientific_pass=false`, and raw classification `REFERENCE_LIMITATION_REVIEW_REQUIRED`. The separate frozen decision classifies the exact same protocol scope as `REFERENCE_LIMITATION_MATCH`, yielding `release_gate_pass=true` without changing the scientific result.

Coverage remains 12/12 shards, 72/72 parameter-recovery cases and 36/36 model-recovery datasets. All 36 BIC winners match MATLAB. No threshold, seed, dataset, start, optimizer or validation grid was changed.

## Physical-GPU result

`M18_S9_PHYSICAL_GPU_AMENDMENT.md` was frozen before the repaired-path physical run. The uploaded evidence satisfies the unchanged S9 gate: JAX backend `gpu`, actual device residency, four required CPU-vs-GPU fitting cells passing the `<= 1e-7` final-objective criterion, and recorded source/hardware/runtime/command/environment provenance. Maximum observed CPU-vs-GPU final-objective gap is `1.4210854715202004e-14`.

The run used 2x Tesla T4 under a hosted/shared Kaggle environment. This establishes numerical backend applicability for the tested NVIDIA/JAX/CUDA path; it does not establish uncontended performance/scaling or H100-specific performance.

## M19/M20 state

The committed M19 manifest remains historical frozen evidence. Fresh candidate validation on `5cf17dcd13c9f30dbfcd500ad409d39d41296b20` is green, and this synchronization revision updates release documents and machine-readable evidence to reference those fresh runs.

M20 remains the only candidate blocker until `m20-finalize.yml` builds a candidate-synchronized manifest and `scripts/check_m20_candidate.py --mode finalize` returns `PASS_M20_CANDIDATE` on this synchronized revision.

## Candidate versus final release

M20 is the `1.0.0rc1` candidate gate. After M20 PASS, PR #26 may be made ready/merged and the RC tag may be created. Promotion from RC to final `1.0.0` still follows `CHAT_WORKFLOW.md`: freeze the candidate, obtain an independent review against `FINAL_REVIEW_CHECKLIST.md`, resolve all Critical/High findings, and rerun full validation.

## Active release blockers

1. M20 v1.0 candidate finalization on the synchronized release-document revision.

## Integrity rules

- Historical FAIL remains FAIL.
- `REFERENCE_LIMITATION_MATCH` is scope-limited product-equivalence evidence, not scientific PASS.
- `PASS_FROZEN` means the M19 release evidence package passed the committed manifest gate.
- `PASS_PREFLIGHT` is not final milestone PASS.
- No post-hoc threshold/seed/dataset/start/grid/model/optimizer changes may obtain PASS.
