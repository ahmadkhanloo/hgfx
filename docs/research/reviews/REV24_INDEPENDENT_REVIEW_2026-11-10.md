# REV-2.4 independent scientific review (LIMITED REVIEW, offline evidence packet)

**Verdict in one line:** `BLOCK_GLOBAL_PARITY` = YES. `ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY` = CONDITIONAL (see section 5). `NEEDS_REFERENCE_EVIDENCE` = YES. REV-2.4 scientific gate = BLOCKED. D2/D3 = BLOCKED.

## 1. Reviewer provenance

| Field | Value |
| --- | --- |
| Reviewer | Claude (Anthropic AI model, Claude Sonnet 5.5), working in a sandbox from an uploaded evidence packet. **Not a human reviewer, no GitHub access, no authorship of the reviewed work.** A human domain expert should countersign before this is cited as independent adjudication. |
| Date | 2026-11-10 (UTC) |
| Reviewed code SHA (per packet) | `75a34897c84ee746feb96a874e0f2ac52789b93f` |
| Packet ZIP SHA-256 | `7bb43d773117253923d0e5908a76cd318ee5e89d3e22b82db7a48564b709d16f` |
| Review type | **Limited review with unavailable primary data** (Panel E raw archives absent; no git history; no MATLAB) |
| Branch / commit / PR / comments | **None created.** No write access. This file is returned to the user for submission unmodified. |
| Independence | Partial. I did not author the protocol or tools, but I received the packet and framing from the project side, and the packet's README states the prior status I was expected to review. |

## 2. Commands actually run (all read-only; no HGF objective was evaluated)

1. `unzip` packet; `sha256sum -c SHA256SUMS.txt` → all 48 listed files match (no mismatches).
2. `python3 verify_reviewer_packet.py` → PASS lines reproduced. I did **not rely on it**: it ships with the packet and is part of the author-side material.
3. Own Python recount from raw JSON of `matlab.json`, `hgfx.json`, `comparison.json`, `manifest.json` (Panel G) and `panel_e_comparison.json`, `input_source_audit.json`, `endpoint_gap_bounds.json`.
4. Own regeneration of Panel G inputs `u`, `y` from the protocol formulas and their binary64-LE SHA-256.
5. Own regeneration of all 600 transformed vectors from `numpy.random.Generator(PCG64(seed))` using the manifest's prior means/variances and the protocol's rule (`mean + sqrt(var)*z` on free indices).
6. Query of PyPI JSON for `hgfx==1.0.0` file digests.
7. Source reading of the HGFX evaluator, MATLAB runner, comparator, protocol, retry record, ledger.

## 3. Evidence checklist

| Check | Result | How |
| --- | --- | --- |
| Packet integrity | **VERIFIED** | Step 1 |
| Panel G ZIP and member hashes | **VERIFIED** | Step 1 and verifier member hashes |
| Panel G denominator 600 (200×3); case-ID/SHA ordering identical across MATLAB, HGFX, comparison | **VERIFIED** | Own recount, asserted per case |
| Panel G validity counts: 560 both-valid / 39 both-invalid / 1 one-sided | **VERIFIED** | Own recount. By family: HGF 164/36/0; eHGF 198/1/1; uHGF 198/2/0 |
| Panel G inputs `u`,`y` follow the protocol formula and match manifest hashes | **VERIFIED** | Step 4 |
| Panel G 600 vectors reproduce from the stated seeds and rule | **VERIFIED** (0 mismatching entries, max diff 0) | Step 5. Done with NumPy 2.5.4, original used 2.0.2; the stream matched exactly |
| Seeds in manifest = protocol seeds (2026111000/1/2) | **VERIFIED** | manifest `strata` |
| Provenance fields identical in MATLAB and HGFX outputs (protocol, manifest hash, input hashes, release commit `4dd8fbd8`, MATLAB ref `2437f4dc`) | **VERIFIED** | Own comparison |
| HGFX 1.0.0 wheel SHA-256 `5c63c16d…0b90` is the PyPI wheel | **VERIFIED** | PyPI JSON digest matches; upload date 2026-09-17, before the runs. HGFX runtime in `hgfx.json` records `hgfx_distribution 1.0.0` imported from site-packages |
| Panel G HGF M8 gate, 164 both-valid | **VERIFIED** (0 failures at field and per-trial level, recomputed with `atol=2e-13, rtol=2e-11`) | Own recompute. Max field diff `7.28e-12` (≈3.9e-5 of the limit); max trial-level diff is **0.43 of the limit**, the closest approach to the gate |
| Validity rule symmetric between HGFX and MATLAB runners | **VERIFIED by source reading** | Both require all 128 trial log-likelihoods and all three objective scalars finite |
| Panel E: 66 cases, 132 slots, 131 paired-valid, 1 missing | **VERIFIED** (sanitized report) | D02-HGFX slot is `INSUFFICIENT_REFERENCE_EVIDENCE` |
| Panel E: 128 HGF slots all `SHARED_OBJECTIVE_WITHIN_EXISTING_GATE`, max gap `2.842e-14` | **VERIFIED from report fields**; gate limits not independently recomputable (objective values not in the packet) | Own max scan. 111 of 128 log-likelihood gaps are exactly 0; all 17 nonzero ones are 1 or 2 ulps (1.42e-14, 2.84e-14) of a value in [64,128). That is the expected scale of floating-point rounding for objectives of this magnitude, so exact agreement is plausible, not suspicious |
| D02 = `ehgf_binary+unitsq_sgm`; D08 = continuous `uhgf+gaussian_obs` | **VERIFIED** (report and audit labels) | Not checked against raw archives |
| Posthoc bounds (max `3.402e-10`, subject 7 `1.087e-10`, D08 `3.979e-10`) | **PARTIAL**. Values match the report; arithmetic not recomputed because archived own-fit objectives are not in the packet | |
| Original Panel E raw archives (D02 `10339454535`, D08 `10339403480`, cohort `13341288055`) | **NOT VERIFIED** (absent by design) | |
| Preregistration chronology at `d1986311…` | **NOT VERIFIED** | No git repository and no push events in the packet. Run metadata only gives run times (Panel G failure 07:35Z, retry 07:39Z, Panel E 08:56Z, posthoc 09:03Z on 2026-11-10). That fits the story but cannot prove commit ordering |
| **Code executed in the runs = code reviewed** | **NOT VERIFIED** | Runs executed at `c5c44d28…` (G retry), `4708518b…` (E), `1e090541…` (posthoc); the packet code is at `75a34897…`. No per-file hashes at the executing SHAs are provided |
| Frozen MATLAB 8.2.0 source identity | **NOT VERIFIED** | Only the recorded commit string `2437f4dc…` is seen; the toolbox source was not provided |
| Family objective gates for eHGF/uHGF | **NOT FOUND** in packet (ledger, protocol, comparator) | Consistent with `NO_PREDECLARED_FAMILY_OBJECTIVE_GATE`. I could not search the wider repo history |
| Historical failures (subject-7 trajectory, 63/64 NONPASS, M18, P3, PERF-01C) unchanged | **VERIFIED as stated** in protocol/ledger/reports; the original fit evidence is not in the packet and was not re-tested | |

## 4. Findings

### 4.1 Scope of what the data show
Same-vector objective agreement is strong for HGF. At 164 valid prior-grid vectors and 128 original fit endpoints, MATLAB and HGFX agree to rounding level, far inside the M8 limit. This says nothing about fitted parameters, optimizer paths, Hessians or covariances, or identifiability. The posthoc cross-fit gaps of order 1e-10 do not contradict the historical subject-7 trajectory failure, because objective values at two endpoints can coincide while the parameters differ.

### 4.2 Panel G denominators must stay full
- 36 of 200 HGF prior draws (18%) are invalid on both sides. The HGF claim covers **164/200**, not 200/200.
- "Both-invalid" shows agreement on validity, **not on cause**. MATLAB records `tapas:hgf:NegPostPrec` (33) or `tapas:hgf:VarApproxInvalid` (3); HGFX returns a `realmax` sentinel with an empty `error_type`. The HGFX-side reason is not recorded.
- The three families expose only **3 free parameters each**, drawn from the priors. The grid is an implementation probe of that slice and does not cover the regions fitted models reach.

### 4.3 `REV24-G-ehgf_binary-019` (case SHA `276d21f4…fefb`)
Classification `UNEXPLAINED_ONE_SIDED_INVALID` is the right label. Observed facts: both `rval` = 0; MATLAB is valid with `negLl = 2607.66` and trial log-likelihoods that repeat the same value `-43.9649` or sit near 0 (`~1e-15`, `~1e-18`), which looks like probability saturation; HGFX is finite through trial 10, then NaN from trial 11 (indices 11–20 are NaN at minimum) while MATLAB stays finite. A persistent NaN after one trial points toward state propagation, not an isolated log of zero. **Candidate causes, none established:** unclipped or differently clipped saturated predictions, an overflow/underflow in the eHGF update at extreme parameters, or a difference in how the two implementations floor precisions. The case sits in an extreme regime (objective ≈ 2.6e3 vs ≈ 1e2 at fitted endpoints), so it may matter little for fitted use, but this is untested. Latent state is `NOT_EXPORTED`, so I do **not** classify it as a model limitation or as an HGFX defect. It needs a separately preregistered diagnostic that exports level states at trials 10–11.

### 4.4 eHGF and uHGF
Descriptive discrepancies computed with the M8 formula (not a gate): eHGF max field ratio `2.0e-4`, max trial ratio `0.28`; uHGF `3.4e-4` and `0.57`. They are small but **must not be reported as passes**. `NO_PREDECLARED_FAMILY_OBJECTIVE_GATE` stands. D08 is continuous `uhgf+gaussian_obs` and cannot support any claim about binary uHGF.

### 4.5 Process and documentation issues
1. **Executed vs reviewed code (above) is the largest unverified link.** Please supply `git hash-object` (or file SHA-256) of each `tools/compstat_rev24_*.py`, the MATLAB runners, and the workflows at `c5c44d28`, `4708518b`, `1e090541`.
2. The protocol's NaN-encoding amendment came after the freeze and after "identifying a generator bug". It is described as transport-only, made before any paired run, and the regenerated vectors match the rule exactly. I accept it as non-scientific, but its commit timing relative to run `42776302837` is unverified and the history must be shown.
3. The one infrastructure retry is consistent with the record (the failed run died on serialization of `numpy.bool_`; the retry reused the same manifest hash `35e7c766…`, which I verified in both output files). The failed run's artifact `13743169745` was not in the packet.
4. `reference/matlab/run_compstat_rev24_matlab.m` line 4 still says "UNVALIDATED SOURCE pending true MATLAB execution". Stale after the run. Leave the file as is and add a dated note elsewhere.
5. All five objective differences at D02 (MATLAB endpoint) and D08 (both endpoints) are exactly 0.0. Plausible at this magnitude (see checklist) and unverifiable without raw data.

### 4.6 Reproducibility and privacy
Public: the complete synthetic Panel G artifacts (fully auditable). Not public: Panel E raw inputs, endpoint vectors, per-trial outputs (deleted by CI). Only SHA commitments exist for them. GitHub Actions artifacts expire, so the run links will not last. Recommended: archive the packet and the three artifact ZIPs with a DOI; keep the private data under controlled access with its hash recorded; state in the manuscript that Panel E is auditable only through a controlled channel.

## 5. Final scoped verdict

- **`BLOCK_GLOBAL_PARITY`: YES.** Evidence is objective-only; fit-level history is unchanged and failing.
- **`ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY`: CONDITIONAL.** Population: `hgf_binary + unitsq_sgm`, Panel G **164 of 200** both-valid prior-grid vectors (36 jointly invalid retained) and Panel E **128 of 128** original endpoint slots (64 subjects × 2 endpoints). The Panel G part is verified from raw data. The Panel E part rests on the sanitized report. The condition: confirm that the executed code equals the reviewed code (4.5.1) and, ideally, that a human checks the Panel E raw archives.
- **`NEEDS_REFERENCE_EVIDENCE`: YES** for (a) `REV24-G-ehgf_binary-019` first cause, (b) any eHGF/uHGF objective claim, (c) the missing D02 HGFX endpoint.
- **REV-2.4 scientific gate: BLOCKED.** D2/D3: BLOCKED.
- This is a **limited review with unavailable primary data**, not a full independent review.

## 6. Suggested manuscript wording

> At each of the two original fitted endpoints of the 64 `hgf_binary` subjects, MATLAB and HGFX 1.0.0 evaluated the same transformed vector; all 128 objective comparisons met the previously established M8 criterion (maximum absolute negative-log-joint difference 2.84×10⁻¹⁴). On a synthetic prior-draw grid, 164 of 200 HGF vectors were valid in both implementations and agreed within the same criterion; 36 were invalid in both. These results concern objective values at shared vectors only and do not establish equivalence of fitted parameters, optimizer trajectories, Hessians, or inference. One eHGF grid vector was finite in MATLAB and non-finite in HGFX (cause undetermined), one original D02 HGFX endpoint was unavailable, and no predeclared objective criterion exists for eHGF or uHGF.

## 7. Return protocol

Report file, branch, commit SHA, PR URL, issue/PR comment links: **not created** (no write access). Remaining blockers to sign-off: executed-code hashes, git push chronology, frozen MATLAB source, Panel E raw archives, a human countersignature.

**Signature:** Claude (AI model), limited offline review, 2026-11-10.