"""
认证控制器 - 处理用户登录、登出等认证相关操作
"""
from flask import Blueprint, request, jsonify, session
from ..models.database import db, User
from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        username = data['username']
        password = data['password']
        
        # 调试日志
        print(f"[DEBUG] 登录尝试 - 用户名: {username}")
        
        # 检查数据库中的用户
        all_users = User.query.all()
        print(f"[DEBUG] 数据库中共有 {len(all_users)} 个用户")
        for u in all_users:
            print(f"[DEBUG]   - {u.username} (姓名: {u.name})")
        
        # 验证用户凭证
        user = AuthService.authenticate_user(username, password)
        print(f"[DEBUG] 认证结果: {'成功' if user else '失败'}")
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 创建会话
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role.value
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user.to_dict()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登出失败: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取当前用户信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户未登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查用户登录状态"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': '用户未登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': '用户不存在'
            }), 401
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'data': {
                'user': user.to_dict()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'authenticated': False,
            'message': f'验证失败: {str(e)}'
        }), 500
