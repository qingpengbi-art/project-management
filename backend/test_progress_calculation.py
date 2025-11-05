#!/usr/bin/env python3
"""
测试项目进度计算
"""

if __name__ == '__main__':
    import sys
    import os
    
    # 设置路径
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    
    # 导入并创建 app
    from app import create_app
    app = create_app()
    
    # 在 app context 中运行测试
    with app.app_context():
        from models.database import db, Project
        from services.project_service import ProjectService
        
        # 查找电池仓项目
        project = Project.query.filter(Project.name.like('%电池仓%')).first()
        
        if not project:
            print("❌ 未找到电池仓项目")
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"项目信息: {project.name}")
        print(f"{'='*60}")
        print(f"项目状态: {project.status.value}")
        print(f"数据库中的进度: {project.progress}%")
        print(f"手动进度: {project.manual_progress}")
        print(f"项目来源: {project.project_source}")
        
        print(f"\n模块信息:")
        if project.modules:
            for module in project.modules:
                print(f"  - {module.name}: {module.progress}%")
        else:
            print("  （无模块）")
        
        # 使用新的计算逻辑
        print(f"\n{'='*60}")
        print("使用新的进度计算逻辑:")
        print(f"{'='*60}")
        
        progress_info = ProjectService.calculate_project_progress(project)
        
        print(f"\n✅ 计算结果:")
        print(f"  进度: {progress_info['progress']}%")
        print(f"  类型: {progress_info['type']}")
        print(f"  来源: {progress_info['source']}")
        print(f"  说明: {progress_info['info']}")
        if 'detail' in progress_info:
            print(f"  详情: {progress_info['detail']}")
        
        # 获取进度限制
        limits = ProjectService.get_progress_limits(project.status.value)
        print(f"\n📊 进度范围限制:")
        print(f"  最小: {limits['min']}%")
        print(f"  最大: {limits['max']}%")
        print(f"  默认: {limits['default']}%")
        print(f"  阶段: {limits['stage']}/{7 if project.project_source == 'horizontal' else 4}")
        print(f"  标签: {limits['label']}")
        
        print(f"\n{'='*60}")
        print(f"Dashboard 应该显示: {progress_info['progress']}%")
        print(f"{'='*60}\n")
