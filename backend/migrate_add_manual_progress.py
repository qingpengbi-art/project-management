#!/usr/bin/env python3
"""
数据库迁移脚本：添加 manual_progress 字段
用于存储用户手动设置的进度（仅前期阶段有效）
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import db, Project
from sqlalchemy import text

def migrate():
    """添加 manual_progress 字段"""
    try:
        # 检查字段是否已存在
        result = db.session.execute(text("PRAGMA table_info(projects)"))
        columns = [row[1] for row in result]
        
        if 'manual_progress' in columns:
            print("✅ manual_progress 字段已存在，无需添加")
            return
        
        print("开始添加 manual_progress 字段...")
        
        # 添加字段
        db.session.execute(text(
            "ALTER TABLE projects ADD COLUMN manual_progress INTEGER DEFAULT NULL"
        ))
        
        db.session.commit()
        
        print("✅ 成功添加 manual_progress 字段")
        print("\n字段说明：")
        print("- manual_progress: 用户手动设置的进度")
        print("- NULL: 表示未手动设置，使用系统默认进度")
        print("- 仅在前期阶段（初步接触→合同签订）有效")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 迁移失败: {str(e)}")
        raise

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        migrate()

