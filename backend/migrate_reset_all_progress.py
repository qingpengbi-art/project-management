#!/usr/bin/env python3
"""
数据库迁移脚本：重置所有项目进度
- 清空所有手动进度
- 根据新逻辑重新计算所有项目进度
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import db, Project, ProjectModule
from services.project_service import ProjectService

def reset_all_project_progress():
    """重置所有项目进度"""
    try:
        projects = Project.query.all()
        
        print(f"\n{'='*70}")
        print(f"开始重置 {len(projects)} 个项目的进度...")
        print(f"{'='*70}\n")
        
        success_count = 0
        error_count = 0
        
        for i, project in enumerate(projects, 1):
            try:
                # 获取旧值
                old_manual = getattr(project, 'manual_progress', None)
                old_progress = project.progress
                
                # 清空手动进度
                project.manual_progress = None
                
                # 重新计算进度
                progress_info = ProjectService.calculate_project_progress(project)
                new_progress = progress_info['progress']
                project.progress = new_progress
                
                # 获取模块信息
                modules = ProjectModule.query.filter_by(project_id=project.id).all()
                module_count = len(modules)
                
                print(f"[{i}/{len(projects)}] {project.name}")
                print(f"  状态: {project.status.value}")
                print(f"  类型: {project.project_source}")
                print(f"  旧进度: {old_progress}% (手动: {old_manual if old_manual is not None else '无'})")
                print(f"  新进度: {new_progress}%")
                print(f"  来源: {progress_info.get('source', '未知')}")
                print(f"  模块数: {module_count}")
                if progress_info.get('info'):
                    print(f"  说明: {progress_info['info']}")
                print(f"{'-'*70}\n")
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ 项目 {project.name} 重置失败: {str(e)}\n")
                error_count += 1
                continue
        
        # 提交所有更改
        db.session.commit()
        
        print(f"\n{'='*70}")
        print(f"✅ 重置完成！")
        print(f"  成功: {success_count} 个项目")
        print(f"  失败: {error_count} 个项目")
        print(f"{'='*70}\n")
        
        # 统计信息
        print("进度来源统计：")
        from sqlalchemy import func
        
        # 按状态统计
        status_stats = db.session.query(
            Project.status,
            func.count(Project.id)
        ).group_by(Project.status).all()
        
        print("\n按状态分布：")
        for status, count in status_stats:
            print(f"  {status.value}: {count} 个")
        
        # 按项目类型统计
        source_stats = db.session.query(
            Project.project_source,
            func.count(Project.id)
        ).group_by(Project.project_source).all()
        
        print("\n按类型分布：")
        for source, count in source_stats:
            print(f"  {source}: {count} 个")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 重置失败: {str(e)}")
        raise

if __name__ == '__main__':
    from app import app
    
    print("\n" + "="*70)
    print("项目进度重置脚本")
    print("="*70)
    print("\n⚠️  警告：此操作将：")
    print("  1. 清空所有项目的手动进度")
    print("  2. 根据新逻辑重新计算所有项目进度")
    print("\n是否继续？(输入 yes 继续)")
    
    confirm = input("\n> ").strip().lower()
    
    if confirm != 'yes':
        print("\n已取消操作")
        sys.exit(0)
    
    with app.app_context():
        reset_all_project_progress()

