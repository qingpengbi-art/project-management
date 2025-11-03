#!/bin/bash
# 智能启动脚本 - 检查并导入数据

set -e

echo "🚀 启动项目管理系统..."

# 数据库路径
DB_PATH="${DATABASE_PATH:-/app/data/project_management.db}"
EXPORT_FILE="/app/database_export.json"
IMPORT_FLAG="/app/data/.data_imported"

# 检查是否有导出文件且未导入过
if [ -f "$EXPORT_FILE" ] && [ ! -f "$IMPORT_FLAG" ]; then
    echo "📥 检测到数据导出文件，准备导入..."
    
    # 如果数据库已存在，先删除（这是默认/空数据库）
    if [ -f "$DB_PATH" ]; then
        echo "🗑️  删除旧数据库，准备导入新数据..."
        rm -f "$DB_PATH"
    fi
fi

# 检查数据库是否存在
if [ ! -f "$DB_PATH" ]; then
    echo "📊 初始化数据库..."
    
    # 检查是否有导出的数据文件
    if [ -f "$EXPORT_FILE" ] && [ ! -f "$IMPORT_FLAG" ]; then
        echo "📥 发现数据导出文件，自动导入数据..."
        
        # 设置环境变量确保导入脚本可以运行
        export FLASK_ENV=production
        
        # 创建临时导入脚本（自动确认）
        cat > /tmp/auto_import.py << 'PYTHON_SCRIPT'
import json
import sys
import os
from datetime import datetime

# 添加正确的路径
sys.path.insert(0, '/app')
os.chdir('/app')

from backend.models.database import (
    db, User, Project, ProjectModule, ModuleAssignment, 
    ModuleWorkRecord, ProjectMember, UserRole, ProjectStatus, 
    ModuleStatus, ProjectMemberRole
)
from backend.app import create_app

def auto_import_data():
    """自动导入数据（无需确认）"""
    app = create_app()
    
    with app.app_context():
        print("📖 读取数据文件...")
        with open('/app/database_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 将导入：{len(data['users'])}用户, {len(data['projects'])}项目, {len(data['modules'])}模块")
        
        try:
            # 导入用户
            print("👥 导入用户...")
            for user_data in data['users']:
                user = User(
                    id=user_data['id'],
                    name=user_data['name'],
                    username=user_data['username'],
                    email=user_data['email'],
                    position=user_data['position'],
                    role=UserRole(user_data['role']) if user_data['role'] else UserRole.MEMBER,
                    created_at=datetime.fromisoformat(user_data['created_at']) if user_data['created_at'] else None
                )
                user.password_hash = user_data['password_hash']
                db.session.add(user)
            db.session.commit()
            print(f"   ✅ {len(data['users'])} 个用户")
            
            # 导入项目
            print("📁 导入项目...")
            for project_data in data['projects']:
                project = Project(
                    id=project_data['id'],
                    name=project_data['name'],
                    description=project_data['description'],
                    start_date=datetime.fromisoformat(project_data['start_date']).date() if project_data['start_date'] else None,
                    end_date=datetime.fromisoformat(project_data['end_date']).date() if project_data['end_date'] else None,
                    status=ProjectStatus(project_data['status']) if project_data['status'] else ProjectStatus.INITIAL_CONTACT,
                    progress=project_data['progress'],
                    project_source=project_data['project_source'],
                    partner=project_data['partner'],
                    amount=project_data['amount'],
                    created_at=datetime.fromisoformat(project_data['created_at']) if project_data['created_at'] else None
                )
                db.session.add(project)
            db.session.commit()
            print(f"   ✅ {len(data['projects'])} 个项目")
            
            # 导入项目成员
            print("👤 导入项目成员...")
            for member_data in data['project_members']:
                member = ProjectMember(
                    id=member_data['id'],
                    project_id=member_data['project_id'],
                    user_id=member_data['user_id'],
                    role=ProjectMemberRole(member_data['role']) if member_data['role'] else ProjectMemberRole.MEMBER,
                    joined_at=datetime.fromisoformat(member_data['joined_at']) if member_data['joined_at'] else None
                )
                db.session.add(member)
            db.session.commit()
            print(f"   ✅ {len(data['project_members'])} 条项目成员记录")
            
            # 导入模块
            print("📦 导入模块...")
            for module_data in data['modules']:
                module = ProjectModule(
                    id=module_data['id'],
                    project_id=module_data['project_id'],
                    name=module_data['name'],
                    description=module_data['description'],
                    assigned_to_id=module_data['assigned_to_id'],
                    progress=module_data['progress'],
                    start_date=datetime.fromisoformat(module_data['start_date']).date() if module_data['start_date'] else None,
                    end_date=datetime.fromisoformat(module_data['end_date']).date() if module_data['end_date'] else None,
                    status=ModuleStatus(module_data['status']) if module_data['status'] else ModuleStatus.NOT_STARTED,
                    created_at=datetime.fromisoformat(module_data['created_at']) if module_data['created_at'] else None
                )
                db.session.add(module)
            db.session.commit()
            print(f"   ✅ {len(data['modules'])} 个模块")
            
            # 导入模块分配
            print("🔗 导入模块分配...")
            for assignment_data in data['module_assignments']:
                assignment = ModuleAssignment(
                    id=assignment_data['id'],
                    module_id=assignment_data['module_id'],
                    user_id=assignment_data['user_id'],
                    role=assignment_data['role'],
                    assigned_at=datetime.fromisoformat(assignment_data['assigned_at']) if assignment_data['assigned_at'] else None
                )
                db.session.add(assignment)
            db.session.commit()
            print(f"   ✅ {len(data['module_assignments'])} 条模块分配记录")
            
            # 导入工作记录
            print("📝 导入工作记录...")
            for record_data in data['work_records']:
                record = ModuleWorkRecord(
                    id=record_data['id'],
                    module_id=record_data['module_id'],
                    week_start=datetime.fromisoformat(record_data['week_start']).date() if record_data['week_start'] else None,
                    week_end=datetime.fromisoformat(record_data['week_end']).date() if record_data['week_end'] else None,
                    work_content=record_data['work_content'],
                    achievements=record_data['achievements'],
                    issues=record_data['issues'],
                    next_week_plan=record_data['next_week_plan'],
                    created_by_id=record_data['created_by_id'],
                    created_at=datetime.fromisoformat(record_data['created_at']) if record_data['created_at'] else None
                )
                db.session.add(record)
            db.session.commit()
            print(f"   ✅ {len(data['work_records'])} 条工作记录")
            
            print("🎉 数据导入完成！")
            
        except Exception as e:
            print(f"❌ 导入出错：{str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    auto_import_data()
PYTHON_SCRIPT
        
        # 执行自动导入
        python3 /tmp/auto_import.py
        
        if [ $? -eq 0 ]; then
            echo "✅ 数据导入成功！"
            # 创建导入标记文件，避免重复导入
            touch "$IMPORT_FLAG"
            echo "📝 已创建导入标记，下次启动将跳过导入"
        else
            echo "⚠️ 数据导入失败，使用默认数据"
        fi
    else
        echo "📊 使用默认数据初始化..."
    fi
else
    echo "✅ 数据库已存在，跳过初始化"
fi

# 启动应用
echo "🌐 启动 Web 服务..."
cd /app/backend
exec gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 4 --timeout 120 app:app

