# REV-2.2 / D08 — read-only historical BFGS and matched-endpoint trajectory audit (2026-11-11)

**VERIFIED, REPRODUCED FROM IMMUTABLE ARCHIVES:** real original 614-input official D08 same-parameter `uhgf + gaussian_obs` trajectories remain **within existing M18 per-element numerical yardstick for all 12 trajectory fields** in both previously archived released-HGFX runs. The original **different-own-fitted-endpoint direct comparison still FAILS** (Run A 4/1228, Run B 3/1228 `traj.epsi` violations). This **does not establish causal first BFGS divergence or scientific family-wide PASS**. Current scientific decision: `UNRESOLVED_DISCREPANCY`.

## Executed audit, original evidence and provenance

- [Predeclared source-only protocol](../../evidence/revision/protocols/REV-2.2_D08_THREE_ARCHIVE_READONLY_PROTOCOL_2026-11-11.md) committed `b69364de6073c7dc337d4f18f8e92eb81a8f70b7` **before audit**; [code](../../tools/compstat_rev22_d08_three_archive_readonly.py), [nine synthetic-only tests](../../tests/paper/test_rev22_d08_three_archive_readonly.py).
- [Real GitHub Actions **42986788313**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42986788313), execution commit `7699100ce8cfc78c4952cc38390fc42df26eeed5`: **SUCCESS**, 9/9 synthetic tests, three original archive SHA-256 checks and *every* original JSON member SHA-256 verified. No MATLAB, HGFX, JAX, forward evaluation, Ridders, optimization, GPU or new fit run. Uploaded [derived-only artifact **13840375598**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42986788313/artifacts/13840375598): ZIP SHA-256 `23fabb75ffe6ea0587b013379af393815bbf1483dd9b43f00f124cbaee728e49`, `rev22_d08_three_archive_readonly_result.json` SHA-256 `79b5475f360fe0c23d451ad3a5519d83d2b31db5084047d48625f923392166ac`. The derived artifact contains no 614 raw inputs/responses.
- Frozen historical [M18 official D08 endpoint artifact `10339403480`](https://github.com/ahmadkhanloo/hgfx/actions/artifacts/10339403480) ZIP SHA-256 `c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de`. Both original concurrent REV-2.2 source archives remain [A `13808150860`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910756224/artifacts/13808150860) ZIP SHA `a2864f8729d9e856eb3454cf1fbf4c26c08cd217695e58b79950cec2ac5b3534`, [B `13808625206`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42910835710/artifacts/13808625206) ZIP SHA `ea577dc80b2194d1658eeb8c296a021f51332199be0ea7d4924608fe12891132`. Both have the **same byte-identical MATLAB original JSON SHA** `5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165`.

## Historical trace provenance — important but limited

Original M18 official D08 MATLAB source used **R2026a Update 5**; new A/B used **R2026b Update 1**. For the **same original seed `123456789` and 614 actual MATLAB-generated response values**, the audit verified binary64 exact equality of:

- all 614 input and simulated response elements;
- final MATLAB fitted transformed parameter vector;
- **full 101 × 7 MATLAB optimizer `iter.x`**, length-101 `iter.val`, and `iter.rst=[2,19,29,38]`.

Thus MATLAB's *archived* output is stable across these two versions **for this exact input/model/workflow**, without claiming general version equivalence. The original historical M18 comparator reports earliest **exact** HGFX vs MATLAB optimizer `iter.x` difference at **(zero-based row 3, free component 0)**, MATLAB `0.9713770115938081`, HGFX `0.9713770115938116`, abs difference **`3.552713678800501e-15`**; its original gate-level optimizer-x divergence is **none**, as is its optimizer reset mismatch. This fact comes from the SHA-verified historical comparator, not from a new recreation of the historical HGFX optimizer trace.

**Crucial evidence boundary:** Neither new published-Wheel HGFX run A nor B serializes stepwise `iter.x/iter.val/iter.invH` or Ridders intermediate decisions; both explicitly report `termination=NOT_EXPORTED`. Therefore the current archived new runs **cannot establish the exact first BFGS/gradient/Armijo decision**. The older original comparator's row-3 exact difference is not proof of the causal mechanism for Run A/B.

## Same-frozen-vector trajectory check on previously recorded HGFX endpoints

Using each run's **actual frozen HGFX fitted final parameter vector**, the original MATLAB `matlab_cross_evaluation.json / matlab_cross_endpoints.json` had already generated complete trajectories **at that same exact vector**, without re-fitting. This audit compares those *already recorded* MATLAB-at-HGFX-endpoint arrays with released-HGFX-at-own-endpoint arrays. **Every one of the 12 named trajectories was checked with unchanged M18 `rtol=3e-8, atol=3e-10` as a descriptive numeric yardstick, NOT a newly authorised scientific uHGF family gate.** MATLAB's source `w` has a (614,1) presentation while HGFX is (614,) and was safely flattened only for equal-sized 1D/column arrays; no outer broadcasting or coordinate omission.

| Trajectory | Run A same-vector max abs gap | Run B same-vector max abs gap | Out of numeric yardstick, A/B |
| --- | ---: | ---: | --- |
| `mu`, `muhat` | `7.605e-15` | `6.661e-16` | 0 / 0 |
| `sa`, `sahat` | `1.332e-15` | `6.661e-16` | 0 / 0 |
| `v` | `4.320e-20` | `2.711e-20` | 0 / 0 |
| `w` | `9.992e-16` | `4.441e-16` | 0 / 0 |
| `da` | `3.264e-14` | `6.661e-16` | 0 / 0 |
| `dau` | `1.110e-16` | `0` | 0 / 0 |
| `ud` | `4.885e-15` | `2.220e-16` | 0 / 0 |
| `psi` | `1.965e-10` | `2.183e-11` | 0 / 0 |
| `epsi` | **`1.382431946694851e-09`** | **`3.2741809263825417e-11`** | **0 / 0** |
| `wt` | `6.661e-16` | `2.220e-16` | 0 / 0 |

Every aligned pair also has **zero IEEE nonfinite-status disagreements**. Source/size/field names were verified for the **complete 12-field set**, not selected according to goodness-of-fit.

### The original different-endpoint failures remain

Run A and B **separately fit the same response vector** and ended at slightly different HGFX fitted transformed parameters (maximum A/B param difference `5.716338513650498e-10`). Those exact parameter vectors are each different from MATLAB's **own fitted final vector**. As originally recorded:

- Run A own-fit original MATLAB-vs-HGFX `traj.epsi` **4/1228** numeric failures at zero-based trials `178,322,412,577`, level index `1`.
- Run B own-fit original MATLAB-vs-HGFX `traj.epsi` **3/1228** failures at trials `178,412,577`, level index `1`.
- First original failed entry `(178,1)`, MATLAB at MATLAB own endpoint `-4.788757533201755` vs HGFX A at HGFX own endpoint `-4.788755010867239` and B `-4.788756086232761`.
- When MATLAB is re-evaluated **at the corresponding HGFX endpoint**, the same failed entry matches HGFX at that endpoint in both original archives to the exported precision (at trial 178, level 1, **zero** observed difference).

**Interpretation:** Original same-vector trajectories, along with near-exact same-vector NLL/NLJ totals, **support endpoint/path sensitivity as the dominant observed difference** rather than an obvious forward semantic defect at the checked vectors. The **first causal numerical BFGS decision is NOT PROVEN** and cannot be extracted from outputs that do not record the new HGFX intermediate trajectory. A small endpoint change and sensitive derived epsi can produce failures under a strict direct trajectory gate even when the fixed-vector forward is consistent. This observation is *not* evidence of global optimizer optimality or model identifiability.

## Scientific decision and requested independent next gate

- **DONE / SOURCE-VERIFIED:** all original artifact/member hashes, historical MATLAB 101×7 trace exact across versions, both actual A/B same-parameter 12-trajectory comparisons within the existing numerical yardstick.
- **STILL FAIL:** direct original own-fit `traj.epsi` gate 4-vs-3, historical M18 official D08 FAIL, original separate failed holdout. Concurrent two-run deviation remains recorded; neither run is selected/discarded.
- **OPEN:** earliest actual A/B Ridders sample/gradient/Armijo/BFGS decision, full Ridders warning inventory and credible optimizer numerical-cause attribution. **No third D08 fit under this consumed one-shot protocol**; if necessary, a separately preregistered and independently reviewed scientific protocol must be authorised before new model work, and must preserve failed historical evidence.
- **Original manuscript/release status unchanged:** REV-2.2 `IN_PROGRESS / UNRESOLVED_DISCREPANCY`; REV-2.1 `BLOCKED` [#110](https://github.com/ahmadkhanloo/hgfx/issues/110); REV-2.4 global `NOT_GLOBAL_PASS`, human eHGF-019 review [#109](https://github.com/ahmadkhanloo/hgfx/issues/109), D2/D3 `BLOCKED`, full CPU `NOT_PASS`.

This report gives a *new, bounded, read-only diagnostic conclusion*, not a change to any preregistered numerical/scientific gate or historical result.
