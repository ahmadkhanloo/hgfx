# HGFX v1.0 Live TODO

Last synchronized: 2026-09-17
Status: **V1.0.0 RELEASE COMPLETE — PV1-02 METHODS PAPER ACTIVE / P1–P2A/P5/P6 DONE; P3 RUNNING ON GITHUB ACTIONS**
Branch: `main`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Published release: `v1.0.0` -> `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
GitHub Release: https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0 (ID `389966452`)
PyPI: https://pypi.org/project/hgfx/1.0.0/

The v1.0.0 release gate remains closed. The active post-v1 objective is PV1-02 methods-paper/publication work, tracked by GitHub issue #32 and `../research/PAPER_EXECUTION_PLAN.md`. Paper protocol P1 is frozen as `hgfx-paper-protocol-1`; P2/P2A/P3 are the next active publication work packages.

## Accepted evidence

- M0–M17: complete in documented scopes.
- Historical M18 scientific experiment: **FAIL preserved**.
- D02/D08 direct failures and exact-grid S7 parameter recovery: scoped `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- D04/D09/D10–D11/D12: PASS in recorded scopes.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8 required repair: DONE.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`.
- S9 physical GPU: `PASS_PHYSICAL_GPU_APPLICABILITY` on 2x Tesla T4; maximum CPU/GPU objective gap `1.4210854715202004e-14` against frozen `1e-7`.
- M19: PASS / FROZEN.
- M20 RC candidate gate: **PASS**, `PASS_M20_CANDIDATE`.
- Independent frontier review: completed; original report preserved in `../validation/INDEPENDENT_REVIEW_REPORT.md`.
- Review blockers H1/H2: **RESOLVED** without changing thresholds, seeds, data, grids, model family, optimizer, or historical evidence.
- PR #29 merged to `main` at `ffa84c616343714d7d384b0a21e6f8d73f7cb990`; main `HGFX Regression` run `35087865209`: PASS.
- Final package/citation metadata: `1.0.0`.
- PR #30 final-promotion head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`:
  - S10 run `35089882319`: PASS.
  - M19/M20 preflight run `35089882608`: PASS.
  - D10/D11 run `35089882668`: PASS.
  - Regression run `35089882392`: PASS on Ubuntu and Windows.
- PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; main Regression run `35090329868`: PASS on Ubuntu and Windows.
- Tag `v1.0.0` verified to resolve directly to `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- GitHub Release ID `389966452` is published, non-draft and non-prerelease.
- PV1-03 PyPI publication: **DONE / PASS**.
  - Trusted Publishing run `35207257208`: PASS.
  - Independent public-PyPI install/smoke run `35207903084`: PASS.
  - Public install: `python -m pip install hgfx==1.0.0`.
- PV1-02 P1 paper protocol freeze: **DONE / FROZEN_FOR_EXECUTION**.
  - protocol: `paper/reproducibility/PAPER_PROTOCOL.md`;
  - protocol ID: `hgfx-paper-protocol-1`;
  - recovery/identifiability settings, statistical summaries, comparator identity, provenance requirements, and claim exclusions frozen before final paper-only execution.

## Ordered release work

1. **DONE:** M20 RC gate and evidence freeze.
2. **DONE:** independent final review.
3. **DONE:** resolve all Critical/High review findings (H1/H2).
4. **DONE:** rerun post-fix cross-platform regression and release gates.
5. **DONE:** merge PR #29 and verify its main integration.
6. **DONE:** promote package/citation metadata to `1.0.0` on PR #30.
7. **DONE:** validate PR #30 exact head, merge to `main`, and verify final main source target `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
8. **DONE:** create and verify `v1.0.0` Git tag/GitHub Release targeting the exact validated source; Release ID `389966452`.
9. **DONE:** publish `hgfx==1.0.0` to PyPI from the exact frozen tag through Trusted Publishing and independently verify clean installation from the public index.

## Post-v1 backlog — future tasks, not v1 release blockers

These items are the explicit forward backlog after the completed `v1.0.0` release. They must not be interpreted as reopening the frozen v1 release gate. A task becomes the active project objective only when explicitly selected and, where appropriate, given a new milestone/release gate.

### PV1-01 — M18C.2 trial-horizon / identifiability analysis

**Status:** IN PROGRESS / RESEARCH / GITHUB ACTIONS EXECUTION 
**Tracking:** GitHub issue #21

Goal: determine whether the preserved M18 parameter-recovery failures are primarily data-horizon limited or reflect structural/weak identifiability.

Planned scope:

- run the frozen recovery protocol at trial horizons `128`, `256`, `512`, and `1024`;
- cover `hgf_binary`, `ehgf_binary`, and `uhgf_binary`;
- report convergence rate, parameter RMSE, standardized RMSE, median correlation, bias, likelihood/profile diagnostics, and model-recovery accuracy;
- compare results without changing the frozen M18 thresholds, seeds, datasets, grids, model family, or optimizer after seeing outcomes.

Exit evidence:

- reproducible result artifacts committed to the repository;
- an explicit conclusion separating data-limited identifiability from structural/weak identifiability, with uncertainty preserved;
- no retroactive conversion of historical M18 FAIL evidence into PASS.

### PV1-02 — Methods paper and reproducibility package

**Status:** IN PROGRESS / PUBLICATION / P1 FROZEN  
**Tracking:** GitHub issue #32  
**Plan:** `../research/PAPER_EXECUTION_PLAN.md`

Goal: turn the validated HGFX implementation and evidence base into a methods-paper-quality research package.

Current state:

- working manuscript created at `../../paper/manuscript.md`;
- initial bibliography created at `../../paper/references.bib`;
- paper plan and evidence map synchronized to post-M19/v1.0.0 reality;
- v1 equivalence narrative is drafted from frozen evidence;
- HGFX `1.0.0` is now publicly installable from PyPI;
- paper protocol P1 is frozen as `hgfx-paper-protocol-1` with status `FROZEN_FOR_EXECUTION`;
- `pyhgf==0.3.2` is the frozen comparator identity for protocol 1, subject to a semantic gate before direct empirical comparison;
- general speedup/multi-GPU scaling is intentionally not a headline claim under protocol 1;
- P2 tables generated and CI-gated (`paper/tables/`);
- P2A common-scope comparison complete (issue #33 closed);
- P5 figures generated from frozen S7/P2A.10 evidence (`paper/figures/`);
- P6 reviewer entry point at `paper/reproducibility/README.md`;
- P3 M18C.2 24-shard MATLAB/HGFX matrix running on GitHub Actions (`35272347167`); invalid 512-trial simulations are retained, not dropped;
- remaining: complete P3 coverage/classification, P3 figure, P6A freeze, P7 lock, P8 independent audit.

Planned scope:

- generate core equivalence tables from frozen v1 evidence;
- complete fair pyhgf semantic mapping and qualitative comparison, allowing `NOT_DIRECTLY_COMPARABLE` where appropriate;
- execute the frozen PV1-01 recovery/identifiability analysis if retained for the stronger methods paper;
- define and record exact software/runtime environments for every new paper execution;
- describe MATLAB-equivalence policy and `REFERENCE_LIMITATION_MATCH` semantics accurately;
- include physical-GPU evidence and clearly distinguish correctness/applicability from scaling claims;
- prepare a reproducibility bundle with commands, configs, seeds, data references, environment information, and exact HGFX commit/tag identifiers;
- draft and review the manuscript without rewriting historical failed experiments.

Exit evidence:

- complete manuscript source;
- frozen paper protocol;
- reproducibility package;
- all reported figures/tables traceable to committed evidence;
- final paper evidence manifest marked `FROZEN_FOR_SUBMISSION`;
- independent pre-submission review with no unresolved CRITICAL/HIGH findings.

### PV1-03 — PyPI publication

**Status:** DONE / PASS / DISTRIBUTION

Published package:

```text
hgfx==1.0.0
https://pypi.org/project/hgfx/1.0.0/
```

Provenance:

- package source: `v1.0.0` -> `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`;
- publication mechanism: PyPI Trusted Publishing / GitHub OIDC;
- publication workflow run `35207257208`: PASS;
- public-index clean-install verification run `35207903084`: PASS on CPython 3.12.14 / Ubuntu 24.04.5;
- verification installed from `https://pypi.org/simple` and confirmed public API imports plus a minimal fitting smoke test;
- distribution provenance and future release rules recorded in `PYPI_PUBLISHING.md`.

### PV1-04 — Post-v1 performance benchmark refresh

**Status:** TODO / PERFORMANCE / NOT ACTIVATED FOR PAPER PROTOCOL 1

Goal: produce a clean, reproducible performance characterization of released HGFX without mixing correctness evidence with throughput claims.

This remains a separate future task. `hgfx-paper-protocol-1` deliberately does not activate general speedup or multi-GPU scaling as a headline paper claim. If a later paper revision requires performance as a headline contribution, a new paper protocol version must be frozen before final benchmark execution.

Planned scope when selected:

- freeze benchmark workloads before execution;
- report compile time separately from steady-state execution;
- benchmark representative trial counts, subject counts, restarts, model families, and batch sizes;
- measure CPU, single-GPU, and multi-GPU throughput where suitable hardware is available;
- record hardware, driver, CUDA/JAX/Python versions, command lines, commit SHA, contention state, and limitations;
- preserve earlier H100/T4 evidence in its original historical scope rather than replacing it.

Exit evidence:

- machine-readable benchmark results;
- reproducible benchmark commands;
- performance report with explicit hardware/environment provenance and no unsupported peak-performance claims.

### PV1-05 — Future upstream HGF compatibility

**Status:** TODO / ON-DEMAND COMPATIBILITY

Goal: handle a future upstream HGF Toolbox release without changing the frozen v1.0 compatibility claim.

Trigger: a new upstream HGF Toolbox version is selected for support.

Planned scope:

- keep HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3` immutable as the v1.0 oracle;
- diff the new upstream version against the frozen oracle;
- classify only new/changed MATLAB files and semantics;
- generate new/changed fixtures;
- create a separate migration plan and versioned compatibility gate;
- choose a new HGFX version according to the compatibility impact rather than silently changing v1 behavior.

Exit evidence:

- explicit new oracle version/commit;
- migration matrix for changed surfaces;
- new validation evidence and release gate separate from v1.0 history.

### PV1-06 — New features and non-blocking maintenance

**Status:** TODO / LOW-PRIORITY UNTIL SELECTED

Goal: maintain and extend HGFX without conflating feature work with the completed v1.0 release.

Current scope candidates:

- triage and, where worthwhile, address independent-review findings M1/L1/L2;
- improve usability, documentation, diagnostics, plotting, convenience APIs, or developer ergonomics;
- add new model/features only with explicit tests and compatibility/scientific acceptance criteria;
- create a dedicated milestone/release plan before any change that alters public behavior or scientific claims.

Exit evidence depends on the selected maintenance/feature item and must be defined before implementation.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, `FINAL_REVIEW_CHECKLIST.md`, `../validation/V1_EVIDENCE_INDEX.md`, `../validation/V1_FINAL_RELEASE_PROVENANCE.md`, and `../validation/INDEPENDENT_REVIEW_REMEDIATION.md` as the frozen v1 continuity set.

For the active publication objective, use `../research/PAPER_EXECUTION_PLAN.md`, `../research/LEVEL2_PAPER_PLAN.md`, `../research/PAPER_EVIDENCE_MAP.md`, `../../paper/reproducibility/PAPER_PROTOCOL.md`, and `../../paper/manuscript.md` as the continuity set.

For public distribution provenance, use `PYPI_PUBLISHING.md` and `.github/workflows/verify-pypi.yml`.

Do not reopen completed D02/D08/S7/S8 diagnostics merely to manufacture a green scientific result. Historical failures remain immutable. No tolerance, seed, data, grid, model family, optimizer, or acceptance threshold may be changed post-hoc to obtain PASS.

**There is no remaining blocking work for HGFX v1.0.0. Publication work is separate post-v1 scope.**
