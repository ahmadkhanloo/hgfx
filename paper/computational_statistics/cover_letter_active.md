# Cover letter — DRAFT (pending D2/D3; not sendable)

> **Status 2026-11-14:** Editorial draft prepared for author review. Every
> scientific statement below mirrors the D2 decision packet's permitted claim
> envelope; nothing here is approved until the author completes the D2 record.
> Bracketed items are author actions; no exclusive-submission or approval
> wording is invented on the author's behalf.

---

Dear Editors,

We submit [AUTHOR CONFIRMS ARTICLE TYPE IN THE PORTAL] our manuscript
"HGFX: a Python package for reference-compatible Hierarchical Gaussian Filter
workflows" for consideration in *Computational Statistics* as a
software/package contribution.

**Contribution.** HGFX is an MIT-licensed Python/JAX package (`hgfx==1.0.0` on
PyPI) that re-implements the workflows of the frozen MATLAB HGF Toolbox 8.2.0
reference without requiring MATLAB at runtime. The accompanying article
contributes a reproducible validation framework that separates three levels
that are easy to conflate: agreement of numerical evaluation at the same
parameter vector, behavior at independently fitted endpoints, and statistical
recovery of parameters and generating models. Every comparison is reported
with machine-readable evidence, and failures are preserved rather than
repaired post hoc.

**Key measured results.** The released wheel and the MATLAB oracle agree at
the same parameter vector in the classic binary-HGF cases that were valid on
both sides (164 of 200; 36 jointly invalid are not counted as parity); a
fixed-parameter forward comparison on authentic published behavioral inputs
(324 blocks, 25,920 trials, 2,540,160 compared elements) showed no element
outside the predeclared tolerance; paired BIC winner agreement (36/36)
coexists with generating-model balanced accuracy of 0.583, and the article
reports these as distinct quantities. A precision-stability study quantifies
the cost of running the filter in float32 by mistake and maps the
horizon-growing failure region of the recursion. Physical-GPU evidence is
discussed as correctness applicability only; no speed claim is made.

**Relationship to a preprint.** A bioRxiv preprint with DOI
`10.64898/2026.09.22.753415` exists; the submitted article is a substantially
revised software-article presentation, and the preprint identity is distinct
from the software version DOI. [AUTHOR CONFIRMS the preprint status and any
overlap disclosures required by the journal.]

**Declarations.** The author is the developer and maintainer of HGFX and
declares this competing interest in the manuscript. The manuscript contains
the generative-AI use disclosure requested by the journal. Funding: none
declared. [AUTHOR CONFIRMS declarations, affiliations and any institutional
or fee conditions before submission.]

We would be glad to answer any questions from the editors or reviewers.

Sincerely,
Mohammad Ahmadkhanloo
Institute for Research in Fundamental Sciences (IPM), Tehran, Iran
m.ahmadkhanloo@ipm.ir
