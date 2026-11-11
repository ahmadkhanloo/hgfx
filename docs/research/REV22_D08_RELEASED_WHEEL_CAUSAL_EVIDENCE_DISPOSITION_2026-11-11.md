# REV-2.2 D08 — released-Wheel optimizer first-cause evidence disposition (2026-11-11)

**Scope:** documentation-only, read-only scientific evidence sufficiency judgment by a project AI agent. This is **not** an independent human scientific countersignature, not a new fit, not a new accepted numerical tolerance, and not a completion of REV-2.2. **Disposition:** `FIRST_NEW_RELEASED_WHEEL_BFGS_CAUSE_NOT_IDENTIFIABLE_FROM_CURRENTLY_REVIEWED_ARCHIVES`. This describes *missing causal trace evidence*, **not** structural/model non-identifiability or a demonstrated reference limitation.

## Frozen context

- Author objective D1=A: target *Computational Statistics*, PR #107 remains Draft; issue #111 remains open.
- Original official D08 `uhgf + gaussian_obs`: 614 public inputs, synthetic response seed `123456789`, frozen MATLAB HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`, released HGFX 1.0.0 Wheel SHA-256 `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`.
- Two *concurrent*, not preregistered-as-replicates, original scientific actions [A 42910756224](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910756224), [B 42910835710](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910835710) violated the one-run execution budget, before either result was observed. Both original outputs are retained.
- Own-endpoint direct gate: A has `traj.epsi` 4/1228 out-of-gate finite entries at trials 178, 322, 412, 577; B has 3/1228 at 178, 412, 577 (zero-based, level 1). Both are **FAIL**, despite 24/25 direct fields within existing criteria.
- In existing archived *same-vector* re-evaluations (MATLAB evaluated at the HGFX endpoint), all 12 trajectory fields fall within the *older descriptive yardstick*, but this is **not** a preregistered uHGF-family parity gate or own-fit equivalence proof. See [three-archive audit](REV22_D08_HISTORICAL_BFGS_SAME_VECTOR_AUDIT_2026-11-11.md).

## Evidence applicability matrix

| Evidence | Valid source and scope | What it does **not** establish |
| --- | --- | --- |
| Current original released-Wheel Run A/B artifacts | Same fixed official seed, frozen MATLAB, actual v1.0.0 Wheel; own-endpoint failures and same-vector evaluations | HGFX released-Wheel per-iteration `iter.x`, `iter.val`, `iter.invH`, complete Ridders probes and accepted Armijo decisions were **not exported**; cannot locate the first *new* solver decision |
| Historical official-seed M18 artifact 10339403480 | Same 614 binary64 inputs and synthetic responses, MATLAB source/fit trace; first historical *bitwise* optimizer x difference (row 3, free index 0), `3.552713678800501e-15`, with no old gate-level x failure | That historical bitwise observation is not a first causally material decision in **new** A/B runs |
| Historical official-seed Ridders 10345886333 and Armijo 10345846351 | Selected Ridders row 2/free index 0: 22/22 exact objective probes; selected Armijo row 2→3: 17/17 exact candidates and same selected `j=2` in four variants | Full 7-parameter/101-row solver trace, or exact released-Wheel probe parity |
| Historical official-seed MATLAB start-ULP 10346050821 | 0/14 starts materially outside frozen diagnostic threshold **for seed 123456789** | Universal optimizer stability or proof that the new A/B tiny endpoint difference has a known cause |
| Historical holdout seed 314159265 | Same 614 public USDCHF *inputs* but **different simulated responses** | Its row-38 Ridders/Armijo split and 13/14 material ULP-start outcomes **cannot** be transferred to official seed 123456789 |
| Historical editable Git source `d360fcd45c996c21ab482d1cd6b45dea6d65574f` versus release source `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` | Same Git blobs for `optim/ridders.py`, `optim/compat_quasinewton.py`, `models/uhgf.py`; different blobs for `models/hgf.py`, `models/_forward_common.py`, `math/matlab_exp.py` | Identical optimizer algorithm does **not** imply identical forward objective evaluation, finite-difference stencil outputs or solver branch choices |

The independently performed pinned-ref six-file Git blob spot-check is documented in [issue #111 comment 6795790307](https://github.com/ahmadkhanloo/hgfx/issues/111#issuecomment-6795790307). This confirms those six file identities, **not** a full new repository audit, a byte-level verification of all downloaded scientific artifacts in this review, or new MATLAB/HGFX executions. The historical source/archive hash and numeric audits are separately preserved in [official-seed archive report](REV22_OFFICIAL_D08_RIDDERS_ARMIJO_SOURCE_AUDIT_2026-11-11.md) and [source lineage report](REV22_OFFICIAL_D08_HISTORICAL_TO_RELEASE_SOURCE_LINEAGE_2026-11-11.md).

## Bounded causal conclusion

1. Direct own-fitted-trajectory **FAIL** is real and must remain in the paper evidence; small endpoint gaps are not a basis for discarding failures or increasing tolerances.
2. Existing same-vector forward agreement is consistent with endpoint/optimizer-path sensitivity; it does **not** establish which optimizer numerical operation, finite-difference sample, stopping condition, reduction order or floating-point runtime property first caused A/B divergence.
3. The historical selected-state source diagnostics cannot bridge the missing released-v1.0.0 iterative trace because the forward numerical path differs between editable historical code and release. Neither an *implementation mismatch* nor an *optimizer/numerical mismatch* is definitively localized at the first **new** released-Wheel optimizer decision; *model-selection mismatch*, *scientific/model limitation* and *structural identifiability* are **not demonstrated** by this evidence.
4. Label only this *causal localization subquestion* as `DOCUMENTED_EVIDENCE_LIMITATION`; keep the overall `REV-2.2=IN_PROGRESS / UNRESOLVED_DISCREPANCY`, `REV-2.4=NOT_GLOBAL_PASS`, historical M18/P3/63-of-64/PERF-01C findings unchanged, full CPU `NOT_PASS`, and D2/D3 `BLOCKED`.
5. The currently reviewed archives are insufficient to locate a first causal decision in **new** A/B fits. This does not prove no other archive exists; any additional genuine original, same-seed, same-release trace must be hash-verified and reviewed without rerunning numeric science.

## Next authorized work / no adaptive execution

- Independent human reviewer may review this evidence-boundary disposition, verify any additional pre-existing *released-Wheel* trace evidence, and sign a separately attributed opinion. Do **not** call this AI judgment human independent validation.
- If no such trace exists, keep the first-cause limitation explicitly unresolved and use the archived original direct failure in the manuscript. A future *new* experiment requires separate prospective protocol, source/version/hardware/seed/thread and optimizer trace controls, reviewer examination, author authorization and an entirely new execution budget **before** any numerical run.
- Original REV-2.2 D08 protocol has exhausted its budget; do **not** rerun A/B, alter seeds, thresholds, datasets, model choice or original artifacts, or relabel the two concurrent runs as a planned replication.

**Verification in this task:** GitHub source documents, issue state, pinned Git blob identity spot-check (6 files × 2 source commits) and historical authenticated audit reports read; **no direct new scientific artifact extraction, new model execution, local test suite, CI run or independent human attestation**.
