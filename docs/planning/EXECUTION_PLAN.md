---
title: "برنامه اجرایی دقیق HGF Python/JAX/GPU"
date: 2026-09-11
status: "Execution Plan"
reference_toolbox: "HGF Toolbox v8.2.0"
target: "Scientific-parity Python/JAX toolbox with GPU batch fitting"
language: "fa"
---

# برنامه اجرایی دقیق HGF Python/JAX/GPU

## ترتیب فعال اجرا — بازنگری 2026-09-11

[برنامه اصلاح با محور تطابق MATLAB](MATLAB_PARITY_RECOVERY_PLAN.md) مرجع ترتیب فعلی R0 تا R6 است. ابتدا شواهد M18B، سپس بازتولید زوجی شکست 512 تریالی و مقایسه استنباط روی داده‌های شکست M18؛ پس از آن آزمایش مستقل بازیابی و بازتأیید GPU. M18 تاریخی FAIL باقی می‌ماند. شماره‌گذاری milestoneها در `MILESTONES.md` معتبر است؛ شماره Phase/Gate در بخش‌های طراحی قدیمی این سند به معنی وضعیت فعلی نیست.

## 1) هدف نهایی

خروجی پروژه باید یک toolbox مستقل Python باشد که:

```text
MATLAB HGF Toolbox
       │
       │ reference only
       ▼
 Golden Numerical Corpus
       │
       ▼
 Python / JAX HGF
       │
 ┌─────┴───────────┐
 │                 │
CPU x64         GPU x64
 │                 │
compat mode      fast batch mode
```

و در استفاده روزانه:

```text
MATLAB runtime dependency = 0
```

باشد.

---

# 2) اصول غیرقابل مذاکره

1. **نسخه مرجع freeze می‌شود.**
2. **هر تابع ریاضی قبل از merge تست MATLAB دارد.**
3. **float64 حالت پیش‌فرض علمی است.**
4. **GPU optimization loop کاملاً on-device است.**
5. **Compatibility mode و Fast mode جدا هستند.**
6. **AI حق اعلام صحت علمی بدون test ندارد.**
7. **هیچ فایل MATLAB بدون classification باقی نمی‌ماند.**
8. **هیچ optimization performance قبل از parity core انجام نمی‌شود.**
9. **custom model API از ابتدا جزو design است.**
10. **Source drift کنترل‌شده است؛ main branch HGF در وسط migration دنبال نمی‌شود.**

---

# 3) معماری Repository

```text
hgf-python/
│
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
│
├── src/
│   └── hgf/
│       ├── __init__.py
│       │
│       ├── compat/
│       │   ├── fit.py
│       │   ├── sim.py
│       │   ├── sample.py
│       │   ├── result.py
│       │   └── matlab_names.py
│       │
│       ├── core/
│       │   ├── model.py
│       │   ├── state.py
│       │   ├── scan.py
│       │   ├── parameters.py
│       │   ├── transforms.py
│       │   ├── priors.py
│       │   └── placeholders.py
│       │
│       ├── updates/
│       │   ├── prediction.py
│       │   ├── precision.py
│       │   ├── binary.py
│       │   ├── continuous.py
│       │   ├── volatility.py
│       │   └── volatility_pe.py
│       │
│       ├── models/
│       │   ├── hgf.py
│       │   ├── hgf_binary.py
│       │   ├── hgf_pu.py
│       │   ├── hgf_pu_tbt.py
│       │   ├── ar1.py
│       │   ├── mab.py
│       │   ├── categorical.py
│       │   ├── jget.py
│       │   ├── rw.py
│       │   ├── pearce_hall.py
│       │   ├── kalman.py
│       │   ├── hmm.py
│       │   └── bayes_optimal/
│       │
│       ├── responses/
│       │   ├── base.py
│       │   ├── unitsq_sigmoid.py
│       │   ├── softmax.py
│       │   ├── gaussian.py
│       │   ├── beta.py
│       │   ├── cdf_gaussian.py
│       │   ├── condhalluc.py
│       │   └── logrt.py
│       │
│       ├── optim/
│       │   ├── interface.py
│       │   ├── compat_quasinewton.py
│       │   ├── ridders.py
│       │   ├── lbfgs.py
│       │   └── batch.py
│       │
│       ├── math/
│       │   ├── lambert_w.py
│       │   ├── psd.py
│       │   └── covariance.py
│       │
│       ├── diagnostics/
│       │   ├── residuals.py
│       │   ├── recovery.py
│       │   └── convergence.py
│       │
│       ├── plotting/
│       │
│       └── gpu/
│           ├── batching.py
│           ├── compile_cache.py
│           ├── scheduler.py
│           └── devices.py
│
├── reference/
│   ├── HGF_VERSION
│   ├── HGF_COMMIT
│   ├── matlab_manifest.tsv
│   ├── source_checksums/
│   └── golden/
│
├── tests/
│   ├── unit/
│   ├── golden/
│   ├── integration/
│   ├── recovery/
│   ├── cpu_gpu/
│   └── performance/
│
├── tools/
│   ├── build_matlab_manifest.py
│   ├── import_matlab_fixture.py
│   └── compare_fixture.py
│
├── benchmarks/
│
└── docs/
```

---

# 4) Environment Baseline

## Development

پیشنهاد:

```text
OS: Linux
Python: pinned supported version
Package management: uv + pyproject.toml
Core: JAX
Reference: frozen MATLAB HGF 8.2.0
Optional comparison/interoperability: PyHGF (not a core dependency)
Tests: pytest
Lint: ruff
Type checking: mypy/pyright
Property tests: hypothesis
Docs: MkDocs or Sphinx
```

## GPU

مطمئن‌ترین target اولیه:

```text
Linux + NVIDIA CUDA + JAX official GPU wheel
```

در ابتدای runtime:

```python
import jax
jax.config.update("jax_enable_x64", True)
```

---

# 5) Git Branching / Governance

Branches:

```text
main
develop
migration/<matrix-id>
perf/<feature>
docs/<feature>
```

هر Issue باید یک `Matrix ID` داشته باشد.

مثال:

```text
B08 - Port hgf_volatility_update
O17 - Port unitsq_sgm family
C01 - fitModel compatibility
```

هر PR باید شامل این موارد باشد:

```text
[ ] Matrix ID
[ ] MATLAB source file(s)
[ ] equation/semantic summary
[ ] golden fixture IDs
[ ] implementation
[ ] CPU x64 result
[ ] GPU x64 result if relevant
[ ] numerical diff report
[ ] provenance/license note
```

---

# 6) AI Agent Workflow

مدل AI باید repository-level agent باشد، نه فقط chat copy/paste.

حداقل سطح پیشنهادی برای کار اصلی:

```text
GPT-5.6 Sol
Reasoning: High / Extra High
```

برای بخش‌های بسیار حساس:

```text
strongest available frontier reasoning model
+
independent second review
```

## چهار نقش AI

### Agent A — Source Analyst

وظیفه:

```text
MATLAB source
→ equations
→ branches
→ parameter semantics
→ edge cases
→ dependency map
```

### Agent B — Implementer

وظیفه:

```text
spec + golden tests
→ JAX implementation
→ unit tests
```

### Agent C — Numerical Reviewer

وظیفه:

```text
independent MATLAB-vs-JAX review
→ sign/index/transform/order checks
→ numerical-stability checks
```

### Agent D — Performance Engineer

فقط بعد از parity:

```text
jit
scan
vmap
batching
memory
compile cache
GPU optimization
```

## قانون

Agent B نباید تنها reviewer کد خودش باشد.

---

# 7) Prompt Template برای هر Migration Item

برای هر تابع، agent باید با قالب ثابت کار کند:

```text
1. فایل MATLAB مرجع را کامل بخوان.
2. همه ورودی‌ها/خروجی‌ها را استخراج کن.
3. معادلات را به notation ریاضی بنویس.
4. همه branchها و edge caseها را لیست کن.
5. parameter ordering و transforms را ثبت کن.
6. fixtureهای MATLAB مرتبط را بررسی کن.
7. ابتدا test بنویس.
8. سپس JAX implementation بنویس.
9. testهای CPU x64 را اجرا کن.
10. diff را trial-by-trial گزارش کن.
11. اگر تابع GPU-critical است، GPU x64 test اجرا کن.
12. هیچ mismatch را با افزایش کورکورانه tolerance پنهان نکن.
13. علت mismatch را مشخص کن.
```

---

# 8) Phase 0 — Freeze & Inventory

## کارها

- checkout دقیق `HGF Toolbox v8.2.0`;
- ثبت exact commit SHA؛
- checkout و pin کردن PyHGF commit/version؛
- استخراج recursive `.m` manifest؛
- SHA-256 برای همه فایل‌ها؛
- license snapshot؛
- استخراج dependency graph اولیه؛
- تولید migration table ماشینی.

## خروجی

```text
reference/HGF_VERSION
reference/HGF_COMMIT
reference/PYHGF_VERSION
reference/PYHGF_COMMIT
reference/matlab_manifest.tsv
reference/matlab_checksums.tsv
```

## Gate 0

- [ ] هیچ فایل `.m` بدون manifest نیست.
- [ ] commitها immutable ثبت شده‌اند.
- [ ] repo status clean است.
- [ ] license provenance ثبت شده است.

تا Gate 0 پاس نشود، implementation شروع نشود.

---

# 9) Phase 1 — Golden Reference Harness

این مهم‌ترین فاز پروژه است.

## MATLAB reference runner

یک wrapper بساز:

```text
reference/matlab/export_fixture.m
```

که برای هر case:

```text
input
config
params
traj
infStates
likelihood
fit metrics
```

را export کند.

## Fixture format

پیشنهاد:

```text
case_0001/
    metadata.json
    input.npz
    config.json
    expected.npz
```

MATLAB می‌تواند خروجی اولیه را `.mat`/JSON بدهد و یک converter یک‌بار آن را به NPZ منتقل کند.

بعد از تولید Golden Corpus، اجرای روزانه تست‌ها MATLAB نمی‌خواهد.

## Minimum fixture families

- binary HGF؛
- continuous HGF؛
- eHGF؛
- uHGF؛
- fixed/free parameter variants؛
- irregular trials؛
- missing response؛
- non-unit time axis؛
- extreme stable parameters؛
- simulation؛
- fitted results.

## Gate 1

یک fixture از ابتدا تا انتها بتواند:

```text
MATLAB export
→ Python load
→ numerical diff report
```

را reproducibly انجام دهد.

---

# 10) Phase 2 — Data Schema / Parameters / Transforms

قبل از مدل:

- `ParameterSpec`
- `ModelConfig`
- `Transform`
- prior semantics
- free/fixed indices
- MATLAB parameter ordering
- placeholder resolver
- irregular-trial mask
- time-axis representation
- result schema.

## Gate 2

برای چند config رسمی:

```text
MATLAB config
→ flattened params
→ Python config
→ flattened params
```

باید ordering یکسان باشد.

---

# 11) Phase 3 — Scalar Math & Utilities

اول:

```text
logit
sigmoid
boltzmann
Lambert W0
nearest PSD
Cov2Corr
```

بعد compatibility derivatives:

```text
Ridders diff
Ridders gradient
Ridders Hessian
```

## چرا قبل از HGF؟

چون mismatch در این utilityها بعداً در صدها trial تکثیر می‌شود.

## Gate 3

تمام utility fixtures CPU x64 پاس شوند.

---

# 12) Phase 4 — Shared HGF Building Blocks

ترتیب پیشنهادی:

```text
time_axis
prediction
pihat
pihat_last
binary_level1
binary_level2
continuous_level1
volatility_pe
volatility_update
trajectory_checks
```

هر تابع:

```text
single step
→ short scan
→ long scan
```

تست شود.

## Gate 4A — Standard HGF

```text
HGF forward trajectory parity
```

## Gate 4B — eHGF

```text
eHGF trajectory parity
```

## Gate 4C — uHGF

به‌طور مستقل:

```text
Lambert W
dual approximations
variational energy
mixture moments
```

پاس شوند.

---

# 13) Phase 5 — PyHGF Compatibility Decision Gate

حالا به‌طور عینی تصمیم می‌گیریم.

## Test

standard/eHGF/uHGF را با:

```text
MATLAB
PyHGF configured for compatibility
our thin adapter
```

مقایسه کن.

## Decision A

اگر parity خوب و patchها کم هستند:

```text
PyHGF = pinned dependency
our toolbox = compatibility + extensions
```

## Decision B

اگر update ordering/defaults/clipping/core shape دائماً mismatch می‌سازند:

```text
shallow fork PyHGF
+
compat patches
+
upstream tracking policy
```

> این تصمیم نباید قبل از Golden Tests گرفته شود.

---

# 14) Phase 6 — Unified Forward Models

ترتیب:

1. continuous HGF؛
2. binary HGF؛
3. binary PU؛
4. binary PU TBT؛
5. AR1 binary؛
6. AR1 binary MAB؛
7. JGET.

برای هر مدل:

```text
default config
custom config
2–5 levels where valid
short/long series
irregular trials
extreme stable parameters
```

## Gate 6

تمام unified HGF family trajectories پاس شوند.

---

# 15) Phase 7 — Observation Models

اول response modelهای پرتکرار:

```text
unitsq_sgm
softmax_binary
softmax
gaussian
```

سپس:

```text
mu3 variants
2beta
beta_obs
cdfgaussian
logRT
world variants
condhalluc families
```

برای هر observation model پنج جزء جدا تست شود:

```text
config
transform
name metadata
log-likelihood
simulation
```

## Gate 7

همه observation familyهای P0/P1:

```text
trial log-likelihood parity
+
total log-likelihood parity
```

داشته باشند.

---

# 16) Phase 8 — Objective / Priors / fitModel Semantics

اکنون:

$$
\log p(y,u,\theta)
=
\log p(y|u,\theta)
+
\log p(\theta)
$$

را دقیقاً مطابق MATLAB assemble کن.

موارد مهم:

- irregular trials؛
- response streams؛
- fixed parameters؛
- NaN/fixed exclusions؛
- perceptual priors؛
- observation priors؛
- transformed/native spaces.

## Test

برای یک **پارامتر ثابت داده‌شده**:

```text
MATLAB objective(theta)
vs
Python objective(theta)
```

قبل از optimizer باید تقریباً یکسان باشد.

## Gate 8

Objective parity برای تمام P0/P1 model-response combinations.

---

# 17) Phase 9 — Compatibility Optimizer

دو optimizer track جدا:

## Track A — `compat`

port رفتار quasi-Newton MATLAB:

- initialization؛
- free parameter set؛
- random starts؛
- numerical gradients where used؛
- termination criteria؛
- invalid objective handling؛
- best-run selection.

## Track B — `fast`

فعلاً فقط interface تعریف شود؛ optimization واقعی GPU در فاز بعد.

## Gate 9

برای fixtureهای well-behaved:

```text
final objective
MAP parameters
convergence state
```

قابل مقایسه باشد.

### نکته مهم

اگر دو optimizer به دو parameter vector کمی متفاوت ولی objective تقریباً یکسان برسند:

```text
parameter distance
+
objective distance
+
trajectory distance
```

هر سه بررسی شوند؛ صرف equality پارامتر کافی نیست.

---

# 18) Phase 10 — Hessian / Covariance / LME

Compatibility:

```text
Ridders Hessian
→ nearest PSD if needed
→ Sigma
→ Corr
→ LME
```

Fast:

```text
jax.hessian
```

به‌عنوان مسیر مستقل.

## تست‌ها

- Hessian matrix elementwise؛
- eigenvalue behavior؛
- PSD repair؛
- covariance؛
- correlation؛
- log determinant؛
- LME؛
- accuracy؛
- complexity؛
- AIC/BIC.

## Gate 10

Model comparison outputs در fixtures استاندارد پاس شوند.

---

# 19) Phase 11 — simModel / sampleModel / RNG

RNG باید explicit باشد:

```python
key = jax.random.PRNGKey(seed)
```

اما compatibility باید semantics MATLAB seed را از طریق fixture بررسی کند.

هدف دو نوع test است:

### Exact deterministic test

جایی که الگوریتم RNG/transform اجازه می‌دهد.

### Distributional test

وقتی stream RNG دقیقاً یکی نیست:

- mean؛
- variance؛
- quantiles؛
- response frequencies؛
- calibration.

## Gate 11

Simulation و sampling برای P0/P1 مدل‌ها scientifically equivalent باشند.

---

# 20) Phase 12 — Specialized / Legacy Perceptual Models

بعد از core stability:

```text
categorical
RW
RW dual
Pearce-Hall
Sutton K1
Kalman
HMM
HHMM
WhatWorld
WhichWorld
Bayes-optimal
other MAB/AR variants
```

برای هر کدام همان pipeline:

```text
source analysis
→ golden forward fixture
→ implementation
→ response compatibility
→ fitting
→ simulation if applicable
```

## Gate 12

100% model families موجود در frozen manifest status `DONE` یا `REFERENCE_ONLY with explicit reason` داشته باشند.

---

# 21) Phase 13 — Compatibility Output API

برای آسان شدن مهاجرت اسکریپت‌های قدیمی:

```python
est.p_prc
est.p_obs
est.traj
est.optim
est.yhat
est.res
est.irr
```

پشتیبانی شود.

همچنین export:

```python
est.to_dict(matlab_style=True)
```

برای downstream code.

## Gate 13

چند analysis script واقعی بدون تغییر عمده بتوانند خروجی Python را مصرف کنند.

---

# 22) Phase 14 — GPU Fast Engine

فقط حالا performance optimization شروع شود.

## 14.1 Trial recursion

```python
jax.lax.scan
```

## 14.2 Subject batch

```python
jax.vmap
```

## 14.3 Restart batch

```python
jax.vmap
```

## 14.4 JIT

```python
jax.jit
```

روی model/objective/optimizer step.

## 14.5 Keep on device

روی GPU بماند:

```text
inputs
responses
params
optimizer state
objective
gradients
trajectory intermediates where needed
```

## 14.6 Compilation cache

key:

```text
model topology
levels
observation model
dtype
shape bucket
static options
```

---

# 23) Phase 15 — GPU Optimizer

Fast mode باید optimizer abstraction داشته باشد:

```python
class Optimizer:
    init(...)
    step(...)
    converged(...)
```

candidateها:

```text
L-BFGS
Adam
hybrid multi-start
```

اما انتخاب نهایی باید benchmark شود.

## معیار

نه «چند iteration کمتر»، بلکه:

```text
same/better final objective
same trajectory
acceptable parameter recovery
higher throughput
```

---

# 24) Phase 16 — Batch Scheduler

Work unit:

```text
subject × model × initialization
```

Scheduler:

```text
jobs
  ↓
group by compatible signature
  ↓
pad/bucket trials
  ↓
batch
  ↓
GPU
```

API:

```python
result = fit_batch(
    models=models,
    datasets=datasets,
    restarts=10,
    batch_size=512,
    device="gpu",
)
```

## Gate 16

برای batch:

```text
batch result
≈
single-fit result
```

برای هر member.

---

# 25) Phase 17 — Multi-GPU

فقط وقتی single-GPU:

```text
correct
stable
profiled
```

است.

Strategy:

```text
GPU 0 → batch A
GPU 1 → batch B
GPU 2 → batch C
...
```

اول data-parallel مستقل؛ نه model-parallel پیچیده.

---

# 26) Phase 18 — Performance Benchmarking

Benchmark باید حداقل این ابعاد را داشته باشد:

```text
trials: 100 / 500 / 1000+
subjects: 1 / 16 / 128 / 512+
models: 1 / multiple
restarts: 1 / 5 / 10
levels: 2 / 3 / 4+
```

## Baselines

```text
MATLAB single
MATLAB parallel if available
Python/JAX CPU
Python/JAX GPU
```

## Metrics

```text
wall time
fits/sec
trials/sec
peak RAM
peak VRAM
compile time
steady-state time
optimizer iterations
objective
numerical error
```

compile time جدا از steady-state گزارش شود.

---

# 27) Phase 19 — Parameter Recovery

برای grid مدل‌ها:

```text
theta_true
  ↓
simulate
  ↓
fit
  ↓
theta_hat
```

Metrics:

```text
bias
RMSE
correlation
coverage where applicable
failure rate
```

به‌خصوص برای custom models آینده این test framework باید reusable باشد.

---

# 28) Phase 20 — Model Recovery

```text
simulate model A
simulate model B
simulate model C
       ↓
fit all candidate models
       ↓
compare LME/AIC/BIC
       ↓
confusion matrix
```

این یکی از مهم‌ترین sanity checkها برای scientific toolbox است.

---

# 29) Phase 21 — Diagnostics / Plotting

پس از computational parity:

- trajectory plots؛
- posterior/fit plots؛
- correlation؛
- residual diagnostics؛
- HMM/KF display equivalents؛
- publication-friendly figures.

Plotting نباید core imports را سنگین کند.

---

# 30) Phase 22 — Documentation

Docs باید چهار مسیر داشته باشد:

## A. MATLAB user migration

```text
tapas_fitModel
→ hgf.fit_model
```

## B. Native Python user

```text
ModelConfig
fit
simulate
compare
```

## C. GPU researcher

```text
fit_batch
device
dtype
batching
profiling
```

## D. Custom model developer

```text
new update
new coupling
new response
golden/custom tests
```

---

# 31) Phase 23 — Release Gates

## Alpha

- standard binary HGF؛
- continuous HGF؛
- basic observations؛
- forward parity؛
- CPU x64.

## Beta

- eHGF/uHGF؛
- fitModel parity؛
- LME/Hessian؛
- simulation؛
- GPU batch؛
- main observations.

## Release Candidate

- all frozen model families classified/ported؛
- all observation families؛
- recovery suites؛
- docs؛
- benchmarks؛
- no MATLAB runtime dependency.

## Stable v1.0

Definition of Done سند Migration Matrix کامل پاس شده باشد.

---

# 32) CI Pipeline

## هر commit

```text
lint
typecheck
unit tests
golden fast subset
```

## هر PR

```text
all unit tests
relevant golden family
CPU x64
property tests
```

## nightly / scheduled

```text
full golden corpus
all model-response combinations
CPU/GPU parity
parameter recovery subset
performance regression
```

## release

```text
full golden
full recovery
model recovery
GPU benchmark
package install test
docs build
license/provenance audit
```

---

# 33) Test Failure Policy

ممنوع:

```text
test failed
→ tolerance *= 100
→ merge
```

مجاز:

```text
test failed
→ locate first divergent trial
→ locate first divergent variable
→ identify equation/branch
→ compare MATLAB intermediate
→ fix
```

ابزار diff باید گزارش دهد:

```text
first failing trial
first failing level
field
MATLAB value
JAX value
absolute diff
relative diff
upstream dependencies
```

---

# 34) Numerical Acceptance Policy

سه سطح:

## Exact-like

برای:

```text
config
parameter ordering
masks
indices
metadata
shapes
```

باید دقیقاً برابر باشند.

## Floating numerical

برای:

```text
trajectory
likelihood
building blocks
```

tolerance calibrated.

## Optimization equivalence

برای fit:

```text
objective equivalence
trajectory equivalence
parameter plausibility
```

چون مسیر optimizer الزاماً یکسان نیست.

---

# 35) Risk Register

| Risk | اثر | کنترل |
|---|---|---|
| PyHGF semantics با TAPAS دقیقاً یکی نباشد | Critical | Golden gate قبل از reuse |
| eHGF/uHGF update mismatch | Critical | block-level fixtures |
| parameter ordering اشتباه | Critical | schema round-trip tests |
| transform/prior mismatch | Critical | objective-at-fixed-theta tests |
| recursive error accumulation | Critical | first-divergence trial report |
| optimizer به minimum متفاوت برسد | High | objective + trajectory acceptance |
| Hessian/LME تفاوت کند | Critical | compat Ridders path |
| GPU nondeterminism | Medium/High | x64 + deterministic config + tolerances |
| FP64 روی GPU کند باشد | Performance | benchmark target hardware |
| JIT recompilation زیاد | Performance | signature cache + bucketing |
| trial lengths متفاوت | Performance | padding/masks/buckets |
| source HGF تغییر کند | High | frozen SHA |
| MATLAB بعداً در دسترس نباشد | High | golden corpus را زود freeze کن |
| AI hallucination | Critical | no merge without golden test |
| custom model API بد طراحی شود | Long-term | plugin protocol from early phase |
| license/provenance گم شود | Legal | THIRD_PARTY_NOTICES + source map |

---

# 36) Resource / Role Plan

حداقل نقش‌ها، حتی اگر توسط یک نفر + AI انجام شوند:

```text
Scientific owner
Numerical implementation owner
Test/validation owner
Performance/GPU owner
```

AI می‌تواند بخش زیادی از implementation را بگیرد، ولی sign-off علمی باید به test و reviewer انسانی/مستقل متکی باشد.

---

# 37) Prioritization

## P0 — اول

```text
freeze
manifest
golden harness
parameter/config schema
transforms
core math
building blocks
standard HGF
eHGF
uHGF
unitsq_sgm
softmax_binary
objective
fitModel
compat optimizer
Hessian/LME
```

## P1 — بعد

```text
PU
PU-TBT
AR1
MAB
JGET
categorical
main response models
sim/sample
GPU batch
```

## P2

```text
RW
PH
Sutton
KF
HMM/HHMM
WhatWorld/WhichWorld
Bayes-optimal
condhalluc
specialized diagnostics
```

## P3

```text
plot parity
UI polish
legacy aliases
extra convenience
```

---

# 38) ترتیب تاریخی طراحی (نه شماره milestoneهای جاری)

شماره‌های G زیر سابقه طراحی‌اند. در کار فعلی M18 = Scientific Recovery، M19 = Methods Paper Dataset Frozen و M20 = v1.0 Candidate؛ ترتیب اصلاح R0–R6 در سند جدید اجرا می‌شود.

```text
G0 Freeze
 ↓
G1 Golden Harness
 ↓
G2 Config/Parameter parity
 ↓
G3 Math utilities
 ↓
G4 HGF/eHGF/uHGF forward parity
 ↓
G5 PyHGF reuse/fork decision
 ↓
G6 Unified model family parity
 ↓
G7 Observation parity
 ↓
G8 Objective parity
 ↓
G9 fit optimizer parity
 ↓
G10 Hessian/LME parity
 ↓
G11 Simulation parity
 ↓
G12 Specialized models
 ↓
G13 API compatibility
 ↓
G14 GPU fast engine
 ↓
G15 GPU optimizer
 ↓
G16 Batch scheduler
 ↓
G17 Multi-GPU
 ↓
G18 Benchmark
 ↓
G19 Parameter recovery
 ↓
G20 Model recovery
 ↓
G21 Docs/Release
```

---

# 39) چه چیزی را نباید در ابتدای پروژه انجام داد؟

### اشتباه 1

```text
کل repo MATLAB را به AI بده
و بگو translate to Python
```

### اشتباه 2

از روز اول performance optimize کردن.

### اشتباه 3

فقط fitted parameters را مقایسه کردن.

### اشتباه 4

فرض اینکه چون PyHGF اسم HGF دارد، با TAPAS bit-for-bit یکسان است.

### اشتباه 5

استفاده پیش‌فرض از float32 برای سرعت.

### اشتباه 6

حذف MATLAB قبل از ساخت Golden Corpus.

---

# 40) Cutover Plan

MATLAB طی migration سه نقش دارد:

## Stage A

```text
MATLAB = active reference + production
Python = development
```

## Stage B

```text
MATLAB = reference
Python = production candidate
```

## Stage C

```text
MATLAB = frozen historical oracle only
Python = primary runtime
```

## Stage D

```text
golden fixtures sufficient
MATLAB installation no longer required for daily work/CI
```

از آن مرحله:

$$
\boxed{\text{Runtime MATLAB dependency}=0}
$$

---

# 41) Maintenance بعد از v1.0

اگر HGF Toolbox upstream نسخه جدید داد:

```text
old frozen version
      ↓
upstream diff
      ↓
new/changed MATLAB files only
      ↓
new fixtures
      ↓
migration PRs
      ↓
compat version bump
```

مثلاً:

```text
hgf-python 1.x
compatible_with = HGF 8.2.0
```

بعد:

```text
hgf-python 2.x
compatible_with = HGF 8.3/9.x
```

بدون اینکه source of truth مبهم شود.

---

# 42) Success Metrics

## Scientific

- forward trajectory parity؛
- log-likelihood parity؛
- MAP objective parity؛
- LME/AIC/BIC compatibility؛
- parameter recovery؛
- model recovery.

## Engineering

- 100% source manifest classification؛
- reproducible install؛
- deterministic test fixtures؛
- CPU/GPU same public API؛
- no MATLAB runtime dependency.

## Performance

- batch throughput افزایش معنادار؛
- CPU↔GPU transfer داخل optimizer loop تقریباً صفر؛
- compile cache مؤثر؛
- memory failure rate کنترل‌شده.

---

# 43) Definition of Done نهایی

پروژه فقط وقتی «تمام» است که:

```text
[PASS] source inventory
[PASS] golden corpus
[PASS] standard HGF
[PASS] eHGF
[PASS] uHGF
[PASS] all targeted perceptual models
[PASS] all observation families
[PASS] config/transforms
[PASS] fitModel
[PASS] simModel
[PASS] sampleModel
[PASS] quasi-Newton compatibility
[PASS] Hessian/Sigma/Corr
[PASS] LME/AIC/BIC
[PASS] CPU x64
[PASS] GPU x64
[PASS] batch/single equivalence
[PASS] parameter recovery
[PASS] model recovery
[PASS] custom model API
[PASS] documentation
[PASS] license/provenance
[PASS] runtime MATLAB dependency = 0
```

---

# 44) پیشنهاد شروع عملی

اولین چهار Issue:

```text
HGF-000 Freeze v8.2.0 + exact source manifest

HGF-001 Build MATLAB Golden Fixture Exporter

HGF-002 Implement Python fixture schema + diff reporter

HGF-003 Port one vertical slice:
        hgf_binary
        +
        unitsq_sgm
        +
        objective at fixed parameters
```

بعد از `HGF-003` یک decision checkpoint بگذار:

```text
Does PyHGF give us sufficient core parity with thin adapters?
```

اگر بله، reuse را گسترش بده.

اگر نه، fork/port core را شروع کن.

این checkpoint جلوی ماه‌ها بازنویسی غیرضروری را می‌گیرد.

---

# 45) Vertical Slice پیشنهادی

اولین end-to-end slice:

```text
binary input
    ↓
3-level HGF
    ↓
unitsq_sgm
    ↓
trial log-likelihood
    ↓
total objective
    ↓
MAP fit
    ↓
Hessian
    ↓
LME
```

باید این خروجی‌ها را MATLAB-vs-Python مقایسه کند:

```text
mu
sa
muhat
sahat
prediction errors
trial ll
total ll
prior
negLogJoint
MAP params
H
Sigma
Corr
LME
AIC
BIC
```

اگر این vertical slice درست شود، architecture پروژه عملاً اثبات شده است.

---

# 46) منابع

- HGF Toolbox  
  https://github.com/ComputationalPsychiatry/hgf-toolbox

- HGF architecture  
  https://github.com/ComputationalPsychiatry/hgf-toolbox/blob/master/ARCHITECTURE.md

- PyHGF  
  https://github.com/ComputationalPsychiatry/pyhgf

- PyHGF documentation  
  https://computationalpsychiatry.github.io/pyhgf/

- JAX installation  
  https://docs.jax.dev/en/latest/installation.html

- JAX x64/default dtypes  
  https://docs.jax.dev/en/latest/default_dtypes.html

---

# 47) سند مرتبط

ماتریکس component-by-component:

```text
01_HGF_Python_GPU_Migration_Matrix.md
```
