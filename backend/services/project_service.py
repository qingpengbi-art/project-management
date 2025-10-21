"""
项目服务层 - 项目相关的业务逻辑
遵循DDD分层架构，处理项目管理的核心业务逻辑
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date
from sqlalchemy import and_, or_, desc
from ..models.database import db, Project, ProjectMember, ProgressRecord, User, ProjectStatus, ProjectMemberRole

class ProjectService:
    """项目服务类 - 处理项目相关的业务逻辑"""
    
    @staticmethod
    def create_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新项目
        
        Args:
            project_data: 项目数据字典
            
        Returns:
            创建结果和项目信息
        """
        try:
            # 创建项目对象
            project = Project(
                name=project_data.get('name'),
                description=project_data.get('description'),
                start_date=datetime.strptime(project_data.get('start_date'), '%Y-%m-%d').date() if project_data.get('start_date') else None,
                end_date=datetime.strptime(project_data.get('end_date'), '%Y-%m-%d').date() if project_data.get('end_date') else None,
                priority=project_data.get('priority', 1),
                status=ProjectStatus(project_data.get('status', 'planning')),
                project_source=project_data.get('project_source', 'horizontal'),  # 项目来源，默认横向
                partner=project_data.get('partner'),  # 合作方（可选）
                amount=project_data.get('amount')  # 项目金额（可选）
            )
            
            db.session.add(project)
            db.session.flush()  # 获取项目ID
            
            # 添加项目成员
            members_data = project_data.get('members', [])
            for member_data in members_data:
                member = ProjectMember(
                    project_id=project.id,
                    user_id=member_data.get('user_id'),
                    role=ProjectMemberRole(member_data.get('role', 'member'))
                )
                db.session.add(member)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '项目创建成功',
                'data': project.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'项目创建失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_project_list(filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取项目列表
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            项目列表
        """
        try:
            query = Project.query
            
            # 应用过滤条件
            if filters:
                if filters.get('status'):
                    query = query.filter(Project.status == ProjectStatus(filters['status']))
                
                if filters.get('user_id'):
                    # 查询用户参与的项目
                    query = query.join(ProjectMember).filter(ProjectMember.user_id == filters['user_id'])
                
                if filters.get('search'):
                    # 搜索项目名称或描述
                    search_term = f"%{filters['search']}%"
                    query = query.filter(or_(
                        Project.name.like(search_term),
                        Project.description.like(search_term)
                    ))
                
                if filters.get('project_ids'):
                    # 按项目ID列表过滤
                    project_ids = filters['project_ids']
                    if project_ids:  # 如果列表不为空
                        query = query.filter(Project.id.in_(project_ids))
                    else:  # 如果列表为空，返回空结果
                        query = query.filter(False)
            
            # 按更新时间降序排列
            projects = query.order_by(desc(Project.updated_at)).all()
            
            # 转换为字典并添加成员信息
            project_list = []
            for project in projects:
                project_dict = project.to_dict()
                
                # 添加项目成员信息
                members = []
                leaders = []
                for member in project.members:
                    member_info = {
                        'id': member.user.id,
                        'name': member.user.name,
                        'role': member.role.value,
                        'position': member.user.position
                    }
                    members.append(member_info)
                    
                    if member.role == ProjectMemberRole.LEADER:
                        leaders.append(member_info)
                
                project_dict['members'] = members
                project_dict['leaders'] = leaders
                project_dict['member_count'] = len(members)
                
                # 添加最新进度记录
                latest_record = ProgressRecord.query.filter_by(project_id=project.id)\
                    .order_by(desc(ProgressRecord.updated_at)).first()
                if latest_record:
                    project_dict['latest_update'] = {
                        'progress': latest_record.progress,
                        'notes': latest_record.notes,
                        'updated_by': latest_record.updated_by.name,
                        'updated_at': latest_record.updated_at.isoformat()
                    }
                
                project_list.append(project_dict)
            
            return {
                'success': True,
                'message': '获取项目列表成功',
                'data': project_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取项目列表失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def get_project_detail(project_id: int) -> Dict[str, Any]:
        """
        获取项目详情
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目详情
        """
        try:
            project = Project.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': '项目不存在',
                    'data': None
                }
            
            project_dict = project.to_dict()
            
            # 添加成员详情
            members = []
            for member in project.members:
                member_info = member.to_dict()
                members.append(member_info)
            project_dict['members'] = members
            
            # 添加进度历史
            progress_history = []
            for record in project.progress_records:
                progress_history.append(record.to_dict())
            project_dict['progress_history'] = sorted(progress_history, key=lambda x: x['updated_at'], reverse=True)
            
            return {
                'success': True,
                'message': '获取项目详情成功',
                'data': project_dict
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取项目详情失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_project(project_id: int, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            project_data: 项目更新数据
            
        Returns:
            更新结果
        """
        try:
            # 查找项目
            project = Project.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': '项目不存在',
                    'data': None
                }
            
            # 更新项目基本信息
            if 'name' in project_data:
                project.name = project_data['name']
            
            if 'description' in project_data:
                project.description = project_data['description']
            
            if 'start_date' in project_data and project_data['start_date']:
                project.start_date = datetime.strptime(project_data['start_date'], '%Y-%m-%d').date()
            
            if 'end_date' in project_data and project_data['end_date']:
                project.end_date = datetime.strptime(project_data['end_date'], '%Y-%m-%d').date()
            
            if 'priority' in project_data:
                project.priority = project_data['priority']
            
            if 'status' in project_data:
                project.status = ProjectStatus(project_data['status'])
            
            if 'project_source' in project_data:
                project.project_source = project_data['project_source']
            
            if 'partner' in project_data:
                project.partner = project_data['partner']
            
            if 'amount' in project_data:
                project.amount = project_data['amount']
            
            project.updated_at = datetime.now()
            
            # 处理项目成员更新
            if 'members' in project_data:
                # 删除现有成员
                ProjectMember.query.filter_by(project_id=project_id).delete()
                
                # 添加新成员
                members_data = project_data['members']
                for member_data in members_data:
                    member = ProjectMember(
                        project_id=project.id,
                        user_id=member_data.get('user_id'),
                        role=ProjectMemberRole(member_data.get('role', 'member'))
                    )
                    db.session.add(member)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '项目更新成功',
                'data': project.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新项目失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def delete_project(project_id: int) -> Dict[str, Any]:
        """
        删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            删除结果
        """
        try:
            project = Project.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': '项目不存在',
                    'data': None
                }
            
            project_name = project.name
            
            # 删除项目（级联删除会自动删除相关的成员、进度记录、模块等）
            db.session.delete(project)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'项目"{project_name}"已成功删除',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除项目失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_project_progress(project_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新项目进度
        
        Args:
            project_id: 项目ID
            progress_data: 进度数据
            
        Returns:
            更新结果
        """
        try:
            project = Project.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': '项目不存在',
                    'data': None
                }
            
            # 更新项目进度
            new_progress = progress_data.get('progress', project.progress)
            if new_progress < 0 or new_progress > 100:
                return {
                    'success': False,
                    'message': '进度值必须在0-100之间',
                    'data': None
                }
            
            project.progress = new_progress
            
            # 根据进度自动更新状态（仅在特定状态下自动更新）
            if new_progress == 0 and project.status == ProjectStatus.INITIAL_CONTACT:
                project.status = ProjectStatus.INITIAL_CONTACT  # 保持初步接触状态
            elif new_progress == 100 and project.status in [ProjectStatus.PROJECT_IMPLEMENTATION]:
                project.status = ProjectStatus.PROJECT_ACCEPTANCE  # 实施完成后进入验收阶段
                project.actual_end_date = date.today()
            elif new_progress > 0 and project.status == ProjectStatus.CONTRACT_SIGNED:
                project.status = ProjectStatus.PROJECT_IMPLEMENTATION  # 合同签订后开始实施
            
            project.updated_at = datetime.now()
            
            # 创建进度记录
            progress_record = ProgressRecord(
                project_id=project_id,
                progress=new_progress,
                notes=progress_data.get('notes'),
                updated_by_id=progress_data.get('updated_by_id')
            )
            
            db.session.add(progress_record)
            db.session.commit()
            
            return {
                'success': True,
                'message': '进度更新成功',
                'data': project.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'进度更新失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_department_overview() -> Dict[str, Any]:
        """
        获取部门项目总览
        用于主管向领导汇报
        
        Returns:
            部门项目总览数据
        """
        try:
            # 统计各状态项目数量
            status_counts = {}
            for status in ProjectStatus:
                count = Project.query.filter_by(status=status).count()
                status_counts[status.value] = count
            
            # 获取所有项目的基本信息
            projects = Project.query.order_by(desc(Project.updated_at)).all()
            
            # 计算整体进度
            total_progress = 0
            active_projects = 0
            
            project_summary = []
            for project in projects:
                if project.status not in [ProjectStatus.NO_FOLLOW_UP]:
                    total_progress += project.progress
                    active_projects += 1
                
                # 获取项目负责人
                leaders = [member.user.name for member in project.members 
                          if member.role == ProjectMemberRole.LEADER]
                
                project_info = {
                    'id': project.id,
                    'name': project.name,
                    'status': project.status.value,
                    'progress': project.progress,
                    'leaders': leaders,
                    'member_count': len(project.members),
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'end_date': project.end_date.isoformat() if project.end_date else None,
                    'priority': project.priority,
                    'project_source': project.project_source,  # 添加项目来源
                    'partner': project.partner,  # 添加合作方
                    'updated_at': project.updated_at.isoformat() if project.updated_at else None
                }
                project_summary.append(project_info)
            
            # 计算平均进度
            avg_progress = round(total_progress / active_projects, 1) if active_projects > 0 else 0
            
            # 统计人员参与情况
            user_stats = db.session.query(
                User.name,
                db.func.count(ProjectMember.id).label('project_count')
            ).join(ProjectMember).group_by(User.id, User.name).all()
            
            return {
                'success': True,
                'message': '获取部门总览成功',
                'data': {
                    'summary': {
                        'total_projects': len(projects),
                        'active_projects': active_projects,
                        'avg_progress': avg_progress,
                        'status_distribution': status_counts
                    },
                    'projects': project_summary,
                    'user_stats': [{'name': stat.name, 'project_count': stat.project_count} 
                                  for stat in user_stats]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取部门总览失败: {str(e)}',
                'data': None
            }
