# M20 — v1.0 Candidate

Last synchronized: 2026-09-15
Status: **FRESH CANDIDATE CI PASS — FINALIZER PENDING ON SYNCHRONIZED REVISION**
Branch: `migration/m18-workflow-closure`

## Purpose

M20 is the final v1.0 release-candidate gate. It does not reopen scientific validation. It verifies that the accepted MATLAB-equivalence surface, packaging, provenance, metadata and M19 evidence freeze are internally consistent and ready to merge/tag as the `1.0.0rc1` candidate.

Final `1.0.0` promotion remains subject to the independent final-review process in `CHAT_WORKFLOW.md`; M20 PASS must not be described as an independent-review PASS.

## Preconditions for M20 PASS

- [x] M19 evidence manifest is committed with status `FROZEN`.
- [x] S9 physical NVIDIA GPU applicability is PASS on the current numerical path under `M18_S9_PHYSICAL_GPU_AMENDMENT.md`.
- [x] S10 release-readiness remains PASS.
- [x] `reference/validation/v1_release/evidence_index.json` has no unresolved blocker other than the M20 candidate gate itself.
- [x] Package/citation metadata are promoted to release-candidate quality and remain mutually consistent.
- [x] PR/release documents preserve historical FAIL and scoped `REFERENCE_LIMITATION_MATCH` evidence.
- [x] Fresh candidate CI on `5cf17dcd13c9f30dbfcd500ad409d39d41296b20` is green across all 10 active PR workflows.
- [x] Fresh S7 paired recovery preserves `scientific_pass=false` while applying the frozen exact-scope `REFERENCE_LIMITATION_MATCH` decision for release accounting.
- [ ] `scripts/check_m20_candidate.py --mode finalize` returns `PASS_M20_CANDIDATE` on the synchronized release-document revision.

## Fresh candidate evidence — 2026-09-15

Source candidate revision: `5cf17dcd13c9f30dbfcd500ad409d39d41296b20`.

All 10 active pull-request workflows completed successfully:

- HGFX Regression `34984783677`: **171 passed, 4 physical-GPU skips, 5 warnings**.
- S10 v1 Release Readiness `34984783640`: PASS; wheel artifact `10402688684`, SHA-256 `b65de6e4ba20a5637935f32010d8a150e7731b113a77ae9256c1f688697b118b`.
- M19 M20 Release Preflight `34984783642`: PASS; artifact `10403445860`, SHA-256 `fdfd1e2a73df597a54b72d929191ca0d11e2eeb5ef8ed56bdb49327229d4b2eb`.
- M18 S7 Paired Recovery `34984783703`: PASS; aggregate artifact `10404477458`, SHA-256 `e62982fa32f61d66d3f8643d95354962944e969bc72868a3326cd816377203a2`.
- M18 S9 Backend Robustness `34984783685`: PASS.
- M18 D09 Official sampleModel `34984783710`: PASS.
- M18 D10 D11 Analysis Surfaces `34984783669`: PASS.
- M18 D12 Bayesian Parameter Averaging `34984783649`: PASS.
- M18 Demo Model Selection Parity `34984783651`: PASS.
- M18 Demo uHGF AR1 Workflow Parity `34984783696`: PASS.

The fresh S7 artifact contains:
- raw `gate_pass=false`;
- raw `scientific_pass=false`;
- raw classification `REFERENCE_LIMITATION_REVIEW_REQUIRED`;
- release classification `REFERENCE_LIMITATION_MATCH`;
- `release_gate_pass=true`;
- complete coverage: 12 shards, 72 parameter-recovery cases, 36 model-recovery datasets, 36/36 BIC winner matches.

Therefore the historical/scientific limitation remains disclosed and is not rewritten as scientific PASS.

## Candidate checker

`scripts/check_m20_candidate.py` supports:

- `preflight`: validates candidate prerequisites available before final closure;
- `finalize`: requires a candidate-synchronized M19 `FROZEN` manifest, valid physical NVIDIA GPU release accounting, release-candidate/final version metadata, and no earlier active blockers.

The next revision intentionally synchronizes release documents and machine-readable evidence with the fresh candidate CI. The `m20-finalize.yml` push gate must then succeed on that exact synchronized revision before M20 is marked PASS.

## Definition of done

M20 becomes **PASS** only when:

1. the synchronized release-document revision is committed;
2. its M20 finalizer returns `PASS_M20_CANDIDATE`;
3. required fresh CI for that revision has no release-blocking failure;
4. the repository records the final candidate evidence without rewriting historical failures.

After M20 PASS, PR #26 may be made ready and merged and the `1.0.0rc1` candidate may be tagged. Final `1.0.0` promotion still follows the independent-review process in `CHAT_WORKFLOW.md`.

## Integrity

No numerical code, tolerance, seed, dataset, start, validation grid, model family, optimizer, or physical-GPU acceptance criterion was changed to obtain the fresh PASS. The S7 CI change only connects the pre-existing frozen exact-scope reference-limitation decision to release accounting.
