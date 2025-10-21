"""
Flask应用主文件
项目推进表管理系统后端服务
"""

import os
from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import init_database
from backend.controllers.project_controller import project_bp
from backend.controllers.user_controller import user_bp
from backend.controllers.module_controller import module_bp
from backend.controllers.auth_controller import auth_bp

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置应用 - 支持环境变量配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # 数据库配置 - 支持Docker环境
    if os.environ.get('DATABASE_PATH'):
        # Docker环境
        db_path = os.environ.get('DATABASE_PATH')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    else:
        # 本地开发环境
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'backend', 'project_management.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print(f"📊 数据库路径: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # 启用CORS支持 - 在Docker环境中允许所有来源
    is_docker = os.environ.get('DATABASE_PATH') is not None
    
    if is_docker:
        # Docker环境 - 允许所有来源（生产环境建议配置具体域名）
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Authorization"]
            }
        })
        print("🌐 CORS配置: 允许所有来源访问（Docker模式）")
    else:
        # 本地开发环境
        CORS(app, resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000", 
                    "http://127.0.0.1:3000",
                    "http://192.168.2.70:3000",   # 局域网访问
                    "http://localhost:3001",      # 静态文件服务器
                    "http://192.168.2.70:3001"    # 局域网静态文件服务器
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Authorization"]
            }
        })
        print("🌐 CORS配置: 本地开发模式")
    
    # 初始化数据库
    init_database(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(module_bp)
    
    # API根路由（仅在非Docker环境或API请求时返回）
    @app.route('/api')
    def api_index():
        """API信息"""
        return jsonify({
            'success': True,
            'message': '部门项目推进表管理系统API',
            'version': '1.0.0',
            'environment': 'docker' if os.environ.get('DATABASE_PATH') else 'local',
            'endpoints': {
                'projects': '/api/projects',
                'users': '/api/users',
                'overview': '/api/projects/overview',
                'health': '/api/health'
            }
        })
    
    # 健康检查路由
    @app.route('/health')
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'message': '系统运行正常',
            'environment': 'docker' if os.environ.get('DATABASE_PATH') else 'local'
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({
            'success': False,
            'message': '请求的资源不存在',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error': 'Internal Server Error'
        }), 500
    
    # Docker环境：提供前端SPA应用（必须在所有API路由之后注册）
    if os.environ.get('DATABASE_PATH'):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_spa(path):
            """提供前端SPA应用"""
            # API路由已经被蓝图处理，这里只处理前端路由
            if path.startswith('api') or path.startswith('api/'):
                # API路由返回404（由错误处理器处理）
                abort(404)
            
            static_dir = '/app/frontend/dist'
            
            # 如果是静态资源文件（assets/, images/等）
            if path:
                file_path = os.path.join(static_dir, path)
                if os.path.isfile(file_path):
                    return send_from_directory(static_dir, path)
            
            # 所有其他路径返回index.html（Vue Router的SPA路由）
            return send_from_directory(static_dir, 'index.html')
    else:
        # 本地开发环境：根路由返回API信息
        @app.route('/')
        def index():
            """根路由 - 系统信息"""
            return jsonify({
                'success': True,
                'message': '部门项目推进表管理系统API',
                'version': '1.0.0',
                'environment': 'local',
                'endpoints': {
                    'projects': '/api/projects',
                    'users': '/api/users',
                    'overview': '/api/projects/overview',
                    'health': '/api/health'
                },
                'note': '前端请访问 http://localhost:3000'
            })
    
    return app

def init_sample_data(app):
    """初始化示例数据"""
    from backend.models.database import db, User, Project, ProjectMember, ProjectModule, ModuleAssignment, ModuleWorkRecord, UserRole, ProjectStatus, ProjectMemberRole
    from datetime import date, datetime, timedelta
    
    with app.app_context():
        # 检查是否已有数据
        if User.query.count() > 1:  # 除了默认管理员
            print("数据库已有数据，跳过初始化")
            return
        
        try:
            # 创建示例用户
            users_data = [
                {'name': '张三', 'position': '前端开发', 'email': 'zhangsan@company.com'},
                {'name': '李四', 'position': '后端开发', 'email': 'lisi@company.com'},
                {'name': '王五', 'position': '产品经理', 'email': 'wangwu@company.com'},
                {'name': '赵六', 'position': 'UI设计师', 'email': 'zhaoliu@company.com'},
                {'name': '钱七', 'position': '测试工程师', 'email': 'qianqi@company.com'}
            ]
            
            users = []
            for user_data in users_data:
                user = User(**user_data, role=UserRole.MEMBER)
                db.session.add(user)
                users.append(user)
            
            db.session.flush()  # 获取用户ID
            
            # 创建示例项目
            projects_data = [
                {
                    'name': '电商平台升级',
                    'description': '升级现有电商平台，提升用户体验',
                    'start_date': date(2024, 1, 1),
                    'end_date': date(2024, 6, 30),
                    'status': ProjectStatus.PROJECT_IMPLEMENTATION,
                    'progress': 65,
                    'priority': 5
                },
                {
                    'name': '移动端APP开发',
                    'description': '开发配套的移动端应用',
                    'start_date': date(2024, 2, 1),
                    'end_date': date(2024, 8, 31),
                    'status': ProjectStatus.PROJECT_IMPLEMENTATION,
                    'progress': 40,
                    'priority': 4
                },
                {
                    'name': '数据分析系统',
                    'description': '构建用户行为数据分析系统',
                    'start_date': date(2024, 3, 1),
                    'end_date': date(2024, 12, 31),
                    'status': ProjectStatus.INITIAL_CONTACT,
                    'progress': 10,
                    'priority': 3
                }
            ]
            
            for project_data in projects_data:
                project = Project(**project_data)
                db.session.add(project)
            
            db.session.flush()  # 获取项目ID
            
            # 分配项目成员
            projects = Project.query.all()
            
            # 电商平台升级项目
            if len(projects) > 0:
                project_members = [
                    ProjectMember(project_id=projects[0].id, user_id=users[1].id, role=ProjectMemberRole.LEADER),
                    ProjectMember(project_id=projects[0].id, user_id=users[0].id, role=ProjectMemberRole.MEMBER),
                    ProjectMember(project_id=projects[0].id, user_id=users[3].id, role=ProjectMemberRole.MEMBER),
                ]
                for member in project_members:
                    db.session.add(member)
            
            # 移动端APP开发项目
            if len(projects) > 1:
                project_members = [
                    ProjectMember(project_id=projects[1].id, user_id=users[0].id, role=ProjectMemberRole.LEADER),
                    ProjectMember(project_id=projects[1].id, user_id=users[1].id, role=ProjectMemberRole.MEMBER),
                    ProjectMember(project_id=projects[1].id, user_id=users[2].id, role=ProjectMemberRole.MEMBER),
                    ProjectMember(project_id=projects[1].id, user_id=users[4].id, role=ProjectMemberRole.MEMBER),
                ]
                for member in project_members:
                    db.session.add(member)
            
            # 数据分析系统项目
            if len(projects) > 2:
                project_members = [
                    ProjectMember(project_id=projects[2].id, user_id=users[2].id, role=ProjectMemberRole.LEADER),
                    ProjectMember(project_id=projects[2].id, user_id=users[1].id, role=ProjectMemberRole.MEMBER),
                ]
                for member in project_members:
                    db.session.add(member)
            
            # 创建示例模块
            if len(projects) > 0:
                # 电商平台升级项目的模块
                modules_data = [
                    {
                        'project_id': projects[0].id,
                        'name': '用户界面改版',
                        'description': '重新设计用户界面，提升用户体验',
                        'assigned_to_id': users[3].id,  # 赵六(UI设计师)
                        'progress': 80,
                        'priority': 5,
                        'status': ProjectStatus.IN_PROGRESS
                    },
                    {
                        'project_id': projects[0].id,
                        'name': '后端API优化',
                        'description': '优化后端接口性能，提升响应速度',
                        'assigned_to_id': users[1].id,  # 李四(后端开发)
                        'progress': 60,
                        'priority': 4,
                        'status': ProjectStatus.IN_PROGRESS
                    },
                    {
                        'project_id': projects[0].id,
                        'name': '数据库重构',
                        'description': '重构数据库结构，提升查询效率',
                        'assigned_to_id': users[1].id,  # 李四(后端开发)
                        'progress': 40,
                        'priority': 3,
                        'status': ProjectStatus.IN_PROGRESS
                    }
                ]
                
                for module_data in modules_data:
                    module = ProjectModule(**module_data)
                    db.session.add(module)
            
            if len(projects) > 1:
                # 移动端APP开发项目的模块
                modules_data = [
                    {
                        'project_id': projects[1].id,
                        'name': '用户注册登录',
                        'description': '实现用户注册、登录和身份验证功能',
                        'assigned_to_id': users[0].id,  # 张三(前端开发)
                        'progress': 70,
                        'priority': 5,
                        'status': ProjectStatus.IN_PROGRESS
                    },
                    {
                        'project_id': projects[1].id,
                        'name': '商品展示',
                        'description': '商品列表、详情页面展示功能',
                        'assigned_to_id': users[0].id,  # 张三(前端开发)
                        'progress': 30,
                        'priority': 4,
                        'status': ProjectStatus.IN_PROGRESS
                    },
                    {
                        'project_id': projects[1].id,
                        'name': '支付系统',
                        'description': '集成第三方支付接口',
                        'assigned_to_id': users[1].id,  # 李四(后端开发)
                        'progress': 20,
                        'priority': 5,
                        'status': ProjectStatus.PLANNING
                    },
                    {
                        'project_id': projects[1].id,
                        'name': '功能测试',
                        'description': '全面测试APP各项功能',
                        'assigned_to_id': users[4].id,  # 钱七(测试工程师)
                        'progress': 10,
                        'priority': 3,
                        'status': ProjectStatus.PLANNING
                    }
                ]
                
                for module_data in modules_data:
                    module = ProjectModule(**module_data)
                    db.session.add(module)
            
            if len(projects) > 2:
                # 数据分析系统项目的模块
                modules_data = [
                    {
                        'project_id': projects[2].id,
                        'name': '需求分析',
                        'description': '分析用户行为数据需求',
                        'assigned_to_id': users[2].id,  # 王五(产品经理)
                        'progress': 50,
                        'priority': 5,
                        'status': ProjectStatus.IN_PROGRESS
                    },
                    {
                        'project_id': projects[2].id,
                        'name': '数据采集',
                        'description': '设计和实现数据采集系统',
                        'assigned_to_id': users[1].id,  # 李四(后端开发)
                        'progress': 0,
                        'priority': 4,
                        'status': ProjectStatus.PLANNING
                    }
                ]
                
                for module_data in modules_data:
                    module = ProjectModule(**module_data)
                    db.session.add(module)
            
            db.session.commit()
            
            # 创建模块分配和工作记录
            modules = ProjectModule.query.all()
            if modules:
                # 为每个模块添加多个负责人
                for module in modules:
                    # 根据模块分配不同的用户组合
                    if module.name == '用户界面改版':
                        user_assignments = [users[3].id, users[0].id]  # 赵六、张三
                    elif module.name == '后端API优化':
                        user_assignments = [users[1].id, users[4].id]  # 李四、钱七
                    elif module.name == '数据库重构':
                        user_assignments = [users[1].id]  # 李四
                    elif module.name == '用户注册登录':
                        user_assignments = [users[0].id, users[1].id]  # 张三、李四
                    elif module.name == '商品展示':
                        user_assignments = [users[0].id, users[3].id]  # 张三、赵六
                    elif module.name == '支付系统':
                        user_assignments = [users[1].id]  # 李四
                    elif module.name == '功能测试':
                        user_assignments = [users[4].id, users[0].id]  # 钱七、张三
                    elif module.name == '需求分析':
                        user_assignments = [users[2].id, users[3].id]  # 王五、赵六
                    elif module.name == '数据采集':
                        user_assignments = [users[1].id, users[4].id]  # 李四、钱七
                    else:
                        user_assignments = [users[0].id]  # 默认张三
                    
                    # 创建模块分配
                    for user_id in user_assignments:
                        assignment = ModuleAssignment(
                            module_id=module.id,
                            user_id=user_id,
                            role='member'
                        )
                        db.session.add(assignment)
                    
                    # 创建工作记录（最近两周）
                    today = date.today()
                    
                    # 上周的工作记录
                    last_week_start = today - timedelta(days=today.weekday() + 7)
                    last_week_end = last_week_start + timedelta(days=6)
                    
                    # 本周的工作记录
                    this_week_start = today - timedelta(days=today.weekday())
                    this_week_end = this_week_start + timedelta(days=6)
                    
                    # 为部分模块添加上周工作记录
                    if module.name in ['用户界面改版', '后端API优化', '用户注册登录']:
                        last_week_record = ModuleWorkRecord(
                            module_id=module.id,
                            week_start=last_week_start,
                            week_end=last_week_end,
                            work_content=f"完成了{module.name}的基础架构搭建，进行了技术方案评估和原型设计。",
                            achievements="技术方案确定，完成了核心功能的70%开发工作。",
                            issues="遇到了一些兼容性问题，需要进一步优化。",
                            next_week_plan="继续完善功能细节，进行测试和优化。",
                            created_by_id=user_assignments[0]
                        )
                        db.session.add(last_week_record)
                    
                    # 为所有模块添加本周工作记录
                    work_contents = {
                        '用户界面改版': "优化了用户交互流程，完成了响应式布局适配，进行了用户体验测试。",
                        '后端API优化': "完成了数据库查询优化，实现了缓存机制，提升了接口响应速度30%。",
                        '数据库重构': "分析了现有数据结构，设计了新的表结构，开始进行数据迁移测试。",
                        '用户注册登录': "完成了OAuth2.0集成，实现了第三方登录功能，进行了安全测试。",
                        '商品展示': "优化了商品列表加载性能，实现了图片懒加载，完成了筛选功能。",
                        '支付系统': "完成了支付宝、微信支付接口集成，进行了支付流程测试。",
                        '功能测试': "完成了用户模块的自动化测试用例编写，发现并修复了5个bug。",
                        '需求分析': "收集了用户反馈，完成了需求文档更新，确定了下阶段开发重点。",
                        '数据采集': "设计了数据采集架构，完成了基础数据源接入，测试了数据准确性。"
                    }
                    
                    achievements = {
                        '用户界面改版': "用户体验得到显著提升，页面加载速度提升40%。",
                        '后端API优化': "系统整体性能提升30%，并发处理能力增强。",
                        '数据库重构': "数据结构更加合理，为后续功能扩展奠定基础。",
                        '用户注册登录': "提供了更便捷的登录方式，用户转化率提升15%。",
                        '商品展示': "页面响应速度提升，用户浏览体验优化。",
                        '支付系统': "支付成功率达到99.5%，用户支付体验良好。",
                        '功能测试': "代码质量得到保障，系统稳定性提升。",
                        '需求分析': "需求更加明确，开发方向更加清晰。",
                        '数据采集': "数据质量可靠，为数据分析提供了基础。"
                    }
                    
                    this_week_record = ModuleWorkRecord(
                        module_id=module.id,
                        week_start=this_week_start,
                        week_end=this_week_end,
                        work_content=work_contents.get(module.name, f"继续推进{module.name}相关工作。"),
                        achievements=achievements.get(module.name, "按计划完成了本周的工作目标。"),
                        issues="无重大问题。" if module.progress > 50 else "进度略有延迟，需要加快推进。",
                        next_week_plan=f"下周将重点推进{module.name}的剩余功能开发。",
                        created_by_id=user_assignments[0]
                    )
                    db.session.add(this_week_record)
            
            db.session.commit()
            print("示例数据初始化完成")
            
        except Exception as e:
            db.session.rollback()
            print(f"初始化示例数据失败: {str(e)}")

if __name__ == '__main__':
    # 创建应用实例
    app = create_app()
    
    # 初始化示例数据
    init_sample_data(app)
    
    # 获取端口（支持Railway等云平台的PORT环境变量）
    port = int(os.environ.get('PORT', 5001))
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # 启动应用
    print("正在启动项目推进表管理系统...")
    print(f"访问地址: http://0.0.0.0:{port}")
    print(f"环境: {'生产环境' if is_production else '开发环境'}")
    
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=port,
        debug=not is_production  # 生产环境关闭debug
    )
