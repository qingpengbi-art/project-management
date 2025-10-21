"""
数据库模型定义
使用SQLAlchemy ORM，遵循DDD分层架构原则
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ProjectStatus(Enum):
    """项目状态枚举 - 业务流程状态"""
    INITIAL_CONTACT = "initial_contact"        # 初步接触
    PROPOSAL_SUBMITTED = "proposal_submitted"   # 提交方案
    QUOTATION_SUBMITTED = "quotation_submitted" # 提交报价
    USER_CONFIRMATION = "user_confirmation"     # 用户确认
    CONTRACT_SIGNED = "contract_signed"         # 合同签订
    PROJECT_IMPLEMENTATION = "project_implementation" # 项目实施
    PROJECT_ACCEPTANCE = "project_acceptance"   # 项目验收
    WARRANTY_PERIOD = "warranty_period"        # 维保期内
    POST_WARRANTY = "post_warranty"            # 维保期外
    NO_FOLLOW_UP = "no_follow_up"             # 不再跟进

class ModuleStatus(Enum):
    """模块状态枚举"""
    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    PAUSED = "paused"           # 暂停

class UserRole(Enum):
    """用户系统角色枚举（固定岗位级别）"""
    DEPARTMENT_MANAGER = "department_manager"  # 部门主管
    MEMBER = "member"                          # 普通成员

class ProjectMemberRole(Enum):
    """项目成员角色枚举"""
    LEADER = "leader"         # 项目负责人
    MEMBER = "member"         # 项目参与者

class User(db.Model):
    """用户表 - 存储部门成员信息"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    position = db.Column(db.String(50), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.MEMBER)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    project_memberships = db.relationship('ProjectMember', back_populates='user', cascade='all, delete-orphan')
    progress_records = db.relationship('ProgressRecord', back_populates='updated_by', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'position': self.position,
            'role': self.role.value if self.role else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Project(db.Model):
    """项目表 - 存储项目基本信息"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    actual_end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.INITIAL_CONTACT)
    progress = db.Column(db.Integer, default=0)
    priority = db.Column(db.Integer, default=1)
    project_source = db.Column(db.String(50), default='horizontal')  # 项目来源：horizontal/vertical/self_developed
    partner = db.Column(db.String(100), nullable=True)  # 合作方（仅横向项目）
    amount = db.Column(db.Float, nullable=True)  # 项目金额（非必填）
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    members = db.relationship('ProjectMember', back_populates='project', cascade='all, delete-orphan')
    progress_records = db.relationship('ProgressRecord', back_populates='project', cascade='all, delete-orphan')
    modules = db.relationship('ProjectModule', back_populates='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'status': self.status.value if self.status else None,
            'project_source': self.project_source,
            'partner': self.partner,
            'amount': self.amount,
            'progress': self.progress,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectMember(db.Model):
    """项目成员关联表 - 存储项目与成员的关系"""
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum(ProjectMemberRole), default=ProjectMemberRole.MEMBER)
    joined_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    project = db.relationship('Project', back_populates='members')
    user = db.relationship('User', back_populates='project_memberships')
    
    # 唯一约束：一个用户在一个项目中只能有一个角色
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='unique_project_user'),)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role.value if self.role else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'user': self.user.to_dict() if self.user else None,
            'project': self.project.to_dict() if self.project else None
        }

class ProjectModule(db.Model):
    """项目模块表 - 存储项目内部模块信息"""
    __tablename__ = 'project_modules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    progress = db.Column(db.Integer, default=0)
    priority = db.Column(db.Integer, default=1)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(ModuleStatus), default=ModuleStatus.NOT_STARTED)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    project = db.relationship('Project', back_populates='modules')
    assigned_to = db.relationship('User', backref='assigned_modules')
    progress_records = db.relationship('ModuleProgressRecord', back_populates='module', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to': self.assigned_to.to_dict() if self.assigned_to else None,
            'progress': self.progress,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ModuleAssignment(db.Model):
    """模块分配表 - 存储模块与用户的多对多关系"""
    __tablename__ = 'module_assignments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('project_modules.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), default='member')
    assigned_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    module = db.relationship('ProjectModule', backref='assignments')
    user = db.relationship('User', backref='module_assignments')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'module_id': self.module_id,
            'user_id': self.user_id,
            'role': self.role,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'user': self.user.to_dict() if self.user else None
        }

class ModuleWorkRecord(db.Model):
    """模块工作内容记录表 - 存储每周的具体工作内容"""
    __tablename__ = 'module_work_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('project_modules.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    work_content = db.Column(db.Text, nullable=False)
    achievements = db.Column(db.Text, nullable=True)
    issues = db.Column(db.Text, nullable=True)
    next_week_plan = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    module = db.relationship('ProjectModule', backref='work_records')
    created_by = db.relationship('User', backref='work_records')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'module_id': self.module_id,
            'week_start': self.week_start.isoformat() if self.week_start else None,
            'week_end': self.week_end.isoformat() if self.week_end else None,
            'work_content': self.work_content,
            'achievements': self.achievements,
            'issues': self.issues,
            'next_week_plan': self.next_week_plan,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by.to_dict() if self.created_by else None,
            'week_label': f"{self.week_start.strftime('%m/%d')} - {self.week_end.strftime('%m/%d')}" if self.week_start and self.week_end else None
        }

class ModuleProgressRecord(db.Model):
    """模块进度记录表 - 存储模块进度更新历史"""
    __tablename__ = 'module_progress_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('project_modules.id'), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    module = db.relationship('ProjectModule', back_populates='progress_records')
    updated_by = db.relationship('User', backref='module_progress_records')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'module_id': self.module_id,
            'progress': self.progress,
            'notes': self.notes,
            'updated_by_id': self.updated_by_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by.to_dict() if self.updated_by else None,
            'module': self.module.to_dict() if self.module else None
        }

class ProgressRecord(db.Model):
    """进度记录表 - 存储项目进度更新历史"""
    __tablename__ = 'progress_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    project = db.relationship('Project', back_populates='progress_records')
    updated_by = db.relationship('User', back_populates='progress_records')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'progress': self.progress,
            'notes': self.notes,
            'updated_by_id': self.updated_by_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by.to_dict() if self.updated_by else None,
            'project': self.project.to_dict() if self.project else None
        }

def init_database(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        try:
            admin_user = User.query.filter_by(role=UserRole.DEPARTMENT_MANAGER).first()
        except:
            # 如果查询失败，说明表结构可能有问题，重新创建表
            db.drop_all()
            db.create_all()
            admin_user = None
        
        if not admin_user:
            admin_user = User(
                name='主管',
                username='admin',
                email='admin@company.com',
                position='部门主管',
                role=UserRole.DEPARTMENT_MANAGER
            )
            admin_user.set_password('td123456')
            db.session.add(admin_user)
            db.session.commit()
            print(f"已创建默认管理员用户: admin, 密码: td123456")
