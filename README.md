# منصة AZDA لمؤشر الكفاءة البحرية (MCI Platform)

منصة ويب شاملة لإدارة معهد AZDA للتدريب البحري: المتدربون، الكورسات، الحضور، تقييمات الكفاءة، الشهادات، واحتساب **مؤشر الكفاءة البحرية (MCI)** لكل متدرب على مقياس 0-1000.

## المكدس التقني

- **Backend:** FastAPI (Python 3.12)
- **قاعدة البيانات:** PostgreSQL + SQLAlchemy 2.0 + Alembic (migrations)
- **المصادقة:** JWT (access + refresh tokens) مع صلاحيات حسب الدور (Role-Based Access Control)
- **النشر:** Docker / docker-compose (جاهز لـ Railway أيضًا)

## هيكل المشروع

```
azda-mci-platform/
├── app/
│   ├── core/          # الإعدادات، الاتصال بقاعدة البيانات، الأمان، الصلاحيات
│   ├── models/         # 12 كيان بيانات (SQLAlchemy)
│   ├── schemas/        # نماذج التحقق من البيانات (Pydantic)
│   ├── routers/        # نقاط الوصول (Endpoints) لكل وحدة
│   ├── services/        # منطق الأعمال - أهمها حساب MCI Score
│   └── utils/           # أدوات مساعدة (seed script)
├── alembic/              # ملفات ترحيل قاعدة البيانات
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## الكيانات الـ 12

| # | الكيان | الوصف |
|---|--------|-------|
| 1 | User | مستخدمو النظام (أدمن، مدير تدريب، مدرب، مقيّم...) |
| 2 | OrganizationUnit | الجهة/السفينة/الشركة التابع لها المتدرب |
| 3 | Trainee | بيانات المتدربين الأساسية |
| 4 | Course | تعريف الكورس (قالب عام) |
| 5 | CourseSession | دورة فعلية بتاريخ ومكان ومدرب |
| 6 | Enrollment | تسجيل متدرب في دورة |
| 7 | Attendance | سجل الحضور اليومي |
| 8 | CompetencyCriteria | معايير الكفاءة الديناميكية لكل كورس |
| 9 | CompetencyAssessment | نتيجة تقييم متدرب على معيار معيّن |
| 10 | Certificate | تتبع الشهادات الصادرة |
| 11 | MCIScore | لقطات (snapshots) تاريخية لمؤشر MCI |
| 12 | AuditLog / FeedbackSurvey | سجل تدقيق + استبيانات رضا المتدربين |

## نظام حساب مؤشر MCI (0 - 1000)

يُحسب المؤشر من 4 مكوّنات قابلة للتعديل في `app/services/mci_scoring.py`:

| المكوّن | الوزن | الأساس |
|---------|-------|--------|
| الحضور | 250 نقطة (25%) | نسبة الحضور الفعلي من كل السجلات |
| الكفاءة | 400 نقطة (40%) | متوسط درجات التقييمات + نسبة "كفء" |
| الشهادات السارية | 250 نقطة (25%) | نسبة الشهادات الصادرة غير المنتهية |
| الحداثة | 100 نقطة (10%) | مدى حداثة آخر نشاط تدريبي (تتلاشى خلال 24 شهر) |

كل حساب يُحفظ كسجل تاريخي في جدول `mci_scores` مع تفاصيل شفافة (`breakdown`) لكل مكوّن، لسهولة التدقيق والمراجعة.

## التشغيل محليًا

### 1. باستخدام Docker (الأسهل)

```bash
cp .env.example .env
docker compose up --build
```

بعد التشغيل، نفّذ الـ migration الأولى وأنشئ مستخدم الأدمن:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.utils.seed_admin
```

الـ API متاح على: `http://localhost:8000`
التوثيق التفاعلي (Swagger): `http://localhost:8000/docs`

### 2. بدون Docker

```bash
python -m venv venv
source venv/bin/activate   # على ويندوز: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# عدّل DATABASE_URL في .env ليشير إلى قاعدة بيانات PostgreSQL محلية أو سحابية

alembic revision --autogenerate -m "initial schema"
alembic upgrade head
python -m app.utils.seed_admin

uvicorn app.main:app --reload
```

## النشر على Railway

1. ارفع هذا المشروع إلى GitHub (الخطوات بالأسفل)
2. أنشئ مشروع جديد في Railway واربطه بالـ repo
3. أضف خدمة PostgreSQL من Railway (Add Plugin → PostgreSQL)
4. اضبط متغيرات البيئة `DATABASE_URL` (تلقائيًا من Railway) و`SECRET_KEY`
5. أمر البدء (Start Command): `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. بعد أول نشر، شغّل من تبويب Railway Shell:
   ```bash
   alembic upgrade head
   python -m app.utils.seed_admin
   ```

## رفع المشروع إلى GitHub

```bash
git init
git add .
git commit -m "المشروع الأولي: منصة MCI - الهيكل الكامل"
git branch -M main
git remote add origin https://github.com/Mohamed100000000/azda-marine-system.git
git push -u origin main
```

> ملاحظة: لو الريبو فيه محتوى سابق (مثل اللوجو)، استخدم `git pull origin main --allow-unrelated-histories` قبل الـ push لدمج المحتوى بدل استبداله.

## خارطة الطريق (المراحل القادمة)

- [ ] وحدة التقارير ولوحة التحكم (Dashboards)
- [ ] وحدة الإشعارات (تنبيهات انتهاء الشهادات)
- [ ] وحدة رفع/معالجة ملفات الشهادات (OCR) - ربط مع AZDA AI Certificate Processor
- [ ] واجهة أمامية (Frontend) - React/Next.js
- [ ] استيراد البيانات التاريخية من ملف Attendace_132.xlsx (ETL)

## بيانات الدخول الافتراضية بعد seed_admin

- **البريد:** admin@azda.local
- **كلمة المرور:** ChangeMe123!

⚠️ **غيّرها فورًا بعد أول تسجيل دخول في بيئة الإنتاج.**
