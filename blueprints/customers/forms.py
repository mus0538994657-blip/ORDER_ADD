from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField,
    EmailField, BooleanField,
)
from wtforms.validators import DataRequired, Optional, Length, Email


class CustomerForm(FlaskForm):
    """نموذج إضافة/تعديل العميل."""

    name = StringField(
        'الاسم *',
        validators=[DataRequired(message='مطلوب'), Length(2, 150)],
    )
    phone = StringField(
        'رقم الهاتف',
        validators=[Optional(), Length(max=30)],
        render_kw={'type': 'tel'},
    )
    email = EmailField(
        'البريد الإلكتروني',
        validators=[Optional(), Email(message='بريد غير صالح'), Length(max=120)],
    )
    address = StringField(
        'العنوان',
        validators=[Optional(), Length(max=300)],
    )
    notes = TextAreaField(
        'ملاحظات',
        validators=[Optional(), Length(max=1000)],
        render_kw={'rows': 2},
    )
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')


class VehicleForm(FlaskForm):
    """نموذج إضافة/تعديل مركبة."""

    make = StringField(
        'الماركة',
        validators=[Optional(), Length(max=100)],
    )
    model = StringField(
        'الموديل',
        validators=[Optional(), Length(max=100)],
    )
    year = StringField(
        'سنة الصنع',
        validators=[Optional(), Length(max=10)],
    )
    plate_number = StringField(
        'رقم اللوحة',
        validators=[Optional(), Length(max=30)],
    )
    color = StringField(
        'اللون',
        validators=[Optional(), Length(max=50)],
    )
    notes = TextAreaField(
        'ملاحظات',
        validators=[Optional(), Length(max=500)],
        render_kw={'rows': 2},
    )
    submit = SubmitField('حفظ المركبة')
