# M18 D12 — Bayesian Parameter Averaging Parity

Status: **IMPLEMENTED / VALIDATION PENDING**

Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## Scope

D12 reproduces the `bayesian_parameter_average(est2, est2b)` workflow used by the official HGF demo. The product API is `hgfx.bayesian_parameter_average(...)` and mirrors the MATLAB utility's posterior-precision pooling semantics.

The gate intentionally isolates BPA from upstream optimizer behavior. MATLAB generates two deterministic demo-family fits using `example_usdchf.txt`, `hgf_config`, `gaussian_obs_config`, default quasi-Newton optimization, and predeclared simulation seeds `123` and `456`. Their fitted transformed parameters, priors, and posterior Hessians are exported. HGFX consumes those exact estimate structures as BPA inputs.

The paired comparison gates:

- pooled posterior precision `optim.H`;
- covariance `optim.Sigma`;
- posterior correlation `optim.Corr`;
- averaged transformed and native perceptual/observation parameters;
- all averaged perceptual trajectory fields returned by the model.

Tolerance is frozen at `rtol=3e-8`, `atol=3e-10`. No threshold, seed, model, start, or fit result may be changed after observing the gate.

A D12 PASS establishes parity of the BPA utility itself. It does not retroactively alter the classification of any upstream fitting case.
