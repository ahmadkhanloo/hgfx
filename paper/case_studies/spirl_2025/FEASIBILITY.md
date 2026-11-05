# SPIRL fallback feasibility - 2026-11-04

**BLOCKED_CUSTOM_JOINT_MODELS_REQUIRE_NEW_MIGRATION.** No fits were run. Existing licensed archive/data and historical acquisition records are preserved.

DOI https://doi.org/10.5334/cpsy.116. Source snapshot 86fd5122a744acfb5bc7ba12720426d8b4aa0ffa; zip CRC passed and files were extracted locally. feasibility_manifest.json records the archive and extracted-file hashes. UPSTREAM_README.md specifies MATLAB R2019b; TAPAS 604c568, VBA aa46573, RainCloudPlots d5085be. These historical pins differ from oracle 8.2.0 and are not treated as interchangeable. Submodules are not bundled in the archive. Data availability/integrity (20 pilot and 59 main records) is established by the preserved acquisition manifest; that is not semantic eligibility.

Opened utils/spirl_setup_model_space.m: seven model pairs M1-M7 all call spirl_tapas_ehgf_binary/config. M1-M4 are informed-RT variants and M5-M7 uninformed-RT variants. Opened utils/spirl_specs.m: nRandInit=399, rng(123,'twister'), pilot and main remain distinct. Inspected hgf_extensions and comb_obs_models: custom forward/config/transform and all seven combined choice/RT families with simulations are present. Their names/configs do not exist as validated exact study pairs in HGFX 1.0.0. These GPLv3 sources must remain separate from MIT core; no copying/translation was performed.

Retaining only choices, using standard eHGF, reducing restarts, or tuning priors on main data would change the published procedure. A complete port requires a separate licensed migration, equation/transform/mask audit and MATLAB golden fixtures for the joint response models. The handoff explicitly stops case work instead of silently adding this core scope. Protocol/fitting/real-data figures are therefore NOT RUN. This is the predetermined fallback stopping outcome, not a negative empirical result.

Hein remains NOT_ELIGIBLE_UNVERIFIED_DOWNLOAD; only a historical inventory is available. Arthur remains BLOCKED_MISSING_ORIGINAL_CONFIG (david1/david2). Neither is promoted based on absence of a successful Pain/SPIRL result. See ../ACQUISITION_REPORT.md.
