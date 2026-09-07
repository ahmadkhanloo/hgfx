---
title: "HGF Toolbox → Python/JAX/GPU Migration Matrix"
date: 2026-09-07
status: "Baseline / Migration Specification"
reference_toolbox: "HGF Toolbox v8.2.0"
target_runtime: "Python + JAX, CPU/GPU, float64-first"
language: "fa"
---

# ماتریکس مهاجرت HGF Toolbox به Python/JAX/GPU

## 1) هدف سند

هدف این سند تعریف یک **ماتریکس مهاجرت علمی و مهندسی** برای تبدیل HGF Toolbox مرجع MATLAB به یک پیاده‌سازی Python/JAX است که:

1. از نظر علمی و عددی با HGF Toolbox مرجع سازگار باشد؛
2. وابستگی runtime به MATLAB نداشته باشد؛
3. روی CPU و GPU از یک کد محاسباتی مشترک استفاده کند؛
4. `float64` را حالت پیش‌فرض علمی قرار دهد؛
5. batch fitting در مقیاس بالا را پشتیبانی کند؛
6. امکان تغییر مدل‌های HGF، couplingها، update ruleها و response modelها را بدون copy/paste گسترده فراهم کند؛
7. مدل‌ها، configها، transformها، simulation، fitting، diagnostics و model comparison را پوشش دهد؛
8. برای هر مدل/تابع، سازگاری با MATLAB با **Golden Tests** اثبات شود.

> اصل پروژه:
>
> **AI کد را می‌نویسد؛ تست مرجع صحت علمی را تعیین می‌کند.**

---

# 2) Source of Truth

مرجع اصلی:

- **HGF Toolbox v8.2.0**
- مخزن رسمی:  
  https://github.com/ComputationalPsychiatry/hgf-toolbox
- معماری رسمی:  
  https://github.com/ComputationalPsychiatry/hgf-toolbox/blob/master/ARCHITECTURE.md

مرجع کمکی:

- **PyHGF**
- مخزن رسمی:  
  https://github.com/ComputationalPsychiatry/pyhgf
- مستندات:  
  https://computationalpsychiatry.github.io/pyhgf/

Backend محاسباتی:

- **JAX**
- نصب GPU:  
  https://docs.jax.dev/en/latest/installation.html
- تنظیم x64:  
  https://docs.jax.dev/en/latest/default_dtypes.html

---

# 3) نکته مهم درباره تعداد فایل‌ها

در `ARCHITECTURE.md` رسمی HGF Toolbox، ساختار به‌صورت زیر توصیف شده است:

| بخش | تعداد گزارش‌شده در Architecture |
|---|---:|
| Core | 5 |
| Building blocks | 10 |
| Perceptual | 149 |
| Observation | 82 |
| Plotting | 26 |
| Utilities | 15 |

اما در درخت فعلی مخزن، حداقل در `plotting` و `utilities` چند فایل جدیدتر دیده می‌شود؛ برای نمونه `lambert_w0.m` در نسخه 8.2 اضافه شده است.

بنابراین **هیچ migration نهایی نباید صرفاً به این شمارش متکی باشد**.

در ابتدای پروژه باید:

```text
HGF v8.2.0 tag
      ↓
exact commit SHA
      ↓
recursive file manifest
      ↓
checksum
      ↓
Migration Matrix
```

ساخته شود.

این سند، ماتریکس معماری و علمی را می‌دهد؛ **manifest فایل‌به‌فایل نهایی باید از همان commit فریز‌شده به‌صورت ماشینی تولید شود.**

---

# 4) تصمیم معماری اصلی

دو لایه پیشنهاد می‌شود:

```text
                  hgf-python
                      │
          ┌───────────┴───────────┐
          │                       │
     hgf_compat                hgf_fast
          │                       │
 TAPAS-compatible           GPU-native API
 semantics/API              JAX/vmap/jit
          │                       │
 numerical parity          high-throughput
          └───────────┬───────────┘
                      │
                  JAX Core
                      │
             CPU / NVIDIA GPU
```

## `hgf_compat`

هدف:

- نزدیک‌ترین رفتار ممکن به MATLAB HGF Toolbox؛
- حفظ ترتیب پارامترها؛
- همان transformها؛
- همان prior semantics؛
- همان placeholder semantics؛
- همان irregular-trial handling؛
- همان `traj`/`infStates`;
- همان AIC/BIC/LME/Hessian pipeline؛
- optimizer compatibility mode.

## `hgf_fast`

هدف:

- همان مدل ریاضی؛
- JAX-native gradient/Hessian؛
- JIT؛
- `lax.scan` روی trialها؛
- `vmap` روی subject/restart؛
- batch fitting؛
- GPU optimizer؛
- multi-GPU در مرحله بعد.

---

# 5) Legend ماتریکس

## Reuse از PyHGF

- **H** = High: بخش مشابه/نزدیک از قبل وجود دارد.
- **M** = Medium: زیرساخت قابل reuse است ولی compatibility layer لازم است.
- **L** = Low: فقط utility/general architecture قابل reuse است.
- **N** = None/Unknown: باید مستقلاً پیاده‌سازی شود یا ابتدا بررسی دقیق شود.

## ریسک parity

- **Critical**: خطا می‌تواند پارامتر، likelihood یا استنتاج علمی را تغییر دهد.
- **High**: خطا trajectory/result را تغییر می‌دهد.
- **Medium**: خروجی تحلیلی/رابط یا utility.
- **Low**: عمدتاً visualization یا convenience.

## Priority

- **P0**: قبل از هر fitting واقعی.
- **P1**: برای parity اصلی HGF.
- **P2**: مدل‌های legacy/specialized و diagnostics.
- **P3**: polish/plotting/compatibility تکمیلی.

---

# 6) ماتریکس Core

| ID | MATLAB | نقش | Target Python/JAX | PyHGF reuse | GPU | Risk | Priority | تست مرجع |
|---|---|---|---|---|---|---|---|---|
| C01 | `fitModel.m` | orchestration کامل fitting | `hgf_compat/fit.py` | M | بله | Critical | P0 | objective, params, ll, priors, metrics |
| C02 | `simModel.m` | شبیه‌سازی پاسخ | `hgf_compat/sim.py` | M | بله | High | P1 | seeded simulation parity |
| C03 | `sampleModel.m` | sampling از مدل | `hgf_compat/sample.py` | M | بله | High | P1 | distribution + seed tests |
| C04 | `quasinewton_optim.m` | MAP quasi-Newton | `optim/compat_quasinewton.py` | L | compat: CPU/JAX؛ fast: GPU | Critical | P0 | step/termination/MAP parity |
| C05 | `quasinewton_optim_config.m` | config optimizer | `config/optim.py` | L | N/A | High | P0 | default/config parity |

## الزامات `fitModel`

نسخه Python باید این رفتارها را دقیقاً پوشش دهد:

- perceptual model execution؛
- observation model likelihood؛
- چند response stream در صورت استفاده؛
- حذف irregular trials از likelihood؛
- prior فقط برای free/non-NaN parameters؛
- fixed parameters؛
- negative log joint؛
- random initialization / multi-start؛
- انتخاب بهترین fit؛
- prediction/residual outputs؛
- AIC؛
- BIC؛
- Hessian؛
- posterior covariance؛
- correlation؛
- LME؛
- accuracy/complexity decomposition.

فرمول‌های کلیدی:

$$
\mathrm{AIC}=2\,\mathrm{negLL}+2d
$$

$$
\mathrm{BIC}=2\,\mathrm{negLL}+d\log(N)
$$

و در تقریب Laplace:

$$
\mathrm{LME}
=
-\mathrm{negLogJoint}(\theta^\*)
+
\frac{1}{2}\log\left(\frac{1}{\det H}\right)
+
\frac{d}{2}\log(2\pi)
$$

---

# 7) ماتریکس Building Blocks

فایل‌های پایه رسمی:

1. `hgf_binary_level1.m`
2. `hgf_binary_level2.m`
3. `hgf_check_trajectories.m`
4. `hgf_continuous_level1.m`
5. `hgf_pihat.m`
6. `hgf_pihat_last.m`
7. `hgf_prediction.m`
8. `hgf_time_axis.m`
9. `hgf_volatility_pe.m`
10. `hgf_volatility_update.m`

| ID | MATLAB | Target | PyHGF reuse | GPU mapping | Risk | Priority | Golden test |
|---|---|---|---|---|---|---|---|
| B01 | `hgf_time_axis.m` | `core/time_axis.py` | M | JIT | High | P0 | irregular dt / first trial |
| B02 | `hgf_prediction.m` | `updates/prediction.py` | H | `jit` | Critical | P0 | per-level prediction |
| B03 | `hgf_pihat.m` | `updates/precision_prediction.py` | H | `jit` | Critical | P0 | precision recursion |
| B04 | `hgf_pihat_last.m` | same module | H | `jit` | Critical | P0 | last-level branch |
| B05 | `hgf_binary_level1.m` | `updates/binary_l1.py` | H | `scan` | Critical | P0 | trial-wise posterior |
| B06 | `hgf_binary_level2.m` | `updates/binary_l2.py` | H | `scan` | Critical | P0 | PE/update |
| B07 | `hgf_continuous_level1.m` | `updates/continuous_l1.py` | H | `scan` | Critical | P0 | continuous observations |
| B08 | `hgf_volatility_update.m` | `updates/volatility.py` | H | `scan/jit` | Critical | P0 | HGF/eHGF/uHGF branches |
| B09 | `hgf_volatility_pe.m` | `updates/volatility_pe.py` | H | `jit` | Critical | P0 | PE parity |
| B10 | `hgf_check_trajectories.m` | `validation/trajectory_checks.py` | M | CPU/JIT | High | P0 | NaN/Inf/invalid state |

---

# 8) خانواده Unified HGF/eHGF/uHGF

از نسخه 8 معماری HGF، eHGF و uHGF تا حد زیادی unified شده است.

`update_type` باید سه حالت اصلی را پشتیبانی کند:

```text
hgf
ehgf
uhgf
```

| ID | خانواده MATLAB | Target | Reuse | Risk | Priority | تست اصلی |
|---|---|---|---|---|---|---|
| U01 | `hgf_unified` | `models/hgf_continuous.py` | H | Critical | P0 | full trajectory |
| U02 | `hgf_binary_unified` | `models/hgf_binary.py` | H | Critical | P0 | binary trajectories |
| U03 | `hgf_binary_pu_unified` | `models/hgf_binary_pu.py` | M | Critical | P1 | PU trajectory |
| U04 | `hgf_binary_pu_tbt_unified` | `models/hgf_binary_pu_tbt.py` | M | Critical | P1 | trial-by-trial PU |
| U05 | `hgf_ar1_binary_unified` | `models/hgf_ar1_binary.py` | M/L | Critical | P1 | AR state recursion |
| U06 | `hgf_ar1_binary_mab_unified` | `models/hgf_ar1_binary_mab.py` | L | Critical | P1 | MAB + AR |
| U07 | `hgf_jget_unified` | `models/hgf_jget.py` | L | Critical | P1 | JGET trajectories |

---

# 9) uHGF: آیتم Critical مستقل

نسخه 8.2.0 در uHGF بخش مهمی دارد که باید **مستقیماً با MATLAB تست شود**:

- posterior-mode calculation؛
- Lambert \(W_0\)؛
- دو quadratic approximation؛
- variational-energy weighting؛
- Gaussian-mixture moment matching.

برای دو تقریب:

$$
q_1(x),q_2(x)
$$

وزن ترکیب:

$$
b=
\frac{1}{1+\exp(I_1-I_2)}
$$

و moment matching:

$$
\mu
=
b\mu_1+(1-b)\mu_2
$$

$$
\sigma^2
=
b\left(\sigma_1^2+\mu_1^2\right)
+
(1-b)\left(\sigma_2^2+\mu_2^2\right)
-\mu^2
$$

$$
\pi=\frac{1}{\sigma^2}
$$

## الزام

حتی اگر PyHGF implementation بسیار نزدیک داشته باشد:

> **بدون Golden Test مستقیم، هیچ uHGF function به‌عنوان compatible علامت نمی‌خورد.**

---

# 10) سایر خانواده‌های Perceptual

بر اساس معماری و تاریخچه رسمی HGF، خانواده‌های زیر باید در inventory نهایی وجود داشته باشند.

| ID | خانواده | Target | PyHGF reuse | Risk | Priority |
|---|---|---|---|---|---|
| P01 | Standard continuous HGF | `models/hgf.py` | H | Critical | P0 |
| P02 | Binary HGF | `models/hgf_binary.py` | H | Critical | P0 |
| P03 | eHGF | shared update type | H | Critical | P0 |
| P04 | uHGF | shared update type | H | Critical | P0 |
| P05 | HGF PU | `models/hgf_pu.py` | M | Critical | P1 |
| P06 | HGF PU TBT | `models/hgf_pu_tbt.py` | M | Critical | P1 |
| P07 | AR1 HGF | `models/hgf_ar1.py` | L/M | Critical | P1 |
| P08 | AR1 Binary | `models/hgf_ar1_binary.py` | L/M | Critical | P1 |
| P09 | MAB variants | `models/mab/` | L | Critical | P1 |
| P10 | JGET | `models/jget.py` | L | Critical | P1 |
| P11 | Categorical HGF | `models/categorical.py` | H/M | Critical | P1 |
| P12 | WhatWorld / WhichWorld | `models/world/` | L | High | P2 |
| P13 | RW binary | `models/rw.py` | N/L | High | P2 |
| P14 | RW binary dual | `models/rw_dual.py` | N/L | High | P2 |
| P15 | Pearce-Hall binary | `models/pearce_hall.py` | N/L | High | P2 |
| P16 | Sutton K1 | `models/sutton_k1.py` | N/L | High | P2 |
| P17 | Kalman-filter family | `models/kalman.py` | N/L | High | P2 |
| P18 | HMM binary | `models/hmm.py` | N/L | High | P2 |
| P19 | HHMM binary | `models/hhmm.py` | N/L | High | P2 |
| P20 | Bayes-optimal models | `models/bayes_optimal/` | N/L | High | P2 |
| P21 | conditional-hallucination related perceptual integrations | model-specific | N/L | High | P2 |
| P22 | custom/user perceptual models | plugin protocol | H architecture | Critical | P1 |

> نکته: تعداد دقیق فایل‌های perceptual در commit فریز‌شده باید با script manifest استخراج شود.  
> ماتریس فوق در سطح **خانواده/رفتار علمی** است؛ manifest نهایی فایل‌به‌فایل به این ماتریس attach می‌شود.

---

# 11) Observation / Response Model Matrix

## خانواده‌های اصلی

| ID | خانواده | MATLAB files | Target | Reuse | GPU | Risk | Priority |
|---|---|---|---|---|---|---|---|
| O01 | Beta observation | `beta_obs*` | `responses/beta.py` | L/M | JIT | High | P1 |
| O02 | CDF Gaussian | `cdfgaussian_obs*` | `responses/cdf_gaussian.py` | L/M | JIT | High | P1 |
| O03 | Conditional Hallucination | `condhalluc_obs*` | `responses/condhalluc.py` | L | JIT | Critical | P2 |
| O04 | Conditional Hallucination 2 | `condhalluc_obs2*` | same family | L | JIT | Critical | P2 |
| O05 | Conditional Hallucination 3 | `condhalluc_obs3*` | same family | L | JIT | Critical | P2 |
| O06 | Gaussian | `gaussian_obs*` | `responses/gaussian.py` | M | JIT | High | P1 |
| O07 | Gaussian offset | `gaussian_obs_offset*` | `responses/gaussian.py` | M | JIT | High | P1 |
| O08 | logRT binary | `logrt_linear_binary*` | `responses/logrt.py` | L | JIT | Critical | P1 |
| O09 | logRT binary minimal | `logrt_linear_binary_minimal*` | same | L | JIT | Critical | P1 |
| O10 | logRT WhatWorld | `logrt_linear_whatworld*` | same | L | JIT | High | P2 |
| O11 | Softmax continuous | `softmax*` | `responses/softmax.py` | M/H | JIT | High | P1 |
| O12 | Softmax 2-beta | `softmax_2beta*` | same | L/M | JIT | High | P1 |
| O13 | Softmax binary | `softmax_binary*` | same | H/M | JIT | Critical | P0 |
| O14 | Softmax mu3 | `softmax_mu3*` | same | M | JIT | High | P1 |
| O15 | Softmax mu3 world | `softmax_mu3_wld*` | same | L | JIT | High | P2 |
| O16 | Softmax world | `softmax_wld*` | same | L | JIT | High | P2 |
| O17 | Unit-square sigmoid | `unitsq_sgm*` | `responses/unitsq_sigmoid.py` | M/H | JIT | Critical | P0 |
| O18 | Unit-square sigmoid mu3 | `unitsq_sgm_mu3*` | same | M | JIT | High | P1 |

---

# 12) فهرست فعلی 82 فایل Observation

این فهرست باید در manifest نهایی با commit فریز‌شده verify شود:

```text
beta_obs.m
beta_obs_config.m
beta_obs_namep.m
beta_obs_sim.m
beta_obs_transp.m

cdfgaussian_obs.m
cdfgaussian_obs_config.m
cdfgaussian_obs_transp.m

condhalluc_obs.m
condhalluc_obs2.m
condhalluc_obs2_config.m
condhalluc_obs2_namep.m
condhalluc_obs2_sim.m
condhalluc_obs2_transp.m
condhalluc_obs3.m
condhalluc_obs3_config.m
condhalluc_obs3_namep.m
condhalluc_obs3_sim.m
condhalluc_obs3_transp.m
condhalluc_obs_config.m
condhalluc_obs_namep.m
condhalluc_obs_sim.m
condhalluc_obs_transp.m

gaussian_obs.m
gaussian_obs_config.m
gaussian_obs_namep.m
gaussian_obs_offset.m
gaussian_obs_offset_config.m
gaussian_obs_offset_namep.m
gaussian_obs_offset_sim.m
gaussian_obs_offset_transp.m
gaussian_obs_sim.m
gaussian_obs_transp.m

logrt_linear_binary.m
logrt_linear_binary_config.m
logrt_linear_binary_minimal.m
logrt_linear_binary_minimal_config.m
logrt_linear_binary_minimal_transp.m
logrt_linear_binary_namep.m
logrt_linear_binary_sim.m
logrt_linear_binary_transp.m
logrt_linear_whatworld.m
logrt_linear_whatworld_config.m
logrt_linear_whatworld_transp.m

softmax.m
softmax_2beta.m
softmax_2beta_config.m
softmax_2beta_transp.m
softmax_binary.m
softmax_binary_config.m
softmax_binary_namep.m
softmax_binary_sim.m
softmax_binary_transp.m
softmax_config.m
softmax_mu3.m
softmax_mu3_config.m
softmax_mu3_namep.m
softmax_mu3_sim.m
softmax_mu3_transp.m
softmax_mu3_wld.m
softmax_mu3_wld_config.m
softmax_mu3_wld_namep.m
softmax_mu3_wld_sim.m
softmax_mu3_wld_transp.m
softmax_namep.m
softmax_sim.m
softmax_transp.m
softmax_wld.m
softmax_wld_config.m
softmax_wld_namep.m
softmax_wld_sim.m
softmax_wld_transp.m

unitsq_sgm.m
unitsq_sgm_config.m
unitsq_sgm_mu3.m
unitsq_sgm_mu3_config.m
unitsq_sgm_mu3_namep.m
unitsq_sgm_mu3_sim.m
unitsq_sgm_mu3_transp.m
unitsq_sgm_namep.m
unitsq_sgm_sim.m
unitsq_sgm_transp.m
```

---

# 13) Config / Transform / Naming Matrix

الگوی کلاسیک فایل‌ها:

```text
<model>.m
<model>_config.m
<model>_transp.m
<model>_namep.m
<model>_sim.m
<model>_plotTraj.m
<model>_config_base.m
```

در Python این الگو نباید به صدها فایل duplicate تبدیل شود.

Target:

```python
@dataclass
class ParameterSpec:
    name: str
    prior_mean: float
    prior_variance: float
    transform: Transform
    fixed: bool
```

و:

```python
@dataclass
class ModelConfig:
    parameters: tuple[ParameterSpec, ...]
    options: dict
```

## موارد Critical

| آیتم | رفتار MATLAB | Target |
|---|---|---|
| ترتیب پارامتر | flat vector order | دقیقاً حفظ شود |
| positive parameters | exponential transform | compatibility identical |
| unconstrained params | identity | identical |
| fixed parameter | prior variance = 0 | identical semantics |
| NaN placeholders | مدل/level dependent | identical |
| config defaults | function-generated | immutable dataclass defaults |
| `namep` | display names | metadata |
| `transp` | native/transformed mapping | transform registry |

---

# 14) Placeholder Semantics

HGF از placeholderهای خاص استفاده می‌کند که باید دقیقاً حفظ شوند.

بر اساس معماری رسمی:

| Placeholder | معنا |
|---:|---|
| `99991` | first input-related placeholder |
| `99992` | variance of first 20 |
| `99993` | log variance of first 20 |
| `99994` | log variance minus 2 |

در Python نباید اینها به‌صورت magic number در سراسر codebase پخش شوند.

پیشنهاد:

```python
class Placeholder(Enum):
    FIRST_INPUT = 99991
    VAR_FIRST_20 = 99992
    LOG_VAR_FIRST_20 = 99993
    LOG_VAR_FIRST_20_MINUS_2 = 99994
```

و resolver مستقل داشته باشد.

---

# 15) `traj` و `infStates` Compatibility

## `traj`

بسته به مدل، فیلدهایی مانند:

```text
mu
sa
muhat
sahat
v
w
da
ud
psi
epsi
wt
```

باید با semantics MATLAB حفظ شوند.

## `infStates`

ساختار استاندارد:

```text
trials × levels × 4
```

چهار channel:

```text
muhat
sahat
mu
sa
```

Target:

```python
InferenceStates(
    muhat=...,
    sahat=...,
    mu=...,
    sa=...,
)
```

اما compatibility wrapper باید export به آرایه MATLAB-like نیز داشته باشد.

---

# 16) Utilities Matrix

فهرست فعلی مشاهده‌شده:

```text
align_priors.m
align_priors_fields.m
bayesian_parameter_average.m
boltzmann.m
datagen_categorical.m
lambert_w0.m
nearest_psd.m
riddersdiff.m
riddersdiff2.m
riddersdiffcross.m
riddersgradient.m
riddershessian.m
tapas_Cov2Corr.m
tapas_autocorr.m
tapas_logit.m
tapas_sgm.m
```

| ID | Utility | Target | Reuse | GPU | Risk | Priority |
|---|---|---|---|---|---|---|
| UT01 | `align_priors` | `utils/priors.py` | L | CPU | High | P0 |
| UT02 | `align_priors_fields` | same | L | CPU | High | P0 |
| UT03 | `bayesian_parameter_average` | `analysis/bpa.py` | L | optional | Medium | P2 |
| UT04 | `boltzmann` | `math/boltzmann.py` | M | JIT | High | P1 |
| UT05 | `datagen_categorical` | `sim/categorical.py` | M | vmap | Medium | P2 |
| UT06 | `lambert_w0` | `math/lambert_w.py` | H/M | JIT | Critical | P0 |
| UT07 | `nearest_psd` | `math/psd.py` | M | JIT/CPU | Critical | P0 |
| UT08 | `riddersdiff` | `numerics/ridders.py` | N | compat CPU/JAX | Critical | P0 |
| UT09 | `riddersdiff2` | same | N | compat | Critical | P0 |
| UT10 | `riddersdiffcross` | same | N | compat | Critical | P0 |
| UT11 | `riddersgradient` | same | N | compat | Critical | P0 |
| UT12 | `riddershessian` | same | N | compat | Critical | P0 |
| UT13 | `tapas_Cov2Corr` | `math/cov.py` | L | CPU/JIT | High | P1 |
| UT14 | `tapas_autocorr` | `diagnostics/autocorr.py` | M | optional | Medium | P2 |
| UT15 | `tapas_logit` | `math/transforms.py` | H | JIT | Critical | P0 |
| UT16 | `tapas_sgm` | `math/transforms.py` | H | JIT | Critical | P0 |

## وضعیت M3 — Scalar Numerical Parity

Gate `M3` برای utilityهای scalar زیر **PASS** شده است:

| Utility IDs | وضعیت | Evidence |
|---|---|---|
| UT04 | PORT + GOLDEN PASS | `boltzmann` |
| UT06–UT07 | PORT + GOLDEN PASS | `lambert_w0`, `nearest_psd` |
| UT08–UT12 | PORT + GOLDEN PASS | خانواده کامل Ridders |
| UT13 | PORT + GOLDEN PASS | `tapas_Cov2Corr` |
| UT15–UT16 | PORT + GOLDEN PASS | `tapas_logit`, `tapas_sgm` |

Reference: HGF 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`  
CI evidence: workflow run `34114052778`.

## نکته مهم

در **compatibility mode** برای Hessian/LME نباید فوراً Ridders را با autodiff جایگزین کرد.

دو مسیر:

```text
compat:
    Ridders numerical derivatives
    → MATLAB-like Hessian/LME

fast:
    jax.grad / jax.hessian
    → GPU-native
```

---

# 17) Plotting / Diagnostics Matrix

درخت فعلی حداقل فایل‌های زیر را نشان می‌دهد:

```text
ehgf_ar1_binary_plotTraj.m
ehgf_binary_plotTraj.m
ehgf_jget_plotTraj.m
ehgf_plotTraj.m
fit_plotCorr.m
fit_plotResidualDiagnostics.m
hgf_ar1_binary_mab_plotTraj.m
hgf_ar1_binary_plotTraj.m
hgf_ar1_mab_plotTraj.m
hgf_ar1_plotTraj.m
hgf_binary_condhalluc_plotTraj.m
hgf_binary_mab_plotTraj.m
hgf_binary_plotTraj.m
hgf_binary_pu_tbt_plotTraj.m
hgf_categorical_plotTraj.m
hgf_jget_plotTraj.m
hgf_plotTraj.m
hgf_whatworld_plotTraj.m
hgf_whichworld_plotTraj.m
ph_binary_plotTraj.m
rw_binary_dual_plotTraj.m
rw_binary_plotTraj.m
sutton_k1_binary_plotTraj.m
tapas_hhmm_binary_displayResults.m
tapas_hmm_binary_displayResults.m
tapas_kf_plotTraj.m
uhgf_binary_plotTraj.m
uhgf_plotTraj.m
```

Target:

```text
plotting/
    trajectories.py
    fit_corr.py
    residuals.py
    model_specific/
```

Plotting از GPU استفاده نمی‌کند و **نباید مسیر critical migration را block کند**.

Priority: P3 مگر diagnosticهای علمی مانند residual diagnostics.

---

# 18) PyHGF Reuse Matrix

## چیزهایی که از قبل مفیدند

PyHGF در معماری فعلی خود موارد زیر را فراهم می‌کند یا زیرساخت قوی برایشان دارد:

- JAX backend؛
- JIT-compatible update functions؛
- differentiable model computations؛
- `jax.lax.scan`-style belief propagation؛
- vectorized operations؛
- continuous HGF؛
- binary/categorical structures؛
- standard volatility updates؛
- eHGF-like updates؛
- unbounded/uHGF-related updates؛
- custom response functions؛
- generalized network/node/edge architecture؛
- sampling utilities؛
- integration با PyMC برای Bayesian workflows.

## Gapهای اصلی برای parity کامل TAPAS/HGF Toolbox

| Gap | شدت |
|---|---|
| API یک‌به‌یک `fitModel` | Critical |
| TAPAS parameter ordering | Critical |
| config/namep/transp compatibility | Critical |
| exact prior/fixed-parameter semantics | Critical |
| placeholder semantics | High |
| exact irregular-trial behavior | Critical |
| multiple response streams | High |
| full 82-file observation compatibility | Critical |
| specialized/legacy perceptual models | Critical |
| MATLAB quasi-Newton parity | Critical |
| Ridders numerical derivative/Hessian path | Critical |
| exact LME decomposition | Critical |
| AIC/BIC/result struct parity | High |
| full simulation parity | High |
| plotting parity | Low/Medium |
| golden regression corpus | Critical |

---

# 19) تصمیم Fork یا Dependency

در شروع پروژه **PyHGF را فوراً fork نکن**.

ابتدا:

```text
PyHGF pinned dependency
       │
       ▼
compat adapters
       │
       ▼
Golden tests:
standard HGF
eHGF
uHGF
```

## Gate

اگر با wrapper/configuration کم بتوانیم parity بگیریم:

```text
keep dependency + adapters
```

اگر core defaults/update ordering/clipping/shape semantics به‌طور مداوم مانع parity شوند:

```text
create shallow fork
pin exact upstream commit
maintain compatibility patches
```

این تصمیم باید بر اساس test result گرفته شود، نه ترجیح معماری.

---

# 20) Numerical Precision Policy

حالت علمی پیش‌فرض:

```python
jax.config.update("jax_enable_x64", True)
```

## سه baseline

```text
MATLAB float64
      vs
JAX CPU float64
      vs
JAX GPU float64
```

## tolerance

نباید یک tolerance ثابت برای همه چیز تعیین کرد.

پیشنهاد اولیه برای calibration:

| سطح | Target اولیه |
|---|---|
| scalar utilities CPU x64 | `rtol ~ 1e-11`, `atol ~ 1e-12` |
| building blocks | `1e-10` تا `1e-11` |
| recursive trajectories | `1e-9` تا `1e-10` |
| GPU x64 | بر اساس backend، معمولاً کمی relaxed |
| MAP parameters | parameter + objective equivalence |
| LME/Hessian | separate calibrated thresholds |

> این اعداد **Definition نهایی نیستند**.  
> با اجرای golden sweep روی مدل‌های واقعی calibration می‌شوند.

---

# 21) Golden Test Matrix

| Level | موضوع | مثال |
|---|---|---|
| G0 | scalar math | logit, sigmoid, Lambert W |
| G1 | building blocks | pihat, volatility update |
| G2 | one-step update | یک trial |
| G3 | forward trajectory | 100–1000 trial |
| G4 | response likelihood | trial log-likelihood |
| G5 | transforms/priors | free/fixed parameters |
| G6 | objective | negLL / negLogJoint |
| G7 | optimizer | fitted MAP |
| G8 | Hessian/LME | H, Sigma, Corr, LME |
| G9 | simulation | deterministic seeded sim |
| G10 | CPU/GPU | JAX CPU vs GPU |
| G11 | batch/single | batch fit == repeated single |
| G12 | parameter recovery | known true params |
| G13 | model recovery | generating model |
| G14 | edge cases | missing/irregular/extreme |

---

# 22) Golden Fixture Schema

هر fixture باید حداقل داشته باشد:

```text
metadata/
    hgf_version
    hgf_commit_sha
    matlab_version
    fixture_schema_version
    model_name
    response_model_name
    optimizer_name
    rng_seed

input/
    u
    y
    irregular_trial_mask
    time_axis

config/
    perceptual_config
    observation_config
    optimizer_config

params/
    native
    transformed
    free_indices
    fixed_indices

forward/
    traj/*
    infStates
    predictions

likelihood/
    trial_loglik
    total_loglik
    priors
    negLogJoint

fit/
    map_params
    objective
    iterations
    convergence
    hessian
    sigma
    corr
    LME
    AIC
    BIC
    accuracy
    complexity
```

---

# 23) Edge Cases اجباری

برای هر مدل P0/P1:

- input all zeros؛
- input all ones؛
- alternating inputs؛
- short sequence؛
- long sequence؛
- extreme but valid parameter values؛
- near-boundary precision؛
- fixed parameter combinations؛
- mixed free/fixed؛
- missing responses؛
- irregular trials؛
- non-unit time intervals؛
- NaN where officially supported؛
- multiple random starts؛
- unstable initializations؛
- deterministic seed؛
- GPU batch with heterogeneous subjects؛
- same model with different trial lengths.

---

# 24) GPU Mapping Matrix

| جزء | Parallelization |
|---|---|
| trial recursion | `jax.lax.scan` |
| subjects | `jax.vmap` |
| random restarts | `jax.vmap` |
| same-model batches | `vmap + jit` |
| model grid | scheduler + compiled signatures |
| gradients | `jax.grad` |
| Hessian fast mode | `jax.hessian` / structured approximation |
| optimizer state | on-device |
| multi-GPU | بعد از single-GPU parity |

## اصل مهم

در loop optimizer:

```text
NO:
CPU params → GPU objective → CPU optimizer → GPU ...

YES:
data + params + objective + grad + optimizer state
             stay on GPU
```

---

# 25) Compilation Strategy

مدل‌های HGF متعدد و سفارشی می‌توانند موجب recompilation زیاد شوند.

پس signature باید بر اساس:

```text
model topology
number of levels
response model
dtype
trial-length bucket
static options
```

cache شود.

برای trial lengths متفاوت:

```text
bucket + mask
```

از compile مجدد مداوم بهتر است.

---

# 26) API پیشنهادی

## Compatibility API

```python
est = fit_model(
    responses=y,
    inputs=u,
    perceptual="hgf_binary_config",
    observation="unitsq_sgm_config",
    optimizer="quasinewton_optim_config",
    mode="compat",
)
```

```python
sim = sim_model(...)
samples = sample_model(...)
```

خروجی:

```python
est.p_prc
est.p_obs
est.traj
est.optim
est.yhat
est.res
est.irr
```

## Native API

```python
model = HGF(
    levels=3,
    update_type="uhgf",
    observation="binary",
)

result = fit_batch(
    model,
    data,
    device="gpu",
    dtype="float64",
    batch_size=512,
)
```

---

# 27) Custom Model Protocol

برای کار پژوهشی بلندمدت باید extension API از روز اول تعریف شود.

```python
class PerceptualModel(Protocol):
    def init_state(self, config): ...
    def step(self, state, input_t, params): ...
    def trajectories(self, ...): ...
```

```python
class ResponseModel(Protocol):
    def log_prob(self, response, inf_state, params): ...
    def simulate(self, key, inf_state, params): ...
```

```python
class Coupling(Protocol):
    def prediction(self, ...): ...
    def update(self, ...): ...
```

هدف:

```text
new model
!=
copy 10 files
```

بلکه:

```text
new model
=
compose existing blocks
+
override only changed equation
```

---

# 28) Source Manifest Generator

در kickoff باید از commit فریز‌شده manifest تولید شود.

نمونه Python:

```python
from pathlib import Path
import hashlib

root = Path("hgf-toolbox")

for path in sorted(root.rglob("*.m")):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{path.as_posix()}\t{digest}")
```

خروجی باید version-control شود:

```text
reference/
    HGF_VERSION
    HGF_COMMIT
    matlab_manifest.tsv
    matlab_manifest.sha256
```

## شرط

هر فایل `.m` باید یکی از statusهای زیر داشته باشد:

```text
PORT
WRAP
REUSE_PYHGF
REFERENCE_ONLY
PLOT_ONLY
DEPRECATED
NOT_APPLICABLE
```

هیچ status خالی مجاز نیست.

---

# 29) Definition of Complete Migration

مهاجرت فقط وقتی کامل است که:

- [ ] 100% فایل‌های MATLAB در manifest classification داشته باشند.
- [ ] همه model families P0/P1 port یا reuse شده باشند.
- [ ] همه observation families port شده باشند.
- [ ] config/transform/name semantics parity داشته باشد.
- [ ] `fitModel` compatibility tests پاس شود.
- [ ] `simModel` compatibility tests پاس شود.
- [ ] `sampleModel` compatibility tests پاس شود.
- [ ] trajectory parity پاس شود.
- [ ] likelihood parity پاس شود.
- [ ] Hessian/Sigma/Corr parity پاس شود.
- [ ] AIC/BIC/LME parity پاس شود.
- [ ] CPU x64 tests پاس شود.
- [ ] GPU x64 tests پاس شود.
- [ ] batch == single tests پاس شود.
- [ ] parameter recovery suite پاس شود.
- [ ] model recovery suite پاس شود.
- [ ] custom-model extension API مستند باشد.
- [ ] runtime MATLAB dependency = 0.
- [ ] provenance/license notices کامل باشد.

---

# 30) جمع‌بندی ماتریکس

## چیزهایی که احتمالاً نباید از صفر نوشته شوند

- JAX graph/update infrastructure؛
- بخش‌هایی از standard HGF؛
- eHGF updates؛
- uHGF/unbounded updates؛
- categorical/generalized network concepts؛
- custom response infrastructure؛
- JAX scan/vectorization.

PyHGF برای اینها foundation جدی است.

## چیزهایی که باید عملاً برای پروژه ساخته شوند

- TAPAS/HGF compatibility layer؛
- config/parameter compatibility؛
- full observation-model compatibility pack؛
- legacy/specialized perceptual models؛
- MATLAB-like quasi-Newton path؛
- Ridders derivative/Hessian implementation؛
- fit statistics/LME pipeline؛
- golden corpus؛
- batch GPU scheduler؛
- compatibility output structures؛
- validation/recovery suite.

## نتیجه معماری

بهترین مسیر:

$$
\boxed{
\text{HGF 8.2.0 as Specification}
+
\text{PyHGF where mathematically reusable}
+
\text{JAX x64}
+
\text{Golden MATLAB Tests}
+
\text{GPU Batch Engine}
}
$$

نه:

$$
\text{MATLAB-to-Python blind translation}
$$

---

# 31) منابع اصلی

1. HGF Toolbox official repository  
   https://github.com/ComputationalPsychiatry/hgf-toolbox

2. HGF Toolbox architecture  
   https://github.com/ComputationalPsychiatry/hgf-toolbox/blob/master/ARCHITECTURE.md

3. PyHGF official repository  
   https://github.com/ComputationalPsychiatry/pyhgf

4. PyHGF documentation  
   https://computationalpsychiatry.github.io/pyhgf/

5. JAX installation  
   https://docs.jax.dev/en/latest/installation.html

6. JAX default dtype / x64  
   https://docs.jax.dev/en/latest/default_dtypes.html

---

# 32) سند مرتبط

برای ترتیب دقیق اجرا، gateها، ساخت repo، workflow هوش مصنوعی، CI، تست و cutover به سند زیر مراجعه شود:

```text
02_HGF_Python_GPU_Execution_Plan.md
```
