# HGFX v1.0 Independent Frontier Review Report

**Review Date:** 2026-09-16  
**Reviewer:** Independent Frontier AI Reasoning Agent (Antigravity)  
**Target Candidate:** HGFX `1.0.0rc1` (commit `ad8f5cd6fbea3bd1e5ac1cef8b51dbbb9a970a84`)  
**Reference Frozen Oracle:** MATLAB HGF Toolbox v8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`  
**Review Mandate:** [docs/planning/CHAT_WORKFLOW.md](../planning/CHAT_WORKFLOW.md#L92-L102) & [docs/planning/FINAL_REVIEW_CHECKLIST.md](../planning/FINAL_REVIEW_CHECKLIST.md)

---

## 1. Executive Summary

In accordance with the frozen promotion gate for HGFX v1.0, an independent frontier-agent review was conducted against the repository codebase, documentation, test suites, and empirical numerical artifacts. Per the review instructions, the implementation was evaluated under the adversarial assumption that subtle numerical or architectural discrepancies may exist.

### Key Results
- **Automated Test Suite (pytest):** 177 test items collected; **168 passed, 4 skipped (GPU-only on CPU host), 5 failed**.
- **Static Release Readiness (`check_v1_release_readiness.py`):** **PASS**.
- **M20 Candidate Gate (`check_m20_candidate.py --mode finalize`):** **PASS** (`PASS_M20_CANDIDATE`).
- **Quickstart End-to-End Simulation & Fit (`quickstart.py`):** **PASS** (`LME=-22.627078`, `BIC=46.263994`).
- **Code Quality & Type Checking:**
  - `ruff check src/hgfx`: 83 style/import errors (non-breaking).
  - `mypy src/hgfx`: 1 syntax/version error on numpy 2.x stubs under Python 3.11 target config.
- **Reference Freeze & Gate Tests:** 5 failures identified, analyzed to the root cause:
  1. Three 1-to-2 ULP numerical mismatches in D02 regression fixtures caused by MSVC C-runtime vs Linux glibc `expm1`/`log` differences.
  2. Two gate-integrity failures in M18B validation caused by raw-byte SHA-256 verification of git-managed text files containing CRLF line endings on Windows.
  3. Reference freeze verification mismatch for 334 files caused by working-tree CRLF expansion.

### Verdict
**CONDITIONAL RC HOLD:** Release promotion from `1.0.0rc1` to final `1.0.0` is held pending resolution of 2 **HIGH** findings (cross-platform MSVC libm divergence in `matlab_theta_exp_scalar`/`unitsq_sigmoid` and Windows CRLF hash integrity). Once resolved and verified green across platforms, promotion to `1.0.0` is recommended.

---

## 2. Checklist Audit Against `FINAL_REVIEW_CHECKLIST.md`

### 2.1 Source Coverage
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Every frozen MATLAB source file classified** | **PASS** | All 334 frozen MATLAB files are classified into `DONE`, `PLOT_ONLY`, `DEPRECATED`, `NOT_APPLICABLE` via `check_v1_source_classification.py`. |
| **No unexplained `TODO` in critical paths** | **PASS** | Zero occurrences of `TODO` or `FIXME` in `src/hgfx`. |
| **Every model family accounted for** | **PASS** | HGF, eHGF, uHGF, continuous, binary, AR(1) families implemented. |
| **Every observation family accounted for** | **PASS** | Gaussian, binary, softmax, unit-square sigmoid, beta, cumulative Gaussian, and reaction-time models accounted for. |

### 2.2 Mathematical Fidelity
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Equations match reference semantics** | **PASS** | Model equations verified against frozen MATLAB code. |
| **Parameter ordering verified** | **PASS** | Config parameter vectors and indices correspond directly to MATLAB ordering. |
| **Priors verified** | **PASS** | Prior means and variances match reference defaults. |
| **Transforms verified** | **PASS** | Bounded and unbounded parameter transforms match MATLAB reference. |
| **Fixed/free semantics verified** | **PASS** | Fixed parameter masks correctly bypass prior penalty and gradient steps. |
| **Irregular trials verified** | **PASS** | Ignored mask semantics correctly filter irregular trials from likelihood. |
| **Placeholder semantics verified** | **PASS** | NaN placeholders correctly preserved. |

### 2.3 Numerical Validation
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Golden fixtures reproducible** | **PARTIAL** | Golden tests pass; however, 3 D02 fixtures fail on Windows due to MSVC CRT `expm1`/`log` 1-2 ULP divergence (Finding H1). |
| **CPU x64 parity** | **PASS** | JAX `jax_enable_x64=True` enforced across all pipelines. |
| **GPU x64 parity** | **PASS (Archived)** | Validated on CI (2x Tesla T4) with maximum CPU-vs-GPU objective discrepancy of `1.42e-14` against frozen threshold `1e-7`. |
| **First-divergence tooling exists** | **PASS** | Diagnostic tools (`scripts/classify_m18_512_reference.py`, `scripts/compare_fixture.py`) present and operational. |
| **Tolerances scientifically justified** | **PASS** | No arbitrary tolerance inflation detected. |
| **No suspicious tolerance inflation** | **PASS** | Direct bitwise equalities and tight analytical bounds preserved. |

### 2.4 Fitting & Optimization
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Objective-at-fixed-theta parity** | **PASS** | All 5 objective decomposition tests in `tests/unit/test_objective.py` pass. |
| **Compatibility optimizer tested** | **PASS** | Quasi-Newton compatibility optimizer with Ridders finite differences validated. |
| **Fast optimizer scientifically equivalent**| **PASS** | Fast JAX optimizer verified against compatibility results. |
| **Multi-start behavior tested** | **PASS** | Multi-start initialization and optimal trajectory selection verified. |
| **Failure behavior tested** | **PASS** | Non-finite penalties, boundary clipping, and fallback logic verified. |

### 2.5 Model Evidence & Recovery
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Parameter recovery** | **PASS (Documented)** | Paired recovery with MATLAB oracle matches known reference limitations (S7). Historical M18 FAIL preserved. |
| **Model recovery** | **PASS** | 36/36 BIC model selection winners match MATLAB reference. |
| **Edge-case sweeps & stability** | **PASS** | Numerical stability verified under extreme input ranges. |

### 2.6 GPU Engine
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Data stays on device in hot loop** | **PASS** | `lax.scan` utilized for forward trajectories; zero host-device transfers in inner loops. |
| **Batch == repeated single** | **PASS** | Verified in `test_m16_batch_engine.py`. |
| **Compilation & VRAM documented** | **PASS** | Documented in `docs/architecture/ARCHITECTURE.md`. |
| **Multi-GPU tested** | **PASS** | Multi-GPU scaling validated on dual-GPU infrastructure. |

### 2.7 Publication Evidence
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Benchmark protocol frozen** | **PASS** | M19 evidence manifest frozen. |
| **Raw benchmark outputs archived** | **PASS** | Archived under `reference/validation/v1_release/` and `gpu_validation_results/`. |
| **Exact hardware/software recorded** | **PASS** | Full host and device metadata recorded in evidence index. |
| **Script-generated figures/examples** | **PASS** | Public companion and examples execute standalone. |

### 2.8 Licensing & Provenance
| Criterion | Status | Observations |
| :--- | :---: | :--- |
| **Third-party notices complete** | **PASS** | `THIRD_PARTY_NOTICES.md` accurately accounts for HGF Toolbox (GPL v3) and PyHGF attribution. |
| **Copied/adapted code provenance** | **PASS** | Provenance comments and licensing clear. |
| **No license contamination** | **PASS** | Permissive MIT package licensing preserved with appropriate notices. |

---

## 3. Formal Review Findings

### Finding H1 [HIGH]: Platform-Dependent CRT libm Differences Perturb D02 Float64 Oracles
- **File / Path:** [src/hgfx/math/matlab_exp.py:107](../../src/hgfx/math/matlab_exp.py#L107) and [src/hgfx/responses/unitsq_sigmoid.py:68](../../src/hgfx/responses/unitsq_sigmoid.py#L68)
- **Issue:** `matlab_theta_exp_scalar` calls `math.expm1(x) + 1.0`, delegating to the underlying OS C-runtime (`ucrtbase.dll` on Windows vs `glibc` on Linux). On Windows, `math.expm1(2.2790816472336535)` returns `9.767706089455684` instead of `9.767706089455686` (a 2 ULP difference). Similarly, in `unitsq_sigmoid._core`, `np.log` on the denominator deviates by 1 ULP (`3.55e-15`) on Windows. This causes three unit tests to fail:
  - `test_d02_current_theta_plus_matches_matlab_first_sahat_exactly`
  - `test_d02_theta_exp_scalar_matches_current_matlab_oracles_exactly`
  - `test_d02_unitsq_active_log_path_matches_matlab_oracle_exactly`
- **Scientific / Engineering Impact:** HGFX's primary tenet is strict cross-platform CPU float64 reproducibility. The pure Python `matlab_exp_scalar` algorithm (fdlibm-based) returns `9.767706089455686` identically on both Windows and Linux, whereas `matlab_theta_exp_scalar` relies on host CRT.
- **Reproduction Steps:** Run `pytest tests/unit/test_m18_d02_fdlibm_regression.py` on a Windows host.
- **Proposed Fix:**
  1. Replace the `math.expm1` call in `matlab_theta_exp_scalar` with an exact, portable polynomial or use `matlab_exp_scalar` with verified bitwise semantics.
  2. Use `_scalar_log` consistently in `unitsq_sigmoid._core` for the normalization denominator.
- **Release Blocker:** **YES (Blocks final 1.0.0 promotion)**.

---

### Finding H2 [HIGH]: Checksum & Reference Verifications Fail on Windows Due to CRLF Line Endings
- **File / Path:** [src/hgfx/diagnostics/identifiability_validation.py:273-278](../../src/hgfx/diagnostics/identifiability_validation.py#L273-L278) and [scripts/verify_reference_freeze.py:48-50](../../scripts/verify_reference_freeze.py#L48-L50)
- **Issue:** `verify_frozen_m18` reads file contents as raw bytes (`Path.read_bytes()`) and computes SHA-256 over working-tree files. On Windows systems where git checks out files with CRLF line endings (`\r\n`), the SHA-256 differs from the Linux-generated hash (`f2182f3...` vs `98cc45...`), causing:
  - `test_complete_raw_evidence_passes` to FAIL.
  - `test_gate_preserves_frozen_m18_semantics` to FAIL.
  Furthermore, `scripts/verify_reference_freeze.py` hashes working-tree files on disk with `git hash-object`, reporting 334 content mismatches.
- **Scientific / Engineering Impact:** False-positive test failures on Windows developers' machines when the underlying repository and scientific content are completely identical.
- **Reproduction Steps:** On Windows with standard git configuration, run `pytest tests/unit/test_m18b_gate_integrity.py` and `python scripts/verify_reference_freeze.py`.
- **Proposed Fix:**
  1. In `verify_frozen_m18`, normalize line endings (`data.replace(b'\r\n', b'\n')`) prior to SHA-256 calculation, and add a `.gitattributes` rule enforcing LF for these validation files.
  2. In `scripts/verify_reference_freeze.py`, compare against git tree objects (`git ls-tree HEAD`) or normalize CRLF when hashing.
- **Release Blocker:** **YES (Blocks final 1.0.0 promotion)**.

---

### Finding M1 [MEDIUM]: Mypy Incompatibility with NumPy 2.x Stubs Under Python 3.11 Target
- **File / Path:** [pyproject.toml:39](../../pyproject.toml#L39)
- **Issue:** `pyproject.toml` specifies `python_version = "3.11"`. In Python 3.12+ environments where NumPy 2.x is installed, NumPy's stubs use PEP 695 `type` syntax, causing `mypy src/hgfx` to halt with `Type statement is only supported in Python 3.12 and greater`.
- **Scientific / Engineering Impact:** Prevents automated static type checking in standard developer workflows.
- **Reproduction Steps:** Run `mypy src/hgfx` in a Python 3.12 virtualenv.
- **Proposed Fix:** Update `python_version = "3.12"` in `[tool.mypy]` or configure mypy to allow modern stub syntax.
- **Release Blocker:** NO.

---

### Finding L1 [LOW]: Unused Unpacked Variable in Specialized Responses
- **File / Path:** [src/hgfx/responses/specialized.py:260:5](../../src/hgfx/responses/specialized.py#L260)
- **Issue:** Variable `u` is assigned via `u, _ = first_input_column(inputs, n)` but never referenced.
- **Scientific / Engineering Impact:** Minor code cleanliness issue; no numerical impact.
- **Proposed Fix:** Rename to `_u` or discard.
- **Release Blocker:** NO.

---

### Finding L2 [LOW]: Import Ordering and `__all__` Formatting
- **File / Path:** `src/hgfx/` (83 occurrences)
- **Issue:** Ruff flags unsorted imports and unsorted `__all__` lists across several modules.
- **Scientific / Engineering Impact:** Style only.
- **Proposed Fix:** Run `ruff check --fix src/hgfx` (safe fixes).
- **Release Blocker:** NO.

---

### Finding I1 [INFO]: GPU Tests Skipped on CPU Host
- **File / Path:** `tests/cpu_gpu/test_m14_fast_engine.py`, `test_m15_gpu_fitting.py`, `test_m16_batch_engine.py`, `test_m17_multi_gpu.py`
- **Issue:** 4 tests skipped due to no physical NVIDIA GPU on the local development host.
- **Observation:** Expected per `M18_S9_PHYSICAL_GPU_AMENDMENT.md`. Full GPU validation is recorded on CI (2x Tesla T4) with maximum objective difference `1.42e-14`.
- **Release Blocker:** NO.

---

## 4. Required Remediation for Final 1.0.0 Promotion

Per [docs/planning/CHAT_WORKFLOW.md](../planning/CHAT_WORKFLOW.md#L100) and [docs/planning/FINAL_REVIEW_CHECKLIST.md](../planning/FINAL_REVIEW_CHECKLIST.md), **all Critical and High findings must be resolved and full validation rerun before promoting `1.0.0rc1` to `1.0.0`**:

1. **Resolve Finding H1:** Normalize `matlab_theta_exp_scalar` and `unitsq_sigmoid._core` so that D02 float64 oracles evaluate identically across Windows and Linux.
2. **Resolve Finding H2:** Implement CRLF normalization in `verify_frozen_m18` and `scripts/verify_reference_freeze.py` (and add `.gitattributes` enforcement) so that Windows checkouts pass 100% of gate tests.
3. **Rerun Full Test Suite:** Verify that all 177 tests pass (173 passed, 4 skipped for GPU) with 0 failures on CPU.
4. **Promotion:** Update package version in `pyproject.toml` and `CITATION.cff` from `1.0.0rc1` to `1.0.0`, tag release, and publish.
