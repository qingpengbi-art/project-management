#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复用户问题 - 直接在后端服务使用的数据库中重新创建所有用户
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def final_fix_users():
    """最终修复用户问题"""
    try:
        from backend.app import create_app
        from backend.models.database import db, User, UserRole
        
        app = create_app()
        
        with app.app_context():
            print("🔧 最终修复用户问题...")
            
            # 清除所有现有用户
            User.query.delete()
            db.session.commit()
            print("🗑️ 清除所有现有用户")
            
            # 创建新用户数据
            users_data = [
                {"name": "高吉敏", "username": "gaojiamin", "position": "部门主管", "role": UserRole.DEPARTMENT_MANAGER, "email": "gaojiamin@company.com"},
                {"name": "杨继同", "username": "yangjitong", "position": "电气工程师", "role": UserRole.MEMBER, "email": "yangjitong@company.com"},
                {"name": "赵权", "username": "zhaoquan", "position": "机械工程师", "role": UserRole.MEMBER, "email": "zhaoquan@company.com"},
                {"name": "金航杰", "username": "jinhangje", "position": "PCB工程师", "role": UserRole.MEMBER, "email": "jinhangje@company.com"},
                {"name": "高建鹏", "username": "gaojianpeng", "position": "PCB工程师", "role": UserRole.MEMBER, "email": "gaojianpeng@company.com"},
                {"name": "王鹏", "username": "wangpeng", "position": "高级研发工程师", "role": UserRole.MEMBER, "email": "wangpeng@company.com"},
                {"name": "周引", "username": "zhouyin", "position": "机械工程师", "role": UserRole.MEMBER, "email": "zhouyin@company.com"},
                {"name": "杨帆", "username": "yangfan", "position": "视觉工程师", "role": UserRole.MEMBER, "email": "yangfan@company.com"},
                {"name": "毕庆鹏", "username": "biqingpeng", "position": "质量工程师", "role": UserRole.MEMBER, "email": "biqingpeng@company.com"},
                {"name": "管理员", "username": "admin", "position": "系统管理员", "role": UserRole.DEPARTMENT_MANAGER, "email": "admin@company.com"},
            ]
            
            # 创建用户
            password = "td123456"
            for user_data in users_data:
                user = User(
                    name=user_data["name"],
                    username=user_data["username"],
                    email=user_data["email"],
                    position=user_data["position"],
                    role=user_data["role"]
                )
                user.set_password(password)
                db.session.add(user)
                print(f"✅ 创建用户: {user_data['name']} ({user_data['username']}) - {user_data['position']}")
            
            db.session.commit()
            
            # 验证创建结果
            total_users = User.query.count()
            print(f"\n🎉 成功创建 {total_users} 个用户!")
            
            print("\n📋 所有用户列表:")
            users = User.query.order_by(User.name).all()
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user.name} ({user.username}) - {user.position} - {user.role.value}")
            
            # 测试登录
            print(f"\n🔐 测试用户登录...")
            test_users = ['admin', 'gaojiamin', 'biqingpeng']
            for username in test_users:
                user = User.query.filter_by(username=username).first()
                if user and user.check_password(password):
                    print(f"  ✅ {user.name} ({username}): 登录测试成功")
                else:
                    print(f"  ❌ {username}: 登录测试失败")
            
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始最终修复用户问题...")
    success = final_fix_users()
    
    if success:
        print("\n✅ 用户问题修复完成!")
        print("🔑 现在可以使用以下账号登录:")
        print("👑 管理员账号: admin / td123456")
        print("👑 部门主管: gaojiamin / td123456 (高吉敏)")
        print("👤 普通用户: biqingpeng / td123456 (毕庆鹏)")
        print("   所有用户密码都是: td123456")
        print("\n💡 请刷新前端页面并重新登录!")
    else:
        print("\n❌ 用户问题修复失败!")
        sys.exit(1)

