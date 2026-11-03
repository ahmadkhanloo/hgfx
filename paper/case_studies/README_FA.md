# مطالعه‌های واقعی برای بازتولید MATLAB → HGFX

> ????? ???? 2026-11-04: Pain ?????? ???? ??????????? SPIRL ??? ? Hein ?????? ????????? ???. Arthur ?? ???? config??? ????? ?????? ???? ????. [??? ?????? ? ???? ????](../../docs/superpowers/plans/2026-11-04-pain-case-study-handoff.md) ?? ????? ?????? ??? ???? ???. ??? ???????? ????? ???? ???? ???.

تاریخ بررسی: ۳ نوامبر ۲۰۲۶. این پوشه **بستهٔ منابع و طرح بازتولید** است؛ هیچ fit جدید، تأیید نتیجهٔ مقاله یا PASS سازگاری از این دریافت فایل‌ها حاصل نشده است.

## تصمیم پیشنهادی

دو مطالعهٔ اصلی برای **بررسی امکان بازتولید**: Arthur et al. 2023 برای پیش‌بینی حرکتی و Hess et al. 2025 برای یادگیری پاداش/زمان پاسخ. انتخاب نهایی پس از تطبیق مدل، نسخه، داده و مجوز خواهد بود، نه براساس میزان توافق مطلوب. مقالهٔ درد، گزینهٔ جایگزین با مدل پاسخ سفارشی است. مطالعهٔ اجتماعی Henco برای تنوع کاربرد ارزشمند است ولی برای این مقاله اولویت پایین‌تری دارد.

وجود مقاله، کد و داده با «آمادگی اجرای بدون تغییر در HGFX1.0» یکسان نیست. هیچ‌یک هنوز انتهابه‌انتها در HGFX اجرا نشده‌اند.

| گزینه | شواهد دسترسی | مانع/دامنهٔ مناسب |
|---|---|---|
| **Arthur et al., 2023 — Testing predictive coding theories of autism spectrum disorder using models of active inference** | [مقاله PLOS](https://doi.org/10.1371/journal.pcbi.1011473)، [داده و کد OSF](https://osf.io/5k48n/)، inventory فایل‌های واقعی در `arthur_2023/osf_inventory.json` | دو تکلیف object lifting و interception؛ Study1 مدل HGF4 دارد. ابتدا Study2 و مسیر binary بررسی شود؛ نسخه و config دقیق هنوز gate باز است. مجوز پروژهٔ OSF اعلام نشده؛ مقاله CC BY است، فایل‌های OSF به‌صورت عمومی در این repo بازتوزیع نمی‌شوند. |
| **Hess et al., 2025 — Bayesian Workflow for Generative Modeling in Computational Psychiatry** | [مقاله](https://doi.org/10.5334/cpsy.116)، [داده Zenodo](https://doi.org/10.5281/zenodo.10663643)، [کد اصلی](https://gitlab.ethz.ch/tnu/code/hessetal_spirl_analysis) | داده و کد دارای مجوز روشن و دریافت‌شده؛ HGF7.1/TAPAS6.0.1، MATLAB R2019b؛ هفت combined-response model و eHGF سفارشی. بازتولید کامل مساوی کاربرد سادهٔ binary نیست. اول semantic audit، سپس common-scope application؛ حذف RT از تحلیل باید «تحلیل محدود جدید روی دادهٔ منتشرشده» نامیده شود، نه بازتولید مقاله. |
| **Lacombe-Thibault & Coll, 2025 — Expectations and uncertainty shape pain perception during learning** | [مقاله](https://doi.org/10.1016/j.jpain.2025.105569)، [GitHub](https://github.com/meganel-t/painuncertainty) | MATLAB fitting، دادهٔ raw و preprocessing موجود؛ responseهای سفارشی logRT و eHGF دو/سه‌سطحی؛ root license یافت نشد. مناسب fallback پس از mapping و بررسی مجوز؛ مقاله/داده بدون مجوز مستقل بازنشر نمی‌شود. |
| **Henco et al., 2020 — Aberrant computational mechanisms of social learning and decision-making in schizophrenia and borderline personality disorder** | [مقاله PLOS](https://doi.org/10.1371/journal.pcbi.1008162)، [OSF](https://osf.io/8kfph/)، `Patient_Study.zip` و README در API واقعی فهرست شدند | دادهٔ **processed** و کد عمومی است؛ مقاله صریحاً اشتراک raw فردی را محدود می‌کند. پردازش‌شده را raw ننامید. مدل اجتماعی دو stream و مجوز OSF نامشخص؛ کاندید توسعهٔ بعدی، نه پیش‌شرط مقالهٔ 1.0. |
| **Gao et al., 2024 — Enhanced “learning to learn” through a hierarchical dual-learning system: the case of action video game players** | [مقاله ناشر](https://doi.org/10.1186/s40359-024-01952-x)، [مخزن اعلام‌شده](https://osf.io/sk82r/) | مقاله کد و داده را اعلام کرده، ولی API پروژه در بررسی حاضر 401 داد. فعلاً **دسترسی عملی تأییدنشده**؛ در شمار منابع آماده قرار نگیرد. |

## چرا این انتخاب‌ها؟

Arthur کاربرد sensorimotor را نشان می‌دهد و Hess یک workflow آماری مستند با choice و RT فراهم می‌کند. این تنوع برای مقاله مفید است، اما مدل‌های اختصاصی‌شان می‌توانند هزینهٔ انتقال را بالا ببرند. آزمون امکان‌سنجی باید پیش از وعدهٔ دو بازتولید موفق انجام شود. اگر تنها یک مورد بدون توسعهٔ هسته پشتیبانی شد، یک مطالعهٔ واقعی کامل به‌همراه دموهای رسمی بهتر از ادعای دو replication ناقص است.

## فایل‌های موجود و سیاست بازتوزیع

- `spirl_2025/data/`: هر پنج فایل deposit نسخهٔ مشخص Zenodo؛ دو MAT، دو JSON و راهنمای داده. **CC BY 4.0**؛ نسخهٔ public دادهٔ preprocessed شامل 20 pilot و 59 main در نام فایل‌ها است، نه تمام شرکت‌کنندگان جذب‌شده. ورودی‌ها بدون تغییر نگهداری می‌شوند.
- `spirl_2025/upstream_source.zip`: snapshot اصلی GPL از commit ثبت‌شده در manifest؛ submoduleها داخل zip نیستند. `UPSTREAM_LICENSE` و README اصلی کنار آن حفظ می‌شوند. این archive مرجع مستقل است؛ مجوز MIT ریشه به آن اعمال نمی‌شود و کد GPL به `src/hgfx` منتقل نشده است.
- PDFهای دریافت‌شده در پوشهٔ هر مقاله؛ هویت، مجوز، URL و SHA-256 در `acquisition_manifest.json`. وضعیت failed را دانلودشده حساب نکنید.
- متن کامل مقالهٔ SPIRL در `spirl_2025/paper.html` از صفحهٔ ناشر Reference Global دریافت شد؛ PDF آن در این جلسه در دسترس نبود. Arthur و Henco به‌صورت PDF اصلی دریافت شدند. HTML با PDF یکسان معرفی نمی‌شود.
- `local_only/`: فایل‌های عمومیِ دریافت‌شده برای بررسی محلی که اجازهٔ بازتوزیع‌شان روشن نیست؛ در `.gitignore` همین پوشه مستثنا هستند و push نمی‌شوند. manifest آدرس و hash را برای دریافت مستقل ثبت می‌کند. **از `git add -f` استفاده نکنید.**
- `citations.json` و `references.bib`: metadata DOI از Crossref؛ bibliography مقالهٔ HGFX هنوز با این منابع ترکیب نشده، چون case study اجرا نشده است.

مجوز مقاله را به کد یا dataset خارجی تعمیم ندهید. اصل noticeهای نویسندگان حفظ شود. raw دادهٔ محدودشده، پرسشنامهٔ تجاری و logهای دارای اطلاعات شخصی به repo عمومی اضافه نشوند. برای اجازهٔ نامشخص، نویسنده می‌تواند درخواست مجوز کند؛ هیچ ایمیلی در این کار ارسال نشده است.

## منابع نسخه‌شده و entry pointها

### SPIRL

- analysis commit: `86fd5122a744acfb5bc7ba12720426d8b4aa0ffa`.
- TAPAS submodule: `604c56843c15411f5bd80190f81d845ac57d8592`؛ VBA: `aa4657346cd0bda23e257bb576aa73a4c1598d52`؛ RainCloudPlots: `d5085be93a4bd835ce24d0205b23759c5e064f27`.
- ابتدا `utils/spirl_setup_model_space.m`، `utils/spirl_specs.m`، `hgf_extensions/`، `comb_obs_models/` و `job_runner_11_main_modinv.m` داخل archive خوانده شود.
- `nRandInit=399` و seed `rng(123,'twister')` در source مشاهده شد. توصیهٔ upstream برای کاهش multistart فقط اجرای آموزشی است؛ اگر آن را کاهش دادید، بازتولید دقیق مقاله ادعا نکنید.
- [پروتکل اصلی](https://doi.org/10.5281/zenodo.10669944) با dataset اشتباه نشود. pilot/main جدا بمانند؛ prior elicitation روی main تکرار نشود.

### Arthur

- Study1: `SWI_HGF_models.m`، `SWI_HGF_getparameters.m`، `param_recover.m`؛ Study2: `modelfitting_HGF_interception.m`، `getparams_HGF_interception.m`، `param_recover_interception.m`.
- OSF شامل پوشه‌های دادهٔ ASD/NT هر مطالعه و خروجی‌های آماری است. exact download URL و hashهای ارائه‌شدهٔ OSF در inventory نگهداری می‌شود.
- برش median، coding ورودی/پاسخ، ترتیب trial و انتخاب veridical/felt بخشی از مدل عملی‌اند؛ استفاده از CSV خروجی گروهی به‌جای trial data مجاز نیست.
- نسخهٔ دقیق toolbox و همهٔ custom configها باید از source احراز شوند؛ ارجاع مقاله به TAPAS به‌تنهایی pin نسخه نیست.
- **یافتهٔ مستقیم بعد از دانلود:** `modelfitting_HGF_interception.m` به `tapas_hgf_binary_config_david1` و `tapas_hgf_binary_config_david2` فراخوانی دارد؛ این دو فایل در inventory دریافت‌شدهٔ پوشه‌های Data/Code موجود نیستند. مسیرهای absolute سیستم نویسنده نیز hard-code شده‌اند. بنابراین این گزینه فعلاً **مشروط به بازیابی config اصلی از supplement یا منبع نویسنده** است؛ جایگزین‌کردن بی‌سروصدای default config ممنوع. دریافت ۱۲۸ فایل به معنی کامل‌بودن dependencyها نیست.
- منابع مستقیم بررسی تکمیلی: [جزئیات مدل](https://osf.io/download/naq9g/) و [priors و model checks مطالعهٔ دوم](https://osf.io/download/x5k9y/). وضعیت دریافت آنها در `arthur_2023/supplement_acquisition.json` ثبت می‌شود؛ وجود توضیح prior لزوماً همهٔ semantics فایل config غایب را تعیین نمی‌کند.

### گزینه‌های جایگزین

- Pain repository HEAD بررسی‌شده: `3f1d32aff73826a1385c359ca638ad0e11a7fda7`. entry points: `code/c01_import_and_plot_participant.py`، `code/c02_fit_models_painuncertainty.m`، `code/c03_compare_models_painuncertainty.m`، `code/models/tapas_logrt_linear_binary_hgf2*` و `...hgf3*`. API هم فایل‌های MATLAB و هم trial CSVهای `sourcedata/` را نشان داد؛ مقاله availability را تأیید می‌کند. تمام فایل‌های بزرگ/پرسشنامه‌ها mirror نشده‌اند.
- Henco OSF file: `s3vwq` / `Patient_Study.zip`، 29,800,222 bytes، SHA-256 اعلام‌شده `7d2797c91db58a642cf73fc45c2b8e4d3bb92d2d85044fd3c72d67c884bd0d8c`. download/inspection با اجرای موفق تحلیل فرق دارد.
- Suthaharan COVID/paranoia نیز غربال شد: [repo](https://github.com/psuthaharan/covid19paranoia)، SHA `c618e032228fb4ed03821f11bdc57af608695631`، choice MAT و configهای `hgf_ar1_binary_mab` موجود؛ HGF5.3.1 و مجوز root نامشخص. چون نیاز به MAB/version mapping و بررسی بیشتر دارد، در دو انتخاب اول نیست.
- Powers/ModelDB229278: بعضی MATها فقط حدود 180 bytes بودند؛ صرف وجود فایل داده برای ادعای dataset کامل کافی نیست. برای این بسته انتخاب نشد.

## روش جست‌وجو و حد قطعیت

این جست‌وجوی هدفمند منابع بازتولید است، نه systematic review یا PRISMA. پرسش‌های جست‌وجو در ۳ نوامبر ۲۰۲۶ شامل `hierarchical Gaussian filter MATLAB data code github`، `hierarchical Gaussian filter code availability`، `HGF data github Diaconescu` و `hierarchical Gaussian filter data and code` بود. پس از discovery، صفحهٔ ناشر/PMC، DOI/Crossref و file API خود GitHub/OSF/Zenodo یا Git بررسی شد. search snippet به‌تنهایی برای دانلود/مجوز یا eligibility کافی شمرده نشد.

محدودیت‌ها: OSF sk82r و 3bk7e با 401 قابل دریافت نبودند؛ بعضی endpointهای وب ETH GitLab پاسخ HTML ضدربات می‌دادند اما Git clone عادی موفق شد. وجود مدل پاسخ custom، نبود license و اختلاف نسخه به‌عنوان مانع واقعی ثبت شده‌اند. هیچ نتیجهٔ موفق برای انتخاب مطالعه پیش‌فرض گرفته نشده است.
