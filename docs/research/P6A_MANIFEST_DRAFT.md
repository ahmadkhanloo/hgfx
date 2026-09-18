# P6A paper-evidence manifest — DRAFT_NOT_FROZEN

Status: **DRAFT_NOT_FROZEN / P6A-1 DONE-PASS / P6A-2 DONE-PASS / P7-P8 OPEN** (2026-09-18)  
P6A-1 merge: `56c64678550ef87744b27630d20bf8de0c72a5a8`  
P6A-1 read-only CI: run `35333572515` — PASS  
P6A-2 merge: `c1bcd6a80556138ee1af6a8bf4e23d1bc616b821`  
P6A-2 read-only CI: run `35335397062` — PASS  
Manifest inventory: **57 committed paper evidence/source artifacts**  
Numerical claim audit: **48 mapped claim lines / 9 explicit exemptions / 20 automatic structural-editorial exemptions / 0 unmapped**  
Manifest ID: `hgfx-paper-evidence-manifest-1`  
Generator: `paper/scripts/generate_p6a_manifest.py`  
Output: `paper/reproducibility/p6a_paper_evidence_manifest.json`

Do **not** flip this manifest to `FROZEN_FOR_SUBMISSION` until an independent P8 review records `PASS` for the exact submission-candidate SHA.

Anchors:

- HGFX v1.0.0: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- MATLAB HGF Toolbox 8.2.0: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- public stable package: `hgfx==1.0.0`
- P2A run: `35268575414`
- P3 run: `35272347167`
- P3 aggregate SHA-256: `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`

## P6A staging

P6A is intentionally split into small stages:

1. **P6A-1 — DONE / PASS — evidence inventory and integrity manifest**: generate a deterministic `DRAFT_NOT_FROZEN` JSON manifest containing hashes for raw paper evidence, generated tables, all canonical PNG/PDF figures, generator scripts, protocol/reproducibility files, and the current manuscript/bibliography. Preserve all negative/inconclusive classifications explicitly.
2. **P6A-2 — DONE / PASS — claim audit**: every current numerical/versioned manuscript line is either mapped to exact committed evidence or explicitly exempted as non-claim structure/editorial metadata; high-risk demo, S7, GPU, pyhgf and P3 values are machine-checked. Output: `paper/reproducibility/p6a_claim_audit.json`.
3. **P7 — exact manuscript candidate lock**: record the exact candidate SHA to be reviewed.
4. **P8 — independent review**: an independent reviewer audits the exact candidate and records PASS/FAIL.
5. **P6A final freeze**: only after P8 PASS, regenerate the manifest with `status=FROZEN_FOR_SUBMISSION` and the exact candidate SHA.

This ordering resolves the distinction between having the P6A evidence inventory ready before manuscript lock and performing the irreversible submission freeze only after independent review.

## P6A-1 required classifications

The draft manifest must preserve, without reinterpretation:

- historical M18 scientific validation: `FAIL_PRESERVED`;
- D02: `REFERENCE_LIMITATION_MATCH`;
- D08: `REFERENCE_LIMITATION_MATCH`;
- S7 parameter recovery: `REFERENCE_LIMITATION_MATCH`;
- S7 paired model selection: `PASS_PAIRED_MODEL_SELECTION_36_OF_36`;
- pyhgf mapped perceptual quantities: 11/11 pass in the single authorized common-scope cell;
- pyhgf participant-response NLL: `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`;
- P3: `INSUFFICIENT_REFERENCE_EVIDENCE`, `gate_pass=false`;
- historical M18 unchanged by P3;
- physical GPU evidence: applicability/correctness only, not a speed claim;
- general performance/scaling: not activated under paper protocol 1.

## Freeze guard

`generate_p6a_manifest.py --status FROZEN_FOR_SUBMISSION` must fail unless:

- a valid 40-character candidate SHA is supplied;
- `docs/research/PAPER_P8_REVIEW_CHECKLIST.md` records the exact candidate SHA;
- the P8 result is `PASS`.

P6A is separate from M19. Nothing in this gate may modify or reinterpret the frozen v1.0.0 release evidence.
