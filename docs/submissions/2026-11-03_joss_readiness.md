# HGFX publication route and JOSS readiness review — 2026-11-03

> Status: **JOSS NOT READY / do not submit**. This is an author-side readiness assessment, not a JOSS editorial decision. Based on live main `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`, repository API metadata, and JOSS official guidance inspected on 2026-11-03. Historical paper/science freeze is unchanged.

## Journal decision chronology (keep historical submissions)

- *Journal of Neuroscience Methods*: declined, previously reported 2026-10-22, no longer under consideration.
- *Neuroinformatics*: declined, transferred from prior submission; detailed independent-review evidence not supplied.
- *Brain Informatics*: **REJECTED**, editorial email from Ning Zhong, received/reported by author on 2026-11-03; submission `a41d238b-de46-4406-8110-3b2acbbbb4c6`. Email contains no reason and no appended reviewer comments in the portion provided. Do not infer review-stage or scientific failure from this email.
- No journal is confirmed as currently considering this manuscript. The preprint has DOI `10.64898/2026.09.22.753415`.

## Current verified GitHub observations

| Property | Evidence from repository | Status for JOSS |
|---|---|---|
| Public GitHub history | Repository `created_at=2026-09-06T22:13:03Z`; on 2026-11-03 it has **58 days** of existence | **BLOCKED**; JOSS asks >6 months of public, iterative development. Earliest age threshold is after 2027-03-06, but age alone cannot satisfy the gate |
| Commit distribution | Sampled current `main` commit history strongly concentrated during September 2026; latest main commit dated 2026-09-27, `bbf17e9` | **BLOCKED / needs months of genuine follow-up development** |
| Research impact | MATLAB/HGFX validation scripts, simulated research data and public preprint document author's research-software validation; no independent user, third-party adoption, published research use, or external group integration verified | **INSUFFICIENT** for strong realized-impact claim; document actual research use without inventing outside adoption |
| License | `LICENSE` contains MIT license text | **PASS (file presence/OSI type)**; GitHub API license metadata `NOASSERTION` does not negate checked actual file |
| Package | stable `hgfx==1.0.0` release publicly documented; `main` has additive `1.1.0b1` metadata | **IMPLEMENTED**; keep JOSS article scoped to validated stable v1.0.0, not beta |
| Documentation | `README.md`, `docs/user/*`, `examples/*`, `CONTRIBUTING.md`, `CITATION.cff` | **IMPLEMENTED**; independent beginner-install usability check still unverified |
| Tests and CI | `tests/`, many `.github/workflows/`, frozen reference artifacts | **IMPLEMENTED**; tests not re-run in this review; no new test PASS declared |
| Open development | issue tracker enabled, issues and PRs are public; most inspected activity author-led and milestone-oriented | **PARTIAL**; add user-facing support expectations and visible genuine iteration/community feedback |
| JOSS-specific paper | Prior `paper/manuscript.md` targets Elsevier scientific methods article; not JOSS Markdown structure | **OPEN**; provisional `paper/joss/paper.md` and `paper.bib` in this branch only, not submit-ready |

## Official JOSS requirements used

- https://joss.readthedocs.io/en/latest/submitting.html
- https://joss.readthedocs.io/en/latest/review_criteria.html
- https://joss.readthedocs.io/en/latest/paper.html
- JOSS charge: **no submission or publication fees**.
- JOSS 2026 paper length **750–1750 words** with YAML front matter and sections: Summary, Statement of need, State of the field, Software design, Research impact statement, AI usage disclosure, Acknowledgements, references via `paper.bib`.
- JOSS pre-review checks enforce >6 months **public and active** history, demonstrated research use/impact, iterative development, open-source workflows, and substantial maintainable software. A recent paper draft does not cure the repo-age gate.
- JOSS allows AI assistance in creating software/paper but requires tool/model/version, scope, human verification and design-responsibility disclosure. Its policy **does not allow AI-based author-editor/reviewer conversation**, except translation. A human author must conduct correspondence.

## Distinct paper strategy

The previous ~2,400-word methods paper presents numerical validation and detailed scientific results. Do **not** submit that full paper verbatim to JOSS. Its six plots, several metric tables, deep validation case IDs, and failure/optimizer experiments belong in public software docs or a companion reproducibility/manuscript repository. For JOSS:
1. Lead with MATLAB-independent reproducible fitting and simulation and the audience in computational neuroscience.
2. State why new software is useful relative to original TAPAS MATLAB HGF and `pyhgf`: a fixed, versioned oracle and validated MATLAB-compatibility surface rather than claiming first Python HGF or universal superiority.
3. Explain numerical design trade-offs (compatibility semantics vs JAX-oriented execution), APIs, evidence provenance.
4. Report **scoped** verified facts: stable 1.0.0, official workflows, 36/36 frozen paired BIC winners, T4 applicability (not speed), historical recovery limitations preserved.
5. Explicitly distinguish reproducibility evidence from **realized community research adoption**. Do not invent citations, user numbers, external labs, or multi-GPU performance outcomes.
6. Disclose AI tool use in the mandated JOSS format and verify the specific versions actually used.
7. Maintain `paper/joss/paper.md` as a future draft; do not publish or submit until all gates and authorship fields are verified.

## Acceptance plan and status

| Gate | Criterion/evidence required | Current state |
|---|---|---|
| JOSS-01 public history | At least >6 months public project history **and meaningful iterative activity across that time** | **BLOCKED** until at least March 2027; no passive wait / invented commits |
| JOSS-02 scholarly use | Dated reproducible use in actual research, cited preprints or independently checkable analyses; ideally external users | **OPEN** |
| JOSS-03 outside usability | Outside-user clean installation, run examples, open issues for actual defects with fixes, release/revision notes | **OPEN** |
| JOSS-04 software paper | Markdown 750–1750 words, YAML, required sections, BibTeX, strong fair alternatives comparison, confirmed author disclosure | **DRAFT** |
| JOSS-05 compliance | Check all required JOSS pre-review items, including license and no concurrent journal consideration | **OPEN** |
| JOSS-06 editorial review | Only after above, human author decides to submit (no automated JOSS submission) | **NOT STARTED** |

## Next steps

1. Keep the existing v1.0.0 scientific freeze untouched. Continue only real user-driven software development, public releases and issue/PR activity. Do not create artificial public commits for apparent eligibility.
2. Gather a dated, independently inspectable example of **research** using HGFX rather than only software-to-software comparison; secure proper permissions and cite actual outputs.
3. Recruit at least one independent user to install/test the release and file genuine issues with evidence; document feedback and fixes.
4. Update `paper/joss/paper.md` when these facts exist, verify explicit AI model versions with author, run JOSS PDF build/preview, and re-audit age/development gate not before March 2027.
5. If near-term publication is necessary, separately research no-APC **subscription/hybrid** software-method journals and compare scope/publication fees before submitting; do not represent JOSS as an immediate route.


## Work performed in the 2026-11-03 assessment
- A JOSS-format manuscript draft was added at `paper/joss/paper.md`, with complete `paper/joss/paper.bib` based on the frozen manuscript bibliography. This is not submitted to JOSS.
- Static manuscript checks: approximately **1,009 words**, all eight expected headings found, **6/6 unique bibliography citation keys resolve**. This checks syntax structure and citations only, **not PDF rendering or scientific acceptance**.
- Dedicated follow-up: https://github.com/ahmadkhanloo/hgfx/issues/81 (JOSS public-history and research-use gate).
- Branch: `docs/joss-readiness-2026-11` created from main `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`. Main, frozen releases, scientific datasets, thresholds, and historical publication evidence were not changed.
