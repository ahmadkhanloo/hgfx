# Paper

Status: **PRE-M19 / manuscript evidence not frozen**

This directory will contain the manuscript assets for the HGFX methods/software-methods paper. The manuscript may be outlined before M19, but final numerical Results/Discussion claims must not be treated as frozen until **M19 — Methods Paper Dataset Frozen**.

## Current paper objective

The primary v1 paper claim is **validated Python reproduction of the frozen MATLAB HGF Toolbox 8.2.0 scientific/workflow behavior**, with scalable JAX/CPU/GPU/batch/multi-GPU execution as secondary contributions where scientific behavior is preserved.

The current source of truth for paper planning is:
- `docs/research/LEVEL2_PAPER_PLAN.md` — manuscript positioning, research questions and experiment plan;
- `docs/research/PAPER_EVIDENCE_MAP.md` — live mapping from candidate claims to repository evidence;
- `docs/research/RESEARCH_LOG.md` — paper-relevant decisions and interpretation changes;
- `docs/research/BENCHMARK_PLAN.md` — benchmark/provenance rules;
- `docs/planning/V1_PRODUCT_DEFINITION.md`, `V1_RELEASE_GATE.md`, `V1_TODO.md` and `M18_COMPLETION_PLAN.md` — current product/release authority.

## Current readiness

- Manuscript outline/methods text: may be developed now.
- Final equivalence Results: **BLOCKED** by open M18 closure items, currently D02_fit and D08_fit among the official nine-case workflow set plus later S6–S10 requirements.
- Final recovery Results: **OPEN** pending paired product-level MATLAB/HGFX recovery.
- Final performance headline results: **PROVISIONAL** until final backend applicability audit and M19 benchmark freeze.
- Final tables/figures: **DO NOT FREEZE YET**.

## Planned structure

```text
paper/
  manuscript.md              # create when drafting begins
  figures/                   # generated from frozen machine-readable results
  tables/                    # generated, not manually transcribed
  scripts/                   # figure/table regeneration
  supplement/                # extended matrices, environments, numerical case studies
```

## Evidence discipline

Do not copy transient debugging values directly into final manuscript results. Paper-used numerical claims must be traceable through `PAPER_EVIDENCE_MAP.md` to a gate/protocol, code SHA, run/job or equivalent provenance, artifact and artifact hash.

Historical failed experiments remain part of the scientific record. A later protocol or repair does not rewrite prior failures.

At M19, record the exact code/reference SHAs, datasets, configs, seeds/drivers, protocol versions, environments and machine-readable evidence set, then regenerate all final tables and figures from that frozen set.
