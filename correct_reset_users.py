#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确的用户数据重置脚本 - 重置Flask应用实际使用的数据库
"""

import sqlite3
import hashlib
import os
import sys

def hash_password(password):
    """生成与Flask应用兼容的密码哈希"""
    # 模拟Werkzeug的密码哈希格式
    import base64
    salt = b'salt'
    hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"pbkdf2:sha256:100000${base64.b64encode(salt).decode()}${base64.b64encode(hash_bytes).decode()}"

def reset_database_with_new_users():
    """清除所有数据并创建新用户"""
    # Flask应用运行时的数据库路径（相对于项目根目录）
    db_paths = [
        '/Users/bizai/Desktop/项目推荐表设计/instance/project_management.db',  # Flask默认路径
        '/Users/bizai/Desktop/项目推荐表设计/backend/instance/project_management.db'  # 备用路径
    ]
    
    success_count = 0
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"⚠️  数据库文件不存在: {db_path}")
            continue
            
        print(f"\n🔄 正在重置数据库: {db_path}")
        
        try:
            # 连接数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("🗑️  正在清除所有数据...")
            
            # 删除所有表中的数据（按依赖关系顺序）
            tables_to_clear = [
                'module_work_records',
                'module_progress_records', 
                'module_assignments',
                'project_modules',
                'project_members',
                'projects',
                'users'
            ]
            
            for table in tables_to_clear:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"  ✅ 清除表: {table}")
                except sqlite3.OperationalError as e:
                    if "no such table" not in str(e).lower():
                        print(f"  ⚠️  清除表 {table} 时出错: {e}")
            
            print("✅ 所有数据已清除")
            
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
            
            # 检查users表结构
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"  📋 用户表结构: {columns}")
            
            # 插入用户数据
            for user_data in users_data:
                try:
                    cursor.execute('''
                        INSERT INTO users (name, username, password_hash, position, role, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    ''', (
                        user_data["name"],
                        user_data["username"], 
                        password_hash,
                        user_data["position"],
                        user_data["role"]
                    ))
                    
                    print(f"  ✅ 创建用户: {user_data['name']} ({user_data['username']}) - {user_data['position']} - {user_data['role']}")
                except sqlite3.IntegrityError as e:
                    print(f"  ⚠️  用户 {user_data['name']} 创建失败: {e}")
            
            # 提交事务
            conn.commit()
            conn.close()
            
            print(f"✅ 数据库 {db_path} 重置成功!")
            success_count += 1
            
        except Exception as e:
            print(f"❌ 重置数据库 {db_path} 失败: {str(e)}")
            if 'conn' in locals():
                conn.close()
    
    if success_count > 0:
        print(f"\n🎉 成功重置 {success_count} 个数据库!")
        print("\n📋 用户登录信息:")
        print("-" * 70)
        print(f"{'姓名':<10} {'用户名':<15} {'密码':<12} {'职位':<20} {'角色'}")
        print("-" * 70)
        
        for user in users_data:
            print(f"{user['name']:<10} {user['username']:<15} {default_password:<12} {user['position']:<20} {user['role']}")
        
        print("-" * 70)
        return True
    else:
        return False

def verify_database_content():
    """验证数据库内容"""
    db_paths = [
        '/Users/bizai/Desktop/项目推荐表设计/instance/project_management.db',
        '/Users/bizai/Desktop/项目推荐表设计/backend/instance/project_management.db'
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
            
        print(f"\n📊 验证数据库内容: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询用户数量
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"  👥 用户总数: {user_count}")
            
            # 查询用户列表
            cursor.execute("SELECT name, username, position, role FROM users ORDER BY id")
            users = cursor.fetchall()
            
            if users:
                print("  📋 用户列表:")
                for user in users:
                    print(f"    - {user[0]} ({user[1]}) - {user[2]} - {user[3]}")
            else:
                print("  ⚠️  没有找到用户数据")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ 验证失败: {str(e)}")

if __name__ == "__main__":
    print("🔄 开始重置数据库并导入新用户数据...")
    success = reset_database_with_new_users()
    
    if success:
        print("\n✅ 数据库重置完成!")
        print("\n🔍 验证数据库内容...")
        verify_database_content()
        
        print("\n🚀 现在可以使用以下账号登录系统:")
        print("👑 管理员账号: gaojiamin / td123456 (高吉敏 - 部门主管)")
        print("👤 普通用户: yangjitong / td123456 (杨继同 - 电气工程师)")
        print("   其他用户请查看上面的完整列表")
        
        print("\n💡 请重启后端服务以确保更改生效!")
    else:
        print("\n❌ 数据库重置失败!")
        sys.exit(1)

