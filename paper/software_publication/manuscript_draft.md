# HGFX: a Python/JAX implementation of Hierarchical Gaussian Filter workflows with evidence-bounded MATLAB compatibility

> **WORKING SOFTWARE ARTICLE, NOT A SUBMISSION:** authored under SWPUB following the 2026-11-10 D1 journal-change decision. This draft is **venue-neutral**, not converted to an official SoftwareX/JOSS template and **not author-approved**. It reuses existing released-software evidence without changing source results. Review all numbers, citations, affiliations and disclosures prior to a final journal-specific build.

**Provisional author metadata — requires author reconfirmation:** Mohammad Ahmadkhanloo; Institute for Research in Fundamental Sciences (IPM), Tehran, Iran.

## Software metadata

| Field | Working metadata |
| --- | --- |
| Software | HGFX |
| Examined version | `1.0.0` (not the current unreleased development branch) |
| Immutable source | [v1.0.0](https://github.com/ahmadkhanloo/hgfx/tree/v1.0.0), commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| Reference | MATLAB HGF Toolbox 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3` |
| Code license | MIT; inspect the repository `LICENSE` and `THIRD_PARTY_NOTICES.md` |
| Language/runtime | Python 3.11+; package runtime requires NumPy 2+ and JAX 0.4.30+ under the released `pyproject.toml` |
| Distribution | `https://pypi.org/project/hgfx/1.0.0/`; an independent clean-install check for this *paper candidate* is still required |
| Reference materials | `docs/validation/V1_EVIDENCE_INDEX.md`, `docs/research/PAPER_EVIDENCE_MAP.md`, `paper/reproducibility/` |
| Archived software DOI | **NOT VERIFIED / do not invent one** |
| Financial and journal submission | **NOT CLEARED**; candidate SoftwareX fee waiver has not been confirmed |

## Summary

Hierarchical Gaussian Filter (HGF) models are used to express trial-by-trial Bayesian learning under uncertainty [@mathys2011; @mathys2014]. Research workflows built around the MATLAB HGF Toolbox are useful but can be difficult to integrate directly with Python-native analysis and accelerated numerical environments. HGFX provides a Python/JAX implementation of the frozen MATLAB HGF Toolbox 8.2.0 model and workflow surface. The released package supports configuration and parameter transforms, forward trajectories, observation likelihoods, fitting, simulation, sampling and several HGF variants in documented compatibility scopes, without MATLAB as a user runtime dependency.

The package is accompanied by frozen reference identities, golden numerical fixtures, regression tests, provenance records and explicit classification of numerical disagreements. Its intended contribution is reusable scientific software with **auditable, limited compatibility evidence**, not a novel HGF model, proof of parameter identifiability or unrestricted agreement for every optimizer invocation.

## Statement of need

A software migration of a learning model involves more than porting equations. The numerical operations, parameter ordering, prior treatment, observation-model semantics, ignored-trial handling, and fitting interface can affect outputs. A user who needs to reuse a MATLAB HGF analysis from Python therefore needs to know **which model/workflow pair was actually checked**, which output quantities agree, and when an optimizer-dependent result remains unresolved.

HGFX addresses this need using a frozen reference release and traceable validation results. Unlike a claim of universal equivalence, the package separates validated forward and objective pathways from inference tasks that may remain sensitive to model specification or numerical optimization.

## Software description

HGFX uses structured perceptual and observation model configuration, transformed/native parameter semantics, and Python/JAX numerical paths. The released interface includes fitting and MATLAB-style compatibility entry points as well as simulation and sampling. Tests cover individual model components and end-to-end workflows against frozen MATLAB exports. Source and test fixtures are version-identified so that readers can reproduce a documented comparison without requiring a live MATLAB installation merely to use HGFX.

MATLAB remains the external **oracle for validation**, not a dependency of the installed Python package. The release provenance distinguishes CPU and physical-GPU applicability from runtime performance claims. Performance benchmarking requires a separate prespecified comparison of exact workloads and valid CPU/GPU environments; no such speedup is asserted here.

## Relation to existing software

The MATLAB HGF Toolbox and TAPAS provide the scientific reference implementation and surrounding analysis environment [@fraessle2021tapas]. The separately maintained Python/JAX project PyHGF provides another research ecosystem implementation [@legrand2026pyhgf]. HGFX therefore is **not** the first Python or JAX HGF library. Its proposed niche is MATLAB-version-anchored workflow compatibility with explicit numerical provenance. A prior `pyhgf==0.3.2` common-scope diagnostic compared 11 mapped perceptual quantities for a single three-level binary-HGF case; that scope does not establish general implementation interchangeability or equality of response likelihoods.

The choice to maintain a distinct implementation rather than claim to supersede these projects requires the research user to value traceability to the frozen MATLAB reference. Evidence of external adoption and generalized scientific impact has **not** been established for this working paper and must not be invented.

## Validation evidence and interpretation

In a paired, frozen synthetic model-selection protocol, MATLAB and HGFX selected the same minimum-BIC candidate for **36 out of 36** datasets. This is evidence of **paired model-selection agreement within that protocol**; the balanced accuracy for recovering the generating family was approximately **0.5833** in both implementations, and the underlying parameter recovery did not satisfy the full original scientific criteria. Agreement of a model-selection decision is not proof that the selected model is the data-generating model.

A separate evaluation involving **324 empirical-data input blocks and 25,920 trials** compared **fixed-parameter forward behavior**. It does **not** reproduce published subject-level fitting or study conclusions. The archived status evidence records **48 blocks with 86 warning events**, concentrated in cases with ignored trials. The warning message categories and numerical causes were not archived, so their harmlessness is not established.

Further limitations remain explicit: the historical trial-horizon study failed its required paired-integrity gate; **four** classic-HGF recovery cases terminated at an HGFX initial-stability check whereas MATLAB returned fit outputs; and a historical **64-subject** full-fit comparison had **63** diagnostically concordant subjects with one subject's level-2 trajectories outside the original comparison gate. Neither the first causal intermediate of that discrepancy nor a same-vector objective replay of the four asymmetric horizon cases has been established. The historical scientific failures remain visible and have not been converted to passing results.

## Reuse, availability and limits

The software source is public at `https://github.com/ahmadkhanloo/hgfx`. The evaluated release is the versioned `v1.0.0` source and its matching Python package, not all subsequent development-line functionality. Validation protocols, source SHAs, failed outcomes, and paper-specific evidence are linked from the project documentation. A final publication package must provide a clean install-and-run example, exact test environment, manuscript-to-evidence map, verified archive or persistent release identifier, third-party notices, and the author's confirmed code/data reuse rights.

HGFX is useful when documented compatibility with the frozen HGF Toolbox is the scientific requirement. It should not be used as evidence for strong parameter or structural identifiability, full inference parity, relative speed or published-study replication beyond the narrowly tested configurations.

## Declarations — pending explicit human verification

**AI-assistance disclosure (working, must be verified and edited by the author):** OpenAI ChatGPT was used to assist with repository documentation, review, source organization, and manuscript drafting; the scientific evidence and implementation changes must be checked by the human authors against frozen validation records. Do not claim human review of this *new* draft until it occurs.

**Funding, competing interests, institutional approvals, all authors and affiliations, preprint overlap, and reuse permissions:** **PENDING AUTHOR CONFIRMATION**. No publication or submission claim is made.

## Reference source and numerical-claim audit

The bibliography source is `paper/references.bib`; all references and their formatted forms require a final check. Numerical values above are drawn from versioned repository reports, notably `docs/validation/M18_S7_REFERENCE_LIMITATION.md`, `docs/research/P3_M18C2_RESULT.md`, `docs/planning/COMPSTAT_REVISION_LEDGER.md` on the revision branch, and `evidence/revision/first_divergence_audit.json`. This is **not** a substitute for running the final strict machine-readable scientific-claim mapping and paper build.
