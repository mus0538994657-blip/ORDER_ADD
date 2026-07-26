from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class CategoryForm(FlaskForm):
    """نموذج إضافة/تعديل الصنف."""

    name = StringField(
        'اسم الصنف *',
        validators=[DataRequired(message='مطلوب'), Length(2, 120)],
    )
    description = TextAreaField(
        'الوصف',
        validators=[Optional(), Length(max=300)],
        render_kw={'rows': 2},
    )
    default_price = FloatField(
        'السعر الافتراضي (ر.س)',
        validators=[Optional(), NumberRange(min=0, message='يجب أن يكون السعر موجباً')],
        default=0.0,
    )
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')
