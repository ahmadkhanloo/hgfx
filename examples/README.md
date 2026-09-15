# HGFX examples

These examples exercise release-supported behavior and the official MATLAB demo workflows.

## Quick start

From a source checkout:

```bash
python -m pip install .
python examples/quickstart.py
```

The quick-start example fits the validated `hgf_binary + unitsq_sgm` workflow through the public `hgfx.fit_model` API and prints basic fit statistics.

## Full companion to MATLAB `hgf_demo.m`

Initialize the frozen reference submodule so both official demo datasets are available:

```bash
git submodule update --init --recursive
```

Then run the complete Python companion:

```bash
python examples/hgf_demo_full.py --output hgf_demo_python_summary.json
```

Optional plots:

```bash
python -m pip install '.[plot]'
python examples/hgf_demo_full.py --plots
```

The script follows the official demo sequence: Bayes-optimal fitting, binary simulation/recovery, prior editing and sampling, eHGF/uHGF, AR(1), Rescorla-Wagner, continuous HGF/eHGF/uHGF, residual diagnostics, and Bayesian parameter averaging.

See `docs/user/HGF_DEMO_COVERAGE.md` for the section-by-section mapping to frozen MATLAB evidence and the exact release interpretation.

## Focused official MATLAB demo reproductions

Two smaller self-checking examples expose the most important release-gated workflows directly:

```bash
python examples/matlab_demo_model_selection.py
python examples/matlab_demo_uhgf_ar1.py
```

`matlab_demo_model_selection.py` reproduces the official eHGF challenge from the frozen `demo/hgf_demo.m`: classic HGF is expected to reject the negative-posterior-precision regime while eHGF succeeds.

`matlab_demo_uhgf_ar1.py` reproduces the official uHGF → uHGF-AR(1) workflow and self-checks its descriptive level-3 extrema against the frozen MATLAB reference values using the release tolerances.

The Python examples do not require a MATLAB runtime. MATLAB is used only by the reference-aware CI workflows that regenerate and compare cross-language evidence.

See `docs/user/MATLAB_DEMOS.md` for exact MATLAB↔HGFX comparison results, workflow run IDs, artifacts, and interpretation.

Examples are part of the v1 release-readiness surface. The quick-start must run from a clean wheel installation without MATLAB; the full demo and focused reproductions are validated against the pinned reference inputs and their corresponding frozen evidence surfaces.
