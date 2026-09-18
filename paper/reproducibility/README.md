# Paper reproducibility bundle

Protocol: `hgfx-paper-protocol-1` (`FROZEN_FOR_EXECUTION`)
Tracking: PV1-02 / issue #32

This package regenerates paper tables and figures from committed evidence.
It does not reopen historical M18, M19, or the v1.0.0 release gate.

## Frozen identities

| Item | Identity |
|---|---|
| HGFX product | `v1.0.0` / `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| PyPI | `hgfx==1.0.0` |
| MATLAB oracle | HGF Toolbox 8.2.0 / `2437f4dc241541072722a2695ddeca7b44d83dd3` |
| pyhgf comparator | `pyhgf==0.3.2` sdist SHA-256 `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d` |
| Paper protocol | `paper/reproducibility/PAPER_PROTOCOL.md` |

## What requires MATLAB

| Step | MATLAB required? |
|---|---|
| Install/use HGFX from PyPI | no |
| Regenerate P2 tables | no |
| Regenerate P5 figures | no |
| Replay P2A common-scope cell | no (`hgfx==1.0.0` and `pyhgf==0.3.2`) |
| Replay paired MATLAB oracle / M18C.2 | **yes** (GitHub Actions `matlab-actions`) |

## Environment

Python ≥ 3.11. Exact paper executions record resolved versions, not just lower bounds.

```bash
git clone --recurse-submodules https://github.com/ahmadkhanloo/hgfx.git
cd hgfx
git checkout v1.0.0   # product source for scientific claims
python -m pip install 'hgfx==1.0.0'
```

For regenerating paper artifacts from this repository (post-v1 paper commits):

```bash
git checkout main
python -m pip install -e '.[dev]' matplotlib
python scripts/verify_reference_freeze.py
```

## Regenerate paper tables (P2)

```bash
python paper/scripts/generate_p2_tables.py
```

Committed Markdown in `paper/tables/` must be identical. CI workflow `p2-paper-tables.yml` checks this.

## Regenerate paper figures (P5)

```bash
python paper/scripts/generate_p5_figures.py
```

Outputs: `paper/figures/*.png`, matching `.pdf` vector files, and `paper/figures/p5_figures_manifest.json`. PNG export is 300 dpi.

The P3 M18C.2 aggregate evidence is now committed and officially classified as `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`. The diagnostic horizon figure is still pending and, if P3 remains in the submission package, must be generated from that committed aggregate. Protocol 1 does not activate a performance/scaling figure.

## Replay the frozen pyhgf common-scope cell (P2A.10)

CPU, `JAX_ENABLE_X64=1`, `JAX_PLATFORMS=cpu`:

```bash
python -m pip install 'numpy==2.3.3' 'jax==0.6.2' 'jaxlib==0.6.2' 'hgfx==1.0.0' 'pyhgf==0.3.2'
python tools/run_p2a10_common_scope.py \
  --case paper/reproducibility/pyhgf_common_scope_case.json \
  --gate paper/reproducibility/pyhgf_final_semantic_gate.json \
  --output-dir /tmp/p2a10
```

Compare canonical `raw_result_sha256` to `202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b`.

## Paired MATLAB oracle / trial-horizon study (P3)

GitHub Actions workflow `PV1-01 M18C.2 Horizon Analysis`, `workflow_dispatch` with `execute_full=true`.
MATLAB is provisioned by `matlab-actions/setup-matlab@v2`. Local MATLAB is not required.

## Frozen v1 validation

See `docs/validation/V1_EVIDENCE_INDEX.md` and `reference/validation/v1_release/`.
Historical M18 FAIL and D02/D08 `REFERENCE_LIMITATION_MATCH` records are immutable.

## Claim audit

Every numerical manuscript sentence must map through `docs/research/PAPER_EVIDENCE_MAP.md`.
Do not transcribe numbers by hand from chat or screenshots.
