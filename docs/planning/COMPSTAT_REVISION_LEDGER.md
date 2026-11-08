# Computational Statistics revision ledger

**Scope:** `COMPSTAT_REVISION_PLAN.md`; working branch `compstat-revision`.
**Baseline main commit:** `46fe45e1fdd110a0e72a6dc661bf05c9c38e8885` (2026-11-08).
**Historical release evidence:** HGFX v1.0.0 at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; immutable.
**Phase:** REV-0 in progress. No REV task has a terminal `FIXED`, `EXPLAINED`, or `DOCUMENTED_LIMITATION` report yet.
**Gate:** NOT PASSED. Required baseline tag and complete audit execution remain to be verified.

## REV-0.3 verified repository inventory (2026-11-09)

| Plan expectation | Checked result at baseline | Status |
|---|---|---|
| Revision branch | `compstat-revision` created from recorded `main` SHA | CREATED |
| `pre-compstat-revision` tag | Not present in Git refs; connected GitHub tools cannot create tags | HUMAN_ACTION / OPEN |
| MATLAB oracle workflows | `.github/workflows/m18-s7-paired-recovery.yml`, `m18-d02-matlab-self-sensitivity.yml`, `m18-d08-matlab-self-sensitivity.yml`, `m18-scientific-validation.yml` and more | PRESENT; execution NOT VERIFIED |
| GPU capability | Historical physical T4 result in `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` | HISTORICAL EVIDENCE PRESENT; current runner UNKNOWN |
| `evidence/s7_aggregate.json` | No `evidence/` tree on `main`; `reference/validation/m18_s7_reference_limitation/decision.json` summarizes S7; raw shards are workflow artifacts | EXPECTED FILE MISSING; RAW AVAILABILITY NOT VERIFIED |
| `evidence/published_input_41809919116.json` | Not in `main` tree | MISSING |
| `empirical_example/`, `worked_example/` | Neither present in `main` tree | MISSING |
| `Manuscript.tex` and `ESM_1.tex` | No committed `.tex` files; active journal source: `paper/computational_statistics/manuscript.md`, supplement `paper/SUPPLEMENTARY_APPENDICES.md` | MARKDOWN BASELINE; TeX NOT CREATED |
| Frozen paired model selection | `reference/validation/m18_s7_reference_limitation/decision.json`: 36/36 BIC winners, balanced accuracy 0.583333... | JSON SOURCE PRESENT |
| P3 horizon integrity | `paper/reproducibility/p3_m18c2_aggregate_35272347167.json`: 10/72 discordant | JSON SOURCE PRESENT; gate FAILED historically |
| Physical T4 objective agreement | `gpu_validation_results/m18_s9_physical_gpu_revalidation.json`: 1.4210854715202004e-14 max gap, fixed 1e-7 criterion | JSON SOURCE PRESENT; no timing claim |
| Performance `182.001 s`, warnings `86`, blocks `324` | No direct JSON key verified in current checkout for these manuscript-plan example numbers | UNMAPPED; do not assert provenance |

## REV-0.4 implementation notes

- `tools/check_manuscript_claims.py` audits numeric tokens in current Markdown inputs by default and accepts explicit `--source` paths for later TeX.
- `docs/planning/COMPSTAT_CLAIM_MAP.json` maps an initial subset of article numbers to JSON pointers. SHA-256 is computed from actual file bytes at execution.
- **Strict mode fails** on either missing mappings or evidence mismatches; `--allow-unmapped` is a REV-0 inventory mode and must never be interpreted as final 100% verification.
- Run `python tools/check_manuscript_claims.py --allow-unmapped --json-out /tmp/compstat-claims.json` to collect baseline coverage; run without the flag to enforce the final gate.
- MATLAB, GPU, physical runtime, and all new experiments are deliberately untouched in REV-0.

## Task reports (append only on terminal resolution; maximum 15 lines per task)

Task report format: ID · `FIXED|EXPLAINED|DOCUMENTED_LIMITATION` · actions · evidence paths and SHA-256 · manuscript numbers · open limitations · time spent.

No terminal reports yet. Recording an inventory is not a claim that REV-0 gate passed.
