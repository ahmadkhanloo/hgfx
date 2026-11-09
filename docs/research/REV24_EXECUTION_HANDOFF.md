# REV-2.4 execution handoff — preregistered science, awaiting real oracle

> **CURRENT executable handoff (2026-11-10):** The original example commands further below precede the frozen-tag byte-verification hardening and must not be run verbatim. The current audited entrypoint is [`.github/workflows/compstat-rev24-original-oracle.yml`](../../.github/workflows/compstat-rev24-original-oracle.yml), a **manual** authentic MATLAB/HGFX objective run. It must be run from an authorized Actions checkout where a true HGF 8.2.0 MATLAB reference is present; the workflow has **not** run in this session. The currently configured artifact identity is the actual [PyPI HGFX 1.0.0 wheel](https://pypi.org/project/hgfx/1.0.0/) SHA-256 `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`. Both the runner and standalone manifest/evaluator now require `--frozen-tag-source <checkout-of-v1.0.0>` and verify every `hgfx/*.py` wheel member against that frozen tag. This is stricter than checking just the version string.


**Current author D1:** A / continue *Computational Statistics* (2026-11-10).  
**Milestone:** REV-2.4 **IN PROGRESS / IMPLEMENTED INPUT TOOLING, SCIENTIFIC VALIDATION OPEN**.  
**Protocol authority:** [REV-2.4_PROTOCOL.md](../../evidence/revision/protocols/REV-2.4_PROTOCOL.md) — commit `d1986311b8a5ff97f088ebac35c612e16cbe89db`; this file was committed **before** the manifest tool or any experimental execution.

## Already implemented (NOT a scientific result)

- `tools/compstat_rev24_manifest.py`: deterministic N=200 × three-model synthetic fixed-vector source, strict original denominators and case/manifest SHA-256, frozen source/config labels and CPU binary64 data hashes.
- Requires installed **non-editable HGFX 1.0.0**, archived **actual 1.0.0 wheel**, exact **NumPy 2.0.2** and checks each installed HGFX Python source file against its byte-identical wheel member. Worktree `1.1.0b1` does **not** count as release evidence.
- `tests/paper/test_compstat_rev24_manifest.py`: eight focused unit-test cases for N=600/no omissions, reproducibility, fixed/free mask, binary64 array identity, corruption rejection, NumPy version mismatch, wheel source tampering. Authored, **NOT claimed executed PASS**.
- `.github/workflows/compstat-rev24-manifest-contract.yml` contains a Python 3.11 / NumPy 2.0.2 contract-only unittest job. An Actions result on this new revision has not yet been observed. This workflow does **not** run MATLAB and is **not** scientific validation.

## Next commands for a fresh authorized Python 3.11 + MATLAB runner

**Important:** run the command only when the exact archived release wheel and the frozen reference source are available and verifiable. No silent fallback to branch `main` or `compstat-revision` for scientific values. Example using a real **PyPI** wheel fetched through the authorized package channel:

```bash
python3.11 -m venv /tmp/hgfx-rev24-v1-wheel
. /tmp/hgfx-rev24-v1-wheel/bin/activate
python -m pip install --index-url https://pypi.org/simple 'numpy==2.0.2' 'jax>=0.4.30'
python -m pip download --index-url https://pypi.org/simple --no-deps 'hgfx==1.0.0' --dest /tmp/rev24-original-wheel
python -m pip install --no-deps /tmp/rev24-original-wheel/hgfx-1.0.0-*.whl
python -m pip show hgfx
sha256sum /tmp/rev24-original-wheel/hgfx-1.0.0-*.whl
# Run OUTSIDE the repository so working-tree source cannot shadow the release.
cd /tmp
python /absolute/path/to/hgfx/tools/compstat_rev24_manifest.py \
  --release-wheel /tmp/rev24-original-wheel/hgfx-1.0.0-<actual-wheel-tag>.whl \
  --output /tmp/rev24_grid_manifest.json
```

Replace the placeholder `<actual-wheel-tag>` with the **real downloaded filename** (no guessed wheel identity). Record exact Python, NumPy, JAX/JAXLIB, installed HGFX path/version, SHA256 of wheel and generated manifest, OS/hardware. Do **not** overwrite an existing manifest or regenerate failed cases.

Before an actual paired science experiment, implement and review **the genuinely frozen MATLAB 8.2.0 evaluator** consuming this exact manifest (no generation or optimization) and **the installed-v1.0.0 HGFX evaluator** consuming the identical free/full vector. The MATLAB evaluator must use the official `fitModel` objective semantics, resolved default configs, free ordering, the same `unitsq_sgm` model, and per-trial likelihood/finite-state handling. Confirm exact input hashes and source paths, not just returned scalars. No performance/timing inference.

Then separately obtain D02, D08 and the original 64-fit source endpoints, with source SHA checks and complete subject/case accounting, before executing endpoint cross-evaluation. D08 is **`uhgf + gaussian_obs`**, not the Panel-G `uhgf_binary + unitsq_sgm` model.

## Numeric decision and blocker policy

- Existing HGF M8 objective tolerance: **rtol 2e-11, atol 2e-13**; frozen per-field M18 tolerances apply to the corresponding older fit/trajectory fields. **Do not invent** an objective PASS threshold for other families; report `NO_PREDECLARED_FAMILY_OBJECTIVE_GATE` until a pre-existing registered gate is identified and pinned.
- Exactly 600 fixed-vector tests (200 × 3) plus the separately sourced endpoint grid, one full scientific run; all errors, NaNs, invalids and dropped/missing inputs counted. Record first trial, level, state and intermediate or precise NOT_EXPORTED marker.
- No MATLAB engine and no distributed v1.0.0 wheel were accessible in the present assistant's local runtime; package download from its configured index returned no matching distribution. **No 600-vector manifest or paired MATLAB/HGFX objective results were produced**, and no new GitHub Actions run was observed.
- If no genuine oracle is available, mark REV-2.4 **BLOCKED_ON_ORACLE** at the experiment level rather than reclassifying historical M18/P3/subject-7 failures or PERF-01C BLOCK_FREEZE.

## Required publication outputs after independent execution

`evidence/revision/rev24_grid_manifest.json`, original raw MATLAB and HGFX result hashes (the latter only after actual execution), per-field first-divergence table, `evidence/revision/rev24_objective_result.json`, one compact ledger report with exact commit/run/versions, and D2 author-reviewed claim scope. No inference of full fitting parity from objective-only results.

## Current pipeline, actual implementation status (2026-11-10)

1. Preregistered `REV-2.4_PROTOCOL.md` and appended a prospective **`NaN` fixed-slot JSON encoding clarification** before any original paired experiment. No sample, seed, parameter mask or frozen tolerance changed.
2. Source-grid generator `tools/compstat_rev24_manifest.py` now writes literal `"NaN"` for preserved undefined parameters, not invalid JSON floats. Per-family free-index, priormus, priorsas and model identity are bound by `config_sha256`. It blocks negative/inf variance, non-finite free draws, altered case counts, missing source, wrong NumPy 2.0.2 or editable 1.1.0b1 installations.
3. The public HGFX 1.0.0 PyPI Wheel SHA-256 is pinned to `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`. PyPI attestation names publish commit `8d46da2a559d869c693eb33602ac3fb0b49ab5eb`; GitHub comparison against frozen `v1.0.0` `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` found 10 subsequent commits but **no changes under `src/hgfx/`**. The final runtime guard nevertheless compares **actual module bytes** inside the downloaded Wheel to frozen tagged checkout. Do not assume matching distribution name is proof of source identity.
4. `tools/compstat_rev24_hgfx_eval.py` evaluates the exact installed Wheel's `_objective_for_variant` on all 600 manifest vectors **without an optimizer**; records status, full per-trial likelihoods, joint/likelihood totals and all failures.
5. `reference/matlab/run_compstat_rev24_matlab.m` consumes precisely the same manifest; asserts real HGF Toolbox 8.2.0 git SHA and config/prior/free-index identity; evaluates all 600 fixed vectors without fitting. It has **not** been executed in MATLAB or independently reviewed here.
6. `tools/compstat_rev24_compare.py` checks exact 600-case identity and provenance of both returned records, rejects per-case config drift/shape/NaN errors, uses only the pre-existing HGF M8 objective threshold and returns `NO_PREDECLARED_FAMILY_OBJECTIVE_GATE` for eHGF/uHGF. **Nine synthetic comparator unit tests executed locally and passed on Python 3.13.5**; these are not evidence of real oracle parity. The input generator now has **12 authored** unit tests, not verified by CI yet.
7. Manual [REV-2.4 original-oracle workflow](../../.github/workflows/compstat-rev24-original-oracle.yml) combines frozen tag, pinned PyPI download, release-only manifest, HGFX and MATLAB evaluations and paired audit. It uploads immutable workflow artifacts rather than modifying historical M18 files. **Panel E original D02/D08/64 cross-endpoints remains a distinct OPEN task.**

**Execution gate today:** No new GitHub Actions run has been observed for these commits, no original paired MATLAB/HGFX 600-vector analysis was executed, no Objective parity or fitted science pass may be claimed. Any test/runner failures must be retained and fixed only through documented source changes without changing input-grid definitions.
