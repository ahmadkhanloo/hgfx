# REV-2.4 eHGF-019 end-of-phase CPU regression — one infrastructure-only retry kickoff (2026-11-10)

Reference [documented original two-OS full-CPU collection failure and one retry authorization](REV-2.4_EHGF019_FULL_REGRESSION_INFRA_RETRY_2026-11-10.md), commit `bc2900ce34891d909ae2ffa00950eeeffdc05f45`, before this trigger.

Original full CPU regression [run 42800906817](https://github.com/ahmadkhanloo/hgfx/actions/runs/42800906817) failed on both Linux and Windows at test collection (`ModuleNotFoundError: No module named 'tools'`) before numerical tests could execute. The only fix is to invoke the exact same `pytest` inventory as `python -m pytest -q --junitxml=regression-results.xml` from repository root, on both OSes; it changes only Python import path and **never model numerical behavior**. The general `.github/workflows/regression.yml` was similarly fixed to avoid recurrence.

**This one-shot run is CPU source unit/integration regression for development HGFX 1.1.0b1 only; NOT a new MATLAB paired science experiment, not original Panel G/E rerun, and no change to released HGFX v1.0.0.** Retain original failed run and any failure of the retry, with no further run-until-PASS loop. Original eHGF-019 issue and REV-2.4 global scientific gate remain BLOCKED, and D2/D3 not approved.
