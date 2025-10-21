#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复用户密码哈希问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_user_passwords():
    """修复用户密码哈希"""
    try:
        # 需要在Flask应用上下文中运行
        from backend.app import create_app
        from backend.models.database import db, User
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        
        with app.app_context():
            print("🔧 开始修复用户密码...")
            
            # 获取所有用户
            users = User.query.all()
            print(f"📋 找到 {len(users)} 个用户")
            
            default_password = "td123456"
            correct_hash = generate_password_hash(default_password)
            
            print(f"🔐 默认密码: {default_password}")
            print(f"🔐 正确的哈希格式: {correct_hash}")
            
            # 更新所有用户的密码
            for user in users:
                print(f"🔄 更新用户: {user.name} ({user.username})")
                user.password_hash = correct_hash
                
            # 提交更改
            db.session.commit()
            print("✅ 所有用户密码已修复!")
            
            # 验证修复结果
            print("\n🔍 验证修复结果:")
            for user in users:
                # 测试密码验证
                from werkzeug.security import check_password_hash
                is_valid = check_password_hash(user.password_hash, default_password)
                status = "✅" if is_valid else "❌"
                print(f"  {status} {user.name} ({user.username}): 密码验证{'成功' if is_valid else '失败'}")
            
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始修复用户密码哈希问题...")
    success = fix_user_passwords()
    
    if success:
        print("\n✅ 密码修复完成!")
        print("🔑 现在可以使用以下账号登录:")
        print("👑 管理员: gaojiamin / td123456")
        print("👤 普通用户: yangjitong / td123456")
        print("   (所有用户密码都是 td123456)")
    else:
        print("\n❌ 密码修复失败!")
        sys.exit(1)

