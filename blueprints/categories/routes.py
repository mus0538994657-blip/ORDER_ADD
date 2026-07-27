from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify)
from flask_login import login_required
from extensions import db
from models.category import Category
from models.unit import Unit
from models.category_group import CategoryGroup
from .forms import CategoryForm, UnitForm, CategoryGroupForm

categories_bp = Blueprint('categories_bp', __name__, url_prefix='/categories')


# ---------------------------------------------------------------------------
# الأصناف — CRUD
# ---------------------------------------------------------------------------

@categories_bp.route('/')
@login_required
def list_categories():
    q            = request.args.get('q', '').strip()
    group_filter = request.args.get('group', 0, type=int)
    status_filter = request.args.get('status', '')
    page         = request.args.get('page', 1, type=int)

    query = Category.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(Category.code.ilike(like), Category.name.ilike(like))
        )
    if group_filter:
        query = query.filter_by(group_id=group_filter)
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    pagination = query.order_by(Category.code).paginate(
        page=page, per_page=20, error_out=False
    )
    groups = CategoryGroup.query.filter_by(is_active=True).order_by(CategoryGroup.name).all()

    return render_template(
        'categories/list.html',
        pagination=pagination,
        categories=pagination.items,
        groups=groups,
        q=q,
        group_filter=group_filter,
        status_filter=status_filter,
    )


@categories_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    groups = CategoryGroup.query.filter_by(is_active=True).order_by(CategoryGroup.name).all()
    units  = Unit.query.filter_by(is_active=True).order_by(Unit.name).all()
    form   = CategoryForm()
    form.populate_groups(groups)

    if form.validate_on_submit():
        code = form.code.data.strip().upper()
        if Category.query.filter(db.func.upper(Category.code) == code).first():
            flash('يوجد صنف بهذا الكود بالفعل', 'warning')
        elif Category.query.filter(
            db.func.lower(Category.name) == form.name.data.strip().lower()
        ).first():
            flash('يوجد صنف بهذا الاسم بالفعل', 'warning')
        else:
            cat = Category(
                code          = code,
                name          = form.name.data.strip(),
                description   = form.description.data.strip() if form.description.data else None,
                group_id      = form.group_id.data,
                unit          = form.unit.data.strip(),
                default_price = form.default_price.data or 0.0,
                is_active     = form.is_active.data,
            )
            db.session.add(cat)
            db.session.commit()
            flash(f'تم إضافة الصنف "{cat.name}"', 'success')
            return redirect(url_for('categories_bp.list_categories'))

    return render_template('categories/form.html',
                           form=form, units=units, title='صنف جديد')


@categories_bp.route('/<int:cat_id>')
@login_required
def view_category(cat_id):
    cat    = Category.query.get_or_404(cat_id)
    orders = cat.order_items.order_by(db.desc('id')).limit(20).all()
    return render_template('categories/detail.html', cat=cat, recent_items=orders)


@categories_bp.route('/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(cat_id):
    cat    = Category.query.get_or_404(cat_id)
    groups = CategoryGroup.query.filter_by(is_active=True).order_by(CategoryGroup.name).all()
    units  = Unit.query.filter_by(is_active=True).order_by(Unit.name).all()
    form   = CategoryForm(obj=cat)
    form.populate_groups(groups)

    if form.validate_on_submit():
        code = form.code.data.strip().upper()
        dup_code = Category.query.filter(
            db.func.upper(Category.code) == code, Category.id != cat_id
        ).first()
        dup_name = Category.query.filter(
            db.func.lower(Category.name) == form.name.data.strip().lower(),
            Category.id != cat_id,
        ).first()
        if dup_code:
            flash('يوجد صنف آخر بهذا الكود', 'warning')
        elif dup_name:
            flash('يوجد صنف آخر بهذا الاسم', 'warning')
        else:
            cat.code          = code
            cat.name          = form.name.data.strip()
            cat.description   = form.description.data.strip() if form.description.data else None
            cat.group_id      = form.group_id.data
            cat.unit          = form.unit.data.strip()
            cat.default_price = form.default_price.data or 0.0
            cat.is_active     = form.is_active.data
            db.session.commit()
            flash(f'تم تحديث الصنف "{cat.name}"', 'success')
            return redirect(url_for('categories_bp.list_categories'))

    if request.method == 'GET':
        form.group_id.data = str(cat.group_id) if cat.group_id else '0'

    return render_template('categories/form.html',
                           form=form, cat=cat, units=units,
                           title=f'تعديل: {cat.name}')


@categories_bp.route('/<int:cat_id>/delete', methods=['POST'])
@login_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.total_orders_count > 0 or cat.order_items.count() > 0:
        flash('لا يمكن حذف صنف مرتبط بطلبات. يمكنك تعطيله بدلاً من ذلك.', 'warning')
        return redirect(url_for('categories_bp.list_categories'))
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'تم حذف الصنف "{name}"', 'info')
    return redirect(url_for('categories_bp.list_categories'))


@categories_bp.route('/<int:cat_id>/toggle', methods=['POST'])
@login_required
def toggle_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    state = 'تفعيل' if cat.is_active else 'تعطيل'
    flash(f'تم {state} الصنف "{cat.name}"', 'success')
    return redirect(url_for('categories_bp.list_categories'))


# ---------------------------------------------------------------------------
# الوحدات
# ---------------------------------------------------------------------------

@categories_bp.route('/units', methods=['GET', 'POST'])
@login_required
def manage_units():
    form  = UnitForm()
    units = Unit.query.order_by(Unit.name).all()

    if form.validate_on_submit():
        name = form.name.data.strip()
        if Unit.query.filter(db.func.lower(Unit.name) == name.lower()).first():
            flash('هذه الوحدة موجودة بالفعل', 'warning')
        else:
            db.session.add(Unit(name=name, is_active=form.is_active.data))
            db.session.commit()
            flash(f'تمت إضافة الوحدة "{name}"', 'success')
            return redirect(url_for('categories_bp.manage_units'))

    return render_template('categories/units.html', form=form, units=units)


@categories_bp.route('/units/<int:unit_id>/edit', methods=['POST'])
@login_required
def edit_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    name = request.form.get('name', '').strip()
    if not name:
        flash('اسم الوحدة مطلوب', 'warning')
        return redirect(url_for('categories_bp.manage_units'))
    dup = Unit.query.filter(
        db.func.lower(Unit.name) == name.lower(), Unit.id != unit_id
    ).first()
    if dup:
        flash('هذه الوحدة موجودة بالفعل', 'warning')
    else:
        unit.name      = name
        unit.is_active = 'is_active' in request.form
        db.session.commit()
        flash(f'تم تحديث الوحدة "{name}"', 'success')
    return redirect(url_for('categories_bp.manage_units'))


@categories_bp.route('/units/<int:unit_id>/delete', methods=['POST'])
@login_required
def delete_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    name = unit.name
    db.session.delete(unit)
    db.session.commit()
    flash(f'تم حذف الوحدة "{name}"', 'info')
    return redirect(url_for('categories_bp.manage_units'))


# ---------------------------------------------------------------------------
# التصنيفات
# ---------------------------------------------------------------------------

@categories_bp.route('/groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    form   = CategoryGroupForm()
    groups = CategoryGroup.query.order_by(CategoryGroup.name).all()

    if form.validate_on_submit():
        name = form.name.data.strip()
        if CategoryGroup.query.filter(db.func.lower(CategoryGroup.name) == name.lower()).first():
            flash('هذا التصنيف موجود بالفعل', 'warning')
        else:
            desc = form.description.data.strip() if form.description.data else None
            db.session.add(CategoryGroup(name=name, description=desc,
                                         is_active=form.is_active.data))
            db.session.commit()
            flash(f'تمت إضافة التصنيف "{name}"', 'success')
            return redirect(url_for('categories_bp.manage_groups'))

    return render_template('categories/groups.html', form=form, groups=groups)


@categories_bp.route('/groups/<int:group_id>/edit', methods=['POST'])
@login_required
def edit_group(group_id):
    group = CategoryGroup.query.get_or_404(group_id)
    name  = request.form.get('name', '').strip()
    if not name:
        flash('اسم التصنيف مطلوب', 'warning')
        return redirect(url_for('categories_bp.manage_groups'))
    dup = CategoryGroup.query.filter(
        db.func.lower(CategoryGroup.name) == name.lower(), CategoryGroup.id != group_id
    ).first()
    if dup:
        flash('هذا التصنيف موجود بالفعل', 'warning')
    else:
        group.name        = name
        group.description = request.form.get('description', '').strip() or None
        group.is_active   = 'is_active' in request.form
        db.session.commit()
        flash(f'تم تحديث التصنيف "{name}"', 'success')
    return redirect(url_for('categories_bp.manage_groups'))


@categories_bp.route('/groups/<int:group_id>/delete', methods=['POST'])
@login_required
def delete_group(group_id):
    group = CategoryGroup.query.get_or_404(group_id)
    if group.categories_count > 0:
        flash('لا يمكن حذف تصنيف مرتبط بأصناف. عطّله بدلاً من ذلك.', 'warning')
        return redirect(url_for('categories_bp.manage_groups'))
    name = group.name
    db.session.delete(group)
    db.session.commit()
    flash(f'تم حذف التصنيف "{name}"', 'info')
    return redirect(url_for('categories_bp.manage_groups'))