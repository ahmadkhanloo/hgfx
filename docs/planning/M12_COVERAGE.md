# M12 — Complete Model Coverage Matrix

Status: **PASS**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Final status semantics

- **DONE** — implementation + config/transform semantics + public export + frozen MATLAB parity.
- **PLOT_ONLY / DEPRECATED / NOT_APPLICABLE** — permitted only for non-scientific-model files.
- **REFERENCE_ONLY** — forbidden for scientific model families.

## Final scientific coverage

| Sub-gate | Family | Status |
|---|---|---|
| M12A | continuous AR1 HGF | DONE |
| M12B | binary MAB | DONE |
| M12B | continuous AR1 MAB | DONE |
| M12B | AR1 binary MAB HGF/eHGF/uHGF | DONE |
| M12C | JGET HGF/eHGF/uHGF | DONE |
| M12D | categorical HGF | DONE |
| M12D | categorical-normalized HGF | DONE |
| M12D | WhatWorld | DONE |
| M12D | WhichWorld | DONE |
| M12E | HMM + HHMM | DONE |
| M12F | Bayes-optimal continuous/binary/categorical/WhatWorld/WhichWorld | DONE |
| M12F | response-speed belief/precision/precision-WhatWorld/surprise | DONE |
| M12F | squared prediction error | DONE |
| M12G | conditional hallucination obs 1/2/3 | DONE |
| M12G | WhatWorld logRT | DONE |
| M12G | world softmax / world mu3 softmax | DONE |
| M12H | config/transform/public API/inventory/regression closure | DONE |

Previously completed standard HGF/eHGF/uHGF, PU/PU-TBT, AR1-binary, RW/dual-RW, Pearce-Hall, Sutton K1, Kalman, HMM, and P0/P1 observation families remain DONE.

## Exhaustive frozen inventory

```text
DONE files=259
REFERENCE_ONLY files=0
DONE families=53
REFERENCE_ONLY families=0
```

No scientific perceptual or observation family remains `REFERENCE_ONLY`.

## Evidence

- M12A: `34224773192`
- M12B/C: `34224773186`
- M12D/E: `34225650007`
- M12F/G: `34225649883`
- config/prior parity: `34224773097`
- full closure/regression: `34225650015`
- M1 golden/regression revalidation: `34224773168`

Frozen source defects and minimal oracle repairs are documented in `M12_SOURCE_DEFECTS.md`.
