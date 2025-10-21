"""
重新创建数据库 - 使用新的用户表结构
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db

def recreate_database():
    """重新创建数据库"""
    app = create_app()
    
    with app.app_context():
        try:
            print("删除所有表...")
            db.drop_all()
            
            print("创建所有表...")
            db.create_all()
            
            print("数据库重新创建完成！")
            return True
            
        except Exception as e:
            print(f"重新创建数据库失败: {e}")
            return False

if __name__ == '__main__':
    print("开始重新创建数据库...")
    success = recreate_database()
    if success:
        print("重新创建成功！")
    else:
        print("重新创建失败！")
        sys.exit(1)
