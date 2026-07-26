from datetime import datetime
from extensions import db


class Category(db.Model):
    """نموذج أصناف الخدمات (أنواع الزجاج)."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    default_price = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # العلاقات
    orders = db.relationship('Order', backref='category', lazy='dynamic')

    @property
    def active_orders_count(self) -> int:
        """عدد الطلبات النشطة لهذا الصنف."""
        from models.order import Order
        return self.orders.filter(
            Order.status.notin_(['مكتمل', 'ملغي'])
        ).count()

    @property
    def total_orders_count(self) -> int:
        return self.orders.count()

    def __repr__(self) -> str:
        return f'<Category {self.name}>'
