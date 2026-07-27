"""
نماذج قاعدة البيانات — يُستورد منها مباشرةً في أي مكان.
الاستيراد هنا يضمن تسجيل جميع النماذج لدى SQLAlchemy.
"""
from models.user import User
from models.customer import Customer
from models.vehicle import Vehicle
from models.category import Category
from models.order import Order
from models.order_item import OrderItem

__all__ = ['User', 'Customer', 'Vehicle', 'Category', 'Order', 'OrderItem']
