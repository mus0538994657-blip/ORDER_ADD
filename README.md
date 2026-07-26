# نظام إدارة ورشة تركيب زجاج المركبات

نظام ويب متكامل مبني بـ **Flask** لإدارة عمليات ورشة تركيب وتبديل زجاج المركبات — يشمل إدارة العملاء، المركبات، الطلبات، الأصناف، التقارير، وواجهة API كاملة.

---

## المميزات الرئيسية

| الميزة | التفاصيل |
|---|---|
| 🔐 المصادقة | تسجيل دخول آمن بـ Flask-Login + CSRF |
| 👥 العملاء | CRUD كامل مع سجل مركبات لكل عميل |
| 🚗 المركبات | ربط كل مركبة بعميل (الموديل، السنة، اللوحة) |
| 📋 الطلبات | إنشاء وتتبع الطلبات مع حالات متعددة |
| 📦 الأصناف | أنواع الزجاج مع أسعار افتراضية |
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

# Twilio (اختياري — للإشعارات)
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
├── config.py                   # إعدادات البيئات
├── extensions.py               # DB, Login, CSRF, Limiter
├── seeds.py                    # بيانات تجريبية
├── requirements.txt
│
├── models/
│   ├── user.py                 # نموذج المستخدم
│   ├── customer.py             # نموذج العميل
│   ├── vehicle.py              # نموذج المركبة
│   ├── category.py             # نموذج الصنف
│   └── order.py                # نموذج الطلب
│
├── blueprints/
│   ├── auth/                   # تسجيل الدخول والخروج
│   ├── main/                   # لوحة التحكم الرئيسية
│   ├── customers/              # إدارة العملاء والمركبات
│   ├── orders/                 # إدارة الطلبات
│   ├── categories/             # إدارة الأصناف
│   ├── reports/                # التقارير (Excel / PDF)
│   └── api/                    # REST API v1
│
├── utils/
│   ├── pdf.py                  # توليد PDF بالعربية
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
| `/customers/add` | إضافة عميل |
| `/customers/view/<id>` | تفاصيل العميل ومركباته |
| `/customers/edit/<id>` | تعديل بيانات العميل |
| `/customers/view/<id>/vehicles/add` | إضافة مركبة للعميل |
| `/orders` | قائمة الطلبات |
| `/orders/add` | إضافة طلب جديد |
| `/orders/edit/<id>` | تعديل الطلب |
| `/orders/status/<id>` | تحديث حالة الطلب |
| `/categories` | إدارة الأصناف |
| `/reports` | التقارير |
| `/reports/export/excel` | تصدير Excel |
| `/reports/export/pdf` | تصدير PDF |

### REST API v1

| المسار | الوصف |
|---|---|
| `GET /api/v1/orders` | قائمة الطلبات (JSON) |
| `GET /api/v1/customers` | قائمة العملاء (JSON) |
| `GET /api/v1/vehicles` | قائمة المركبات (JSON) |
| `GET /api/v1/stats/dashboard` | إحصائيات لوحة التحكم |
| `GET /api/v1/customers/<id>/vehicles` | مركبات عميل محدد |

---

## التقنيات المستخدمة

| الطبقة | التقنية |
|---|---|
| Backend | Flask 2.3 + SQLAlchemy |
| قاعدة البيانات | SQLite (قابل للترقية إلى PostgreSQL) |
| المصادقة | Flask-Login + CSRF (Flask-WTF) |
| Frontend | Bootstrap 5 RTL + IBM Plex Sans Arabic |
| التقارير | ReportLab (PDF) + OpenPyXL (Excel) |
| الإشعارات | Twilio API |
| الحماية | Flask-Limiter (Rate Limiting) |

---

## الأمان

- ✅ CSRF Protection على جميع النماذج
- ✅ كلمات المرور مشفرة بـ `werkzeug.security`
- ✅ Rate Limiting على مسار تسجيل الدخول
- ✅ `SECRET_KEY` من متغيرات البيئة فقط
- ✅ SQLAlchemy ORM لمنع SQL Injection
- ✅ `@login_required` على جميع المسارات الحساسة

---

## حالات الطلب

```
pending     → قيد الانتظار
in_progress → قيد التنفيذ
completed   → مكتمل
cancelled   → ملغي
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
