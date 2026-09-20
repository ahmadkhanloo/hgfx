# P7 Journal of Neuroscience Methods preflight

Last checked: 2026-09-18  
Status: **P7 CONTENT/PREFLIGHT COMPLETE; REPLACEMENT SHA LOCK PENDING P8-HARDENING VALIDATION**

## Current publisher-facing constraints checked

The current Elsevier Journal of Neuroscience Methods scope states that the journal considers neuroscience methods and major methodological refinements, but does not consider software/tools that lack a scientific or research component. The manuscript therefore explicitly frames HGFX as a neuroscience-method validation/reproducibility study rather than a software-only announcement.

Publisher guidance used for this preflight:

- Journal of Neuroscience Methods scope: https://shop.elsevier.com/journals/journal-of-neuroscience-methods/0165-0270
- Elsevier highlights guidance: https://www.elsevier.com/researcher/author/tools-and-resources/highlights
- Elsevier author guidance: https://www.elsevier.com/subject/next/guide-for-authors
- Elsevier generative-AI policy: https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals

The direct ScienceDirect journal page/Guide-for-Authors endpoint was not reliably machine-retrievable during this check. Final submission should still be compared manually with the live JNM submission form before upload.

## P7-1 corrections

- highlights rewritten to five plain-language lines, each <=85 characters;
- manuscript keywords reduced to six;
- stale "Technology and Code article" wording removed;
- neuroscience-method relevance made explicit;
- Elsevier-style competing-interest, CRediT and no-specific-funding sections added;
- generative-AI use disclosed both for software-development assistance in Methods and manuscript preparation before References;
- bibliography-key resolution and manuscript-format checks automated by `paper/scripts/check_p7_submission.py`.

## P7-2 strict-gate result

Strict JNM preflight run `35342388457`: **PASS**.

- exact approved corresponding email present;
- zero P7 format/evidence errors;
- zero blockers;
- replacement candidate SHA will be the final read-only PR head after the P8-hardening wording/document synchronization passes P7/P6A/P2/P5/regression validation, then it will be recorded in the P8 checklist.

## Corresponding-author metadata

The author-approved institutional email `m.ahmadkhanloo@ipm.ir` is committed in the manuscript. The strict preflight now verifies that the manuscript contains this exact approved address.

P6A remains `DRAFT_NOT_FROZEN`; P8 must start only after the exact validated P7 candidate SHA is recorded.

Run:

```bash
python paper/scripts/check_p7_submission.py
python paper/scripts/check_p7_submission.py --strict
```

Both the normal and strict commands must report `PASS_P7_PREFLIGHT`. The strict command is the P7-2 candidate-readiness gate.
