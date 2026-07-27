# نظام إدارة ورشة تركيب زجاج المركبات

نظام ويب متكامل مبني بـ **Flask** لإدارة عمليات ورشة تركيب وتبديل زجاج المركبات — يشمل إدارة العملاء، المركبات، الطلبات، الأصناف، التقارير، وواجهة API كاملة.

---

## المميزات الرئيسية

| الميزة | التفاصيل |
|---|---|
| 🔐 المصادقة | تسجيل دخول آمن بـ Flask-Login + CSRF |
| 👥 العملاء | CRUD كامل مع سجل مركبات لكل عميل |
| 🚗 المركبات | ربط كل مركبة بعميل (الموديل، السنة، اللوحة) |
| 📋 الطلبات | بنود متعددة لكل طلب (جدول order_items) |
| 📦 الأصناف | كود فريد + وحدة + سعر افتراضي |
| 📊 التقارير | تصدير Excel وPDF مع ترشيح متقدم |
| 🔔 الإشعارات | إرسال SMS عبر Twilio عند تحديث الطلب |
| 🌐 API | 5 endpoints JSON لـ `/api/v1/` |
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
# ثم عدّل .env بقيمك

# 5. تشغيل التطبيق
python run.py
```

افتح المتصفح على: `http://localhost:5000`

**بيانات الدخول الافتراضية:**
- المستخدم: `admin`
- كلمة المرور: `Admin@1234`

> عند أول تشغيل يُنشئ النظام قاعدة البيانات تلقائياً ويُضيف بيانات تجريبية.

---

## متغيرات البيئة (.env)

```dotenv
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///workshop.db
WORKSHOP_NAME=ورشة الزجاج الحديثة

# Twilio (اختياري - للاشعارات)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+966500000000
```

---

## بنية المشروع

```
ORDER_ADD/
├── app.py                      # Application Factory
├── run.py                      # نقطة التشغيل
├── config.py                   # اعدادات البيئات
├── extensions.py               # DB, Login, CSRF, Limiter
├── seeds.py                    # بيانات تجريبية
├── requirements.txt
│
├── models/
│   ├── user.py                 # نموذج المستخدم
│   ├── customer.py             # نموذج العميل
│   ├── vehicle.py              # نموذج المركبة
│   ├── category.py             # نموذج الصنف
│   ├── order.py                # نموذج الطلب
│   └── order_item.py           # نموذج بنود الطلب (جديد)
│
├── blueprints/
│   ├── auth/                   # تسجيل الدخول والخروج
│   ├── main/                   # لوحة التحكم الرئيسية
│   ├── customers/              # ادارة العملاء والمركبات
│   ├── orders/                 # ادارة الطلبات
│   ├── categories/             # ادارة الاصناف
│   ├── reports/                # التقارير (Excel / PDF)
│   └── api/                    # REST API v1
│
├── utils/
│   ├── pdf.py                  # توليد PDF بالعربية (A4 مضبوط)
│   └── notifications.py        # Twilio SMS
│
├── templates/
│   ├── base.html               # القالب الرئيسي (Bootstrap 5 RTL)
│   ├── index.html              # لوحة التحكم
│   ├── auth/
│   ├── customers/
│   ├── orders/
│   ├── categories/
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
| `/customers/add` | اضافة عميل |
| `/customers/view/<id>` | تفاصيل العميل ومركباته |
| `/customers/edit/<id>` | تعديل بيانات العميل |
| `/customers/view/<id>/vehicles/add` | اضافة مركبة للعميل |
| `/orders` | قائمة الطلبات |
| `/orders/add` | اضافة طلب جديد |
| `/orders/edit/<id>` | تعديل الطلب |
| `/orders/status/<id>` | تحديث حالة الطلب |
| `/categories` | ادارة الاصناف |
| `/reports` | التقارير |
| `/reports/export/excel` | تصدير Excel |
| `/reports/export/pdf` | تصدير PDF |

### REST API v1

| المسار | الوصف |
|---|---|
| `GET /api/v1/orders` | قائمة الطلبات (JSON) |
| `GET /api/v1/customers` | قائمة العملاء (JSON) |
| `GET /api/v1/vehicles` | قائمة المركبات (JSON) |
| `GET /api/v1/stats/dashboard` | احصائيات لوحة التحكم |
| `GET /api/v1/categories/search?code=GLS-001` | بحث بكود الصنف (AJAX) |
| `GET /api/v1/categories/search?q=زجاج` | بحث جزئي في الاسم/الكود |

---

## التقنيات المستخدمة

| الطبقة | التقنية |
|---|---|
| Backend | Flask 2.3 + SQLAlchemy |
| قاعدة البيانات | SQLite (قابل للترقية الى PostgreSQL) |
| المصادقة | Flask-Login + CSRF (Flask-WTF) |
| Frontend | Bootstrap 5 RTL + **IBM Plex Sans Arabic** |
| التنسيق | Design Tokens (`--ab-primary #00663d`) |
| التقارير | ReportLab PDF (A4 مضبوط، 10pt) + OpenPyXL Excel |
| الاشعارات | Twilio API |
| الحماية | Flask-Limiter (Rate Limiting) |

---

## نظام التصميم (Design System)

الواجهة مبنية على متغيرات CSS موحّدة:

```css
--ab-primary: #00663d        /* اللون الرئيسي */
--ab-primary-dark: #0b7e3e   /* hover */
--ab-secondary: #E0F5EC      /* خلفيات فاتحة */
--ab-system-success: #006604
--ab-system-warning: #f6c244
--ab-system-error: #af0818
```

الخط الاساسي: **IBM Plex Sans Arabic** (Google Fonts) — مُطبَّق على جميع عناصر الصفحة.

---

## تقارير PDF

- **A4 صارم** — الاعمدة تملا العرض المتاح بالضبط (`CONTENT_W = A4 - 2 × margin`)
- **هيدر منظم** على كل صفحة: شريط اخضر (اسم الورشة + تاريخ) + شريط فاتح (عنوان التقرير)
- **فوتر** على كل صفحة: رقم الصفحة يسارا
- **خط 10pt** موحّد في جسم الجدول
- **`splitByRow=True`** لضمان عدم تجاوز حدود الصفحة

---

## تفاصيل الطلب (بنود متعددة)

كل طلب يحتوي على جدول `order_items` بالبنود التالية:

| الحقل | النوع | الوصف |
|---|---|---|
| `code` | String | كود الصنف (مثل `GLS-001`) |
| `name` | String | اسم الصنف (snapshot) |
| `description` | String | وصف الصنف (snapshot) |
| `unit` | String | الوحدة (قطعة، متر، ساعة...) |
| `quantity` | Float | الكمية |
| `unit_price` | Float | سعر الوحدة |
| `total` | Float | quantity x unit_price |

**سير العمل في نموذج الطلب:**
1. اكتب كود الصنف في الحقل او اضغط زر البحث (modal)
2. البيانات تُعبّأ تلقائياً عبر `GET /api/v1/categories/search?code=...`
3. عدّل الكمية والسعر حسب الحاجة
4. اضغط "اضافة بند" لإضافة المزيد
5. الإجمالي يُحسب لحظياً (JavaScript)
6. عند الحفظ، ترسل البنود كـ JSON في حقل `items_json`

---



- CSRF Protection على جميع النماذج
- كلمات المرور مشفرة بـ `werkzeug.security`
- Rate Limiting على مسار تسجيل الدخول
- `SECRET_KEY` من متغيرات البيئة فقط
- SQLAlchemy ORM لمنع SQL Injection
- `@login_required` على جميع المسارات الحساسة

---

## حالات الطلب

```
pending     --> قيد الانتظار
in_progress --> قيد التنفيذ
completed   --> مكتمل
cancelled   --> ملغي
```

---

## المساهمة

1. Fork المشروع
2. انشئ branch جديد: `git checkout -b feature/اسم-الميزة`
3. Commit: `git commit -m 'feat: وصف التغيير'`
4. Push: `git push origin feature/اسم-الميزة`
5. افتح Pull Request

---

## الرخصة

هذا المشروع مخصص للاستخدام الداخلي لورشة تركيب زجاج المركبات.

