# Research Log

This log records paper-relevant scientific and engineering decisions. It is not a substitute for gate documents or raw evidence. Historical failures are preserved; entries summarize decisions without rewriting prior results.

## 2026-09-13 — v1 paper objective aligned to MATLAB-equivalent product objective
- **Question:** What should the paper claim as the primary contribution of HGFX v1?
- **Alternatives:** (a) primarily a differentiable/GPU HGF implementation; (b) primarily a Python replacement of the MATLAB HGF Toolbox with validated workflow/scientific equivalence, with GPU/differentiability as secondary contributions.
- **Evidence:** `docs/planning/V1_PRODUCT_DEFINITION.md`, `V1_RELEASE_GATE.md`, `M18_COMPLETION_PLAN.md`, current validation matrices.
- **Decision:** Use (b). The paper must first establish equivalence to the frozen MATLAB HGF Toolbox 8.2.0 reference; acceleration/scaling claims are conditional on preserved scientific behavior.
- **Consequence:** `LEVEL2_PAPER_PLAN.md` and the paper evidence map are organized around reference/workflow equivalence before performance.
- **Related:** issue #24; PR #26.

## 2026-09-13 — frozen MATLAB reference is the compatibility oracle
- **Question:** Which implementation defines v1 compatibility behavior?
- **Alternatives:** current MATLAB installation behavior without pinning; formula-level equivalence; frozen source-level MATLAB reference.
- **Evidence:** reference freeze files and submodule.
- **Decision:** HGF Toolbox 8.2.0 at commit `2437f4dc241541072722a2695ddeca7b44d83dd3` is the frozen oracle.
- **Consequence:** Paper comparisons must identify the exact reference commit and use matched model/config/data/parameter/workflow settings.
- **Related:** M0, `reference/REFERENCE_FREEZE.md`.

## 2026-09-13 — historical M18 FAIL must remain visible
- **Question:** Should redesigned identifiability-aware recovery protocols replace the historical failed M18 recovery result?
- **Alternatives:** overwrite/reclassify historical M18; preserve historical result and report redesigned protocol separately.
- **Evidence:** M18, M18A and M18B gate documents.
- **Decision:** Preserve the historical M18 scientific result as FAIL. M18B integrity/protocol PASS is separate evidence and does not retroactively convert the historical experiment into PASS.
- **Consequence:** The paper must distinguish historical recovery failure, protocol diagnosis, redesigned validation and final paired product-level recovery.
- **Related:** `M18_GATE.md`, `M18A_GATE.md`, `M18B_GATE.md`.

## 2026-09-13 — MATLAB reference limitations may be matched, not repaired silently
- **Question:** Must HGFX v1 outperform or repair every MATLAB limitation?
- **Alternatives:** force every HGF variant to pass; match documented MATLAB model-family selection/limitations; silently substitute a different model family.
- **Evidence:** MATLAB demo/model-selection evidence and reference-limitations policy.
- **Decision:** A demonstrated exact MATLAB limitation can be classified `REFERENCE_LIMITATION_MATCH` when HGFX matches the same limitation and no earlier HGFX-only divergence exists. If the official MATLAB workflow selects eHGF/uHGF/specialized models, HGFX should mirror that selection rather than force base HGF.
- **Consequence:** The paper must not describe matched reference limitations as scientific success of the underlying model; they are compatibility evidence.
- **Related:** `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, D02 model-selection evidence.

## 2026-09-13 — implementation parity and scientific identifiability are distinct
- **Question:** Does failed parameter recovery imply a porting error?
- **Alternatives:** treat all recovery failure as implementation mismatch; separate software parity from model/data identifiability.
- **Evidence:** M18A/M18B diagnosis and paired-reference policy.
- **Decision:** Separate implementation mismatch, optimizer/numerical mismatch, model-selection mismatch, scientific/model limitation and insufficient reference evidence.
- **Consequence:** Paper recovery sections must use paired MATLAB/HGFX evidence before attributing failure to HGFX.
- **Related:** M18 completion plan classification procedure.

## 2026-09-13 — physical GPU evidence is required for GPU claims
- **Question:** Can CPU tests or mocked devices support GPU validation claims?
- **Alternatives:** accept emulated/mock evidence; require physical device evidence.
- **Evidence:** M14–M17 gate policy and recorded H100 runs.
- **Decision:** GPU claims require physical GPU execution with hardware, driver/runtime, command, commit and result provenance. Shared/contended hardware is acceptable when documented and the criterion does not require uncontended peak performance.
- **Consequence:** Paper performance/backend sections must cite physical-GPU evidence and distinguish compatibility from throughput.
- **Related:** `M14_M16_H100_GPU_EVIDENCE.md`, `M17_H100_GPU_EVIDENCE.md`.

## 2026-09-13 — D02 exposed consequential cross-runtime floating-point sensitivity
- **Question:** Why can a tiny elementary-function/runtime difference produce a large fitted-parameter divergence?
- **Alternatives:** relax fitting tolerance; change optimizer settings; diagnose the first upstream numerical divergence under the unchanged MATLAB-compatible workflow.
- **Evidence:** regression-first commit `27bba3e44aae832e8805d25a631ebac15f81f40f`; compatibility repair commit `7b43ae5e45f85f44d23a6e980200baca46609fbd`; diagnostic head `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`; run `34776952053`, job `103776700085`, artifact `10323968264`, artifact SHA-256 `ac4d0094cfe49b5e5ee8d5c75f89311c35a2727b46ed433078412be63c3b5f9c`.
- **Observed evidence:** prior terms are exact at the selected Ridders samples. After the MATLAB-compatible `exp` repair, the residual selected D02 case is classified `FORWARD_NUMERICAL_DIVERGENCE`; `inf_states` max absolute difference is `7.105427357601002e-15`, observation input difference `1.1102230246251565e-16`, per-trial log-likelihood difference `2.4868995751603507e-14`, while replaying the observation calculation on exact MATLAB state yields zero log-likelihood difference. A tiny replay primitive difference appears in `pow1mx` (`6.776263578034403e-21`) but does not change replayed log-likelihood.
- **Decision:** Continue regression-first localization in the forward eHGF path. Do not change thresholds, seeds, datasets, model family, starts, Ridders settings or quasi-Newton settings to force agreement.
- **Consequence:** D02 is a candidate numerical-reproducibility case study for the supplement/main discussion only if the final repair/evidence remains scientifically relevant. It is not yet a closed paper result.
- **Related:** PR #26; M18 S4/S8.

## 2026-09-13 — current official workflow closure remains 7/9
- **Question:** Is the MATLAB-equivalent fitting/demo surface closed?
- **Evidence:** run `34776952053` / job `103776700085` at head `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`.
- **Decision/status:** **IN PROGRESS — 7/9 PASS**. D01_bayes, D01_fit, D03_fit, D05_fit, D06_bayes, D06_fit and D07_fit pass. D02_fit and D08_fit remain `OPTIMIZER_MISMATCH` under the unchanged gate.
- **D02 detail:** reference point PASS, initial Ridders PASS, MATLAB-path objective replay PASS; final fitting diverges after numerical-path amplification.
- **D08 detail:** optimizer trace and MATLAB-path objective replay PASS; current frozen mismatch is `fit.traj.epsi` near index `(178,1)`.
- **Consequence:** No manuscript claim may state complete fitting/workflow equivalence yet.
- **Related:** artifact `10323968264`.

## 2026-09-13 — paper dataset/results freeze deferred to M19
- **Question:** Should paper tables/results be finalized while M18 product closure is still open?
- **Alternatives:** draft final results now; freeze only after required v1 evidence is closed.
- **Decision:** Final paper dataset/results freeze occurs at M19 only. Manuscript structure and methods text may evolve earlier, but final numerical claims, tables and figures remain provisional.
- **Consequence:** M19 records exact code/reference SHAs, protocols, datasets, environments, run/job/artifact IDs, hashes and regeneration scripts.
- **Related:** M19 — Methods Paper Dataset Frozen.
