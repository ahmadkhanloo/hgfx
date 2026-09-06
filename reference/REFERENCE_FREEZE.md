# HGF Reference Freeze

HGFX freezes the MATLAB HGF reference before scientific porting begins.

## Frozen reference

- Repository: `https://github.com/ComputationalPsychiatry/hgf-toolbox`
- Version: `8.2.0`
- Exact commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Release date: `2026-04-21`
- Upstream license: MIT
- MATLAB files: `334`

The exact commit SHA—not a moving branch—is the scientific source of truth.

## Integrity evidence

`reference/matlab_manifest.tsv` records every MATLAB source path, its Git blob SHA, and byte size from the frozen commit. Git blob IDs are content-addressed hashes, so this registry verifies exact source identity without depending on filenames alone.

For publication artifacts, `scripts/build_sha256_checksums.py` can additionally generate SHA-256 checksums from the initialized submodule.

## Development layout

The reference is pinned as a Git submodule at `external/hgf-toolbox/`.

Runtime target remains:

```text
MATLAB dependency = 0
```

## Verification

```bash
git submodule update --init
python scripts/verify_reference_freeze.py
```

Do not update the submodule during the 8.2.0 compatibility program.
