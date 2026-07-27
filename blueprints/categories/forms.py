from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, FloatField, SubmitField,
                     BooleanField, SelectField, IntegerField)
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class CategoryForm(FlaskForm):
    """نموذج إضافة/تعديل الصنف."""

    code = StringField(
        'كود الصنف *',
        validators=[DataRequired(message='مطلوب'), Length(2, 30)],
        render_kw={'placeholder': 'مثال: GLS-001', 'class': 'text-uppercase'},
    )
    name = StringField(
        'اسم الصنف *',
        validators=[DataRequired(message='مطلوب'), Length(2, 120)],
    )
    description = TextAreaField(
        'الوصف',
        validators=[Optional(), Length(max=300)],
        render_kw={'rows': 2},
    )
    group_id = SelectField(
        'التصنيف',
        coerce=lambda x: int(x) if x and x != '0' else None,
        validators=[Optional()],
    )
    unit = StringField(
        'الوحدة *',
        validators=[DataRequired(message='مطلوب'), Length(1, 30)],
        default='قطعة',
    )
    default_price = FloatField(
        'السعر الافتراضي (ر.س)',
        validators=[Optional(), NumberRange(min=0, message='يجب أن يكون السعر موجباً')],
        default=0.0,
    )
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')

    def populate_groups(self, groups):
        choices = [('0', '— بدون تصنيف —')]
        choices += [(str(g.id), g.name) for g in groups if g.is_active]
        self.group_id.choices = choices


class UnitForm(FlaskForm):
    """نموذج إضافة/تعديل وحدة."""
    name = StringField(
        'اسم الوحدة *',
        validators=[DataRequired(message='مطلوب'), Length(1, 50)],
    )
    is_active = BooleanField('نشطة', default=True)
    submit = SubmitField('حفظ')


class CategoryGroupForm(FlaskForm):
    """نموذج إضافة/تعديل تصنيف."""
    name = StringField(
        'اسم التصنيف *',
        validators=[DataRequired(message='مطلوب'), Length(2, 100)],
    )
    description = TextAreaField(
        'الوصف',
        validators=[Optional(), Length(max=300)],
        render_kw={'rows': 2},
    )
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')