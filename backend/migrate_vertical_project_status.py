"""
纵向项目状态迁移脚本
将现有纵向项目的旧状态映射到新的纵向专用状态
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import db, Project, ProjectStatus
from backend.app import create_app

# 状态映射关系
STATUS_MIGRATION_MAP = {
    ProjectStatus.INITIAL_CONTACT: ProjectStatus.VERTICAL_DECLARATION,       # 初步接触 → 申报阶段
    ProjectStatus.PROPOSAL_SUBMITTED: ProjectStatus.VERTICAL_DECLARATION,    # 提交方案 → 申报阶段
    ProjectStatus.QUOTATION_SUBMITTED: ProjectStatus.VERTICAL_REVIEW,        # 提交报价 → 审核阶段
    ProjectStatus.USER_CONFIRMATION: ProjectStatus.VERTICAL_REVIEW,          # 用户确认 → 审核阶段
    ProjectStatus.CONTRACT_SIGNED: ProjectStatus.VERTICAL_APPROVED,          # 合同签订 → 审核通过
    ProjectStatus.PROJECT_IMPLEMENTATION: ProjectStatus.VERTICAL_APPROVED,   # 项目实施 → 审核通过
    ProjectStatus.PROJECT_ACCEPTANCE: ProjectStatus.VERTICAL_APPROVED,       # 项目验收 → 审核通过
    ProjectStatus.WARRANTY_PERIOD: ProjectStatus.VERTICAL_APPROVED,          # 维保期内 → 审核通过
    ProjectStatus.POST_WARRANTY: ProjectStatus.VERTICAL_APPROVED,            # 维保期外 → 审核通过
    ProjectStatus.NO_FOLLOW_UP: ProjectStatus.VERTICAL_REJECTED,             # 不再跟进 → 审核未通过
}

def migrate_vertical_projects():
    """迁移纵向项目状态"""
    print("=" * 60)
    print("纵向项目状态迁移工具")
    print("=" * 60)
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 查询所有纵向项目
        vertical_projects = Project.query.filter_by(project_source='vertical').all()
        
        if not vertical_projects:
            print("✅ 未找到纵向项目，无需迁移")
            return
        
        print(f"\n📊 找到 {len(vertical_projects)} 个纵向项目")
        print("\n当前状态统计:")
        
        # 统计当前状态
        status_count = {}
        for project in vertical_projects:
            status = project.status
            status_count[status] = status_count.get(status, 0) + 1
        
        for status, count in status_count.items():
            print(f"  - {status.value}: {count} 个")
        
        print("\n" + "-" * 60)
        print("迁移映射关系:")
        print("-" * 60)
        for old_status, new_status in STATUS_MIGRATION_MAP.items():
            print(f"  {old_status.value:30} → {new_status.value}")
        
        print("\n" + "-" * 60)
        print("开始迁移...\n")
        
        updated_count = 0
        skipped_count = 0
        
        for project in vertical_projects:
            old_status = project.status
            
            # 如果已经是新状态，跳过
            if old_status.value.startswith('vertical_'):
                print(f"⏭️  项目 #{project.id} [{project.name}] 已是新状态: {old_status.value}")
                skipped_count += 1
                continue
            
            # 根据映射表更新状态
            if old_status in STATUS_MIGRATION_MAP:
                new_status = STATUS_MIGRATION_MAP[old_status]
                project.status = new_status
                project.progress = 0  # 确保纵向项目进度为0
                
                print(f"✅ 项目 #{project.id} [{project.name}]")
                print(f"   状态: {old_status.value} → {new_status.value}")
                print(f"   进度: {project.progress}%")
                
                updated_count += 1
            else:
                print(f"⚠️  项目 #{project.id} [{project.name}] 状态未知: {old_status.value}")
                skipped_count += 1
        
        # 提交更改
        if updated_count > 0:
            try:
                db.session.commit()
                print("\n" + "=" * 60)
                print(f"✅ 迁移完成！")
                print(f"   - 更新: {updated_count} 个项目")
                print(f"   - 跳过: {skipped_count} 个项目")
                print("=" * 60)
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ 迁移失败: {str(e)}")
                raise
        else:
            print("\n" + "=" * 60)
            print("ℹ️  无需更新")
            print(f"   - 跳过: {skipped_count} 个项目")
            print("=" * 60)
        
        # 显示迁移后的状态统计
        print("\n迁移后状态统计:")
        vertical_projects = Project.query.filter_by(project_source='vertical').all()
        status_count_after = {}
        for project in vertical_projects:
            status = project.status
            status_count_after[status] = status_count_after.get(status, 0) + 1
        
        for status, count in status_count_after.items():
            print(f"  - {status.value}: {count} 个")

if __name__ == '__main__':
    try:
        migrate_vertical_projects()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消迁移")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 迁移过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

