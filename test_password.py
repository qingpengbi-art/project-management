#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户密码验证
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_password():
    """测试密码验证"""
    try:
        from backend.app import create_app
        from backend.models.database import User
        from backend.services.auth_service import AuthService
        
        app = create_app()
        
        with app.app_context():
            print("🔍 测试用户密码验证...")
            
            # 测试高吉敏用户
            user = User.query.filter_by(username='gaojiamin').first()
            if user:
                print(f"👤 找到用户: {user.name} ({user.username})")
                print(f"🔐 密码哈希: {user.password_hash[:50]}...")
                
                # 测试密码验证
                password = "td123456"
                is_valid = user.check_password(password)
                print(f"🔐 密码验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
                
                # 测试认证服务
                auth_user = AuthService.authenticate_user('gaojiamin', password)
                print(f"🔐 认证服务结果: {'✅ 成功' if auth_user else '❌ 失败'}")
                
                if auth_user:
                    print(f"🎉 认证成功的用户: {auth_user.name}")
                
            else:
                print("❌ 未找到用户 gaojiamin")
            
            # 列出所有用户
            print("\n📋 所有用户列表:")
            users = User.query.all()
            for user in users:
                print(f"  - {user.name} ({user.username}) - {user.role.value}")
                
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_password()

