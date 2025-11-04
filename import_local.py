#!/usr/bin/env python3
"""
本地数据导入脚本 - 从 database_export.json 导入数据到本地数据库
"""

import json
import os
import sys

# 切换到 backend 目录
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'

from datetime import datetime
from app import create_app
from models.database import db, User, Project, ProjectModule, ModuleAssignment, ModuleWorkRecord, ProjectMember, UserRole, ProjectStatus, ModuleStatus, ProjectMemberRole

def import_data():
    """导入数据"""
    print("="*60)
    print("本地数据导入")
    print("="*60)
    
    # 检查数据文件
    export_file = '../database_export.json'
    if not os.path.exists(export_file):
        print(f"❌ 找不到数据文件: {export_file}")
        return False
    
    # 创建应用
    app = create_app()
    
    with app.app_context():
        print("\n📖 读取数据文件...")
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 将导入：{len(data['users'])}用户, {len(data['projects'])}项目, {len(data['modules'])}模块")
        
        # 确认
        print("\n⚠️  警告：这将清空现有数据！")
        confirm = input("确认导入？(yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 已取消")
            return False
        
        try:
            # 清空现有数据
            print("\n🗑️  清空现有数据...")
            db.session.execute(db.delete(ModuleWorkRecord))
            db.session.execute(db.delete(ModuleAssignment))
            db.session.execute(db.delete(ProjectMember))
            db.session.execute(db.delete(ProjectModule))
            db.session.execute(db.delete(Project))
            db.session.execute(db.delete(User))
            db.session.commit()
            print("   ✅ 数据清空完成")
            
            # 导入用户
            print("\n👥 导入用户...")
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
            print("\n📁 导入项目...")
            for project_data in data['projects']:
                # 处理金额字段（兼容新旧字段名）
                contract_amount = project_data.get('contract_amount') or project_data.get('amount')
                received_amount = project_data.get('received_amount')
                
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
                    contract_amount=contract_amount,
                    received_amount=received_amount,
                    created_at=datetime.fromisoformat(project_data['created_at']) if project_data['created_at'] else None
                )
                db.session.add(project)
            db.session.commit()
            print(f"   ✅ {len(data['projects'])} 个项目")
            
            # 导入项目成员
            print("\n👤 导入项目成员...")
            for member_data in data['project_members']:
                member = ProjectMember(
                    id=member_data['id'],
                    project_id=member_data['project_id'],
                    user_id=member_data['user_id'],
                    role=ProjectMemberRole(member_data['role']) if member_data['role'] else ProjectMemberRole.MEMBER
                )
                db.session.add(member)
            db.session.commit()
            print(f"   ✅ {len(data['project_members'])} 条项目成员记录")
            
            # 导入模块
            print("\n📦 导入模块...")
            for module_data in data['modules']:
                module = ProjectModule(
                    id=module_data['id'],
                    project_id=module_data['project_id'],
                    name=module_data['name'],
                    description=module_data['description'],
                    status=ModuleStatus(module_data['status']) if module_data['status'] else ModuleStatus.NOT_STARTED,
                    progress=module_data['progress'],
                    start_date=datetime.fromisoformat(module_data['start_date']).date() if module_data['start_date'] else None,
                    end_date=datetime.fromisoformat(module_data['end_date']).date() if module_data['end_date'] else None,
                    created_at=datetime.fromisoformat(module_data['created_at']) if module_data['created_at'] else None
                )
                db.session.add(module)
            db.session.commit()
            print(f"   ✅ {len(data['modules'])} 个模块")
            
            # 导入模块分配
            print("\n🔗 导入模块分配...")
            for assignment_data in data['module_assignments']:
                assignment = ModuleAssignment(
                    id=assignment_data['id'],
                    module_id=assignment_data['module_id'],
                    user_id=assignment_data['user_id'],
                    assigned_at=datetime.fromisoformat(assignment_data['assigned_at']) if assignment_data['assigned_at'] else None
                )
                db.session.add(assignment)
            db.session.commit()
            print(f"   ✅ {len(data['module_assignments'])} 条模块分配记录")
            
            # 导入工作记录
            print("\n📝 导入工作记录...")
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
            
            print("\n" + "="*60)
            print("🎉 数据导入完成！")
            print("="*60)
            
            # 验证数据
            print("\n📊 数据验证:")
            print(f"   用户数: {User.query.count()}")
            print(f"   项目数: {Project.query.count()}")
            print(f"   模块数: {ProjectModule.query.count()}")
            print(f"   模块分配: {ModuleAssignment.query.count()}")
            print(f"   工作记录: {ModuleWorkRecord.query.count()}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 导入失败: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    import_data()

