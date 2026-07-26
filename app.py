import os
from flask import Flask
from config import config_map
from extensions import db, login_manager, migrate, cache, limiter, csrf


def create_app(config_name: str = None) -> Flask:
    """Application factory — ينشئ ويُهيّئ تطبيق Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_shell_context(app)
    _register_cli_commands(app)

    # تهيئة قاعدة البيانات والبذر عند أول تشغيل
    with app.app_context():
        db.create_all()
        from seeds import run_seeds
        run_seeds()

    return app


# ---------------------------------------------------------------------------
# تهيئة الإضافات
# ---------------------------------------------------------------------------

def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)


# ---------------------------------------------------------------------------
# تسجيل الـ Blueprints
# ---------------------------------------------------------------------------

def _register_blueprints(app: Flask) -> None:
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.orders import orders_bp
    from blueprints.categories import categories_bp
    from blueprints.reports import reports_bp
    from blueprints.customers import customers_bp
    from blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(api_bp)


# ---------------------------------------------------------------------------
# معالجات الأخطاء
# ---------------------------------------------------------------------------

def _register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def too_many_requests(e):
        from flask import flash, redirect, url_for
        flash('لقد تجاوزت الحد المسموح من الطلبات. يرجى الانتظار قبل المحاولة مجدداً.', 'danger')
        return render_template('errors/429.html'), 429

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {'now': datetime.utcnow()}


# ---------------------------------------------------------------------------
# Shell context للتطوير
# ---------------------------------------------------------------------------

def _register_shell_context(app: Flask) -> None:
    from models.user import User
    from models.customer import Customer
    from models.vehicle import Vehicle
    from models.category import Category
    from models.order import Order

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db, 'User': User, 'Customer': Customer,
            'Vehicle': Vehicle, 'Category': Category, 'Order': Order,
        }


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def _register_cli_commands(app: Flask) -> None:
    import click

    @app.cli.command('seed-db')
    def seed_db():
        """تعبئة قاعدة البيانات بالبيانات الافتراضية."""
        from seeds import run_seeds
        run_seeds()
        click.echo('✅ تمت تعبئة قاعدة البيانات بنجاح.')

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    def create_admin(username, password):
        """إنشاء مستخدم مسؤول جديد."""
        from models.user import User
        if User.query.filter_by(username=username).first():
            click.echo(f'❌ المستخدم "{username}" موجود بالفعل.')
            return
        user = User(username=username, email=f'{username}@workshop.local',
                    full_name='مدير النظام', is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'✅ تم إنشاء المسؤول "{username}" بنجاح.')
