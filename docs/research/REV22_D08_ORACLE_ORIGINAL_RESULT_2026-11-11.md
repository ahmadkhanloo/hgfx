# COMPSTAT REV-2.2 official D08 USD/CHF paired oracle — original science and concurrent execution audit (2026-11-11)

**Research outcome:** `UNRESOLVED_DISCREPANCY` in both original archived runs, **NOT** direct fit parity; `REV-2.2 IN_PROGRESS`; original M18 D08 direct failure preserved; REV-2.4 `NOT_GLOBAL_PASS`, D2/D3 `BLOCKED`.

**PROTOCOL DEVIATION / NEVER HIDE:** During GitHub source review, a **second independent one-shot workflow had been launched concurrently** on the same development branch, against the **same original official D08 study**, contrary to the intended single-invocation budget. Both kickoff commits were created before either scientific result was available. They were not adaptive retries after seeing a discrepancy; nevertheless **two numeric fitting executions occurred**, not one. **Do not label them as a pre-registered two-replicate design, cherry-pick the better result, merge their denominators, rewrite the original protocol, or run any further models under this scope.** Preserve **both** artifacts and both sets of disagreements.

## Source, input and experimental identity

- Previously preregistered exact [REV-2.2 D08 official protocol](../../evidence/revision/protocols/REV-2.2_D08_USDCHF_ORACLE_PROTOCOL_2026-11-11.md), commit `600c0499cacd57067d6f8e345b485e0d34872322`; [source-only preflight `42910384629`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910384629) success **10/10** contracts, original 334-file MATLAB SHA freeze pass. The extra concurrent branch push was not an author-approved expansion of the sample size.
- Authentic HGF Toolbox **8.2.0**, source SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, exact source `demo/example_usdchf.txt` Git blob `29a4d0322faf8894c414883c517950aa87b481db`, **614 public USD/CHF input values**, simulated Gaussian response seed `123456789`, model `uhgf + gaussian_obs`, native perceptual `[1.04,1,.0001,.1,0,0,1,-13,-2,10000]`, observation variance `.00002`. These responses are **synthetic**, not patient/participant observed values.
- Both used real MATLAB version `26.2.0.3433840 (R2026b) Update 1`, real CPU runtime Linux kernel `7.0.0-1017-azure`, Python `3.11.18`, **NumPy `2.0.2` and JAX `0.10.2`**, and verified published **HGFX 1.0.0** Wheel SHA-256 `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`. One workflow pinned `jax==0.10.2`; the other specified `jax>=0.4.30`, which **resolved to the same `0.10.2`**. No evidence of a JAX-version cause. The exact **MATLAB reference JSON is byte-identical between runs**, SHA-256 `5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165`. Both HGFX runs checked the same original **614 binary64 MATLAB-generated responses**, prior vectors, start vector, model and endpoint ordering.
- Original MATLAB fit was evaluated once **in each independent concurrent workflow**, not twice within one workflow. Both runs then fitted the released Wheel against the exact MATLAB output and re-evaluated both endpoints in MATLAB without a new optimizer call.

## Immutable execution records and source hashes

| | Run A (first launched) | Run B (concurrently launched) |
| --- | --- | --- |
| GitHub Actions | [42910756224](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910756224) | [42910835710](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910835710) |
| Source HEAD | `f127f6066bbc22f00d7fb9f410c317bad0cb431f` | `365cffc0f79f88f61d7c3836bc55a082f391ed69` |
| Workflow | `compstat-rev22-d08-official-science.yml` | `compstat-rev22-d08-science.yml` |
| Workflow conclusion | SUCCESS (execution and postprocessing only) | SUCCESS (execution and postprocessing only) |
| Artifact | [13808150860](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910756224/artifacts/13808150860) | [13808625206](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910835710/artifacts/13808625206) |
| Exact outer ZIP SHA-256 | `a2864f8729d9e856eb3454cf1fbf4c26c08cd217695e58b79950cec2ac5b3534` | `ea577dc80b2194d1658eeb8c296a021f51332199be0ea7d4924608fe12891132` |
| MATLAB original member SHA-256 | `5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165` | **same byte identity** |
| HGFX output member SHA-256 | `d06a2f961a27f73a9c38621a86fe2204aebb481f2857ce45368e176111a9f37d` | `202fb1ab5177d39c6104c9a5004057fc19ae58637e706b0459ea48aa3bc27b13` |
| Original paired comparison SHA-256 | `0304d8366c497d1e03cf9b75da1670a8a2d09e06979c064098cdd4e062595440` | `eb8f598158d057df0c574fd0cd188bed629ff13c7e40fbcde24627daebac5422` |
| Same new scope classification | `UNRESOLVED_DISCREPANCY` | `UNRESOLVED_DISCREPANCY` |

Both one-shot triggers were removed after launch. Their commits remain recorded. No other model run is authorized to select a more favorable realization.

## Actual direct comparison at each own optimum — **preserve both**

The unchanged existing official M18 D08 gate compares numeric values within `rtol=3e-8`, `atol=3e-10` for trajectories/primary scalars; existing special Hessian/LME and Sigma/Corr criteria were left intact. **24/25 directly compared fields satisfy their appropriate old gate in both executions; `traj.epsi` does NOT.** All 1228 epsi slots are finite in both languages (zero nonfinite classification disagreements). Differences are numerical, not NaN/dropout disagreements.

| Observation | Run A | Run B |
| --- | ---: | ---: |
| epsi slots outside old gate | **4 of 1228** | **3 of 1228** |
| First violated trial (zero-based) | 178 | 178 |
| First violated level (zero-based) | 1 | 1 |
| First MATLAB value | `-4.788757533201755` | **same** |
| Corresponding HGFX value | `-4.788755010867239` | `-4.788756086232761` |
| Largest epsi absolute difference (not necessarily outside gate at max point) | `9.533250704407692e-06` | `4.993140464648604e-06` |
| Zero-based bad trial indices (all level 1) | `178, 322, 412, 577` | `178, 412, 577` |
| Largest absolute transformed endpoint difference vs MATLAB | `1.3502421403188691e-09` | differs, see full data |

Raw MATLAB transformed parameter initial vector is **bitwise equal** to both HGFX run initial vectors. Their final fitted HGFX vectors are **not** bitwise identical to each other: max absolute element gap **`5.716338513650498e-10`** at transformed zero-based index 8. Because the original data, frozen source, released Wheel and reported software versions are the same, **run-to-run numerical endpoint variability is observed**; its mechanism (host CPU/BLAS threading, evaluation order, optimizer rounding or other environment/scheduling effects) is **NOT PROVEN**. Do not call it a scientific/model identifiability limitation without independent mechanism evidence.

## Own fitted statistics and same-vector cross-objective result

| Numeric field | MATLAB original official D08 (identical in both) | Released HGFX Run A | Released HGFX Run B |
| --- | ---: | ---: | ---: |
| negLj | -2323.459762013518 | -2323.4597620137324 | -2323.459762013633 |
| negLl | -2474.7536183437173 | -2474.7536183383972 | -2474.7536183406814 |
| LME | 2317.003896399031 | 2317.0038963991306 | 2317.0038963987336 |
| BIC | -4904.567272190405 | -4904.567272179765 | -4904.567272184333 |

- The reported 7×7 Hessians from authentic MATLAB and both HGFX runs are finite **positive definite** at their respective endpoints, with 2-norm condition numbers approximately **`88962.50563`** (MATLAB), **`88962.50565`** (A), and **`88962.50557`** (B). These are reported Hessians; the condition number is descriptive, not an identifiability proof.
- MATLAB self-objective replay at its authentic original endpoint reproduces `negLl/negLj` **exactly** in both runs, supporting that the cross-evaluator uses the correct frozen original objective.
- Both implementations' negative log-likelihood and negative log-joint totals when evaluated at the **same fixed MATLAB endpoint** agree **exactly at the JSON-reported precision**, in both runs.
- At the **HGFX Run A endpoint**, same-vector totals also agree exactly as exported; at the **Run B endpoint** the reported same-vector `negLj` and `negLl` gaps are only **`4.547473508864641e-13`** each. Per-trial likelihood terms are not generally bitwise equal. Importantly, **there is no preregistered uHGF family objective tolerance**, so do not promote these same-vector observations to a family PASS or "same optimum reached."
- This pattern is **consistent with numerical optimizer-path or endpoint sensitivity** rather than a gross fixed-vector model mismatch, but it does **not independently localize the first BFGS gradient/step decision**. The full optimizer path remains `NOT_ASSESSED` under this new protocol; further reference evidence/human scientific review is needed for a causal attribution.

## Missing evidence and remaining gates

- Frozen MATLAB and published Wheel v1.0.0 **do not expose** the new development-only `fitModel().optim.converged` field; record termination `NOT_EXPORTED`, not success inferred from objective closeness. Ridders warning counting/categorization still **`WARNING_COVERAGE_INCOMPLETE`**; MATLAB `lastwarn` recorded an empty last-warning message but is NOT an exhaustive warning audit. No additional Ridders settings were tried.
- The original official M18 D08 failure **remains FAIL**, its separate holdout at seed `314159265` also remains historically FAIL, and prior limited `REFERENCE_LIMITATION_MATCH` is only for the exact documented historical scope. This new two-run concurrent observation is *not* permission to enlarge the limitation to arbitrary uHGF fitting.
- REV-2.1 pre-experiment source design [#110](https://github.com/ahmadkhanloo/hgfx/issues/110) remains BLOCKED; the original eHGF-019 `np.fmax` development-only patch lacks human source review; REV-2.4 global scientific parity `NOT_GLOBAL_PASS`; full Linux/Windows historical CPU suite `NOT_PASS`; original 63/64, M18/P3/PERF-01C and D02 missing original endpoint remain. **D2/D3 BLOCKED**.

## Read-only independent evidence check

An additional **NO SCIENCE** independent audit of *Run A's original ZIP* [Actions `42912304642`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42912304642) succeeded: verified whole ZIP/member hashes, source/response IEEE identities, all 25 direct fields and exactly four epsi violations, matched endpoints and unchanged global gate. Audit source `tools/compstat_rev22_d08_archive_audit.py`; artifact [`13807393065`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42912304642/artifacts/13807393065). Local read-only inspection of **both** downloaded source ZIPs reproduced each run's finite epsi violation indices, original MATLAB reference byte identity and published Wheel/Python runtime.

**Final recorded status: `REV-2.2 FIT_COMPARISON_DONE_WITH_UNRESOLVED_DISCREPANCY`, `RIDDERS_WARNING_AUDIT_OPEN`, `BFGS_FIRST_CAUSAL_DIFFERENCE_NOT_ESTABLISHED`, `CONCURRENT_DUPLICATE_RUN_PROTOCOL_DEVIATION`. No scientific PASS and no data/threshold/result suppression.**
