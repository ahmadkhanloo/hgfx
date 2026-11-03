# Supplementary evidence and provenance

## S1 Frozen identities and regeneration

The evaluated HGFX release is 1.0.0. Its source commit is

`4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

The MATLAB oracle is 8.2.0 at

`2437f4dc241541072722a2695ddeca7b44d83dd3`.
These identities define the scope; current development features are not included.
Original numerical experiments were not rerun for this revision.

Candidate figures regenerate with `python generate_figures.py` from this directory.
The agreement/accuracy figure is redesigned from the frozen decision; recovery is redrawn in grayscale from the decision, and pyhgf includes a signed residual from all frozen trials. Horizon and backend figures are byte-identical copies of historical images.
Their input/output hashes are recorded separately. The workflow diagram is
conceptual and contains no data. Complete machine-readable source links appear
in the repository claim ledger; this supplement supplies a compact reading route.

## S2 Fitting and recovery

The official stress-fit D02 and holdout D08 are preserved failures, classified as
matched reference limitations, not direct parameter parity. Their decision files
and frozen source runs remain in the reference validation directory. No endpoint
was forced, no trial was silently discarded and no tolerance was changed here.
The historical M18 scientific failure remains separate from paired S7 accounting.

The paired grid has 72 parameter cases and 36 model-recovery datasets with three
candidate fits each. There are 12 shards, two trial lengths (128,256), two truth
scales (0.15,0.35 prior SD), six parameter replicates per stratum and three model
replicates per stratum. The selection rule is minimum BIC. Metrics rounded for display; full precision remains in the frozen decision:

| Model | Implementation | Convergence | Median r | Median sRMSE |
|---|---|---|---|---|
| hgf_binary | matlab | 0.833333333333 | 0.202684570158 | 2.60966284547 |
| hgf_binary | hgfx | 0.833333333333 | 0.202684570141 | 2.60966284551 |
| ehgf_binary | matlab | 0.916666666667 | 0.461918369101 | 2.35912688823 |
| ehgf_binary | hgfx | 0.916666666667 | 0.461918369078 | 2.35912688867 |
| uhgf_binary | matlab | 0.791666666667 | 0.380968313583 | 2.95788661965 |
| uhgf_binary | hgfx | 0.791666666667 | 0.380968313591 | 2.95788661807 |

The frozen scientific criteria are convergence >=0.80, median r >=0.50,
median sRMSE <=1.00 and model-recovery balanced accuracy >=0.50. Agreement is
36/36 winners, while balanced accuracy is 0.5833333333333334 in each implementation.
These are deterministic grid summaries, not uncertainty intervals.

## S3 Trial-horizon integrity

The original run 35272347167 contains 24 shards, 144 parameter cases and 72 model
cases. The overall gate is false. Both winner agreement and the free-index
contract fail. Ten BIC winners differ, confined to classic HGF at 512/1024 trials;
the aggregate per-model mismatch classification covers all three families. Invalid
classic-HGF trajectories remain in the denominator; undefined metrics remain gaps.
A favorable diagnostic row is not an aggregate scientific success.

![Figure S1](figures/fig_p3_horizon_diagnostics.pdf){width=100%}

**Fig. S1** Frozen diagnostic recovery metrics by horizon. Dotted lines are
predeclared thresholds, gaps preserve invalid classic-HGF cases, and the paired
integrity gate fails. No new uncertainty interval, interpolation or imputation is
introduced

## S4 Backend applicability

Physical evidence is retained from source
`07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`, Python 3.12.13,
JAX/JAXLIB 0.11.1. Two Tesla T4 devices were visible; four required fitting cells
ran on cuda:0. Residency checks and enumeration are separate. Its raw JSON and
retention basis remain archived; it is not a new post-remediation GPU execution.
The CPU remeasurement has its own source/runtime identity. The maximum gaps are
0.006783711260709424 (compatibility/JAX CPU, criterion 0.10) and
1.4210854715202004e-14 (JAX CPU/T4, criterion 1e-7).

![Figure S2](figures/fig_gpu_applicability.pdf){width=95%}

**Fig. S2** Each maximum objective gap divided by its own frozen criterion;
the dashed line is the acceptance boundary. These bars describe numerical
agreement in recorded cells, without error bars. There is no speed measurement

## S5 pyhgf common scope

pyhgf 0.3.2 source is `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`.
The fixed 128-trial case uses a three-level binary hierarchy, standard volatility
updates and mean-field updates, zero drift and unit coupling. The native response
inverse temperature is 48. Input and response hashes and the prospective semantic
mapping remain in the original common-scope record. Field-wise measured errors:

| Quantity | Classification | Maximum absolute error |
|---|---|---|
| derived first level input surprise | PASS | 4.440892098500626e-16 |
| derived first level prediction error | PASS | 1.1102230246251565e-16 |
| first level predicted probability | PASS | 1.1102230246251565e-16 |
| level 2 posterior mean | PASS | 4.440892098500626e-16 |
| level 2 posterior precision | PASS | 6.661338147750939e-16 |
| level 2 predicted mean | PASS | 4.440892098500626e-16 |
| level 2 predicted precision | PASS | 6.661338147750939e-16 |
| level 3 posterior mean | PASS | 1.1102230246251565e-16 |
| level 3 posterior precision | PASS | 1.5543122344752192e-15 |
| level 3 predicted mean | PASS | 1.1102230246251565e-16 |
| level 3 predicted precision | PASS | 1.5543122344752192e-15 |
| participant response nll per trial | NDC | not applicable |
| participant response nll total | NDC | not applicable |

NDC applies to participant-response NLL at a probability boundary; belief agreement
does not repair the response comparison. No clipping or changed tolerance was
introduced after results. Package-wide or fitted-model equivalence is untested.

## S6 Applied feasibility and source routes

Pain source commit is `3f1d32aff73826a1385c359ca638ad0e11a7fda7`;
all 504 tracked files are hashed in its source manifest. Its exact likelihood/config
license and historical environment remain unresolved. Some simulation files carry
GPL notices; no source was translated into MIT code. The missing plotting helper
and filename/declaration mismatches remain recorded. Input-name confusion was
resolved using the actual source table path, without manufacturing data.

SPIRL source commit is `86fd5122a744acfb5bc7ba12720426d8b4aa0ffa`.
Its custom eHGF and seven joint choice/RT response models require a separate
migration. The recorded original settings include 399 random starts and MATLAB
R2019b; using standard eHGF or dropping RT is a changed analysis.

No published-study fit or new recovery was executed. The clean-wheel quickstart
is synthetic workflow evidence only. Unlicensed external files remain local and
ignored; public manifests contain hashes and URLs rather than participant values.
The historical acquisition dossier remains unchanged.

## S7 Evidence index and claims

The revision's CLAIM_EVIDENCE.csv maps manuscript paragraphs to source artifacts,
hashes, locators and scope. Agent checks are distinct from human verification;
author confirmation is pending throughout. The baseline hash inventory protects
historical evidence. Paper protocol 1 remains the numerical authority. Failed
recovery, sensitive fits, P3 integrity failure and response NDC remain in the main
text. Editorial files record unresolved financial and authorship conditions.
