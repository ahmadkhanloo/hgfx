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
| Re-run historical M18C.2 from its recorded historical revision | **yes** (MATLAB required; historical workflow only, not dispatchable from current HEAD) |

## Environment

Paper-gate regeneration uses Python 3.11 with `numpy==2.3.3`, `matplotlib==3.10.9`, and `pytest>=8`, matching the active P5/P6A workflows. Specialized historical/comparator executions keep their own recorded environments; do not substitute the generic development environment for a frozen protocol.

```bash
git clone --recurse-submodules https://github.com/ahmadkhanloo/hgfx.git
cd hgfx
git checkout v1.0.0   # product source for scientific claims
python -m pip install 'hgfx==1.0.0'
```

For regenerating paper artifacts from this repository (post-v1 paper commits):

```bash
# Use the exact locked submission candidate recorded in docs/research/P8_REVIEW_PACKET.md
git checkout <P8-candidate-SHA>
python -m pip install -e '.[dev]' 'numpy==2.3.3' 'matplotlib==3.10.9' 'pytest>=8'
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

Outputs: `paper/figures/*.png`, matching `.pdf` vector files, and `paper/figures/p5_figures_manifest.json`. PNG export is 300 dpi. Publication zero-diff generation is gated on Ubuntu; portability tests generate into a temporary directory and compare deterministic manifest semantics without mutating committed figures. Manifest paths are POSIX-normalized, and submission-critical JSON inputs are LF-normalized through `.gitattributes`.

The P3 M18C.2 aggregate evidence is committed at `paper/reproducibility/p3_m18c2_aggregate_35272347167.json` with SHA-256 `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`; Actions provenance is recorded in `p3_m18c2_provenance_35272347167.json`. It is officially classified as `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`. Figure 6 (`paper/figures/fig_p3_horizon_diagnostics.png`) is generated directly from this machine-readable aggregate and is zero-diff gated by the P5 workflow; it remains diagnostic-only evidence and does not establish identifiability. Protocol 1 does not activate a performance/scaling figure.

## Generate the P6A draft paper-evidence manifest

```bash
python paper/scripts/generate_p6a_manifest.py
pytest -q tests/paper/test_p6a_manifest.py
```

Output: `paper/reproducibility/p6a_paper_evidence_manifest.json`.

Current status is `DRAFT_NOT_FROZEN`. The authoritative inventory count is the `file_count` recorded in `p6a_paper_evidence_manifest.json`; P6A-1/P6A-2 use canonical Git-byte SHA-256 values, so hashes are independent of checkout line-ending policy. The numerical claim audit is complete with zero unmapped current manuscript claim lines, and the manifest explicitly preserves failed, reference-limitation and NDC outcomes. It must not be promoted to `FROZEN_FOR_SUBMISSION` until an exact P7 candidate is locked and independent P8 records PASS for that exact candidate SHA.

Regenerate the current numerical claim audit before the manifest:

```bash
python paper/scripts/generate_p6a_claim_audit.py
python paper/scripts/generate_p6a_manifest.py
pytest -q tests/paper/test_p6a_claim_audit.py tests/paper/test_p6a_manifest.py
```

## Replay the frozen pyhgf common-scope cell (P2A.10)

CPU only. These environment variables are mandatory; the runner rejects the execution if they are absent:

```bash
export JAX_ENABLE_X64=1
export JAX_PLATFORMS=cpu
python -m pip install 'numpy==2.3.3' 'jax==0.6.2' 'jaxlib==0.6.2' 'hgfx==1.0.0' 'pyhgf==0.3.2'
python tools/run_p2a10_common_scope.py \
  --case paper/reproducibility/pyhgf_common_scope_case.json \
  --gate paper/reproducibility/pyhgf_final_semantic_gate.json \
  --output-dir /tmp/p2a10
```

Compare canonical `raw_result_sha256` to `202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b`.

## Paired MATLAB oracle / trial-horizon study (P3)

Historical P3 execution is preserved in `paper/reproducibility/p3_m18c2_aggregate_35272347167.json` and `paper/reproducibility/p3_m18c2_provenance_35272347167.json` (workflow run `35272347167`). The original execution workflow is not present at this revision, so do **not** attempt to dispatch it from current HEAD. Regenerate paper-facing tables/figures from the committed aggregate using the commands above. Reproducing the original MATLAB execution requires the historical workflow/source recorded by the provenance file; that historical workflow specified the MATLAB release as `latest`, so the exact MATLAB release used by that old run was not preserved and the historical execution is not version-reproducible beyond its committed outputs/provenance.

## Backend / GPU evidence provenance

The physical-GPU applicability record at `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` is a retained pre-release run from source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`. Two Tesla T4 devices were visible; the required fitting cells executed on `cuda:0`. JAX device placement establishes residency and `nvidia-smi -L` records device enumeration. The retained GPU result is correctness/applicability evidence, not a speed or scaling benchmark.

The host-libm remediation changed the NumPy compatibility path, so the CPU compatibility-versus-JAX-CPU leg is remeasured separately on post-fix code rather than inheriting the pre-release CPU summary. The canonical Ubuntu execution is Actions run `36255732941` at source `0a40e7081421c0ad66ea45f852f11bd823cc9d51`, Python 3.12.14, JAX/JAXLIB 0.11.1. Two repeated runs were byte-identical (SHA-256 `f5ad2c412a8ad9f6325e45e2398ec46f54bcb13bba64ebe12827033d8aeedfab`); the maximum fit-objective gap is `0.006783711260709424` against the unchanged `0.1` criterion. The committed machine-readable artifact `gpu_validation_results/m18_s9_cpu_postfix_revalidation.json` is the source for the CPU bar in Figure 4.

## Frozen v1 validation

See `docs/validation/V1_EVIDENCE_INDEX.md` and `reference/validation/v1_release/`.
Historical M18 FAIL and D02/D08 `REFERENCE_LIMITATION_MATCH` records are immutable.

## Claim audit

Every numerical manuscript sentence must map through `docs/research/PAPER_EVIDENCE_MAP.md`.
Do not transcribe numbers by hand from chat or screenshots.

The immutable submission candidate is the Git commit that contains the final draft manifest. The P8 review packet records that commit identity after candidate lock; reproduction must use that recorded immutable revision rather than a moving branch.
