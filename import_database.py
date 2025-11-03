"""
从 JSON 文件导入数据到数据库
警告：这会清空现有数据！仅在 Render 上使用
"""
import json
import sys
import os
from datetime import datetime
sys.path.insert(0, './backend')

from backend.models.database import (
    db, User, Project, ProjectModule, ModuleAssignment, 
    ModuleWorkRecord, ProjectMember, UserRole, ProjectStatus, 
    ModuleStatus, ProjectMemberRole
)
from backend.app import create_app

def import_data(json_file='database_export.json'):
    """从 JSON 文件导入数据"""
    
    # 安全检查：只允许在生产环境（Render）上运行
    if os.getenv('FLASK_ENV') != 'production':
        print("❌ 错误：此脚本只能在生产环境运行！")
        print("   为了安全，请在本地使用正常的数据库管理方式")
        return
    
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("📥 数据库导入工具")
        print("="*60)
        
        # 读取 JSON 文件
        print("\n📖 读取数据文件...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   ✅ 成功读取 {json_file}")
        except FileNotFoundError:
            print(f"   ❌ 错误：找不到文件 {json_file}")
            return
        except json.JSONDecodeError:
            print(f"   ❌ 错误：JSON 文件格式错误")
            return
        
        # 显示数据统计
        print("\n📊 将要导入的数据：")
        print(f"   - 用户：{len(data['users'])}")
        print(f"   - 项目：{len(data['projects'])}")
        print(f"   - 项目成员：{len(data['project_members'])}")
        print(f"   - 模块：{len(data['modules'])}")
        print(f"   - 模块分配：{len(data['module_assignments'])}")
        print(f"   - 工作记录：{len(data['work_records'])}")
        
        # 确认操作
        print("\n" + "⚠️ "*20)
        print("⚠️  警告：此操作将清空现有数据库并导入新数据！")
        print("⚠️  所有现有数据将被永久删除！")
        print("⚠️ "*20)
        
        response = input("\n确认继续？输入 'yes' 继续，其他任何输入取消: ")
        if response.lower() != 'yes':
            print("\n❌ 操作已取消")
            return
        
        try:
            # 备份提示
            print("\n💡 建议：在继续之前，确保已备份当前数据库")
            backup = input("   已备份？输入 'yes' 继续: ")
            if backup.lower() != 'yes':
                print("\n❌ 操作已取消。请先备份数据！")
                return
            
            # 清空现有数据（按照外键依赖顺序）
            print("\n🗑️  清空现有数据...")
            ModuleWorkRecord.query.delete()
            print("   ✅ 清空工作记录")
            ModuleAssignment.query.delete()
            print("   ✅ 清空模块分配")
            ProjectModule.query.delete()
            print("   ✅ 清空模块")
            ProjectMember.query.delete()
            print("   ✅ 清空项目成员")
            Project.query.delete()
            print("   ✅ 清空项目")
            User.query.delete()
            print("   ✅ 清空用户")
            db.session.commit()
            print("   ✅ 现有数据已清空")
            
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
                user.password_hash = user_data['password_hash']  # 直接设置加密后的密码
                db.session.add(user)
            db.session.commit()
            print(f"   ✅ 成功导入 {len(data['users'])} 个用户")
            
            # 导入项目
            print("\n📁 导入项目...")
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
            print(f"   ✅ 成功导入 {len(data['projects'])} 个项目")
            
            # 导入项目成员
            print("\n👤 导入项目成员...")
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
            print(f"   ✅ 成功导入 {len(data['project_members'])} 条项目成员记录")
            
            # 导入模块
            print("\n📦 导入模块...")
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
            print(f"   ✅ 成功导入 {len(data['modules'])} 个模块")
            
            # 导入模块分配
            print("\n🔗 导入模块分配...")
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
            print(f"   ✅ 成功导入 {len(data['module_assignments'])} 条模块分配记录")
            
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
            print(f"   ✅ 成功导入 {len(data['work_records'])} 条工作记录")
            
            print("\n" + "="*60)
            print("🎉 数据导入完成！")
            print("="*60)
            print("\n📊 最终统计：")
            print(f"   - 用户：{User.query.count()}")
            print(f"   - 项目：{Project.query.count()}")
            print(f"   - 项目成员：{ProjectMember.query.count()}")
            print(f"   - 模块：{ProjectModule.query.count()}")
            print(f"   - 模块分配：{ModuleAssignment.query.count()}")
            print(f"   - 工作记录：{ModuleWorkRecord.query.count()}")
            print("\n💡 建议：访问应用验证数据是否正确导入")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 导入过程中出错：{str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            print("\n💡 数据库已回滚，没有任何更改")

if __name__ == '__main__':
    import_data()

