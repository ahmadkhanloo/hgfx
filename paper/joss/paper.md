---
title: 'HGFX: A Python/JAX toolbox for validated Hierarchical Gaussian Filter workflows'
tags:
  - Python
  - JAX
  - computational neuroscience
  - Bayesian learning
  - reproducible research
authors:
  - name: Mohammad Ahmadkhanloo
    affiliation: '1'
affiliations:
  - index: 1
    name: Institute for Research in Fundamental Sciences (IPM), Tehran, Iran
date: 3 November 2026
bibliography: paper.bib
---

<!-- PROVISIONAL JOSS DRAFT. DO NOT SUBMIT. The public-history and research-impact gates remain open; see docs/submissions/2026-11-03_joss_readiness.md. The date, paper contents, funding and author metadata must be checked anew when ready. -->

# Summary

Computational neuroscience often uses mathematical models to infer how people learn under uncertainty and respond to changing environments. One established family, the Hierarchical Gaussian Filter (HGF), models beliefs about hidden states and the volatility of those states [@mathys2011; @mathys2014]. The widely used HGF reference implementation is distributed in MATLAB as part of the TAPAS software ecosystem [@fraessle2021tapas]. HGFX is an open-source Python library that supports fitting, simulation, sampling, and analysis workflows for HGF-family models, with documented compatibility against a fixed version of that MATLAB reference. Its regular usage requires no MATLAB installation. This makes the library usable in Python-based analysis environments while retaining a testable connection to previous MATLAB workflows.

HGFX version 1.0.0 is distributed through PyPI and supplies Python-first functions alongside MATLAB-style aliases. Its numerical validation cases, supporting figures and tables, and reproducing scripts are available in the project repository. HGFX has a NumPy-compatible execution surface and JAX-backed paths for CPU and GPU workloads; accelerator support is not an assertion of universal speedup.

# Statement of need

Studies of belief updating and volatility learning commonly rely on workflows whose results depend on more than the underlying mathematical equations. Parameter priors and transformations, numerical methods, observation likelihoods, starting points, optimizer choices, and statistical summaries all influence the analysis. Transferring such workflows to a new programming language requires validation of those conventions, not simply a visually similar learning trajectory [@wilson2019ten; @peng2011reproducible].

HGFX addresses researchers who need to inspect and reuse HGF models from Python, and especially those who want to migrate analysis scripts originally constructed with the MATLAB HGF toolbox. The project targets a specific, versioned reference—HGF Toolbox 8.2.0—and publishes reproducible checks of the parts of that reference it aims to preserve. Researchers can fit observed responses, simulate inputs and responses, access model-comparison quantities, and generate diagnostic outputs without licensing MATLAB for ordinary software use. Reproducing the historical cross-language validation artifacts still requires the MATLAB reference, so the package does not claim to remove MATLAB from oracle regeneration.

# State of the field

The MATLAB HGF toolbox and TAPAS provide established implementations and modeling workflows [@mathys2011; @mathys2014; @fraessle2021tapas]. pyhgf is another Python implementation, designed around configurable predictive-coding networks and differentiation [@legrand2026pyhgf]. HGFX is neither the first Python implementation of HGF nor a general replacement for every pyhgf model. Its distinguishing design objective is a frozen MATLAB-compatibility target, covering the documented configuration, parameter, likelihood, simulation, fitting and model-comparison surfaces.

The project chose a separate compatibility-focused library rather than simply extending an existing Python package because its principal engineering constraint is the behavior of a pinned MATLAB implementation. The algorithms, configuration conventions and numerical tests in this repository make that constraint explicit. A frozen common-scope comparison with pyhgf 0.3.2 found rounding-scale agreement on eleven mapped perceptual quantities in one authorized three-level binary-HGF case, but response negative log-likelihood was not directly comparable due to a numerical-boundary difference. This is not package-wide equivalence or a ranking of implementations.

# Software design

HGFX separates compatibility-sensitive numerical paths from JAX-backed compute paths. This structure lets the reference-matching implementation retain behavior tied to MATLAB-style parameter definitions and optimizer conventions without forcing every user operation into the legacy environment. Python-first and familiar MATLAB-style function names support migration from existing scripts; tests and examples exercise fitting, simulation, sampling, specialized configurations, and analysis outputs.

A second design decision is to make numerical provenance part of the software contract. Published test and validation artifacts name the exact MATLAB reference version, package release, data-generating workflow, comparison quantity and predetermined numerical tolerances. Results are classified as direct agreement, a limitation matched to the reference, a preserved scientific failure, or a quantity that is not directly comparable. The distinctions are operationally important: a matching model-selection winner does not prove reliable recovery of the generating parameters, and optimizer disagreement in a sensitive basin need not imply different model equations.

In two pinned official demonstration workflows, HGFX reproduces MATLAB model behavior within the documented numerical tolerances. The frozen paired model-selection grid has 36 of 36 identical BIC winners. In contrast, the recorded parameter-recovery criteria were not fully satisfied; the additional trial-horizon experiment failed its paired-integrity gate. Neither result is presented as successful scientific parameter identifiability. An archived physical Tesla T4 execution supports final-objective agreement for four fitting cells, but does not establish speedup, maximum throughput, or multi-GPU scaling.

# Research impact statement

HGFX has been used in the author's reproducible computational experiments to compare a new Python implementation against a MATLAB oracle across fitting, simulation, model-selection, and numerical analysis procedures. The corresponding test cases, paper tables, raw evidence, workflow records, and reproduction instructions are in the public repository. A preprint describing the validation study was deposited on bioRxiv in 2026 (DOI: 10.64898/2026.09.22.753415).

This documents internal research-software validation and reproducible materials, **not** independent research adoption. As of this draft, the repository review has not verified a published neuroscience study that uses HGFX as its analysis engine, an outside laboratory deployment, or an independent software citation. Such evidence must be added with verifiable references rather than inferred from package availability, download counts, or the existence of this paper. Accordingly, the present draft is not ready for submission to JOSS under its current screening policy.

# AI usage disclosure

OpenAI ChatGPT has assisted the author with software code drafting and review, documentation maintenance, consistency checks, manuscript organization, and language editing. The author reviewed and revised assisted material and applied the project's documented frozen regression, numerical parity, scientific-validation and provenance procedures to reported claims. Scientific conclusions and acceptance classifications were not delegated to AI output. **Before submission, the author must verify and add the exact AI tool/model versions used throughout the project and explicitly attest to ownership of core design choices and final human review.** This paragraph is a transparency draft, not a complete finalized disclosure under current JOSS policy.

# Acknowledgements

The published HGF methodology and TAPAS software provide the scientific and numerical reference for this work. No specific grant funding was reported for this research. The author is the developer and maintainer of the evaluated HGFX software.

# References
