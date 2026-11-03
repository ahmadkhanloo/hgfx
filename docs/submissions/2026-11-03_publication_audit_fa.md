# ممیزی مستقل راهبرد انتشار HGFX

**تاریخ بررسی: ۳ نوامبر ۲۰۲۶ — گزارش مشورتی برای نویسنده، نه تصمیم تحریریه یا داوری رسمی مجله.**

**تصمیم پیشنهادی: راهبرد B؛ بازنویسی مقاله به‌صورت software/package paper و سپس ارسال به Computational Statistics از مسیر subscription.** توسعهٔ گستردهٔ نرم‌افزار یا اجرای دوبارهٔ آزمایش‌های شکست‌خورده، پیش‌شرط این مسیر نیست. شرط مالی ارسال، صفر بودن تمام هزینه‌های اجباری است؛ جزئیات و حد تأیید این شرط در بخش‌های ۳ و ۴ آمده است.

## بخش ۱ — رأی اجرایی

| پرسش | پاسخ ممیزی |
|---|---|
| آیا HGFX قابل انتشار است؟ | **بله، به‌عنوان نرم‌افزار پژوهشی با سازگاری محدود و مستند با MATLAB.** شواهد فعلی برای ادعای اعتبار علمی عمومی مدل، بازیابی قابل‌اعتماد پارامترها یا برتری سرعت کافی نیست. متن فعلی را بدون بازنویسی ارسال نکنید. |
| محتمل‌ترین دستهٔ مشکل ارسال‌های ناموفق چیست؟ | **تناسب نوع مقاله، روایت ارزش افزوده و مخاطب مجله.** این استنباط از محتوای مقاله است، نه کشف علت قطعی تصمیم‌های سردبیری. |
| آیا کد الزاماً باید اصلاح شود؟ | نقص تازه و قطعی در هستهٔ علمی که ارسال محدودشده را متوقف کند، در این ممیزی شناسایی نشد. اختلاف‌های حل‌نشدهٔ آزمایش P3 واقعی‌اند؛ علت آن‌ها را نمی‌توان بدون تشخیص بیشتر «اشکال قطعی کد» نامید. |
| آیا مقاله ضعف اصلی است؟ | مهم‌ترین ضعف قابل‌اصلاح در کوتاه‌مدت، مقاله و بستهٔ بازتولید است: گزارش داخلی validation بر مسئلهٔ کاربردی، توضیح روش و نمونهٔ استفاده غلبه دارد. این به معنای نادرستی نتایج نیست. |
| ارسال اکنون، بازنویسی، اعتبارسنجی یا انتظار؟ | **بازنویسی نخست؛ کنترل محدود نصب و بازتولید؛ سپس ارسال.** انتظار منفعل برای JOSS توصیه نمی‌شود. |

مقاله در حال حاضر «توصیف نرم‌افزار همراه با مطالعهٔ سازگاری عددی» است. خود متن تصریح می‌کند مدل مولد تازه یا مجموعه‌دادهٔ رفتاری/تصویربرداری تازه معرفی نمی‌کند. بنابراین عرضهٔ آن به‌صورت کشف جدید علوم اعصاب یا پیشرفت عمومی در identifiability، با شواهد آن تناسب ندارد. [متن بررسی‌شده، بخش‌های ۱، ۲٫۲ و ۴](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/paper/manuscript.md)

**سه انتخاب اصلی:** Computational Statistics برای ارسال نزدیک؛ Behavior Research Methods برای نسخه‌ای با کاربرد رفتاری روشن‌تر؛ Journal of Statistical Software برای مقالهٔ نرم‌افزاری مفصل‌تر با بازتولید سخت‌گیرانه‌تر. JOSS گزینهٔ بلندمدت است.

## بخش ۲ — تشخیص مبتنی بر شواهد

### ۲٫۱ دامنه و وضعیت واقعی مخزن

اطلاعات زیر در همین بررسی از Git remote، GitHub API، PyPI و فایل‌های محلی تطبیق داده شد:

| موضوع | وضعیت |
|---|---|
| HEAD محلی و main راه دور | `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`؛ فرض قبلی هنوز درست است. |
| نسخهٔ منتشرشده | GitHub و PyPI فقط stable `1.0.0` را نشان دادند؛ انتشار GitHub در ۱۶ سپتامبر ۲۰۲۶. |
| SHA محصول ۱٫۰ | `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| main | metadata برابر `1.1.0b1`؛ شامل امکانات افزودهٔ بتا و معادل wheel منتشرشده نیست. |
| MATLAB oracle | HGF Toolbox `8.2.0`، SHA برابر `2437f4dc241541072722a2695ddeca7b44d83dd3` |
| شاخهٔ JOSS | `docs/joss-readiness-2026-11` در `123d76562fba185b4f237909b4b61ff20b96f064` |
| شاخهٔ انتقال | `docs/brain-informatics-transfer-2026-10` در `e66b634b17c60c2136150c6d313a8d907a8e38d6` |
| CI روی main | [Regression 36315504844](https://github.com/ahmadkhanloo/hgfx/actions/runs/36315504844) و [P2 Tables 36315504839](https://github.com/ahmadkhanloo/hgfx/actions/runs/36315504839) با نتیجهٔ success مشاهده شد. |
| مسائل باز | #81 برای JOSS، #56 برای beta و #32 برای مقاله؛ چند PR قدیمیِ بسته‌های ارسال نیز هنوز بازند. شمار open issues شامل PRهاست و معیار شمار نقص نرم‌افزار نیست. |

منابع محصول: [release ثابت](https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0)، [PyPI](https://pypi.org/project/hgfx/1.0.0/)، [تنظیمات package](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/pyproject.toml)، [issue 81](https://github.com/ahmadkhanloo/hgfx/issues/81).

تغییرات قبلی کاربر در `.gitignore` و پوشه‌های untracked به حال خود باقی ماند. در کد، نتایج، معیارها، مقاله یا تاریخچهٔ Git تغییری ایجاد نشد. این گزارش خارج از مخزن ذخیره شد.

### ۲٫۲ چه چیزهایی واقعاً بررسی و اجرا شد؟

README، مقالهٔ اصلی، ضمائم، بستهٔ reproducibility، جدول‌ها، هر شش شکل، اسناد برنامه‌ریزی/معماری/پذیرش، انتخابی از API و تنظیمات بسته، workflow رگرسیون، سوابق review و شاخه‌های ارسال بررسی شد. پیش‌نویس JOSS و bibliography آن نیز خوانده شد. نسخهٔ Neuroinformatics در شاخهٔ خودش موجود است؛ وجود فایل، اثبات یکسان بودن آن با فایل واقعاً ارسال‌شده نیست.

دو کنترل تازه:

```powershell
$env:JAX_ENABLE_X64='1'
$env:JAX_PLATFORMS='cpu'
.venv/Scripts/python.exe -m pytest -q tests/paper/test_p2_tables.py tests/paper/test_p3_evidence.py tests/paper/test_p6a_claim_audit.py tests/paper/test_p6a_manifest.py
# 14 passed in 35.98s
.venv/Scripts/python.exe scripts/verify_reference_freeze.py
# PASS; matlab_files=334; frozen commit matches
```

این‌ها آزمون‌های انتخابیِ شواهد و یکپارچگی‌اند؛ **بازاجرای کامل آزمایش علمی، نصب تازه از wheel، MATLAB، GPU یا اندازه‌گیری پوشش کد انجام نشد.** گزارش‌های تاریخی و CI زنده جای این ادعاها را نمی‌گیرند. ممیزی خط‌به‌خط تمام معادلات نیز انجام نشده است.

### ۲٫۳ نقاط قوت تأییدشده

- هویت مرجع ثابت، versioning، license و provenance روشن است؛ استفادهٔ معمول از package به MATLAB وابسته نیست.
- API عمومی برای fitting، simulation و sampling وجود دارد؛ نام‌های Python و MATLAB-style کنار هم عرضه شده‌اند. مستندات کاربر و مثال‌های رسمی موجودند؛ بنابراین پیشنهاد «ساخت مستندات از صفر» توجیه ندارد.
- workflow رگرسیون روی Ubuntu و Windows، با CPU و x64 تنظیم شده است. نصب عمومی و gateهای انتشار سوابق جداگانه دارند.
- دامنه‌های config/transform/prior، likelihood، fitting، Hessian و model comparison در شواهد مهاجرت تفکیک شده‌اند.
- شکست‌های علمی و نتیجه‌های NDC حفظ شده‌اند؛ مقاله عمدتاً از ادعاهای سرعت و برتری غیرمستند پرهیز می‌کند.
- منشأ اقتباس‌های fdlibm و مجوزهای ثالث ثبت شده است؛ وجود این noticeها مثبت است، هرچند ممیزی حقوقی کامل license انجام نشده است.

منابع: [API عمومی](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/src/hgfx/__init__.py)، [Regression workflow](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/.github/workflows/regression.yml)، [مثال‌ها](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/examples/README.md)، [مجوز و provenance ثالث](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/THIRD_PARTY_NOTICES.md).

### ۲٫۴ نقص‌های تأییدشده و محدودیت‌های علمی

**نقص مستندسازی تأییدشده:** `paper/reproducibility/README.md` هنوز manifest را `DRAFT_NOT_FROZEN` می‌خواند؛ خود JSON برابر `FROZEN_FOR_SUBMISSION` است. `P8_REVIEW_PACKET.md` می‌گوید round 3 هنوز PASS نشده، ولی `PAPER_P8_REVIEW_CHECKLIST.md` رکورد round-3 PASS و freeze را دارد. `PAPER_EVIDENCE_MAP.md` نیز وضعیت قدیمی P6A–P8 را نمایش می‌دهد. این تناقض‌ها برای داور سردرگمی ایجاد می‌کنند، اما دلیلی برای بازکردن gate علمی بسته‌شده نیستند. [README بازتولید](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/paper/reproducibility/README.md)، [رکورد معتبر round 3](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/docs/research/PAPER_P8_REVIEW_CHECKLIST.md)

**نقص provenance تأییدشده:** اجرای تاریخی P3 نسخهٔ MATLAB را `latest` گرفته و شمارهٔ دقیق release را نگه نداشته است. بازتولید نمودار از aggregate ممکن است؛ بازتولید دقیق محیط تاریخی تضمین‌شده نیست. این محدودیت در README افشا شده؛ نباید شمارهٔ نسخه را حدس زد.

| شواهد | نتیجهٔ واقعی | نتیجه‌ای که مجاز نیست |
|---|---|---|
| paired S7 model selection | ۳۶/۳۶ برندهٔ BIC یکسان؛ balanced accuracy هر دو `0.583333333333` | «دقت تشخیص مدل ۱۰۰٪» یا عملکرد عمومی روی داده‌های واقعی |
| paired S7 parameter recovery | برای HGF/eHGF/uHGF، median r به‌ترتیب حدود ۰٫۲۰۳، ۰٫۴۶۲، ۰٫۳۸۱ و sRMSE حدود ۲٫۶۱۰، ۲٫۳۵۹، ۲٫۹۵۸؛ معیارهای recovery برآورده نشد | identifiability معتبر یا قابلیت استنباط فردی/بالینی |
| P3، run `35272347167` | ۲۴/۲۴ shard اجرا؛ ۱۰ اختلاف از ۷۲ برندهٔ BIC؛ `gate_pass=false` و `INSUFFICIENT_REFERENCE_EVIDENCE` | موفقیت با دادهٔ طولانی‌تر یا اثبات non-identifiability ساختاری |
| D02/D08 | محدودیت‌های عددی/حساسیت مرجع با `REFERENCE_LIMITATION_MATCH` | direct fitting parity یا موفقیت علمی |
| pyhgf cell `p2a9-binary-hgf-common-scope-001` | ۱۱ کمیت ادراکی در یک cell با ۱۲۸ trial سازگار؛ response NLL برابر NDC | برتری کلی HGFX یا هم‌ارزی کل دو package |
| T4، source `07b45a5…` | چهار fitting cell روی `cuda:0`؛ حداکثر objective gap برابر `1.4210854715202004e-14` با معیار `1e-7` | سرعت بیشتر، استفادهٔ همزمان از دو GPU، یا scaling عمومی |
| compatibility CPU در برابر JAX CPU | gap برابر `0.006783711260709424` با معیار مستقل `0.10` | یکی گرفتن این معیار با معیار `1e-7` مربوط به CPU/GPU |

منابع: [جدول S7](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/paper/tables/recovery_model_selection.md)، [طبقه‌بندی P3](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/docs/research/P3_M18C2_RESULT.md)، [گزارش pyhgf](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/docs/research/PYHGF_COMMON_SCOPE_NUMERICAL_RESULT.md)، [ضمائم S2–S5](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/paper/SUPPLEMENTARY_APPENDICES.md).

برچسب تشخیصی P3، یعنی `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`، در بخش ۲٫۶ مقالهٔ فعلی **وجود دارد**. گزارش تاریخی که نبودن آن را ایراد می‌گرفت، نباید به‌عنوان نقص فعلی تکرار شود. این برچسب وجود اختلاف را نشان می‌دهد؛ علت مکانیکی آن را تعیین نمی‌کند.

شواهد H100 هم موجود است: در source تاریخی `e6f1740…` آزمون واقعی دو GPU و residency ثبت شده؛ هم‌زمان هشدار دقت timing و بار مشترک سرور گزارش شده است. پس عبارت «هیچ شواهد multi-GPU وجود ندارد» نادرست است؛ تعمیم آن به speedup نسخهٔ مقاله نیز نادرست است. [گزارش H100](https://github.com/ahmadkhanloo/hgfx/blob/bbf17e9cf0d14d91bf44f50e307a0be55cbede02/docs/planning/M17_H100_GPU_EVIDENCE.md)

### ۲٫۵ ضعف مقاله و نمایش شواهد

۱. **مسئلهٔ کاربر زیر جزئیات اعتبارسنجی پنهان است.** Abstract و Introduction عمدتاً توضیح می‌دهند چه gateهایی گذرانده شده، ولی مسیر پژوهشگر از داده تا نتیجه را نشان نمی‌دهند. بخش ۳٫۶ با عنوان examples بیشتر توصیف محل مثال‌هاست تا یک worked example.

۲. **روش از نظر آموزشی کم‌توضیح است.** بخش ۲٫۲ به معادلات مرجع ارجاع می‌دهد؛ برای مخاطب آماری باید مدل سلسله‌مراتبی، observation model، پارامترهای آزاد/ثابت، prior، transformation و تابع هدف در یک روایت کوتاه و خودبسنده توضیح داده شوند.

۳. **نوآوری باید دقیق‌تر صورت‌بندی شود.** contribution مناسب، مهاجرت قابل‌ردیابی workflowهای HGF و حفظ semantics است؛ نه اولین Python HGF، الگوریتم تازه، یا GPU سریع‌تر. مقایسهٔ طراحی با MATLAB و pyhgf موجود است، اما بهتر است به یک جدول تصمیم کاربر تبدیل شود.

۴. **شکل ۳ دو مفهوم متفاوت را روی یک محور می‌گذارد.** balanced accuracy حدود ۰٫۵۸۳ و winner agreement برابر ۱، دو estimand متفاوت‌اند. دو پنل با برچسب روشن لازم است؛ خط threshold بازیابی مدل نباید بر agreement هم دلالت بصری پیدا کند. هیچ عددی عوض نشود.

۵. **شکل‌های ۱، ۵ و ۶ اصطلاحات داخلی طولانی دارند.** شش تصویر بررسی شدند؛ عنوان‌های سنگین، فضای زیاد و شناسه‌های داخلی ارزش آموزشی را کم می‌کنند. Figure 5 همپوشانی مسیرها را خوب نشان می‌دهد، ولی یک residual inset از همان داده‌ها اختلاف عددی را روشن‌تر می‌کند. نتیجهٔ منفی P3 باید در متن بماند؛ نمایش کامل diagnostic می‌تواند با ارجاع برجسته در supplement باشد.

۶. **بحث به پیامد پژوهشی بیشتری نیاز دارد:** کاربر چه زمانی نباید پارامتر فردی را تفسیر کند؟ توافق BIC چه چیز را تضمین نمی‌کند؟ چگونه یک تحلیل قدیمی MATLAB را منتقل کند؟ چه زمانی pyhgf انتخاب مناسب‌تری است؟

۷. **AI review داخلی، peer review مستقل انسانی نیست.** رکوردهای Antigravity/Qoder شواهد کنترل داخلی‌اند و نباید به‌عنوان داوری دانشگاهی مجله معرفی شوند. round-3 PASS فقط به candidate خودش مربوط است؛ نسخهٔ بازنویسی‌شده باید بررسی نهایی جداگانه داشته باشد.

### ۲٫۶ سابقهٔ تصمیم‌ها، فرضیه‌ها و شواهد مفقود

| رویداد | آنچه قابل اتکاست | آنچه معلوم نیست |
|---|---|---|
| JNM، `JNEUMETH-D-26-01047` | رد شدن ۲۲ اکتبر؛ out-of-scope طبق اطلاعات نویسنده | اصل کامل نامه در مواد بررسی‌شده پیدا نشد؛ علت تفصیلی مستقلاً تأیید نشد. |
| Neuroinformatics، `b6d791b5-…` | رکورد رد و پیشنهاد انتقال در dossier وجود دارد | گزارش داور یا نقد علمی مشخص ارائه نشده؛ توصیهٔ انتقال پذیرش یا تأیید علمی نیست. |
| Brain Informatics، `a41d238b-…` | رد ۳ نوامبر در متن ارائه‌شده و رکورد جدید؛ نامه فاقد دلیل/گزارش داور است | مرحلهٔ دقیق رسیدگی و علت رد معلوم نیست. |

[پروندهٔ انتقال تاریخی](https://github.com/ahmadkhanloo/hgfx/blob/e66b634b17c60c2136150c6d313a8d907a8e38d6/docs/submissions/2026-10-31_brain_informatics_transfer.md) هنوز PREPARED می‌گوید؛ [پروندهٔ جدید](https://github.com/ahmadkhanloo/hgfx/blob/123d76562fba185b4f237909b4b61ff20b96f064/docs/submissions/2026-11-03_joss_readiness.md) رد شدن را ثبت کرده است. سند جدید برای وضعیت جاری مقدم است؛ تاریخ ارسال ۳۰ اکتبر و آماده‌سازی ۳۱ اکتبر نیز بدون رسید پورتال نباید بازسازی یا تصحیح حدسی شود.

فرضیهٔ معقول: incremental novelty و کمبود نمونهٔ کاربرد، ارزش سردبیری را کم کرده است. **هیچ شاهدی برای نسبت دادن سه رد به کد نادرست، تخلف، تحریم، یا شکست داوری خارجی وجود ندارد.** همچنین نبود کاربران بیرونیِ تأییدشده، اثبات نبودن همهٔ کاربران نیست.

شواهد مفقود: فایل نهایی و hash هر ارسال، نامه‌های کامل اصلی، usage مستقل قابل‌ارجاع، کنترل نصب توسط کاربر تازه، درصد پوشش آزمون، محیط دقیق MATLAB برای P3. DOI پیش‌چاپ در اسناد موجود است، ولی resolver آن در ابزار وب این بررسی باز نشد؛ فایل public preprint با نسخهٔ ارسال‌شده تطبیق داده نشد.

## بخش ۳ — مقایسهٔ مجلات و شرط مالی

### ۳٫۱ نتیجهٔ غربالگری

**۱۰ مجله بررسی شدند؛ هشت گزینهٔ هم‌زمان مناسب، قابل‌ارسال اکنون و با هزینهٔ صفر تأیید نشد.** افزایش مصنوعی فهرست با مجلات کم‌تناسب، به هدف پذیرش کمک نمی‌کند. سه گزینهٔ اول واقع‌بینانه‌ترند؛ JOSS شرط زمانی دارد؛ JMLR فعلاً از نظر community evidence ضعیف است؛ سه گزینهٔ OA بدون waiver قطعی کنار گذاشته شده‌اند.

رتبه‌ها قضاوت این ممیزی‌اند، نه نرخ پذیرش یا وعدهٔ نتیجه. هیچ احتمال عددی پذیرش ساخته نشده است.

| رتبه/وضعیت | مجله و ناشر | تناسب و نوع مقاله | سابقهٔ مشخص و ریسک اصلی | تغییر لازم |
|---|---|---|---|---|
| **۱، هدف اصلی** | **Computational Statistics — Springer Nature** | software article / package report صریحاً در scope؛ تناسب خوب با filtering، Bayesian computing و validation | [hermiter](https://link.springer.com/article/10.1007/s00180-023-01382-0)، نمونهٔ واقعی package paper؛ ریسک: بازپیاده‌سازی بدون فایدهٔ آماری روشن | توضیح ریاضی مختصر، مثال end-to-end، مقایسهٔ ابزارها و حدود inference |
| **۲** | **Behavior Research Methods — Springer Nature / Psychonomic Society** | Original Research یا Tutorial؛ ابزار پژوهش رفتاری | [dynConfiR](https://link.springer.com/article/10.3758/s13428-026-03013-0)؛ ریسک: parity بدون مسئلهٔ رفتاری/کاربرد آموزشی کافی | بازنویسی بیشتر برای کاربر روان‌شناسی و worked example روشن |
| **۳** | **Journal of Statistical Software — Foundation for Open Access Statistics** | مقالهٔ نرم‌افزار آماری؛ Python پذیرفته است | [PyMC](https://www.jstatsoft.org/article/view/v035i04)؛ ریسک: novelty و الزامات مفصل بازتولید، قالب و مخاطب گسترده‌تر | مقالهٔ LaTeX آموزشی، کد نمونه و replication script یکپارچه |
| **۴، بلندمدت** | **Journal of Open Source Software — Open Journals** | software paper؛ تناسب موضوعی بسیار خوب | [ArviZ](https://joss.theoj.org/papers/10.21105/joss.01143)؛ فعلاً مانع قطعی سابقهٔ عمومی | توسعهٔ واقعی در طول زمان، evidence پژوهشی و مقالهٔ JOSS کامل |
| **۵** | **Computational Brain & Behavior — Springer Nature / Society for Mathematical Psychology** | Research؛ سابقهٔ مقالهٔ tutorial با نرم‌افزار | [آموزش RL و HDDM](https://link.springer.com/article/10.1007/s42113-020-00084-w)؛ ریسک: نبود insight دربارهٔ شناخت/رفتار | محور کردن تحلیل و کاربرد شناختی، نه inventory تست‌ها |
| **۶، کم‌اولویت** | **Biological Cybernetics — Springer Nature** | Research/Brief Report؛ scope نظری و کاربردی زیستی | [setup محاسباتی ethology](https://link.springer.com/article/10.1007/s00422-021-00886-6) نمونهٔ مجاور، نه معادل HGF software paper؛ ریسک scope/novelty زیاد | نیاز به ارزش روش‌شناختی زیستی مشخص؛ صرفاً عوض کردن عنوان کافی نیست |
| **۷، فعلاً توصیه نمی‌شود** | **Journal of Machine Learning Research، مسیر MLOSS — JMLR** | مقالهٔ کوتاه نرم‌افزار ML | [scikit-learn](https://www.jmlr.org/papers/v12/pedregosa11a.html)؛ scope عمومی inference ممکن، ولی active user community باید مستند شود | شواهد استفاده و contribution عمومی‌تر؛ نباید برای این مجله feature مصنوعی ساخت |
| **خارج از فهرست صفرهزینهٔ فعلی** | **SoftwareX — Elsevier** | Original Software Publication / Software Update؛ تناسب موضوعی خوب | وجود مسیر اختصاصی software از ناشر تأیید شد؛ دسترسی مستقیم به صفحات ScienceDirect و مقالهٔ مقایسه‌ای در این بررسی مسدود بود | فقط پس از waiver کامل مکتوب؛ قالب نرم‌افزاری و use case |
| **خارج از فهرست صفرهزینهٔ فعلی** | **Journal of Open Research Software — Ubiquity Press** | Software Metapaper؛ همچنین Issues in Research Software | [bayesint](https://openresearchsoftware.metajnl.com/articles/283/files/submission/proof/283-1-5629-2-10-20211221.pdf)؛ تناسب خوب ولی APC اجباری بدون waiver | فقط پس از waiver کامل؛ metadata، reuse و quality control |
| **خارج از فهرست صفرهزینهٔ فعلی** | **Statistics and Computing — Springer Nature** | Original Paper در محاسبات آماری؛ نوآوری روش مهم‌تر است | [prior/likelihood sensitivity](https://link.springer.com/article/10.1007/s11222-023-10366-5)، نمونهٔ روش همراه نرم‌افزار، نه precedent نزدیک package parity؛ ریسک مالی و novelty | ارسال تازه مشمول سیاست OA است؛ بدون waiver کامل کنار گذاشته شود |

دلیل انتخاب رتبهٔ اول بر BRM: [scope رسمی Computational Statistics](https://link.springer.com/journal/180/aims-and-scope) صریحاً software article و package report را می‌پذیرد. HGFX برای آن نیاز ندارد کشف تازهٔ علوم اعصاب را وانمود کند. [راهنمای BRM](https://link.springer.com/journal/13428/submission-guidelines) نیز ابزار و Tutorial را می‌پذیرد، اما اتصال به کاربرد رفتاری باید قوی‌تر شود. JSS از نظر نوع مقاله بسیار مناسب است، ولی [الزامات بازتولید و آماده‌سازی](https://www.jstatsoft.org/guides/submission) سنگین‌تر و زمان انتشار بالقوه طولانی‌تر است.

### ۳٫۲ هزینه‌ها و لینک‌های رسمی

**تعریف جدول:** «مسیر صفر تأییدشده» یعنی publisher صریحاً subscription بدون APC یا no-author-fees دارد، با کنارگذاشتن خدمات اختیاری. برای چهار hybrid زیر، تعرفهٔ اجباری ارسال/صفحه در راهنمای بررسی‌شده پیدا نشد؛ این با داشتن تأییدیهٔ مکتوبِ اختصاصی IPM برای تمام اقلام یکی نیست. هیچ waiver یا قرارداد پوشش هزینهٔ IPM فرض نشده است.

| مجله؛ صفحهٔ رسمی | هزینهٔ ارسال | APC و هزینه‌های دیگر | آیا €0 ممکن است؟ | راهنمای نویسنده |
|---|---|---|---|---|
| [Computational Statistics](https://link.springer.com/journal/180) | تعرفه اعلام نشده؛ عبارت مستقل صفرِ submission fee پیدا نشد | [subscription: بدون APC؛ OA اختیاری €2790](https://link.springer.com/journal/180/how-to-publish-with-us). رنگ آنلاین رایگان؛ رنگ چاپی می‌تواند هزینه داشته باشد | **بله، مسیر subscription بدون خدمات پولی؛ کنترل نهایی تمام هزینه‌ها لازم** | [Guidelines](https://link.springer.com/journal/180/submission-guidelines) |
| [BRM](https://link.springer.com/journal/13428) | تعرفه اعلام نشده؛ تصریح مستقل جداگانه پیدا نشد | [subscription: بدون APC؛ OA اختیاری €3090](https://link.springer.com/journal/13428/how-to-publish-with-us). مجله الکترونیکی و رنگ رایگان است | **بله، مسیر subscription**؛ نبود هزینهٔ اجباری اضافی در پروندهٔ نهایی کنترل شود | [Guidelines، از جمله Color Figures](https://link.springer.com/journal/13428/submission-guidelines) |
| [JSS](https://www.jstatsoft.org/) | صفر | no author fees؛ APC، صفحه و publication fee صفر؛ عضویت/کمک مالی شرط چاپ نیست | **بله؛ روشن‌ترین سیاست عمومیِ تماماً رایگان** | [Submission guide](https://www.jstatsoft.org/guides/submission) |
| [JOSS](https://joss.theoj.org/) | صفر | submission/publication fees صفر | **بله از نظر مالی؛ خیر برای ارسال امروز از نظر eligibility** | [Requirements](https://joss.readthedocs.io/en/latest/submitting.html) |
| [CBB](https://link.springer.com/journal/42113) | تعرفه اعلام نشده؛ تصریح مستقل پیدا نشد | [subscription بدون APC؛ OA اختیاری €2790](https://link.springer.com/journal/42113/how-to-publish-with-us)؛ رنگ آنلاین رایگان، رنگ چاپی پولی | **بله با subscription و بدون رنگ چاپی پولی** | [Guidelines](https://link.springer.com/journal/42113/submission-guidelines) |
| [Biological Cybernetics](https://link.springer.com/journal/422) | تعرفه اعلام نشده؛ تصریح مستقل پیدا نشد | [subscription بدون APC؛ OA اختیاری €3090](https://link.springer.com/journal/422/how-to-publish-with-us)؛ رنگ چاپی و آنلاین رایگان | **بله از نظر مسیر مالی؛ اولویت علمی پایین** | [Guidelines](https://link.springer.com/journal/422/submission-guidelines) |
| [JMLR](https://www.jmlr.org/) | تعرفه‌ای در راهنمای ارسال اعلام نشده | no publication fees؛ دسترسی آزاد | **مسیر انتشار رایگان دارد؛ eligibility/community مشکل اصلی است** | [Author information](https://www.jmlr.org/author-info.html)، [MLOSS](https://jmlr.csail.mit.edu/mloss/mloss-info) |
| [SoftwareX](https://www.sciencedirect.com/journal/softwarex) | مستقلاً تأیید نشد | OA با APC؛ مبلغ جاری رسمی به‌علت 403 تأیید نشد. ارقام سایت‌های تجمیعی مبنا قرار نگرفت | **فقط مشروط به waiver کامل؛ اکنون تأیید نشده** | [Guide](https://www.sciencedirect.com/journal/softwarex/publish/guide-for-authors)، [ناشر](https://www-prod.elsevier.com/researcher/author/tools-and-resources/research-elements-journals) |
| [JORS](https://openresearchsoftware.metajnl.com/) | هزینهٔ جداگانه اعلام نشده | Metapaper: **£824**؛ Issues: **£891**؛ درخواست waiver هم‌زمان با submission و موافقت کتبی لازم است | **فقط مشروط به waiver کامل؛ اکنون تأیید نشده** | [Guidelines و تعرفه](https://openresearchsoftware.metajnl.com/about/submissions) |
| [Statistics and Computing](https://link.springer.com/journal/11222) | راهنمای قدیمی می‌گوید صفر؛ سیاست جدید APC دارد | صفحهٔ عمومی €2390 نشان می‌دهد، اما مبلغ قابل‌اعمال پس از transition باید تأیید شود | **برای ارسال امروز subscription رایگان قابل اتکا نیست** | [اطلاعیهٔ مقدم بر متن قدیمی](https://link.springer.com/journal/11222/aims-and-scope)، [Guidelines متعارض](https://link.springer.com/journal/11222/submission-guidelines) |

**تعارض مهم و قطعی:** Statistics and Computing اعلام کرده از ۱ ژانویهٔ ۲۰۲۷ fully OA می‌شود و **ارسال‌های دریافت‌شده از ۱ ژوئیهٔ ۲۰۲۶** در صورت پذیرش مشمول APC هستند. برچسب Hybrid و متن قدیمی no publication fee برای ارسال ۳ نوامبر کافی نیستند. این مجله توصیهٔ صفرهزینه نیست.

**ایران و IPM:** در [فهرست رسمی waiverهای Springer](https://www.springernature.com/gp/open-science/policies/journal-policies/apc-waiver-countries) ایران یافت نشد. hardship waiver موردی است و نبود grant تضمین دریافت آن نیست. [فرایند رسمی](https://support.springernature.com/en/support/solutions/articles/6000227580-apc-waivers-and-discounts) درخواست در زمان ارسال و تکمیل فرم را لازم می‌داند. مسیر subscription به waiver کشوری متکی نیست. مجاز بودن خدمت انتشار برای affiliation دقیق IPM و نویسنده، در این بررسی به‌صورت پرونده‌ای و مکتوب تأیید نشده است؛ هیچ رد قبلی نیز به تحریم نسبت داده نمی‌شود.

[سیاست Elsevier](https://www.elsevier.com/about/policies-and-standards/pricing) waiver موردی را تضمین نمی‌کند؛ در مدل قیمت‌گذاری کشوری درج‌شده، ایران در دستهٔ پرداخت ۴۵٪ APC است، نه صفر. این نرخ را هم بدون بررسی شمول journal به SoftwareX تعمیم نمی‌دهم. [سیاست انتشار و تحریم Elsevier](https://www-prod.elsevier.com/about/policies-and-standards/trade-sanctions) امکان انتشار برای نویسندگان ایرانی را تحت شرایط بیان می‌کند؛ این معادل waiver نیست.

### ۳٫۳ نمایه، JIF، quartile و زمان

اطلاعات Springer از صفحهٔ رسمی همان مجله است؛ نه تأیید مستقل اشتراک JCR. **quartile جاری JCR برای هیچ‌یک مستقلاً تأیید نشد** و از SJR یا شهرت مجله به Q1 تبدیل نشده است. «اولین تصمیم» شامل desk rejection است و زمان داوری خارجی یا پذیرش نیست.

| مجله | نمایهٔ قابل تأیید در منابع این بررسی | JIF | زمان قابل اتکا |
|---|---|---|---|
| Computational Statistics | ناشر: Scopus و SCIE | **۱٫۳، سال ۲۰۲۵** | median اولین تصمیم **۸ روز**؛ زمان پذیرش نامعلوم |
| BRM | ناشر: Scopus، SSCI، Medline، PsycINFO | **۵٫۱، ۲۰۲۵** | عدد جاری قابل اتکای review/publication پیدا نشد |
| JSS | [ISSN Portal](https://portal.issn.org/resource/issn/1548-7660): Scopus و WoS؛ [DOAJ](https://doaj.org/toc/1548-7660) | JIF جاری تأیید نشد | خود مجله تأخیر بالقوه را هشدار می‌دهد؛ عدد ۵۳ هفتهٔ DOAJ مبتنی بر رکورد قدیمی است و مبنای برنامه‌ریزی قرار نگیرد |
| JOSS | peer review و review عمومی تأیید شد؛ Scopus/WoS/JIF جاری در منبع رسمی این بررسی تأیید نشد | تأیید نشده | زمان تضمین‌شده‌ای ندارد؛ gate فعلی مقدم است |
| CBB | ناشر: Scopus، PsycINFO؛ WoS در فهرست مشاهده‌شده نبود | صفحهٔ رسمی عدد JIF نشان نداد | median اولین تصمیم **۱۲ روز** |
| Biological Cybernetics | ناشر: Scopus، SCIE و Medline | **۲٫۰، ۲۰۲۵** | median اولین تصمیم **۸ روز** |
| JMLR | نمایهٔ جاری از پایگاه مالک در این بررسی تأیید نشد؛ این به معنای فقدان نمایه نیست | تأیید نشده | زمان قابل اتکای اختصاصی MLOSS پیدا نشد |
| SoftwareX | [رکورد DOAJ](https://doaj.org/toc/2352-7110) یافت شد؛ وضعیت جاری Scopus/WoS مستقلاً کنترل نشد | تأیید نشده | ارقام غیررسمی استفاده نشد |
| JORS | [ناشر](https://openresearchsoftware.metajnl.com/about): Scopus و DOAJ؛ CiteScore با JIF یکی نیست | JIF تأیید نشده | تضمین قابل اتکا برای این پرونده نداریم |
| Statistics and Computing | ناشر: Scopus و SCIE | **۱٫۸، ۲۰۲۵** | median اولین تصمیم **۳ روز**؛ با وجود مانع مالی، مزیت تصمیم‌گیری نیست |

منابع اعداد: [CompStat](https://link.springer.com/journal/180)، [BRM](https://link.springer.com/journal/13428)، [CBB](https://link.springer.com/journal/42113)، [Biological Cybernetics](https://link.springer.com/journal/422)، [Statistics and Computing](https://link.springer.com/journal/11222).

## بخش ۴ — انتخاب نهایی و مقایسهٔ چهار راهبرد

| راهبرد | ارزیابی مستقل | تصمیم |
|---|---|---|
| A: متن فعلی با تغییر کم | نزدیک‌ترین مقصدِ واجد مسیر رایگان CompStat است، اما مثال کاربری و توضیح روش هنوز کم است. تغییر cover letter و نام مجله به‌تنهایی مشکل را حل نمی‌کند | توصیه نمی‌شود |
| B: اصلاح مقاله بدون تغییر هسته | بیشترین سود نزدیک: مسئله، ریاضیات مختصر، API، مثال موجود، مقایسه و تفکیک inference از parity | **راهبرد اصلی** |
| C: نرم‌افزار + validation + مقاله | فقط برای نقص بازتولیدشده یا گسترش ادعا توجیه دارد. رفع P3 یا benchmark تازه پروژهٔ جداگانه است | فعلاً محدود به کنترل نصب و provenance؛ بدون campaign علمی تازه |
| D: انتظار برای JOSS | مناسب از نظر موضوع و هزینه؛ امروز gate سابقه رد می‌شود و انتظار منفعل کافی نیست | مسیر پشتیبان بلندمدت |

**هدف انتخاب‌شده: Computational Statistics، مقالهٔ نرم‌افزاری/package report، مسیر subscription.** این تصمیم با فهرست تاریخی که BRM را اول می‌گذاشت متفاوت است: در اولویت فعلی شما، پذیرش دفاع‌پذیر و تناسب مهم‌تر از JIF است. دامنهٔ صریح software/package و سابقهٔ hermiter دلیل اصلی‌اند؛ از JIF پایین‌تر، پذیرش آسان‌تر استنتاج نشده است.

عنوان پیشنهادی برای نسخهٔ تازه:

> HGFX: Reproducible Hierarchical Gaussian Filter workflows in Python with MATLAB-reference validation

سهم مقاله باید سه جزء داشته باشد: استفادهٔ مستقل از MATLAB؛ حفظ conventions مؤثر بر inference؛ و evidence قابل‌بازتولید که موفقیت و شکست را جدا می‌کند. این framing از سه مقصد قبلی به نرم‌افزار آماری نزدیک‌تر است، بدون ادعای اینکه آن مجلات اصولاً software نمی‌پذیرند.

**هزینه:** publisher صریحاً مسیر subscription بدون APC دارد؛ رنگ آنلاین رایگان است. باید OA، رنگ چاپی پولی، reprints و خدمات اختیاری انتخاب نشوند. به‌دلیل الزام «دقیقاً صفر»، پیش از ارسال واقعی، نویسنده باید متن نهایی پورتال/توافق یا پاسخ کتبی دفتر را برای نبود submission/page/processing fee و امکان انتشار با affiliation واقعی IPM بررسی کند. **تأییدیهٔ اختصاصیِ تمام هزینه‌ها هنوز دریافت نشده است.** این درخواست waiver نیست و در این ممیزی هم پیامی ارسال نشده است. اگر هزینهٔ اجباری یا ابهام حل‌نشده وجود داشت، ارسال انجام نشود؛ JSS سیاست عمومیِ بی‌ابهام‌تری برای صفر بودن author fees دارد.

ریسک‌های باقی‌مانده: incremental novelty در برابر pyhgf؛ سؤال دربارهٔ کارایی عملیِ پارامترهای ضعیف‌قابل‌بازیابی؛ فقدان کاربرد مستقل؛ و پرسش دربارهٔ reproducibility محیط تاریخی. پاسخ درست، محدودکردن ادعا و ارائهٔ مثال شفاف است، نه ساختن نتیجهٔ مثبت تازه.

## بخش ۵ — حداقل برنامهٔ بهبود

برآوردها زمان کار متمرکز یک نویسنده/مهندس هستند، نه زمان سردبیری. برای مسیر اصلی حدود **۵ تا ۱۰ روز کاری** معقول است، اگر نصب و بازتولید نقص تازه‌ای آشکار نکند.

### ضروری پیش از ارسال

| کار و محل | مسئله/فایده | آزمایش تازه؟ | تلاش | خروجی و معیار پذیرش | خطر |
|---|---|---|---|---|---|
| تعیین نسخهٔ مقاله و محصول؛ `paper/` و پروندهٔ submission جدید | جلوگیری از مخلوط شدن stable، beta و فایل‌های سه ارسال | خیر | نیم‌روز | یک paper SHA، یک product SHA، hash فایل PDF و فهرست ورودی‌ها؛ main به‌عنوان محصول ۱٫۰ معرفی نشود | پایین؛ آرشیوهای قدیمی حفظ شوند |
| Introduction/Abstract/Discussion | روشن شدن نیاز کاربر و contribution نرم‌افزاری | خیر | ۱–۲ روز | خواننده بتواند مخاطب، قابلیت، تفاوت با pyhgf و حدود اعتبار را از abstract تشخیص دهد | overclaim؛ کنترل جمله‌به‌شاهد |
| Methods 2.1–2.4 | فقدان بیان خودبسندهٔ مدل/پارامتر/هدف | خیر؛ از منبع ثابت | ۱ روز | خلاصهٔ معادلات، ترتیب و فضای پارامتر، prior، fixed/free و objective؛ تطبیق با oracle | تغییر ناخواستهٔ semantics در متن |
| worked example؛ §3.6 و `examples/` | مثال اجرایی موجود هست، ولی روایت آموزشی کامل نیست | اجرای مثال موجود؛ نه آزمایش تأییدی جدید | ۱–۲ روز | ورودی با provenance، config، fit، trajectory، BIC و محدودیت تفسیر؛ اجرای CPU در محیط تمیز با `hgfx==1.0.0` | انتخاب مثال بر مبنای نتیجهٔ مطلوب ممنوع |
| `paper/reproducibility/README.md`، evidence map و packet | تضاد DRAFT/FROZEN و وضعیت review | خیر | نیم‌روز | وضعیت جاری و تاریخی به‌وضوح جدا؛ لینک دقیق candidate؛ هیچ gate تاریخی بازتعریف نشود | شکستن freeze؛ در بستهٔ جدید انجام شود |
| Figures 3–6 و جدول ادعاها | مخلوط شدن agreement/accuracy و اصطلاحات داخلی | خیر؛ فقط همان artifactها | نیم تا یک روز | عددهای ثابت، دو estimand جدا، criterion هر backend مشخص، P3 منفی و NDC آشکار | تغییر ناخواستهٔ عدد/label؛ آزمون figure/table |
| preflight مالی و journal format | هزینهٔ صفر و تناسب نوع مقاله | خیر | چند ساعت + زمان پاسخ | عدم هر تعهد مالی؛ فایل نهایی با figure و bibliography خوانا؛ declarations کامل | پذیرش ناخواستهٔ OA/رنگ پولی |

### قویاً توصیه‌شده

| کار | تلاش | خروجی و معیار |
|---|---|---|
| خواندن و اجرای مستقل مثال توسط یک پژوهشگر تازه | ۱–۲ روز هماهنگی | گزارش واقعی نصب، commands و خطاها؛ بدون ادعای adoption صرفاً از این تست |
| جدول مقایسهٔ MATLAB / HGFX 1.0 / pyhgf 0.3.2 | نیم‌روز | runtime، config semantics، inference، GPU و دامنهٔ evidence؛ هر خانه منبع داشته باشد |
| replication entry point واحد | حدود ۱ روز | تولید جدول/شکل از ورودی‌های ثابت در مسیر خروجی جدا؛ اجرای علمی تاریخی از بازسازی artifact جدا باشد |
| آرشیو پایدار بستهٔ مقاله با شناسهٔ دائمی | نیم‌روز | فایل‌ها، license، hashes و نسخهٔ release روشن؛ قبل از هر upload کنترل مجوز و اطلاعات حساس |
| آرشیو اصل نامه‌ها و فایل‌های ارسال | نیم‌روز | chronology با رسید واقعی؛ نامهٔ خصوصی بدون رضایت عمومی نشود |

### اختیاری و فقط با توجیه علمی

| کار | ماژول/فایل درگیر | تلاش و معیار پذیرش | خطر و شرط اجرا |
|---|---|---|---|
| تشخیص محدود P3 | workflow تاریخی در SHA `a051e747…`، aggregate P3، مسیرهای model و optimizer مرتبط پس از localization | ۲–۵ روز برای diagnosis اولیه، نه تضمین حل؛ اولین اختلاف trial/level/state/intermediate ثبت شود | بدون بازتعریف threshold؛ علت باید پیش از patch مشخص شود. فقط اگر ادعای عمومی‌تر یا داور نیاز داشت |
| revalidation GPU روی release دقیق | runner S9 و artifact جدید مجزا | ۱–۲ روز مهندسی به‌علاوه دسترسی سخت‌افزار؛ همان معیار float64 و دستگاه واقعی | ضروری برای ادعای جدید GPU؛ بدون جایگزینی evidence قدیمی |
| تحلیل دادهٔ واقعی | example/analysis مستقل با مجوز داده | حداقل ۱–۳ هفته؛ سؤال و پروتکل پیش از نتیجه، بازتولید و تفسیر محدود | ارزش کاربردی دارد؛ نباید برای «نجات» مقاله یا نمایش recovery انتخاب شود |

### کارهای غیرضروری برای این ارسال

بازنویسی هسته، افزودن مدل‌های جدید، GUI، benchmark بزرگ GPU، general scaling، تطبیق همهٔ خانواده‌های pyhgf، یا تبدیل شکست recovery به PASS. برای رفع یک ابهام مستنداتی، تغییر tolerance، prior، optimizer، seeds یا dataset هیچ توجیهی ندارد. ارتقای ۱٫۱ نیز شرط انتشار مقالهٔ ۱٫۰ نیست.

## بخش ۶ — مسیرهای جایگزین

**سریع‌ترین مسیر معتبر نزدیک:** نسخهٔ package paper برای Computational Statistics پس از بازنویسی محدود و بستن کنترل هزینه. ارسال فوری متن فعلی سریع‌تر است، اما از نظر editorial fit قابل توصیه نیست. median هشت‌روزهٔ first decision وعدهٔ review یا acceptance نیست.

**قوی‌ترین مسیر نرم‌افزاری بلندمدت:** JOSS، پس از عبور واقعی از eligibility. GitHub ایجاد مخزن را `2026-09-06T22:13:03Z` نشان می‌دهد. اگر از همان ابتدا public بوده، نخستین تاریخ روزانهٔ محافظه‌کارانه برای «بیش از شش ماه» **۷ مارس ۲۰۲۷** است؛ حدود چهار ماه دیگر. created_at زمان public شدن را ثابت نمی‌کند، پس این یک حد زودهنگام مشروط است. [قواعد رسمی](https://joss.readthedocs.io/en/latest/submitting.html)

سن به‌تنهایی کافی نیست: فعالیت واقعی در طول دوره و استفادهٔ پژوهشی باید مستند باشند. استفاده توسط خود توسعه‌دهنده می‌تواند قابل قبول باشد؛ کاربر بیرونی شرط مطلق نیست. [معیارهای review](https://joss.readthedocs.io/en/latest/review_criteria.html) نیز reproducible research materials را در ارزیابی significance مطرح می‌کنند؛ بنابراین نبود adoption مستقل نباید به منع مطلق تبدیل شود. gate سن اکنون به‌تنهایی مانع است. فعالیت نمایشی یا دستکاری Git history پذیرفتنی نیست.

پیش‌نویس `paper/joss/paper.md` مناسب شروع است، نه آمادهٔ ارسال: disclosure نسخهٔ ابزارهای AI و evidence اثر پژوهشی باید نهایی شود. اگر مقالهٔ دیگری پذیرفته شد، eligibility انتشار software paper جداگانه و overlap دوباره بررسی شود؛ دو ارسال هم‌زمان از یک متن انجام نشود. مکاتبهٔ نویسنده با سردبیر/داور JOSS باید مطابق منع فعلی AI برای گفت‌وگوی تحریریه، توسط انسان انجام شود.

**اگر هدف اصلی رد کرد:** دلیل واقعی را ثبت کنید. اگر مشکل مخاطب بود، نسخهٔ رفتاری/آموزشی را به BRM ببرید. اگر نیاز به مقالهٔ نرم‌افزاری کامل‌تر و بازتولید بیشتر بود، JSS را انتخاب کنید. اگر نقص علمی مشخص گزارش شد، ابتدا همان نقص بررسی شود؛ ارسال زنجیره‌ای بدون پاسخ به آن مناسب نیست. SoftwareX و JORS فقط با waiver کاملِ کتبی می‌توانند وارد مسیر عملی شوند.

## بخش ۷ — چک‌لیست اجرایی مستقل از تاریخچهٔ گفتگو

- [ ] `git status`، SHA محلی و remote ثبت؛ تغییرات نامرتبط محفوظ بماند.
- [ ] هشت سند الزامی AGENTS.md و policyهای freeze پیش از هر تغییر کد خوانده شود.
- [ ] محصول مقاله `hgfx==1.0.0` و SHA `4dd8fbd8…` باقی بماند؛ branch مقالهٔ جدید از baseline معلوم ایجاد شود.
- [ ] نامه‌های تصمیم و فایل‌های واقعاً ارسال‌شده با hash جمع‌آوری؛ تاریخ‌های نامطمئن unknown بمانند.
- [ ] target برابر Computational Statistics و نوع software/package paper ثبت؛ فقط یک ارسال فعال.
- [ ] سیاست هزینه در روز ارسال دوباره کنترل؛ subscription انتخاب؛ هیچ هزینهٔ اجباری یا waiver نامطمئن پذیرفته نشود.
- [ ] وضعیت affiliation واقعی IPM و نبود هزینهٔ ارسال/صفحه/پردازش در شرایط نهایی تأیید؛ اگر نامعلوم ماند، ارسال متوقف و مسیر JSS بررسی شود.
- [ ] Abstract، Introduction، Methods و Discussion با framing نرم‌افزار آماری بازنویسی شوند.
- [ ] یک worked example از داده/دموی موجود با manifest و دستور CPU ساخته و توسط فرد تازه اجرا شود؛ نمونهٔ انتخابی دلیل پیشینی داشته باشد.
- [ ] ۳۶/۳۶ agreement کنار accuracy برابر ۰٫۵۸۳ گزارش شود؛ recovery failures، P3 failed gate و NDC حذف نشوند.
- [ ] T4 applicability، CPU/backend tolerance و H100 تاریخی جدا بمانند؛ ادعای سرعت تازه اضافه نشود.
- [ ] اسناد وضعیت قدیمی به رکورد جدید ارجاع دهند؛ historical FAIL و freezeهای سابق دست‌نخورده بمانند.
- [ ] تمام claimها به artifact ثابت وصل؛ هزینه/رتبه/زمان مجله با منبع رسمی و تاریخ کنترل ثبت شود.
- [ ] table/figure checks و reference guard اجرا؛ اگر کد تغییر کرد، golden test ابتدا fail و سپس CPU x64 و diff گزارش شود؛ tolerance افزایش نیابد.
- [ ] PDF و source نهایی با همهٔ شکل‌ها، جدول‌ها، bibliography، funding/COI/data/AI disclosures بازبینی شوند.
- [ ] candidate جدید با SHA و hashes قفل؛ review داخلی جدید با داوری انسانی مجله اشتباه نشود.
- [ ] نویسنده پس از کنترل نهایی علمی و مالی شخصاً ارسال کند؛ این گزارش هیچ ارسال یا مکاتبه‌ای انجام نداده است.

**حد قطعیت این گزارش:** توصیهٔ انتشار از شواهد فعلی و policyهای عمومی به‌دست آمده است. نتیجهٔ سردبیری، waiver، قرارداد مالی اختصاصی و صحت همهٔ مسیرهای نرم‌افزار تضمین نشده‌اند. هیچ نتیجهٔ علمی، milestone یا سابقهٔ رد برای بهبود ظاهر پروژه تغییر نکرده است.
