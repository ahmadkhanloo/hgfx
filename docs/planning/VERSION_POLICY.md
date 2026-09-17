# HGFX version policy

Recorded: 2026-09-18
Status: **v1 FROZEN / v2 NOT STARTED — current owner decision, not a release gate**
Authority: this file is the product-line decision record. It does not reopen the v1.0.0 scientific gate.

Immutable v1 source: `v1.0.0` → `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
Frozen MATLAB oracle: HGF Toolbox 8.2.0 → `2437f4dc241541072722a2695ddeca7b44d83dd3`
PyPI: `hgfx==1.0.0`

## Decision in one paragraph

HGFX v1 is the locked MATLAB-compatibility product and the claim of the first methods paper: a validated Python/JAX reproduction of the frozen HGF Toolbox 8.2.0 scientific and workflow contract, with no MATLAB runtime for users. pyhgf is a different design center (generalized / nodal predictive-coding networks) and is not the competitor v1 tries to beat. v2 is not open. The current owner decision is that a future v2, if started at all, would be a native Python modeling layer on top of the v1 core after a second scientific question exists — not a precision contest with MATLAB or pyhgf, and not a silent change to v1 behavior.

## v1 — frozen compatibility line

These points are accepted and must not be revised by later feature work.

1. **Product identity.** v1 is a TAPAS/HGF Toolbox compatibility surface in Python/JAX. It is not a generic new HGF library and is not a GPU-performance product.
2. **Scientific ceiling for v1.** Matching the frozen MATLAB 8.2.0 oracle is the acceptance criterion. Higher mathematical precision that would change reference behavior is out of scope for v1.
3. **Release immutability.** Tag `v1.0.0` and commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` do not move. Later `main` commits are post-release documentation, publication assets, or v1.x maintenance. They do not rewrite frozen evidence.
4. **v1.x maintenance only.** Allowed on the compatibility line: bugfixes that restore the frozen contract, portability, packaging, documentation, and citation metadata. Forbidden: new model semantics, tolerance inflation, retuning failed experiments into PASS, and headline speed/scaling claims.
5. **Evidence honesty.** Historical M18 FAIL stays FAIL. D02/D08 and exact-grid S7 recovery stay `REFERENCE_LIMITATION_MATCH` where that is the recorded class. Shared MATLAB limitations are reproduced, not repaired into scientific success.
6. **Paper 1 claim.** The printable v1 paper is a software-methods / validated-reproduction article. Allowed headlines: workflow and statistical-surface equivalence, official demo parity, paired model-selection agreement, backend/GPU applicability, explicit reference limitations. Disallowed headlines for paper 1: general superiority to pyhgf, general parameter-recovery success, peak GPU speedup, multi-GPU scaling.
7. **pyhgf relation.** pyhgf (`==0.3.2` in paper protocol 1) is an external comparator with a different center of design. Common-scope trajectory agreement does not imply interchangeable response-likelihood or fitting surfaces. Quantities without a mapped contract remain `NOT_DIRECTLY_COMPARABLE`. HGFX does not race pyhgf on nodal/gHGF/network construction.
8. **P3 is optional for paper 1.** The trial-horizon identifiability study (issue #21) may enter the supplement if it finishes cleanly under its frozen protocol. Paper 1 must not wait on P3, and P3 must not rewrite historical M18 FAIL.
9. **Audience.** v1 is for researchers who already use the MATLAB HGF Toolbox and need the same analysis contract in Python. It is not the default toolkit for building arbitrary predictive-coding graphs.
10. **Opt-in MAP.** `hgfx.optim.minimize_map` is an additive analysis helper. It must not become the `fit_model` default, must not enter paper-1 headlines, and must not rewrite frozen fitting evidence. See `OPT_IN_MAP.md`.

## v2 — current owner decision, not a plan

Status: **NOT STARTED / NOT COMMITTED / NO MILESTONE**

This section records the owner's present intent. It is not a specification, not a backlog, and not authorization to implement.

Current decision:

- Do not start v2 while paper 1 is unsubmitted.
- Do not name v2 "higher precision." float64 MATLAB fidelity is a v1 job. pyhgf already provides JAX float64. Numerics that diverge from MATLAB belong in a separately versioned line so that old TAPAS analyses remain reproducible on v1.
- If v2 is opened later, its job is a native Python modeling layer on the existing v1 mathematical core: compositional models, explicit priors/transforms, first-class trajectory arrays, and tools that answer a question neither frozen MATLAB nor pyhgf already answers well for TAPAS users (for example identifiability of the toolbox HGF family, or inference beyond the compatibility quasi-Newton/Laplace surface).
- MATLAB remains a regression oracle for any shared equation. It is not the scientific ceiling of a future v2 line.
- Opening v2 requires an explicit second scientific question, a new milestone/release gate, and a versioning rule that leaves the v1 compatibility contract untouched.

Until that happens, treat every new feature request as either v1.x maintenance or out of scope.

## What this file does not do

- It does not change frozen tolerances, seeds, datasets, grids, models, or optimizers.
- It does not activate PV1-04 performance work or PV1-06 feature work.
- It does not authorize a pyhgf fork or a gHGF/network-builder rewrite.
- It does not make paper 1 submission-ready by itself. Submission still follows `../research/PAPER_EXECUTION_PLAN.md`.
