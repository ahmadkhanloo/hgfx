# REV-2.4 — provenance follow-up to the AI-limited offline review (2026-11-10)

**This is a repository-side evidence supplement, NOT a reviewer-authored amendment.** Original reviewer report: [`REV24_INDEPENDENT_REVIEW_2026-11-10.md`](REV24_INDEPENDENT_REVIEW_2026-11-10.md), committed verbatim from the user's uploaded Claude Sonnet 5.5 report at `c031da6b97bc85ab7fe5c6b04354825a33419b60`. Reviewer status is explicitly **limited AI review** (not human, no direct GitHub history, no private original Panel E archive audit). Its original verdict is unchanged: `BLOCK_GLOBAL_PARITY`, conditional `ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY`, `NEEDS_REFERENCE_EVIDENCE`, scientific REV-2.4/D2/D3 **BLOCKED**.

## Reviewer's key follow-up: execution code versus reviewed code

Direct GitHub `fetch_file` at **each actual Actions run HEAD** versus the frozen reviewer-source snapshot `75a34897c84ee746feb96a874e0f2ac52789b93f`. All IDs below are **Git blob IDs**, not arbitrary named-branch file hashes. Equal blob IDs prove byte-identical Git file contents; this is not a rerun of MATLAB, HGFX, or Python science.

| Panel | Exact file path | Git blob at executed HEAD (equal to reviewed snapshot unless noted) |
| --- | --- | --- |
| G (run `42776781367`; head `c5c44d284a95b291c20d736e17bbb38ed1d865bd`) | `tools/compstat_rev24_manifest.py` | `84f4d7d3233b5e895e247a2c64ccb2148063bd83` — SAME |
| G | `tools/compstat_rev24_hgfx_eval.py` | `08c6e06cb9edd331ff1f38c0b7e8d74057ea4f68` — SAME |
| G | `tools/compstat_rev24_compare.py` | `1402b34246698e4fff623ab94e9a59e96e6d54b5` — SAME |
| G | `reference/matlab/run_compstat_rev24_matlab.m` | `98bd22e03ed622a0ae38aebdb54462d108715241` — SAME |
| E (run `42786519173`; head `4708518b0304eabb16fd0840f75d368cddb4710d`) | `tools/compstat_rev24_panel_e_inputs.py` | `7b9f9335f0d5c4204440d3f72f6e1e333f9c424b` — SAME |
| E | `tools/compstat_rev24_panel_e_hgfx.py` | `515c2614cc3597e54c3d1863395f1aa2e15640fa` — SAME |
| E | `tools/compstat_rev24_panel_e_compare.py` | `26067f9178eee2d1b9154997c22b8484f79d6ad9` — SAME |
| E | `tools/compstat_rev24_endpoint_coverage.py` | `8c8a1d3bc0f97625e992743db656c1fc0ae66d50` — SAME |
| E | `tools/compstat_rev24_endpoint_sources.py` | `8bc88e1fa17f55919a644ed312d1464684020b5b` — SAME |
| E | `reference/matlab/run_compstat_rev24_panel_e_matlab.m` | `d16c3a1a070379d65d75f4c14f41afc88aba4419` — SAME |
| Posthoc (run `42787522512`; head `1e090541836d778c1c24e83cfdaae9c4d72de5fa`) | `tools/compstat_rev24_endpoint_gap_bounds.py` | `152ef1da8d724a89727699c71ed0c200fc9dd9d9` — SAME |
| Posthoc | `.github/workflows/compstat-rev24-endpoint-gap-bounds.yml` | `8a064db372b56093a83607093236c67091ea4c9e` — SAME |
| All above | `evidence/revision/protocols/REV-2.4_PROTOCOL.md` | `9d36b914ddd52d1290d181ceebb086daf9179ecc` — SAME at run HEAD and reviewed snapshot |

**Two workflow file exceptions, fully accounted for:**
- G `.github/workflows/compstat-rev24-original-oracle.yml`: execution Git blob `5f1c0b50e2a6adc177ae89279ec372ac8d4f3ed6`; reviewed Git blob `209dcf7b81b49b69ae83e07b615d1b3391a4a880`.
- E `.github/workflows/compstat-rev24-original-panel-e.yml`: execution Git blob `3ddd9676ca04bdf23efa8db313785d38bb5413b8`; reviewed Git blob `0160255f8f32be1fc4d52db02494f139c4311093`.
- GitHub Compare API, run HEAD → reviewer snapshot, shows the **only** modifications to those two workflow files: removal of their one-shot `push` trigger and replacement of comments with a note that the run already launched. **All evaluation steps, numerical commands, environment, inputs, result audit and frozen model install steps are identical.** The changed workflow blob is therefore a change to future execution authorization, not the content of the completed scientific job. Reviewer should independently check these diffs before upgrading their conditional assessment.

## Protocol ancestry, late NaN encoding amendment, and original attempt

GitHub Compare API with base `d1986311b8a5ff97f088ebac35c612e16cbe89db` reports **status `ahead`, behind-by zero** and the base as the **merge-base** for all of:

- Original failed attempt `ae1adfbf5060ed3a2c64348a0119aca46088a851` (49 successor commits), [run `42776302837`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776302837) created **2026-11-10 07:35:04 UTC**.
- Actual Panel G retry `c5c44d284a95b291c20d736e17bbb38ed1d865bd` (56 successor commits), [run `42776781367`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776781367) created **2026-11-10 07:39:11 UTC**.
- Actual Panel E `4708518b0304eabb16fd0840f75d368cddb4710d` (72 successor commits), [run `42786519173`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786519173) created **2026-11-10 08:56:07 UTC**.
- Original posthoc-only audit `1e090541836d778c1c24e83cfdaae9c4d72de5fa` (77 successor commits), [run `42787522512`](https://github.com/ahmadkhanloo/hgfx/actions/runs/42787522512) created **2026-11-10 09:03:40 UTC**.

Git commits in the original first-attempt ancestry include `c5a116e1ee186ce4717d7bb95cbb23ea5a585785` (encode preexisting undefined NaN slots), `6d90909942f21ad5eb9d828f497f633297ec45ac` (synthetic NaN/inf tests), and `fdd0365e62af9161a309282582acdd0cc2d5e075` (protocol transport-only NaN addendum). These are **all ancestors of the first real paired attempt** `ae1adfb...`, not changes introduced after seeing its results. Their Git committer timestamps on 2026-11-09 are recorded in the compare API, but **timestamps alone do not prove when a server received a push**. The immutable SHA ancestry plus authenticated GitHub Actions run-head evidence is stronger evidence of what code and protocol existed when those runs executed. Server push webhooks or external append-only transparency logs have **not** been independently audited; retain this limit.

Original failed run `42776302837` is preserved (NumPy Boolean JSON serializer infrastructure failure). Sole authorized retry `42776781367` reused manifest semantic SHA256 `35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95`. The original failed artifact `13743169745` remains a separate historical object. **No new numerical experiment was performed during this follow-up.**

## Frozen MATLAB 8.2.0 source identity and actual CI check

- Both executed Git trees have the Git submodule entry `external/hgf-toolbox`: Git **mode `160000`**, type `commit`, SHA **`2437f4dc241541072722a2695ddeca7b44d83dd3`**, with `.gitmodules` pointing to `https://github.com/ComputationalPsychiatry/hgf-toolbox.git`.
- In both original Actions logs the `scripts/verify_reference_freeze.py` step says `Reference freeze verification: PASS`, pinned `commit=2437f4dc241541072722a2695ddeca7b44d83dd3`, `matlab_files=334`. The script checks HEAD, exact `.m` inventory against frozen `reference/matlab_manifest.tsv`, canonical-byte Git blobs and file sizes. Frozen manifest Git blob is `83256d8fca5b4c4d77dee68e7de01fa4e5ee9506`, identical at G and E run heads.
- This closes the *repository-side source identity and runtime validation* concern, **not** the fact that the external AI reviewer did not personally inspect the MATLAB Toolbox `.m` sources or execute the original scientific evaluators. Their original report should not be rewritten to claim they did.

## Original Panel E source archive identity — available but not shared as primary evidence

Local original historical source archives were SHA-256 checked against the frozen source manifest without reading or exporting raw participant-level values:

| Original source | Artifact | Verified whole-ZIP SHA256 |
| --- | ---: | --- |
| D02, 320-trial eHGF binary | `10339454535` | `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b` |
| D08, 614-trial continuous uHGF | `10339403480` | `c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de` |
| 64-subject original cohort | `13341288055` | `45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587` |

This is an **author-side archival source hash check only**. The AI reviewer still did not possess or re-evaluate original Panel E raw source archives. A controlled human review of those originals and the archived private evaluation limitation is OPEN. No private records or full vectors were committed or attached to this public report.

## Scope, verdict, and no-overclaim policy

The reviewer independently recounted **Panel G 560 paired-valid / 39 both-invalid / 1 one-sided-invalid** with a 600-row denominator and **164/200 valid HGF** within the old M8 objective gate. For Panel E they confirmed **131/132 paired-valid from sanitized fields** and HGF **128/128** passing statuses, **not** a first-principles raw recomputation. All of that remains exactly as in their unmodified review.

Potential same-vector objective language is **HGF-only**, with the original 36 jointly invalid HGF draws and all family limitations visible. The reviewer notes that only 3 free parameters/family were varied in Panel G, limiting global coverage. `REV24-G-ehgf_binary-019` is `UNEXPLAINED_ONE_SIDED_INVALID` until reference latent states at trials 10–11 are available. eHGF/uHGF family-wide objective parity, original D02 missing HGFX full endpoint, fitting/optimizer/Hessian/trajectory/identifiability and original subject-7 failures all remain unsupported or failing.

**No gate reclassification:** `BLOCK_GLOBAL_PARITY`, `ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY=CONDITIONAL`, `NEEDS_REFERENCE_EVIDENCE`; REV-2.4 global science **BLOCKED**; D2/D3 **BLOCKED**. Human domain-expert countersignature is requested by the AI reviewer before the work is cited as independent scientific adjudication. No third Panel G/E execution is authorized by the original protocol.
