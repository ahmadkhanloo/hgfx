# M18 S8 — HGF R0 optimizer localization

Status: **FROZEN DIAGNOSTIC / NO ACCEPTANCE EFFECT**

Protocol: `m18-s8-hgf-r0-optimizer-probe-1`

Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

Localize the demonstrated S7 HGFX-only optimizer mismatch in exactly one immutable paired-recovery case before any product repair.

This diagnostic does **not** change S7 acceptance, recovery thresholds, seeds, data, starts, model family, optimizer settings, or the frozen paired grid.

## Frozen case

- case: `PR-hgf_binary-T256-S0.35-R0`
- case SHA-256: `1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5`
- source protocol: `m18-s7-paired-recovery-1`
- original S7 run: `34856542785`
- original shard artifact: `m18-s7-shard-hgf-t256-s035`, artifact `10354120392`
- immutable data fixture: `reference/validation/m18_s7_paired_recovery/hgf_anomaly_fixture.json`
- model: `hgf_binary + unitsq_sgm`
- trials: `256`
- truth scale: `0.35`
- replicate: `0`
- seed: `47118`
- free transformed indices, zero-based: `[12, 13, 14]`
- start: `[-3, -6, log(48)]`
- optimizer: frozen `quasinewton_optim_config`
- numerical comparison: unchanged `rtol=3e-8`, `atol=3e-10`

The S7 anomaly review established that the MATLAB reference is stable to all six preregistered one-local-spacing start perturbations for this case, while shared endpoint objective evaluations pass. Therefore this case requires S8 optimizer localization rather than a reference-limitation disposition.

## Evidence exported

MATLAB exports the complete finite optimizer path and, at every finite optimizer state:

- `iter.x` and `iter.val`;
- Ridders gradient and gradient error with `min_steps=10`;
- stored inverse-Hessian state where available;
- reset indices;
- official final endpoint/value.

HGFX then:

1. reruns the exact immutable case;
2. reports first exact and first existing-gate path divergence;
3. evaluates objective and Ridders gradient at the exact MATLAB states;
4. compares stored inverse-Hessian states;
5. replays quasi-Newton step selection and BFGS transitions from exact MATLAB states.

## Diagnostic classifications

- `SHARED_STATE_OBJECTIVE_OR_GRADIENT_DIVERGENCE`: same-vector objective or Ridders gradient leaves the unchanged gate; localize numerical primitive/model evaluation before optimizer repair.
- `QUASINEWTON_STATE_ALGEBRA_MISMATCH`: shared-state objective/gradient pass but exact-state step/BFGS replay does not; repair optimizer state algebra.
- `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`: shared-state objective/gradient and exact-state transition replay pass, but the independent optimizer path diverges; localize amplification/termination/finite-difference runtime sensitivity without widening thresholds.
- `NO_REQUIRED_MISMATCH_REPRODUCED`: the frozen mismatch is not reproduced; evidence is insufficient for repair.
- `INSUFFICIENT_REFERENCE_EVIDENCE`: required trace/state evidence is incomplete.

None of these classifications closes S7 by itself. A product change must be preceded by a regression reproducing the demonstrated mismatch and followed by rerunning the affected S7 shard plus the aggregate paired-recovery gate.
