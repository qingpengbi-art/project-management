#!/usr/bin/env python3
"""检查数据库中的用户信息"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 设置环境变量
os.environ['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'project_management.db')

from flask import Flask
from models.database import db, User
from werkzeug.security import check_password_hash

# 创建临时Flask应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.environ["DATABASE_PATH"]}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("=" * 60)
    print("数据库用户信息检查")
    print("=" * 60)
    print()
    
    users = User.query.all()
    
    if not users:
        print("⚠️  数据库中没有用户！")
    else:
        print(f"找到 {len(users)} 个用户：\n")
        
        for user in users:
            print(f"📋 用户 #{user.id}")
            print(f"   姓名: {user.name}")
            print(f"   用户名: {user.username}")
            print(f"   邮箱: {user.email}")
            print(f"   职位: {user.position}")
            print(f"   角色: {user.role.value if user.role else 'None'}")
            print(f"   密码哈希: {user.password_hash[:50]}...")
            
            # 测试密码
            if user.username == 'admin':
                test_pwd = 'admin123'
            else:
                test_pwd = '123456'
            
            is_valid = check_password_hash(user.password_hash, test_pwd)
            print(f"   测试密码 '{test_pwd}': {'✅ 正确' if is_valid else '❌ 错误'}")
            print()
    
    print("=" * 60)
    print("\n💡 提示：")
    print("   - admin 的密码应该是: admin123")
    print("   - 其他用户的密码应该是: 123456")
    print()

