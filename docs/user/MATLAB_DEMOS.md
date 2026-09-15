# MATLAB Demo Reproductions and Parity Evidence

This document records the two official HGF Toolbox demo workflows that are release-gated for HGFX v1 and exposes them as runnable Python examples.

Reference implementation:

- HGF Toolbox version: 8.2.0
- frozen reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- official source: `demo/hgf_demo.m`
- official input: `demo/example_binary_input.txt`
- input length: 320 trials

The comparison tolerances are frozen at `rtol=5e-11` and `atol=5e-13`. They are not adjusted after seeing results.

## Demo 1 — classic HGF versus eHGF failure regime

The official MATLAB demo contains an eHGF challenge in which the classic HGF enters a region with negative posterior precision while eHGF remains valid.

Native parameter vector:

```text
[NaN, 0, 1, NaN, 1, 1, NaN, 0, 0, 1, 1.5, NaN, -4, 3]
```

### Python reproduction

```bash
python examples/matlab_demo_model_selection.py
```

Expected user-facing result:

```text
hgf_binary_success=False
ehgf_binary_success=True
status=PASS_EXPECTED_REFERENCE_BEHAVIOR
```

The classic-HGF failure is expected reference behavior, not an HGFX defect and not a scientific PASS for classic HGF.

### Exact MATLAB ↔ HGFX validation

The release workflow exports the actual MATLAB result and then runs:

```bash
python tools/check_m18_demo_model_selection.py \
  reference/generated/m18_demo_model_selection_matlab.json \
  --output reference/generated/m18_demo_model_selection_classification.json
```

Validated source revision:

```text
443ff678575f5494aebd59083b0bbf4cd7e4154b
```

GitHub Actions run:

```text
35028441041
```

Result:

| Surface | MATLAB 8.2.0 | HGFX | Result |
| --- | --- | --- | --- |
| classic `hgf_binary` | fails with `tapas:hgf:NegPostPrec` | fails with `ValueError: Negative posterior precision...` | behavior match |
| `ehgf_binary` | succeeds | succeeds | match |
| eHGF trajectories | reference values | compared at frozen tolerances | match |
| eHGF inference states | reference values | compared at frozen tolerances | match |
| mismatch list | — | `[]` | PASS |

Final classification:

```text
PASS_MODEL_SELECTION_PARITY
```

Evidence artifact:

```text
artifact_id = 10420615907
sha256 = bcae2b97272d4403d75f4a97ff07adebcf0e199adf6fdb57494646c800cea982
```

## Demo 2 — uHGF to uHGF-AR(1)

The second workflow reproduces the official transition from the unbounded binary HGF to its AR(1) variant.

Native uHGF parameter vector:

```text
[NaN, 0, 1, NaN, 1, 1, NaN, 0, 0, 1, 1, NaN, -2.5, 3]
```

Native uHGF-AR(1) parameter vector:

```text
[NaN, 0, 1, NaN, 1, 1, NaN, 0, 0.3, NaN, 0, 1, NaN, 0, 0, 1, 1, NaN, -2.5, 3]
```

### Python reproduction

```bash
python examples/matlab_demo_uhgf_ar1.py
```

The frozen MATLAB descriptive values are:

| Quantity | MATLAB 8.2.0 | HGFX on validated revision |
| --- | ---: | ---: |
| uHGF max `abs(mu[:, level 3])` | `16.99162398501939` | `16.99162398501939` |
| uHGF-AR(1) max `abs(mu[:, level 3])` | `4.0927117005012175` | `4.0927117005012175` |

Both perceptual workflows succeed in both implementations.

### Exact MATLAB ↔ HGFX validation

```bash
python tools/check_m18_demo_uhgf_ar1.py \
  reference/generated/m18_demo_uhgf_ar1_matlab.json \
  --output reference/generated/m18_demo_uhgf_ar1_classification.json
```

Validated source revision:

```text
443ff678575f5494aebd59083b0bbf4cd7e4154b
```

GitHub Actions run:

```text
35028441038
```

The checker compares complete release-relevant trajectories and inference states at the frozen tolerances, not only the two descriptive extrema above.

Final classification:

```text
PASS_UHGF_AR1_WORKFLOW_PARITY
```

Mismatch list:

```text
[]
```

Evidence artifact:

```text
artifact_id = 10420651501
sha256 = d9cc69b6292158cbc401835aa5b953d009440ce60910ff7dda99ca275e251768
```

## Running the Python demos locally

The examples use the official input stored in the pinned MATLAB reference submodule. From a repository checkout:

```bash
git submodule update --init --recursive
python -m pip install .
python examples/matlab_demo_model_selection.py
python examples/matlab_demo_uhgf_ar1.py
```

If the official input is stored elsewhere, pass it explicitly:

```bash
python examples/matlab_demo_model_selection.py --input /path/to/example_binary_input.txt
python examples/matlab_demo_uhgf_ar1.py --input /path/to/example_binary_input.txt
```

No MATLAB runtime is required to execute the Python reproductions. MATLAB is required only when regenerating the cross-language oracle evidence.

## Regenerating the full cross-language evidence

The authoritative route is the GitHub Actions workflows:

- `.github/workflows/m18-demo-model-selection.yml`
- `.github/workflows/m18-demo-uhgf-ar1.yml`

They perform all of the following on one revision:

1. checkout the exact HGFX revision and frozen MATLAB submodule;
2. verify the reference freeze;
3. execute the user-facing Python demo;
4. execute the corresponding MATLAB reference workflow;
5. compare MATLAB and HGFX outputs at frozen tolerances;
6. upload machine-readable evidence artifacts.

This prevents a demo from appearing correct merely because documentation contains previously recorded numbers.

## Interpretation

The two demos establish concrete product-level MATLAB equivalence for the workflows they cover. They do not erase the historical M18 scientific failures or turn reference limitations into scientific successes.

For the complete model-by-model release scope, use `docs/validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md` and `docs/validation/V1_EVIDENCE_INDEX.md` as the authoritative sources.
