from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request,
)
from flask_login import login_required
from extensions import db
from models.customer import Customer
from models.vehicle import Vehicle
from .forms import CustomerForm, VehicleForm

customers_bp = Blueprint('customers_bp', __name__, url_prefix='/customers')


# ---------------------------------------------------------------------------
# قائمة العملاء
# ---------------------------------------------------------------------------

@customers_bp.route('/')
@login_required
def list_customers():
    search = request.args.get('q', '').strip()
    query = Customer.query
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Customer.name.ilike(like),
                Customer.phone.ilike(like),
                Customer.email.ilike(like),
            )
        )
    customers = query.order_by(Customer.name).all()
    return render_template('customers/list.html', customers=customers, search=search)


# ---------------------------------------------------------------------------
# تفاصيل العميل
# ---------------------------------------------------------------------------

@customers_bp.route('/view/<int:cust_id>')
@login_required
def view_customer(cust_id):
    customer = Customer.query.get_or_404(cust_id)
    return render_template('customers/detail.html', customer=customer)


# ---------------------------------------------------------------------------
# إضافة عميل
# ---------------------------------------------------------------------------

@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            email=form.email.data.strip().lower() if form.email.data else None,
            address=form.address.data.strip() if form.address.data else None,
            notes=form.notes.data.strip() if form.notes.data else None,
            is_active=form.is_active.data,
        )
        db.session.add(customer)
        db.session.commit()
        flash(f'✅ تم إضافة العميل "{customer.name}"', 'success')
        return redirect(url_for('customers_bp.view_customer', cust_id=customer.id))
    return render_template('customers/form.html', form=form, title='عميل جديد')


# ---------------------------------------------------------------------------
# تعديل عميل
# ---------------------------------------------------------------------------

@customers_bp.route('/edit/<int:cust_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(cust_id):
    customer = Customer.query.get_or_404(cust_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data.strip()
        customer.phone = form.phone.data.strip() if form.phone.data else None
        customer.email = form.email.data.strip().lower() if form.email.data else None
        customer.address = form.address.data.strip() if form.address.data else None
        customer.notes = form.notes.data.strip() if form.notes.data else None
        customer.is_active = form.is_active.data
        db.session.commit()
        flash(f'✅ تم تحديث بيانات العميل "{customer.name}"', 'success')
        return redirect(url_for('customers_bp.view_customer', cust_id=customer.id))
    return render_template('customers/form.html', form=form,
                           customer=customer, title=f'تعديل: {customer.name}')


# ---------------------------------------------------------------------------
# حذف عميل
# ---------------------------------------------------------------------------

@customers_bp.route('/delete/<int:cust_id>', methods=['POST'])
@login_required
def delete_customer(cust_id):
    customer = Customer.query.get_or_404(cust_id)
    if customer.orders_count > 0:
        flash('لا يمكن حذف عميل لديه طلبات. يمكنك تعطيله بدلاً من ذلك.', 'warning')
        return redirect(url_for('customers_bp.view_customer', cust_id=cust_id))
    name = customer.name
    db.session.delete(customer)
    db.session.commit()
    flash(f'🗑️ تم حذف العميل "{name}"', 'info')
    return redirect(url_for('customers_bp.list_customers'))


# ---------------------------------------------------------------------------
# إضافة مركبة للعميل
# ---------------------------------------------------------------------------

@customers_bp.route('/view/<int:cust_id>/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle(cust_id):
    customer = Customer.query.get_or_404(cust_id)
    form = VehicleForm()
    if form.validate_on_submit():
        vehicle = Vehicle(
            customer_id=customer.id,
            make=form.make.data.strip() if form.make.data else None,
            model=form.model.data.strip() if form.model.data else None,
            year=form.year.data.strip() if form.year.data else None,
            plate_number=form.plate_number.data.strip().upper() if form.plate_number.data else None,
            color=form.color.data.strip() if form.color.data else None,
            notes=form.notes.data.strip() if form.notes.data else None,
        )
        db.session.add(vehicle)
        db.session.commit()
        flash(f'✅ تم إضافة المركبة "{vehicle.full_description}"', 'success')
        return redirect(url_for('customers_bp.view_customer', cust_id=customer.id))
    return render_template('customers/vehicle_form.html', form=form,
                           customer=customer, title='مركبة جديدة')


# ---------------------------------------------------------------------------
# تعديل مركبة
# ---------------------------------------------------------------------------

@customers_bp.route('/vehicles/edit/<int:vid>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vid):
    vehicle = Vehicle.query.get_or_404(vid)
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        vehicle.make = form.make.data.strip() if form.make.data else None
        vehicle.model = form.model.data.strip() if form.model.data else None
        vehicle.year = form.year.data.strip() if form.year.data else None
        vehicle.plate_number = form.plate_number.data.strip().upper() if form.plate_number.data else None
        vehicle.color = form.color.data.strip() if form.color.data else None
        vehicle.notes = form.notes.data.strip() if form.notes.data else None
        db.session.commit()
        flash('✅ تم تحديث بيانات المركبة', 'success')
        return redirect(url_for('customers_bp.view_customer', cust_id=vehicle.customer_id))
    return render_template('customers/vehicle_form.html', form=form,
                           vehicle=vehicle, customer=vehicle.customer,
                           title=f'تعديل: {vehicle.full_description}')


# ---------------------------------------------------------------------------
# حذف مركبة
# ---------------------------------------------------------------------------

@customers_bp.route('/vehicles/delete/<int:vid>', methods=['POST'])
@login_required
def delete_vehicle(vid):
    vehicle = Vehicle.query.get_or_404(vid)
    cust_id = vehicle.customer_id
    if vehicle.orders.count() > 0:
        flash('لا يمكن حذف مركبة مرتبطة بطلبات.', 'warning')
        return redirect(url_for('customers_bp.view_customer', cust_id=cust_id))
    db.session.delete(vehicle)
    db.session.commit()
    flash('🗑️ تم حذف المركبة', 'info')
    return redirect(url_for('customers_bp.view_customer', cust_id=cust_id))
