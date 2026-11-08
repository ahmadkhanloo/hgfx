Dear Editors,

Please consider our manuscript, “HGFX: reference-compatible hierarchical Gaussian
filtering in Python,” as a software contribution to Computational Statistics.
HGFX addresses a practical statistical-computing problem: moving established
Hierarchical Gaussian Filter analyses from MATLAB into Python while preserving
the tested meaning of model configurations, parameter transformations, priors,
trial masks and fitted outputs. The contribution is a released research package
and an auditable evaluation of its compatibility boundaries, rather than a new
statistical model or a claim of improved neuroscientific inference.

The manuscript connects the analysis workflow to a frozen MATLAB HGF Toolbox
8.2.0 reference. It separates configuration and trajectory checks from fitting,
model selection and recovery. In the frozen paired experiment, all 36 Bayesian
information criterion winners agree across implementations, while generating-model
recovery balanced accuracy is 0.583 in each. Failed parameter-recovery criteria
and the failed integrity gate of a separate trial-horizon experiment remain
explicit. A comparison with pyhgf is restricted to one prospectively mapped
perceptual case; response negative log-likelihood remains not directly comparable.

The software and accompanying source, evidence manifests and reproducibility
instructions are publicly available through the HGFX repository. A released-wheel example applies the continuous HGF to all 614 observations
of the reference toolbox's empirical USD/CHF series. The evaluation also compares fixed-parameter perceptual outputs across MATLAB and HGFX on
324 source-defined blocks from two published behavioral input files. All blocks met the
prespecified numerical criterion. The paper reports the warnings and distinguishes this
compatibility result from fitting or reproducing either study's scientific conclusions.

We believe the combination of statistical software, numerical evidence and a
clear account of inferential limitations fits the journal's stated package-report
and software-article scope. A related preprint is posted under DOI
10.64898/2026.09.22.753415; this draft is a proposed revision and has not been
uploaded. We intend the subscription route, subject to confirmation that it
incurs no mandatory author charges. Authorship and declarations have been confirmed; final scientific approval
and administrative clearance must be completed before this letter is sent.

Sincerely,

Mohammad Ahmadkhanloo

---

Preparation note: this is an unsent author-review letter. Do not add a declaration
of exclusive consideration, institutional approval or author consent until it is
confirmed. No reason for previous editorial decisions is inferred.
