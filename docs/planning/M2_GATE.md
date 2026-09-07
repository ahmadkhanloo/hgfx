# M2 — Parameter/Config Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Validation workflow: `M2 Parameter Config Parity`
- Passing workflow run: `34088423448`

## Scope validated

- [x] MATLAB flat parameter order
- [x] perceptual prior means and variances
- [x] observation prior means and variances
- [x] identity/exponential transform semantics
- [x] transformed vector → native vector
- [x] transformed vector → MATLAB-style named structure
- [x] free parameters: non-zero, non-NaN prior variance
- [x] fixed parameters: zero prior variance
- [x] undefined parameters: NaN prior variance
- [x] MATLAB 1-based free/fixed/undefined indices
- [x] placeholders `99991`, `99992`, `99993`, `99994`, and `-99993`
- [x] MATLAB population variance semantics for placeholder calculation
- [x] ignored trial mask from NaN input
- [x] irregular trial mask from ignored input or NaN response
- [x] regular time axis
- [x] irregular time axis from final input column

## Official configs used as Gate-2 representatives

1. `perceptual/hgf_binary_config.m`
2. `perceptual/hgf_config.m`
3. `observation/unitsq_sgm_config.m`

Their corresponding `*_config_base`, `*_transp`, and `*_namep` behavior is included where applicable.

## Evidence

The MATLAB oracle exporter writes the frozen reference values and semantics.
The independent Python checker reconstructs the same values from HGFX schemas and compares them at `rtol=1e-12`, `atol=1e-12`.

Passing jobs in workflow run `34088423448`:

- `python-schema-tests`: PASS
- `matlab-python-parity`: PASS

The first run exposed a harness defect (missing generated output directory), which was fixed before the gate was accepted. No scientific mismatch was hidden by tolerance changes.

## Next milestone

`M3 — Scalar Numerical Parity`
