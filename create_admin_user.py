#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建管理员用户用于测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_admin_user():
    """创建管理员用户"""
    try:
        from backend.app import create_app
        from backend.models.database import db, User, UserRole
        
        app = create_app()
        
        with app.app_context():
            print("🔧 创建管理员用户...")
            
            # 删除现有的admin用户
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                db.session.delete(existing_admin)
                print("🗑️ 删除现有admin用户")
            
            # 创建新的admin用户
            admin = User(
                name='管理员',
                username='admin',
                email='admin@test.com',
                position='系统管理员',
                role=UserRole.DEPARTMENT_MANAGER
            )
            admin.set_password('td123456')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ 管理员用户创建成功!")
            print(f"👤 姓名: {admin.name}")
            print(f"👤 用户名: {admin.username}")
            print(f"🔐 密码: td123456")
            print(f"👤 角色: {admin.role.value}")
            
            # 验证创建结果
            test_admin = User.query.filter_by(username='admin').first()
            if test_admin and test_admin.check_password('td123456'):
                print("✅ 用户创建验证成功!")
            else:
                print("❌ 用户创建验证失败!")
                
            # 显示所有用户
            print(f"\n📋 数据库中共有 {User.query.count()} 个用户")
            
    except Exception as e:
        print(f"❌ 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()

