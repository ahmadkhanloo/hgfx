# REV-2.6A protocol — forward-filter precision stability (float32 vs float64)

Status: FROZEN_BEFORE_EXECUTION (committed before any run).
Task: `COMPSTAT_REVISION_PLAN.md` REV-2.6, angle **A** (the single permitted
statistical-computing angle; default choice after D1=A). One run; at most one
rerun for documented infrastructure failure. Three terminal states apply
(FIXED / EXPLAINED / DOCUMENTED_LIMITATION); this study is descriptive and
never produces a scientific PASS.

## Question

Does the released HGFX 1.0.0 forward filter remain stable when a user
accidentally runs on JAX's default float32 (the common user mistake), and how
does forward-filter error against the float64 reference grow with trial
horizon? This yields the concrete computational question the article may
state (plan C6): precision/stability separation between numerical evaluation
layers, with practical guidance ("use float64; the failure region is X").

## Scope and known limitations (frozen now)

- Model: `hgf_binary` perceptual forward filter with `unitsq_sgm` observation
  semantics ignored (perception only; no observation likelihood, no fitting,
  no optimizer, no gradient).
- Implementation: the released `hgfx==1.0.0` wheel (evidence for 1.0.0
  claims), CPU only, one JAX device.
- MATLAB half of the plan text ("characterize the parameter regions where the
  recursion fails in **both** MATLAB and HGFX") is **NOT RUN** here: no local
  MATLAB oracle exists on this machine, and the failure-region comparison
  against MATLAB remains a documented limitation of this task
  (DOCUMENTED_LIMITATION for the MATLAB half; the HGFX half is measured).
- Perceptual family: classic binary HGF only (the article's primary family);
  eHGF/uHGF are out of scope for this bounded study.

## Parameter draws (REV-2.4 scheme, new seed)

- Exactly **200** transformed-parameter vectors, scheme identical to the
  REV-2.4 Panel-G generator: `numpy.random.Generator(numpy.random.PCG64(2026111400))`;
  for each row, in the exact free-index order of the resolved
  `hgf_binary_config`, draw `z = rng.standard_normal(n_free)` and set
  `theta_free = prior_mean_free + sqrt(prior_variance_free) * z`; only free
  entries of the resolved default vector are replaced; fixed entries stay at
  resolved defaults. No clipping, redraw or rejection. Draws causing forward
  failure remain in the denominator with their status.
- Inputs `u`: binary sequence from `numpy.random.Generator(numpy.random.PCG64(2026111401))`,
  `u = rng.integers(0, 2, size=65536)`; each horizon uses the first `T`
  entries (prefix property), identical across draws and precision legs.

## Horizons, legs and pairing

- Horizons: `T in {128, 4096, 65536}`.
- Leg **R (reference)**: `JAX_ENABLE_X64=1`, CPU; float64 forward filter.
- Leg **F (treatment)**: default JAX without x64 (the user mistake); the same
  NumPy float64 input arrays are handed to the same runner code and are cast
  down by JAX, exactly reproducing the mistake.
- Both legs run the same runner script twice (separate processes; JAX x64
  cannot be toggled in-process). Pairing is by `(T, draw index)`; `u` and
  `theta` are bitwise identical across legs (exported once, hashed, reloaded).

## Metrics and failure classification (no tolerance invention)

For each `(T, draw)`:
1. Leg status: `ok` | `exception:<first line>` | `nonfinite_output` |
   `negative_posterior_precision` (any finite posterior precision `sa < 0`
   at any level/trial in that leg's trajectories).
2. When **both** legs are `ok`: paired absolute differences
   `max|mu_F - mu_R|` and `max|sa_F - sa_R|` over all levels and trials
   (descriptive; no acceptance threshold is defined or applied).
3. Aggregate per `T`: failure fraction per class for each leg, and quantiles
   (median, 90th, 99th percentile, max) of the paired differences over valid
   pairs. All draws stay in denominators; failures are never dropped.

## Outputs

- `evidence/revision/rev26_precision_stability.json` — protocol ID, wheel
  SHA-256, JAX/NumPy versions, input/vector hashes, per-draw records, per-T
  aggregate table.
- `evidence/revision/rev26_precision_error.png` — one figure: paired max
  absolute `mu` difference quantiles vs horizon (log-log), with the float32
  failure fraction annotated.
- One practical-guidance sentence for the article, stated from the measured
  data (integration into the manuscript is a later REV-3 editorial step
  requiring author review; this protocol does not edit the manuscript).

## Stopping rule and caps

- One complete run of both legs. A rerun is allowed only for infrastructure
  failure (crash, OOM, runner outage), at most once, logged as such.
- No change of seeds, draws, horizons, inputs, code paths, precision flags or
  denominators after seeing results. No tolerance is defined or relaxed.
