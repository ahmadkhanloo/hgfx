# Reference Layer

This directory stores immutable metadata and golden outputs for HGFX validation against the frozen MATLAB HGF reference.

It must **not** contain an uncontrolled copy of upstream source.

## Frozen MATLAB compatibility reference

HGFX v1 is specified against:

- HGF Toolbox `8.2.0`
- commit `2437f4dc241541072722a2695ddeca7b44d83dd3`
- development/validation submodule: `external/hgf-toolbox/`

The frozen registry is:

```text
HGF_VERSION
HGF_COMMIT
matlab_manifest.tsv
matlab_checksums.tsv
```

`matlab_manifest.tsv` contains every frozen MATLAB `.m` path plus its Git blob SHA and byte size. `scripts/verify_reference_freeze.py` verifies that the initialized submodule exactly matches this registry. `tools/check_v1_source_classification.py` additionally requires a release disposition and evidence for all 334 frozen MATLAB sources; unknown files fail the gate.

Golden fixtures belong in `reference/golden/` and validation evidence belongs under `reference/validation/`.

## PyHGF status

PyHGF was evaluated as a possible reuse/interoperability source during planning, but it is **not used as a dependency or fork for the HGFX v1 release**. MATLAB HGF Toolbox 8.2.0 is the compatibility oracle.

For that reason:

```text
PYHGF_VERSION = NOT_USED_FOR_V1_RELEASE
PYHGF_COMMIT  = NOT_USED_FOR_V1_RELEASE
```

These markers are deliberate release metadata, not unresolved placeholders.
