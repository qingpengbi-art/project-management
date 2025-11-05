"""
模块服务层 - 项目模块管理的业务逻辑
遵循DDD分层架构，处理项目模块管理的核心业务逻辑
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, desc, func
from ..models.database import db, ProjectModule, ModuleProgressRecord, ModuleWorkRecord, ModuleAssignment, Project, User, ProjectStatus, ModuleStatus

class ModuleService:
    """模块服务类 - 处理项目模块相关的业务逻辑"""
    
    @staticmethod
    def create_module(project_id: int, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建项目模块
        
        Args:
            project_id: 项目ID
            module_data: 模块数据字典
            
        Returns:
            创建结果和模块信息
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
            
            # 获取初始进度和状态
            initial_progress = module_data.get('progress', 0)
            status_value = module_data.get('status')
            
            # 根据状态自动调整进度，确保状态和进度一致
            if status_value == 'completed':
                # 如果状态是已完成，强制设置进度为100%
                initial_progress = 100
                auto_status = ModuleStatus.COMPLETED
            elif status_value == 'not_started':
                # 如果状态是未开始，强制设置进度为0%
                initial_progress = 0
                auto_status = ModuleStatus.NOT_STARTED
            elif status_value == 'in_progress':
                # 如果状态是进行中，确保进度在1-99之间
                if initial_progress <= 0:
                    initial_progress = 10  # 默认10%
                elif initial_progress >= 100:
                    initial_progress = 99  # 最多99%
                auto_status = ModuleStatus.IN_PROGRESS
            elif status_value == 'paused':
                auto_status = ModuleStatus.PAUSED
            else:
                # 没有指定状态，根据进度自动设置
                if initial_progress == 0:
                    auto_status = ModuleStatus.NOT_STARTED
                elif initial_progress == 100:
                    auto_status = ModuleStatus.COMPLETED
                else:
                    auto_status = ModuleStatus.IN_PROGRESS
            
            # 创建模块对象
            module = ProjectModule(
                project_id=project_id,
                name=module_data.get('name'),
                description=module_data.get('description'),
                assigned_to_id=module_data.get('assigned_to_id'),
                progress=initial_progress,  # 设置初始进度
                priority=module_data.get('priority', 1),
                start_date=datetime.strptime(module_data.get('start_date'), '%Y-%m-%d').date() if module_data.get('start_date') else None,
                end_date=datetime.strptime(module_data.get('end_date'), '%Y-%m-%d').date() if module_data.get('end_date') else None,
                status=auto_status
            )
            
            db.session.add(module)
            db.session.commit()
            
            # 创建模块后更新项目进度
            try:
                ModuleService._update_project_progress(project_id)
                db.session.commit()
            except Exception as e:
                print(f"更新项目进度时出错: {str(e)}")
                # 不影响模块创建的成功
            
            return {
                'success': True,
                'message': '模块创建成功',
                'data': module.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'模块创建失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_project_modules(project_id: int) -> Dict[str, Any]:
        """
        获取项目的所有模块
        
        Args:
            project_id: 项目ID
            
        Returns:
            模块列表
        """
        try:
            # 检查项目是否存在
            project = Project.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': '项目不存在',
                    'data': []
                }
            
            # 获取项目模块
            modules = ProjectModule.query.filter_by(project_id=project_id)\
                .order_by(ProjectModule.priority.desc(), ProjectModule.created_at).all()
            
            module_list = []
            for module in modules:
                module_dict = module.to_dict()
                
                # 添加模块成员列表
                assignments = ModuleAssignment.query.filter_by(module_id=module.id).all()
                assigned_users = []
                for assignment in assignments:
                    if assignment.user:
                        assigned_users.append({
                            'id': assignment.user.id,
                            'name': assignment.user.name,
                            'position': assignment.user.position,
                            'role': assignment.role
                        })
                module_dict['assigned_users'] = assigned_users
                
                # 添加最新进度记录
                latest_record = ModuleProgressRecord.query.filter_by(module_id=module.id)\
                    .order_by(desc(ModuleProgressRecord.updated_at)).first()
                if latest_record:
                    module_dict['latest_update'] = {
                        'progress': latest_record.progress,
                        'notes': latest_record.notes,
                        'updated_by': latest_record.updated_by.name,
                        'updated_at': latest_record.updated_at.isoformat()
                    }
                
                module_list.append(module_dict)
            
            return {
                'success': True,
                'message': '获取模块列表成功',
                'data': module_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取模块列表失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def update_module(module_id: int, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新模块基本信息
        
        Args:
            module_id: 模块ID
            module_data: 模块数据
            
        Returns:
            更新结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            # 更新可编辑的字段
            if 'name' in module_data:
                module.name = module_data['name']
            
            if 'description' in module_data:
                module.description = module_data['description']
            
            if 'status' in module_data:
                module.status = ModuleStatus[module_data['status'].upper()] if isinstance(module_data['status'], str) else module_data['status']
            
            if 'start_date' in module_data:
                if module_data['start_date']:
                    module.start_date = datetime.strptime(module_data['start_date'], '%Y-%m-%d').date()
                else:
                    module.start_date = None
            
            if 'end_date' in module_data:
                if module_data['end_date']:
                    module.end_date = datetime.strptime(module_data['end_date'], '%Y-%m-%d').date()
                else:
                    module.end_date = None
            
            module.updated_at = datetime.now()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '模块更新成功',
                'data': module.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'模块更新失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_module_progress(module_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新模块进度
        
        Args:
            module_id: 模块ID
            progress_data: 进度数据
            
        Returns:
            更新结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            # 更新模块进度
            new_progress = progress_data.get('progress', module.progress)
            if new_progress < 0 or new_progress > 100:
                return {
                    'success': False,
                    'message': '进度值必须在0-100之间',
                    'data': None
                }
            
            module.progress = new_progress
            
            # 根据进度自动更新状态
            if new_progress == 0:
                module.status = ModuleStatus.NOT_STARTED
            elif new_progress == 100:
                module.status = ModuleStatus.COMPLETED
            else:
                module.status = ModuleStatus.IN_PROGRESS
            
            module.updated_at = datetime.now()
            
            # 创建模块进度记录
            progress_record = ModuleProgressRecord(
                module_id=module_id,
                progress=new_progress,
                notes=progress_data.get('notes'),
                updated_by_id=progress_data.get('updated_by_id')
            )
            
            db.session.add(progress_record)
            
            # 更新项目整体进度（基于所有模块的平均进度）
            try:
                ModuleService._update_project_progress(module.project_id)
            except Exception as e:
                print(f"更新项目进度时出错: {str(e)}")
                # 即使项目进度更新失败，也要保存模块进度
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '模块进度更新成功',
                'data': module.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'模块进度更新失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def _update_project_progress(project_id: int):
        """
        根据模块进度更新项目整体进度
        
        Args:
            project_id: 项目ID
        """
        try:
            modules = ProjectModule.query.filter_by(project_id=project_id).all()
            if not modules:
                return
            
            # 计算所有模块的平均进度
            total_progress = sum(module.progress for module in modules)
            avg_progress = round(total_progress / len(modules))
            
            # 更新项目进度
            project = Project.query.get(project_id)
            if project:
                project.progress = avg_progress
                project.updated_at = datetime.now()
                
                # 根据模块进度自动更新项目状态（仅在特定状态下）
                if avg_progress == 0 and project.status == ProjectStatus.INITIAL_CONTACT:
                    project.status = ProjectStatus.INITIAL_CONTACT  # 保持初步接触状态
                elif avg_progress == 100 and project.status == ProjectStatus.PROJECT_IMPLEMENTATION:
                    project.status = ProjectStatus.PROJECT_ACCEPTANCE  # 实施完成后进入验收
                elif avg_progress > 0 and project.status == ProjectStatus.CONTRACT_SIGNED:
                    project.status = ProjectStatus.PROJECT_IMPLEMENTATION  # 开始实施
                    
        except Exception as e:
            print(f"更新项目进度失败: {str(e)}")
    
    @staticmethod
    def assign_module_to_user(module_id: int, user_id: int) -> Dict[str, Any]:
        """
        分配模块给用户
        
        Args:
            module_id: 模块ID
            user_id: 用户ID
            
        Returns:
            分配结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 分配模块
            module.assigned_to_id = user_id
            module.updated_at = datetime.now()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '模块分配成功',
                'data': module.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'模块分配失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_module_assignee(module_id: int, assigned_to_id: Optional[int]) -> Dict[str, Any]:
        """
        更新模块负责人（支持移除）
        
        Args:
            module_id: 模块ID
            assigned_to_id: 新负责人ID，None表示移除负责人
            
        Returns:
            更新结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            # 如果指定了新负责人，检查用户是否存在
            if assigned_to_id is not None:
                user = User.query.get(assigned_to_id)
                if not user:
                    return {
                        'success': False,
                        'message': '指定的用户不存在',
                        'data': None
                    }
            
            # 更新模块负责人
            old_assignee = module.assigned_to.name if module.assigned_to else '无'
            module.assigned_to_id = assigned_to_id
            module.updated_at = datetime.now()
            
            db.session.commit()
            
            # 准备返回消息
            if assigned_to_id is None:
                message = f'已移除模块负责人（原负责人：{old_assignee}）'
            else:
                new_assignee = User.query.get(assigned_to_id).name
                message = f'模块负责人已更新为：{new_assignee}（原负责人：{old_assignee}）'
            
            return {
                'success': True,
                'message': message,
                'data': module.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新模块负责人失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_module_members(module_id: int) -> Dict[str, Any]:
        """
        获取模块成员列表
        
        Args:
            module_id: 模块ID
            
        Returns:
            模块成员列表
        """
        try:
            from backend.models.database import ModuleAssignment
            
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            # 获取模块成员分配记录
            assignments = ModuleAssignment.query.filter_by(module_id=module_id).all()
            
            members_data = []
            for assignment in assignments:
                members_data.append(assignment.to_dict())
            
            return {
                'success': True,
                'message': '获取模块成员成功',
                'data': members_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取模块成员失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def add_module_member(module_id: int, user_id: int, role: str = 'member') -> Dict[str, Any]:
        """
        添加模块成员
        
        Args:
            module_id: 模块ID
            user_id: 用户ID
            role: 成员角色
            
        Returns:
            添加结果
        """
        try:
            from backend.models.database import ModuleAssignment
            
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'data': None
                }
            
            # 检查是否已经是成员
            existing = ModuleAssignment.query.filter_by(
                module_id=module_id,
                user_id=user_id
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'message': '该用户已经是模块成员',
                    'data': None
                }
            
            # 创建成员分配记录
            assignment = ModuleAssignment(
                module_id=module_id,
                user_id=user_id,
                role=role
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'成功添加 {user.name} 为模块成员',
                'data': assignment.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'添加模块成员失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def remove_module_member(assignment_id: int) -> Dict[str, Any]:
        """
        移除模块成员
        
        Args:
            assignment_id: 分配记录ID
            
        Returns:
            移除结果
        """
        try:
            from backend.models.database import ModuleAssignment
            
            assignment = ModuleAssignment.query.get(assignment_id)
            if not assignment:
                return {
                    'success': False,
                    'message': '成员分配记录不存在',
                    'data': None
                }
            
            user_name = assignment.user.name
            
            db.session.delete(assignment)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'成功移除 {user_name} 的模块成员身份',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'移除模块成员失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_user_modules(user_id: int) -> Dict[str, Any]:
        """
        获取用户负责的所有模块
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户模块列表
        """
        try:
            modules = ProjectModule.query.filter_by(assigned_to_id=user_id)\
                .order_by(ProjectModule.priority.desc(), ProjectModule.updated_at.desc()).all()
            
            module_list = []
            for module in modules:
                module_dict = module.to_dict()
                module_dict['project_name'] = module.project.name
                module_list.append(module_dict)
            
            return {
                'success': True,
                'message': '获取用户模块成功',
                'data': module_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取用户模块失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def get_module_detail(module_id: int) -> Dict[str, Any]:
        """
        获取模块详情
        
        Args:
            module_id: 模块ID
            
        Returns:
            模块详情
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            module_dict = module.to_dict()
            
            # 添加进度历史
            progress_history = []
            for record in module.progress_records:
                progress_history.append(record.to_dict())
            module_dict['progress_history'] = sorted(progress_history, key=lambda x: x['updated_at'], reverse=True)
            
            # 添加项目信息
            module_dict['project'] = module.project.to_dict()
            
            return {
                'success': True,
                'message': '获取模块详情成功',
                'data': module_dict
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取模块详情失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_all_modules_overview() -> Dict[str, Any]:
        """
        获取所有项目的模块概览
        
        Returns:
            所有项目及其模块信息
        """
        try:
            # 获取所有项目及其模块
            projects = Project.query.all()
            
            projects_with_modules = []
            for project in projects:
                project_dict = project.to_dict()
                
                # 使用新的进度计算逻辑
                from .project_service import ProjectService
                progress_info = ProjectService.calculate_project_progress(project)
                project_dict['progress'] = progress_info['progress']  # 使用实时计算的进度
                project_dict['progress_type'] = progress_info.get('type', 'unknown')
                project_dict['progress_info'] = progress_info.get('info', '')
                
                # 获取项目模块
                modules = ProjectModule.query.filter_by(project_id=project.id)\
                    .order_by(ProjectModule.priority.desc(), ProjectModule.created_at).all()
                
                module_list = []
                for module in modules:
                    module_dict = module.to_dict()
                    
                    # 添加分配的用户列表
                    assignments = ModuleAssignment.query.filter_by(module_id=module.id).all()
                    assigned_users = []
                    for assignment in assignments:
                        if assignment.user:
                            assigned_users.append({
                                'id': assignment.user.id,
                                'name': assignment.user.name,
                                'position': assignment.user.position,
                                'role': assignment.role
                            })
                    module_dict['assigned_users'] = assigned_users
                    
                    # 添加最近2条工作记录
                    recent_works = ModuleWorkRecord.query.filter_by(module_id=module.id)\
                        .order_by(desc(ModuleWorkRecord.week_start)).limit(2).all()
                    
                    recent_works_list = []
                    for work in recent_works:
                        week_label = f"{work.week_start.strftime('%m/%d')} - {work.week_end.strftime('%m/%d')}" if work.week_start and work.week_end else None
                        recent_works_list.append({
                            'week_label': week_label,
                            'work_content': work.work_content,
                            'achievements': work.achievements,
                            'created_by': work.created_by.name if work.created_by else None,
                            'updated_at': work.updated_at.isoformat()
                        })
                    
                    module_dict['recent_works'] = recent_works_list
                    # 保留latest_work以保持向后兼容
                    module_dict['latest_work'] = recent_works_list[0] if recent_works_list else None
                    
                    # 添加最新进度记录
                    latest_record = ModuleProgressRecord.query.filter_by(module_id=module.id)\
                        .order_by(desc(ModuleProgressRecord.updated_at)).first()
                    if latest_record:
                        module_dict['latest_update'] = {
                            'progress': latest_record.progress,
                            'notes': latest_record.notes,
                            'updated_by': latest_record.updated_by.name,
                            'updated_at': latest_record.updated_at.isoformat()
                        }
                    
                    module_list.append(module_dict)
                
                project_dict['modules'] = module_list
                project_dict['module_count'] = len(module_list)
                
                # 计算项目模块统计
                if module_list:
                    completed_modules = [m for m in module_list if m['progress'] == 100]
                    in_progress_modules = [m for m in module_list if 0 < m['progress'] < 100]
                    pending_modules = [m for m in module_list if m['progress'] == 0]
                    
                    project_dict['module_stats'] = {
                        'total': len(module_list),
                        'completed': len(completed_modules),
                        'in_progress': len(in_progress_modules),
                        'pending': len(pending_modules)
                    }
                else:
                    project_dict['module_stats'] = {
                        'total': 0,
                        'completed': 0,
                        'in_progress': 0,
                        'pending': 0
                    }
                
                projects_with_modules.append(project_dict)
            
            return {
                'success': True,
                'message': '获取模块概览成功',
                'data': projects_with_modules
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取模块概览失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def add_work_record(module_id: int, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加模块工作记录
        
        Args:
            module_id: 模块ID
            work_data: 工作记录数据
            
        Returns:
            添加结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            # 解析周期
            week_start = datetime.strptime(work_data.get('week_start'), '%Y-%m-%d').date()
            week_end = datetime.strptime(work_data.get('week_end'), '%Y-%m-%d').date()
            
            # 检查是否已存在重叠的周期记录
            # 重叠条件：新记录的开始日期小于等于现有记录的结束日期 且 新记录的结束日期大于等于现有记录的开始日期
            overlapping_record = ModuleWorkRecord.query.filter(
                ModuleWorkRecord.module_id == module_id,
                ModuleWorkRecord.week_start <= week_end,
                ModuleWorkRecord.week_end >= week_start
            ).first()
            
            if overlapping_record:
                return {
                    'success': False,
                    'message': f'该周期与现有工作记录重叠 ({overlapping_record.week_start} 至 {overlapping_record.week_end})',
                    'data': None
                }
            
            # 创建工作记录
            work_record = ModuleWorkRecord(
                module_id=module_id,
                week_start=week_start,
                week_end=week_end,
                work_content=work_data.get('work_content'),
                achievements=work_data.get('achievements'),
                issues=work_data.get('issues'),
                next_week_plan=work_data.get('next_week_plan'),
                created_by_id=work_data.get('created_by_id')
            )
            
            db.session.add(work_record)
            db.session.commit()
            
            return {
                'success': True,
                'message': '工作记录添加成功',
                'data': work_record.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'添加工作记录失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_module_work_records(module_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        获取模块工作记录
        
        Args:
            module_id: 模块ID
            limit: 返回记录数限制
            
        Returns:
            工作记录列表
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': []
                }
            
            # 获取工作记录，按时间倒序
            work_records = ModuleWorkRecord.query.filter_by(module_id=module_id)\
                .order_by(desc(ModuleWorkRecord.week_start))\
                .limit(limit).all()
            
            records_data = [record.to_dict() for record in work_records]
            
            return {
                'success': True,
                'message': '获取工作记录成功',
                'data': records_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取工作记录失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def update_work_record(record_id: int, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新工作记录（部门主管专用）
        
        Args:
            record_id: 工作记录ID
            work_data: 更新的数据
            
        Returns:
            更新结果
        """
        try:
            work_record = ModuleWorkRecord.query.get(record_id)
            if not work_record:
                return {
                    'success': False,
                    'message': '工作记录不存在',
                    'data': None
                }
            
            # 更新字段
            if 'week_start' in work_data:
                work_record.week_start = datetime.strptime(work_data['week_start'], '%Y-%m-%d').date()
            if 'week_end' in work_data:
                work_record.week_end = datetime.strptime(work_data['week_end'], '%Y-%m-%d').date()
            if 'work_content' in work_data:
                work_record.work_content = work_data['work_content']
            if 'achievements' in work_data:
                work_record.achievements = work_data['achievements']
            if 'issues' in work_data:
                work_record.issues = work_data['issues']
            if 'next_week_plan' in work_data:
                work_record.next_week_plan = work_data['next_week_plan']
            
            work_record.updated_at = datetime.now()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '工作记录更新成功',
                'data': work_record.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新工作记录失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def delete_work_record(record_id: int) -> Dict[str, Any]:
        """
        删除工作记录（部门主管专用）
        
        Args:
            record_id: 工作记录ID
            
        Returns:
            删除结果
        """
        try:
            work_record = ModuleWorkRecord.query.get(record_id)
            if not work_record:
                return {
                    'success': False,
                    'message': '工作记录不存在',
                    'data': None
                }
            
            db.session.delete(work_record)
            db.session.commit()
            
            return {
                'success': True,
                'message': '工作记录删除成功',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除工作记录失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_latest_work_content(module_id: int) -> Dict[str, Any]:
        """
        获取模块最新工作内容
        
        Args:
            module_id: 模块ID
            
        Returns:
            最新工作内容
        """
        try:
            # 获取最新的工作记录
            latest_record = ModuleWorkRecord.query.filter_by(module_id=module_id)\
                .order_by(desc(ModuleWorkRecord.week_start)).first()
            
            if not latest_record:
                return {
                    'success': True,
                    'message': '暂无工作记录',
                    'data': None
                }
            
            return {
                'success': True,
                'message': '获取最新工作内容成功',
                'data': latest_record.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取最新工作内容失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def assign_users_to_module(module_id: int, user_ids: List[int]) -> Dict[str, Any]:
        """
        为模块分配多个用户
        
        Args:
            module_id: 模块ID
            user_ids: 用户ID列表
            
        Returns:
            分配结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            # 清除现有分配
            ModuleAssignment.query.filter_by(module_id=module_id).delete()
            
            # 添加新分配
            for user_id in user_ids:
                user = User.query.get(user_id)
                if user:
                    assignment = ModuleAssignment(
                        module_id=module_id,
                        user_id=user_id,
                        role='member'
                    )
                    db.session.add(assignment)
            
            # 保持原有的assigned_to_id字段兼容性（设置为第一个用户）
            if user_ids:
                module.assigned_to_id = user_ids[0]
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '用户分配成功',
                'data': module.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'用户分配失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_current_week_dates():
        """
        获取当前周的开始和结束日期
        
        Returns:
            (week_start, week_end) 元组
        """
        today = date.today()
        # 获取本周一
        week_start = today - timedelta(days=today.weekday())
        # 获取本周日
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    @staticmethod
    def get_all_modules_overview():
        """
        获取所有项目的模块概览
        
        Returns:
            包含所有项目模块信息的字典
        """
        try:
            from backend.models.database import Project, ProjectModule, User, ProjectMember, ProjectMemberRole, ModuleWorkRecord, ModuleAssignment
            from sqlalchemy import desc
            
            projects = Project.query.all()
            projects_data = []
            
            for project in projects:
                modules = ProjectModule.query.filter_by(project_id=project.id).all()
                modules_data = []
                
                for module in modules:
                    module_dict = module.to_dict()
                    
                    # 添加分配的用户列表
                    assignments = ModuleAssignment.query.filter_by(module_id=module.id).all()
                    assigned_users = []
                    for assignment in assignments:
                        if assignment.user:
                            assigned_users.append({
                                'id': assignment.user.id,
                                'name': assignment.user.name,
                                'position': assignment.user.position,
                                'role': assignment.role
                            })
                    module_dict['assigned_users'] = assigned_users
                    
                    # 添加最近2条工作记录
                    recent_works = ModuleWorkRecord.query.filter_by(module_id=module.id)\
                        .order_by(desc(ModuleWorkRecord.week_start)).limit(2).all()
                    
                    recent_works_list = []
                    for work in recent_works:
                        week_label = f"{work.week_start.strftime('%m/%d')} - {work.week_end.strftime('%m/%d')}" if work.week_start and work.week_end else None
                        recent_works_list.append({
                            'week_label': week_label,
                            'work_content': work.work_content,
                            'achievements': work.achievements,
                            'created_by': work.created_by.name if work.created_by else None,
                            'updated_at': work.updated_at.isoformat()
                        })
                    
                    module_dict['recent_works'] = recent_works_list
                    # 保留latest_work以保持向后兼容
                    module_dict['latest_work'] = recent_works_list[0] if recent_works_list else None
                        
                    modules_data.append(module_dict)
                
                project_dict = project.to_dict()
                
                # 使用新的进度计算逻辑
                from .project_service import ProjectService
                progress_info = ProjectService.calculate_project_progress(project)
                project_dict['progress'] = progress_info['progress']  # 使用实时计算的进度
                project_dict['progress_type'] = progress_info.get('type', 'unknown')
                project_dict['progress_info'] = progress_info.get('info', '')
                
                project_dict['modules'] = modules_data
                
                # 添加项目成员信息
                members = []
                for member in project.members:
                    member_info = {
                        'id': member.user.id,
                        'user_id': member.user.id,
                        'name': member.user.name,
                        'role': member.role.value,
                        'position': member.user.position
                    }
                    members.append(member_info)
                
                project_dict['members'] = members
                
                # 添加项目负责人信息
                project_leader = ProjectMember.query.filter_by(
                    project_id=project.id, 
                    role=ProjectMemberRole.LEADER
                ).first()
                
                if project_leader and project_leader.user:
                    project_dict['leader'] = project_leader.user.to_dict()
                else:
                    project_dict['leader'] = None
                
                projects_data.append(project_dict)
            
            return {
                'success': True,
                'message': '获取模块概览成功',
                'data': projects_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取模块概览失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def get_modules_overview_by_projects(project_ids):
        """
        根据项目ID列表获取模块概览
        
        Args:
            project_ids (list): 项目ID列表
            
        Returns:
            包含指定项目模块信息的字典
        """
        try:
            if not project_ids:
                return {
                    'success': True,
                    'message': '获取模块概览成功',
                    'data': []
                }
            
            from backend.models.database import Project, ProjectModule, User, ProjectMember, ProjectMemberRole, ModuleWorkRecord, ModuleAssignment
            from sqlalchemy import desc
            
            projects = Project.query.filter(Project.id.in_(project_ids)).all()
            projects_data = []
            
            for project in projects:
                modules = ProjectModule.query.filter_by(project_id=project.id).all()
                modules_data = []
                
                for module in modules:
                    module_dict = module.to_dict()
                    
                    # 添加分配的用户列表
                    assignments = ModuleAssignment.query.filter_by(module_id=module.id).all()
                    assigned_users = []
                    for assignment in assignments:
                        if assignment.user:
                            assigned_users.append({
                                'id': assignment.user.id,
                                'name': assignment.user.name,
                                'position': assignment.user.position,
                                'role': assignment.role
                            })
                    module_dict['assigned_users'] = assigned_users
                    
                    # 添加最近2条工作记录
                    recent_works = ModuleWorkRecord.query.filter_by(module_id=module.id)\
                        .order_by(desc(ModuleWorkRecord.week_start)).limit(2).all()
                    
                    recent_works_list = []
                    for work in recent_works:
                        week_label = f"{work.week_start.strftime('%m/%d')} - {work.week_end.strftime('%m/%d')}" if work.week_start and work.week_end else None
                        recent_works_list.append({
                            'week_label': week_label,
                            'work_content': work.work_content,
                            'achievements': work.achievements,
                            'created_by': work.created_by.name if work.created_by else None,
                            'updated_at': work.updated_at.isoformat()
                        })
                    
                    module_dict['recent_works'] = recent_works_list
                    # 保留latest_work以保持向后兼容
                    module_dict['latest_work'] = recent_works_list[0] if recent_works_list else None
                        
                    modules_data.append(module_dict)
                
                project_dict = project.to_dict()
                
                # 使用新的进度计算逻辑
                from .project_service import ProjectService
                progress_info = ProjectService.calculate_project_progress(project)
                project_dict['progress'] = progress_info['progress']  # 使用实时计算的进度
                project_dict['progress_type'] = progress_info.get('type', 'unknown')
                project_dict['progress_info'] = progress_info.get('info', '')
                
                project_dict['modules'] = modules_data
                
                # 添加项目成员信息
                members = []
                for member in project.members:
                    member_info = {
                        'id': member.user.id,
                        'user_id': member.user.id,
                        'name': member.user.name,
                        'role': member.role.value,
                        'position': member.user.position
                    }
                    members.append(member_info)
                
                project_dict['members'] = members
                
                # 添加项目负责人信息
                project_leader = ProjectMember.query.filter_by(
                    project_id=project.id, 
                    role=ProjectMemberRole.LEADER
                ).first()
                
                if project_leader and project_leader.user:
                    project_dict['leader'] = project_leader.user.to_dict()
                else:
                    project_dict['leader'] = None
                
                projects_data.append(project_dict)
            
            return {
                'success': True,
                'message': '获取模块概览成功',
                'data': projects_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取模块概览失败: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def delete_module(module_id: int) -> Dict[str, Any]:
        """
        删除模块
        
        Args:
            module_id: 模块ID
            
        Returns:
            删除结果
        """
        try:
            module = ProjectModule.query.get(module_id)
            if not module:
                return {
                    'success': False,
                    'message': '模块不存在',
                    'data': None
                }
            
            project_id = module.project_id
            
            # 删除相关数据
            # 1. 删除模块分配记录
            ModuleAssignment.query.filter_by(module_id=module_id).delete()
            
            # 2. 删除模块进度记录
            ModuleProgressRecord.query.filter_by(module_id=module_id).delete()
            
            # 3. 删除模块工作记录
            ModuleWorkRecord.query.filter_by(module_id=module_id).delete()
            
            # 4. 删除模块本身
            db.session.delete(module)
            db.session.commit()
            
            # 5. 更新项目进度（删除模块后重新计算）
            try:
                ModuleService._update_project_progress(project_id)
                db.session.commit()
            except Exception as e:
                print(f"更新项目进度时出错: {str(e)}")
                # 不影响模块删除的成功
            
            return {
                'success': True,
                'message': '模块删除成功',
                'data': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'模块删除失败: {str(e)}',
                'data': None
            }
