import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """الإعدادات الأساسية"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', False)
    
    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///workshop.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # معلومات الورشة
    WORKSHOP_NAME = os.environ.get('WORKSHOP_NAME', 'ورشة تركيب زجاج المركبات')
    WORKSHOP_PHONE = os.environ.get('WORKSHOP_PHONE', '')
    WORKSHOP_ADDRESS = os.environ.get('WORKSHOP_ADDRESS', '')
    WORKSHOP_EMAIL = os.environ.get('WORKSHOP_EMAIL', '')
    
    # حالات الطلب
    ORDER_STATUSES = ['قيد الانتظار', 'قيد التنفيذ', 'مكتمل', 'ملغي']
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # إعدادات التخزين المؤقت
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = 300

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workshop.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'