"""
自动数据库迁移脚本：将模块负责人转为成员（无需确认）
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import db, ProjectModule, ModuleAssignment, User
from backend.app import create_app

def migrate_module_members():
    """将模块负责人迁移为成员"""
    
    print("=" * 60)
    print("开始迁移模块成员数据...")
    print("=" * 60)
    
    try:
        # 获取所有模块
        modules = ProjectModule.query.all()
        print(f"\n📊 找到 {len(modules)} 个模块")
        
        migrated_count = 0
        skipped_count = 0
        
        for module in modules:
            print(f"\n处理模块: {module.name} (ID: {module.id})")
            
            # 检查是否有负责人
            if not module.assigned_to_id:
                print(f"  ⚠️  模块没有负责人，跳过")
                skipped_count += 1
                continue
            
            # 检查负责人是否存在
            user = User.query.get(module.assigned_to_id)
            if not user:
                print(f"  ❌ 负责人(ID: {module.assigned_to_id})不存在，跳过")
                skipped_count += 1
                continue
            
            # 检查是否已经有成员记录
            existing_assignment = ModuleAssignment.query.filter_by(
                module_id=module.id,
                user_id=module.assigned_to_id
            ).first()
            
            if existing_assignment:
                print(f"  ℹ️  {user.name} 已经是成员，更新角色为member")
                existing_assignment.role = 'member'
                skipped_count += 1
            else:
                # 创建新的成员记录
                new_assignment = ModuleAssignment(
                    module_id=module.id,
                    user_id=module.assigned_to_id,
                    role='member'  # 统一设置为member
                )
                db.session.add(new_assignment)
                print(f"  ✅ 已将 {user.name} 添加为成员")
                migrated_count += 1
        
        # 提交更改
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ 迁移完成！")
        print(f"📊 统计信息:")
        print(f"   - 总模块数: {len(modules)}")
        print(f"   - 新增成员: {migrated_count}")
        print(f"   - 已存在/跳过: {skipped_count}")
        print("=" * 60)
        
        # 验证
        print("\n验证迁移结果...")
        total_assignments = ModuleAssignment.query.count()
        member_count = ModuleAssignment.query.filter_by(role='member').count()
        leader_count = ModuleAssignment.query.filter_by(role='leader').count()
        
        print(f"\n📊 总成员记录数: {total_assignments}")
        print(f"   - member角色: {member_count}")
        print(f"   - leader角色: {leader_count}")
        
        if leader_count > 0:
            print(f"\n⚠️  警告: 仍有 {leader_count} 个leader角色")
        else:
            print(f"\n✅ 所有角色已统一为member")
        
        print("=" * 60)
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        print("\n模块成员自动迁移脚本")
        print("=" * 60)
        migrate_module_members()

