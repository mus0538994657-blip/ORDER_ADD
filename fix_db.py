# fix_db.py
import sqlite3
import os

def fix_database():
    db_path = 'workshop.db'
    
    # التحقق من وجود قاعدة البيانات
    if not os.path.exists(db_path):
        print(f'❌ قاعدة البيانات غير موجودة: {db_path}')
        print('⚠️ سيتم إنشاء قاعدة بيانات جديدة عند تشغيل التطبيق')
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # عرض الأعمدة الحالية
        print('📋 التحقق من هيكل قاعدة البيانات...')
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print('\n📋 الأعمدة الحالية في جدول orders:')
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')
        
        # إضافة العمود إذا لم يكن موجوداً
        if 'customer_id' not in column_names:
            print('\n⚠️ جاري إضافة عمود customer_id...')
            cursor.execute("ALTER TABLE orders ADD COLUMN customer_id INTEGER")
            conn.commit()
            print('✅ تم إضافة عمود customer_id بنجاح')
            
            # عرض الأعمدة بعد الإضافة
            cursor.execute("PRAGMA table_info(orders)")
            print('\n📋 الأعمدة بعد الإضافة:')
            for col in cursor.fetchall():
                print(f'  - {col[1]} ({col[2]})')
        else:
            print('\n✅ عمود customer_id موجود بالفعل')
        
        # إضافة عمود customer_id في جدول customers إذا لم يكن موجوداً
        cursor.execute("PRAGMA table_info(customers)")
        customer_columns = [col[1] for col in cursor.fetchall()]
        
        if 'total_orders' not in customer_columns:
            print('\n⚠️ جاري إضافة أعمدة إضافية في جدول customers...')
            try:
                cursor.execute("ALTER TABLE customers ADD COLUMN total_orders INTEGER DEFAULT 0")
                cursor.execute("ALTER TABLE customers ADD COLUMN total_spent REAL DEFAULT 0")
                cursor.execute("ALTER TABLE customers ADD COLUMN last_order_date DATETIME")
                conn.commit()
                print('✅ تم إضافة الأعمدة في جدول customers')
            except:
                print('⚠️ بعض الأعمدة موجودة بالفعل')
        
        conn.close()
        print('\n✅ تم إصلاح قاعدة البيانات بنجاح!')
        return True
        
    except sqlite3.OperationalError as e:
        print(f'❌ خطأ في قاعدة البيانات: {e}')
        print('💡 قد تحتاج إلى حذف قاعدة البيانات وإعادة إنشائها')
        return False
    except Exception as e:
        print(f'❌ خطأ غير متوقع: {e}')
        return False

if __name__ == '__main__':
    print('🔧 إصلاح قاعدة البيانات - إضافة عمود customer_id')
    print('=' * 50)
    fix_database()