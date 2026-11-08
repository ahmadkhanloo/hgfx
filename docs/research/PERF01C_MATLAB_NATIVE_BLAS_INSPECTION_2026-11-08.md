# PERF-01C: in-process native MATLAB BLAS/MKL probe (UNTIMED; 2026-11-08)

**Gate: `BLOCK_FREEZE / NOT FROZEN`.** Research diagnostic only. Parent [PR #103](https://github.com/ahmadkhanloo/hgfx/pull/103) established **same physical CPU boot/affinity** and active Python OpenBLAS `1` reported thread, but the MATLAB process reported `MKL_NUM_THREADS=''` while Python reported `1`. The original all-six-variable environment attestation failed on real run [42489311821](https://github.com/ahmadkhanloo/hgfx/actions/runs/42489311821) and remains a **documented BLOCK**; no post-launch environment repair or post-hoc acceptance change.

## New question — not a new benchmark

Can we observe, *in the same running MATLAB process*, which BLAS/MKL shared libraries are actually mapped, and whether the **native MKL `mkl_get_max_threads` API reports a target concurrency cap**, without inferring real parallel worker activity from a process-wide thread count?

MathWorks documents `maxNumCompThreads(1)` and the `-singleCompThread` launch option as numerical computation controls; it documents Intel MKL as default x86_64 BLAS/LAPACK in R2026a and AOCL as an optional alternative. Intel defines `mkl_get_max_threads` as the maximum **targeted** internal OpenMP threads, **not an observation of actual active concurrent workers**. Therefore do not claim full BLAS thread parity merely from this new direct API probe.

Authoritative vendor documentation:
- https://www.mathworks.com/help/matlab/ref/maxnumcompthreads.html
- https://www.mathworks.com/matlabcentral/answers/1672304-how-can-i-use-the-blas-and-lapack-implementations-included-in-amd-optimizing-cpu-libraries-aocl-wi
- https://www.mathworks.com/matlabcentral/answers/102372-how-can-i-get-the-pid-of-the-current-matlab-session
- https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2026-2/mkl-get-max-threads.html

## Implementation (instrumentation code is separate from frozen scientific code)

1. `benchmarks/runtime_v1/matlab/perf01c_native_mkl_probe.c` is a **read-only C MEX** compiled inside the same MATLAB process: it obtains `getpid()`, scans the real `/proc/self/maps` for already mapped `mkl`, `blas`, `blis`, `aocl`, and OpenMP libraries, then queries `mkl_get_max_threads` (when exported) using `dlsym` and `dlopen(..., RTLD_NOLOAD)`. **RTLD_NOLOAD forbids loading an alternative BLAS library** just for observation. The MEX does not call `mkl_set_*`, `omp_set_*`, or any timing function.
2. `benchmarks/runtime_v1/matlab/probe_matlab_native_blas_untimed.m` obtains the official `matlabProcessID()` (available since R2025a), original environment snapshot and the current `maxNumCompThreads`; it initializes the native BLAS via a single small deterministic `A*A'` *untimed* operation, checks the MEX PID and records process thread totals before and afterward. These totals include MATLAB's many unrelated runtime worker/helper threads; **they do not count actual active BLAS threads**. If a MATLAB C compiler or the MKL symbol is unavailable, the evidence is `UNAVAILABLE_OR_FAILED`/unobserved, **not an inferred one-thread result**.
3. `benchmarks/runtime_v1/compare_matlab_native_blas_untimed.py` validates the two frozen versions and original same-runner CPU/affinity metadata, confirms MEX process PID and explicitly persists `original_env_rule=FAIL` and `original_environment_gate=BLOCKED_MATLAB_MKL_ENV` whenever the original MATLAB `MKL_NUM_THREADS` remains empty. Even if the native MKL target cap reads `1`, `matlab_actual_blas_worker_count_independently_verified` is **false** and `PERF-01C` is **BLOCK_FREEZE**.
4. `tests/test_perf01_matlab_native_blas_untimed.py` uses positive and negative controls: MKL target 1, target 4, missing API/compiler, wrong process/source/host, falsified worker claim, divergent env snapshots. `.github/workflows/perf01-matlab-native-blas-untimed.yml` executes the Python and MATLAB probe in one Actions job without clocks and archives the full raw JSON and analysis.

The original frozen scientific experiment remains untouched. Original 28 cases **16 REVIEW_PENDING / 12 BLOCKED**; original 64-subject fitting **63/64 SCIENTIFIC NONPASS** (subject index 7 with four `traj.mu` and four `traj.muhat` failures); original primary standard-HGF CPU denominator has **6/9 BLOCKED**. The seven Forward-only full-output diagnostic remains **7/7**, *untimed and without external scientific signoff*.

## Decisions still blocked

- Record actual supported BLAS implementation, MATLAB MEX availability and MKL target cap on the given host, without substituting another implementation/library after observing the result.
- Never equate `mkl_get_max_threads()==1` with **proof of one active worker** in real HGF workloads; independent process/thread evidence and prospective policy review are still required.
- Do not waive the observed original `MKL_NUM_THREADS` environment mismatch based only on the native target reading. Any acceptable alternative must be **prospectively versioned and externally reviewed**; preserve the failed original runs.
- No `hgfx-matlab-runtime-2` protocol lock, speedup benchmark, manuscript claim or physical GPU assertion before scientific reference evidence, full pairwise comparable timing policy and independent signoff.
