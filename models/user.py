from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager


class User(UserMixin, db.Model):
    """نموذج المستخدم — يدعم تعدد الأدوار."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # العلاقات
    orders = db.relationship('Order', backref='created_by', lazy='dynamic',
                             foreign_keys='Order.created_by_id')

    def set_password(self, password: str) -> None:
        """تشفير كلمة المرور باستخدام bcrypt عبر Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """التحقق من كلمة المرور."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self) -> None:
        """تحديث وقت آخر تسجيل دخول."""
        self.last_login_at = datetime.utcnow()
        db.session.commit()

    @property
    def display_name(self) -> str:
        return self.full_name or self.username

    def __repr__(self) -> str:
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
