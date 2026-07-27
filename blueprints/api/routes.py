"""
API v1 â€” ظ…ط³ط§ط±ط§طھ JSON ظ„ظ„ط§ط³طھط®ط¯ط§ظ… ط§ظ„ط¯ط§ط®ظ„ظٹ.
ط§ظ„ظ…طµط§ط¯ظ‚ط© ط¹ط¨ط± ط§ظ„ط¬ظ„ط³ط© (Flask-Login) ظپظ‚ط·.
"""
from datetime import datetime
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required
from extensions import db
from models.order import Order
from models.customer import Customer
from models.vehicle import Vehicle
from models.category import Category

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
# /api/v1/customers/<id>/vehicles  â€” ظ„طھط­ظ…ظٹظ„ ط§ظ„ظ…ط±ظƒط¨ط§طھ ط¨ظ€ AJAX ظپظٹ ظ†ظ…ظˆط°ط¬ ط§ظ„ط·ظ„ط¨
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
# /api/v1/categories/search?code=<code>  â€” ط§ظ„ط¨ط­ط« ط¨ظƒظˆط¯ ط§ظ„طµظ†ظپ (ظ„ظ„ظ€ AJAX ظپظٹ ط§ظ„ط·ظ„ط¨)
# ---------------------------------------------------------------------------

@api_bp.route('/categories/search')
@login_required
def api_category_search():
    """
    ظٹظڈط¹ظٹط¯ ط¨ظٹط§ظ†ط§طھ ط§ظ„طµظ†ظپ ط¹ظ†ط¯ ط§ظ„ط¨ط­ط« ط¨ط§ظ„ظƒظˆط¯ ط£ظˆ ط§ظ„ط§ط³ظ….
    Query params:
        code  â€” ظƒظˆط¯ ط§ظ„طµظ†ظپ (ظ…ط·ط§ط¨ظ‚ط© ظƒط§ظ…ظ„ط©)
        q     â€” ط¨ط­ط« ط¬ط²ط¦ظٹ ظپظٹ ط§ظ„ظƒظˆط¯ ط£ظˆ ط§ظ„ط§ط³ظ…
    """
    code = request.args.get('code', '').strip().upper()
    q    = request.args.get('q', '').strip()

    if code:
        cat = Category.query.filter(
            db.func.upper(Category.code) == code,
            Category.is_active == True,
        ).first()
        if not cat:
            return jsonify({'error': 'ط§ظ„ظƒظˆط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯'}), 404
        return jsonify(cat.to_dict())

    if q:
        like = f'%{q}%'
        cats = Category.query.filter(
            Category.is_active == True,
            db.or_(
                Category.code.ilike(like),
                Category.name.ilike(like),
            )
        ).order_by(Category.code).limit(20).all()
        return jsonify([c.to_dict() for c in cats])

    return jsonify({'error': 'ظٹط¬ط¨ طھظ…ط±ظٹط± code ط£ظˆ q'}), 400


# ---------------------------------------------------------------------------
# /api/v1/stats/dashboard
# ---------------------------------------------------------------------------

@api_bp.route('/stats/dashboard')
@login_required
def api_dashboard_stats():
    today = datetime.utcnow().date()

    total_orders = Order.query.count()
    pending      = Order.query.filter_by(status=Order.STATUS_PENDING).count()
    in_progress  = Order.query.filter_by(status=Order.STATUS_IN_PROGRESS).count()
    completed    = Order.query.filter_by(status=Order.STATUS_COMPLETED).count()
    cancelled    = Order.query.filter_by(status=Order.STATUS_CANCELLED).count()

    revenue = db.session.query(
        db.func.sum(Order.final_price)
    ).filter_by(status=Order.STATUS_COMPLETED).scalar() or 0.0

    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()

    total_customers = Customer.query.filter_by(is_active=True).count()
    total_vehicles  = Vehicle.query.count()

    return jsonify({
        'orders': {
            'total':       total_orders,
            'pending':     pending,
            'in_progress': in_progress,
            'completed':   completed,
            'cancelled':   cancelled,
            'today':       today_orders,
        },
        'revenue':   round(revenue, 2),
        'customers': total_customers,
        'vehicles':  total_vehicles,
    })


