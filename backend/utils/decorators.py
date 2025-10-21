"""
装饰器工具 - 提供权限检查、登录验证等装饰器
"""
from functools import wraps
from flask import session, jsonify, request
from ..models.database import User
from ..services.auth_service import AuthService

def login_required(f):
    """
    登录验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 将当前用户添加到请求上下文
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def permission_required(permission):
    """
    权限检查装饰器
    
    Args:
        permission (str): 需要的权限名称
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            if not user or not AuthService.has_permission(user, permission):
                return jsonify({
                    'success': False,
                    'message': '权限不足'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def role_required(*allowed_roles):
    """
    角色检查装饰器
    
    Args:
        allowed_roles: 允许的角色列表
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            if not user or user.role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': '角色权限不足'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
