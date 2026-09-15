# HGFX examples

These examples exercise only release-supported behavior.

## Quick start

From a source checkout:

```bash
python -m pip install .
python examples/quickstart.py
```

The quick-start example fits the validated `hgf_binary + unitsq_sgm` workflow through the public `hgfx.fit_model` API and prints basic fit statistics.

## Official MATLAB demo reproductions

Initialize the frozen reference submodule so the official 320-trial demo input is available:

```bash
git submodule update --init --recursive
```

Then run:

```bash
python examples/matlab_demo_model_selection.py
python examples/matlab_demo_uhgf_ar1.py
```

`matlab_demo_model_selection.py` reproduces the official eHGF challenge from the frozen `demo/hgf_demo.m`: classic HGF is expected to reject the negative-posterior-precision regime while eHGF succeeds.

`matlab_demo_uhgf_ar1.py` reproduces the official uHGF → uHGF-AR(1) workflow and self-checks its descriptive level-3 extrema against the frozen MATLAB reference values using the release tolerances.

The Python examples do not require a MATLAB runtime. MATLAB is used only by the reference-aware CI workflows that regenerate and compare cross-language evidence.

See `docs/user/MATLAB_DEMOS.md` for the exact MATLAB↔HGFX comparison results, workflow run IDs, artifacts, and interpretation.

Examples are part of the v1 release-readiness surface. The quick-start must run from a clean wheel installation without MATLAB; the official demo reproductions are also executed by their corresponding parity workflows against the pinned reference input.
