#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的用户数据重置脚本
"""

import sqlite3
import hashlib
import os

def hash_password(password):
    """生成密码哈希"""
    # 使用简单的方法生成密码哈希
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000).hex()

def reset_database_with_new_users():
    """清除所有数据并创建新用户"""
    db_path = 'backend/instance/project_management.db'
    
    # 如果数据库文件不存在，创建目录
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️  正在清除所有数据...")
        
        # 删除所有表（如果存在）
        tables = [
            'module_work_records',
            'module_progress_records', 
            'module_assignments',
            'project_modules',
            'projects',
            'users'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            except:
                pass
        
        print("✅ 所有数据已清除")
        
        print("\n📋 正在创建用户表...")
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                position VARCHAR(100),
                role VARCHAR(20) NOT NULL DEFAULT 'MEMBER',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ 用户表创建成功")
        
        print("\n👥 正在创建新用户...")
        
        # 新用户数据
        users_data = [
            {"name": "高吉敏", "username": "gaojiamin", "position": "部门主管", "role": "DEPARTMENT_MANAGER"},
            {"name": "杨继同", "username": "yangjitong", "position": "电气工程师", "role": "MEMBER"},
            {"name": "赵权", "username": "zhaoquan", "position": "机械工程师", "role": "MEMBER"},
            {"name": "金航杰", "username": "jinhangje", "position": "PCB工程师", "role": "MEMBER"},
            {"name": "高建鹏", "username": "gaojianpeng", "position": "PCB工程师", "role": "MEMBER"},
            {"name": "王鹏", "username": "wangpeng", "position": "高级研发工程师", "role": "MEMBER"},
            {"name": "周引", "username": "zhouyin", "position": "机械工程师", "role": "MEMBER"},
            {"name": "杨帆", "username": "yangfan", "position": "视觉工程师", "role": "MEMBER"},
            {"name": "毕庆鹏", "username": "biqingpeng", "position": "质量工程师", "role": "MEMBER"},
        ]
        
        # 默认密码
        default_password = "td123456"
        password_hash = hash_password(default_password)
        
        # 插入用户数据
        for user_data in users_data:
            cursor.execute('''
                INSERT INTO users (name, username, password_hash, position, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_data["name"],
                user_data["username"], 
                password_hash,
                user_data["position"],
                user_data["role"]
            ))
            
            print(f"✅ 创建用户: {user_data['name']} ({user_data['username']}) - {user_data['position']} - {user_data['role']}")
        
        # 提交事务
        conn.commit()
        
        print(f"\n🎉 成功创建 {len(users_data)} 个用户!")
        print("\n📋 用户登录信息:")
        print("-" * 70)
        print(f"{'姓名':<10} {'用户名':<15} {'密码':<12} {'职位':<20} {'角色'}")
        print("-" * 70)
        
        for user in users_data:
            print(f"{user['name']:<10} {user['username']:<15} {default_password:<12} {user['position']:<20} {user['role']}")
        
        print("-" * 70)
        print("\n💡 说明:")
        print("- 所有用户的默认密码都是: td123456")
        print("- 高吉敏是部门主管，拥有最高权限")
        print("- 其他人员都是普通成员")
        print("- 用户名是姓名的拼音")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        if 'conn' in locals():
            conn.close()
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
        exit(1)
