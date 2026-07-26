"""تعبئة قاعدة البيانات بالبيانات الافتراضية."""
from extensions import db
from models.user import User
from models.category import Category


def run_seeds() -> None:
    _seed_categories()
    _seed_admin()


def _seed_categories() -> None:
    if Category.query.count():
        return
    defaults = [
        ('زجاج أمامي', 'تركيب أو تبديل الزجاج الأمامي للمركبة', 350.0),
        ('زجاج خلفي', 'تركيب أو تبديل الزجاج الخلفي للمركبة', 250.0),
        ('زجاج جانبي', 'تركيب أو تبديل الزجاج الجانبي', 180.0),
        ('فتحة سقف', 'تركيب أو تبديل زجاج فتحة السقف', 400.0),
        ('تظليل زجاج', 'خدمة تظليل الزجاج بأفضل الأنواع', 150.0),
    ]
    for name, desc, price in defaults:
        db.session.add(Category(name=name, description=desc, default_price=price))
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
