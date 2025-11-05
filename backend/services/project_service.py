"""
项目服务层 - 项目相关的业务逻辑
遵循DDD分层架构，处理项目管理的核心业务逻辑
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date
from sqlalchemy import and_, or_, desc
from ..models.database import db, Project, ProjectMember, ProgressRecord, User, ProjectStatus, ProjectMemberRole, ProjectModule, ModuleAssignment, ModuleWorkRecord

class ProjectService:
    """项目服务类 - 处理项目相关的业务逻辑"""
    
    # 状态阶段进度映射表
    STATE_STAGE_PROGRESS = {
        'initial_contact': {'stage': 1, 'progress': 5, 'label': '初步接触'},
        'proposal_submitted': {'stage': 2, 'progress': 15, 'label': '提交方案'},
        'quotation_submitted': {'stage': 3, 'progress': 20, 'label': '提交报价'},
        'user_confirmation': {'stage': 4, 'progress': 25, 'label': '用户确认'},
        'contract_signed': {'stage': 5, 'progress': 35, 'label': '合同签订'},
        'project_implementation': {'stage': 6, 'progress': None, 'label': '项目实施'},
        'project_acceptance': {'stage': 7, 'progress': 100, 'label': '项目验收'},
        'warranty_period': {'stage': 8, 'progress': None, 'label': '维保期内'},
        'post_warranty': {'stage': 9, 'progress': 100, 'label': '维保完成'},
        'no_follow_up': {'stage': 0, 'progress': 0, 'label': '已终止'},
        # 纵向项目状态
        'vertical_declaration': {'stage': 1, 'progress': 25, 'label': '申报阶段'},
        'vertical_review': {'stage': 2, 'progress': 50, 'label': '审核阶段'},
        'vertical_approved': {'stage': 3, 'progress': 100, 'label': '审核通过'},
        'vertical_rejected': {'stage': 0, 'progress': 0, 'label': '审核未通过'},
    }
    
    @staticmethod
    def get_progress_limits(status: str) -> Dict[str, int]:
        """
        获取状态对应的进度范围
        
        Args:
            status: 项目状态
            
        Returns:
            进度范围 {min, max, default, stage}
        """
        LIMITS = {
            'initial_contact': {'min': 0, 'max': 5, 'default': 5, 'stage': 1, 'label': '初步接触'},
            'proposal_submitted': {'min': 5, 'max': 15, 'default': 15, 'stage': 2, 'label': '提交方案'},
            'quotation_submitted': {'min': 15, 'max': 20, 'default': 20, 'stage': 3, 'label': '提交报价'},
            'user_confirmation': {'min': 20, 'max': 25, 'default': 25, 'stage': 4, 'label': '用户确认'},
            'contract_signed': {'min': 25, 'max': 35, 'default': 35, 'stage': 5, 'label': '合同签订'}
        }
        return LIMITS.get(status, {'min': 0, 'max': 100, 'default': 0, 'stage': 0, 'label': '未知'})
    
    @staticmethod
    def calculate_project_progress(project) -> Dict[str, Any]:
        """
        计算项目进度（新版本 - 支持模块映射和手动进度）
        
        优先级：
        1. 如果有模块 → 基于模块进度计算
        2. 如果没有模块但有手动进度 → 使用手动进度
        3. 否则 → 使用状态默认进度
        
        Args:
            project: 项目对象
            
        Returns:
            进度信息字典 {progress: int, type: str, info: str, ...}
        """
        status = project.status.value if hasattr(project.status, 'value') else project.status
        project_source = project.project_source
        manual_progress = getattr(project, 'manual_progress', None)
        
        # 获取项目的所有模块
        modules = ProjectModule.query.filter_by(project_id=project.id).all()
        has_modules = len(modules) > 0
        
        # 纵向项目：使用状态阶段进度
        if project_source == 'vertical':
            stage_info = ProjectService.STATE_STAGE_PROGRESS.get(status, {'progress': 0, 'label': '未知', 'stage': 0})
            return {
                'progress': stage_info['progress'],
                'type': 'stage',
                'stage': stage_info['stage'],
                'label': stage_info['label'],
                'info': '纵向项目阶段进度',
                'source': 'status'
            }
        
        # 项目验收阶段：85-90%，基于模块映射
        if status == 'project_acceptance':
            if has_modules:
                # 计算模块平均进度
                total_progress = sum(module.progress for module in modules)
                avg_module_progress = total_progress / len(modules)
                
                # 将模块进度（0-100%）映射到验收阶段范围（85-90%）
                # 公式：85 + (模块平均 / 100 × 5)
                mapped_progress = 85 + (avg_module_progress / 100 * 5)
                progress = round(mapped_progress)
                
                return {
                    'progress': progress,
                    'type': 'acceptance',
                    'module_count': len(modules),
                    'avg_module_progress': round(avg_module_progress),
                    'label': '项目验收',
                    'info': f'验收阶段，基于 {len(modules)} 个模块（平均 {round(avg_module_progress)}%），映射到 85-90%',
                    'source': 'modules',
                    'detail': {
                        'stage': 7,
                        'total_stages': 9,
                        'range': '85-90%'
                    }
                }
            else:
                # 没有模块，使用默认值（范围中点）
                return {
                    'progress': 88,
                    'type': 'acceptance',
                    'label': '项目验收',
                    'info': '验收阶段（未设置模块）',
                    'source': 'default'
                }
        
        if status == 'warranty_period':
            if has_modules:
                # 维保期内：90-100%，基于模块映射
                total_progress = sum(module.progress for module in modules)
                avg_module_progress = total_progress / len(modules)
                
                # 将模块进度（0-100%）映射到维保阶段范围（90-100%）
                # 公式：90 + (模块平均 / 100 × 10)
                mapped_progress = 90 + (avg_module_progress / 100 * 10)
                progress = round(mapped_progress)
                
                return {
                    'progress': progress,
                    'type': 'warranty',
                    'module_count': len(modules),
                    'avg_module_progress': round(avg_module_progress),
                    'label': '维保期内',
                    'info': f'维保期内，基于 {len(modules)} 个模块（平均 {round(avg_module_progress)}%），映射到 90-100%',
                    'source': 'modules',
                    'detail': {
                        'stage': 8,
                        'total_stages': 9,
                        'range': '90-100%'
                    }
                }
            else:
                # 没有模块，使用默认值（范围中点）
                return {
                    'progress': 95,
                    'type': 'warranty',
                    'label': '维保期内',
                    'info': '维保期内（未设置模块）',
                    'source': 'default'
                }
        
        if status == 'post_warranty':
            return {
                'progress': 100,
                'type': 'completed',
                'label': '维保完成',
                'info': '项目已完成',
                'source': 'status'
            }
        
        if status == 'no_follow_up':
            return {
                'progress': 0,
                'type': 'terminated',
                'label': '已终止',
                'info': '项目已终止跟进',
                'source': 'status'
            }
        
        # 项目实施阶段：35-85%，基于模块映射
        if status == 'project_implementation':
            if has_modules:
                # 计算模块平均进度
                total_progress = sum(module.progress for module in modules)
                avg_module_progress = total_progress / len(modules)
                
                # 将模块进度（0-100%）映射到项目实施范围（35-85%）
                # 公式：35 + (模块平均 / 100 × 50)
                mapped_progress = 35 + (avg_module_progress / 100 * 50)
                final_progress = round(mapped_progress)
                
                return {
                    'progress': final_progress,
                    'type': 'implementation',
                    'module_count': len(modules),
                    'avg_module_progress': round(avg_module_progress),
                    'info': f'项目实施，基于 {len(modules)} 个模块（平均 {round(avg_module_progress)}%），映射到 35-85%',
                    'source': 'modules',
                    'detail': {
                        'stage': 6,
                        'total_stages': 9,
                        'range': '35-85%'
                    }
                }
            else:
                # 没有模块，使用默认值（范围中点）
                return {
                    'progress': 60,
                    'type': 'implementation',
                    'info': '项目实施中（未设置模块）',
                    'module_count': 0,
                    'source': 'default'
                }
        
        # 前期阶段：优先级 模块 > 手动 > 默认
        if status in ['initial_contact', 'proposal_submitted', 'quotation_submitted',
                      'user_confirmation', 'contract_signed']:
            
            limits = ProjectService.get_progress_limits(status)
            
            # 优先级1：如果有模块，基于模块进度映射到阶段范围
            if has_modules:
                total_progress = sum(module.progress for module in modules)
                avg_module_progress = total_progress / len(modules)
                
                # 将模块进度映射到当前阶段的范围
                # 公式：阶段下限 + (模块平均 / 100 × 阶段范围)
                range_size = limits['max'] - limits['min']
                mapped_progress = limits['min'] + (avg_module_progress / 100 * range_size)
                
                return {
                    'progress': round(mapped_progress),
                    'type': 'stage_with_modules',
                    'stage': limits['stage'],
                    'total_stages': 7,
                    'module_count': len(modules),
                    'avg_module_progress': round(avg_module_progress),
                    'label': limits['label'],
                    'info': f'基于 {len(modules)} 个模块，映射到阶段范围 {limits["min"]}-{limits["max"]}%',
                    'source': 'modules'
                }
            
            # 优先级2：如果有手动进度，使用手动进度
            if manual_progress is not None:
                # 验证范围
                if manual_progress < limits['min'] or manual_progress > limits['max']:
                    # 超出范围，使用默认值
                    return {
                        'progress': limits['default'],
                        'type': 'stage',
                        'stage': limits['stage'],
                        'total_stages': 7,
                        'label': limits['label'],
                        'info': f'手动进度超出范围，使用默认进度',
                        'source': 'default',
                        'error': f'手动进度 {manual_progress}% 超出范围 {limits["min"]}-{limits["max"]}%'
                    }
                
                return {
                    'progress': manual_progress,
                    'type': 'stage_manual',
                    'stage': limits['stage'],
                    'total_stages': 7,
                    'label': limits['label'],
                    'info': '手动设置',
                    'source': 'manual'
                }
            
            # 优先级3：使用默认进度
            return {
                'progress': limits['default'],
                'type': 'stage',
                'stage': limits['stage'],
                'total_stages': 7,
                'label': limits['label'],
                'info': '阶段默认进度',
                'source': 'default'
            }
        
        # 默认
        return {
            'progress': 0,
            'type': 'unknown',
            'info': '未知状态',
            'source': 'error'
        }
    
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
            project_source = project_data.get('project_source', 'horizontal')
            
            # 创建项目对象
            project = Project(
                name=project_data.get('name'),
                description=project_data.get('description'),
                start_date=datetime.strptime(project_data.get('start_date'), '%Y-%m-%d').date() if project_data.get('start_date') else None,
                end_date=datetime.strptime(project_data.get('end_date'), '%Y-%m-%d').date() if project_data.get('end_date') else None,
                status=ProjectStatus(project_data.get('status', 'planning')),
                project_source=project_source,  # 项目来源，默认横向
                partner=project_data.get('partner'),  # 合作方（可选）
                contract_amount=project_data.get('contract_amount'),  # 合同金额（可选）
                received_amount=project_data.get('received_amount'),  # 到账金额（可选）
                progress=0 if project_source == 'vertical' else project_data.get('progress', 0)  # 纵向项目进度固定为0
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
                
                # 从模块中收集真实的项目成员（去重）
                module_members = {}
                project_modules = ProjectModule.query.filter_by(project_id=project.id).all()
                for module in project_modules:
                    # 获取模块分配的成员
                    assignments = ModuleAssignment.query.filter_by(module_id=module.id).all()
                    for assignment in assignments:
                        user = assignment.user
                        if user.id not in module_members:
                            module_members[user.id] = {
                                'id': user.id,
                                'name': user.name,
                                'position': user.position
                            }
                
                project_dict['members'] = members
                project_dict['leaders'] = leaders
                # 成员数量使用从模块中收集的实际成员数
                project_dict['member_count'] = len(module_members)
                
                # 计算项目进度（使用新的三层进度体系）
                progress_info = ProjectService.calculate_project_progress(project)
                project_dict['progress'] = progress_info['progress']
                project_dict['progress_type'] = progress_info['type']
                project_dict['progress_info'] = progress_info.get('info', '')
                project_dict['progress_detail'] = progress_info  # 完整的进度信息
                
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
            
            # 计算项目进度（使用新的三层进度体系）
            progress_info = ProjectService.calculate_project_progress(project)
            project_dict['progress'] = progress_info['progress']
            project_dict['progress_type'] = progress_info['type']
            project_dict['progress_info'] = progress_info.get('info', '')
            project_dict['progress_detail'] = progress_info  # 完整的进度信息
            
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
            
            if 'start_date' in project_data:
                # 如果日期为空（None, null, 空字符串），则清空日期
                if project_data['start_date']:
                    project.start_date = datetime.strptime(project_data['start_date'], '%Y-%m-%d').date()
                else:
                    project.start_date = None
            
            if 'end_date' in project_data:
                # 如果日期为空（None, null, 空字符串），则清空日期
                if project_data['end_date']:
                    project.end_date = datetime.strptime(project_data['end_date'], '%Y-%m-%d').date()
                else:
                    project.end_date = None
            
            if 'status' in project_data:
                project.status = ProjectStatus(project_data['status'])
            
            if 'project_source' in project_data:
                project.project_source = project_data['project_source']
            
            if 'partner' in project_data:
                # 合作方可以为空字符串或None
                project.partner = project_data['partner'] if project_data['partner'] else None
            
            if 'contract_amount' in project_data:
                # 金额可以为None（表示未设置）
                project.contract_amount = project_data['contract_amount']
            
            if 'received_amount' in project_data:
                # 金额可以为None（表示未设置）
                project.received_amount = project_data['received_amount']
            
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
            
            # 手动删除关联数据（避免外键约束错误）
            # 1. 获取项目的所有模块
            modules = ProjectModule.query.filter_by(project_id=project_id).all()
            
            # 2. 删除每个模块的关联数据
            for module in modules:
                # 删除模块分配记录
                ModuleAssignment.query.filter_by(module_id=module.id).delete()
                # 删除模块工作记录
                ModuleWorkRecord.query.filter_by(module_id=module.id).delete()
                # 删除模块进度记录会被级联删除（已配置cascade）
            
            # 3. 删除项目成员记录
            ProjectMember.query.filter_by(project_id=project_id).delete()
            
            # 4. 删除项目进度记录
            ProgressRecord.query.filter_by(project_id=project_id).delete()
            
            # 5. 删除项目本身（会级联删除模块）
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
            
            # 纵向项目不允许更新进度
            if project.project_source == 'vertical':
                return {
                    'success': False,
                    'message': '纵向项目没有进度概念，不允许更新进度',
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
    def update_manual_progress(project_id: int, progress: int) -> Dict[str, Any]:
        """
        更新项目的手动进度
        仅适用于前期阶段（初步接触 → 合同签订）
        
        Args:
            project_id: 项目ID
            progress: 手动进度值（0-100）
            
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
            
            status = project.status.value if hasattr(project.status, 'value') else project.status
            
            # 检查是否允许手动设置进度
            allowed_statuses = ['initial_contact', 'proposal_submitted', 
                              'quotation_submitted', 'user_confirmation', 
                              'contract_signed']
            
            if status not in allowed_statuses:
                return {
                    'success': False,
                    'message': f'当前状态不允许手动设置进度',
                    'data': None
                }
            
            # 获取进度范围限制
            limits = ProjectService.get_progress_limits(status)
            
            # 验证进度范围
            if progress < limits['min']:
                return {
                    'success': False,
                    'message': f'进度不能低于 {limits["min"]}%（前一阶段上限）',
                    'data': {'min': limits['min'], 'max': limits['max']}
                }
            
            if progress > limits['max']:
                return {
                    'success': False,
                    'message': f'进度不能超过 {limits["max"]}%（当前阶段上限）',
                    'data': {'min': limits['min'], 'max': limits['max']}
                }
            
            # 更新手动进度
            project.manual_progress = progress
            project.updated_at = datetime.now()
            
            db.session.commit()
            
            # 重新计算项目进度
            progress_info = ProjectService.calculate_project_progress(project)
            
            return {
                'success': True,
                'message': f'进度已更新为 {progress}%',
                'data': {
                    'manual_progress': progress,
                    'calculated_progress': progress_info['progress'],
                    'limits': limits,
                    'info': progress_info.get('info', '')
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新进度失败: {str(e)}',
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
                # 使用新的进度计算逻辑
                progress_info = ProjectService.calculate_project_progress(project)
                current_progress = progress_info['progress']
                
                if project.status not in [ProjectStatus.NO_FOLLOW_UP]:
                    total_progress += current_progress
                    active_projects += 1
                
                # 获取项目负责人
                leaders = [member.user.name for member in project.members 
                          if member.role == ProjectMemberRole.LEADER]
                
                project_info = {
                    'id': project.id,
                    'name': project.name,
                    'status': project.status.value,
                    'progress': current_progress,  # 使用计算后的进度
                    'progress_type': progress_info.get('type', 'unknown'),  # 进度类型
                    'progress_info': progress_info.get('info', ''),  # 进度说明
                    'leaders': leaders,
                    'member_count': len(project.members),
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'end_date': project.end_date.isoformat() if project.end_date else None,
                    'project_source': project.project_source,  # 添加项目来源
                    'partner': project.partner,  # 添加合作方
                    'contract_amount': project.contract_amount,  # 合同金额
                    'received_amount': project.received_amount,  # 到账金额
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
