# Reference Layer

This directory stores immutable metadata and golden outputs from the frozen MATLAB HGF reference.

It should **not** contain an uncontrolled copy of upstream source.

Preferred development setup:

```text
external/hgf-toolbox/
```

as a pinned Git submodule.

Required files after Phase 0:

```text
HGF_VERSION
HGF_COMMIT
PYHGF_VERSION
PYHGF_COMMIT
matlab_manifest.tsv
matlab_checksums.tsv
```

Golden fixtures belong in `reference/golden/`.
