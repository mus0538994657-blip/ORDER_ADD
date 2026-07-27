"""تعبئة قاعدة البيانات بالبيانات الافتراضية."""
from extensions import db
from models.user import User
from models.category import Category
from models.customer import Customer
from models.vehicle import Vehicle


def run_seeds() -> None:
    _seed_categories()
    _seed_admin()
    _seed_sample_customers()


def _seed_categories() -> None:
    if Category.query.count():
        return
    defaults = [
        # (code,  name,          description,                              unit,    default_price)
        ('GLS-001', 'زجاج أمامي',  'تركيب أو تبديل الزجاج الأمامي للمركبة',  'قطعة', 350.0),
        ('GLS-002', 'زجاج خلفي',   'تركيب أو تبديل الزجاج الخلفي للمركبة',   'قطعة', 250.0),
        ('GLS-003', 'زجاج جانبي',  'تركيب أو تبديل الزجاج الجانبي',          'قطعة', 180.0),
        ('GLS-004', 'فتحة سقف',    'تركيب أو تبديل زجاج فتحة السقف',         'قطعة', 400.0),
        ('GLS-005', 'تظليل زجاج',  'خدمة تظليل الزجاج بأفضل الأنواع',        'متر',  150.0),
    ]
    for code, name, desc, unit, price in defaults:
        db.session.add(Category(
            code=code, name=name, description=desc,
            unit=unit, default_price=price,
        ))
    db.session.commit()


def _seed_admin() -> None:
    if User.query.filter_by(username='admin').first():
        return
    admin = User(
        username='admin',
        email='admin@workshop.local',
        full_name='مدير النظام',
        is_admin=True,
    )
    admin.set_password('Admin@1234')
    db.session.add(admin)
    db.session.commit()


def _seed_sample_customers() -> None:
    """بيانات تجريبية — تُضاف مرة واحدة فقط."""
    if Customer.query.count():
        return
    sample = [
        ('أحمد محمد', '0501234567', 'ahmed@example.com'),
        ('سارة علي', '0559876543', None),
        ('خالد إبراهيم', '0531112233', 'khalid@example.com'),
    ]
    for name, phone, email in sample:
        customer = Customer(name=name, phone=phone, email=email)
        db.session.add(customer)
        db.session.flush()  # للحصول على id قبل الـ commit

        # إضافة مركبة لكل عميل
        vehicle = Vehicle(
            customer_id=customer.id,
            make='تويوتا',
            model='كامري',
            year='2020',
            plate_number=f'ABC{customer.id:03d}',
        )
        db.session.add(vehicle)

    db.session.commit()

