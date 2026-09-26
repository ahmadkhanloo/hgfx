# P8 paper-delta review scope

Status: **ROUND-3 CANDIDATE LOCKED / READY FOR INDEPENDENT DELTA REVIEW**

The full v1 implementation/release review is **not repeated**. The accepted independent baseline is:

- independent review target: `ad8f5cd6fbea3bd1e5ac1cef8b51dbbb9a970a84`;
- post-review remediation validated source: `09c49031cda95b449f8115030a9d32dcba36098e`;
- H1/H2: resolved;
- post-remediation status: no unresolved CRITICAL/HIGH findings.

Two independent P8 paper-delta reviews are preserved as historical evidence. The most recent reviewed content candidate was `b66f294f4799968404273127a9b06b4fc451ffb3`, which returned **FAIL** with one HIGH blocker plus MEDIUM/LOW findings. Round-3 remediation is now locked at content candidate `897aed804901f9f49ad1d73ecfab6fa714d50098` (tree `2c50052dfd06b3013ee5402f56caa4b640ab4cce`). The deterministic delta manifest for that exact candidate is committed and the full-history P8 Delta Scope gate passed in run `36260789049`. No frozen MATLAB reference file or frozen v1 release-evidence artifact changed.

For an exact candidate SHA, regenerate the deterministic file-level delta with:

```bash
python paper/scripts/generate_p8_delta_manifest.py --candidate-sha <40-hex-candidate-SHA>
pytest -q tests/paper/test_p8_delta_manifest.py
```

Output: `docs/research/P8_DELTA_MANIFEST.json`.

The JSON manifest is authoritative for the exact candidate SHA, commit count, changed-file count, review-class counts, and frozen-reference-change assertions. Do not copy those values manually into this guide.

## Reviewer priority

Review in this order:

1. **PAPER_REVIEW_REQUIRED** — manuscript, P2A/pyhgf evidence, P3 evidence, tables, figures, reproducibility, claim audit, post-fix backend evidence, and JNM preflight.
2. **EVIDENCE_PROVENANCE_REVIEW_REQUIRED** — only provenance/release-context changes that support manuscript claims.
3. **PRODUCT_ONLY_CHECK_CLAIM_LEAKAGE** — do not repeat v1 implementation review; verify that additive v1.1 code has not leaked into paper-1 claims.
4. **MAINTENANCE_CONTEXT_ONLY** — inspect only if a direct paper/evidence dependency is found.

The generator must classify every changed path. Post-fix paper evidence under `gpu_validation_results/` and its dedicated P8 CPU-evidence workflow are part of the paper-review delta. The generated manifest also asserts that no frozen `reference/matlab/` file and no `reference/validation/v1_release/` artifact changed between the accepted post-remediation baseline and the candidate.

P8 can close only when the final bounded delta review records no unresolved CRITICAL/HIGH finding for the exact locked candidate SHA. After that PASS is committed, and only then, P6A may be promoted to `FROZEN_FOR_SUBMISSION` for that exact candidate.
