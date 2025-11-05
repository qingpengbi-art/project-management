"""
用户控制器 - 处理用户相关的HTTP请求
遵循DDD分层架构，作为表现层处理用户API请求
"""

from flask import Blueprint, request, jsonify
from ..services.user_service import UserService
from ..utils.decorators import login_required, permission_required

# 创建用户蓝图
user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['POST'])
@permission_required('manage_users')
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': '用户姓名不能为空',
                'data': None
            }), 400
        
        result = UserService.create_user(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建用户时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('', methods=['GET'])
@permission_required('view_users')
def get_users():
    """获取用户列表"""
    try:
        # 获取查询参数
        filters = {}
        
        if request.args.get('role'):
            filters['role'] = request.args.get('role')
        
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        result = UserService.get_user_list(filters)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表时发生错误: {str(e)}',
            'data': []
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    """获取用户详情"""
    try:
        result = UserService.get_user_detail(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户详情时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': '用户姓名不能为空',
                'data': None
            }), 400
        
        result = UserService.update_user(user_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        result = UserService.delete_user(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/projects/<int:project_id>/members', methods=['POST'])
def add_project_member(project_id):
    """添加项目成员"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('user_id'):
            return jsonify({
                'success': False,
                'message': '用户ID不能为空',
                'data': None
            }), 400
        
        result = UserService.add_project_member(project_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加项目成员时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/projects/<int:project_id>/members/<int:user_id>', methods=['DELETE'])
def remove_project_member(project_id, user_id):
    """移除项目成员"""
    try:
        result = UserService.remove_project_member(project_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'移除项目成员时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/projects/<int:project_id>/members/<int:user_id>/role', methods=['PUT'])
def update_member_role(project_id, user_id):
    """更新项目成员角色"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('role'):
            return jsonify({
                'success': False,
                'message': '角色不能为空',
                'data': None
            }), 400
        
        # 验证角色值
        valid_roles = ['leader', 'member']
        if data['role'] not in valid_roles:
            return jsonify({
                'success': False,
                'message': f'角色必须是以下之一: {", ".join(valid_roles)}',
                'data': None
            }), 400
        
        result = UserService.update_member_role(project_id, user_id, data['role'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新成员角色时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    """用户修改自己的密码"""
    try:
        data = request.get_json()
        current_user = request.current_user
        
        # 验证必填字段
        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': '旧密码和新密码不能为空',
                'data': None
            }), 400
        
        # 验证新密码长度
        if len(data['new_password']) < 6:
            return jsonify({
                'success': False,
                'message': '新密码长度不能少于6位',
                'data': None
            }), 400
        
        result = UserService.change_password(
            current_user.id,
            data['old_password'],
            data['new_password']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'修改密码时发生错误: {str(e)}',
            'data': None
        }), 500

@user_bp.route('/<int:user_id>/reset-password', methods=['PUT'])
@login_required
def reset_password(user_id):
    """部门主管重置用户密码为初始密码"""
    try:
        current_user = request.current_user
        
        # 验证权限：只有部门主管才能重置密码
        if current_user.role != 'supervisor':
            return jsonify({
                'success': False,
                'message': '只有部门主管才能重置密码',
                'data': None
            }), 403
        
        result = UserService.reset_password(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码时发生错误: {str(e)}',
            'data': None
        }), 500
