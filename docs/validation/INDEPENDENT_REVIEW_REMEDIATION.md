# HGFX v1.0 Independent Review Remediation Record

Date: 2026-09-16
Initial independent-review target: `ad8f5cd6fbea3bd1e5ac1cef8b51dbbb9a970a84`
Post-remediation validated source: `09c49031cda95b449f8115030a9d32dcba36098e`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Status: **POST-REVIEW VALIDATION PASS — NO UNRESOLVED CRITICAL/HIGH FINDINGS**

This record is additive. It does not rewrite `INDEPENDENT_REVIEW_REPORT.md`, historical M18 failures, reference-limit classifications, frozen thresholds, seeds, datasets, grids, model families, or optimizer settings.

## H1 — platform-dependent libm divergence

**Status: RESOLVED.**

The compatibility path no longer delegates the D02-sensitive `exp`, `expm1`, or active unit-square `log` calculations to host CRT/libm implementations. Portable binary64 fdlibm-compatible implementations are used in:

- `src/hgfx/math/matlab_exp.py`;
- `src/hgfx/math/matlab_log.py`;
- `src/hgfx/responses/unitsq_sigmoid.py`.

Regression coverage includes the frozen D02 scalar oracles and portability tests. The acceptance criteria were not relaxed.

## H2 — Windows CRLF/hash integrity

**Status: RESOLVED.**

Git-managed validation text is LF-controlled by `.gitattributes`, while reference verification canonicalizes text line endings where the frozen scientific content is text-semantic. The frozen MATLAB submodule verifier no longer mistakes Windows working-tree CRLF expansion for source modification.

A clean Windows checkout now passes both the frozen-reference guard and the complete source-classification guard.

## Post-remediation validation

All listed workflows ran against PR #29 with head `09c49031cda95b449f8115030a9d32dcba36098e` and completed successfully:

- `HGFX Regression` run `35080084509`: **PASS** on Ubuntu 24.04 and Windows Server 2025. Windows result: `178 passed, 4 skipped, 0 failed`; frozen reference verification: `PASS`, `matlab_files=334`.
- `M18 S9 Backend Robustness` run `35080084517`: **PASS**.
- `S10 v1 Release Readiness` run `35080084519`: **PASS**.
- `M19 M20 Release Preflight` run `35080084594`: **PASS**.
- `V1 Full MATLAB Demo Composition` run `35080084742`: **PASS**.

The four skipped tests in CPU-host regression are the explicitly physical-GPU-only M14/M15/M16/M17 cases; they are not counted as CPU substitutes for GPU evidence.

## Physical-GPU evidence applicability after H1/H2

Physical S9 evidence remains the recorded Kaggle run at source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec` on two Tesla T4 devices, with `PASS_PHYSICAL_GPU_APPLICABILITY` and maximum CPU/GPU objective gap `1.4210854715202004e-14` against the frozen `1e-7` criterion.

This evidence is retained only because the physical-GPU executable path is unchanged since that run:

- the blob SHAs for files under `src/hgfx/gpu/` are unchanged between `07b45a...` and `09c49031...`;
- `scripts/run_m18_s9_backend_robustness.py` has identical blob SHA `d886819c2ef8fa4969f397310f39ca0ac4b02bc8` at both revisions;
- the post-review numerical changes are in the CPU/MATLAB-compatibility `exp`/`expm1`/`log` path and reference-integrity handling, not the JAX GPU fast path;
- the compatibility-vs-JAX CPU portion of S9 was rerun on the post-fix source and passed in run `35080084517`.

This is an executable-path identity argument backed by prior physical hardware evidence, not a claim that CPU testing substitutes for GPU validation.

## Licensing/provenance addendum

The portable numerical routines are adapted from fdlibm `e_exp.c`, `s_expm1.c`, and `e_log.c`; the applicable Sun Microsystems/SunSoft permission notices are preserved in the adapted source modules and summarized in `THIRD_PARTY_NOTICES.md`.

Factual erratum to the original independent report: its licensing checklist text refers to the frozen HGF Toolbox as GPL v3. The frozen upstream commit `2437f4dc...` contains an MIT license. The original review report is preserved unchanged as historical evidence; this record supplies the correction.

## Promotion conclusion

The independent review identified two release-blocking HIGH findings, H1 and H2. Both are resolved and the post-remediation cross-platform/release validation is green. The MEDIUM/LOW findings in the original review remain non-blocking and should be tracked as maintenance work rather than used to rewrite the frozen scientific gate.

The next release step is to merge PR #29, verify required main-branch checks on the merge commit, then promote package/citation metadata from `1.0.0rc1` to `1.0.0` and create the final release provenance.
