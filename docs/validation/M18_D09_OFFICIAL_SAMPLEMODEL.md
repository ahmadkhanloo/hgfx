# M18 D09 — official prior-predictive sampleModel demo gate

Status: **FROZEN FOR PAIRED VALIDATION**

Protocol: `m18-d09-official-samplemodel-1`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scope

Reproduce the official `hgf_demo.m` prior-predictive sampling calls:

```matlab
sample1 = sampleModel(u, hgf_binary_config, unitsq_sgm_config, 123);
sample2 = sampleModel(u, hgf_binary_config, unitsq_sgm_config, 456);
```

using `demo/example_binary_input.txt` and the frozen default `hgf_binary_config` / `unitsq_sgm_config`.

MATLAB and NumPy RNG streams are not assumed to be byte-identical. For each official seed, MATLAB exports the standard-normal draws actually implied by its seeded `sampleModel` parameter-sampling sequence. HGFX is evaluated with those exact drivers. This isolates model/config/transform/trajectory semantics from RNG-engine identity.

## Required parity

For both seeds `123` and `456`, using unchanged M11 tolerance `rtol=3e-10`, `atol=3e-12`:

- resolved transformed perceptual parameters;
- transformed/native observation parameter;
- native perceptual parameters;
- every trajectory field present in the frozen MATLAB sample result that is also part of the HGFX compatibility trajectory;
- input/ignored-trial and seed/result semantics.

MATLAB response samples are retained as evidence but are not cross-runtime equality-gated because `unitsq_sgm_sim` uses MATLAB's Statistics Toolbox RNG path after re-seeding. Observation sampling semantics are already separately validated by deterministic-driver M11 tests.

## Decision

- `PASS` only if both frozen seed cases pass every required comparison.
- Any parameter/config/transform/trajectory mismatch is `IMPLEMENTATION_MISMATCH` and blocks D09.
- Missing required evidence is `INSUFFICIENT_REFERENCE_EVIDENCE`.

No seed, dataset, config, field set or tolerance may be changed after execution to obtain PASS.
