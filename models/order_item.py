"""
نموذج بنود الطلب (تفاصيل الطلب).
كل طلب يمكن أن يحتوي على عدة بنود.
البيانات مُخزَّنة كـ snapshot (لا تتأثر بتعديل الصنف لاحقاً).
"""
from extensions import db


class OrderItem(db.Model):
    """بند واحد داخل الطلب."""

    __tablename__ = 'order_items'

    id          = db.Column(db.Integer, primary_key=True)
    order_id    = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'),
                            nullable=False, index=True)

    # snapshot من الصنف وقت إنشاء الطلب
    category_id   = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'),
                               nullable=True, index=True)
    code          = db.Column(db.String(30),  nullable=False)   # كود الصنف
    name          = db.Column(db.String(120), nullable=False)   # اسم الصنف
    description   = db.Column(db.String(300), nullable=True)    # وصف الصنف
    unit          = db.Column(db.String(30),  nullable=False, default='قطعة')

    # التسعير
    quantity   = db.Column(db.Float, nullable=False, default=1.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total      = db.Column(db.Float, nullable=False, default=0.0)

    def compute_total(self) -> None:
        """يحسب الإجمالي = الكمية × سعر الوحدة."""
        self.total = round(self.quantity * self.unit_price, 2)

    def to_dict(self) -> dict:
        return {
            'id':          self.id,
            'code':        self.code,
            'name':        self.name,
            'description': self.description or '',
            'unit':        self.unit,
            'quantity':    self.quantity,
            'unit_price':  self.unit_price,
            'total':       self.total,
        }

    def __repr__(self) -> str:
        return f'<OrderItem {self.code} × {self.quantity}>'
