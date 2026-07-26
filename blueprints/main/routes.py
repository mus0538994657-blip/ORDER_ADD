from flask import Blueprint, render_template
from flask_login import login_required
from models.order import Order
from models.category import Category

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
@login_required
def index():
    """لوحة التحكم الرئيسية مع الإحصائيات."""
    stats = {
        'total': Order.query.count(),
        'pending': Order.query.filter_by(status=Order.STATUS_PENDING).count(),
        'in_progress': Order.query.filter_by(status=Order.STATUS_IN_PROGRESS).count(),
        'completed': Order.query.filter_by(status=Order.STATUS_COMPLETED).count(),
        'cancelled': Order.query.filter_by(status=Order.STATUS_CANCELLED).count(),
    }

    # إيرادات الطلبات المكتملة
    from extensions import db
    revenue_row = db.session.query(
        db.func.sum(Order.final_price)
    ).filter_by(status=Order.STATUS_COMPLETED).scalar()
    stats['revenue'] = revenue_row or 0.0

    recent_orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template('index.html', stats=stats, recent_orders=recent_orders)
