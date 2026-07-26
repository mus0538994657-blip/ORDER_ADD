import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """الإعدادات الأساسية للتطبيق."""

    # الأمان
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # ساعة واحدة

    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///workshop.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # معلومات الورشة
    WORKSHOP_NAME = os.environ.get('WORKSHOP_NAME', 'ورشة تركيب زجاج المركبات')
    WORKSHOP_PHONE = os.environ.get('WORKSHOP_PHONE', '')
    WORKSHOP_ADDRESS = os.environ.get('WORKSHOP_ADDRESS', '')

    # حالات الطلب
    ORDER_STATUSES = ['قيد الانتظار', 'قيد التنفيذ', 'مكتمل', 'ملغي']

    # تحديد معدل الطلبات
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '200 per day;50 per hour'

    # الكاش
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    # الترقيم
    ORDERS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workshop.db'


class ProductionConfig(Config):
    DEBUG = False
    WTF_CSRF_SSL_STRICT = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}