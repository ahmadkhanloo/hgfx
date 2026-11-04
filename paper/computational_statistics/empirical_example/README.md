# Empirical USD/CHF workflow

This example was executed once under the committed revision protocol, using all
614 observations from the frozen HGF 8.2.0 demo. It is an empirical-input
demonstration, not a participant-study replication or a forecasting evaluation.

The MIT-licensed source is pinned at
https://github.com/ComputationalPsychiatry/hgf-toolbox/tree/2437f4dc241541072722a2695ddeca7b44d83dd3.
See `demo/hgf_demo.m`, lines 343-359. Original notice: Copyright (c) 2012-2024
Christoph Mathys and contributors; the complete license is HGF_LICENSE.txt.
The upstream description identifies 2010/2011 exchange rates. Calendar labels
and the original market provider are not independently established.

## Reproduce

Create an isolated Python 3.12 environment; install hgfx==1.0.0 and the pinned
dependencies in ../worked_example/requirements.lock. From outside the repository:

```sh
python /path/to/empirical_example/run.py --input /path/to/empirical_example/example_usdchf.txt --output /path/to/new-result.json
```

Use a new output path to preserve the recorded result. No MATLAB is required.
The original run used the already verified release-wheel environment described
in ../worked_example/acquisition.json. `result.json` records the actual installed
module path, runtime, x64, input byte digest, full states and statistics.
`provenance.json` also gives an LF-canonical input digest for portable checkouts;
line-ending normalization does not change the numeric sequence.

The call is `hgfx.fit_model([], inputs, 'hgf_config', 'bayes_optimal_config',
'quasinewton_optim_config')`. Input likelihood, empty responses, two levels,
input-dependent default priors and one default optimizer run are preserved.
No simulated responses, exclusions, model selection or parameter tuning were used.

## Recorded result and limitations

The run returned finite likelihood/evidence statistics in 182.001 seconds.
The negative log likelihood was -2387.6219521878747 and BIC -4736.723934806867.
Continuous densities can exceed one, so negative NLL values are possible.
Ridders differentiation emitted `invalid value encountered in scalar subtract`
warnings at lines 56 and 60 of the installed ridders.py. The result has no public
termination-reason field. Finite statistics do not certify convergence or
curvature accuracy. Warnings were not suppressed and no scientific retry was made.

Figure 5 is generated from the saved result, without re-running the fit.
No held-out forecast, independent new MATLAB parity, financial recommendation,
parameter-recovery success or successful Pain/SPIRL replication is claimed.
