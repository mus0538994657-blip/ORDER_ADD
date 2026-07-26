from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# تهيئة SQLAlchemy
db = SQLAlchemy()

# تهيئة LoginManager
login_manager = LoginManager()

# نموذج المستخدم
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# نموذج الصنف
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    default_price = db.Column(db.Float, nullable=True, default=0.0)
    orders = db.relationship('Order', backref='category', lazy=True)

# نموذج الطلب
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    car_make = db.Column(db.String(100), nullable=True)
    car_model = db.Column(db.String(100), nullable=True)
    car_year = db.Column(db.String(10), nullable=True)
    plate_number = db.Column(db.String(30), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(30), nullable=False, default='قيد الانتظار')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workshop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ORDER_STATUSES'] = ['قيد الانتظار', 'قيد التنفيذ', 'مكتمل', 'ملغي']
    app.config['WORKSHOP_NAME'] = 'ورشة تركيب زجاج المركبات'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    
    # استيراد البلوبريتات
    from blueprints.auth_bp import auth_bp
    from blueprints.orders_bp import orders_bp
    from blueprints.categories_bp import categories_bp
    from blueprints.reports_bp import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(reports_bp)
    
    # الصفحة الرئيسية
    @app.route('/')
    def index():
        total_orders = Order.query.count()
        pending = Order.query.filter_by(status='قيد الانتظار').count()
        in_progress = Order.query.filter_by(status='قيد التنفيذ').count()
        completed = Order.query.filter_by(status='مكتمل').count()
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        return render_template(
            'index.html',
            total_orders=total_orders,
            pending=pending,
            in_progress=in_progress,
            completed=completed,
            recent_orders=recent_orders
        )
    
    with app.app_context():
        db.create_all()
        # إضافة بيانات افتراضية
        if Category.query.count() == 0:
            categories = [
                ('زجاج أمامي', 'تركيب أو تبديل الزجاج الأمامي', 350.0),
                ('زجاج خلفي', 'تركيب أو تبديل الزجاج الخلفي', 250.0),
                ('زجاج جانبي', 'تركيب أو تبديل الزجاج الجانبي', 180.0),
                ('فتحة سقف', 'تركيب أو تبديل زجاج فتحة السقف', 400.0),
                ('تظليل زجاج', 'خدمة تظليل الزجاج', 150.0),
            ]
            for name, desc, price in categories:
                db.session.add(Category(name=name, description=desc, default_price=price))
            db.session.commit()
        
        # إنشاء مستخدم افتراضي
        if User.query.filter_by(username='admin').first() is None:
            admin = User(
                username='admin',
                email='admin@workshop.com',
                full_name='مدير النظام',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("🚗 نظام إدارة ورشة تركيب زجاج المركبات")
    print("=" * 50)
    print("🌐 تشغيل على: http://localhost:5000")
    print("👤 المستخدم الافتراضي: admin")
    print("🔑 كلمة المرور: admin123")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)