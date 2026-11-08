# PERF-01C CPU host, affinity and thread metadata candidate (2026-11-08)

**State after first real paired run: IMPLEMENTED; HOST/AFFINITY MATCH OBSERVED; MATLAB MKL ENVIRONMENT REQUEST MISMATCH — BLOCKED.** Scope: untimed CPU environment attestation, not a prospective benchmark. The previous [PR #102](https://github.com/ahmadkhanloo/hgfx/pull/102) established a seven-case full-output, one-call boundary at [run 42481218455](https://github.com/ahmadkhanloo/hgfx/actions/runs/42481218455) (7/7 numerical diagnostic only). Author-published [review PR #100](https://github.com/ahmadkhanloo/hgfx/pull/100) retains `BLOCK_FREEZE`. [Issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88) is **OPEN / NOT FROZEN**.

## Proposed environment metadata control: no timers

This is a bounded preflight to check whether original frozen HGFX `v1.0.0` (`4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`) and MATLAB HGF 8.2.0 (`2437f4dc241541072722a2695ddeca7b44d83dd3`) can run on a matching *real GitHub-hosted Linux CPU instance* with matching process-affinity visibility and consistent requested threading controls. Both probes are executed inside **one Actions job** to avoid treating two independent cloud machines as interchangeable.

Files added:
- `benchmarks/runtime_v1/probe_cpu_host_hgfx_untimed.py`
- `benchmarks/runtime_v1/matlab/probe_cpu_host_matlab_untimed.m`
- `benchmarks/runtime_v1/compare_cpu_host_attestation.py`
- `tests/test_perf01_cpu_host_attestation.py`
- `.github/workflows/perf01-cpu-host-attestation-untimed.yml`

The probes record `GITHUB_RUN_ID`, `GITHUB_SHA`, the Linux boot UUID, kernel, architecture, `/proc/cpuinfo` CPU model/vendor/microcode/flags, logical CPU count, per-process `Cpus_allowed_list`, visible governor if any, runtime versions and six selected thread-related process environment variables. Comparison **fails closed** on a missing/different boot identity, model, CPU flags, microcode, allowed CPU list, source pin, MATLAB R2026a or requested process thread limit.

The six candidate **requested** variables are `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `BLIS_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`. MATLAB additionally calls `maxNumCompThreads(1)` and requires the reported setting to be one. Python force-loads NumPy BLAS with a trivial **untimed** operation and inspects actual active `threadpoolctl` metadata (must include BLAS and report single threading). These settings are **not an already approved future benchmark policy**.

**Deliberate unresolved control:** `maxNumCompThreads(1)` + MKL/OMP environment is *not direct, independently verified active MATLAB BLAS/MKL runtime thread instrumentation*. Therefore even a successful host probe must return the explicit class `HOST_AFFINITY_AND_REQUESTED_THREADS_MATCH_MATLAB_BLAS_RUNTIME_UNVERIFIED`, **never** `PERF01C_PASS` or `CPU_BENCHMARK_READY`. Same allowed-affinity mask is also **not** per-core pinning or protection against scheduler migration. A public/shared GitHub runner is not guaranteed to be uncontended or stable in frequency, thermals, power or frequency governor. The metadata cannot establish those properties and the comparator explicitly marks them unproven.

The probe does **not** run the 7 original scientific forward tasks, compile JAX, measure time, compare speed, change seeds/data/starts, relabel the original 28 cases or retest the 64 public fit denominator. The original **28 = 16 review pending + 12 blocked**, including **six of nine primary CPU cells blocked**, and the original **63/64 whole-fit scientific NONPASS** with 4 `traj.mu` and 4 `traj.muhat` failures for subject index 7 remain binding.

## Gate after this isolated step

1. Independently inspect both complete raw host JSON files and the compare report under one source and Actions run SHA; download/re-hash the archive rather than assuming an artifact metadata digest is an independent hash.
2. Resolve **actual MATLAB BLAS runtime thread count**; if it cannot be established, record the environment as partially attested, not suitable for an unqualified controlled CPU speed claim.
3. Predeclare an enforceable affinity/pinning and contention/power policy for a prospective *restricted* benchmark; select the host independently of observed benchmark time, and explicitly record any shared runner caveats.
4. Obtain external scientific and measurement-protocol signoff of exact compute boundaries, original evidence, hardware conditions, output materialization and preregistered paired ABBA/BAAB statistical design **before** implementing/executing final timing.
5. Keep `hgfx-matlab-runtime-2` a DRAFT and PERF-01C `BLOCK_FREEZE / NOT FROZEN`; never infer an approved benchmark merely from a successful CI job.

**No GPU validation or speed comparison has taken place here.**

## First real same-host execution — failed acceptance preserved, not retested away

- **GitHub Actions [42488833040](https://github.com/ahmadkhanloo/hgfx/actions/runs/42488833040)**, initial PR #103 branch head `b18b6162c51a61d9a78ba34d21e555b3687d554d`, PR-triggered **executed GitHub merge SHA `73b093c1b037f0262e7a35088842c88928262622`** (note: the actual Actions `GITHUB_SHA` is the pull-request merge commit, *not* the PR branch head). CI classification: **FAIL / BLOCKED_ENVIRONMENT** at comparison, despite successful Python and MATLAB probe runs.
- **Real CPU and host concordance:** same actual Linux boot identifier (verified directly from both recorded files), same kernel `7.0.0-1017-azure`, physical CPU model label `AMD EPYC 9V45 96-Core Processor`, CPU vendor/flags/microcode, `4` visible logical CPUs, identical allowed process affinity `0-3`. The two processes did share a physical runner according to this Linux boot/CPU/affinity evidence. This is not proof of core pinning, uncontended performance, or stable frequency.
- **Python/HGFX:** active NumPy OpenBLAS runtime `0.3.30`, `pthreads`, `1` reported worker; six requested threading environment variables all observed as `1`.
- **MATLAB R2026a:** `maxNumCompThreads(1)` reported `1`; five of six process environment variables remained `1`, but **`getenv('MKL_NUM_THREADS')` was empty**, while the pre-MATLAB Python process recorded `MKL_NUM_THREADS=1`. This difference was observed inside the MATLAB process, even though the GitHub job requested `MKL_NUM_THREADS=1`. **Do not infer where the value was cleared or that the actual MATLAB MKL runtime thread count was one.** A missing variable is not an allowed match. The strictly predeclared host+all-thread-env comparator rightly **failed**.
- **Authenticated raw archive check:** downloaded complete [artifact 13620018816](https://github.com/ahmadkhanloo/hgfx/actions/runs/42488833040/artifacts/13620018816) directly through the GitHub-connected artifact API. Locally recalculated the ZIP SHA256 `d703ee011cdb82e33717934febd48f79935a227fd66b711b4bb95046cccb01a2`, **matching the GitHub metadata digest**. Raw member hashes: `hgfx_host.json` `dbf4de01f798d596a791c6d86aeb72a1e8859cc14fc790f729d4e185d11b26ca`; `matlab_host.json` `f1869129e2a31bdf9ac6e5a8e6ead666dd5fd3829fb167f5cc73fe4ec4775812`. Unlike earlier metadata-only references, this ZIP and its members were independently inspected in this run. The two observations and underlying failure are preserved in original Actions artifact/history.
- **Engineering follow-up:** the subsequent comparator now persists a machine-readable **`BLOCKED_ENVIRONMENT_ATTESTATION`** report, with the exact six process-variable differences and same-host field comparison **even when the CI job exits nonzero**. This **does not relax or bypass** the original requirement that each requested environment variable must equal `1`. A regression negative test asserts the exact `MKL_NUM_THREADS: Python='1', MATLAB=''` failure is retained and the process still fails.
- **Environment-specific unresolved gate:** independently demonstrate MATLAB's *actual runtime BLAS/MKL threading*, not only the in-process `maxNumCompThreads` value; predeclare whether MATLAB's observable unset MKL environment is acceptable by different direct evidence. Until then this control is **BLOCKED**. Do not set `MKL_NUM_THREADS=1` **after** MATLAB has initialized and pretend that proves initial MKL thread count.

This separate failure does not affect the 7/7 **untimed numerical diagnostic** reported by PR #102, does not alter data or thresholds and is **not permission** to run a measured CPU speed comparison or to change historical PERF-01C acceptance decisions.
