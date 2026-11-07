# PERF-01C author-side timed-boundary audit (NOT approved/frozen)

Date: 2026-11-04  
Status: **AUTHOR-SIDE METHODS REVIEW / OPEN QUESTIONS / NO TIMING EXECUTED**  
Primary protocol: [RUNTIME_PERFORMANCE_PROTOCOL_V1.md](RUNTIME_PERFORMANCE_PROTOCOL_V1.md)  
Eligibility evidence: [28-case candidate manifest](../../benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json)  
Independent review tracking: [#88](https://github.com/ahmadkhanloo/hgfx/issues/88)

This audit describes the existing code. It does **not** freeze any performance claim, independently sign off the review, or propose replacing blocked workloads with a successful post-hoc dataset.

## Timed scientific boundary candidates

| Measured stage | MATLAB 8.2.0 candidate | HGFX 1.0.0 candidate | Audit decision before timing |
|---|---|---|---|
| Forward | Frozen `hgf_binary(r,p,'trans')` / corresponding `ehgf_binary` or `uhgf_binary`, returning `traj` and `infStates` | `hgfx.models.{hgf_binary,ehgf_binary,uhgf_binary}(u,p,transformed=True)` with the matching mask | **Candidate only**: source identity, model path resolution and exact trial output gate must be confirmed. Construct `r`, `u`, `p` outside timer in both. No unstable HGF 512/1024 trial is eligible. |
| Fixed objective | Scripted reference `[~,states]=model(r,p_prc,'trans'); logp=unitsq_sgm(r,states,p_obs);` plus the frozen `negLogJoint` prior and reduction semantics | `hgfx.compat.objective.evaluate_objective(...)`, whose core invokes the same model+observation+prior terms | **Candidate, not identical public API**. MATLAB's exact `negLogJoint` is a nested/private function in `fitModel.m`; the independently reviewed custom MATLAB composition is required. Confirm full returned/scored fields and equivalent inclusion of reference-function orchestration in the timed region before approving. |
| Complete compatibility fitting | MATLAB `fitModel(y,u,'hgf_binary_config','unitsq_sgm_config','quasinewton_optim_config')` including optimization, Hessian/LME and result display | HGFX `fit_model(y,u,'hgf_binary_config','unitsq_sgm_config','quasinewton_optim_config')` including optimization, Hessian/LME and result construction | **Candidate only on the 128-trial default-start case**, whose full outputs were diagnostically concordant. Unchanged HGF 512/1024 have invalid default starts, and the APIs differ materially in implicit start recovery; classify them `NOT_DIRECTLY_COMPARABLE` rather than timing success vs exception. |
| Serial throughput | Loop of exact full MATLAB `fitModel` calls for every subject with all failures accounted | Loop of exact full HGFX `fit_model` calls, including all final fit statistics | **Not yet scientifically gated for 16/64 subjects.** Cohort preflight proves fixed-vector objectives only, not per-subject fitting. 512-trial HGF batch is invalid at every frozen start, and may not be silently reduced to successes. |
| JAX fast CPU/GPU batch | MATLAB full workflow on CPU | HGFX fast fitting on JAX CPU/GPU | **Different optimizer and hardware execution.** Must remain an explicitly separate exploratory completed-workflow comparison. Numerical output/selection/failure equivalence, x64, synchronized residency and postprocessing contracts are not currently established. |

## MATLAB-specific runtime side effects — explicit blocker

The immutable MATLAB HGF `core/fitModel.m` prints parameter estimates, quality measures and other output unconditionally at the end of a successful fit. HGFX `fit_model` does not print the same text.

An unqualified stopwatch around both functions will therefore include **different stdout/I/O work**. Possible reporting designs, to be **decided prospectively by an independent reviewer**, include:

1. A literal **end-user end-to-end call** that retains each library's actual console output and labels the difference; it is a workflow comparison, not an algorithm-only CPU performance claim.
2. A distinct **output-suppressed computation** study, after evaluating MATLAB `evalc` buffering overhead and any HGFX-equivalent result materialization. Neither side may silently bypass Hessian/LME or other returned results.

The choice must be fixed **before** any timing; do not choose a reporting convention after observing speeds. `maxNumCompThreads(1)` by itself is not proof that all MATLAB/BLAS/background threads and CPU affinity are identical.

## Startpoint contract, exact reference behavior

MATLAB's frozen `fitModel.m` contains an implicit loop that resamples unstable optimization starts from the prior distribution up to 1000 times. `nRandInit=0` controls *extra random full optimizations* after a valid start, **not** this initialization recovery loop. HGFX 1.0.0's compatibility `fit_model` rejects an invalid default start rather than executing the same implicit recovery policy.

Consequently the two products are comparable for the predeclared, confirmed-stable 128-trial full fit only (subject zero, with a documented full-output diagnostic). Do not reinterpret random MATLAB restarts as a valid 512/1024 matched fit or count a failed HGFX call as a completed fit.

## Whole-cohort scientific denominators

MATLAB R2026a / frozen HGF 8.2.0 and HGFX 1.0.0 were executed, without timers, on the same GitHub-hosted CPU job for all **576 = 64 subjects × 3 horizons × 3 models**, preserving the original data and 27 nested prefix strata.

- **448** matched, successful forward/objective scalar pairs under existing diagnostic criteria;
- **128** matching invalid standard-HGF pairs: exactly the 64 subjects at each of 512 and 1024 trials;
- **0** source-config, validity-class or objective-tolerance discrepancies in this particular probe.
- Maximum recorded absolute negative-log-joint discrepancy on completed cells: **1.6370904631912708e-11**, for uHGF 1024, subject index 21 (zero-based).

Workflow [41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774) completed and archived its evidence. The earlier attempt [41859496548](https://github.com/ahmadkhanloo/hgfx/actions/runs/41859496548) performed the same calculations successfully but failed the *evidence commit push* because the branch moved; this separate failed-run record is preserved. Raw traces are kept as workflow artifacts with SHA-256 links from `benchmarks/runtime_v1/cohort_results/summary-41860187774.json`.

**Evidence scope:** fixed-vector scalar concordance for all subjects is not equivalent to trialwise trajectory parity on every individual subject, and it is **not** per-subject optimizer fitting parity. The preceding 10-case trialwise and one-case full-fitting diagnostics remain separate, narrower evidence.

## Prior nine-primary-cell summary cannot satisfy its own gate

The preregistered nine-primary-cell summary requires *all nine* eligible cells, an equal-weighted geometric mean of speed ratios and its original confidence criteria. Because six primary cases are invalid or fitting-noncomparable, that headline cannot pass under the frozen dataset and starts. The result is not a justification for relaxing inclusion, substituting eHGF/uHGF as if they were original primary HGF, suppressing failures or revising thresholds after seeing results.

The already-preregistered **12 secondary eHGF/uHGF forward/objective cases** and the three 128-trial primary cells may be evaluated for **scoped** performance only after prospective review and protocol freeze. Even there, a positive speed outcome is **not assumed**.

## What remains before PERF-01C freeze

- Independent reviewer signature, source path/hashes, raw-artifact audit and precise scientific tolerance/eligibility approval; author-side records are not independent verdicts.
- CPU **same-host** deployment details: CPU model, pinning, thread counts, BLAS/OpenMP/MKL policies, MATLAB and Python process lifecycle, power/turbo and multi-tenant contention. Existing shared GitHub runner was used for correctness diagnostics, not a controlled performance host.
- A mutually accepted computational boundary for forward, objective and complete fitting, including MATLAB printouts and exact objective code.
- A versioned immutable runner, seed, workload, acceptance-policy and statistical-analysis lock. No final performance run or public speed claim before the lock.
- GPU physical-device evidence, transfer/block-until-ready accounting and optimizer/output comparability are separate from CPU.

No historical frozen v1 release, reference evidence, benchmark result or paper protocol was altered by this author-side audit.
