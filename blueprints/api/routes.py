"""
API v1 — مسارات JSON للاستخدام الداخلي.
المصادقة عبر الجلسة (Flask-Login) فقط.
"""
from datetime import datetime
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required
from extensions import db
from models.order import Order
from models.customer import Customer
from models.vehicle import Vehicle

api_bp = Blueprint('api_bp', __name__, url_prefix='/api/v1')


def _paginate(query, page: int, per_page: int = 50):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination


# ---------------------------------------------------------------------------
# /api/v1/orders
# ---------------------------------------------------------------------------

@api_bp.route('/orders')
@login_required
def api_orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    q = request.args.get('q', '').strip()

    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if q:
        like = f'%{q}%'
        query = query.join(Customer).filter(
            db.or_(
                Customer.name.ilike(like),
                Customer.phone.ilike(like),
                Order.order_number.ilike(like),
            )
        )

    pg = _paginate(query.order_by(Order.created_at.desc()), page)
    return jsonify({
        'data': [o.to_dict() for o in pg.items],
        'total': pg.total,
        'pages': pg.pages,
        'page': pg.page,
    })


# ---------------------------------------------------------------------------
# /api/v1/customers
# ---------------------------------------------------------------------------

@api_bp.route('/customers')
@login_required
def api_customers():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()

    query = Customer.query.filter_by(is_active=True)
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Customer.name.ilike(like),
                Customer.phone.ilike(like),
            )
        )

    pg = _paginate(query.order_by(Customer.name), page)
    return jsonify({
        'data': [
            {
                'id': c.id,
                'name': c.name,
                'phone': c.phone or '',
                'email': c.email or '',
                'vehicles_count': c.vehicles_count,
                'orders_count': c.orders_count,
            }
            for c in pg.items
        ],
        'total': pg.total,
        'pages': pg.pages,
        'page': pg.page,
    })


# ---------------------------------------------------------------------------
# /api/v1/customers/<id>/vehicles  — لتحميل المركبات بـ AJAX في نموذج الطلب
# ---------------------------------------------------------------------------

@api_bp.route('/customers/<int:cust_id>/vehicles')
@login_required
def api_customer_vehicles(cust_id):
    customer = Customer.query.get_or_404(cust_id)
    vehicles = customer.vehicles.order_by(Vehicle.plate_number).all()
    return jsonify([v.to_dict() for v in vehicles])


# ---------------------------------------------------------------------------
# /api/v1/vehicles
# ---------------------------------------------------------------------------

@api_bp.route('/vehicles')
@login_required
def api_vehicles():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()

    query = Vehicle.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Vehicle.plate_number.ilike(like),
                Vehicle.make.ilike(like),
                Vehicle.model.ilike(like),
            )
        )

    pg = _paginate(query.order_by(Vehicle.plate_number), page)
    return jsonify({
        'data': [v.to_dict() for v in pg.items],
        'total': pg.total,
        'pages': pg.pages,
        'page': pg.page,
    })


# ---------------------------------------------------------------------------
# /api/v1/stats/dashboard
# ---------------------------------------------------------------------------

@api_bp.route('/stats/dashboard')
@login_required
def api_dashboard_stats():
    today = datetime.utcnow().date()

    total_orders = Order.query.count()
    pending = Order.query.filter_by(status=Order.STATUS_PENDING).count()
    in_progress = Order.query.filter_by(status=Order.STATUS_IN_PROGRESS).count()
    completed = Order.query.filter_by(status=Order.STATUS_COMPLETED).count()
    cancelled = Order.query.filter_by(status=Order.STATUS_CANCELLED).count()

    revenue = db.session.query(
        db.func.sum(Order.final_price)
    ).filter_by(status=Order.STATUS_COMPLETED).scalar() or 0.0

    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()

    total_customers = Customer.query.filter_by(is_active=True).count()
    total_vehicles = Vehicle.query.count()

    return jsonify({
        'orders': {
            'total': total_orders,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'cancelled': cancelled,
            'today': today_orders,
        },
        'revenue': round(revenue, 2),
        'customers': total_customers,
        'vehicles': total_vehicles,
    })
