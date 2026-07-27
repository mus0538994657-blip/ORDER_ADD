import io
import json
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, abort, jsonify, send_file, current_app,
)
from flask_login import login_required, current_user
from extensions import db
from models.order import Order
from models.order_item import OrderItem
from models.category import Category
from models.customer import Customer
from models.vehicle import Vehicle
from utils.notifications import notify_order_created, notify_order_status_changed
from .forms import OrderForm

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/orders')


# ---------------------------------------------------------------------------
# ظ…ط³ط§ط¹ط¯: ط­ظپط¸ ط¨ظ†ظˆط¯ ط§ظ„ط·ظ„ط¨ ظ…ظ† JSON ط§ظ„ظ…ظڈط±ط³ظ„ ظپظٹ ط§ظ„ظپظˆط±ظ…
# ---------------------------------------------------------------------------

def _save_items(order: Order, items_json: str) -> tuple[bool, str]:
    """
    ظٹط­ظ„ظ‘ظ„ items_json ظˆظٹظڈظ†ط´ط¦/ظٹظڈط­ط¯ظ‘ط« ط¨ظ†ظˆط¯ ط§ظ„ط·ظ„ط¨.
    ظٹظڈط¹ظٹط¯ (True, '') ط¹ظ†ط¯ ط§ظ„ظ†ط¬ط§ط­طŒ ط£ظˆ (False, ط±ط³ط§ظ„ط©_ط®ط·ط£).
    """
    try:
        items_data = json.loads(items_json or '[]')
    except (ValueError, TypeError):
        return False, 'ط¨ظٹط§ظ†ط§طھ ط§ظ„ط¨ظ†ظˆط¯ ط؛ظٹط± طµط§ظ„ط­ط©'

    if not items_data:
        return False, 'ظٹط¬ط¨ ط¥ط¶ط§ظپط© ط¨ظ†ط¯ ظˆط§ط­ط¯ ط¹ظ„ظ‰ ط§ظ„ط£ظ‚ظ„'

    # ط­ط°ظپ ط§ظ„ط¨ظ†ظˆط¯ ط§ظ„ظ‚ط¯ظٹظ…ط©
    order.items.delete()

    for row in items_data:
        try:
            qty   = float(row.get('quantity', 1) or 1)
            price = float(row.get('unit_price', 0) or 0)
        except (ValueError, TypeError):
            return False, 'ظ‚ظٹظ…ط© ظƒظ…ظٹط© ط£ظˆ ط³ط¹ط± ط؛ظٹط± طµط§ظ„ط­ط©'

        if qty <= 0 or price < 0:
            return False, 'ط§ظ„ظƒظ…ظٹط© ظٹط¬ط¨ ط£ظ† طھظƒظˆظ† ظ…ظˆط¬ط¨ط© ظˆط§ظ„ط³ط¹ط± ط؛ظٹط± ط³ط§ظ„ط¨'

        code = str(row.get('code', '')).strip()
        name = str(row.get('name', '')).strip()
        if not code or not name:
            return False, 'ظƒظˆط¯ ظˆط§ط³ظ… ط§ظ„ط¨ظ†ط¯ ظ…ط·ظ„ظˆط¨ط§ظ†'

        item = OrderItem(
            order_id    = order.id,
            category_id = row.get('category_id') or None,
            code        = code,
            name        = name,
            description = str(row.get('description', '')).strip() or None,
            unit        = str(row.get('unit', 'ظ‚ط·ط¹ط©')).strip() or 'ظ‚ط·ط¹ط©',
            quantity    = qty,
            unit_price  = price,
        )
        item.compute_total()
        db.session.add(item)

    return True, ''


# ---------------------------------------------------------------------------
# ظ‚ط§ط¦ظ…ط© ط§ظ„ط·ظ„ط¨ط§طھ
# ---------------------------------------------------------------------------

@orders_bp.route('/')
@login_required
def list_orders():
    page           = request.args.get('page', 1, type=int)
    search         = request.args.get('q', '').strip()
    status_filter  = request.args.get('status', '')
    category_filter = request.args.get('category', '', type=int)
    per_page       = current_app.config.get('ORDERS_PER_PAGE', 20)

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
# طھظپط§طµظٹظ„ ط§ظ„ط·ظ„ط¨
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    items = order.items.all()
    return render_template('orders/detail.html', order=order, items=items)


# ---------------------------------------------------------------------------
# ط¥ط¶ط§ظپط© ط·ظ„ط¨
# ---------------------------------------------------------------------------

@orders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    customers  = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.code).all()
    statuses   = current_app.config['ORDER_STATUSES']

    preselect_customer_id = request.args.get('customer_id', 0, type=int)
    preselect_vehicles    = []
    if preselect_customer_id:
        cust = Customer.query.get(preselect_customer_id)
        if cust:
            preselect_vehicles = cust.vehicles.all()

    form = OrderForm()
    form.populate_choices(customers, categories, statuses, preselect_vehicles)

    if form.validate_on_submit():
        items_json = request.form.get('items_json', '[]')
        vehicle_id = form.vehicle_id.data if form.vehicle_id.data else None

        order = Order(
            order_number  = Order.generate_order_number(),
            customer_id   = form.customer_id.data,
            vehicle_id    = vehicle_id,
            discount      = form.discount.data or 0.0,
            status        = form.status.data,
            notes         = form.notes.data.strip() if form.notes.data else None,
            created_by_id = current_user.id,
        )
        db.session.add(order)
        db.session.flush()  # ظ„ظ„ط­طµظˆظ„ ط¹ظ„ظ‰ order.id ظ‚ط¨ظ„ ط¥ط¶ط§ظپط© ط§ظ„ط¨ظ†ظˆط¯

        ok, err = _save_items(order, items_json)
        if not ok:
            db.session.rollback()
            flash(f'ط®ط·ط£ ظپظٹ ط§ظ„ط¨ظ†ظˆط¯: {err}', 'danger')
            return render_template(
                'orders/form.html', form=form, title='ط·ظ„ط¨ ط¬ط¯ظٹط¯',
                categories_json=_categories_json(categories),
                preselect_customer_id=preselect_customer_id,
            )

        order.recalculate()
        db.session.commit()
        notify_order_created(order)
        flash(f'طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ط·ظ„ط¨ {order.order_number}', 'success')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    return render_template(
        'orders/form.html',
        form=form,
        title='ط·ظ„ط¨ ط¬ط¯ظٹط¯',
        categories_json=_categories_json(categories),
        preselect_customer_id=preselect_customer_id,
        existing_items=[],
    )


# ---------------------------------------------------------------------------
# طھط¹ط¯ظٹظ„ ط·ظ„ط¨
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == Order.STATUS_CANCELLED:
        flash('ظ„ط§ ظٹظ…ظƒظ† طھط¹ط¯ظٹظ„ ط·ظ„ط¨ ظ…ظ„ط؛ظٹ', 'warning')
        return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    customers  = Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.code).all()
    statuses   = current_app.config['ORDER_STATUSES']
    current_vehicles = order.customer.vehicles.all() if order.customer else []

    form = OrderForm()
    form.populate_choices(customers, categories, statuses, current_vehicles)

    if form.validate_on_submit():
        items_json = request.form.get('items_json', '[]')
        vehicle_id = form.vehicle_id.data if form.vehicle_id.data else None

        order.customer_id = form.customer_id.data
        order.vehicle_id  = vehicle_id
        order.discount    = form.discount.data or 0.0
        order.status      = form.status.data
        order.notes       = form.notes.data.strip() if form.notes.data else None

        ok, err = _save_items(order, items_json)
        if not ok:
            db.session.rollback()
            flash(f'ط®ط·ط£ ظپظٹ ط§ظ„ط¨ظ†ظˆط¯: {err}', 'danger')
        else:
            order.recalculate()
            db.session.commit()
            flash(f'طھظ… طھط­ط¯ظٹط« ط§ظ„ط·ظ„ط¨ {order.order_number}', 'success')
            return redirect(url_for('orders_bp.order_detail', order_id=order.id))

    if request.method == 'GET':
        form.customer_id.data = order.customer_id
        form.vehicle_id.data  = str(order.vehicle_id) if order.vehicle_id else '0'
        form.discount.data    = order.discount
        form.status.data      = order.status
        form.notes.data       = order.notes

    existing_items = [item.to_dict() for item in order.items.all()]

    return render_template(
        'orders/form.html',
        form=form,
        order=order,
        title=f'طھط¹ط¯ظٹظ„ ط§ظ„ط·ظ„ط¨ {order.order_number}',
        categories_json=_categories_json(categories),
        preselect_customer_id=order.customer_id,
        existing_items=existing_items,
    )


# ---------------------------------------------------------------------------
# ط­ط°ظپ ط·ظ„ط¨
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order  = Order.query.get_or_404(order_id)
    number = order.order_number
    db.session.delete(order)
    db.session.commit()
    flash(f'طھظ… ط­ط°ظپ ط§ظ„ط·ظ„ط¨ {number}', 'info')
    return redirect(url_for('orders_bp.list_orders'))


# ---------------------------------------------------------------------------
# طھط­ط¯ظٹط« ط§ظ„ط­ط§ظ„ط© (AJAX + POST)
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
        return jsonify({'error': 'ط­ط§ظ„ط© ط؛ظٹط± طµط§ظ„ط­ط©'}), 400

    old_status   = order.status
    order.status = new_status
    db.session.commit()
    notify_order_status_changed(order, old_status)

    if request.is_json:
        return jsonify({'success': True, 'status': order.status,
                        'color': order.status_color})
    flash(f'طھظ… طھط­ط¯ظٹط« ط­ط§ظ„ط© ط§ظ„ط·ظ„ط¨ ط¥ظ„ظ‰ "{new_status}"', 'success')
    return redirect(url_for('orders_bp.order_detail', order_id=order.id))


# ---------------------------------------------------------------------------
# طھطµط¯ظٹط± Excel
# ---------------------------------------------------------------------------

@orders_bp.route('/export')
@login_required
def export_excel():
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    status_filter   = request.args.get('status', '')
    category_filter = request.args.get('category', '', type=int)

    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    orders = query.order_by(Order.created_at.desc()).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'ط§ظ„ط·ظ„ط¨ط§طھ'
    ws.sheet_view.rightToLeft = True

    header_fill = PatternFill('solid', fgColor='00663d')
    alt_fill    = PatternFill('solid', fgColor='E0F5EC')
    thin        = Side(style='thin', color='BBBBBB')
    border      = Border(left=thin, right=thin, top=thin, bottom=thin)

    headers = [
        'ط±ظ‚ظ… ط§ظ„ط·ظ„ط¨', 'ط§ظ„ط¹ظ…ظٹظ„', 'ط§ظ„ظ‡ط§طھظپ', 'ط§ظ„ظ…ط±ظƒط¨ط©',
        'ط§ظ„ط³ط¹ط±', 'ط§ظ„ط®طµظ…', 'ط§ظ„ط¥ط¬ظ…ط§ظ„ظٹ',
        'ط§ظ„ط­ط§ظ„ط©', 'ظ…ظ„ط§ط­ط¸ط§طھ', 'طھط§ط±ظٹط® ط§ظ„ط¥ظ†ط´ط§ط،',
    ]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font      = Font(bold=True, color='FFFFFF', size=11)
        cell.fill      = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = border
    ws.row_dimensions[1].height = 22

    for r, order in enumerate(orders, 2):
        row_data = [
            order.order_number, order.customer_name,
            order.customer.phone if order.customer else '',
            order.vehicle_info,
            order.price, order.discount, order.final_price,
            order.status, order.notes or '',
            order.created_at.strftime('%Y-%m-%d') if order.created_at else '',
        ]
        fill = alt_fill if r % 2 == 0 else None
        for c, val in enumerate(row_data, 1):
            cell           = ws.cell(row=r, column=c, value=val)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border    = border
            if fill:
                cell.fill = fill

    for i, w in enumerate([15, 20, 15, 22, 10, 10, 10, 16, 25, 18], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    output   = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f'orders_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)


# ---------------------------------------------------------------------------
# ظ…ط³ط§ط¹ط¯ ط¯ط§ط®ظ„ظٹ
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# تصدير طلب مفرد — PDF
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/export/pdf')
@login_required
def export_order_pdf(order_id):
    from utils.pdf import generate_order_pdf
    order = Order.query.get_or_404(order_id)
    items = order.items.all()
    workshop_name = current_app.config.get('WORKSHOP_NAME', 'ورشة الزجاج')
    buf = generate_order_pdf(order, items, workshop_name)
    filename = f'order_{order.order_number}_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)


# ---------------------------------------------------------------------------
# تصدير طلب مفرد — Excel
# ---------------------------------------------------------------------------

@orders_bp.route('/<int:order_id>/export/excel')
@login_required
def export_order_excel(order_id):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    order = Order.query.get_or_404(order_id)
    items = order.items.all()
    cust  = order.customer
    veh   = order.vehicle
    workshop_name = current_app.config.get('WORKSHOP_NAME', 'ورشة الزجاج')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'أمر العمل'
    ws.sheet_view.rightToLeft = True

    green_fill = PatternFill('solid', fgColor='00663d')
    light_fill = PatternFill('solid', fgColor='E0F5EC')
    total_fill = PatternFill('solid', fgColor='aee6c6')
    alt_fill   = PatternFill('solid', fgColor='f6f9f8')
    thin   = Side(style='thin', color='BBBBBB')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def _cell(row, col, value, bold=False, color='000000', fill=None, size=10):
        c = ws.cell(row=row, column=col, value=value)
        c.font      = Font(bold=bold, color=color, size=size, name='Arial')
        c.alignment = Alignment(horizontal='center', vertical='center',
                                wrap_text=True, reading_order=2)
        c.border    = border
        if fill:
            c.fill = fill
        return c

    # صف العنوان
    ws.merge_cells('A1:H1')
    _cell(1, 1, workshop_name + ' — أمر عمل: ' + order.order_number,
          bold=True, color='FFFFFF', fill=green_fill, size=13)
    ws.row_dimensions[1].height = 28

    # الحالة والتاريخ
    ws.merge_cells('A2:D2'); ws.merge_cells('E2:H2')
    _cell(2, 1, f'الحالة: {order.status}', bold=True, color='09572b', fill=light_fill)
    created = order.created_at.strftime('%Y-%m-%d') if order.created_at else ''
    _cell(2, 5, f'التاريخ: {created}', bold=True, color='09572b', fill=light_fill)
    ws.row_dimensions[2].height = 18

    # بيانات العميل | المركبة
    ws.merge_cells('A3:D3'); ws.merge_cells('E3:H3')
    _cell(3, 1, 'بيانات العميل',  bold=True, color='FFFFFF', fill=green_fill)
    _cell(3, 5, 'بيانات المركبة', bold=True, color='FFFFFF', fill=green_fill)
    ws.row_dimensions[3].height = 18

    cust_info = [
        ('الاسم',   cust.name    if cust else ''),
        ('الهاتف',  cust.phone   if cust else ''),
        ('البريد',  cust.email   if cust else ''),
        ('العنوان', cust.address if cust else ''),
    ]
    veh_info = [
        ('الماركة',    veh.make         if veh else ''),
        ('الموديل',    veh.model        if veh else ''),
        ('سنة الصنع',  str(veh.year)    if veh and veh.year else ''),
        ('رقم اللوحة', veh.plate_number if veh else ''),
    ]
    for i, ((lbl, val), (vlbl, vval)) in enumerate(zip(cust_info, veh_info), 4):
        ws.merge_cells(f'A{i}:B{i}'); ws.merge_cells(f'C{i}:D{i}')
        ws.merge_cells(f'E{i}:F{i}'); ws.merge_cells(f'G{i}:H{i}')
        _cell(i, 1, lbl,  bold=True, fill=alt_fill)
        _cell(i, 3, val)
        _cell(i, 5, vlbl, bold=True, fill=alt_fill)
        _cell(i, 7, vval)
        ws.row_dimensions[i].height = 15

    # رأس جدول البنود
    item_row = 9
    hdrs = ['#','كود الصنف','اسم الصنف','الوصف','الوحدة','الكمية','سعر الوحدة','الإجمالي']
    for c, h in enumerate(hdrs, 1):
        _cell(item_row, c, h, bold=True, color='FFFFFF', fill=green_fill, size=11)
    ws.row_dimensions[item_row].height = 20

    # بنود
    for idx, item in enumerate(items, 1):
        r = item_row + idx
        f = alt_fill if idx % 2 == 0 else None
        for c, v in enumerate([idx, item.code, item.name, item.description or '',
                                item.unit, item.quantity, item.unit_price, item.total], 1):
            _cell(r, c, v, fill=f)
        ws.row_dimensions[r].height = 15

    # ملخص
    last = item_row + len(items)
    summary = [('مجموع البنود', order.price)]
    if order.discount:
        summary.append(('الخصم', -order.discount))
    summary.append(('الإجمالي النهائي', order.final_price))
    for i, (lbl, val) in enumerate(summary, 1):
        r = last + i
        is_final = (lbl == 'الإجمالي النهائي')
        f = green_fill if is_final else total_fill
        tc = 'FFFFFF' if is_final else '09572b'
        ws.merge_cells(f'A{r}:G{r}')
        _cell(r, 1, lbl, bold=True, color=tc, fill=f)
        _cell(r, 8, val, bold=True, color=tc, fill=f)
        ws.row_dimensions[r].height = 17

    # ملاحظات
    if order.notes:
        nr = last + len(summary) + 2
        ws.merge_cells(f'A{nr}:H{nr}')
        _cell(nr, 1, 'ملاحظات', bold=True, color='FFFFFF', fill=green_fill)
        nr += 1
        ws.merge_cells(f'A{nr}:H{nr}')
        _cell(nr, 1, order.notes)
        ws.row_dimensions[nr].height = 24

    for i, w in enumerate([6,14,22,24,10,10,14,14], 1):
        from openpyxl.utils import get_column_letter as gcl
        ws.column_dimensions[gcl(i)].width = w

    output = io.BytesIO()
    wb.save(output); output.seek(0)
    fname = f'order_{order.order_number}_{datetime.utcnow().strftime("%Y%m%d")}.xlsx'
    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=fname)


def _categories_json(categories) -> str:
    """ظٹظڈط­ظˆظ‘ظ„ ظ‚ط§ط¦ظ…ط© ط§ظ„ط£طµظ†ط§ظپ ط¥ظ„ظ‰ JSON ظ„ظ„ظ€ JavaScript."""
    return json.dumps([c.to_dict() for c in categories], ensure_ascii=False)

