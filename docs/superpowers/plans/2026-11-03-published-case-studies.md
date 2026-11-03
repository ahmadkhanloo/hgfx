# Published MATLAB HGF studies → HGFX: execution addendum

**وضعیت:** انتخاب منبع و دریافت فایل؛ بازتولید هنوز اجرا نشده. این ضمیمه مرحلهٔ ۳ پلن انتشار را گسترش می‌دهد، نه نتایج علمی frozen را.

**ورودی اصلی:** `paper/case_studies/README_FA.md`، `acquisition_manifest.json`، `references.bib` و منابع نسخه‌شده. **هدف:** یک یا دو worked case study با دادهٔ واقعی منتشرشده و مقایسهٔ قابل ممیزی با MATLAB، بدون ادعای بازتولید کامل در صورت تغییر مدل/نسخه/تحلیل.

## انتخاب از پیش و شرط ورود

ترتیب بررسی بر اساس دسترسی و دامنه، پیش از دیدن خروجی HGFX:

1. **Arthur 2023، Study2 interception**: کاربرد sensorimotor؛ MATLAB scripts و data folders در OSF مشاهده شدند. اول همین مطالعه، نه HGF4 مطالعهٔ اول. نسخه، config، preprocessing، مجوز و trial inputs هنوز باید احراز شوند.
2. **Hess 2025، SPIRL**: بستهٔ دارای مجوز روشن، دادهٔ pilot20/main59 و source snapshot موجود. فقط common-scope‌ای که با audit سازگار است؛ هفت مدل joint choice/RT و eHGF سفارشی به‌طور پیش‌فرض قابلیت 1.0 فرض نشوند.
3. **Pain 2025** fallback: اگر گزینهٔ اول به دلیل نقص دسترسی/مدل غیرقابل اجرا بود؛ دلیل جایگزینی پیش از fit ثبت شود. custom logRT پاسخ باید بررسی شود.
4. Henco2020 و Gao2024 برای آینده/ذخیره؛ اولی raw محدودشده و مدل دو-stream دارد، دومی دسترسی عملی OSF فعلاً تأیید نشده است.

بودجهٔ feasibility هر گزینهٔ اصلی حداکثر یک روز کاری. شکست نتیجه یا ناسازگاری عددی دلیل حذف مطالعه نیست؛ نبود ورودی لازم، مدل خارج دامنه یا نبود مرجع نسخه‌شده دلیل مستند توقف است. اگر تنها یک مورد واجد شرایط بود، یک case واقعی کامل + دموهای frozen تحویل بده؛ به‌قیمت توسعهٔ هسته تعداد مطالعه‌ها را افزایش نده.

## مرحله C1 — inventory و semantic audit، بدون fit

- [ ] `AGENTS.md` و اسناد الزامی آن خوانده شود. ورودی‌های دانلودشده با manifest و checksum ناشر کنترل شوند؛ PDFهای HTML یا zip خراب منبع معتبر نیستند.
- [ ] `paper/case_studies/<study>/FEASIBILITY.md` بساز: DOI، source commit، toolbox version، MATLAB version، entry point، input path، subject/trial counts، exclusions، response coding، missing/irregular trials و preprocessing. موارد نامعلوم explicit باشند.
- [ ] برای Arthur `modelfitting_HGF_interception.m` و `getparams_HGF_interception.m` را باز کن؛ فایل‌های ASD/NT لازم را به inputs و responses واقعی map کن. Study1 مدل HGF4 دارد؛ آن را سه‌سطحی نکن. summary parameter CSV جای trial data نیست.
- [ ] مانع مشخص Arthur: دو config فراخوانی‌شدهٔ `tapas_hgf_binary_config_david1` و `tapas_hgf_binary_config_david2` در inventory Data/Code نیستند. ابتدا supplement را بررسی کن؛ اگر exact definition پیدا نشد، `BLOCKED_MISSING_ORIGINAL_CONFIG` ثبت کن. بازسازی حدسی یا default جدید replication اصلی نیست. اصلاح absolute path فقط adaptation اجرایی مستند است.
- [ ] برای SPIRL archive را خارج `src/` باز کن؛ source GPL و noticeها مستقل بمانند. `utils/spirl_setup_model_space.m`، `utils/spirl_specs.m`، `hgf_extensions/` و `comb_obs_models/` بررسی شوند. کد GPL را در HGFX MIT کپی/ترجمه نکن.
- [ ] table مدل/پارامتر بنویس: مدل مقاله، معادل frozen MATLAB8.2، معادل HGFX1.0، semantics، evidence و وضعیت exact/changed/unsupported. API با نام مشابه اثبات معادل‌بودن نیست.
- [ ] مجوز paper/data/code جدا؛ فایل local_only تنها برای بررسی محلی است و force-add نشود. فقدان مجوز redistribution مانع انتشار فایل upstream است؛ می‌توان دستور دریافت مستقیم ارائه کرد، مشروط به شرایط استفادهٔ منبع.

**Acceptance:** تصمیم `ELIGIBLE_FOR_PROTOCOL` یا `BLOCKED_<specific reason>` برای هر مطالعه با شاهد. Downloaded را eligible ننام. پیش از این تصمیم fit انبوه اجرا نکن.

## مرحله C2 — قرارداد بازتولید پیش از اجرا

- [ ] `paper/case_studies/<study>/REPLICATION_PROTOCOL.md` بنویس و commit کن: مدل‌ها، همهٔ subjects واجد شرایط طبق قواعد اصلی، exclusions اصلی، inputs/hashes، priors، parameter transforms/order، starts و RNG، optimizer budget و metricهای مقایسه. نسخهٔ فایل input قفل شود.
- [ ] سه سطح ادعا جدا باشد: **A** اجرای مجدد کد اصلی با نسخهٔ اصلی؛ **B** انتقال مستند همان دامنه به oracle8.2؛ **C** مقایسهٔ HGFX1.0 با B. اگر A ممکن نیست، «بازتولید دقیق نتیجهٔ مقاله» ممنوع؛ B/C فقط application/portability example است.
- [ ] معیارها از سیاست و fixtures موجودِ مدل مربوط تعیین شوند؛ معیار واحد برای trajectory/objective/پارامتر/Hessian/BIC نساز. کمیتی که معیار معتبر ندارد توصیفی و بدون PASS گزارش شود. هیچ tolerance پس از دیدن خروجی تنظیم نشود.
- [ ] smoke sample صرفاً اولین subject بر اساس شناسهٔ مرتب و قواعد اصلی؛ برای نتیجهٔ مقاله همهٔ subjects واجد شرایط پردازش شوند، موارد fail/NaN در denominator بمانند. براساس کیفیت fit نمونه انتخاب نشود.
- [ ] در SPIRL pilot و main تفکیک؛ prior اصلی حفظ؛ هیچ tuning روی main. کاهش `nRandInit=399` یا حذف RT فقط با برچسب demonstration متفاوت؛ نه replication کامل. RNGهای یک seed در MATLAB/Python لزوماً یکسان نیستند؛ starts/draws واقعی برای paired comparison export شوند.
- [ ] خروجی جدید صرفاً `paper/case_studies/<study>/results/<run_id>/`؛ نتایج release، recovery و P3 overwrite نشوند. research associations تازه، recovery تازه و بازتفسیر بالینی خارج دامنه است.

**Acceptance:** protocol قبل از fit commit شده و از نظر ورودی و scope کامل است. اگر لازمهٔ کار توسعهٔ مدل تازه است، gap را ثبت و این case را متوقف کن؛ به‌طور پنهان آن را داخل بازنویسی مقاله پیاده‌سازی نکن.

## مرحله C3 — اجرای محدود و سپس دامنهٔ قفل‌شده

- [ ] محیط MATLAB نسخهٔ اصلی و oracle8.2 جدا باشد؛ `which`، نسخه و SHA ثبت شود. اگر MATLAB در دسترس نیست، نبود آن گزارش شود؛ خروجی HGFX را با خروجی مرجع ساختگی مقایسه نکن.
- [ ] HGFX فقط wheel1.0.0 در محیط تمیز خارج checkout، CPU x64؛ log نسخه و module path. ابتدا smoke یک subject، سپس تمام scope قفل‌شده بدون تغییر روش.
- [ ] exporter/adapter مخصوص case در `paper/case_studies/<study>/scripts/` ایجاد شود. پیش از adapter، test مشخص برای trial alignment، missing masks، coding و parameter order با یک fixture واقعی بنویس. reference original files immutable بمانند.
- [ ] ثبت per-subject input، model/config، starts، fit exit status، objective، BIC/LME در صورت قابل مقایسه، و trajectoryهای مربوط. failureها به‌صورت داده در summary باشند.
- [ ] در mismatch، اولین trial/level/state/intermediate divergent پیدا شود. تفاوت نسخه، objective، transform یا optimizer بررسی شود؛ clip/retry/tolerance inflation برای رسیدن به PASS ممنوع.
- [ ] runtime/CPU زمان صرفاً برای قابلیت اجرا ثبت شود، نه headline speedup. هیچ اجرای GPU لازم نیست.

**Acceptance:** نتیجهٔ همهٔ موارد، از جمله fail، ثبت شده؛ اجرای موفق code با صحت علمی یکی نشده؛ هر gate فقط در دامنهٔ تعریف‌شده ارزیابی شود.

## مرحله C4 — نمایش در مقاله و بستهٔ مستقل

- [ ] برای هر case یک صفحه walkthrough انگلیسی: پرسش اصلی مقاله، دادهٔ واقعاً استفاده‌شده، کد MATLAB/Python کوتاه کنار هم، مراحل اجرا و مرز ادعا.
- [ ] شکل: ورودی/response، trajectories دو implementation، residual واقعی؛ histogram/جدول اختلاف per-subject، تعداد success/fail و denominator کامل. correlation تنها معیار توافق نباشد. شکل انتخابی فقط از subject قفل‌شده باشد.
- [ ] نسخه‌های paper/data/code و تغییرات بین A/B/C را در caption/table ذکر کن. «دقت در بازتولید reference» از prediction accuracy و scientific validity جدا باشد.
- [ ] در `paper/computational_statistics/manuscript.md` بخش worked case studies و limitations اضافه کن؛ تا قبل از اجرا هیچ نتیجه/شکل موفقی نوشته نشود. references لازم از bibliography این پوشه منتقل و بررسی شود.
- [ ] artifact جدید، checksumها، commands، environment و status در manifest جدا؛ build/render مقاله و تمام کنترل‌های plan اصلی تکرار شوند.
- [ ] فقط فایل مجاز برای redistribution commit/push شود؛ برای بقیه source URL، hash و دستور دریافت. هیچ upstream license با MIT ریشه جایگزین نشود.

**Definition of done:** حداقل یک case end-to-end قابل بررسی یا blocker دقیق برای تمام گزینه‌های ازپیش‌مشخص‌شده؛ هیچ وعدهٔ موفقیت لازم نیست. هدف دو مطالعه است، نه دستکاری برای دو PASS. آماده‌بودن مقاله همچنان نیازمند author review و preflight مالی است.

**برآورد:** ۲ روز feasibility؛ در صورت سازگاری، ۳–۵ روز برای هر case + compute/MATLAB availability. پروژهٔ انتشار با این افزودن احتمالاً چند هفته می‌شود؛ ۵–۱۰ روز پلن اولیه شامل انتقال کامل مطالعات جدید نبود.
