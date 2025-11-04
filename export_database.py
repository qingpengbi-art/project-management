"""
导出数据库数据为 JSON 格式
用于同步本地数据到 Render
"""
import json
import sys
sys.path.insert(0, './backend')

from backend.models.database import db, User, Project, ProjectModule, ModuleAssignment, ModuleWorkRecord, ProjectMember
from backend.app import create_app

def export_data():
    """导出所有数据"""
    app = create_app()
    
    with app.app_context():
        data = {
            'users': [],
            'projects': [],
            'project_members': [],
            'modules': [],
            'module_assignments': [],
            'work_records': []
        }
        
        print("="*60)
        print("📤 开始导出数据库数据...")
        print("="*60)
        
        # 导出用户
        print("\n👥 导出用户...")
        users = User.query.all()
        for user in users:
            data['users'].append({
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'password_hash': user.password_hash,  # 直接导出加密后的密码
                'email': user.email,
                'position': user.position,
                'role': user.role.value if user.role else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        print(f"   ✅ 导出 {len(data['users'])} 个用户")
        
        # 导出项目
        print("\n📁 导出项目...")
        projects = Project.query.all()
        for project in projects:
            data['projects'].append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'status': project.status.value if project.status else None,
                'progress': project.progress,
                'project_source': project.project_source,
                'partner': project.partner,
                'contract_amount': project.contract_amount,
                'received_amount': project.received_amount,
                'created_at': project.created_at.isoformat() if project.created_at else None
            })
        print(f"   ✅ 导出 {len(data['projects'])} 个项目")
        
        # 导出项目成员
        print("\n👤 导出项目成员...")
        members = ProjectMember.query.all()
        for member in members:
            data['project_members'].append({
                'id': member.id,
                'project_id': member.project_id,
                'user_id': member.user_id,
                'role': member.role.value if member.role else None,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None
            })
        print(f"   ✅ 导出 {len(data['project_members'])} 条项目成员记录")
        
        # 导出模块
        print("\n📦 导出模块...")
        modules = ProjectModule.query.all()
        for module in modules:
            data['modules'].append({
                'id': module.id,
                'project_id': module.project_id,
                'name': module.name,
                'description': module.description,
                'assigned_to_id': module.assigned_to_id,
                'progress': module.progress,
                'start_date': module.start_date.isoformat() if module.start_date else None,
                'end_date': module.end_date.isoformat() if module.end_date else None,
                'status': module.status.value if module.status else None,
                'created_at': module.created_at.isoformat() if module.created_at else None
            })
        print(f"   ✅ 导出 {len(data['modules'])} 个模块")
        
        # 导出模块分配
        print("\n🔗 导出模块分配...")
        assignments = ModuleAssignment.query.all()
        for assignment in assignments:
            data['module_assignments'].append({
                'id': assignment.id,
                'module_id': assignment.module_id,
                'user_id': assignment.user_id,
                'role': assignment.role,
                'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None
            })
        print(f"   ✅ 导出 {len(data['module_assignments'])} 条模块分配记录")
        
        # 导出工作记录
        print("\n📝 导出工作记录...")
        records = ModuleWorkRecord.query.all()
        for record in records:
            data['work_records'].append({
                'id': record.id,
                'module_id': record.module_id,
                'week_start': record.week_start.isoformat() if record.week_start else None,
                'week_end': record.week_end.isoformat() if record.week_end else None,
                'work_content': record.work_content,
                'achievements': record.achievements,
                'issues': record.issues,
                'next_week_plan': record.next_week_plan,
                'created_by_id': record.created_by_id,
                'created_at': record.created_at.isoformat() if record.created_at else None
            })
        print(f"   ✅ 导出 {len(data['work_records'])} 条工作记录")
        
        # 保存为 JSON 文件
        print("\n💾 保存数据文件...")
        with open('database_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print("🎉 数据导出完成！")
        print("="*60)
        print(f"\n📁 文件位置：database_export.json")
        print(f"📊 数据统计：")
        print(f"   - 用户：{len(data['users'])}")
        print(f"   - 项目：{len(data['projects'])}")
        print(f"   - 项目成员：{len(data['project_members'])}")
        print(f"   - 模块：{len(data['modules'])}")
        print(f"   - 模块分配：{len(data['module_assignments'])}")
        print(f"   - 工作记录：{len(data['work_records'])}")
        print("\n💡 下一步：")
        print("   1. 将 database_export.json 提交到 Git")
        print("   2. 推送到 GitHub")
        print("   3. 在 Render Shell 中运行：python3 import_database.py")
        print("="*60)
        
        return data

if __name__ == '__main__':
    try:
        export_data()
    except Exception as e:
        print(f"\n❌ 导出失败：{str(e)}")
        import traceback
        traceback.print_exc()

