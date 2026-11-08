# PERF-01C follow-up review of PR #105

**Decision** — `BLOCK_FREEZE`. The seven original Forward cells have positive case-specific evidence and are suitable candidates for a new Forward-only protocol. Final scientific eligibility requires inspection of the original arrays and explicit Level-0 and Level-1 checks. A new one-logical-CPU resource contract is defensible in principle and still needs validation on the chosen host.

**Publication** — Mohammad Ahmadkhanloo (@ahmadkhanloo), repository owner. Codex performed the evidence review at the owner's request on 2026-11-08. The owner publishes this AI-assisted assessment. External independent signoff is outstanding.

## Reviewed snapshots and evidence

| Ref | SHA |
|---|---|
| [PR #105](https://github.com/ahmadkhanloo/hgfx/pull/105), open draft | `0a17e5dd8379ed49009a93e2546dcae21c58d7c3` |
| PR #105 stacked base | `e6ff1c47151a3445b6ac2af79b492c399d6d5602` |
| [PR #99](https://github.com/ahmadkhanloo/hgfx/pull/99) | `81d9e8fc67c1d801f7d749cf44ba9fcfffdbf1f3` |
| [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87) | `271e480216ed8ecd19f76c960b75a3826ed89337` |
| `main` | `44353387ab2578339174f0d8252aecb737654ae7` |
| HGFX 1.0.0 | `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| MATLAB HGF Toolbox 8.2.0, run with R2026a | `2437f4dc241541072722a2695ddeca7b44d83dd3` |

GitHub records both the [raw replay 42494412815](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494412815) and [Linux/Windows regression 42494412793](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494412793) as successful at the reviewed #105 head. The raw replay job reports successful authenticated retrieval, recomputation and upload. The code checks all six extracted member hashes and equality with both archived comparison reports. It separately verifies the three provenance keys added to the tracked fit report and independently recounts the subject-7 exceedances from the raw arrays. The workflow checks extracted member bytes. The verifier's optional ZIP path also checks the original ZIP bytes. [Replay workflow](../../.github/workflows/perf01c-raw-artifacts-replay.yml) · [Verifier](../../benchmarks/runtime_v1/verify_perf01c_raw_archives.py)

| Artifact | GitHub ZIP SHA-256 checked against public metadata |
|---|---|
| [13341288055, original 64 fits](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006/artifacts/13341288055) | `45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587` |
| [13617382986, original seven Forward boundaries](https://github.com/ahmadkhanloo/hgfx/actions/runs/42481218455/artifacts/13617382986) | `6928272eeab342df85a833fa2ce058d713202495fb2f666bb3c7b3307cd21a95` |
| [13623385329, current replay report](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494412815/artifacts/13623385329) | `e29e02c9405eb704bcd25223825511b6cfbca94b576775a7da6aa8f3b9351c49` |

GitHub listed all three artifacts as unexpired and returned HTTP 401 for their unauthenticated archive endpoints. This review confirms the Actions execution and metadata. Direct inspection and rehashing of the original ZIP and member bytes remain outstanding here. The [raw evidence handoff](../PERF01C_RAW_ARCHIVE_REVIEW_HANDOFF_2026-11-08.md) records all six member hashes and distinguishes independently downloaded ZIPs from the Actions extraction.

## Scientific assessment and callable boundary

The [previous review's case-by-case ledger](https://github.com/ahmadkhanloo/hgfx/blob/eda00c9d60fe44fe90c601c6a811f4493819f270/docs/research/reviews/PERF01C_REVIEW_2026-11-08.md#3-all-28-original-cases) applies to all 28 original cases. Git-tree comparison against #99 found identical original source pins, inputs, configs, eligibility ledgers and fit summaries. The current tracked-ledger check confirmed 16 pending and 12 blocked, including six of nine primary cases. The original 64-subject fitting result remains **63/64 SCIENTIFIC NONPASS**. The replay handoff reports four `traj.mu` exceedances at `[83,1], [108,1], [116,1], [126,1]` and four `traj.muhat` exceedances at `[84,1], [109,1], [117,1], [127,1]`, zero-based, with a maximum absolute delta of `1.5704625655477145e-9` in each field. The follow-up supplies no new basis for a fitting exception.

| Case | Evidence at the original subject-zero input |
|---|---|
| `primary_forward_128` | Positive full-output concordance for HGF 128 |
| `secondary_ehgf_binary_forward_128` | Positive full-output concordance for eHGF 128 |
| `secondary_ehgf_binary_forward_512` | Positive full-output concordance for eHGF 512 |
| `secondary_ehgf_binary_forward_1024` | Positive full-output concordance for eHGF 1024 |
| `secondary_uhgf_binary_forward_128` | Positive full-output concordance for uHGF 128 |
| `secondary_uhgf_binary_forward_512` | Positive full-output concordance for uHGF 512 |
| `secondary_uhgf_binary_forward_1024` | Positive full-output concordance for uHGF 1024 |

Both wrappers make one perceptual call and return eager arrays in memory. Both return all 11 trajectory fields and an `N×3×4` inference-state array. The fixed, unmasked input and transformed starts are prepared before the call. A public-call latency protocol should charge native dispatch and return construction on both sides, including MATLAB `feval` and Python's callable lookup, while placing validation, representation normalization and JSON serialization outside both clocks. The replay checks the active MATLAB paths `_original_models/hgf_binary.m`, `_original_models/ehgf_binary.m` and `perceptual/uhgf_binary.m`. This scope ends at perceptual outputs. [MATLAB wrapper](../../benchmarks/runtime_v1/matlab/forward7_boundary_matlab_untimed.m) · [HGFX wrapper](../../benchmarks/runtime_v1/forward7_boundary_hgfx_untimed.py)

Before scientific signoff:

1. Independently inspect both originals. Verify ZIP and members and review all seven field reports for shapes, finite counts, special-value positions and discrepancies under `abs(HGFX − MATLAB) <= 3e-10 + 3e-8*abs(MATLAB)`.
2. Define expected dimensions and missingness by field from the frozen source. The comparator checks paired shapes and the leading trial axis, with a full dimensional check for inference states. A synthetic probe with both `traj.mu` and inference-state arrays entirely null on both sides classified all seven cases as concordant with zero finite pairs for those arrays. Require finite values on defined cells and preserve legitimate placeholders. This is a prospective checker gap. The synthetic probe says nothing about the contents of the original archives. [Forward comparator](../../benchmarks/runtime_v1/compare_forward7_untimed.py#L104) · [Numerical comparator](../../benchmarks/runtime_v1/compare_trialwise.py#L33)
3. Attest the exact prepared input and transformed parameter binary64 values, resolved perceptual options, masks and actual model/config paths for both engines. Python uses the hexadecimal snapshot and checks resolved priors. MATLAB checks its parsed decimal values against its runtime priors and records the input digest copied from the manifest, with no MATLAB-side config digest in the output. An untimed check of the exact seven calls under the proposed launcher should verify these Level-0 properties before numerical acceptance.

## Prospective CPU and thread contract

The original `BLOCKED_MATLAB_MKL_ENV` remains warranted. The same-host probe reported four allowed logical CPUs and an empty MATLAB `MKL_NUM_THREADS`. The native probe observed `maxNumCompThreads=1` and `omp_get_max_threads=1`, with `mkl_get_max_threads` unresolved. The OpenMP target and process-wide thread total do not identify oneMKL activity during a Forward call. Even the oneMKL API reports the maximum number of threads available to internal regions. [Host attestation](../PERF01C_CPU_HOST_ATTESTATION_UNTIMED_2026-11-08.md) · [MATLAB native probe](../PERF01C_MATLAB_NATIVE_BLAS_INSPECTION_2026-11-08.md) · [Intel reference](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2026-2/mkl-get-max-threads.html)

A prospective protocol can measure **full Forward call wall time under a one-logical-CPU budget**. Select one named dedicated physical Linux host and reserve one logical CPU for both engines, with the SMT sibling idle or disabled. Confine each entire process tree to an enforced Linux cpuset before startup, run the engines sequentially and record effective membership, CPU/ISA/microcode, OS, frequency and contention policy, MATLAB build, NumPy, BLAS and dispatch. Launch MATLAB with `-singleCompThread` and record the observed runtime controls, including any unset environment variables. Set the HGFX BLAS limit before import and verify its runtime metadata. The enforced budget limits simultaneous execution to one logical CPU, while helper or library threads may still time-share it. [MathWorks startup options](https://www.mathworks.com/help/matlab/ref/matlablinux.html) · [Linux cgroup v2 cpuset](https://docs.kernel.org/admin-guide/cgroup-v2.html#cpuset)

**Smallest decisive check** — run the exact seven paired calls once without benchmark timers on the named host. Verify the singleton effective cpuset and record scheduler events covering the complete process tree and call boundaries. Use a separate known multi-thread control to demonstrate detection of a second participating thread. Fail on an escaping task, invalid cpuset, missing trace coverage, or failed parity. Record the observed workers and contention. An assertion of exactly one participating computational worker would additionally need reliable per-thread attribution during those calls. The enforceable one-CPU estimand does not depend on resolving the private MKL symbol.

Before collecting speed data, lock the scientific scope, host evidence, runnable measurement boundaries, runner and analysis hashes, warmups and paired ABBA/BAAB blocks, seed `20261104`, paired bootstrap and the `1.10×` criterion. Report the seven cases individually with denominators and failures. [Timing and statistical candidate](../RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md#L61-L94)

## Local checks and disposition

I ran 33 focused tests from a Git archive of the exact #105 tree with Python 3.14.7 and NumPy 2.5.2, followed by the tracked-ledger check and the synthetic missing-output probe. The focused tests and ledger passed. The initial attempt hit a sandbox temp-directory restriction and an older worktree where LF Git blobs remained materialized as CRLF. The archive used canonical Git bytes and a writable scratch directory. No MATLAB, HGFX model evaluation or performance timing was run during this follow-up.

**Recommendation for Issue #88** — retain `BLOCK_FREEZE` and keep #105 in Draft. Advance the seven Forward cases to a separately versioned protocol candidate. Complete the direct raw-field review and the dedicated-host validation before independent approval and any performance timing.
