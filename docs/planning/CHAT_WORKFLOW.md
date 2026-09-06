# Workflow: Advancing HGFX Through ChatGPT

This document defines how to use ChatGPT as the scientific/architecture collaborator while a repository agent performs repetitive implementation.

## Recommended division of work

### ChatGPT
Use the chat for:
- deciding architecture;
- reviewing MATLAB equations;
- designing numerical tests;
- reviewing JAX implementations;
- diagnosing mismatches;
- deciding tolerances;
- deciding whether PyHGF is reusable for a component;
- designing recovery experiments;
- interpreting benchmarks;
- planning the paper;
- reviewing milestone completion.

### Repository coding agent
Use the repository agent for:
- searching the repo;
- implementing one migration item at a time;
- running tests;
- generating fixtures;
- refactoring repetitive code;
- updating manifests;
- preparing commits and PRs.

## How to work step by step in chat

For each task, provide the smallest self-contained unit possible.

Example:

```text
We are on HGF-B02: hgf_prediction.
Here is:
1. MATLAB source file
2. current Python implementation
3. current golden fixture diff
4. relevant config
Review the equations and tell me why trial 37 diverges.
```

Then apply the reviewed change to the repo.

## Recommended chat loop

```text
1. Select next Roadmap item
2. Upload/reference relevant MATLAB file(s)
3. Ask ChatGPT to extract equations and edge cases
4. Ask repository agent to implement
5. Run tests
6. Bring failing diff back to ChatGPT
7. Diagnose
8. Patch
9. Re-run
10. Mark item complete only after gate passes
```

## What to paste/upload to ChatGPT for efficient review

For each item:
- exact MATLAB file;
- exact upstream commit;
- Python target file;
- test file;
- smallest failing fixture;
- first-divergence report;
- config/parameter vector;
- expected and actual values around divergence.

Avoid pasting huge full-repo dumps unless architecture-wide review is requested.

## Milestone review in chat

At the end of each milestone, ask:

```text
Review milestone M4 against:
- MIGRATION_MATRIX.md
- MILESTONES.md
- ACCEPTANCE_CRITERIA.md
- test report
- numerical diff summary
Tell me if the milestone genuinely passes.
```

## Final project review

When the project is feature-complete:
1. freeze the repo;
2. generate full test/benchmark reports;
3. provide the repo to an independent frontier coding/reasoning agent;
4. ask it to review against `FINAL_REVIEW_CHECKLIST.md`;
5. do not let that agent modify acceptance criteria before finishing the review;
6. resolve all Critical/High findings;
7. rerun full validation.

## Important

The chat should not become the only memory of the project.

Every substantive decision made in chat must be written back into one of:
- architecture docs;
- numerical policy;
- migration matrix;
- changelog;
- issue/PR;
- research log.

The repository is the durable source of truth.
