# M11 — Simulation Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Orchestration: frozen `simModel.m` and `sampleModel.m`
- Passing workflow run: `34167613757`
- Numerical mode: CPU float64

## Gate definition

M11 passes when the compatibility simulation path preserves frozen MATLAB
orchestration, parameter transforms, prior sampling semantics, ignored-trial
behavior, deterministic response probabilities, seeded same-runtime
reproducibility, and the stochastic distributions of supported observation
samplers.

Cross-language RNG-stream identity is **not** claimed.

## simModel parity

Validated on the standard vertical slice `hgf_binary + unitsq_sgm`:

- [x] fixed native perceptual parameters
- [x] fixed native observation parameters
- [x] HGF `infStates`
- [x] returned `traj.mu`
- [x] returned `traj.sa`
- [x] returned `traj.da`
- [x] deterministic unit-square-sigmoid response probability
- [x] ignored-trial index semantics
- [x] response length remains equal to input length
- [x] exported-uniform Bernoulli semantics

### Frozen ignored-trial quirk

The source `simModel.m` removes ignored rows from returned
`traj.muhat` and `traj.sahat` during its binary-HGF NaN validation, while
the full `infStates` used by the observation model retain all trials.

M11 reproduces and tests this behavior explicitly rather than normalizing it.

## sampleModel parity

Validated with a controlled `hgf_binary_config + unitsq_sgm_config` prior
predictive case:

- [x] MATLAB prior standard-normal drivers exported
- [x] transformed perceptual parameter vector
- [x] native perceptual parameter vector
- [x] transformed observation parameter vector
- [x] native observation parameter vector
- [x] parameter transform semantics
- [x] perceptual trajectories
- [x] `sampleModel` keeps full trajectory rows
- [x] seeded same-runtime reproducibility

The checker injects MATLAB-exported standard-normal drivers into Python. This
gates the scientific prior-draw → transform → forward path without pretending
MATLAB and NumPy normal generators emit the same stream.

## Stochastic observation validation

Python unit tests cover:

- `unitsq_sgm_sim`: Bernoulli mean converges to deterministic probability
- `softmax_binary_sim`: Bernoulli mean converges to deterministic probability
- `gaussian_obs_sim`: empirical mean and variance match the generating model
- identical Python seeds reproduce identical local simulation results

## MATLAB Actions dependency isolation

The frozen `unitsq_sgm_sim.m` calls `binornd`, which requires MATLAB's
Statistics and Machine Learning Toolbox. The GitHub MATLAB runner used here
does not include that toolbox.

M11 therefore uses a **test-only**, M11-scoped Bernoulli shim:

`reference/matlab/m11_shims/binornd.m`

It implements only the required `n=1` Bernoulli case as `rand < p`.
It is added to the MATLAB path only by the M11 exporter. Its random sequence is
not compared against Python or claimed to reproduce Statistics Toolbox RNG
internals. The deterministic probability path and Bernoulli distribution are
the parity targets.

## Evidence

Workflow run `34167613757`:

- `python-simulation-tests`: PASS
- `matlab-python-simulation`: PASS
- frozen reference verification: PASS
- MATLAB oracle export: PASS
- MATLAB/Python checker: PASS

The first MATLAB CI attempt correctly exposed the missing Statistics Toolbox
dependency. The gate was repaired by isolating that external dependency rather
than relaxing numerical tolerances or modifying scientific equations.

## Architecture boundary

M11 completes the standard compatibility chain through prior-predictive
simulation:

```text
parameters/config
→ forward model
→ observation likelihood
→ objective
→ compatibility MAP fitting
→ Hessian/LME
→ simModel
→ sampleModel
→ seeded/distributional simulation validation
```

## Next milestone

`M12 — Specialized Model Coverage`
