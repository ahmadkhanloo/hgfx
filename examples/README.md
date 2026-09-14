# HGFX examples

These examples exercise only release-supported behavior.

## Quick start

From a source checkout:

```bash
python -m pip install .
python examples/quickstart.py
```

The quick-start example fits the validated `hgf_binary + unitsq_sgm` workflow through the public `hgfx.fit_model` API and prints basic fit statistics.

Examples are part of the v1 release-readiness gate: they must run from a clean wheel installation without MATLAB on the runtime path.
