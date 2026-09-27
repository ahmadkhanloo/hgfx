# Cover letter — Journal of Neuroscience Methods

Dear Editors,

Please consider the manuscript **“HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox”** for publication as a Research Article in *Journal of Neuroscience Methods*.

The manuscript describes HGFX 1.0.0, an open-source Python/JAX implementation designed to reproduce the documented behavior of a frozen HGF Toolbox 8.2.0 MATLAB reference while removing MATLAB as a runtime dependency for users. The work treats reimplementation as a validation problem: configuration semantics, parameter transforms, forward trajectories, observation likelihoods, fitting and statistical surfaces, simulation workflows, model selection, and backend agreement are evaluated against predeclared criteria and machine-readable evidence.

The principal methodological contribution is the validation and provenance framework rather than a new generative model. The manuscript reports successful results together with preserved failures and matched reference limitations, explicitly separates parameter recovery from model-selection agreement, and limits GPU claims to the tested correctness/applicability scope. It also includes a prospectively gated common-scope comparison with pyhgf and identifies recent generalized-HGF work as outside the compatibility scope evaluated here.

HGFX 1.0.0 is released under the MIT license and is available from GitHub and PyPI. The manuscript’s tables, figures, validation records, and reproducibility instructions are maintained with the source repository so that the reported software evidence can be traced to committed artifacts.

The study does not introduce a new behavioral or neuroimaging dataset. Its intended contribution to neuroscience methods is a reproducible route for running established HGF workflows in a modern Python/JAX environment while retaining an explicit, testable relationship to the reference implementation used in prior computational-neuroscience work.

Thank you for considering the manuscript.

Sincerely,

Mohammad Ahmadkhanloo  
Institute for Research in Fundamental Sciences (IPM), Tehran, Iran  
m.ahmadkhanloo@ipm.ir
