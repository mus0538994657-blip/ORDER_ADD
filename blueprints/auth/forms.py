from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول."""

    username = StringField(
        'اسم المستخدم',
        validators=[DataRequired(message='مطلوب'), Length(1, 80)],
        render_kw={'autofocus': True, 'autocomplete': 'username'},
    )
    password = PasswordField(
        'كلمة المرور',
        validators=[DataRequired(message='مطلوب')],
        render_kw={'autocomplete': 'current-password'},
    )
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')
