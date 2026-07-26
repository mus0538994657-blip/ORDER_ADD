from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
limiter = Limiter(key_func=get_remote_address)

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)
    
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'warning'