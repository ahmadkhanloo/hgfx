# PERF-01C — authenticated original raw evidence and independent reviewer return packet

Prepared: 2026-11-08. **AUTHOR-PREPARED EVIDENCE AND INSTRUCTIONS; NOT AN EXTERNAL INDEPENDENT REVIEW.**
Objective: remove the previous *raw original archive inaccessible* blocker and ask a genuinely independent scientist/methodologist to adjudicate the original 28 cases, seven-forward restricted candidate and unresolved CPU-thread environment. **PERF-01C = BLOCK_FREEZE / NOT FROZEN.** No timers/speedup/GPU claim are authorized.

## Immutable source and branches to review

| Surface | Source / exact known SHA | Status |
|---|---|---|
| Original primary CPU candidate | [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), `271e480216ed8ecd19f76c960b75a3826ed89337` | Original nine-standard-HGF scope, **6/9 BLOCKED** |
| Original 28-case evidence, cohort fit | [PR #99](https://github.com/ahmadkhanloo/hgfx/pull/99), `81d9e8fc67c1d801f7d749cf44ba9fcfffdbf1f3` | 16 review-pending/12 blocked |
| Author-published AI-assisted report | [PR #100](https://github.com/ahmadkhanloo/hgfx/pull/100), `eda00c9d60fe44fe90c601c6a811f4493819f270` | `BLOCK_FREEZE`, **NOT independently signed** |
| Original frozen HGFX | `v1.0.0` — `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` | Immutable scientific reference |
| Frozen MATLAB HGF toolbox 8.2.0 | `2437f4dc241541072722a2695ddeca7b44d83dd3` | Immutable scientific oracle |
| Seven Forward full-output evidence | [PR #101](https://github.com/ahmadkhanloo/hgfx/pull/101) `88e7150f6349abdcd3ea78dca1aa9295c2edbe7e`; [PR #102](https://github.com/ahmadkhanloo/hgfx/pull/102) `be5a3ed7e91c6dec9e09b4c8459e584bae26e8f1` | **7/7 UNTIMED diagnostic**, not scientific signoff |
| CPU physical-host/BLAS environment | [PR #103](https://github.com/ahmadkhanloo/hgfx/pull/103) `96b77bf80eec748054120ab5249400f42868533c` | Same host+affinity observed, **MATLAB `MKL_NUM_THREADS` empty** |
| MATLAB native OpenMP read-only probe | [PR #104](https://github.com/ahmadkhanloo/hgfx/pull/104) `e6ff1c47151a3445b6ac2af79b492c399d6d5602` | `omp_get_max_threads=1` TARGET only, actual MKL workers unknown |
| Raw archive replay author tools | **this stacked research PR** on #104 | Pure evidence-integrity check; reviewer must verify actual fetched HEAD |

Reviewers must record the **actual fetched full PR SHA** in their own report, not assume a document's historic pin is the current head. No scientific source/threshold/data/seed/optimizer has been altered in these stacked PRs.

## Authenticated ORIGINAL raw artifacts — previously unreviewable

The original paired 64-subject 128-trial HGF full public fit and the seven-forward full-output task were **downloaded from their original GitHub Actions artifacts and independently SHA-256 verified** on 2026-11-08. These are original source outputs, not a reconstruction from derived report text.

| Provenance | Original raw ZIP SHA-256 | Raw members and SHA-256 |
|---|---|---|
| [Run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), [artifact 13341288055](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006/artifacts/13341288055) | `45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587` | `comparison.json` `97877d64f609a62b3ca10674809907ae18562321c170f9b47aebaf672f3fcede`; `hgfx_raw.json` `6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb`; `matlab_raw.json` `2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98` |
| [Run 42481218455](https://github.com/ahmadkhanloo/hgfx/actions/runs/42481218455), [artifact 13617382986](https://github.com/ahmadkhanloo/hgfx/actions/runs/42481218455/artifacts/13617382986) | `6928272eeab342df85a833fa2ce058d713202495fb2f666bb3c7b3307cd21a95` | `forward7_boundary_comparison.json` `dc859460b2f61770e9ef8ef0e173776f21a054f0ce0195f41ab66757a7e8c61f`; `hgfx_forward7_boundary.json` `8abf2b6de3ae805365d867ce6f9101022826733ebf949c389578c50b2a132ff3`; `matlab_forward7_boundary.json` `d8d83ee30c935f17350d0934b4f92da2a930145f01eb60470640122fc7afa639` |

The [GitHub Actions raw replay workflow](../../.github/workflows/perf01c-raw-artifacts-replay.yml) downloads original artifacts using `gh run download`; in that workflow the extracted member hashes are independently checked, but it **does not claim it rehashed the original GitHub ZIP** after extraction. Use actual original ZIPs when additionally checking ZIP hashes. The fixed checksums and original failing status are immutable evidence guards, **not adjustable parameters**.

## Observations from raw source bytes

- Original `matlab_raw.json` explicitly resolves `fitModel` to `/reference_toolbox/core/fitModel.m` and `hgf_binary` to `/reference_toolbox/_original_models/hgf_binary.m`. The old source-name collision is no longer unknowable for this *specific original run*. This does **not** establish current working directory/path resolution for every subsequent run.
- Original 64 full public fits: archived 64-case comparison and raw trajectories show **63 within preexisting diagnostic tolerances, 1 NONPASS** (zero-based subject **7**). For `traj.mu` and `traj.muhat`, direct per-cell arithmetic from real raw arrays (not trusting archived `mismatch_count`) gives **4 and 4 actual threshold exceedances**, at historical frozen `atol=3e-10,rtol=3e-8`, with maximum absolute difference `1.5704625655477145e-9` in each field (most values pass). This is scientifically NONPASS, regardless of how small individual differences look.
- Original 7-forward raw outputs retain the complete 11 trajectory fields and `N×3×4` state arrays for standard HGF 128; eHGF and uHGF 128/512/1024, using original first subject. Active reference paths on this exact run: `_original_models/hgf_binary.m`, `_original_models/ehgf_binary.m`, and `perceptual/uhgf_binary.m`. All seven were preliminary diagnostic-concordant under existing source tolerances; **not a prospective scientific or benchmark PASS**.
- The previous actual CPU host/threads diagnostic correctly remains **BLOCKED**. Running in one GitHub job proved matching boot, CPU and affinity, but `MKL_NUM_THREADS` inside MATLAB was empty while Python requested `1`. Later true MATLAB in-process native MEX returned `omp_get_max_threads=1` (OpenMP *target cap*), with `mkl_get_max_threads` unavailable. Neither observation measures actual active MKL/BLAS worker count or resolves the original policy failure. No actual CPU runtime performance samples have been collected.

## Repeatable raw scientific integrity check

On the actual fetched head of this stacked PR:

```bash
git clone https://github.com/ahmadkhanloo/hgfx.git hgfx-perf01c-audit
cd hgfx-perf01c-audit
git fetch origin pull/105/head:refs/remotes/origin/perf01c-raw-replay
git switch --detach refs/remotes/origin/perf01c-raw-replay
git rev-parse HEAD # record the actual SHA; PR number may vary on a fork
python -m pip install 'numpy==2.3.5'
python -m unittest discover -s tests -p 'test_perf01c_raw_archive_replay.py' -v
mkdir -p /tmp/hgfx-perf01c/fit /tmp/hgfx-perf01c/forward
gh run download 41863441006 --repo ahmadkhanloo/hgfx \
  --name perf01-64-full-fits-41863441006 --dir /tmp/hgfx-perf01c/fit
gh run download 42481218455 --repo ahmadkhanloo/hgfx \
  --name perf01c-forward7-boundary-untimed-42481218455 --dir /tmp/hgfx-perf01c/forward
python benchmarks/runtime_v1/verify_perf01c_raw_archives.py \
  --root benchmarks/runtime_v1 \
  --original-fit /tmp/hgfx-perf01c/fit \
  --forward7 /tmp/hgfx-perf01c/forward \
  --output /tmp/hgfx-perf01c/verified.json
```

The validator hardcodes expected artifacts and member hashes, **re-executes the original unchanged full-64-field Python comparator** on raw MATLAB/HGFX source arrays, checks equality with the **original archived and Git-tracked** full-fits summaries, independently recounts the original eight subject-7 exceedances using only basic arithmetic, and re-executes the unchanged all-field seven-forward comparator with source path checks. It rejects missing/duplicate source members, altered bytes, changed subject and case denominators, altered scientific outcomes or new performance claims. It emits **`AUTHOR_SIDE_RAW_EVIDENCE_REPLAY_SUCCESS_NOT_SCIENTIFIC_ACCEPTANCE`**, never `PERF-01C PASS`.

The original 28-case worksheet and external reviewer instructions still apply; this script does *not* replace the scientific reviewer. If artifact download is no longer available, report the blocker rather than substituting summaries, and do not claim reinspection.

## Questions for a genuinely independent reviewer

1. Independently inspect **all 28 planned cases** and original failure denominators, the actual raw 64-subject public-fit artifact, original source/model/start/mask configuration and the exact active MATLAB paths. Does the **seven-case forward-only** question have adequate Level-0/Level-1 scientific eligibility? It can be **scientifically plausible while PERF-01C remains blocked**.
2. Is the proposed one-call Forward-only boundary in [PR #102](https://github.com/ahmadkhanloo/hgfx/pull/102) *actually* equivalent across MATLAB and NumPy, including full outputs, materialization, interface overhead and active source resolution? Which acceptance conditions must be added, if any, **before** a new timer is implemented?
3. Can a **new prospective CPU host/threading policy** be justified using existing direct native OpenMP and `maxNumCompThreads` evidence, given MATLAB's absent `MKL_NUM_THREADS` and **unverified active MKL workers**? If not, specify the *smallest decisive additional hardware/thread measurement* needed. **Do not retroactively deem the previously failed rule PASS.**
4. Evaluate shared/contended GitHub runner, pinning/affinity, BLAS implementation dispatch and frequency/power controls for the intended performance estimand. Avoid claiming one-runner identity proves stable uncontended CPU throughput.
5. Preserve original full-fit **63/64 NONPASS**, original 28-case **16 REVIEW_PENDING/12 BLOCKED**, six of nine original primary cases blocked. Do not relabel failed fitting as an accepted Level-2 exception without independent scientific reference evidence, or combine seven selected cases into an unapproved headline speedup.

**Required external return:** a new reviewer-authored signed Markdown report on a fresh `review/perf01c-<reviewer>-<date>` branch, with reviewer identity, independence statement, exact PR/source/runs/artifact/member SHAs, all 28 case findings, frozen-tolerance decisions, CPU policy adjudication and closure requirements; commit/push under the reviewer's account, create a separate review-only PR and sign an Issue #88 comment. Follow the complete [reviewer git/commit/push/return guide](PERF01C_REVIEWER_GIT_COMMIT_PUSH_RETURN_GUIDE_2026-11-08.md). Until all requirements are met, the only defensible official freeze verdict is **`BLOCK_FREEZE`**. Existing owner-published AI-assisted report [PR #100](https://github.com/ahmadkhanloo/hgfx/pull/100) is not independent signoff.

**No prospective timer workflow, scientific waiver, acceptance-threshold relaxation, dataset/subset re-selection or performance result is created by this packet.**

## Executed exact raw-member replay and provenance-only mismatch resolution

- **[Actions 42494216216](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494216216)** at authored source SHA `4787ed3abee975ce074f2e498e3ea93d7df73411`: **SUCCESS as author-side raw evidence integrity replay, not scientific approval**. Authenticated GitHub CLI independently downloaded the two *original historical* artifacts; seven archive/tolerance corruption tests passed. The full 64-subject original comparator and seven-forward 12-full-field comparator reconstructed the *archived original reports* from all six pinned real raw member files, with no timer.
- The initially strict tracked-Git summary equality check **failed** at [run 42494004896](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494004896) and [42494130567](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494130567). The latter provided the exact difference: the tracked full-fit summary contains **three additional provenance-only keys** `github_run_id`, `raw_evidence_location`, and `raw_evidence_sha256`, absent from the raw-run original `comparison.json`. The scientific comparator output itself matched exactly. The final verifier **requires an exact, enumerated three-key provenance set** and validates their values against the original run ID and raw member hashes. It continues comparing **all scientific fields without exclusions or threshold relaxation**. The failed initial checks remain in GitHub's workflow history.
- **Recomputed scientific result:** original full-fit 64 subjects, 63 diagnostic-concordant and **one SCIENTIFIC NONPASS**, zero-based subject 7. Independent direct math checks of the two raw trajectory matrices found `traj.mu` failed at zero-based `[83,1], [108,1], [116,1], [126,1]`, and `traj.muhat` at `[84,1], [109,1], [117,1], [127,1]`; max absolute delta `1.5704625655477145e-9`, frozen `rtol=3e-8, atol=3e-10`. All 7 prospective Forward-only candidate cases remain complete-output **UNFROZEN_DIAGNOSTIC_CONCORDANCE**. Nothing was reclassified.
- Original raw fit paths specifically resolve `reference_toolbox/core/fitModel.m` and `reference_toolbox/_original_models/hgf_binary.m`; seven Forward source paths resolve standard HGF/eHGF to `_original_models` and uHGF to `perceptual`. These path values were read from original raw records and verified against the expected frozen model identities.
- [New archival verification report artifact 13623215535](https://github.com/ahmadkhanloo/hgfx/actions/runs/42494216216/artifacts/13623215535) was downloaded via authenticated GitHub API and its ZIP bytes independently rehashed: `sha256:57e18cfed3c2c3b569fa27653380151743564a68437d07b8f83252f95135f3cb`, matching GitHub's artifact digest. Its sole JSON member `raw_archive_replay.json` has `sha256:4ba328786dc9d36b598cd88d063ee8e6a57171bb807abceddf11742a88aeca44`. It explicitly and correctly states `EXTRACTED_MEMBERS_SHA256_ONLY_NO_ZIP_CLAIM` for the original two artifacts as downloaded by this GitHub Actions workflow. Their original full ZIP bytes were independently downloaded and verified in the **separate initial source retrieval** documented above.
- **Remaining gates:** independent external source/methods review not received; environment still `BLOCKED_MATLAB_MKL_ENV`, original 28 cases 16 pending/12 blocked, original full-fit scientific gate fails 63/64, no matched CPU timing / no physical GPU or speedup result. The original manuscript/release claim must not change.

**Verdict: RAW ARCHIVE BYTE INTEGRITY & RECOMPUTATION DONE (author-side); PERF-01C still `BLOCK_FREEZE / NOT FROZEN`.**
