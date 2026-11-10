# REV-2.4 eHGF-019 maintenance — full Linux/Windows CPU regression kickoff (2026-11-10)

**Authoritative scope:** Development worktree `1.1.0b1` eHGF-only NaN precision compatibility patch `e6eb57fdc037aeb0d0c5776ed0fb07ee3cccbad6`, under [prospective maintenance plan](../../../docs/research/REV24_EHGF019_MAINTENANCE_FIX_PLAN_2026-11-10.md). This run tests **only the current repository CPU suite** and frozen reference source hashes, not any new original MATLAB/HGFX numerical science and not the exhausted original 600-case/one-case diagnostic protocols.

- Original pre-fix golden [CI 42799735544](https://github.com/ahmadkhanloo/hgfx/actions/runs/42799735544) **expected fail** (1 original scalar precision failure).
- Post-fix [CI 42799847334](https://github.com/ahmadkhanloo/hgfx/actions/runs/42799847334) 7/7 unit PASS and expanded [CI 42799998082](https://github.com/ahmadkhanloo/hgfx/actions/runs/42799998082) 22/22 unit PASS.
- **One full CPU regression per OS** (Ubuntu 24.04, Windows latest), source branch 1.1.0b1 exact kickoff HEAD, pinned HGF 8.2.0 *source inventory* 334 files only; archive all JUnit PASS/FAIL. No optimizer evidence should be converted to a scientific paper PASS.
- Original scientific REV-2.4 remains `NOT_GLOBAL_PASS`; original 1.0.0 one-sided-invalid eHGF019 and every historical failed fit/grid preserved. No new MATLAB model objective or original Panel G/E/diagnostic rerun allowed.

After the one-shot workflow launches, remove automatic push trigger to avoid an unbounded regression loop. Document actual run IDs and results in the project ledger before further work.
