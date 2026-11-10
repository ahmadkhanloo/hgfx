# REV-2.4 eHGF-019 — maintenance-only numerical compatibility fix plan (2026-11-10)

**Version isolation and gate:** original peer-reviewed **released HGFX v1.0.0** at commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` is **immutable**. The current `compstat-revision` development branch is `1.1.0b1`, a separate maintenance implementation. Do not rewrite original 600-grid evidence or declare eHGF/v1.0.0 scientific PASS.

## Source-rooted numerical defect candidate

The original single-vector authentic MATLAB/HGFX eHGF-019 trace is preserved at [run 42797497943](https://github.com/ahmadkhanloo/hgfx/actions/runs/42797497943), artifact `13754932663`, and source-only postprocessor [42798716279](https://github.com/ahmadkhanloo/hgfx/actions/runs/42798716279), artifact `13755237519`. [Detailed report](../../docs/research/REV24_EHGF019_ORIGINAL_TRACE_RESULT_2026-11-10.md) pinpoints the first finite-status difference at zero-based trial 8, level 3 posterior `sa`: MATLAB `8.209456713045242`, HGFX `NaN`, before likelihood difference at trial 11.

Source frozen MATLAB `building_blocks/hgf_volatility_update.m` eHGF update computes `pihat + max(0, correction)`; frozen HGFX `src/hgfx/updates/volatility.py` computes `pihat + np.maximum(0.0,correction)`. MATLAB default `max(0,NaN)=0` (MathWorks documentation), NumPy `np.maximum(0,NaN)=NaN`. The archived updated top-level mean `1009.0446083588881` and `omega2=1.391502762318833` imply an `exp(1010.4361111212067)` overflow, which makes `vv*0` a NaN correction; MATLAB then retains its finite predicted precision.

## Exactly scoped maintenance implementation and testing

1. **Before modifying code**, add a **golden original-scalar failure-based unit test** in `tests/unit/test_ehgf_max_nan_compat.py`: use the 12 frozen top-level scalar inputs from the original case/trial-8 trace (not the complete 600-case grid or a new model fit) and assert that the eHGF posterior precision equals its finite predicted precision under a NaN correction, matching the actual original MATLAB output. Include a companion test of finite correction behavior and the unaffected HGF/uHGF model branches.
2. Run that golden test against the **currently unmodified 1.1.0b1 development source** in a source-only CI workflow; preserve the **expected failure** and exact run/commit. This is not a failure of the original Panel G run, but a maintenance regression baseline.
3. Change exactly **one** numerical operation on the development branch, `np.maximum` → `np.fmax` for the **eHGF correction only**, adding an explanatory MATLAB-compatibility comment. Do not alter any priors, transforms, data/seed, optimization/gradient code, numeric gates, v1.0.0 release tag, or shared HGF/uHGF branch.
4. Re-run the golden test, existing eHGF unit/forward tests and relevant regression contracts. Record PASS/FAIL honestly. No MATLAB or v1.0.0 Panel G/E scientific re-execution is authorized under the consumed original protocol; CPU synthetic unit PASS would mean **IMPLEMENTED BUT NOT SCIENTIFICALLY VALIDATED**.
5. Submit for independent/human scientific review alongside the immutable original failure and trace. Any proposed formal cross-language **maintenance** scientific validation requires a separately predeclared protocol/data/acceptance gate and explicit author decision. No historical milestone or original manuscript claim is reclassified.

The original numerical source semantics are considered an implementation-compatibility candidate with strong causal evidence; the uninstrumented original `vv/ww/rr/correction` arithmetic is a source-derived reconstruction rather than directly logged intermediate on both sides. Until independent review, preserve `LIKELY_NUMERICAL_MAX_NAN_SEMANTICS_MISMATCH` as the mechanism's evidentiary label.

**Global scientific status:** REV-2.4 `NOT_GLOBAL_PASS`; D2/D3 `BLOCKED`, independent review remains limited AI without human countersignature. Original eHGF-019 one-sided-invalid is preserved.
