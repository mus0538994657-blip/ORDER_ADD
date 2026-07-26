from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import limiter
from models.user import User
from .forms import LoginForm

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    """تسجيل الدخول مع حماية ضد هجمات القوة الغاشمة."""
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()

        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            next_page = request.args.get('next')
            # منع Open Redirect
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main_bp.index'))

        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """تسجيل الخروج — POST فقط لتجنب CSRF."""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth_bp.login'))
