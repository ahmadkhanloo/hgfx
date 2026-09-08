# M12 — Complete Model Coverage Matrix

Status: **IN PROGRESS**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Corrected status semantics

- **DONE** — implementation + config/transform semantics + public export + frozen MATLAB parity.
- **IN_PROGRESS** — scientific family that must be implemented before M12 can pass.
- **PLOT_ONLY / DEPRECATED / NOT_APPLICABLE** — permitted only for non-scientific-model files.
- **REFERENCE_ONLY** — forbidden as a final status for scientific model families.

## Already DONE before reopening

- standard HGF / eHGF / uHGF, continuous and binary
- binary PU / PU-TBT HGF/eHGF/uHGF
- AR1 binary HGF/eHGF/uHGF
- RW / dual-RW
- Pearce-Hall
- Sutton K1
- Kalman
- HMM
- former P0/P1 observation families

## Scientific families still required

| Sub-gate | Family | Status |
|---|---|---|
| M12A | continuous AR1 HGF | IN_PROGRESS |
| M12B | binary MAB | IN_PROGRESS |
| M12B | continuous AR1 MAB | IN_PROGRESS |
| M12B | AR1 binary MAB HGF/eHGF/uHGF | IN_PROGRESS |
| M12C | JGET HGF/eHGF/uHGF | IN_PROGRESS |
| M12D | categorical HGF | IN_PROGRESS |
| M12D | categorical-normalized HGF | IN_PROGRESS |
| M12D | WhatWorld | IN_PROGRESS |
| M12D | WhichWorld | IN_PROGRESS |
| M12E | HHMM | IN_PROGRESS |
| M12F | Bayes-optimal continuous/binary/categorical/WhatWorld/WhichWorld | IN_PROGRESS |
| M12F | response-surprise belief/precision/precision-WhatWorld/surprise | IN_PROGRESS |
| M12F | squared prediction error | IN_PROGRESS |
| M12G | conditional hallucination obs 1/2/3 | IN_PROGRESS |
| M12G | WhatWorld logRT | IN_PROGRESS |
| M12G | world softmax / world mu3 softmax | IN_PROGRESS |

M12H will replace this table with final DONE/non-model classifications only after all scientific families have parity evidence.
