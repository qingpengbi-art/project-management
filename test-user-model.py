#!/usr/bin/env python3
"""
测试User模型字段
验证docker-start.sh中的用户创建代码是否正确
"""

import sys
import os

# 设置路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import User, UserRole
from werkzeug.security import generate_password_hash

# 测试创建用户
try:
    # 测试管理员用户
    admin = User(
        name='系统管理员',
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role=UserRole.DEPARTMENT_MANAGER,
        email='admin@example.com'
    )
    print("✅ 管理员用户对象创建成功")
    print(f"   name: {admin.name}")
    print(f"   username: {admin.username}")
    print(f"   role: {admin.role}")
    print(f"   email: {admin.email}")
    
    # 测试普通用户
    user = User(
        name='张三',
        username='zhangsan',
        password_hash=generate_password_hash('123456'),
        role=UserRole.MEMBER,
        email='zhangsan@example.com'
    )
    print("\n✅ 普通用户对象创建成功")
    print(f"   name: {user.name}")
    print(f"   username: {user.username}")
    print(f"   role: {user.role}")
    print(f"   email: {user.email}")
    
    print("\n🎉 所有用户模型测试通过！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

