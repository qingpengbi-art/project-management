#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加项目来源和合作方字段
"""

import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'project_management.db')

def migrate():
    """执行数据库迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("开始数据库迁移...")
        
        # 1. 检查字段是否已存在
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 2. 添加 project_source 字段（如果不存在）
        if 'project_source' not in columns:
            print("添加 project_source 字段...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN project_source TEXT DEFAULT 'horizontal'
            """)
            
            # 将所有现有项目设置为横向
            cursor.execute("""
                UPDATE projects 
                SET project_source = 'horizontal' 
                WHERE project_source IS NULL
            """)
            print("✅ project_source 字段添加成功，现有项目已设置为横向")
        else:
            print("⚠️  project_source 字段已存在，跳过")
        
        # 3. 添加 partner 字段（如果不存在）
        if 'partner' not in columns:
            print("添加 partner 字段...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN partner TEXT
            """)
            print("✅ partner 字段添加成功")
        else:
            print("⚠️  partner 字段已存在，跳过")
        
        # 提交更改
        conn.commit()
        print("\n🎉 数据库迁移完成！")
        
        # 显示迁移后的表结构
        print("\n当前 projects 表结构：")
        cursor.execute("PRAGMA table_info(projects)")
        for col in cursor.fetchall():
            print(f"  - {col[1]}: {col[2]}")
        
        # 显示项目统计
        cursor.execute("""
            SELECT project_source, COUNT(*) as count 
            FROM projects 
            GROUP BY project_source
        """)
        print("\n项目来源统计：")
        for row in cursor.fetchall():
            source = row[0] or '未设置'
            count = row[1]
            source_name = {
                'horizontal': '横向',
                'vertical': '纵向', 
                'self_developed': '自研'
            }.get(source, source)
            print(f"  - {source_name}: {count}个")
            
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()



