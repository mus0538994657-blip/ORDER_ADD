# نظام إدارة ورشة تركيب زجاج المركبات

نظام ويب متكامل مبني بـ **Flask** لإدارة عمليات ورشة تركيب وتبديل زجاج المركبات — يشمل إدارة العملاء، المركبات، الطلبات، الأصناف، التصنيفات، الوحدات، التقارير، وواجهة API كاملة.

---

## المميزات الرئيسية

| الميزة | التفاصيل |
|---|---|
| 🔐 المصادقة | تسجيل دخول آمن بـ Flask-Login + CSRF |
| 👥 العملاء | CRUD كامل مع سجل مركبات لكل عميل |
| 🚗 المركبات | ربط كل مركبة بعميل (الموديل، السنة، اللوحة) |
| 📋 الطلبات | بنود متعددة لكل طلب (جدول order_items) |
| 📦 الأصناف | كود فريد + وحدة + تصنيف + سعر افتراضي |
| 🗂️ التصنيفات | تصنيف الأصناف في مجموعات (CategoryGroup) |
| 📏 الوحدات | إدارة وحدات القياس (Unit) مع CRUD كامل |
| 📊 التقارير | تصدير Excel وPDF مع ترشيح متقدم |
| 🔔 الإشعارات | إرسال SMS عبر Twilio عند تحديث الطلب |
| 🌐 API | 6 endpoints JSON لـ `/api/v1/` |
| 🛡️ الحماية | Rate Limiting، CSRF، SQL Injection prevention |

---

## متطلبات التشغيل

- Python 3.10+
- pip

---

## التثبيت والتشغيل

```bash
# 1. استنساخ المشروع
git clone https://github.com/mus0538994657-blip/ORDER_ADD.git
cd ORDER_ADD

# 2. إنشاء بيئة افتراضية
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. إعداد متغيرات البيئة
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS

# 5. تشغيل التطبيق
python run.py
```

افتح المتصفح على: `http://localhost:5000`

**بيانات الدخول الافتراضية:**
- المستخدم: `admin`
- كلمة المرور: `Admin@1234`

> عند أول تشغيل يُنشئ النظام قاعدة البيانات تلقائياً ويُضيف بيانات تجريبية (7 وحدات، 6 تصنيفات، 5 أصناف، 3 عملاء).

> **ترقية Schema تلقائية** — عند إضافة أعمدة جديدة للنماذج، يُطبّقها النظام تلقائياً على قاعدة البيانات الموجودة عبر `_apply_incremental_migrations()` دون فقدان البيانات.

---

## متغيرات البيئة (.env)

```dotenv
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///workshop.db
WORKSHOP_NAME=ورشة الزجاج الحديثة

# Twilio (اختياري - للإشعارات)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+966500000000
```

---

## بنية المشروع

```
ORDER_ADD/
├── app.py                      # Application Factory + incremental migration
├── run.py                      # نقطة التشغيل
├── config.py                   # إعدادات البيئات
├── extensions.py               # DB, Login, CSRF, Limiter, Cache
├── seeds.py                    # بيانات افتراضية (وحدات، تصنيفات، أصناف، عملاء)
├── requirements.txt
│
├── models/
│   ├── user.py                 # المستخدم
│   ├── customer.py             # العميل
│   ├── vehicle.py              # المركبة
│   ├── unit.py                 # وحدات القياس (جديد)
│   ├── category_group.py       # تصنيفات الأصناف (جديد)
│   ├── category.py             # الصنف (code، unit، group_id)
│   ├── order.py                # الطلب
│   └── order_item.py           # بنود الطلب (snapshot)
│
├── blueprints/
│   ├── auth/                   # تسجيل الدخول والخروج
│   ├── main/                   # لوحة التحكم الرئيسية
│   ├── customers/              # إدارة العملاء والمركبات
│   ├── orders/                 # إدارة الطلبات وبنودها
│   ├── categories/             # إدارة الأصناف + الوحدات + التصنيفات
│   ├── reports/                # التقارير (Excel / PDF)
│   └── api/                    # REST API v1
│
├── utils/
│   ├── pdf.py                  # توليد PDF بالعربية (A4 مضبوط، 10pt)
│   └── notifications.py        # Twilio SMS
│
├── templates/
│   ├── base.html               # القالب الرئيسي (Bootstrap 5 RTL)
│   ├── index.html              # لوحة التحكم
│   ├── auth/
│   ├── customers/
│   ├── orders/
│   │   ├── list.html
│   │   ├── form.html           # نموذج الطلب مع جدول بنود ديناميكي
│   │   └── detail.html         # تفاصيل الطلب مع جدول البنود
│   ├── categories/
│   │   ├── list.html           # جدول مع بحث وفلتر وترقيم صفحات
│   │   ├── form.html           # إضافة/تعديل (code، name، group، unit، price)
│   │   ├── detail.html         # تفاصيل الصنف + آخر الطلبات
│   │   ├── units.html          # إدارة الوحدات (CRUD مدمج)
│   │   └── groups.html         # إدارة التصنيفات (CRUD + Modal تعديل)
│   ├── reports/
│   └── errors/                 # 403 / 404 / 429 / 500
│
└── static/
    ├── css/main.css            # IBM Plex Sans Arabic + Design Tokens
    └── js/main.js
```

---

## المسارات الرئيسية

### واجهة المستخدم

| المسار | الوصف |
|---|---|
| `/` | لوحة التحكم |
| `/customers` | قائمة العملاء |
| `/customers/add` | إضافة عميل |
| `/customers/view/<id>` | تفاصيل العميل ومركباته |
| `/customers/edit/<id>` | تعديل بيانات العميل |
| `/orders` | قائمة الطلبات |
| `/orders/add` | إضافة طلب جديد (بنود متعددة) |
| `/orders/<id>` | تفاصيل الطلب مع جدول البنود |
| `/orders/<id>/edit` | تعديل الطلب |
| `/orders/<id>/status` | تحديث حالة الطلب (AJAX POST) |
| `/orders/<id>/export/pdf` | تصدير الطلب PDF (فاتورة A4 RTL) |
| `/orders/<id>/export/excel` | تصدير الطلب Excel (RTL مع بيانات العميل والمركبة) |
| `/categories` | إدارة الأصناف (جدول + بحث + فلتر) |
| `/categories/add` | إضافة صنف جديد |
| `/categories/<id>` | تفاصيل الصنف |
| `/categories/<id>/edit` | تعديل الصنف |
| `/categories/<id>/toggle` | تفعيل/تعطيل الصنف |
| `/categories/units` | إدارة وحدات القياس |
| `/categories/groups` | إدارة التصنيفات |
| `/reports` | التقارير |
| `/reports/export/excel` | تصدير Excel |
| `/reports/export/pdf` | تصدير PDF |

### REST API v1

| المسار | الوصف |
|---|---|
| `GET /api/v1/orders` | قائمة الطلبات (JSON) |
| `GET /api/v1/customers` | قائمة العملاء (JSON) |
| `GET /api/v1/customers/<id>/vehicles` | مركبات عميل محدد (AJAX) |
| `GET /api/v1/vehicles` | قائمة المركبات (JSON) |
| `GET /api/v1/stats/dashboard` | إحصائيات لوحة التحكم |
| `GET /api/v1/categories/search?code=GLS-001` | بحث بكود الصنف (AJAX) |
| `GET /api/v1/categories/search?q=زجاج` | بحث جزئي في الاسم/الكود |

---

## نماذج قاعدة البيانات

```
users            — المستخدمون (id, username, email, password_hash, is_admin)
customers        — العملاء (id, name, phone, email, address, is_active)
vehicles         — المركبات (id, customer_id, make, model, year, plate_number)
units            — وحدات القياس (id, name, is_active)
category_groups  — تصنيفات الأصناف (id, name, description, is_active)
categories       — الأصناف (id, code*, name*, group_id, unit, default_price, is_active)
orders           — الطلبات (id, order_number*, customer_id, vehicle_id, price, discount, status)
order_items      — بنود الطلب (id, order_id, category_id, code, name, unit, quantity, unit_price, total)
```

`*` = unique index

---

## التقنيات المستخدمة

| الطبقة | التقنية |
|---|---|
| Backend | Flask 2.3 + SQLAlchemy |
| قاعدة البيانات | SQLite (قابل للترقية إلى PostgreSQL) |
| المصادقة | Flask-Login + CSRF (Flask-WTF) |
| Frontend | Bootstrap 5 RTL + **IBM Plex Sans Arabic** |
| التنسيق | Design Tokens (`--ab-primary: #00663d`) |
| التقارير | ReportLab PDF (A4 مضبوط، 10pt) + OpenPyXL Excel |
| الإشعارات | Twilio API |
| الحماية | Flask-Limiter (Rate Limiting) |

---

## نظام التصميم (Design System)

الواجهة مبنية على متغيرات CSS موحّدة:

```css
--ab-primary:        #00663d   /* اللون الرئيسي */
--ab-primary-dark:   #0b7e3e   /* hover */
--ab-secondary:      #E0F5EC   /* خلفيات فاتحة */
--ab-system-success: #006604
--ab-system-warning: #f6c244
--ab-system-error:   #af0818
```

الخط الأساسي: **IBM Plex Sans Arabic** (Google Fonts، أوزان 300–700) — مُطبَّق على جميع عناصر الصفحة.

---

## تقارير PDF

- **A4 صارم** — الأعمدة تملأ العرض المتاح بالضبط (`CONTENT_W = A4 - 2 × margin`)
- **هيدر منظم** على كل صفحة: شريط أخضر (اسم الورشة + تاريخ) + شريط فاتح (عنوان التقرير)
- **فوتر** على كل صفحة: رقم الصفحة
- **خط 9pt** موحّد في جسم الجدول مع Paragraph لالتفاف النص
- **`splitByRow=True`** لضمان عدم تجاوز حدود الصفحة
- **تسجيل خطوط عربية**: يبحث عن NotoNaskhArabic → Amiri → Arial → Tahoma (ويندوز/لينكس)
- **خط مائل (italic)** لتاريخ الطباعة عبر `ArabicItalic` (`ariali.ttf`) أو affine shear كـ fallback

### PDF طلب مفرد (`/orders/<id>/export/pdf`)

| القسم | المحتوى |
|---|---|
| هيدر | اسم الورشة (يمين) + تاريخ الطباعة مائل (يسار) + رقم الطلب + الحالة |
| بيانات العميل | يمين الصفحة (RTL-dominant) — الاسم، الهاتف، البريد، العنوان |
| بيانات المركبة | يسار الصفحة — الماركة، الموديل، السنة، اللوحة |
| جدول البنود | RTL حقيقي — **#** يميناً ← **الإجمالي** يساراً |
| ملخص | مجموع + خصم + إجمالي نهائي (شريط أخضر) |
| ملاحظات | إن وجدت |

---

## تفاصيل الطلب (بنود متعددة)

كل طلب يحتوي على جدول `order_items` بالحقول:

| الحقل | النوع | الوصف |
|---|---|---|
| `code` | String | كود الصنف (مثل `GLS-001`) |
| `name` | String | اسم الصنف (snapshot وقت الطلب) |
| `description` | String | وصف الصنف (snapshot) |
| `unit` | String | الوحدة (قطعة، متر...) |
| `quantity` | Float | الكمية |
| `unit_price` | Float | سعر الوحدة |
| `total` | Float | quantity × unit_price |

**سير العمل في نموذج الطلب:**
1. اضغط "إضافة بند" لإضافة صف جديد
2. اكتب كود الصنف مباشرة أو اضغط زر البحث (modal)
3. البيانات تُعبّأ تلقائياً عبر `GET /api/v1/categories/search?code=...`
4. عدّل الكمية والسعر حسب الحاجة
5. الإجمالي يُحسب لحظياً (JavaScript بدون إعادة تحميل)
6. عند الحفظ، ترسل البنود كـ JSON في حقل `items_json`

---

## تصدير الطلب المفرد

من صفحة تفاصيل الطلب `/orders/<id>` تتوفر ثلاثة خيارات:

| الزر | الوظيفة | المسار |
|---|---|---|
| 🖨️ **طباعة** | طباعة الصفحة مباشرة (`window.print()`) مع CSS مخصص | — |
| 📄 **PDF** | فاتورة/أمر عمل A4 بالعربية | `GET /orders/<id>/export/pdf` |
| 📊 **Excel** | ورقة RTL ببيانات العميل والمركبة والبنود | `GET /orders/<id>/export/excel` |

**ملاحظات طباعة الصفحة:**
- `@media print` يُخفي Navbar والأزرار وقسم تغيير الحالة
- رأس طباعة بسيط (اسم الورشة + رقم الطلب) يظهر فقط عند الطباعة
- ألوان الجداول محفوظة بـ `print-color-adjust: exact`

---

## تصميم صفحة تسجيل الدخول

صفحة مستقلة (لا تمتد من base.html) بتصميم Split Panel:

| اللوحة | المحتوى |
|---|---|
| يسار (مخفية على الموبايل) | خلفية متدرجة خضراء + أيقونة + اسم النظام + قائمة 5 ميزات |
| يمين | فورم تسجيل الدخول: حقول بارتفاع 48px، أيقونة مدمجة، زر إظهار/إخفاء كلمة المرور |

- Focus ring بلون `--ab-primary`
- Flash messages بأيقونة ملوّنة
- Navbar غائب تماماً

---

## لوحة التحكم (Dashboard)

تعرض لوحة التحكم الرئيسية:

- **بطاقات KPI** — إجمالي الطلبات، قيد الانتظار، قيد التنفيذ، مكتملة، ملغية، إجمالي الإيرادات
- **نشاط اليوم والأسبوع** — عدد الطلبات وإيرادات اليوم، طلبات الأسبوع، عدد العملاء النشطين
- **توزيع الحالات** — أشرطة تقدم نسبية لكل حالة
- **وصول سريع** — 6 روابط للعمليات الأكثر استخداماً
- **آخر 8 طلبات** — جدول مع الرقم، العميل، المركبة، البنود، الإجمالي، الحالة

### تخطيط الصفحات (Layout)

- **الـ Navbar** يمتد بعرض 100% (لا هوامش)
- **محتوى الصفحات** بهامش 100px على الجانبين (`@media >= 1200px`) للراحة البصرية على الشاشات الكبيرة
  - 48px على الشاشات المتوسطة (768–1199px)
  - 12px على الأجهزة المحمولة (< 768px)

---

## إدارة الأصناف (Catalog)

### الوحدات (`/categories/units`)
- إضافة وحدة جديدة من نموذج مدمج في الصفحة
- تعديل مباشر في الجدول (inline edit)
- حذف الوحدة إذا لم تُستخدم

### التصنيفات (`/categories/groups`)
- إضافة تصنيف جديد (اسم + وصف)
- تعديل عبر Bootstrap Modal
- حذف التصنيف إذا لم يرتبط بأصناف

### الأصناف (`/categories`)
- جدول مع بحث بالكود أو الاسم
- فلتر بالتصنيف والحالة (نشط/معطّل)
- ترقيم صفحات (20 صنف لكل صفحة)
- تفعيل/تعطيل سريع بزر واحد
- نموذج الصنف يدعم `datalist` للوحدات (اختيار أو كتابة حرة)

---

## الأمان

- CSRF Protection على جميع النماذج وطلبات AJAX
- كلمات المرور مشفرة بـ `werkzeug.security` (pbkdf2:sha256)
- Rate Limiting على مسار تسجيل الدخول
- `SECRET_KEY` من متغيرات البيئة فقط
- SQLAlchemy ORM لمنع SQL Injection
- `@login_required` على جميع المسارات الحساسة

---

## حالات الطلب

```
قيد الانتظار  →  قيد التنفيذ  →  مكتمل
                              ↘  ملغي
```

---

## المساهمة

1. Fork المشروع
2. أنشئ branch جديد: `git checkout -b feature/اسم-الميزة`
3. Commit: `git commit -m 'feat: وصف التغيير'`
4. Push: `git push origin feature/اسم-الميزة`
5. افتح Pull Request

---

## الرخصة

هذا المشروع مخصص للاستخدام الداخلي لورشة تركيب زجاج المركبات.