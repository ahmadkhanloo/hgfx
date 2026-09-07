# M9 — Compatibility Fitting Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Optimizer: `quasinewton_optim.m`
- Config: `quasinewton_optim_config.m`
- Passing workflow run: `34161336607`
- Numerical mode: CPU float64

## Gate definition

M9 passes when the frozen compatibility optimizer and the default deterministic MAP fitting path are scientifically equivalent to MATLAB while reusing the already-frozen M8 objective.

## Optimizer configuration frozen

```text
tolGrad   = 1e-3
tolArg    = 1e-3
maxStep   = 1
maxIter   = 100
maxRegu   = 16
maxRst    = 10
nRandInit = 0
optIter   = 1
```

## Scope validated

- [x] MATLAB-compatible BFGS quasi-Newton port
- [x] Ridders numerical gradient with `min_steps=10`
- [x] initial inverse Hessian `T = I`
- [x] descent vector and slope semantics
- [x] max-step clipping
- [x] regularization schedule `t=0.5^j`
- [x] frozen sufficient-decrease test
- [x] reset toward the initial vector by 10%
- [x] maximum reset semantics
- [x] MATLAB `tolArg` convergence formula
- [x] MATLAB `tolGrad` convergence formula
- [x] BFGS curvature threshold and update
- [x] quadratic optimizer oracle: `argMin`, `valMin`, and `T`
- [x] combined perceptual+observation free parameter indices
- [x] reconstruction of the full transformed vector
- [x] fixed and NaN-prior parameters remain restricted
- [x] deterministic initialization from prior means
- [x] standard `hgf_binary + unitsq_sgm` MAP fit
- [x] transformed perceptual MAP parameters
- [x] transformed observation MAP parameters
- [x] native perceptual MAP parameters
- [x] native observation MAP parameters
- [x] final negative log joint
- [x] final negative log likelihood
- [x] upstream M8 objective and M3 Ridders regressions

## Architecture decision

The optimizer receives a restricted scalar function built from the M8 objective. Likelihood and prior equations are not reimplemented inside the optimizer.

## Multi-start boundary

The frozen config uses `nRandInit=0`, so default `fitModel` compatibility is single-start. When random initializations are enabled, the reference chooses the winning run by LME. Because LME requires Hessian parity, seeded multi-start selection is explicitly deferred to M10 rather than approximated in M9.

## Fit-statistics boundary

M9 deliberately does **not** claim parity for:

- numerical Hessian at MAP
- Sigma / Corr
- LME or decomposed LME
- accuracy / complexity
- AIC / BIC
- LME-based random-restart selection

These are the M10 gate.

## Evidence

Workflow run `34161336607`:

- `python-compat-fitting-tests`: PASS
- `matlab-python-compat-fitting`: PASS

No SciPy optimizer was substituted. No autodiff gradient was substituted. The frozen Ridders+BFGS numerical path is retained for compatibility mode.

## Next milestone

`M10 — Hessian/LME Parity`
