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
from models.customer import Customer
from models.vehicle import Vehicle
from utils.notifications import notify_order_created, notify_order_status_changed
from .forms import OrderForm

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/orders')


# ---------------------------------------------------------------------------
# قائمة الطلبات
# ---------------------------------------------------------------------------

@orders_bp.route('/')
@login_required
def list_orders():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '', type=int)
    per_page = current_app.config.get('ORDERS_PER_PAGE', 20)

    query = Order.query.join(Customer)

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Customer.name.ilike(like),
                Customer.phone.ilike(like),
                Order.order_number.ilike(like),
            )
        )
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if category_filter:
        query = query.filter(Order.category_id == category_filter)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
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
# إضافة طلب
# ---------------------------------------------------------------------------

@orders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    statuses = current_app.config['ORDER_STATUSES']

    # تحديد عميل مسبق من URL
    preselect_customer_id = request.args.get('customer_id', 0, type=int)
    preselect_vehicles = []
    if preselect_customer_id:
        cust = Customer.query.get(preselect_customer_id)
        if cust:
            preselect_vehicles = cust.vehicles.all()

    form = OrderForm()
    form.populate_choices(customers, categories, statuses, preselect_vehicles)

    if form.validate_on_submit():
        vehicle_id = form.vehicle_id.data if form.vehicle_id.data else None
        order = Order(
            order_number=Order.generate_order_number(),
            customer_id=form.customer_id.data,
            vehicle_id=vehicle_id,
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
        notify_order_created(order)
        flash(f'✅ تم إنشاء الطلب {order.order_number}', 'success')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    category_prices = {c.id: c.default_price for c in categories}
    return render_template(
        'orders/form.html',
        form=form,
        title='طلب جديد',
        category_prices=category_prices,
        preselect_customer_id=preselect_customer_id,
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

    customers = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    statuses = current_app.config['ORDER_STATUSES']

    # تحميل مركبات العميل الحالي
    current_vehicles = order.customer.vehicles.all() if order.customer else []

    form = OrderForm()
    form.populate_choices(customers, categories, statuses, current_vehicles)

    if form.validate_on_submit():
        vehicle_id = form.vehicle_id.data if form.vehicle_id.data else None
        order.customer_id = form.customer_id.data
        order.vehicle_id = vehicle_id
        order.category_id = form.category_id.data
        order.price = form.price.data
        order.discount = form.discount.data or 0.0
        order.status = form.status.data
        order.notes = form.notes.data.strip() if form.notes.data else None
        order.calculate_final_price()
        db.session.commit()
        flash(f'✅ تم تحديث الطلب {order.order_number}', 'success')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    # تعبئة القيم الحالية
    if request.method == 'GET':
        form.customer_id.data = order.customer_id
        form.vehicle_id.data = str(order.vehicle_id) if order.vehicle_id else '0'
        form.category_id.data = order.category_id
        form.price.data = order.price
        form.discount.data = order.discount
        form.status.data = order.status
        form.notes.data = order.notes

    category_prices = {c.id: c.default_price for c in categories}
    return render_template(
        'orders/form.html',
        form=form,
        order=order,
        title=f'تعديل الطلب {order.order_number}',
        category_prices=category_prices,
        preselect_customer_id=order.customer_id,
    )


# ---------------------------------------------------------------------------
# حذف طلب
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    number = order.order_number
    db.session.delete(order)
    db.session.commit()
    flash(f'🗑️ تم حذف الطلب {number}', 'info')
    return redirect(url_for('orders_bp.list_orders'))


# ---------------------------------------------------------------------------
# تحديث الحالة (AJAX + POST)
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = (
        request.json.get('status')
        if request.is_json
        else request.form.get('status')
    )
    if new_status not in Order.STATUSES:
        return jsonify({'error': 'حالة غير صالحة'}), 400

    old_status = order.status
    order.status = new_status
    db.session.commit()
    notify_order_status_changed(order, old_status)

    if request.is_json:
        return jsonify({'success': True, 'status': order.status,
                        'color': order.status_color})
    flash(f'✅ تم تحديث حالة الطلب إلى "{new_status}"', 'success')
    return redirect(url_for('orders_bp.order_detail', order_id=order.id))


# ---------------------------------------------------------------------------
# تصدير Excel
# ---------------------------------------------------------------------------

@orders_bp.route('/export')
@login_required
def export_excel():
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

    header_fill = PatternFill('solid', fgColor='1B4F72')
    alt_fill = PatternFill('solid', fgColor='EBF5FB')
    thin = Side(style='thin', color='BBBBBB')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    headers = [
        'رقم الطلب', 'العميل', 'الهاتف', 'المركبة',
        'الخدمة', 'السعر', 'الخصم', 'الإجمالي',
        'الحالة', 'ملاحظات', 'تاريخ الإنشاء',
    ]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(bold=True, color='FFFFFF', size=11)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    ws.row_dimensions[1].height = 22

    for r, order in enumerate(orders, 2):
        row_data = [
            order.order_number,
            order.customer_name,
            order.customer.phone if order.customer else '',
            order.vehicle_info,
            order.category.name if order.category else '',
            order.price, order.discount, order.final_price,
            order.status, order.notes or '',
            order.created_at.strftime('%Y-%m-%d') if order.created_at else '',
        ]
        fill = alt_fill if r % 2 == 0 else None
        for c, val in enumerate(row_data, 1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
            if fill:
                cell.fill = fill

    for i, w in enumerate([15, 20, 15, 22, 18, 10, 10, 10, 16, 25, 18], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f'orders_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)

