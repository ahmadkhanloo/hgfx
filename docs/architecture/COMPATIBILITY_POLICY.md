# Compatibility Policy

Compatibility is defined against a frozen reference release and exact commit.

## Levels

### Level A — Structural
Names, shapes, parameter order, masks, fixed/free indexing.

### Level B — Forward numerical
Trajectories and intermediate states.

### Level C — Likelihood/objective
Trial likelihood, priors, objective.

### Level D — Fit
Scientifically equivalent MAP solution.

### Level E — Statistics
Hessian, covariance, correlation, AIC, BIC, LME.

### Level F — Simulation
Simulation and sampling behavior.

A component's documentation must state which level(s) it satisfies.
