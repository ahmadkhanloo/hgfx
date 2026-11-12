# Prospective real-data forward-parity protocol — two published studies

**Established 2026-11-04 BEFORE ANY MODEL EXECUTION.**
This is a bounded *published-input, matched-model numerical compatibility* investigation, **NOT** a full replication of published parameter fits, clinical findings, or group-level model comparison.

## Source and reason for objective fallback selection

Public-source access checks at [workflow 41807813892](https://github.com/ahmadkhanloo/hgfx/actions/runs/41807813892) found Oberwelland OSF 410 and Gao OSF 401. Pain and SPIRL were already BLOCKED for documented scientific/rights reasons. Two independent published datasets, subsequently screened for structural accessibility in [workflow 41808176346](https://github.com/ahmadkhanloo/hgfx/actions/runs/41808176346), are therefore advanced before inspecting any HGFX–MATLAB comparison outcomes. Their origin and older HGF versions remain explicit.

- **Suthaharan et al. 2021**, DOI 10.1038/s41562-021-01176-8; source `psuthaharan/covid19paranoia@c618e032228fb4ed03821f11bdc57af608695631`, `data/hgfPRL/pandemic_prelockdown_TP117_TP261_130.mat`, SHA256 `9c3e81cc4533b49dfa993f1f885678f1a541dd2f31d6738e6e845bb2e7834428`, 130 subject records, 80 trials per block.
- **Reed et al. 2020**, DOI 10.7554/eLife.56345; source `ModelDBRepository/258631@39ccaca508b81ca610e7666a613e061c801faaf9`, `IRL_Data.mat`, SHA256 `b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708`, 33 subject prefixes, 80-trial condition halves and 160-trial combined records.

The source schema was accessed with real downloads. This DOES NOT establish identical tasks, HGF priors, fitted parameters or response-model semantics. Both published analyses used older HGF/TAPAS releases. Original version A is not executable/pinned from the selected sources, so only compare **B** frozen MATLAB 8.2.0 to **C** released HGFX 1.0.0 in the common perceptual-forward family. Do not label B/C outcomes an exact replication of those journal results. Native vector is deliberately drawn verbatim from the pre-existing M12B MATLAB fixture.

## First non-cherry-picked bounded pilot — fixed before results

Use the lexicographically first available subject and first numbered split in each source:
- Suthaharan `TP117_V3_outcomes_1` and `TP117_V3_choices_1`: 80 trials.
- Reed `P01_outcomes_804020` and `P01_choices_804020`: 80 trials.

No cohort/subject substitution because of a failed result. Preserve each complete 80-trial sequence. Accept ONLY original outcome coding {0,1}, choice coding {1,2,3} plus NaN for missing observations, as those are the 8.2.0 model's native domains. Any other encoding yields **BLOCKED_DATA_CODING_UNRESOLVED** and no model run; no inferred recoding from desired result. Missing input or choice indexes remain `r.ign` / HGFX `ignored_trials` without removing rows. This pilot does not prove original paper used precisely these transformations or participant exclusions.

**Model:** frozen HGF `hgf_ar1_binary_mab`, `n_bandits=3`, `coupled=false`, `irregular_intervals=false`. Do not substitute regular HGF, RW, eHGF or remove response covariates to claim full paper replication.

**Fixed native perceptual vector (17 elements):**
`[NaN, 0, 1, NaN, 0.1, 1, NaN, 0, 0.2, NaN, 0, 1, 1, 1, NaN, -2, -6]`.
This is the exact existing `p_hgf` in `tools/check_m12bc_parity.py` / `reference/matlab/export_m12bc_parity.m`. It is NOT the published fitted parameters.

**Executions:** MATLAB release via physically executed public `matlab-actions/setup-matlab@v3`, pinned HGF 8.2.0 submodule at `2437f4dc241541072722a2695ddeca7b44d83dd3`; Python HGFX **installed stable PyPI 1.0.0** (not working-tree editable install), NumPy/JAX CPU float64, matched input/choice masks and model vector.

**Comparison**: every overlapping trial-by-trial trajectory field and `infStates` vector, shape and finite/nonfinite masks; earliest divergent zero-based index plus 1-based trial/level (where relevant), absolute and relative maximum differences. The numeric comparison gate on this exact frozen family is inherited unchanged from `tools/check_m12bc_parity.py`, **rtol 2e-9, atol 2e-11**, `equal_nan=True` across all comparable elements, and match infinities only if same sign. No adjustments after inspecting results. A new data/shape mapping defect remains a **FAIL/diagnosis**, not an invitation to relax criteria. Missing fields/partial comparable domains must be explicitly reported and cannot be declared complete PASS.

**Metrics absent here**: no study-response likelihood, fitting convergence, model selection, clinical associations, inferential parameter recovery, prediction generalization or speedup. Forward parity alone does NOT establish that HGFX performed better in either paper.

**Privacy/reproducibility:** source files remain downloaded only on ephemeral GitHub runner; verify SHA256; do not upload participant-level values, raw trajectories or downloaded MATs. Upload aggregate comparison summaries, source SHA, environment and full error codes. Retain failures and warnings. If pilot succeeds, a distinct prospectively locked full-cohort protocol is required before claiming all-subject coverage; no sampling based on agreement. All historical 75 protected artifacts remain unchanged.

**Current gate at writing:** protocol frozen; pilot NOT RUN; two published-paper replication studies NOT COMPLETE. Manuscript revision withheld pending results and author review.
