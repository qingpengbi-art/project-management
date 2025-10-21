#!/usr/bin/env python3
"""
数据库清理脚本
清理无效的枚举值和数据
"""

import sqlite3
import sys
import os

def clean_database():
    """清理数据库中的无效数据"""
    db_path = "backend/project_management.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧹 开始清理数据库...")
        
        # 清理无效的项目状态
        print("📋 清理项目状态...")
        cursor.execute("""
            UPDATE projects 
            SET status = 'INITIAL_CONTACT' 
            WHERE status NOT IN (
                'INITIAL_CONTACT', 'PROPOSAL_SUBMITTED', 'QUOTATION_SUBMITTED', 
                'USER_CONFIRMATION', 'CONTRACT_SIGNED', 'PROJECT_IMPLEMENTATION', 
                'PROJECT_ACCEPTANCE', 'WARRANTY_PERIOD', 'POST_WARRANTY', 'NO_FOLLOW_UP'
            )
        """)
        invalid_project_status = cursor.rowcount
        
        # 清理无效的模块状态
        print("📦 清理模块状态...")
        cursor.execute("""
            UPDATE project_modules 
            SET status = 'NOT_STARTED' 
            WHERE status NOT IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'PAUSED', 'CANCELLED')
        """)
        invalid_module_status = cursor.rowcount
        
        # 清理无效的用户角色
        print("👥 清理用户角色...")
        cursor.execute("""
            UPDATE users 
            SET role = 'MEMBER' 
            WHERE role NOT IN ('DEPARTMENT_MANAGER', 'MEMBER')
        """)
        invalid_user_roles = cursor.rowcount
        
        # 清理无效的项目成员角色
        print("🤝 清理项目成员角色...")
        cursor.execute("""
            UPDATE project_members 
            SET role = 'MEMBER' 
            WHERE role NOT IN ('LEADER', 'MEMBER')
        """)
        invalid_member_roles = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print("✅ 数据库清理完成!")
        print(f"   - 修复了 {invalid_project_status} 个无效项目状态")
        print(f"   - 修复了 {invalid_module_status} 个无效模块状态")
        print(f"   - 修复了 {invalid_user_roles} 个无效用户角色")
        print(f"   - 修复了 {invalid_member_roles} 个无效成员角色")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理数据库时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = clean_database()
    sys.exit(0 if success else 1)
