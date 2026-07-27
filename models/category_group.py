from extensions import db


class CategoryGroup(db.Model):
    """تصنيفات الأصناف — زجاج أمامي، زجاج خلفي ..."""

    __tablename__ = 'category_groups'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(300), nullable=True)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)

    categories = db.relationship('Category', backref='group', lazy='dynamic')

    @property
    def categories_count(self) -> int:
        return self.categories.count()

    def __repr__(self) -> str:
        return f'<CategoryGroup {self.name}>'
