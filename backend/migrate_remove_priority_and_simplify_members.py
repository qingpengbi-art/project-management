"""
数据库迁移脚本：移除优先级字段，简化成员角色
1. 将现有的模块负责人(assigned_to_id)转为成员记录
2. 保留优先级字段但在UI中不显示（保持向后兼容）
3. 确保所有模块的assigned_to_id都有对应的成员记录
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
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def verify_migration():
    """验证迁移结果"""
    
    print("\n" + "=" * 60)
    print("验证迁移结果...")
    print("=" * 60)
    
    try:
        modules = ProjectModule.query.all()
        
        for module in modules:
            if module.assigned_to_id:
                # 检查是否有对应的成员记录
                assignment = ModuleAssignment.query.filter_by(
                    module_id=module.id,
                    user_id=module.assigned_to_id
                ).first()
                
                if assignment:
                    print(f"✅ 模块 '{module.name}' - 负责人已转为成员 ({assignment.role})")
                else:
                    print(f"⚠️  模块 '{module.name}' - 负责人未转为成员")
        
        # 统计所有成员记录
        total_assignments = ModuleAssignment.query.count()
        print(f"\n📊 总成员记录数: {total_assignments}")
        
        # 按角色统计
        member_count = ModuleAssignment.query.filter_by(role='member').count()
        leader_count = ModuleAssignment.query.filter_by(role='leader').count()
        
        print(f"   - member角色: {member_count}")
        print(f"   - leader角色: {leader_count} (应该全部转为member)")
        
        if leader_count > 0:
            print("\n⚠️  警告: 仍有leader角色存在，建议手动检查")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("模块成员迁移脚本")
        print("=" * 60)
        print("\n此脚本将:")
        print("1. 将所有模块的负责人(assigned_to_id)添加为成员")
        print("2. 统一设置角色为'member'")
        print("3. 保留assigned_to_id字段以保持向后兼容")
        print("\n⚠️  注意: 此操作不会删除任何数据")
        
        response = input("\n是否继续? (y/n): ")
        
        if response.lower() == 'y':
            success = migrate_module_members()
            
            if success:
                verify_migration()
                print("\n✅ 所有操作已完成！")
            else:
                print("\n❌ 迁移失败，请检查错误信息")
        else:
            print("\n❌ 已取消迁移")

