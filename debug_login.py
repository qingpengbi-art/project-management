#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试登录问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_login():
    """调试登录问题"""
    try:
        from backend.app import create_app
        from backend.models.database import User
        from backend.services.auth_service import AuthService
        
        app = create_app()
        
        with app.app_context():
            print("🔍 调试登录问题...")
            
            username = 'gaojiamin'
            password = 'td123456'
            
            print(f"📝 尝试登录: {username} / {password}")
            
            # 1. 检查用户是否存在
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"✅ 用户存在: {user.name} ({user.username})")
                print(f"🔐 密码哈希: {user.password_hash[:50]}...")
                print(f"👤 角色: {user.role.value}")
                
                # 2. 测试密码验证
                is_valid = user.check_password(password)
                print(f"🔐 密码验证: {'✅ 成功' if is_valid else '❌ 失败'}")
                
                # 3. 测试认证服务
                auth_user = AuthService.authenticate_user(username, password)
                print(f"🔐 认证服务: {'✅ 成功' if auth_user else '❌ 失败'}")
                
                if not auth_user:
                    print("🔍 详细调试认证服务...")
                    # 手动执行认证逻辑
                    try:
                        user_check = User.query.filter_by(username=username).first()
                        print(f"  - 查询用户: {'✅' if user_check else '❌'}")
                        if user_check:
                            pwd_check = user_check.check_password(password)
                            print(f"  - 密码检查: {'✅' if pwd_check else '❌'}")
                            if pwd_check:
                                print(f"  - 返回用户: {user_check.name}")
                            else:
                                print(f"  - 密码不匹配!")
                    except Exception as e:
                        print(f"  - 认证异常: {e}")
                
            else:
                print("❌ 用户不存在")
                # 列出所有用户
                print("\n📋 数据库中的所有用户:")
                all_users = User.query.all()
                for u in all_users:
                    print(f"  - {u.name} ({u.username})")
                
    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_login()

