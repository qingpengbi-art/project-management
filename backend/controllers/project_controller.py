"""
项目控制器 - 处理项目相关的HTTP请求
遵循DDD分层架构，作为表现层处理API请求
"""

from flask import Blueprint, request, jsonify
from ..services.project_service import ProjectService
from ..services.user_service import UserService
from ..utils.decorators import login_required, permission_required
from ..models.database import UserRole

# 创建项目蓝图
project_bp = Blueprint('project', __name__, url_prefix='/api/projects')

@project_bp.route('', methods=['POST'])
@permission_required('create_project')
def create_project():
    """创建新项目"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': '项目名称不能为空',
                'data': None
            }), 400
        
        result = ProjectService.create_project(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建项目时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('', methods=['GET'])
@login_required
def get_projects():
    """获取项目列表"""
    try:
        # 获取查询参数
        filters = {}
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        if request.args.get('user_id'):
            filters['user_id'] = int(request.args.get('user_id'))
        
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        # 根据用户角色过滤项目
        current_user = request.current_user
        if current_user.role != UserRole.DEPARTMENT_MANAGER:
            # 非部门主管只能看到自己参与的项目
            from ..services.auth_service import AuthService
            accessible_project_ids = AuthService.get_user_projects(current_user)
            filters['project_ids'] = accessible_project_ids
        
        result = ProjectService.get_project_list(filters)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取项目列表时发生错误: {str(e)}',
            'data': []
        }), 500

@project_bp.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project_detail(project_id):
    """获取项目详情"""
    try:
        result = ProjectService.get_project_detail(project_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取项目详情时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """更新项目信息"""
    try:
        # 权限检查
        current_user = request.current_user
        from ..services.auth_service import AuthService
        
        # 部门主管可以编辑所有项目，项目负责人只能编辑自己的项目
        if current_user.role != UserRole.DEPARTMENT_MANAGER:
            accessible_project_ids = AuthService.get_user_projects(current_user)
            if project_id not in accessible_project_ids:
                return jsonify({
                    'success': False,
                    'message': '没有权限编辑此项目'
                }), 403
        
        data = request.get_json()
        
        # 验证必填字段
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        result = ProjectService.update_project(project_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新项目时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目 - 仅部门主管有权限"""
    try:
        # 权限检查：只有部门主管可以删除项目
        current_user = request.current_user
        if current_user.role != UserRole.DEPARTMENT_MANAGER:
            return jsonify({
                'success': False,
                'message': '只有部门主管才能删除项目'
            }), 403
        
        result = ProjectService.delete_project(project_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除项目时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/<int:project_id>/progress', methods=['PUT'])
def update_project_progress(project_id):
    """更新项目进度"""
    try:
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
        
        # 验证更新人
        if 'updated_by_id' not in data:
            return jsonify({
                'success': False,
                'message': '更新人不能为空',
                'data': None
            }), 400
        
        result = ProjectService.update_project_progress(project_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新项目进度时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/<int:project_id>/manual-progress', methods=['PUT'])
@login_required
def update_manual_progress(project_id):
    """
    更新项目的手动进度
    仅适用于前期阶段（初步接触 → 合同签订）
    """
    try:
        data = request.get_json()
        progress = data.get('progress')
        
        if progress is None:
            return jsonify({
                'success': False,
                'message': '进度值不能为空',
                'data': None
            }), 400
        
        # 验证进度值类型
        try:
            progress = int(progress)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': '进度值必须是整数',
                'data': None
            }), 400
        
        result = ProjectService.update_manual_progress(project_id, progress)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新进度失败: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/overview', methods=['GET'])
def get_department_overview():
    """获取部门项目总览"""
    try:
        result = ProjectService.get_department_overview()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取部门总览时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/<int:project_id>/members', methods=['POST'])
def add_project_member():
    """添加项目成员"""
    try:
        # 这个功能将在用户服务中实现
        return jsonify({
            'success': False,
            'message': '功能开发中',
            'data': None
        }), 501
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加项目成员时发生错误: {str(e)}',
            'data': None
        }), 500

@project_bp.route('/<int:project_id>/members/<int:user_id>', methods=['DELETE'])
def remove_project_member():
    """移除项目成员"""
    try:
        # 这个功能将在用户服务中实现
        return jsonify({
            'success': False,
            'message': '功能开发中',
            'data': None
        }), 501
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'移除项目成员时发生错误: {str(e)}',
            'data': None
        }), 500
