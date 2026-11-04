# Prospective original-family softmax_mu3 likelihood test — 2026-11-04

**Status at protocol freeze: NOT RUN.** This is a distinct, predefined comparison from the successfully executed fixed-temperature softmax protocol and run #41811411017. Neither that run nor this protocol reproduces original papers' model fits.

## Original-paper source evidence

Suthaharan et al. (2021), DOI 10.1038/s41562-021-01176-8, describe the 3-level autoregressive multi-armed bandit HGF paired with a *softmax-mu03* decision model: https://pmc.ncbi.nlm.nih.gov/articles/PMC7814833/. Reed et al. (2020), DOI 10.7554/eLife.56345, describe a third-level-volatility-dependent softmax decision model: https://pmc.ncbi.nlm.nih.gov/articles/PMC7326495/. Exact historical source, fitting parameters, priors and optimization restarts remain unresolved. This experiment uses the **same mathematical response family** in frozen MATLAB 8.2.0 and HGFX 1.0.0 but does **not** fit participant-specific parameters.

## Scope and strictly frozen controls

- The pre-existing 324-case cohort: Suthaharan source-derived 260 80-trial blocks and Reed source-derived 64 80-trial blocks, 25,920 trials. See PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_V2_2026-11-04.md for pinned raw source hashes and the preserved failed 326-case hypothesis.
- Same three-arm, uncoupled, regular-interval `hgf_ar1_binary_mab` perceptual model and exact M12B preselected native vector `[NaN,0,1,NaN,.1,1,NaN,0,.2,NaN,0,1,1,1,NaN,-2,-6]`. No participant fit, changed data, seed or pruning.
- B: physically executed frozen MATLAB8.2 `softmax_mu3`, default `predorpost=1` (predicted level-one states), `r.irr = isnan(outcome) | isnan(choice)`. C: stable released `hgfx==1.0.0` `hgfx.responses.softmax_mu3` with identical `infStates` construction and zero-based irregular masks. No beta parameter exists in this response model; trial-wise effective decision temperature is derived from the level-three latent state.
- Original historical A: HGF5.3.1 and source-specific fit settings **NOT REPRODUCED**; the 8.2/1.0 comparison is a new ported compatibility experiment.

## Frozen numerical acceptance

Inherit **without change** the M7 softmax_mu3/observation numerical gate `rtol=2e-11, atol=2e-13` (tools/check_m7_parity.py). Independently compare all trial-wise `logp`, chosen-choice `yhat`, residual `res`, and block total finite regular-trial log-likelihood. NaN/nonfinite masks and shape must match exactly. Declare `PASS_BOUNDED_MU3_RESPONSE_PARITY` only if all 324 cases and all four quantities pass, preserving failures and first mismatching trial otherwise. No tuning or threshold changes after results.

All participant inputs and per-trial states remain in the ephemeral CI working directory and must not be uploaded. Store only bounded aggregate and per-case status/warning counts with reference SHA, wheel version, physical MATLAB/runtime metadata, CI run ID and branch SHA. Record 48-case warnings from the previous standard softmax experiment as separate historical evidence, not predetermined warnings or ignored cases here.

The only permissible interpretation of a PASS is **numerical equality at a fixed vector for a published-study-type observation family on real published inputs**. It is not identical published fitted-parameter results, optimizer parity, predictive accuracy, model identifiability, new GPU evidence or MATLAB speed superiority.
