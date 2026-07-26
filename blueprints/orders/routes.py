import io
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, abort, jsonify, send_file, current_app,
)
from flask_login import login_required, current_user
from extensions import db
from models.order import Order
from models.category import Category
from .forms import OrderForm

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/orders')


# ---------------------------------------------------------------------------
# قائمة الطلبات مع البحث والفلترة والترقيم
# ---------------------------------------------------------------------------

@orders_bp.route('/')
@login_required
def list_orders():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '', type=int)
    per_page = current_app.config.get('ORDERS_PER_PAGE', 20)

    query = Order.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Order.customer_name.ilike(like),
                Order.customer_phone.ilike(like),
                Order.plate_number.ilike(like),
                Order.order_number.ilike(like),
            )
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category_id=category_filter)

    pagination = (
        query
        .order_by(Order.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    return render_template(
        'orders/list.html',
        pagination=pagination,
        orders=pagination.items,
        categories=categories,
        statuses=Order.STATUSES,
        search=search,
        status_filter=status_filter,
        category_filter=category_filter,
    )


# ---------------------------------------------------------------------------
# تفاصيل الطلب
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('orders/detail.html', order=order)


# ---------------------------------------------------------------------------
# إضافة طلب جديد
# ---------------------------------------------------------------------------

@orders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    form = OrderForm()
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    statuses = current_app.config['ORDER_STATUSES']
    form.populate_choices(categories, statuses)

    if form.validate_on_submit():
        order = Order(
            order_number=Order.generate_order_number(),
            customer_name=form.customer_name.data.strip(),
            customer_phone=form.customer_phone.data.strip() if form.customer_phone.data else None,
            customer_email=form.customer_email.data.strip().lower() if form.customer_email.data else None,
            car_make=form.car_make.data.strip() if form.car_make.data else None,
            car_model=form.car_model.data.strip() if form.car_model.data else None,
            car_year=form.car_year.data.strip() if form.car_year.data else None,
            plate_number=form.plate_number.data.strip().upper() if form.plate_number.data else None,
            category_id=form.category_id.data,
            price=form.price.data,
            discount=form.discount.data or 0.0,
            status=form.status.data,
            notes=form.notes.data.strip() if form.notes.data else None,
            created_by_id=current_user.id,
        )
        order.calculate_final_price()
        db.session.add(order)
        db.session.commit()
        flash(f'✅ تم إنشاء الطلب {order.order_number} بنجاح', 'success')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    # تعبئة السعر الافتراضي عند التحميل الأول
    category_prices = {c.id: c.default_price for c in categories}
    return render_template(
        'orders/form.html',
        form=form,
        title='طلب جديد',
        category_prices=category_prices,
    )


# ---------------------------------------------------------------------------
# تعديل طلب
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == Order.STATUS_CANCELLED:
        flash('لا يمكن تعديل طلب ملغي', 'warning')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    form = OrderForm(obj=order)
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    statuses = current_app.config['ORDER_STATUSES']
    form.populate_choices(categories, statuses)

    if form.validate_on_submit():
        order.customer_name = form.customer_name.data.strip()
        order.customer_phone = form.customer_phone.data.strip() if form.customer_phone.data else None
        order.customer_email = form.customer_email.data.strip().lower() if form.customer_email.data else None
        order.car_make = form.car_make.data.strip() if form.car_make.data else None
        order.car_model = form.car_model.data.strip() if form.car_model.data else None
        order.car_year = form.car_year.data.strip() if form.car_year.data else None
        order.plate_number = form.plate_number.data.strip().upper() if form.plate_number.data else None
        order.category_id = form.category_id.data
        order.price = form.price.data
        order.discount = form.discount.data or 0.0
        order.status = form.status.data
        order.notes = form.notes.data.strip() if form.notes.data else None
        order.calculate_final_price()
        db.session.commit()
        flash(f'✅ تم تحديث الطلب {order.order_number}', 'success')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    category_prices = {c.id: c.default_price for c in categories}
    return render_template(
        'orders/form.html',
        form=form,
        order=order,
        title=f'تعديل الطلب {order.order_number}',
        category_prices=category_prices,
    )


# ---------------------------------------------------------------------------
# حذف طلب
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order_number = order.order_number
    db.session.delete(order)
    db.session.commit()
    flash(f'🗑️ تم حذف الطلب {order_number}', 'info')
    return redirect(url_for('orders_bp.list_orders'))


# ---------------------------------------------------------------------------
# تحديث الحالة (AJAX)
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.json.get('status') if request.is_json else request.form.get('status')

    if new_status not in Order.STATUSES:
        return jsonify({'error': 'حالة غير صالحة'}), 400

    order.status = new_status
    db.session.commit()
    return jsonify({
        'success': True,
        'status': order.status,
        'color': order.status_color,
    })


# ---------------------------------------------------------------------------
# تصدير Excel
# ---------------------------------------------------------------------------

@orders_bp.route('/export')
@login_required
def export_excel():
    """تصدير الطلبات إلى ملف Excel منسَّق RTL."""
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '', type=int)

    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category_id=category_filter)

    orders = query.order_by(Order.created_at.desc()).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'الطلبات'
    ws.sheet_view.rightToLeft = True

    # الألوان
    header_fill = PatternFill('solid', fgColor='1B4F72')
    alt_fill = PatternFill('solid', fgColor='EBF5FB')
    thin = Side(style='thin', color='BBBBBB')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    headers = [
        'رقم الطلب', 'العميل', 'الهاتف', 'السيارة', 'اللوحة',
        'الخدمة', 'السعر', 'الخصم', 'الإجمالي', 'الحالة',
        'ملاحظات', 'تاريخ الإنشاء',
    ]

    # رأس الجدول
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True, color='FFFFFF', size=11)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    ws.row_dimensions[1].height = 22

    # البيانات
    for row_num, order in enumerate(orders, 2):
        row_data = [
            order.order_number,
            order.customer_name,
            order.customer_phone or '',
            order.car_full,
            order.plate_number or '',
            order.category.name if order.category else '',
            order.price,
            order.discount,
            order.final_price,
            order.status,
            order.notes or '',
            order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '',
        ]
        fill = alt_fill if row_num % 2 == 0 else None
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
            if fill:
                cell.fill = fill

    # عرض الأعمدة تلقائياً
    col_widths = [15, 20, 15, 22, 14, 18, 10, 10, 10, 16, 25, 20]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # حفظ في الذاكرة
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f'orders_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename,
    )
