from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from extensions import db
from models.category import Category
from .forms import CategoryForm

categories_bp = Blueprint('categories_bp', __name__, url_prefix='/categories')


@categories_bp.route('/')
@login_required
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories/list.html', categories=categories)


@categories_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter(
            db.func.lower(Category.name) == form.name.data.strip().lower()
        ).first():
            flash('يوجد صنف بهذا الاسم بالفعل', 'warning')
        else:
            cat = Category(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                default_price=form.default_price.data or 0.0,
                is_active=form.is_active.data,
            )
            db.session.add(cat)
            db.session.commit()
            flash(f'✅ تم إضافة الصنف "{cat.name}"', 'success')
            return redirect(url_for('categories_bp.list_categories'))
    return render_template('categories/form.html', form=form, title='صنف جديد')


@categories_bp.route('/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        duplicate = Category.query.filter(
            db.func.lower(Category.name) == form.name.data.strip().lower(),
            Category.id != cat_id,
        ).first()
        if duplicate:
            flash('يوجد صنف بهذا الاسم بالفعل', 'warning')
        else:
            cat.name = form.name.data.strip()
            cat.description = form.description.data.strip() if form.description.data else None
            cat.default_price = form.default_price.data or 0.0
            cat.is_active = form.is_active.data
            db.session.commit()
            flash(f'✅ تم تحديث الصنف "{cat.name}"', 'success')
            return redirect(url_for('categories_bp.list_categories'))
    return render_template('categories/form.html', form=form, cat=cat, title=f'تعديل: {cat.name}')


@categories_bp.route('/<int:cat_id>/delete', methods=['POST'])
@login_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.total_orders_count > 0:
        flash('لا يمكن حذف صنف مرتبط بطلبات. يمكنك تعطيله بدلاً من ذلك.', 'warning')
        return redirect(url_for('categories_bp.list_categories'))
    db.session.delete(cat)
    db.session.commit()
    flash(f'🗑️ تم حذف الصنف "{cat.name}"', 'info')
    return redirect(url_for('categories_bp.list_categories'))
