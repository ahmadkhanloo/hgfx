# PERF-01C: first bounded untimed forward-only runner candidate (2026-11-08)

Status: **IMPLEMENTED, EXECUTION/SCIENTIFIC REVIEW PENDING** until a real paired Actions result is inspected. Protocol `hgfx-matlab-runtime-2` remains **BLOCK_FREEZE / NOT FROZEN** under owner-published [review PR #100](https://github.com/ahmadkhanloo/hgfx/pull/100) and [Issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88). The review was Codex-assisted and owner-published, **not a proven external independent review**.

## Strict first step, no performance numbers

New candidates:
- `benchmarks/runtime_v1/forward7_hgfx_untimed.py`
- `benchmarks/runtime_v1/matlab/forward7_matlab_untimed.m`
- `benchmarks/runtime_v1/compare_forward7_untimed.py`
- `tests/test_perf01_forward7_untimed.py`
- `.github/workflows/perf01-forward7-untimed.yml`

These run the original frozen HGFX 1.0.0 and genuine MATLAB HGF 8.2.0 *perceptual forward only*, no observation likelihood, no objective, no optimiser, no timers. Workloads use existing original subject zero, unchanged binary64 inputs and original resolved transformed-start vector; return **all 11 original trajectory fields and full `N×3×4` inference states**. Inputs and configs are materialized before each call, and both exports retain the complete output without reducing to a scalar surrogate. MATLAB's active `which(model)` source resolution is recorded; it is not assumed to be verified merely from the toolbox SHA. Only full output/parity checks are attempted, not timing comparability or equal thread/ISA/BLAS conditions.

The **seven already diagnostic-concordant original Forward IDs** in the 28-case ledger are:
`primary_forward_128`; `secondary_ehgf_binary_forward_128`, `_512`, `_1024`; `secondary_uhgf_binary_forward_128`, `_512`, `_1024`.
This is an explicit *candidate sub-scope*, **not removal** of the other 21 original cells. The eight original invalid, two restart-incompatible and two original multisubject-fit-mismatched cases stay blocked. Historical original matrix remains **16 REVIEW_PENDING / 12 BLOCKED**, six of nine original primary cells blocked; original fitting remains **63/64 SCIENTIFIC NONPASS** (four `traj.mu` and four `traj.muhat` failures for zero-based subject 7).

The new comparator rejects missing/duplicated case IDs, unpinned source versions, input/config hash changes, wrong subject/horizon, absent/extra trajectory fields, mismatched trial axes (even for equal flattened array sizes), incomplete states, and any failed original-tolerance field. Its calculation reuses **unchanged** `compare_trialwise.compare_numeric` (`atol=3e-10`, `rtol=3e-8`); this is a diagnostic, not a new Level-1 or Level-2 gate. The comparison report is never marked as an approved timing or scientific PASS, even when seven rows agree.

## Execution / provenance

Open a PR from `research/perf01c-forward7-untimed` against the stacked original-diagnostics branch `research/perf01d-unitsq-intermediate-arithmetic`. The `perf01-forward7-untimed` Actions workflow is PR-triggered or manual. It checks both exact frozen source SHAs, verifies input/config files, executes synthetic fail-closed unit tests, runs paired source forward-only on the same Actions runner (without timers), writes a 7-row full-vector comparison, and uploads all available raw JSON in an Actions artifact even when a comparison step fails.

**DO NOT** change a source/seed/start/horizon to obtain agreement, suppress failed workflows, selectively time only a favorable outcome, or claim speedup. A green job is *engineering diagnostic execution only*, not independent scientific or benchmark approval.

## Remaining review blockers after this first step

1. Inspect the actual paired workflow run and all exported source paths; verify real array shape, source resolution, original raw evidence hashes and correspondence with frozen original models. If it fails, retain failure and investigate without changing original thresholds.
2. Obtain authenticated archive ZIP bytes/member checks and rerun original raw comparators independently. Review original scientific Level-2/optimizer condition separately; historical 63/64 must remain.
3. Define, code and independently review the **actual timed-region wrapper** for these same seven forward operations, with precisely symmetric input preparation/output materialization and exclusion/inclusion of result serialization. An untimed exporter **alone does not constitute a timeable comparator**.
4. On one identified physical CPU host, predeclare core affinity, active MATLAB and Python/BLAS thread counts/ISA dispatch, software/dtype, power and contention policy, output policy, retries, execution order, statistical analysis and immutable source/runner hashes.
5. Obtain separate authenticated scientifically independent reviewer adjudication and lock a *new prospective restricted protocol* **before** any paper-use benchmark timing. No CPU/GPU performance claims or original nine-case aggregate approval.
