"""
认证服务 - 处理用户认证、权限检查等业务逻辑
"""
import re
from sqlalchemy.exc import IntegrityError
from pypinyin import lazy_pinyin

class AuthService:
    """认证服务类"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        验证用户凭证 - 支持双重认证（拼音用户名或中文姓名）
        
        Args:
            username (str): 用户名（可以是拼音用户名或中文姓名）
            password (str): 密码
            
        Returns:
            User: 验证成功返回用户对象，失败返回None
        """
        try:
            from ..models.database import User
            # 首先尝试用户名匹配
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return user
            
            # 如果用户名匹配失败，尝试中文姓名匹配
            user = User.query.filter_by(name=username).first()
            if user and user.check_password(password):
                return user
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def generate_username(name):
        """
        生成用户名 - 使用pypinyin自动转换所有汉字
        
        Args:
            name (str): 用户姓名
            
        Returns:
            str: 生成的用户名
        """
        try:
            # 使用pypinyin自动转换中文为拼音
            pinyin_list = lazy_pinyin(name)
            base_username = ''.join(pinyin_list).lower()
            
            # 移除非字母数字字符
            base_username = re.sub(r'[^\w]', '', base_username)
            
            # 确保用户名不为空且不超过50个字符
            if not base_username:
                base_username = 'user'
            elif len(base_username) > 40:  # 留10个字符给序号
                base_username = base_username[:40]
            
            # 检查用户名是否已存在，如果存在则添加数字后缀
            username = base_username
            counter = 1
            
            from ..models.database import User
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
                # 防止无限循环
                if counter > 9999:
                    username = f"{base_username}{counter}"
                    break
            
            return username
            
        except Exception as e:
            # 如果pypinyin转换失败，使用备用方案
            print(f"Pypinyin转换失败: {e}")
            # 使用姓名的哈希值作为用户名
            import hashlib
            hash_value = hashlib.md5(name.encode('utf-8')).hexdigest()
            return f"user_{hash_value[:8]}"
    
    @staticmethod
    def create_user(name, email=None, position=None, role=None):
        """
        创建新用户
        
        Args:
            name (str): 用户姓名
            email (str): 邮箱
            position (str): 职位
            role (UserRole): 用户角色
            
        Returns:
            tuple: (User对象, 原始密码) 成功时，(None, 错误信息) 失败时
        """
        try:
            from ..models.database import db, User, UserRole
            
            if role is None:
                role = UserRole.MEMBER
            
            # 生成用户名
            username = AuthService.generate_username(name)
            
            # 创建用户
            user = User(
                name=name,
                username=username,
                email=email,
                position=position,
                role=role
            )
            
            # 设置默认密码
            default_password = 'td123456'
            user.set_password(default_password)
            
            # 保存到数据库
            db.session.add(user)
            db.session.commit()
            
            return user, default_password
            
        except IntegrityError as e:
            db.session.rollback()
            if 'username' in str(e):
                return None, '用户名已存在'
            elif 'email' in str(e):
                return None, '邮箱已存在'
            else:
                return None, '数据完整性错误'
        except Exception as e:
            db.session.rollback()
            return None, f'创建用户失败: {str(e)}'
    
    @staticmethod
    def has_permission(user, permission):
        """
        检查用户是否有指定权限
        
        Args:
            user (User): 用户对象
            permission (str): 权限名称
            
        Returns:
            bool: 有权限返回True，否则返回False
        """
        if not user or not user.role:
            return False
        
        from ..models.database import UserRole
        
        # 部门主管拥有所有权限
        if user.role == UserRole.DEPARTMENT_MANAGER:
            return True
        
        # 定义基础权限映射（基于系统角色）
        permissions = {
            # 项目权限
            'view_all_projects': [UserRole.DEPARTMENT_MANAGER],
            'create_project': [UserRole.DEPARTMENT_MANAGER],
            'edit_all_projects': [UserRole.DEPARTMENT_MANAGER],
            'delete_project': [UserRole.DEPARTMENT_MANAGER],
            'view_own_projects': [UserRole.DEPARTMENT_MANAGER, UserRole.MEMBER],
            
            # 模块权限（基础权限，具体项目权限需要额外检查）
            'update_all_modules': [UserRole.DEPARTMENT_MANAGER],
            'view_all_modules': [UserRole.DEPARTMENT_MANAGER, UserRole.MEMBER],
            
            # 用户管理权限
            'manage_users': [UserRole.DEPARTMENT_MANAGER],
            'view_users': [UserRole.DEPARTMENT_MANAGER, UserRole.MEMBER],  # 所有用户都能查看用户列表（用于项目协作）
            
            # 系统权限
            'access_dashboard': [UserRole.DEPARTMENT_MANAGER, UserRole.MEMBER],
            'access_user_management': [UserRole.DEPARTMENT_MANAGER],
        }
        
        allowed_roles = permissions.get(permission, [])
        return user.role in allowed_roles
    
    @staticmethod
    def has_project_permission(user, project_id, permission):
        """
        检查用户在特定项目中是否有指定权限
        
        Args:
            user (User): 用户对象
            project_id (int): 项目ID
            permission (str): 权限名称
            
        Returns:
            bool: 有权限返回True，否则返回False
        """
        if not user:
            return False
        
        from ..models.database import UserRole, ProjectMember, ProjectMemberRole
        
        # 部门主管拥有所有项目的所有权限
        if user.role == UserRole.DEPARTMENT_MANAGER:
            return True
        
        # 查询用户在该项目中的角色
        project_member = ProjectMember.query.filter_by(
            user_id=user.id,
            project_id=project_id
        ).first()
        
        if not project_member:
            return False  # 用户不是该项目成员
        
        # 根据项目角色和权限类型判断
        if permission == 'edit_project':
            # 只有项目负责人可以编辑项目
            return project_member.role == ProjectMemberRole.LEADER
        elif permission == 'view_project':
            # 所有项目成员都可以查看项目
            return True
        elif permission == 'update_project_modules':
            # 项目负责人可以更新项目的所有模块
            return project_member.role == ProjectMemberRole.LEADER
        elif permission == 'view_project_modules':
            # 所有项目成员都可以查看项目模块
            return True
        
        return False
    
    @staticmethod
    def has_module_permission(user, module_id, permission):
        """
        检查用户是否有操作特定模块的权限
        
        Args:
            user (User): 用户对象
            module_id (int): 模块ID
            permission (str): 权限名称
            
        Returns:
            bool: 有权限返回True，否则返回False
        """
        if not user:
            return False
        
        from ..models.database import UserRole, ProjectModule, ProjectMember, ProjectMemberRole
        
        # 部门主管拥有所有权限
        if user.role == UserRole.DEPARTMENT_MANAGER:
            return True
        
        # 获取模块信息
        module = ProjectModule.query.get(module_id)
        if not module:
            return False
        
        # 检查用户是否是该项目成员
        project_member = ProjectMember.query.filter_by(
            user_id=user.id,
            project_id=module.project_id
        ).first()
        
        if not project_member:
            return False
        
        if permission == 'update_module':
            # 项目负责人可以更新项目的所有模块
            if project_member.role == ProjectMemberRole.LEADER:
                return True
            # 普通成员只能更新分配给自己的模块
            return user.id in [u.id for u in module.assigned_users]
        elif permission == 'delete_module':
            # 项目负责人可以删除项目的所有模块
            if project_member.role == ProjectMemberRole.LEADER:
                return True
            # 普通成员不能删除模块
            return False
        elif permission == 'view_module':
            # 所有项目成员都可以查看模块
            return True
        
        return False
    
    @staticmethod
    def get_user_projects(user):
        """
        获取用户可访问的项目
        
        Args:
            user (User): 用户对象
            
        Returns:
            list: 项目ID列表
        """
        if not user:
            return []
        
        from ..models.database import UserRole
        
        # 部门主管可以看到所有项目
        if user.role == UserRole.DEPARTMENT_MANAGER:
            from ..models.database import Project
            return [p.id for p in Project.query.all()]
        
        # 项目负责人和成员只能看到自己参与的项目
        project_ids = []
        for membership in user.project_memberships:
            project_ids.append(membership.project_id)
        
        return project_ids
    
    @staticmethod
    def get_user_modules(user, project_id=None):
        """
        获取用户可更新的模块
        
        Args:
            user (User): 用户对象
            project_id (int): 项目ID，可选
            
        Returns:
            list: 模块ID列表
        """
        if not user:
            return []
        
        from ..models.database import UserRole
        
        # 部门主管可以更新所有模块
        if user.role == UserRole.DEPARTMENT_MANAGER:
            from ..models.database import ProjectModule
            query = ProjectModule.query
            if project_id:
                query = query.filter_by(project_id=project_id)
            return [m.id for m in query.all()]
        
        # 普通成员中的项目负责人可以更新自己项目的所有模块
        if user.role == UserRole.MEMBER:
            from ..models.database import ProjectModule, ProjectMember, ProjectMemberRole
            # 获取用户作为项目负责人的项目中的所有模块
            leader_modules = ProjectModule.query.join(ProjectMember).filter(
                ProjectMember.user_id == user.id,
                ProjectMember.role == ProjectMemberRole.LEADER
            )
            if project_id:
                leader_modules = leader_modules.filter(ProjectModule.project_id == project_id)
            
            leader_module_ids = [m.id for m in leader_modules.all()]
            
            # 获取用户直接负责的模块
            assigned_modules = ProjectModule.query.filter_by(assigned_to_id=user.id)
            if project_id:
                assigned_modules = assigned_modules.filter_by(project_id=project_id)
            
            assigned_module_ids = [m.id for m in assigned_modules.all()]
            
            # 合并两个列表并去重
            return list(set(leader_module_ids + assigned_module_ids))
        
        # 默认情况，返回空列表
        return []
