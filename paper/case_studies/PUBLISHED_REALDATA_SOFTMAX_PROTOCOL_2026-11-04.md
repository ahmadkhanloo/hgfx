# Prospective real-data softmax likelihood parity — 2026-11-04

**Status at protocol freeze: NOT RUN.** This protocol is a follow-on to the 324-block fixed-parameter perceptual-forward parity on published behavioral inputs. It is **not** a replication of the participant studies' published fitted parameters, behavioral associations or inferential claims.

## Exact sources and scope

- Suthaharan et al. (2021), DOI 10.1038/s41562-021-01176-8, source commit `psuthaharan/covid19paranoia@c618e032228fb4ed03821f11bdc57af608695631`, `data/hgfPRL/pandemic_prelockdown_TP117_TP261_130.mat`, SHA-256 `9c3e81cc4533b49dfa993f1f885678f1a541dd2f31d6738e6e845bb2e7834428`.
- Reed et al. (2020), DOI 10.7554/eLife.56345, source commit `ModelDBRepository/258631@39ccaca508b81ca610e7666a613e061c801faaf9`, `IRL_Data.mat`, SHA-256 `b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708`.
- Reuse the prospectively corrected v2 full-source enumeration: 130 Suthaharan people × 2 original 80-trial blocks, plus 32 Reed people × 2 blocks = **324 blocks / 25,920 trials**. This is a source-defined set, not the original published eligibility/exclusion set. All cases, missingness, invalid values, errors and warnings remain in the denominator.
- Inputs, outcomes and choices are read directly from the files above using `prepare_fullcohort_pair.py`; original 0/1 reward and 1/2/3 choice coding, original trial order. No subjects or trials are selected by downstream numerical agreement. The originally failed 326-case schema hypothesis remains historical evidence.

## Matched analysis

A. Original published-study environment: **NOT REPRODUCED**; original older HGF release, original fitting priors, optimizer restarts, response-model semantics and published conclusions have not been established.
B. Frozen MATLAB HGF Toolbox 8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, physical MATLAB R2025b on GitHub Actions.
C. Frozen released `hgfx==1.0.0` wheel, CPU float64, JAX x64, in a separately installed Python environment.

For each source-defined case, B/C run *the same fixed-vector* `hgf_ar1_binary_mab` forward implementation, three arms, uncoupled, regular intervals. Native perceptual vector (unchanged from the frozen M12B test):
`[NaN, 0, 1, NaN, 0.1, 1, NaN, 0, 0.2, NaN, 0, 1, 1, 1, NaN, -2, -6]`.
Then B/C run the frozen built-in multinomial `softmax` observation on *predicted* level-one beliefs (`predorpost=1`), with a **single, fixed transformed response parameter** `log(beta)=0`, hence native `beta=1`; do not fit this value, tune parameters or assert it is the historical papers' fitted response model. Exclude irregular/missing response or outcome indices consistently using MATLAB's one-based `r.irr` and Python's zero-based `irregular_trials`. Do not remove trials from forward processing.

## Predeclared gate (inherited, not tuned)

Use M7 existing frozen `softmax` observation gate from `tools/check_m7_parity.py` and `docs/planning/M7_GATE.md`: **rtol=2e-11; atol=2e-13**. Compare all regular-trial `logp`, chosen-choice `yhat`, and `res` elements, and per-block total regular-trial log-likelihood. Require identical shape and positions/values of NaN and +/-infinity; accept only if **every one of 324 cases** passes each of the four quantities. No threshold adjustment after results; each failure is retained with its earliest mismatching trial/quantity. Raw values are **not** uploaded. Report per-case failed-field/first-index statuses and aggregate max errors, numbers of elements, exclusions, failed cases and warnings. If a value lacks valid predeclared scope, mark descriptive rather than PASS.

The older 324-case forward-parity run is independent frozen evidence; this experiment neither overwrites it nor upgrades the historical model-recovery failure or published-study replication gate.

## Execution and safety

Use exactly pinned public study MATs with SHA checks. On an ephemeral runner, use actual `matlab-actions/setup-matlab@v3` + `run-command@v3`, pinned HGF submodule, and separately `hgfx==1.0.0`. Keep the source data, per-trial inference and MATLAB result MATs in an untracked temporary directory; upload aggregate JSON status only, never raw participant values or trajectories. Preserve every exception, warning type/count, and failed case. Report physical MATLAB runtime and Python/JAX device versions, Git SHA and action run ID. This is an O11 response-layer compatibility test, not a claim of general statistical equivalence or greater predictive accuracy.

If execution fails, retain failed CI evidence and diagnose mismatch; do not shrink the cohort, change the data/model, suppress warnings or relax the threshold to pass. A successful numerical gate is labelled **PASS_BOUNDED_FIXED_VECTOR_RESPONSE_PARITY**, never **PUBLISHED_PAPER_REPLICATED**.
