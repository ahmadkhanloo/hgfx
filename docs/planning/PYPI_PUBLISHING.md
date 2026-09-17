# HGFX PyPI Publishing

Last synchronized: 2026-09-17
Status: **DONE / PASS — HGFX 1.0.0 published and independently verified from public PyPI**
Tracking: PV1-03 / issue #34
Frozen published source: `v1.0.0` -> `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
PyPI project: https://pypi.org/project/hgfx/1.0.0/

## Outcome

HGFX `1.0.0` is published to the public Python Package Index using PyPI Trusted Publishing with GitHub OIDC. No long-lived PyPI API token was used.

Public installation:

```bash
python -m pip install hgfx==1.0.0
```

The published distributions were built from the immutable release tag `v1.0.0`, not from the later post-release `main` tree.

## Frozen identity

```text
Distribution:    hgfx
Version:         1.0.0
Source tag:      v1.0.0
Source SHA:      4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27
Workflow:        .github/workflows/release-pypi.yml
Environment:     pypi
Authentication:  PyPI Trusted Publishing / GitHub OIDC
```

## Publication evidence

The manual publication run was executed from `main` at repository commit:

```text
8d46da2a559d869c693eb33602ac3fb0b49ab5eb
```

GitHub Actions run:

```text
PyPI Release
Run ID: 35207257208
Event: workflow_dispatch
Conclusion: success
```

Both required jobs completed successfully:

1. `Build, audit, and smoke-test distributions` — **PASS**
2. `Publish validated distributions to PyPI` — **PASS**

The publish job's `Publish to PyPI with Trusted Publishing` step completed successfully.

Before upload, the workflow:

- checked out the immutable `v1.0.0` source;
- verified tag/version consistency;
- hard-checked `v1.0.0` -> `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`;
- built wheel and source distribution;
- ran `twine check`;
- audited distribution contents for forbidden MATLAB/reference and VCS payloads;
- installed the built wheel in an isolated environment;
- ran the public API smoke test.

## Independent public-index verification

A separate workflow verifies that the package is actually installable from the public package index rather than only confirming that the upload action returned success.

Workflow:

```text
.github/workflows/verify-pypi.yml
```

Verification run:

```text
Verify PyPI Distribution
Run ID: 35207903084
Job: Clean install and smoke-test from public PyPI
Conclusion: success
Runner OS: Ubuntu 24.04.5 LTS
Python: CPython 3.12.14
```

The verification command used the public PyPI index explicitly:

```bash
python -m pip install --index-url https://pypi.org/simple --no-cache-dir "hgfx==1.0.0"
```

The runner downloaded and installed:

```text
hgfx-1.0.0-py3-none-any.whl
```

The final environment reported:

```text
Successfully installed hgfx-1.0.0
Public PyPI verification PASS: hgfx==1.0.0
```

The imported package resolved from the runner's installed `site-packages`, not from a repository checkout.

The verification also confirmed that the public APIs `fit_model`, `sim_model`, and `sample_model` are callable and that a minimal `fit_model` workflow returns finite LME and BIC values.

## Security and provenance rules

The following rules remain in force for future PyPI releases:

- Never move or recreate an existing release tag.
- Never publish a working-tree/main snapshot under an existing release version.
- The project version in `pyproject.toml` must exactly match the selected release tag (`v<version>`).
- Build wheel and sdist before publication.
- Run metadata validation and archive-content audit before upload.
- Clean-install and smoke-test the built wheel before upload.
- Use the dedicated GitHub environment `pypi`.
- Use Trusted Publishing / OIDC; do not add a long-lived PyPI token unless the publication architecture is explicitly changed and reviewed.
- Verify each newly published version independently from the public PyPI index.

## Exit gate

PV1-03 exit criteria are satisfied:

- **PASS:** build, metadata validation, content audit and local clean-install smoke test;
- **PASS:** Trusted Publishing without a long-lived PyPI token;
- **PASS:** `hgfx==1.0.0` available through public PyPI;
- **PASS:** clean external installation from `https://pypi.org/simple`;
- **PASS:** public API import and fit smoke test from the installed PyPI artifact;
- **PASS:** published package mapped to exact frozen `v1.0.0` source SHA;
- **PASS:** README installation instructions updated to use the public package.

**PV1-03 = DONE / PASS.**
