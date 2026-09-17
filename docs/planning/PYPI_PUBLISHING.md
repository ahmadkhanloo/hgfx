# HGFX PyPI Publishing

Last synchronized: 2026-09-17
Status: **IN PROGRESS — workflow prepared; PyPI Trusted Publisher setup and final publish pending**
Tracking: PV1-03 / issue #34
Frozen initial source: `v1.0.0` -> `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`

## Goal

Publish HGFX to the public Python Package Index without rewriting the frozen `v1.0.0` tag and without storing a long-lived PyPI API token in GitHub.

The publishing mechanism is PyPI Trusted Publishing (GitHub OIDC). The release workflow lives on `main`, but the package build checks out the immutable selected release tag. For the initial publication that source is exactly `v1.0.0`.

## Security and provenance rules

- Never move or recreate `v1.0.0`.
- Never publish a working-tree/main snapshot as `1.0.0`.
- `v1.0.0` must resolve to `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- The project version in `pyproject.toml` must exactly match the selected tag (`v<version>`).
- Build wheel and sdist before any publish step.
- Run `twine check` on all distributions.
- Reject distributions containing the frozen `external/hgf-toolbox` source payload or VCS internals.
- Install the built wheel in an isolated virtual environment and execute the public API smoke test before upload.
- The publish job receives only `id-token: write`; no PyPI password/API-token secret is required.
- Publication uses the dedicated GitHub environment `pypi`.

## GitHub workflow

Workflow file:

```text
.github/workflows/release-pypi.yml
```

Manual inputs:

- `source_ref`: immutable release tag/ref; initial value `v1.0.0`.
- `publish`: `false` performs build/audit/smoke only; `true` enables the PyPI upload job after all validations pass.

The initial `v1.0.0` workflow additionally hard-checks the frozen release SHA.

## One-time action required in PyPI

### If `hgfx` does not yet exist on PyPI

Use a **Pending Trusted Publisher**. In your PyPI account, open the account-level **Publishing** page and add a GitHub publisher with exactly:

```text
PyPI project name: hgfx
GitHub owner:       ahmadkhanloo
Repository name:    hgfx
Workflow name:      release-pypi.yml
Environment name:   pypi
```

Do not create or move the Git tag during this step. A pending publisher does not reserve the project name until the first successful publish.

### If `hgfx` already exists and is controlled by this account

Open the project's **Manage -> Publishing** page and add a GitHub Trusted Publisher using the same values:

```text
GitHub owner:       ahmadkhanloo
Repository name:    hgfx
Workflow name:      release-pypi.yml
Environment name:   pypi
```

If `hgfx` exists but is owned by an unrelated party, stop publication and choose a new distribution name before changing package metadata. Do not publish under an ambiguous or unauthorized namespace.

## Recommended GitHub environment setup

In repository settings, create an environment named exactly:

```text
pypi
```

Where the account/repository plan supports it, add a required reviewer for the environment. This makes the final upload an explicit approval point even after the workflow has been dispatched.

No PyPI token should be added to GitHub Secrets for this workflow.

## Execution sequence

1. Merge the PV1-03 publishing workflow into `main` only after its PR build/audit/smoke job passes.
2. Configure the PyPI Trusted Publisher with the exact identity above.
3. From GitHub Actions, open **PyPI Release** and choose **Run workflow**.
4. First run with:

```text
source_ref = v1.0.0
publish    = false
```

5. Confirm the build/audit/smoke job passes and that the validated artifact is named `pypi-distributions-1.0.0`.
6. Run the workflow again with:

```text
source_ref = v1.0.0
publish    = true
```

7. Approve the `pypi` environment deployment if GitHub requests an environment reviewer.
8. After upload, verify from a clean environment:

```bash
python -m venv /tmp/hgfx-pypi-verify
source /tmp/hgfx-pypi-verify/bin/activate
python -m pip install --upgrade pip
python -m pip install hgfx==1.0.0
python -c "import hgfx; from importlib.metadata import version; print(version('hgfx')); print(hgfx.__file__)"
```

9. Record the final PyPI URL/version and successful clean-install evidence in issue #34 and the release provenance docs.
10. Only after public installation is verified should README installation instructions be changed from source-install-first to `pip install hgfx`.

## Expected first-publication identity

```text
Distribution: hgfx
Version:      1.0.0
Source tag:   v1.0.0
Source SHA:   4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27
Workflow:     release-pypi.yml
Environment:  pypi
Authentication: PyPI Trusted Publishing / GitHub OIDC
```

## Exit gate

PV1-03 is **DONE / PASS** only when all of the following are true:

- build, metadata validation, content audit and clean-install smoke test pass;
- Trusted Publishing succeeds without a long-lived PyPI token;
- `hgfx==1.0.0` is visible on public PyPI;
- a clean external environment installs `hgfx==1.0.0` from PyPI and the public API imports successfully;
- the published package maps to the exact frozen `v1.0.0` source SHA;
- README/user installation documentation is updated after verification.
