from datetime import datetime
from extensions import db


class Order(db.Model):
    """نموذج طلبات العمل — مرتبط بعميل ومركبة وبنود متعددة."""

    __tablename__ = 'orders'

    # ثوابت الحالات
    STATUS_PENDING     = 'قيد الانتظار'
    STATUS_IN_PROGRESS = 'قيد التنفيذ'
    STATUS_COMPLETED   = 'مكتمل'
    STATUS_CANCELLED   = 'ملغي'

    STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_CANCELLED]

    STATUS_COLORS = {
        STATUS_PENDING:     'warning',
        STATUS_IN_PROGRESS: 'info',
        STATUS_COMPLETED:   'success',
        STATUS_CANCELLED:   'danger',
    }

    STATUS_ICONS = {
        STATUS_PENDING:     'bi-clock',
        STATUS_IN_PROGRESS: 'bi-gear-fill',
        STATUS_COMPLETED:   'bi-check-circle-fill',
        STATUS_CANCELLED:   'bi-x-circle-fill',
    }

    # الأعمدة
    id           = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # المفاتيح الخارجية
    customer_id   = db.Column(db.Integer, db.ForeignKey('customers.id'),
                              nullable=False, index=True)
    vehicle_id    = db.Column(db.Integer, db.ForeignKey('vehicles.id'),
                              nullable=True, index=True)
    # category_id محتفظ به للتوافق مع الكود القديم (nullable)
    category_id   = db.Column(db.Integer, db.ForeignKey('categories.id'),
                              nullable=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # التسعير (يُحسب من مجموع البنود)
    price      = db.Column(db.Float, nullable=False, default=0.0)   # مجموع البنود
    discount   = db.Column(db.Float, nullable=False, default=0.0)
    final_price = db.Column(db.Float, nullable=False, default=0.0)  # price - discount

    # الحالة والملاحظات
    status = db.Column(db.String(30), nullable=False,
                       default=STATUS_PENDING, index=True)
    notes  = db.Column(db.Text, nullable=True)

    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # بنود الطلب
    items = db.relationship(
        'OrderItem',
        backref='order',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    # ---------------------------------------------------------------------------
    # Methods
    # ---------------------------------------------------------------------------

    @staticmethod
    def generate_order_number() -> str:
        """يولّد رقم طلب فريد بالصيغة: ORD-YYYY-NNNN."""
        year  = datetime.utcnow().year
        count = Order.query.filter(
            db.extract('year', Order.created_at) == year
        ).count()
        return f'ORD-{year}-{count + 1:04d}'

    def recalculate(self) -> None:
        """يُعيد حساب price من مجموع البنود ثم final_price."""
        items_total = sum(item.total for item in self.items.all())
        self.price      = round(items_total, 2)
        self.final_price = round(max(0.0, self.price - self.discount), 2)

    def calculate_final_price(self) -> None:
        """للتوافق مع الكود القديم."""
        self.final_price = round(max(0.0, self.price - self.discount), 2)

    # ---------------------------------------------------------------------------
    # Properties
    # ---------------------------------------------------------------------------

    @property
    def status_color(self) -> str:
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def status_icon(self) -> str:
        return self.STATUS_ICONS.get(self.status, 'bi-circle')

    @property
    def customer_name(self) -> str:
        return self.customer.name if self.customer else '—'

    @property
    def vehicle_info(self) -> str:
        return self.vehicle.full_description if self.vehicle else '—'

    @property
    def items_count(self) -> int:
        return self.items.count()

    def to_dict(self) -> dict:
        return {
            'id':             self.id,
            'order_number':   self.order_number,
            'customer':       self.customer_name,
            'customer_phone': self.customer.phone if self.customer else '',
            'vehicle':        self.vehicle_info,
            'category':       self.category.name if self.category else '',
            'price':          self.price,
            'discount':       self.discount,
            'final_price':    self.final_price,
            'items_count':    self.items_count,
            'status':         self.status,
            'status_color':   self.status_color,
            'notes':          self.notes or '',
            'created_at':     self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }

    def __repr__(self) -> str:
        return f'<Order {self.order_number}>'

