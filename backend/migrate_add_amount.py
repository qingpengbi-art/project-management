"""
数据库迁移脚本 - 添加项目金额字段
为projects表添加amount字段（金额，非必填）
"""

import sqlite3
import os

def migrate():
    """执行迁移"""
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'project_management.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查amount字段是否已存在
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'amount' in columns:
            print("amount字段已存在，无需迁移")
            return True
        
        # 添加amount字段（REAL类型，允许NULL）
        print("开始添加amount字段...")
        cursor.execute("""
            ALTER TABLE projects 
            ADD COLUMN amount REAL
        """)
        
        conn.commit()
        print("✓ 成功添加amount字段到projects表")
        
        # 验证字段已添加
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'amount' in columns:
            print("✓ 验证通过：amount字段已成功添加")
            return True
        else:
            print("✗ 验证失败：amount字段未添加成功")
            return False
            
    except Exception as e:
        print(f"✗ 迁移失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("项目金额字段迁移脚本")
    print("=" * 50)
    
    success = migrate()
    
    if success:
        print("\n✓ 迁移成功完成！")
    else:
        print("\n✗ 迁移失败，请检查错误信息")


