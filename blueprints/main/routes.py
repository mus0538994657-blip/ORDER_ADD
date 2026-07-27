from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from extensions import db
from models.order import Order
from models.customer import Customer
from models.category import Category

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
@login_required
def index():
    """لوحة التحكم الرئيسية مع الإحصائيات."""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    # إحصائيات الطلبات
    total       = Order.query.count()
    pending     = Order.query.filter_by(status=Order.STATUS_PENDING).count()
    in_progress = Order.query.filter_by(status=Order.STATUS_IN_PROGRESS).count()
    completed   = Order.query.filter_by(status=Order.STATUS_COMPLETED).count()
    cancelled   = Order.query.filter_by(status=Order.STATUS_CANCELLED).count()

    # إيرادات الطلبات المكتملة
    revenue = db.session.query(
        db.func.coalesce(db.func.sum(Order.final_price), 0.0)
    ).filter_by(status=Order.STATUS_COMPLETED).scalar() or 0.0

    # طلبات اليوم
    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()

    today_revenue = db.session.query(
        db.func.coalesce(db.func.sum(Order.final_price), 0.0)
    ).filter(
        db.func.date(Order.created_at) == today,
        Order.status == Order.STATUS_COMPLETED,
    ).scalar() or 0.0

    # طلبات الأسبوع
    week_orders = Order.query.filter(
        db.func.date(Order.created_at) >= week_ago
    ).count()

    # العملاء والأصناف
    customers_count  = Customer.query.filter_by(is_active=True).count()
    categories_count = Category.query.filter_by(is_active=True).count()

    stats = {
        'total':            total,
        'pending':          pending,
        'in_progress':      in_progress,
        'completed':        completed,
        'cancelled':        cancelled,
        'revenue':          revenue,
        'today_orders':     today_orders,
        'today_revenue':    today_revenue,
        'week_orders':      week_orders,
        'customers_count':  customers_count,
        'categories_count': categories_count,
        # نسب التوزيع للشريط البياني
        'pct_pending':     round(pending     / total * 100) if total else 0,
        'pct_progress':    round(in_progress / total * 100) if total else 0,
        'pct_completed':   round(completed   / total * 100) if total else 0,
        'pct_cancelled':   round(cancelled   / total * 100) if total else 0,
    }

    recent_orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .limit(8)
        .all()
    )

    return render_template('index.html', stats=stats, recent_orders=recent_orders)