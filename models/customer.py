from datetime import datetime
from extensions import db


class Customer(db.Model):
    """عميل الورشة — قد يمتلك عدة مركبات وطلبات."""

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # العلاقات
    vehicles = db.relationship('Vehicle', backref='customer',
                               lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    @property
    def vehicles_count(self) -> int:
        return self.vehicles.count()

    @property
    def orders_count(self) -> int:
        return self.orders.count()

    @property
    def total_spent(self) -> float:
        from models.order import Order
        result = db.session.query(
            db.func.sum(Order.final_price)
        ).filter_by(customer_id=self.id, status=Order.STATUS_COMPLETED).scalar()
        return result or 0.0

    @property
    def display_phone(self) -> str:
        return self.phone or '—'

    def __repr__(self) -> str:
        return f'<Customer {self.name}>'
