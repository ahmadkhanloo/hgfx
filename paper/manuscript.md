# HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox

**Target journal:** *Journal of Neuroscience Methods* (Elsevier; hybrid; **subscription track, no APC**)  
**Article type:** Research Article (methods)  
**Highlights:** `paper/highlights.txt`  
**Word count (main text, approximate):** 2,400  
**Figures:** 5\qquad**Tables:** 6  
**Abstract:** \le250 words (this draft \approx 230)

**Authors and affiliations**

Mohammad Ahmadkhanloo\\
Institute for Research in Fundamental Sciences (IPM), Tehran, Iran\\
https://github.com/ahmadkhanloo

**Correspondence:** Mohammad Ahmadkhanloo, Institute for Research in Fundamental Sciences (IPM), Niavaran Square, Tehran, Iran. Software: https://github.com/ahmadkhanloo/hgfx. Institutional email to be inserted before submission if required by the journal.

**Keywords:** Hierarchical Gaussian Filter; computational psychiatry; MATLAB equivalence; Python; JAX; reproducibility; model selection; GPU

## Abstract

The Hierarchical Gaussian Filter (HGF) is a hierarchical Bayesian model of learning under uncertainty and volatility, with a widely used MATLAB implementation. We present HGFX 1.0.0, a Python/JAX toolbox whose primary objective is functional and scientific equivalence with a frozen HGF Toolbox 8.2.0 reference, while removing MATLAB as a user-runtime dependency. Reimplementation is treated as a validation problem rather than source translation: configuration semantics, parameter transforms, forward trajectories, observation likelihoods, objectives, fitting and statistical surfaces, simulation workflows, official demo behavior, model selection, and backend agreement are compared against the pinned oracle under predeclared tolerances. Two official MATLAB demo workflows reproduce the reference at frozen trajectory tolerances, including a model-family failure regime in which classic HGF fails and eHGF succeeds. In paired model-selection validation, all 36 BIC winners agree between MATLAB and HGFX. Physical NVIDIA GPU applicability was confirmed on two Tesla T4 devices, with a maximum CPU-versus-GPU final-objective difference of 1.42e-14 against a frozen 1e-7 criterion. Historical parameter-recovery failures and exact MATLAB/HGFX limitation matches are preserved and are not reclassified as scientific success. A prospectively gated comparison with pyhgf 0.3.2 shows binary64-scale agreement on mapped perceptual trajectories in one authorized three-level binary-HGF cell, while participant-response negative log-likelihood is retained as not directly comparable. HGFX therefore provides a MATLAB-independent Python implementation with an explicit evidence model that separates direct parity, matched reference limitations, backend applicability, and future performance claims.
