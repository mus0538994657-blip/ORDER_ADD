from flask_wtf import FlaskForm
from wtforms import (
    SelectField, FloatField, TextAreaField,
    SubmitField, HiddenField,
)
from wtforms.validators import DataRequired, Optional, NumberRange


class OrderForm(FlaskForm):
    """نموذج إضافة/تعديل الطلب — يختار العميل والمركبة من قوائم."""

    customer_id = SelectField(
        'العميل *',
        coerce=int,
        validators=[DataRequired(message='يجب اختيار العميل')],
    )
    vehicle_id = SelectField(
        'المركبة',
        coerce=lambda x: int(x) if x and str(x) != '0' else None,
        validators=[Optional()],
        default=None,
    )
    category_id = SelectField(
        'نوع الخدمة *',
        coerce=int,
        validators=[DataRequired(message='يجب اختيار نوع الخدمة')],
    )
    price = FloatField(
        'السعر (ر.س) *',
        validators=[
            DataRequired(message='مطلوب'),
            NumberRange(min=0, message='السعر يجب أن يكون موجباً'),
        ],
        default=0.0,
    )
    discount = FloatField(
        'الخصم (ر.س)',
        validators=[Optional(), NumberRange(min=0)],
        default=0.0,
    )
    status = SelectField(
        'الحالة',
        validators=[DataRequired()],
    )
    notes = TextAreaField(
        'ملاحظات',
        validators=[Optional()],
        render_kw={'rows': 3},
    )
    submit = SubmitField('حفظ الطلب')

    def populate_choices(self, customers, categories, statuses, vehicles=None):
        self.customer_id.choices = [(c.id, f'{c.name} ({c.phone or "—"})') for c in customers]
        self.category_id.choices = [(c.id, c.name) for c in categories]
        self.status.choices = [(s, s) for s in statuses]
        # المركبات: فارغة أولاً، تُملأ بـ AJAX
        v_list = vehicles or []
        self.vehicle_id.choices = [('0', '— بدون مركبة —')] + [
            (str(v.id), v.label) for v in v_list
        ]

