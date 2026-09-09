# Model Recovery Protocol

M18 performs simulation-based model recovery over a frozen binary HGF candidate set.

## Candidate set

- `hgf_binary`
- `ehgf_binary`
- `uhgf_binary`

All candidates use `unitsq_sgm`.

Each generated dataset is independently fitted under **every** candidate. Model recovery
therefore tests inference and selection; it does not compare forward trajectories at the
generating parameter vector.

## Frozen gate design

- trial counts: 128 and 256;
- truth perturbation scales: 0.15 and 0.35 prior SD;
- 3 replicates per generating-model/trial-count/regime cell;
- deterministic seeds;
- BIC is the primary winner rule;
- AIC is stored as a secondary diagnostic.

Outputs:

- generating-model × selected-model confusion matrix;
- row-normalized recovery matrix;
- balanced accuracy;
- per-dataset BIC/AIC values.

## Minimum M18 criterion

Balanced recovery accuracy must be >= 0.50 across the three-model candidate family.
Chance performance is 1/3, so this threshold requires useful discrimination while
remaining a minimum gate rather than a publication-level effect-size claim.

The final paper should additionally report uncertainty and recovery stratified by trial
count and parameter regime.
