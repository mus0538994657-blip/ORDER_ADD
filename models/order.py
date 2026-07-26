from datetime import datetime
from extensions import db


class Order(db.Model):
    """نموذج طلبات العمل."""

    __tablename__ = 'orders'

    # ثوابت الحالات
    STATUS_PENDING = 'قيد الانتظار'
    STATUS_IN_PROGRESS = 'قيد التنفيذ'
    STATUS_COMPLETED = 'مكتمل'
    STATUS_CANCELLED = 'ملغي'

    STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_CANCELLED]

    STATUS_COLORS = {
        STATUS_PENDING: 'warning',
        STATUS_IN_PROGRESS: 'info',
        STATUS_COMPLETED: 'success',
        STATUS_CANCELLED: 'danger',
    }

    STATUS_ICONS = {
        STATUS_PENDING: 'bi-clock',
        STATUS_IN_PROGRESS: 'bi-gear-fill',
        STATUS_COMPLETED: 'bi-check-circle-fill',
        STATUS_CANCELLED: 'bi-x-circle-fill',
    }

    # الأعمدة
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=True)
    customer_email = db.Column(db.String(120), nullable=True)
    car_make = db.Column(db.String(100), nullable=True)
    car_model = db.Column(db.String(100), nullable=True)
    car_year = db.Column(db.String(10), nullable=True)
    plate_number = db.Column(db.String(30), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    final_price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(30), nullable=False, default=STATUS_PENDING, index=True)
    notes = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ---------------------------------------------------------------------------
    # Methods
    # ---------------------------------------------------------------------------

    @staticmethod
    def generate_order_number() -> str:
        """يولّد رقم طلب فريد بالصيغة: ORD-YYYY-NNNN."""
        year = datetime.utcnow().year
        count = Order.query.filter(
            db.extract('year', Order.created_at) == year
        ).count()
        return f'ORD-{year}-{count + 1:04d}'

    def calculate_final_price(self) -> None:
        """يحسب السعر النهائي بعد خصم الخصم."""
        self.final_price = max(0.0, self.price - self.discount)

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
    def car_full(self) -> str:
        """وصف السيارة كاملاً في نص واحد."""
        parts = filter(None, [self.car_make, self.car_model, self.car_year])
        return ' '.join(parts) or '—'

    def __repr__(self) -> str:
        return f'<Order {self.order_number}>'
