# V1 Frozen MATLAB Source Classification

Status: **RELEASE-HARDENING GATE**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## Purpose

The final v1 review checklist requires every frozen MATLAB source file to have an explicit release disposition. Earlier M12 scientific inventory enforcement deliberately focused on `perceptual/` and `observation/` sources and reported 259 scientific files / 53 families. The frozen manifest contains 334 MATLAB `.m` files in total.

`tools/check_v1_source_classification.py` closes that bookkeeping gap without changing any scientific acceptance criterion. It reads the immutable `reference/matlab_manifest.tsv`, classifies every frozen source, and fails on an unknown path, missing evidence, a scientific family that is not `DONE`, or a manifest count other than 334.

## Status semantics

- `DONE` — a computational/scientific or compatibility surface is implemented and has named release evidence.
- `PLOT_ONLY` — upstream visualization code; underlying numerical surface/model evidence is the release criterion, not pixel identity.
- `DEPRECATED` — frozen upstream archival implementation superseded by the v8 unified scientific surface that HGFX implements and validates.
- `NOT_APPLICABLE` — upstream MATLAB-only setup/test/convenience source with no required Python runtime analogue.
- `REFERENCE_ONLY` — forbidden for the v1 frozen-source gate.

## Classification policy

| Frozen source group | v1 disposition | Evidence basis |
| --- | --- | --- |
| `perceptual/` | `DONE` | existing M12 exhaustive scientific-family rules and parity evidence |
| `observation/` | `DONE` | existing M12 exhaustive scientific-family rules and parity evidence |
| `building_blocks/` | `DONE` | M4 forward parity |
| `core/` | `DONE` | M9-M11 plus M18 fitting/sample/workflow validation |
| `demo/` | `DONE` | V1 Full MATLAB Demo Composition |
| `_original_models/` | `DEPRECATED` | frozen archival pre-unified sources; current v8 families are covered by M12 |
| `plotting/` | `PLOT_ONLY` | D10/D11 where applicable plus validated underlying trajectory/model surfaces |
| `tests/` | `NOT_APPLICABLE` | upstream MATLAB test harness; HGFX uses Python golden/regression/oracle tests |
| `utilities/` | explicit file-by-file `DONE` or `NOT_APPLICABLE` | M2/M3/M10/D11/D12 and model coverage |
| `setup.m` | `NOT_APPLICABLE` | Python packaging/S10 clean-wheel readiness |

The only frozen utility classified `NOT_APPLICABLE` is `utilities/datagen_categorical.m`, a stochastic convenience input generator. It does not define HGF inference semantics; HGFX categorical models consume explicit categorical inputs, and v1 does not claim MATLAB/NumPy RNG stream identity.

## Integrity

This gate does **not** alter or reinterpret historical scientific results. In particular, M18/S7 parameter-recovery scientific failures remain recorded as failures/reference limitations. Whole-source classification is migration/release bookkeeping, not a new scientific PASS.
