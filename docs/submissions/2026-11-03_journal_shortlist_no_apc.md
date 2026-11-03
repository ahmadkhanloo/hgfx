# HGFX journal shortlist after three editorial rejections — 2026-11-03

**Status: RECOMMENDATION / journal not selected; NO active submission.** Author has a strict no-fee preference. Current repo main inspected at `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`. Historical submissions: JNM declined, Neuroinformatics declined, Brain Informatics rejected (Ning Zhong letter with no reason/reviewer comments in provided text). Do not infer scientific failure or invent reviewer objections.

## Priority option — Behavior Research Methods (Springer Nature, Psychonomic Society)
- Official journal: https://link.springer.com/journal/13428
- Author publishing options: https://link.springer.com/journal/13428/how-to-publish-with-us
- Model: hybrid. Official 2026 author page explicitly says **subscription publishing route: no APC charges**, offered after acceptance. OA choice has APC; user should select subscription and verify whether any other charges apply.
- Journal scope: experimental psychology methods, techniques and research software; computer technology. Source: https://link.springer.com/journal/13428/aims-and-scope
- Concrete precedent in journal: **Hellmann, Zehetleitner, Rausch, "dynConfiR: An R package for sequential sampling models of decision confidence" (2026)**: https://link.springer.com/article/10.3758/s13428-026-03013-0. This illustrates fit for model-fitting/simulation packages, **not** a promised acceptance.
- Main risk: HGFX is currently framed as software parity with MATLAB, not a demonstrated new experimental-psychology use case or improved cognitive modeling technique. More user-facing worked examples/empirical workflows and concrete methodological significance needed. An optional presubmission scope enquiry to editor is prudent after rewriting summary; it is not editorial permission to skip paper quality requirements.
- 2025 JIF displayed 5.1 as of source check.

## Alternative — Biological Cybernetics (Springer Nature)
- https://link.springer.com/journal/422 and https://link.springer.com/journal/422/aims-and-scope
- Hybrid subscription route generally permits avoiding OA APC; verify other charges on journal-specific instructions. The publisher classifies as Hybrid.
- Computational neuroscience relevant, but asks for theoretical/application insights about biological information processing. HGFX's implementation-faithfulness paper currently has **weak direct new neural-theory contribution**; considerable risk of scope-related desk rejection. Was previously present in the publisher's suggested alternatives list; that is not an endorsement/acceptance guarantee.

## Conditional open-access alternative — SoftwareX (Elsevier)
- Official publisher description: https://www.elsevier.com/researcher/author/tools-and-resources/research-elements-journals
- Directly publishes research-software descriptions and applications; strongest general *software article* scope.
- **Fully open access with APC**, no routine no-charge subscription route. Official Elsevier waiver policy: https://www.elsevier.support/publishing/answer/what-is-elseviers-waiver-policy-for-open-access-fees ; individual waivers discretionary (no promise of full waiver), and before incurring any commitment, confirm written full fee coverage/waiver. Do not quote outdated/third-party conflicting APC amounts as definitive.
- For the author's zero-payment requirement, **do not submit without reliable clarification of full waiver route or written fee coverage**, and check current price/individual rules in publisher portal.

## Less suitable near-term
- Computational Brain & Behavior: hybrid https://link.springer.com/journal/42113 ; focuses scientific insight about mind and behavior rather than new software itself. As-is HGFX parity-only article may be judged out of scope.
- Neural Computation: MIT Press has a **non-refundable $125 submission fee** (official https://mitpressjournals.mit.edu/shop/fees/?issn=0899-7667), so it violates user's no-payment preference.
- JOSS: software-oriented and no APC, but project is <6 months old as of 2026-11-03; see `docs/submissions/2026-11-03_joss_readiness.md` and issue #81. Not ready for an immediate submission.

## Editorial preflight for Behavior Research Methods
1. Position scope as replicable Bayesian computational modeling for learning/uncertainty in psychology; not new neuroscience findings or first Python HGF package.
2. Rebuild abstract and introduction around the actual behavioral-research problem/benefit and explain use-case, keeping numerical validation details honest and verifiable.
3. Preserve all 36/36 BIC paired winner data, negative parameter-recovery criteria, NDC pyhgf NLL, and T4-only GPU applicability. Avoid unearned speedup/identifiability.
4. Add actual runnable pedagogical or research example with complete inputs, model specification, interpretation and reproducibility using verified evidence; new empirical claims require genuine additional experiments, not fabricated case studies.
5. Keep bibliography, preprint DOI `10.64898/2026.09.22.753415`, code release and authorship/AI disclosures; do not alter frozen evidence.
6. Check final submission guidelines and any non-APC charges and seek optional pre-submission scope feedback before submitting.
7. Update this decision record once author actually chooses journal or an editorial response changes the plan. Do **not** update historic milestone meaning or label paper PASS without acceptance checks.

## Verification snapshot
Sources inspected live on 2026-11-03. No JOSS or BRM submission has been performed. No article accepted, no fee waived/paid. The latest `main` has not been modified for this recommendation.
