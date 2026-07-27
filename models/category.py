from datetime import datetime
from extensions import db


class Category(db.Model):
    """نموذج أصناف الخدمات (أنواع الزجاج)."""

    __tablename__ = 'categories'

    id            = db.Column(db.Integer, primary_key=True)
    code          = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name          = db.Column(db.String(120), unique=True, nullable=False)
    description   = db.Column(db.String(300), nullable=True)
    unit          = db.Column(db.String(30), nullable=False, default='قطعة')
    default_price = db.Column(db.Float, nullable=False, default=0.0)
    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # العلاقات
    orders      = db.relationship('Order', backref='category', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='category', lazy='dynamic')

    @property
    def active_orders_count(self) -> int:
        from models.order import Order
        return self.orders.filter(
            Order.status.notin_(['مكتمل', 'ملغي'])
        ).count()

    @property
    def total_orders_count(self) -> int:
        return self.orders.count()

    def to_dict(self) -> dict:
        return {
            'id':            self.id,
            'code':          self.code,
            'name':          self.name,
            'description':   self.description or '',
            'unit':          self.unit,
            'default_price': self.default_price,
        }

    def __repr__(self) -> str:
        return f'<Category {self.code} — {self.name}>'
