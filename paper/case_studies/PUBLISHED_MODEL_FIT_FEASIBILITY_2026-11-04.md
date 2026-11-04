# Published-study full fitting gate: source-grounded feasibility audit (2026-11-04)

**Status: BOTH ORIGINAL-PAPER FIT REPLICATIONS BLOCKED; fixed-vector MATLAB8.2/HGFX1.0 forward parity independently PASS in the documented 324-block scope.** The observation-layer extension [is prospectively defined separately](PUBLISHED_REALDATA_SOFTMAX_PROTOCOL_2026-11-04.md); no result from that run is assumed here.

## Suthaharan et al. 2021 (Nature Human Behaviour)

- Paper DOI: https://doi.org/10.1038/s41562-021-01176-8; peer-reviewed Methods on https://pmc.ncbi.nlm.nih.gov/articles/PMC8458246/ and related manuscript https://pmc.ncbi.nlm.nih.gov/articles/PMC7814833/.
- Source pin: https://github.com/psuthaharan/covid19paranoia/tree/c618e032228fb4ed03821f11bdc57af608695631. Code files `code/hgf/tapas_hgf_ar1_binary_mab_config_1.m` and `_2.m` are present; behavioral input MATs include the prelockdown dataset used for the forward demonstration.
- **Published analysis actually specifies** a three-level autoregressive HGF multi-armed-bandit perceptual model paired with a **softmax-mu03 (third-level-volatility dependent) decision model**, not a fixed-temperature ordinary `softmax`. It fits participant-specific parameters separately for task halves. Treat the new generic fixed-temperature softmax comparison strictly as an *additional different observation-family compatibility check*.
- Original toolbox: TAPAS HGF **5.3.1**, MATLAB/Statistics Toolbox R2016a per paper and source README. This is not the HGF **8.2.0** port oracle; numerical equality across those historical versions has not been established.
- Source config 1 prescribes three arms, `coupled=false`, `irregular_intervals=false`, priors over `mu_0`, `logsa_0`, `logitphi`, `m`, `logka`, `om`; source config 2 uses undefined workspace variables `mu02`, `mu03` as prior means from an earlier half's fitted values, so the sequential fit chain must be recovered rather than guessing these values. Record original subject exclusions and optimizer settings before any participant fit.
- **Status:** `BLOCKED_ORIGINAL_VERSION_AND_FIT_CHAIN`. The newer MATLAB8.2 model-family forward parity is valid in its frozen scope, not a reproduced paper fit. HGFX 1.0.0 lacks a complete public MAB + softmax_mu3 `fit_model` dispatch, although the raw forward and response functions exist and have separate component golden evidence.

## Reed et al. 2020 (eLife)

- DOI https://doi.org/10.7554/eLife.56345; full text https://pmc.ncbi.nlm.nih.gov/articles/PMC7326495/; source/data mirror https://github.com/ModelDBRepository/258631/tree/39ccaca508b81ca610e7666a613e061c801faaf9.
- ModelDB repository contains `IRL_Data.mat`, `MTurk_Data.mat`, rat data and spreadsheets; it does **not** contain a full versioned per-participant original MATLAB inversion pipeline or model-prior configuration. Paper uses HGF **5.3.1** with a third-level-volatility-dependent softmax model; exact historical response semantics, starts, priors, coding and original eligibility must be frozen before scientific reproduction.
- Earlier source-cohort audit established 32 genuine person prefixes and two 80-trial halves each in `IRL_Data.mat`; misleading variable `ans` is not a 33rd participant. These 64 blocks form only the source-derived parity demonstration, not a claim about the article's full original analyzed population.
- **Status:** `BLOCKED_ORIGINAL_SCRIPT_CONFIG_AND_FIT_CHAIN`; numerical MATLAB8.2/HGFX1.0 fixed-vector forward evidence remains separately valid.

## Additional candidate screening

- **Oberwelland et al. 2021**, DOI https://doi.org/10.3389/fnins.2020.536596, code https://github.com/msrlab/reversal_learning_behav. The actual original `run_analysis.m` fits RW plus two HGF variants with custom perceptual priors and binary softmax across three task conditions per participant, using TAPAS **2.0.0.1 / HGF4.0**. Requires data from OSF https://osf.io/3xrn2/; previous source-availability screen recorded HTTP 410. The code's custom config filename `tapas_hgf_binary_config_custom.m` declares `function c = tapas_hgf_binary_config` and uses a historical theta convention; exact function dispatch and semantics require independent mapping. **Status: BLOCKED_DATA_ACQUISITION_AND_HISTORICAL_SEMANTICS**, not a verified simpler immediate replacement.
- **Gao et al. 2024**, DOI https://doi.org/10.1186/s40359-024-01952-x, reports conventional binary HGF and 100 restarts/participant but the declared OSF dataset https://osf.io/sk82r/ returned 401 during source screening. The 100 restarts and original theta priors cannot be shortened without changing the analysis. **Status: BLOCKED_DATA_ACCESS**.
- **Sheffield et al.**, https://github.com/JuliaSheffield/CogMech_delusions, newly screened as an additional hypothesis: public `CogMech_PRL_gh.mat`, `Sheffield_CogMech.xlsx`, `hgf_softmax_mu3.m`, `hgfToolBox.zip` exist. **NOT YET ELIGIBLE**: exact source release, licensing, full original fitting pipeline, trial schema, cohort/exclusions, old-reference mappings and compatibility require separate audit before any model run. No inference is made from the presence of an archive alone.

## Next traceable technical gate

1. Preserve this and the fixed-vector softmax protocol/results. The latter uses fixed `logbeta=0` by design; **do not** describe it as either publication's original softmax-mu3 fit.
2. Recover and pin historical HGF5.3.1 with original fitted model/response configs, optimizer settings, exclusion rules and sequential first→second-half initialization for Suthaharan; recover Reed original inversion code or document inability.
3. Separately pre-register original **softmax_mu3 fixed-vector** likelihood check on the full source grid (no fitting), using frozen M7 O14 tolerance, and then a bounded study-specific matched objective/fit workflow only after exact parameter-order/priors/starts mapping is documented. Include all failures and warnings.
4. If original fit scripts cannot be reproduced, B/C are **ported analyses** rather than reproductions of original papers. A fully original published-results PASS requires participant-level fit and scientific-result metrics from the true original workflow.

Historical failed simulations, recovery experiments, source schema changes and journal fee/approval gates remain unchanged. No scientific fit is represented as having run merely because a protocol or implementation file exists.
