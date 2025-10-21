#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置数据库并导入新的用户数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.models.database import db, User, UserRole, Project, ProjectModule, ModuleProgressRecord, ModuleWorkRecord, ModuleAssignment
from werkzeug.security import generate_password_hash

def reset_database_with_new_users():
    """清除所有数据并创建新用户"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  正在清除所有数据...")
            
            # 删除所有表中的数据（按依赖关系顺序）
            ModuleWorkRecord.query.delete()
            ModuleProgressRecord.query.delete()
            ModuleAssignment.query.delete()
            ProjectModule.query.delete()
            Project.query.delete()
            User.query.delete()
            
            db.session.commit()
            print("✅ 所有数据已清除")
            
            print("\n👥 正在创建新用户...")
            
            # 新用户数据
            users_data = [
                {"name": "高吉敏", "position": "部门主管", "role": UserRole.DEPARTMENT_MANAGER},
                {"name": "杨继同", "position": "电气工程师", "role": UserRole.MEMBER},
                {"name": "赵权", "position": "机械工程师", "role": UserRole.MEMBER},
                {"name": "金航杰", "position": "PCB工程师", "role": UserRole.MEMBER},
                {"name": "高建鹏", "position": "PCB工程师", "role": UserRole.MEMBER},
                {"name": "王鹏", "position": "高级研发工程师", "role": UserRole.MEMBER},
                {"name": "周引", "position": "机械工程师", "role": UserRole.MEMBER},
                {"name": "杨帆", "position": "视觉工程师", "role": UserRole.MEMBER},
                {"name": "毕庆鹏", "position": "质量工程师", "role": UserRole.MEMBER},
            ]
            
            # 创建用户
            created_users = []
            for user_data in users_data:
                # 生成用户名（使用姓名的拼音或简化版本）
                name_to_username = {
                    "高吉敏": "gaojiamin",
                    "杨继同": "yangjitong", 
                    "赵权": "zhaoquan",
                    "金航杰": "jinhangje",
                    "高建鹏": "gaojianpeng",
                    "王鹏": "wangpeng",
                    "周引": "zhouyin",
                    "杨帆": "yangfan",
                    "毕庆鹏": "biqingpeng"
                }
                
                username = name_to_username.get(user_data["name"], user_data["name"].lower())
                password = "td123456"  # 默认密码
                
                user = User(
                    name=user_data["name"],
                    username=username,
                    password_hash=generate_password_hash(password),
                    position=user_data["position"],
                    role=user_data["role"]
                )
                
                db.session.add(user)
                created_users.append({
                    "name": user_data["name"],
                    "username": username,
                    "password": password,
                    "position": user_data["position"],
                    "role": user_data["role"].value
                })
                
                print(f"✅ 创建用户: {user_data['name']} ({username}) - {user_data['position']} - {user_data['role'].value}")
            
            db.session.commit()
            
            print(f"\n🎉 成功创建 {len(created_users)} 个用户!")
            print("\n📋 用户登录信息:")
            print("-" * 60)
            print(f"{'姓名':<10} {'用户名':<15} {'密码':<12} {'职位':<15} {'角色'}")
            print("-" * 60)
            
            for user in created_users:
                print(f"{user['name']:<10} {user['username']:<15} {user['password']:<12} {user['position']:<15} {user['role']}")
            
            print("-" * 60)
            print("\n💡 说明:")
            print("- 所有用户的默认密码都是: td123456")
            print("- 高吉敏是部门主管，拥有最高权限")
            print("- 其他人员都是普通成员")
            print("- 用户名是姓名的拼音")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 操作失败: {str(e)}")
            return False

if __name__ == "__main__":
    print("🔄 开始重置数据库并导入新用户数据...")
    success = reset_database_with_new_users()
    
    if success:
        print("\n✅ 数据库重置完成!")
        print("\n🚀 现在可以使用以下账号登录系统:")
        print("👑 管理员账号: gaojiamin / td123456 (高吉敏 - 部门主管)")
        print("👤 普通用户: yangjitong / td123456 (杨继同 - 电气工程师)")
        print("   其他用户请查看上面的完整列表")
    else:
        print("\n❌ 数据库重置失败!")
        sys.exit(1)


