from extensions import db


class Unit(db.Model):
    """وحدات القياس — قطعة، متر، مجموعة ..."""

    __tablename__ = 'units'

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(50), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f'<Unit {self.name}>'
