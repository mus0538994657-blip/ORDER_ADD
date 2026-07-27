from flask_wtf import FlaskForm
from wtforms import (
    SelectField, FloatField, TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange


class DynamicSelectField(SelectField):
    """SelectField يتخطى التحقق من الخيارات — للقوائم المُحمَّلة بـ AJAX."""
    def pre_validate(self, form):
        pass


class OrderForm(FlaskForm):
    """نموذج إضافة/تعديل الطلب.
    البنود (items) تُرسل عبر حقل hidden items_json — لا تُعالَج هنا.
    """

    customer_id = SelectField(
        'العميل *',
        coerce=int,
        validators=[DataRequired(message='يجب اختيار العميل')],
    )
    # vehicle_id يُحمَّل عبر AJAX → نستخدم DynamicSelectField لتجاوز choices validation
    vehicle_id = DynamicSelectField(
        'المركبة',
        coerce=lambda x: int(x) if x and str(x) not in ('0', '') else None,
        validators=[Optional()],
        default=None,
    )
    discount = FloatField(
        'الخصم (ر.س)',
        validators=[Optional(), NumberRange(min=0, message='الخصم يجب أن يكون موجباً')],
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
        self.status.choices      = [(s, s) for s in statuses]
        v_list = vehicles or []
        self.vehicle_id.choices  = [('0', '— بدون مركبة —')] + [
            (str(v.id), v.label) for v in v_list
        ]

