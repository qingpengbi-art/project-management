#!/usr/bin/env python3
"""
数据库迁移脚本 - 更新项目金额字段
- 将 amount 字段重命名为 contract_amount（合同金额）
- 添加 received_amount 字段（到账金额）
- 删除 priority 字段（优先级）
"""

import sqlite3
import os

def migrate():
    """执行迁移"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'project_management.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"📊 开始迁移数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 projects 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            print("❌ projects 表不存在")
            return False
        
        print("✅ projects 表存在")
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(projects)")
        columns = {row[1]: row for row in cursor.fetchall()}
        column_names = list(columns.keys())
        
        print(f"📋 当前字段: {', '.join(column_names)}")
        
        # 1. 重命名 amount 为 contract_amount（如果存在）
        if 'amount' in column_names and 'contract_amount' not in column_names:
            print("🔄 重命名 amount -> contract_amount...")
            cursor.execute("ALTER TABLE projects RENAME COLUMN amount TO contract_amount")
            print("   ✅ 字段重命名成功")
        elif 'contract_amount' in column_names:
            print("   ℹ️  contract_amount 字段已存在，跳过重命名")
        else:
            # 如果 amount 和 contract_amount 都不存在，则添加 contract_amount
            print("➕ 添加 contract_amount 字段...")
            cursor.execute("ALTER TABLE projects ADD COLUMN contract_amount REAL")
            print("   ✅ contract_amount 字段添加成功")
        
        # 2. 添加 received_amount 字段（如果不存在）
        cursor.execute("PRAGMA table_info(projects)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'received_amount' not in columns:
            print("➕ 添加 received_amount 字段...")
            cursor.execute("ALTER TABLE projects ADD COLUMN received_amount REAL")
            print("   ✅ received_amount 字段添加成功")
        else:
            print("   ℹ️  received_amount 字段已存在，跳过添加")
        
        # 3. 删除 priority 字段
        # SQLite 不支持直接删除列，需要重建表
        cursor.execute("PRAGMA table_info(projects)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'priority' in columns:
            print("🗑️  删除 priority 字段（重建表）...")
            
            # 删除可能存在的临时表
            cursor.execute("DROP TABLE IF EXISTS projects_new")
            
            # 获取所有字段（除了 priority）
            columns_without_priority = [col for col in column_names if col != 'priority']
            
            # 添加新字段（如果刚才添加了）
            if 'contract_amount' not in columns_without_priority and 'amount' in columns_without_priority:
                columns_without_priority[columns_without_priority.index('amount')] = 'contract_amount'
            if 'received_amount' not in columns_without_priority:
                columns_without_priority.append('received_amount')
            
            # 创建临时表
            cursor.execute("""
                CREATE TABLE projects_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    start_date DATE,
                    end_date DATE,
                    actual_end_date DATE,
                    status VARCHAR(50),
                    progress INTEGER DEFAULT 0,
                    project_source VARCHAR(50) DEFAULT 'horizontal',
                    partner VARCHAR(100),
                    contract_amount REAL,
                    received_amount REAL,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            
            # 重新获取当前字段列表（因为可能已经重命名）
            cursor.execute("PRAGMA table_info(projects)")
            current_columns = {row[1]: row for row in cursor.fetchall()}
            current_column_names = list(current_columns.keys())
            
            print(f"   📋 当前字段: {', '.join(current_column_names)}")
            
            # 构建要复制的字段列表（排除 priority）
            fields_to_copy = []
            target_fields = []
            
            for col in ['id', 'name', 'description', 'start_date', 'end_date', 
                       'actual_end_date', 'status', 'progress', 'project_source', 
                       'partner', 'created_at', 'updated_at']:
                if col in current_column_names:
                    fields_to_copy.append(col)
                    target_fields.append(col)
            
            # 处理 contract_amount
            if 'contract_amount' in current_column_names:
                fields_to_copy.append('contract_amount')
                target_fields.append('contract_amount')
            
            # 处理 received_amount
            if 'received_amount' in current_column_names:
                fields_to_copy.append('received_amount')
                target_fields.append('received_amount')
            
            # 复制数据
            copy_fields = ', '.join(target_fields)
            select_fields = ', '.join(fields_to_copy)
            
            print(f"   📝 复制字段: {copy_fields}")
            
            cursor.execute(f"""
                INSERT INTO projects_new ({copy_fields})
                SELECT {select_fields} FROM projects
            """)
            
            # 删除旧表
            cursor.execute("DROP TABLE projects")
            
            # 重命名新表
            cursor.execute("ALTER TABLE projects_new RENAME TO projects")
            
            print("   ✅ priority 字段删除成功")
        else:
            print("   ℹ️  priority 字段不存在，跳过删除")
        
        # 提交更改
        conn.commit()
        
        # 验证更改
        cursor.execute("PRAGMA table_info(projects)")
        new_columns = [row[1] for row in cursor.fetchall()]
        
        print("\n📋 迁移后的字段:")
        for col in new_columns:
            print(f"   - {col}")
        
        print("\n✅ 数据库迁移成功!")
        print("   ✅ contract_amount（合同金额）字段已就绪")
        print("   ✅ received_amount（到账金额）字段已添加")
        print("   ✅ priority（优先级）字段已删除")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("="*50)
    print("项目字段更新迁移")
    print("="*50)
    migrate()

