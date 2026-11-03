# HGFX Publication Revision Implementation Plan

> Current execution extension (2026-11-04): [case-study and full journal rewrite handoff](2026-11-04-pain-case-study-handoff.md). Sections J1-J6 define the venue decision, section-level rewrite, figures, financial checks and final submission package. New scientific work is limited to its predeclared gates; frozen results remain unchanged. Submission itself is excluded.

> **For agentic workers:** Execute this plan task by task using `superpowers:executing-plans` if available. Otherwise follow the same checklist directly. No previous conversation is required. Do not stop after producing another plan. Complete all locally executable preparation, verification, and Git delivery; report genuine external blockers separately.

**Goal:** آماده‌کردن یک مقالهٔ نرم‌افزار آماری دربارهٔ HGFX 1.0.0 برای Computational Statistics، با حفظ همهٔ نتایج مثبت و منفی و شرط قطعی صفر هزینهٔ اجباری.

**Architecture:** مقاله و بستهٔ جدید در `paper/computational_statistics/` ساخته می‌شوند. متن، نتایج، manifest و بسته‌های frozen قدیمی مرجع تاریخی می‌مانند. بازنویسی و بازتولید نمایش‌های موجود از اجرای علمی جدید جدا است؛ هیچ توسعهٔ هسته‌ای شرط این برنامه نیست.

**Tech Stack:** English Markdown, existing BibTeX, Python, NumPy/JAX CPU float64, existing paper scripts; final PDF and editable source using current official journal instructions.

**Spec:** `docs/submissions/2026-11-03_publication_audit_fa.md` — گزارش تصمیم‌گیری مورخ ۳ نوامبر ۲۰۲۶. سیاست مجله در روز اجرای مرحلهٔ مربوط دوباره بررسی شود. این سند برنامه است، نه تأیید علمی یا تضمین پذیرش.

## دستور شروع برای ایجنت

«این فایل و spec پیوندشده را بخوان. مراحل باز را به ترتیب تا آماده‌شدن بستهٔ قابل بررسی نویسنده انجام بده. کار معمول، رفع ایراد مستندات، ساخت شکل از دادهٔ ثابت و اجرای smoke test به اجازهٔ مجدد نیاز ندارد. وضعیت هر مرحله، خروجی و شواهد آزمون را در EXECUTION_LOG.md بنویس. هیچ submission، upload پیش‌چاپ، ایمیل، تغییر نتیجه، آزمایش علمی جدید یا تعهد مالی انجام نده. در صورت مانع بیرونی، بقیهٔ کارهای مستقل را تمام کن. تغییرات مرتبط را commit و push کن و تحویل نهایی را با لینک فایل‌ها و محدودیت‌های باقی‌مانده بده.»

## وضعیت تحویل اولیه و مرز اجرا

- [x] ممیزی اولیه انجام و نسخهٔ آن داخل مخزن قرار داده شد.
- [x] پیش‌نویس جدید از `paper/manuscript.md` ایجاد؛ عنوان، چکیده، framing مقدمه و بحث و caption شکل ۳ اصلاح اولیه شد.
- [x] متن تاریخی، جداول، شکل‌ها، نتایج و freeze اصلی دست‌نخورده باقی ماند.
- [ ] مراحل ۱ تا ۸ زیر هنوز باید اجرا و مستند شوند؛ اصلاح اولیه به معنی پایان بازنویسی نیست.

هدف اولیه **Computational Statistics / software-package contribution / subscription** است. این توصیف نوع علمی مقاله است؛ نام دقیق article type در سامانه باید با راهنمای جاری تطبیق یابد. **مبلغ اجباری مجاز: €0**. اگر هزینهٔ ارسال، صفحه، پردازش، انتشار یا هزینهٔ اجباری دیگر نامعلوم است، وضعیت مالی OPEN می‌ماند؛ optional OA انتخاب نشود. هیچ waiver احتمالی معادل رایگان قطعی نیست.

## Global Constraints — قرارداد علمی غیرقابل تغییر

1. ابتدا `AGENTS.md` و هشت سند الزامی آن را بخوان: `docs/planning/{MIGRATION_MATRIX,EXECUTION_PLAN,ROADMAP,MILESTONES}.md`، `docs/architecture/{ARCHITECTURE,NUMERICAL_POLICY}.md`، `docs/validation/{GOLDEN_TEST_SPEC,ACCEPTANCE_CRITERIA}.md`.
2. baseline ممیزی `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`؛ HEAD اجرای جدید را دوباره ثبت کن. محصول مقاله `hgfx==1.0.0` با source `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` است؛ main دارای کارهای beta است و جانشین آن نیست.
3. oracle: HGF Toolbox 8.2.0، SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`، منطبق با `reference/HGF_VERSION` و `reference/HGF_COMMIT`.
4. داده، seed، prior، پارامتر، objective، optimizer، tolerances و thresholds برای بهبود نتیجه تغییر نکنند. نتایج قدیمی یا manifest آنها بازتولید/بازنویسی نشوند.
5. 36/36 توافق BIC معادل بازیابی درست مدل نیست: balanced accuracy هر دو پیاده‌سازی `0.583333333333` است. recovery تاریخی موفق نشده است.
6. P3: run `35272347167`، 10/72 اختلاف BIC؛ gate شکست‌خورده و `INSUFFICIENT_REFERENCE_EVIDENCE` حفظ شود. برچسب `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` حذف یا به علت قطعی جدید تعبیر نشود. MATLAB release تاریخی `latest` بوده و نسخهٔ دقیق معلوم نیست.
7. pyhgf `0.3.2`: فقط یک cell سه‌سطحی binary با 128 trial و 11 مقدار mapped؛ NLL پاسخ NDC است. هیچ ادعای برتری یا equivalence سراسری اضافه نشود.
8. T4: دو دستگاه visible، چهار fitting cell روی `cuda:0`، applicability محدود؛ نه speedup یا multi-GPU. معیار CPU `0.1` را با معیار T4 `1e-7` یکی نکن. شواهد تاریخی H100 با provenance مستقل بماند.
9. manuscript جدید همچنان draft است؛ تأیید نویسنده و صحت declarations شرط آماده‌سازی نهایی برای ارسال است. AI review را external human peer review معرفی نکن.
10. تغییرات نامرتبط کاربر، از جمله `.gitignore`، `.freebuff/` و `.repowise/` را stage، حذف یا reset نکن. فقط مسیرهای متعلق به همین کار commit شوند. هیچ force push یا جعل history/adoption مجاز نیست.

## Review Focus

| خطر | آزمون/کنترل مالک |
|---|---|
| اجرای checkout beta به جای wheel 1.0.0 | مرحله ۳: version، module path، hash wheel و محیط خارج checkout |
| پنهان‌شدن شکست علمی زیر عدد توافق | مراحل ۲ و ۴: claim ledger و بررسی مستقل agreement/accuracy |
| تغییر ناخواستهٔ artifact frozen | مراحل ۱ و ۷: hash baseline و diff مسیرهای حفاظت‌شده |
| build مقالهٔ قدیمی به جای candidate جدید | مرحله ۶: عنوان، ورودی، شکل و bibliography در PDF خروجی کنترل شود |
| رایگان فرض‌کردن subscription یا waiver | مرحله ۸: مدرک رسمی/شرایط نهایی، unknown مانع submission است |

## نقشهٔ فایل‌ها

| مسیر | نقش |
|---|---|
| `paper/computational_statistics/manuscript.md` | تنها متن فعال این revision، انگلیسی؛ اکنون اصلاح اولیه دارد |
| `paper/computational_statistics/README.md` | وضعیت واقعی، مسیر build و رابطه با نسخهٔ تاریخی |
| `paper/computational_statistics/EXECUTION_LOG.md` | ایجاد در مرحله ۱؛ هر task با command، outcome و blocker |
| `paper/computational_statistics/claim_evidence.md` | ایجاد در مرحله ۲؛ claim → exact source + locator + scope |
| `paper/computational_statistics/worked_example/` | مرحله ۳؛ walkthrough، runner در صورت نیاز، environment و manifest خروجی |
| `paper/computational_statistics/figures/` | مرحله ۴؛ فقط نسخه‌های ارائه‌ای جدید و manifest، بدون overwrite قدیمی |
| `paper/computational_statistics/build_submission.py` | مرحله ۶؛ فقط اگر ابزار موجود ورودی جدید را پشتیبانی نمی‌کند |
| `paper/computational_statistics/dist/` | PDF، source و supplementary جدید؛ فایل‌های موقت commit نشوند |
| `paper/computational_statistics/REVISION_MANIFEST.json` | مرحله ۷؛ source identities، input/output hashes و وضعیت کنترل‌ها |
| `docs/submissions/2026-11-03_publication_revision_status.md` | مرحله ۵؛ وضعیت جاری با تفکیک تاریخی و فعلی |
| `paper/computational_statistics/SUBMISSION_PREFLIGHT.md` | مرحله ۸؛ کنترل مالی، اداری و author approval |
| `paper/computational_statistics/BIORXIV_REVISION.md` | مرحله ۸؛ فایل‌ها و change summary برای نویسنده، بدون upload |

## مرحله ۱ — ثبت baseline و حفاظت از شواهد (۲–۳ ساعت)

**Consumes:** مخزن جاری، اسناد الزامی، گزارش ممیزی. **Produces:** execution log و hash baseline.

- [ ] `git status --short`، `git rev-parse HEAD`، `git ls-remote origin refs/heads/main` و وضعیت branch را ثبت کن. اگر baseline تغییر کرده، diff مرتبط را بخوان؛ تغییر علمی را نادیده نگیر.
- [ ] branch کاری `paper/computational-statistics-revision` بساز، یا اگر موجود است همان را پس از بررسی ادامه بده. تغییرات نامرتبط را همراه commit نبر.
- [ ] قبل از هر کاری SHA-256 فایل‌های tracked زیر را در `paper/computational_statistics/baseline_hashes.json` ثبت کن: `reference/validation/`، `gpu_validation_results/`، `paper/reproducibility/`، `paper/tables/`، `paper/figures/`، `paper/manuscript.md`، `paper/references.bib` و `paper/arxiv/frozen/`. symlink/submodule را با identity مناسب جدا ثبت کن.
- [ ] read-only guard را اجرا کن: `.venv/Scripts/python.exe scripts/verify_reference_freeze.py`؛ نتیجه/نسخهٔ Python ثبت شود. شکست را پنهان نکن.
- [ ] مراحل باز، prerequisites و منابع غایب را در EXECUTION_LOG ثبت کن؛ برای متن مستقل نیازی به انتظار نامه‌های رد نیست.

**Acceptance:** identity کامل، hash baseline و guard معلوم؛ هیچ artifact تاریخی تغییر نکرده. Commit ثبت provenance.

## مرحله ۲ — بازنویسی کامل برای خوانندهٔ آماری (۱–۲ روز)

**Files:** candidate manuscript، claim_evidence.md؛ bibliography جدید در همان پوشه فقط در صورت نیاز. **Consumes:** متن اولیه و شواهد frozen. **Produces:** مقالهٔ مستقل و جدول پشتیبانی ادعاها.

- [ ] برای هر ادعای عددی/قابلیت، source دقیق و locator ثبت کن؛ author verification را تا بررسی واقعی انسان `pending` بگذار. عددها از artifact خوانده شوند، نه گزارش یا گفتگو.
- [ ] عنوان پیشنهادی موجود را حفظ یا با همان دامنه بهبود بده: `HGFX: a Python package for reference-compatible Hierarchical Gaussian Filter workflows`. از validated به معنی اعتبار علمی عمومی و GPU-native به معنی برتری سرعت پرهیز کن.
- [ ] Introduction را حول مسئلهٔ کاربر بنویس: اجرای workflow تثبیت‌شدهٔ HGF خارج MATLAB، چرا semantics مهم است، تفاوت با pyhgf، و contribution محدود. ادعای «اولین Python HGF» یا novelty مدل جدید ممنوع.
- [ ] Methods یک خلاصهٔ ریاضی کوتاه و دقیق از نسخهٔ frozen داشته باشد: hierarchy، observation model، فضای native/transformed، ترتیب پارامترها، priors، fixed/free، missing/irregular trial و objective. معادله را از MATLAB و مستندات تطبیق بده؛ به‌خصوص index سطح binary را با نگارش موجود کنترل کن. بدون بررسی منبع فرمول ننویس؛ تفصیل خانواده‌ها به supplement برود.
- [ ] Results به ترتیب نیاز خواننده: workflow، numerical parity، recovery/model selection، comparison محدود pyhgf، backend. شکست‌ها با مقدار و دامنه در متن اصلی باقی بمانند؛ IDهای اجرایی بلند به supplement منتقل شوند.
- [ ] جدول مقایسهٔ MATLAB/HGFX1.0/pyhgf0.3.2 اضافه کن: هدف طراحی، runtime، semantics، inference، GPU و دامنهٔ آزمایش. هر خانه source داشته باشد؛ نبود بررسی را unknown بنویس نه «ندارد».
- [ ] Discussion بگوید چه استفاده‌ای پشتیبانی می‌شود و چه استنباطی پشتیبانی نمی‌شود. release parity، recovery، identifiability و performance چهار ادعای جدا هستند. به جای دفاع از پروژه، محدودیت عملی برای پژوهشگر توضیح داده شود.
- [ ] Abstract پس از تکمیل متن، حداکثر مطابق راهنمای روز مجله؛ عدد توافق و accuracy کنار هم، شکست recovery/P3 و حدود GPU/NDC صریح. بخش funding/COI/CRediT/AI را بدون تأیید به facts جدید تبدیل نکن.
- [ ] تمام citation keys با BibTeX تطبیق؛ منابع تازه فقط از صفحهٔ ناشر/اصل مقاله تأیید شوند. bibliography تاریخی را تغییر نده؛ در صورت نیاز copy با provenance بساز.

**Acceptance:** هیچ ادعای بی‌منبع، هیچ عدد متناقض، هیچ gate جدید ساختگی؛ مقاله برای خوانندهٔ بیرون مخزن قابل فهم است. هنوز draft تا author review. Commit متن و ledger.

## مرحله ۳ — worked example و نصب مستقل

**به‌روزرسانی ۳ نوامبر:** درخواست جدید نویسنده شامل مطالعه‌های منتشرشده با کد و داده است. ابتدا `docs/superpowers/plans/2026-11-03-published-case-studies.md` و `paper/case_studies/README_FA.md` خوانده و مراحل C1–C4 آن اجرا شوند. دو کاندید اول Arthur2023 و Hess2025 هستند؛ eligibility آنها هنوز PASS نیست. ضمیمه، اولویت قبلیِ صرفاً quickstart را به امکان‌سنجی case واقعی ارتقا می‌دهد. نتایج جدید از frozenها جدا بمانند. محدودیت «آزمایش علمی جدید ممنوع» همچنان دربارهٔ recovery/association/مدل جدید برقرار است؛ بازتولید محدودِ تعریف‌شده در ضمیمه پس از قفل protocol مسیر جدید آماده‌سازی است. در نوبت گردآوری منابع هیچ fit جدید اجرا نشده است. برآورد یک روز برای demo بود؛ caseهای واقعی زمان جداگانهٔ ضمیمه را دارند.

**Read:** `examples/README.md`، `examples/quickstart.py`، `examples/hgf_demo_full.py`، `examples/matlab_demo_model_selection.py`، `examples/matlab_demo_uhgf_ar1.py`.

- [ ] انتخاب از پیش: اولین quickstart موجود که API نسخهٔ 1.0.0 پشتیبانی می‌کند، برای fit/simulation؛ demo رسمی challenge برای نشان‌دادن محدودیت کلاسیک در صورت نیاز. علت انتخاب، input hash و seed را قبل از اجرا ثبت کن. انتخاب براساس recovery مطلوب ممنوع.
- [ ] یک venv جدید خارج checkout بساز؛ wheel `hgfx==1.0.0` از PyPI نصب، `pip freeze`، version، `hgfx.__file__` و SHA-256 wheel دانلودشده ثبت شود. `PYTHONPATH=src` یا editable install مجاز نیست. از cwd خارج checkout اجرا کن.
- [ ] دستورهای PowerShell و یک معادل POSIX در README مثال ارائه کن. `JAX_ENABLE_X64=1` و `JAX_PLATFORMS=cpu`؛ device و x64 را در خروجی واقعاً کنترل کن.
- [ ] walkthrough شامل ورودی با provenance، config و پارامتر، fit/sim، trajectory و تفسیر باشد. BIC فقط اگر runner موجود واقعاً آن را محاسبه می‌کند؛ برای افزودن عدد هیچ نتیجه جعل نشود. دادهٔ شبیه‌سازی‌شده صریحاً synthetic معرفی شود.
- [ ] اگر demo به submodule نیاز دارد، منبع و دستور تهیه را صریح بگو؛ dependency بر فایل repo را قابلیت wheel ننام. دادهٔ third-party بدون مجوز بازتوزیع نشود.
- [ ] runtime result و خطاها حفظ شوند؛ اجرای مثال smoke/workflow است، نه آزمایش جدید recovery. هیچ نتیجهٔ frozen جایگزین نشود.

**Acceptance:** فرمان‌های مستند از محیط تمیز اجرا شده، version1.0.0 و CPU x64 ثابت شده؛ output path، seed و input hash ثبت؛ §Examples مقاله از همین اجرای محدود تغذیه شود. اگر install واقعاً fail شد، دقیق مستند کن و مانع را از نقص مقاله جدا کن. Commit مثال و شواهد کم‌حجم.

## مرحله ۴ — شکل‌ها و جدول‌های قابل تفسیر (نیم تا یک روز)

**Read:** `paper/scripts/generate_p5_figures.py`، `paper/scripts/generate_p2_tables.py`، `tests/paper/test_p5_figures.py` و artifactهای ورودی آنها.

- [ ] شکل ۳ را در مسیر جدید بازطراحی کن: یک panel برای agreement=36/36، panel دیگر برای balanced accuracy=0.583333333333 هر implementation. threshold model recovery فقط در panel مربوط؛ legend روشن کند توافق مساوی صحت مدل مولد نیست.
- [ ] Figure2 recovery و Figure6 horizon را با failure/gapهای موجود نگه دار. P3 paired-integrity failure باید در caption خوانا بماند.
- [ ] Figure4 هر backend را نسبت به معیار خاص خودش نمایش دهد، hardware و provenance محدود در caption؛ speed یا scale axis ایجاد نکن.
- [ ] Figure5 در صورت هم‌پوشانی خطوط، residual/inset فقط از همان arrays ثابت؛ بدون fit تازه، smoothing یا resampling گزینشی. این بهبود اختیاری است.
- [ ] عناوین طولانی/IDهای داخلی را از plot به caption/supplement منتقل کن. PDF vector و PNG preview تولید؛ فونت، legend و کنتراست در اندازهٔ نهایی واقعاً بازبینی شود.
- [ ] اگر script جدید می‌نویسی، ابتدا test معنادار برای جدایی دو metric و برابری اعداد با input ثابت بنویس؛ سپس اجرا کن. scriptهای قدیمی را با defaults جدید تغییر نده. hash ورودی/خروجی و transformation در manifest جدید.

**Acceptance:** همهٔ اعداد همان input؛ no overwritten historical figures؛ تصاویر نهایی دیده شده و فقط «file exists» ملاک نباشد. Commit rendering و tests مرتبط.

## مرحله ۵ — رفع ابهام تاریخچه و وضعیت (۲–۴ ساعت)

- [ ] `docs/submissions/2026-11-03_publication_revision_status.md` بساز و conflict اسناد قدیمی را به‌صورت dated correction ثبت کن: reproducibility README قدیمی `DRAFT_NOT_FROZEN` در برابر manifest `FROZEN_FOR_SUBMISSION`، P8 packet قدیمی در برابر `docs/research/PAPER_P8_REVIEW_CHECKLIST.md`. اسناد hashشده را بازنویسی نکن.
- [ ] «P8 داخلی تاریخی PASS» را از «candidate جدید هنوز author-reviewed نیست» جدا کن. milestone جدید یا PASS علمی ایجاد نکن.
- [ ] رکورد تصمیم‌های سه مجله را با سطح evidence ثبت کن. نامهٔ اصلیِ در دسترس‌نبودن را صریح بگو؛ Brain Informatics: رد ۳ نوامبر بدون دلیل تفصیلی بر اساس اطلاعات نویسنده. شکست external peer review یا bug از آن استنتاج نکن.
- [ ] اختلاف dossier transfer مورخ ۳۱ اکتبر و تاریخ submit اعلام‌شدهٔ ۳۰ اکتبر unknown بماند تا receipt واقعی. نامهٔ خصوصی را در repo عمومی منتشر نکن.
- [ ] README candidate به گزارش وضعیت جدید لینک بده. branchهای JOSS/transfer را تنها در صورت نیاز read-only بخوان؛ merge کورکورانه نکن.

**Acceptance:** خواننده با یک entry point وضعیت جدید و تاریخی را تفکیک کند؛ تاریخچه بازنویسی نشده باشد. Commit اصلاح مستندات.

## مرحله ۶ — ساخت بستهٔ مجله (نیم تا یک روز)

- [ ] راهنمای رسمی روز را بخوان: https://link.springer.com/journal/180/submission-guidelines ؛ limits، template و article type را ثبت کن. قالب JNM به candidate منتقل نشود.
- [ ] سازندهٔ قدیمی `paper/scripts/build_journal_submission.py` مسیر `paper/manuscript.md` را hard-code می‌کند. آن را با `--output-dir` صرف اجرا نکن و خروجی را نسخهٔ جدید ننام. یا یک wrapper مستقل با ورودی صریح بساز یا tool مناسب با candidate جدید استفاده کن؛ regression قدیمی دست‌نخورده.
- [ ] اگر builder جدید لازم است، ورودی manuscript، bibliography، figures و output صریح و بدون overwrite باشد. ابتدا test بنویس که عنوان candidate جدید در خروجی است، شش figure/caption وارد شده و citation unresolved باقی نمانده.
- [ ] PDF قابل ارسال + editable source + supplement با شماره‌های سازگار بساز. draft banner و metadata داخلی تا author approval در working source بماند؛ نسخهٔ review را واضح علامت بزن.
- [ ] PDF را render و همهٔ صفحات را بررسی کن: بریدگی جدول، نشانهٔ citation خام، فرمول خراب، شکل گم‌شده و metadata داخلی نباشد. گزارش page-by-page کوتاه بنویس. در صورت تولید DOCX، مهارت documents و render آن لازم است.
- [ ] cover letter پیشنهادی تهیه کن، با scope نرم‌افزار آماری و preprint DOI، بدون ساختن originality statement/author approval؛ ارسال یا ایمیل نکن.

**Acceptance:** build reproducible و PDF واقعاً دیده شده؛ output از candidate جدید است؛ unknown declarations باقی‌مانده جدا فهرست شود. Commit source و deliverableهای نهایی مجاز.

## مرحله ۷ — کنترل یکپارچگی و تحویل فنی (۲–۴ ساعت)

```powershell
$env:JAX_ENABLE_X64 = '1'
$env:JAX_PLATFORMS = 'cpu'
.venv/Scripts/python.exe scripts/verify_reference_freeze.py
.venv/Scripts/python.exe -m pytest -q tests/paper/test_p2_tables.py tests/paper/test_p3_evidence.py tests/paper/test_p6a_claim_audit.py tests/paper/test_p6a_manifest.py
git diff --check
```

- [ ] خروجی واقعی این کنترل‌ها و تست‌های جدید builder/figure را ثبت کن. تعداد آزمون ممکن است نسبت به ممیزی عوض شده باشد؛ آن را hard-code نکن. این tests قدیمی به‌تنهایی candidate جدید را تأیید نمی‌کنند؛ claim ledger و output QA جدید هم لازم است.
- [ ] hash تمام baselineها را دوباره مقایسه کن. `src/`، reference، validation، thresholds و artifact frozen باید unchanged باشند. هر انحراف توضیح داده و رفع شود، نه اینکه baseline جدید جای قبلی گذاشته شود.
- [ ] REVISION_MANIFEST شامل baseline، release، oracle، DOI، sourceهای نتایج، input/output hashes، environment، status هر check، limitations و تاریخ باشد. از self-hash یا ادعای SHA commitی که هنوز ساخته نشده پرهیز کن؛ commit نهایی در handoff ثبت شود.
- [ ] checkpoint را با ledger، مثال، تصاویر، PDF و report تطبیق بده؛ هیچ چک‌باکس بدون شاهد completed نشود. به‌جای «کل پروژه PASS»، دامنهٔ کنترل را بنویس.
- [ ] فقط مسیرهای مرتبط را stage؛ `git diff --cached --check` و diff staged بازبینی؛ commit و push بدون force. SHA remote را با local مقایسه کن. در صورت branch protection، push branch و گزارش لینک؛ merge اجباری نکن.

**Acceptance:** scientific inputs unchanged، tests و rendering معلوم، remote delivery تأیید. Full suite/MATLAB/GPU rerun شرط این بازنویسی نیست، مگر تغییر واقعیِ آن مسیر ضرورت تازه ایجاد کند.

## مرحله ۸ — preflight مالی و نسخهٔ bioRxiv (چند ساعت + پاسخ بیرونی احتمالی)

- [ ] در SUBMISSION_PREFLIGHT منبع و تاریخ هر مورد ثبت: subscription بدون APC، submission fee، page/processing/publication charges، رنگ/نسخه چاپی، applicability برای affiliation واقعی IPM ایران. منبع: https://link.springer.com/journal/180/how-to-publish-with-us و author guidelines. optional OA انتخاب نشود.
- [ ] اگر نبود تمام هزینه‌های اجباری از شرایط نهایی معلوم نیست، یک متن inquiry کوتاه آماده کن تا نویسنده ارسال کند؛ خودت ایمیل نزن. **مالی OPEN = ممنوعیت ارسال واقعی، نه توقف بقیهٔ آماده‌سازی.** affiliation پنهان/عوض نشود و waiver ایران فرض نشود.
- [ ] بودجه صفر، funding/COI/CRediT/AI و دقت متن باید توسط نویسنده تأیید شود. هیچ manuscript هم‌زمان در دو journal فعال نباشد. rejection قبلی از روی شواهد واقعی ثبت شود.
- [ ] BIORXIV_REVISION.md بنویس: DOI موجود `10.64898/2026.09.22.753415`؛ فایل posted فعلی و history ابتدا توسط نویسنده/دسترسی مجاز بررسی شود. متن repo را بدون تطبیق برابر نسخهٔ posted فرض نکن.
- [ ] طبق راهنمای رسمی https://www.biorxiv.org/about-biorxiv ، پیش از پذیرش رسمی journal امکان `Author Area → Submit a Revision` وجود دارد؛ DOI ثابت و نسخه‌های قدیمی در دسترس می‌مانند. policy را روز اجرا دوباره بررسی کن؛ upload جدید به‌عنوان مقالهٔ تازه نکن.
- [ ] برای revision، PDF preprint بدون metadata هدف مجله و summary تغییرات بساز: reframing، توضیح دقیق agreement/accuracy، worked example و نمایش شفاف محدودیت‌ها؛ فقط موارد واقعاً انجام‌شده نوشته شود. «نتایج جدید» در صورت نبود آزمایش جدید ادعا نشود.
- [ ] بستهٔ آماده را به نویسنده بده؛ update title/abstract در portal و انتخاب مقالهٔ درست را به checklist انسانی اضافه کن. در این برنامه upload bioRxiv، publication archive یا submit journal خودکار مجاز نیست.

**Acceptance:** همهٔ کارهای محلی تمام؛ وضعیت author approval و finance جدا و صادقانه. خروجی مطلوب `READY_FOR_AUTHOR_REVIEW` است؛ `READY_TO_SUBMIT` فقط بعد از تأیید انسانی و هزینهٔ قطعی صفر. اگر شرط مالی حل نشد، بسته حفظ و JSS به‌عنوان fallback بررسی شود؛ بازنویسی جدید خودکار شروع نشود.

## اولویت، زمان و کارهای خارج از دامنه

**ضروری:** مراحل ۱–۸ با حدود ۵–۱۰ روز کاری؛ زمان پاسخ دفتر مجله در این برآورد نیست. اجرای برنامه نباید به انتظار بی‌دلیل تقسیم شود.

**قویاً توصیه‌شده، بدون جعل:** یک پژوهشگر واقعی مثال را اجرا و readability را بررسی کند؛ اگر در دسترس نبود `not performed` ثبت و author review درخواست شود. agent review جانشین آن معرفی نشود.

**اختیاری:** residual Figure5، archive دارای DOI پس از تأیید نویسنده، کاربرد دادهٔ واقعی با پروتکل مستقل در آینده. اینها شرط پایان محلی نیستند.

**غیرضروری/خارج از این قرارداد:** مدل جدید، GUI، refactor هسته، release1.1، GPU benchmark تازه، tuning recovery، اجرای دوبارهٔ تمام P3، مقایسهٔ سراسری pyhgf. اگر نقص بحرانی واقعی پیدا شد، ابتدا سند علت/اولین divergence بنویس؛ patch علمی نیازمند قرارداد migration و golden test مستقل است.

**JOSS:** مسیر بلندمدت مشروط؛ زودترین روز محافظه‌کارانه ۷ مارس ۲۰۲۷ فقط با اثبات public history از ۶ سپتامبر ۲۰۲۶ و فعالیت/کاربرد پژوهشی واقعی. گذر زمان به‌تنهایی eligibility را تضمین نمی‌کند. history مصنوعی نساز.

## قالب تحویل نهایی ایجنت

1. لینک manuscript، PDF، editable source، worked example، manifest و execution log.
2. جدول هر مرحله: completed / blocked / not performed همراه شاهد؛ بدون واژهٔ PASS کلی برای علم.
3. فهرست exact claims حفظ‌شده و تأیید unchanged بودن داده‌ها/thresholds.
4. نتایج واقعی tests/build/visual review/clean install، و محدودیت آزمون‌ها.
5. branch، commit SHA و remote SHA؛ تغییرات نامرتبط باقی‌مانده.
6. فقط کارهای باقی‌ماندهٔ نویسنده: تأیید علمی/declarations، بستن شرط مالی، upload revision و submission نهایی. هیچ‌کدام را انجام‌شده تلقی نکن.
