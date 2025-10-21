"""
模块控制器 - 处理项目模块相关的HTTP请求
遵循DDD分层架构，作为表现层处理模块API请求
"""

from flask import Blueprint, request, jsonify
from ..services.module_service import ModuleService
from ..utils.decorators import login_required, permission_required
from ..models.database import UserRole

# 创建模块蓝图
module_bp = Blueprint('module', __name__, url_prefix='/api/modules')

@module_bp.route('/projects/<int:project_id>', methods=['POST'])
def create_module(project_id):
    """创建项目模块"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': '模块名称不能为空',
                'data': None
            }), 400
        
        result = ModuleService.create_module(project_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建模块时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project_modules(project_id):
    """获取项目的所有模块"""
    try:
        result = ModuleService.get_project_modules(project_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取项目模块时发生错误: {str(e)}',
            'data': []
        }), 500

@module_bp.route('/<int:module_id>', methods=['GET'])
def get_module_detail(module_id):
    """获取模块详情"""
    try:
        result = ModuleService.get_module_detail(module_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模块详情时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/progress', methods=['PUT'])
@login_required
def update_module_progress(module_id):
    """更新模块进度"""
    try:
        # 权限检查
        current_user = request.current_user
        from ..services.auth_service import AuthService
        
        # 检查用户是否有权限更新此模块
        if current_user.role == UserRole.DEPARTMENT_MANAGER:
            # 部门主管可以更新所有模块，无需额外检查
            pass
        else:
            # 普通成员需要检查模块权限
            if not AuthService.has_module_permission(current_user, module_id, 'update_module'):
                return jsonify({
                    'success': False,
                    'message': '没有权限更新此模块'
                }), 403
        
        data = request.get_json()
        
        # 验证进度值
        if 'progress' not in data:
            return jsonify({
                'success': False,
                'message': '进度值不能为空',
                'data': None
            }), 400
        
        progress = data.get('progress')
        if not isinstance(progress, int) or progress < 0 or progress > 100:
            return jsonify({
                'success': False,
                'message': '进度值必须是0-100之间的整数',
                'data': None
            }), 400
        
        # 自动设置更新人为当前用户
        data['updated_by_id'] = current_user.id
        
        result = ModuleService.update_module_progress(module_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新模块进度时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/assign', methods=['PUT'])
def assign_module(module_id):
    """分配模块给用户"""
    try:
        data = request.get_json()
        
        # 验证用户ID
        if 'user_id' not in data:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空',
                'data': None
            }), 400
        
        result = ModuleService.assign_module_to_user(module_id, data['user_id'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分配模块时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/assignee', methods=['PUT'])
@login_required
def update_module_assignee(module_id):
    """更新模块负责人（支持移除）"""
    try:
        data = request.get_json()
        
        # assigned_to_id 可以为 null（移除负责人）
        assigned_to_id = data.get('assigned_to_id')
        
        result = ModuleService.update_module_assignee(module_id, assigned_to_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新模块负责人时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_modules(user_id):
    """获取用户负责的所有模块"""
    try:
        result = ModuleService.get_user_modules(user_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户模块时发生错误: {str(e)}',
            'data': []
        }), 500

@module_bp.route('/overview', methods=['GET'])
@login_required
def get_modules_overview():
    """获取所有项目的模块概览"""
    try:
        # 根据用户角色过滤数据
        current_user = request.current_user
        if current_user.role != UserRole.DEPARTMENT_MANAGER:
            # 非部门主管只能看到自己参与的项目的模块
            from ..services.auth_service import AuthService
            accessible_project_ids = AuthService.get_user_projects(current_user)
            result = ModuleService.get_modules_overview_by_projects(accessible_project_ids)
        else:
            result = ModuleService.get_all_modules_overview()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模块概览时发生错误: {str(e)}',
            'data': []
        }), 500

@module_bp.route('/<int:module_id>/work-records', methods=['POST'])
def add_work_record(module_id):
    """添加模块工作记录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['week_start', 'week_end', 'work_content', 'created_by_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} 不能为空',
                    'data': None
                }), 400
        
        result = ModuleService.add_work_record(module_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加工作记录时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/work-records', methods=['GET'])
def get_module_work_records(module_id):
    """获取模块工作记录"""
    try:
        limit = request.args.get('limit', 10, type=int)
        result = ModuleService.get_module_work_records(module_id, limit)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取工作记录时发生错误: {str(e)}',
            'data': []
        }), 500

@module_bp.route('/<int:module_id>/latest-work', methods=['GET'])
def get_latest_work_content(module_id):
    """获取模块最新工作内容"""
    try:
        result = ModuleService.get_latest_work_content(module_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取最新工作内容时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/assign-users', methods=['PUT'])
def assign_users_to_module(module_id):
    """为模块分配多个用户"""
    try:
        data = request.get_json()
        
        # 验证用户ID列表
        if not data or 'user_ids' not in data:
            return jsonify({
                'success': False,
                'message': '用户ID列表不能为空',
                'data': None
            }), 400
        
        user_ids = data['user_ids']
        if not isinstance(user_ids, list):
            return jsonify({
                'success': False,
                'message': '用户ID必须是列表格式',
                'data': None
            }), 400
        
        result = ModuleService.assign_users_to_module(module_id, user_ids)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分配用户时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/members', methods=['GET'])
@login_required
def get_module_members(module_id):
    """获取模块成员列表"""
    try:
        result = ModuleService.get_module_members(module_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模块成员时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>/members', methods=['POST'])
@login_required
def add_module_member(module_id):
    """添加模块成员"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'user_id' not in data:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空',
                'data': None
            }), 400
        
        user_id = data['user_id']
        role = data.get('role', 'member')
        
        result = ModuleService.add_module_member(module_id, user_id, role)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加模块成员时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/members/<int:assignment_id>', methods=['DELETE'])
@login_required
def remove_module_member(assignment_id):
    """移除模块成员"""
    try:
        result = ModuleService.remove_module_member(assignment_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'移除模块成员时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/current-week', methods=['GET'])
def get_current_week():
    """获取当前周的日期范围"""
    try:
        week_start, week_end = ModuleService.get_current_week_dates()
        return jsonify({
            'success': True,
            'message': '获取当前周成功',
            'data': {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'week_label': f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}"
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取当前周时发生错误: {str(e)}',
            'data': None
        }), 500

@module_bp.route('/<int:module_id>', methods=['DELETE'])
@login_required
def delete_module(module_id):
    """删除模块"""
    try:
        # 权限检查
        current_user = request.current_user
        from ..services.auth_service import AuthService
        
        # 检查用户是否有权限删除此模块
        if current_user.role == UserRole.DEPARTMENT_MANAGER:
            # 部门主管可以删除所有模块
            pass
        else:
            # 普通成员需要检查模块权限（项目负责人可以删除项目模块）
            if not AuthService.has_module_permission(current_user, module_id, 'delete_module'):
                return jsonify({
                    'success': False,
                    'message': '没有权限删除此模块'
                }), 403
        
        result = ModuleService.delete_module(module_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除模块时发生错误: {str(e)}',
            'data': None
        }), 500
