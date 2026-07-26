from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, FloatField,
    SubmitField, EmailField,
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Email


class OrderForm(FlaskForm):
    """نموذج إضافة/تعديل الطلب."""

    # بيانات العميل
    customer_name = StringField(
        'اسم العميل *',
        validators=[DataRequired(message='مطلوب'), Length(2, 150)],
    )
    customer_phone = StringField(
        'رقم الهاتف',
        validators=[Optional(), Length(max=30)],
    )
    customer_email = EmailField(
        'البريد الإلكتروني',
        validators=[Optional(), Email(message='بريد غير صالح'), Length(max=120)],
    )

    # بيانات المركبة
    car_make = StringField(
        'ماركة السيارة',
        validators=[Optional(), Length(max=100)],
    )
    car_model = StringField(
        'الموديل',
        validators=[Optional(), Length(max=100)],
    )
    car_year = StringField(
        'سنة الصنع',
        validators=[Optional(), Length(max=10)],
    )
    plate_number = StringField(
        'رقم اللوحة',
        validators=[Optional(), Length(max=30)],
    )

    # تفاصيل الخدمة
    category_id = SelectField(
        'نوع الخدمة *',
        coerce=int,
        validators=[DataRequired(message='مطلوب')],
    )
    price = FloatField(
        'السعر (ر.س) *',
        validators=[DataRequired(message='مطلوب'), NumberRange(min=0, message='يجب أن يكون السعر موجباً')],
        default=0.0,
    )
    discount = FloatField(
        'الخصم (ر.س)',
        validators=[Optional(), NumberRange(min=0, message='يجب أن يكون الخصم موجباً')],
        default=0.0,
    )
    status = SelectField(
        'الحالة',
        validators=[DataRequired()],
    )
    notes = TextAreaField(
        'ملاحظات',
        validators=[Optional(), Length(max=1000)],
        render_kw={'rows': 3},
    )
    submit = SubmitField('حفظ الطلب')

    def populate_choices(self, categories, statuses):
        """تعبئة قوائم الاختيار ديناميكياً."""
        self.category_id.choices = [(c.id, c.name) for c in categories]
        self.status.choices = [(s, s) for s in statuses]
