# P7 Journal of Neuroscience Methods preflight

Last checked: 2026-09-18  
Status: **P7-1 FORMAT/EVIDENCE PREFLIGHT IMPLEMENTED; P7 LOCK BLOCKED BY AUTHOR INPUT**

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

## Remaining blocker

The exact corresponding-author institutional email is not committed in the paper source. It is intentionally **not inferred or guessed**.

Until the author supplies/approves the address:

- P7 exact candidate SHA must not be locked;
- P8 must not start;
- P6A must remain `DRAFT_NOT_FROZEN`.

Run:

```bash
python paper/scripts/check_p7_submission.py
python paper/scripts/check_p7_submission.py --strict
```

The non-strict command should report `BLOCKED_AUTHOR_INPUT` with only `MISSING_CORRESPONDING_AUTHOR_EMAIL`. The strict command is the future P7 lock gate and must fail until that blocker is resolved.
