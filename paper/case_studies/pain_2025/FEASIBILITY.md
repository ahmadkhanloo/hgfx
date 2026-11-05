# Pain 2025 feasibility - 2026-11-04

**Decision: BLOCKED_UNLICENSED_CUSTOM_RESPONSE_AND_UNRESOLVED_ENVIRONMENT.** No fitting, recovery, or paper-result reproduction was executed. This is a documented stopping outcome under P1/P2, not scientific completion of a case study.

## Frozen source and acquisition

Paper: Lacombe-Thibault and Coll, DOI https://doi.org/10.1016/j.jpain.2025.105569. Source: https://github.com/meganel-t/painuncertainty at `3f1d32aff73826a1385c359ca638ad0e11a7fda7`. All 504 tracked files are hashed in the new `source_manifest.json`; the historical acquisition manifest is unchanged. Sources remain ignored and are not redistributed.

Reacquire from the repository root:

```sh
git clone https://github.com/meganel-t/painuncertainty.git paper/case_studies/local_only/pain_2025
git -C paper/case_studies/local_only/pain_2025 checkout --detach 3f1d32aff73826a1385c359ca638ad0e11a7fda7
python paper/computational_statistics/audit_case_sources.py
```

Actual shell entry point: `code/runall.sh`, not a root runall.sh. It invokes preprocessing, model fitting, model comparison, statistics, recovery, and final figures. In addition, c02 itself runs recovery after the first fit. Running c02 or runall unmodified would exceed the bounded replication scope.

## Input closure and preprocessing

`code/c01_import_and_plot_participant.py:28` reads **sourcedata/participants.csv**, which exists. The root participants.tsv is a distinct derived/output table: c01 writes it twice; c03 consumes its excluded column. The participants-name concern in the handoff is resolved by the actual tree; no substitute file was created. `sourcedata/iasta.csv`, `pcs.csv`, and `bdi.csv` also exist and are separately hashed. Task CSVs remain local. The source enumerates folders containing sub- and excludes sub-055 and sub-059, sorts them, selects a case-sensitive PainUncertainty CSV, drops rows with missing block_name and stimulus_, and asserts 192 trials. A source-level inventory is in the manifest; these counts are not a validated final analysis sample. Root participant exclusions used later by c03 must be reconciled with c01 before any protocol is eligible.

On Windows, Path.glob is case-insensitive; the inventory deliberately uses the source's case-sensitive string predicate to avoid counting calibration files as task files. No preprocessing is executed by the inventory.

c02 recodes aigu/grave as 0/1 and moderee/forte as 0/1. It recodes n/m as 0/1 and other choices as NaN. Contingency is cue XOR pain. Incorrect choices, including missing choices, make response RT NaN; RT <0.2 seconds is then NaN. It computes `round(log(rt*1000),16)` (natural logarithm of milliseconds), without deleting the input trial. Input is `[contingency, pain, ones]`; whether the last column is used depends on the original config's interval flag, not merely column presence. Missing response trials must remain separate from ignored inputs. No rounding approximation has been substituted.

## Dependency closure

`dependency_inventory.csv` maps external MATLAB symbols in every .m file to local study files or candidate frozen-oracle paths. MATLAB builtins and toolbox functions (tables, plotting, parfor/Parallel Computing Toolbox, etc.) require a MATLAB runtime; the inventory is a namespace scan, not proof of dynamic closure. Custom model response, transform, simulation and naming files are present under code/models. `tapas_hgf_binary_plotTraj_nosd` is absent from both this snapshot and oracle 8.2. Plotting could be omitted only as a declared executable adaptation, not used to claim the unmodified original runs. VBA_groupBMC is required for the group result and its historical version is unpinned.

Original MATLAB, TAPAS and VBA commits are not recorded: **ORIGINAL_ENVIRONMENT_UNRESOLVED**. R2024a in code/runall.sh is an executable path hint, not evidence of the environment used for published results. The local R2025b installation does not settle this. Oracle 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3` is a separate port target; stripping tapas_ from names does not establish equivalence.

## Model semantics and scope

The six fitted models are hgf2, hgf2pu, hgf3, hgf3pu, RW and PH (see model_mapping.csv). The HGF-labelled models use **enhanced** HGF configs. c02 changes priors, not just model names. hgf2 retains three represented levels: kappa2 is fixed to zero by logkappa2=-Inf, third-level omega variance is zero. The frozen candidate config has n_levels=3 and its infStates is N x levels x 4: predicted means, predicted variances, posterior means, posterior variances. Reading infStates(:,3,3) inside the response labelled hgf2 is therefore not itself an indexing bug; it is unused in that response. This is source-shape evidence for the candidate, not a measurement of the unknown historical runtime.

Perceptual transformed order is `[mu_0, logsa_0, rho, logka, om]`; PU appends `[logal, eta0, eta1]`. c02 rebuilds both prior means and variances in that order. HGF2/PU sets omega2 mean=-5, variance=16, omega3 variance=0, both logkappa variances=0 and means=[0,-Inf]. HGF3/PU sets omega means=[NaN,-5,-6], variances=[NaN,16,16]. RW additionally sets logitv_0sa=1 and rebuilds [logitv_0sa,logitalsa]; PH sets logitv_0sa=1 and rebuilds [logitv_0sa,logital_0sa,logSsa]. Their remaining inherited means/variances are unresolved. Other perceptual priors are inherited from the unpinned original configs and remain unresolved, rather than silently imported from 8.2. Positive quantities sa_0, kappa, alpha use the indicated log transforms; placeholder/fixed entries require preserving NaN and zero variance.

HGF2 response order `[be0,be1,be2,logze]`; HGF3 inserts be3 before logze. RW/PH order `[be0,be1,logze]`. Only ze is exponentiated; it is residual **variance**, not standard deviation or choice inverse temperature. Priors: be0 mean log(760), variance 4; each slope mean 0, variance 4; logze mean log(log(20)), variance log(2). All these response parameters are free. HGF2 predictors are Bernoulli predictive variance and sigmoid(mu2)*(1-sigmoid(mu2))*sa2. HGF3 adds sigmoid(mu2)*(1-sigmoid(mu2))*exp(mu3). RW uses absolute contingency prediction error; PH uses associability. Likelihood is Gaussian in log RT. No choice likelihood is fitted by these responses.

No exact study response adapter/golden fixture is established in HGFX 1.0.0. Standard logRT names do not certify equality of covariates, priors or missingness. Dropping these responses would change the statistical question. Broad core expansion is outside this handoff's default scope. No mathematical implementation or Migration Matrix status has changed.

## Licenses and terminal gate

Paper, data and code are separate: the publisher PDF/fulltext returned HTTP 403 during this execution; secondary metadata suggesting article CC-BY is not treated as a verified license for data or code. No root LICENSE was found. The HGF2/HGF3 simulation files carry GPLv3 notices, which are preserved locally; the main likelihood/configuration files do not carry a clear grant. Permission for the exact custom response/config port remains unresolved. Data license and main custom likelihood/configuration license: **UNRESOLVED**. Do not copy or translate these custom sources into HGFX or publicly commit them. Public URLs/hashes are sufficient for this audit.

A minimum defensible replication would retain all six original perceptual/response pairs and group model comparison, clarify exclusions and the original environment, and acquire permission for the custom model port plus case-specific golden references. There is currently no authorized exact port. P3/P4/P5 case-result execution is gated off; no original numbered figure is selected as if it were reproduced. SPIRL was checked as the predetermined fallback. Independent journal preparation continues, explicitly without a successful real-data case.

The HGF2/HGF3 simulation files have declared MATLAB function names that differ from filenames. These are flagged as DECLARED_NAME_FILENAME_MISMATCH in the inventory, not repaired. Exact tapas_sgm is mapped before considering a stripped-name oracle candidate.
