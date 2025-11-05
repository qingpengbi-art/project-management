"""
用户服务层 - 用户和项目成员管理的业务逻辑
遵循DDD分层架构，处理用户管理的核心业务逻辑
"""

from typing import List, Dict, Optional, Any
from ..models.database import db, User, ProjectMember, Project, UserRole, ProjectMemberRole, ModuleAssignment, ProjectModule
from .auth_service import AuthService

class UserService:
    """用户服务类 - 处理用户相关的业务逻辑"""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新用户
        
        Args:
            user_data: 用户数据字典
            
        Returns:
            创建结果和用户信息
        """
        try:
            # 使用认证服务创建用户
            role = UserRole(user_data.get('role', 'member'))
            user, password = AuthService.create_user(
                name=user_data.get('name'),
                email=user_data.get('email'),
                position=user_data.get('position'),
                role=role
            )
            
            if not user:
                return {
                    'success': False,
                    'message': password,  # 这里password实际是错误信息
                    'data': None
                }
            
            return {
                'success': True,
                'message': '用户创建成功',
                'data': {
                    'user': user.to_dict(),
                    'username': user.username,
                    'password': password
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'用户创建失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_user_list(filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取用户列表
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            用户列表
        """
        try:
            query = User.query
            
            # 应用过滤条件
            if filters:
                if filters.get('role'):
                    query = query.filter(User.role == UserRole(filters['role']))
                
                if filters.get('search'):
                    # 搜索用户名称或职位
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        User.name.like(search_term) | 
                        User.position.like(search_term)
                    )
            
            users = query.order_by(User.name).all()
            
            # 转换为字典并添加项目参与信息
            user_list = []
            for user in users:
                user_dict = user.to_dict()
                
                # 统计参与项目数量：通过模块参与统计
                # 1. 找到用户参与的所有模块
                module_assignments = ModuleAssignment.query.filter_by(user_id=user.id).all()
                module_ids = [assignment.module_id for assignment in module_assignments]
                
                # 2. 找到这些模块对应的项目（去重）
                if module_ids:
                    project_ids = db.session.query(ProjectModule.project_id)\
                        .filter(ProjectModule.id.in_(module_ids))\
                        .distinct()\
                        .all()
                    project_count = len(project_ids)
                else:
                    project_count = 0
                
                user_dict['project_count'] = project_count
                
                # 统计负责项目数量：通过ProjectMember表中的LEADER角色
                leader_count = ProjectMember.query.filter_by(
                    user_id=user.id, 
                    role=ProjectMemberRole.LEADER
                ).count()
                user_dict['leader_count'] = leader_count
                
                user_list.append(user_dict)
            
            return {
                'success': True,
                'message': '获取用户列表成功',
                'data': user_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取用户列表失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def get_user_detail(user_id: int) -> Dict[str, Any]:
        """
        获取用户详情
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户详情
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            user_dict = user.to_dict()
            
            # 添加参与的项目信息
            projects = []
            for membership in user.project_memberships:
                project_info = {
                    'id': membership.project.id,
                    'name': membership.project.name,
                    'role': membership.role.value,
                    'status': membership.project.status.value,
                    'progress': membership.project.progress,
                    'joined_at': membership.joined_at.isoformat()
                }
                projects.append(project_info)
            
            user_dict['projects'] = projects
            
            return {
                'success': True,
                'message': '获取用户详情成功',
                'data': user_dict
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取用户详情失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def add_project_member(project_id: int, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加项目成员
        
        Args:
            project_id: 项目ID
            member_data: 成员数据
            
        Returns:
            添加结果
        """
        try:
            # 检查项目是否存在
            project = Project.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': '项目不存在',
                    'data': None
                }
            
            # 检查用户是否存在
            user_id = member_data.get('user_id')
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 检查是否已经是项目成员
            existing_member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=user_id
            ).first()
            
            if existing_member:
                return {
                    'success': False,
                    'message': '用户已经是项目成员',
                    'data': None
                }
            
            # 创建项目成员关系
            member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                role=ProjectMemberRole(member_data.get('role', 'member'))
            )
            
            db.session.add(member)
            db.session.commit()
            
            return {
                'success': True,
                'message': '项目成员添加成功',
                'data': member.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'添加项目成员失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def remove_project_member(project_id: int, user_id: int) -> Dict[str, Any]:
        """
        移除项目成员
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            
        Returns:
            移除结果
        """
        try:
            # 查找项目成员关系
            member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'message': '项目成员关系不存在',
                    'data': None
                }
            
            db.session.delete(member)
            db.session.commit()
            
            return {
                'success': True,
                'message': '项目成员移除成功',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'移除项目成员失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_member_role(project_id: int, user_id: int, new_role: str) -> Dict[str, Any]:
        """
        更新项目成员角色
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            new_role: 新角色
            
        Returns:
            更新结果
        """
        try:
            # 查找项目成员关系
            member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'message': '项目成员关系不存在',
                    'data': None
                }
            
            # 更新角色
            member.role = ProjectMemberRole(new_role)
            db.session.commit()
            
            return {
                'success': True,
                'message': '成员角色更新成功',
                'data': member.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新成员角色失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_user(user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 用户数据字典
            
        Returns:
            更新结果和用户信息
        """
        try:
            # 查找用户
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 检查邮箱是否已被其他用户使用
            if user_data.get('email') and user_data['email'] != user.email:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user:
                    return {
                        'success': False,
                        'message': '邮箱已被其他用户使用',
                        'data': None
                    }
            
            # 更新用户信息
            if 'name' in user_data:
                user.name = user_data['name']
            if 'email' in user_data:
                user.email = user_data['email']
            if 'position' in user_data:
                user.position = user_data['position']
            if 'role' in user_data:
                user.role = UserRole(user_data['role'])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '用户信息更新成功',
                'data': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'用户信息更新失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def delete_user(user_id: int) -> Dict[str, Any]:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除结果
        """
        try:
            # 查找用户
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 检查用户是否还参与模块（即参与项目）
            module_assignment_count = ModuleAssignment.query.filter_by(user_id=user_id).count()
            if module_assignment_count > 0:
                # 统计参与的项目数量用于提示
                module_assignments = ModuleAssignment.query.filter_by(user_id=user_id).all()
                module_ids = [assignment.module_id for assignment in module_assignments]
                if module_ids:
                    project_ids = db.session.query(ProjectModule.project_id)\
                        .filter(ProjectModule.id.in_(module_ids))\
                        .distinct()\
                        .all()
                    project_count = len(project_ids)
                else:
                    project_count = 0
                    
                return {
                    'success': False,
                    'message': f'用户还参与 {project_count} 个项目的 {module_assignment_count} 个模块，无法删除。请先从所有模块中移除该用户。',
                    'data': None
                }
            
            # 检查用户是否是项目负责人
            leader_count = ProjectMember.query.filter_by(user_id=user_id, role=ProjectMemberRole.LEADER).count()
            if leader_count > 0:
                return {
                    'success': False,
                    'message': f'用户还负责 {leader_count} 个项目，无法删除。请先更换项目负责人。',
                    'data': None
                }
            
            # 删除用户
            db.session.delete(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': '用户删除成功',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'用户删除失败: {str(e)}',
                'data': None
            }

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        用户修改自己的密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            修改结果
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 验证旧密码
            if not user.check_password(old_password):
                return {
                    'success': False,
                    'message': '旧密码不正确',
                    'data': None
                }
            
            # 设置新密码
            user.set_password(new_password)
            db.session.commit()
            
            return {
                'success': True,
                'message': '密码修改成功',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'密码修改失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def reset_password(user_id: int) -> Dict[str, Any]:
        """
        重置用户密码为初始密码 td123456
        只有部门主管可以执行此操作
        
        Args:
            user_id: 用户ID
            
        Returns:
            重置结果
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 设置为初始密码
            initial_password = 'td123456'
            user.set_password(initial_password)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'密码已重置为初始密码: {initial_password}',
                'data': {
                    'username': user.username,
                    'password': initial_password
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'密码重置失败: {str(e)}',
                'data': None
            }