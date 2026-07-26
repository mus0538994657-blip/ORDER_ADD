from datetime import datetime
from extensions import db


class Vehicle(db.Model):
    """مركبة مرتبطة بعميل."""

    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False, index=True)
    make = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(10), nullable=True)
    plate_number = db.Column(db.String(30), nullable=True, index=True)
    color = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # العلاقات
    orders = db.relationship('Order', backref='vehicle', lazy='dynamic')

    @property
    def full_description(self) -> str:
        """وصف كامل للمركبة في نص واحد."""
        parts = filter(None, [self.make, self.model, self.year])
        desc = ' '.join(parts)
        if self.plate_number:
            desc = f'{desc} [{self.plate_number}]'
        return desc.strip() or '—'

    @property
    def label(self) -> str:
        """نص مختصر لعرضه في القوائم."""
        return self.full_description

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'make': self.make or '',
            'model': self.model or '',
            'year': self.year or '',
            'plate_number': self.plate_number or '',
            'color': self.color or '',
            'label': self.label,
        }

    def __repr__(self) -> str:
        return f'<Vehicle {self.full_description}>'
