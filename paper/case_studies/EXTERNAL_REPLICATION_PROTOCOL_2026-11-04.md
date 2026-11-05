# Prospectively bounded external-study selection and replication protocol (2026-11-04)

Status: **SOURCE SCREENING ONLY — no new fitting has been run under this protocol.**

## Objective and scientific boundary

The author requests direct, real-data checks of HGFX 1.0.0 against MATLAB HGF, preferably on **two independently published empirical studies**. This protocol governs candidate screening, mapping and execution without changing the historical v1.0.0 compatibility oracle or its frozen validation results. The existing Pain and SPIRL feasibility failures remain retained and are not retconned into successes.

**Never select, replace or shrink data/participants based on whether HGFX happens to agree with MATLAB.** Do not rewrite paper results until both actual runs and evidence classification are complete. Rejecting a candidate *before* scientific execution for missing source/model/config/data/licensing is allowed and must be recorded.

### Pre-registered candidate order (before fitting)

1. **Oberwelland et al. (2021)**, DOI 10.3389/fnins.2020.536596, analysis code [msrlab/reversal_learning_behav](https://github.com/msrlab/reversal_learning_behav), behavioral-data deposit [OSF 3xrn2](https://osf.io/3xrn2/). Public code is CC BY 4.0; original TAPAS/HGF reference is **v4.0**, so a frozen 8.2.0 comparison would be a *documented migrated workflow*, not exact replication of the historical published fit. Public response model: `tapas_softmax_binary`; custom perceptual configurations with non-default priors must be mapped field-by-field. The old analysis uses three conditions per participant and missing trials were removed by original preprocessing. Gate: inspect original study metadata and trial vectors before accepting.
2. **Gao et al. (2024)**, DOI 10.1186/s40359-024-01952-x, author-declared code and participant data [OSF sk82r](https://osf.io/sk82r/). Paper cites `tapas_hgf_binary_config`, `tapas_unitsq_sgm_config` and `tapas_quasinewton_optim_config`, which are nominally within HGFX scope. However its published fit involves 100 restarts per participant and revised priors: `log(kappa2)~N(log(1),4)`, `omega~N(-3,16)`, `log(theta)~N(-6,16)` as rendered in the publisher text. Candidate is **NOT ELIGIBLE** until those semantics, OSF files and original code have been inspected, including whether the old theta transform matches the 8.2.0 family. No 100-start substitution by a single optimizer run.
3. **Reed et al. (2020)**, *Paranoia as a deficit in non-social belief updating*, [ModelDB source/data](https://github.com/ModelDBRepository/258631), containing `IRL_Data.mat` and `MTurk_Data.mat`. Original paper used HGF 5.3.1; this public mirror presently exposes input data but not a complete versioned fitting script/config. **Data presence alone does not establish eligible comparison**. Screen only if a previous candidate fails feasibility.
4. **Iglesias et al. (2013) / Mathys et al. (2014)**, original 320-trial binary *input-only* sequence bundled with MATLAB HGF 8.2.0 (pinned `demo/example_binary_input.txt`). This is a reference-backed supplementary **filtering** comparison, not a participant-response inversion or independent reanalysis of a full paper. It cannot be counted as one of two complete external participant-study replications.

Prior candidate screening outcomes remain: Pain 2025 BLOCKED by custom likelihood permission/original environment; SPIRL 2025 BLOCKED by custom joint models; Arthur 2023 BLOCKED by missing configurations; Henco 2020 requires separate combined social model mapping. No silent swapping of original models for defaults.

## Feasibility gate — mandatory before any fit

For each candidate, record original paper DOI, public code/data URL and exact commit/version where available; evidence of redistributability; MATLAB release + original HGF version; trial-level schema, response coding/missingness, exclusions and participant counts; perceptual and observation model identities, parameter order/transforms/priors/fixed values, optimizer/multistart budgets; group-level comparisons; and whether identical HGF 8.2.0 config/model can be instantiated in HGFX 1.0.0 without new core code.

Classify each study as exactly one of:
- `ELIGIBLE_EXACT_HISTORICAL`: original environment executable and same analysis portable without semantic changes;
- `ELIGIBLE_8_2_PORT`: full analysis portable to pinned MATLAB8.2 and HGFX1.0, with version difference from original explicitly labeled;
- `BLOCKED_<reason>`: critical original config/data/code/rights/model/environment absent.

No fabricated source versions, no synthesized responses, and no extracting patient identifiers or re-publishing restricted participant data.

## Prospective run gate — only for eligible candidates

First commit a study-specific `REPLICATION_PROTOCOL.md` **before** any fit. Declare exact pin/hash of all source input files and study scripts, pre-existing original exclusions, all study subjects and conditions, exact perceptual/response configuration and transformed/native parameter values; optimization configuration and starts (matched parameter vectors, not merely same RNG seed across MATLAB and Python); hardware, MATLAB runtime, CPU/JAX float64 and stable HGFX wheel 1.0.0.

Run original MATLAB model family/version (A) when reproducible, then matched frozen MATLAB8.2 (B), and identical HGFX1.0 (C), in separately labeled outputs. If A cannot execute, do **not** claim published numerical reproduction; B/C can establish scoped real-data 8.2 portability only. Use `matlab-actions/setup-matlab@v3` and `run-command@v3` on the public GitHub project for a physically executed MATLAB comparison, not mocked output. The GitHub action supports public project licensing, but availability/execution still must be observed.

Predefine comparison quantities from the exact existing HGFX paper numerical policy and model-specific golden fixtures: trial-level states, prediction errors, likelihood/objective at shared parameter vector, and fitted parameters/model selection only if the optimizer and starts are truly comparable. No universal tolerance: `P3` or recovery thresholds must not be borrowed; do not create new post-hoc pass criteria. Where no predeclared gate can be justified, report raw differences with status `DESCRIPTIVE_NOT_GATED`.

The first trial, level, state and intermediate with mismatch are required for all failed trajectory gates. Keep every subject/replicate, invalid fit, warning and denominator. A reference limitation match is not model identifiability or proof that HGFX is better; speed comparisons require separately specified hardware and protocol.

## Status now

- **Source discovery:** ongoing. Web-identified journal pages and repository names are hypotheses until file-level access is confirmed.
- **MATLAB8.2 x HGFX scientific execution under this protocol:** NOT STARTED.
- **Two published participant-study replications:** NOT COMPLETED.
- **Historical P3 failures / release freeze:** unchanged.
- **Paper integration:** prohibited until new results are validated and author-reviewed.

Reference policy: `AGENTS.md`, `docs/architecture/NUMERICAL_POLICY.md`, `docs/validation/ACCEPTANCE_CRITERIA.md` and prior frozen paper protocol.