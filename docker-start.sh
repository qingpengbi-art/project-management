#!/bin/bash

# Docker容器启动脚本
# 用于初始化数据库并启动Flask应用

set -e

echo "=========================================="
echo "🚀 启动IDIM项目管理系统 (Docker版)"
echo "=========================================="

# 设置数据库路径
export DATABASE_PATH=${DATABASE_PATH:-/app/data/project_management.db}
export LOG_PATH=${LOG_PATH:-/app/logs}

# 创建必要的目录
mkdir -p /app/data
mkdir -p /app/logs

echo "📁 数据目录: /app/data"
echo "📝 日志目录: /app/logs"
echo "💾 数据库路径: $DATABASE_PATH"

# 进入后端目录
cd /app/backend

# 检查数据库是否存在
if [ ! -f "$DATABASE_PATH" ]; then
    echo ""
    echo "📊 数据库不存在，开始初始化..."
    
    # 初始化数据库
    python3 -c "
import sys
import os

# 设置正确的导入路径
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

from models.database import db, User, Project, ProjectModule, UserRole
from werkzeug.security import generate_password_hash
import os

# 设置数据库路径
os.environ['DATABASE_PATH'] = '$DATABASE_PATH'

# 创建Flask应用并初始化数据库
from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.environ.get(\"DATABASE_PATH\", \"/app/data/project_management.db\")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

with app.app_context():
    # 创建所有表
    db.create_all()
    print('✅ 数据库表创建完成')
    
    # 创建默认管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            name='系统管理员',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role=UserRole.DEPARTMENT_MANAGER,
            email='admin@example.com'
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ 默认管理员用户创建成功')
        print('   用户名: admin')
        print('   密码: admin123')
        print('   请登录后立即修改密码！')
    
    # 创建测试用户
    test_users = [
        {'username': 'zhangsan', 'name': '张三', 'email': 'zhangsan@example.com'},
        {'username': 'lisi', 'name': '李四', 'email': 'lisi@example.com'},
        {'username': 'wangwu', 'name': '王五', 'email': 'wangwu@example.com'},
    ]
    
    for user_data in test_users:
        user = User.query.filter_by(username=user_data['username']).first()
        if not user:
            user = User(
                name=user_data['name'],
                username=user_data['username'],
                password_hash=generate_password_hash('123456'),
                role=UserRole.MEMBER,
                email=user_data['email']
            )
            db.session.add(user)
    
    db.session.commit()
    print('✅ 测试用户创建完成')
    print('✅ 数据库初始化完成！')
"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "✅ 数据库初始化成功！"
        echo "=========================================="
        echo ""
        echo "📋 默认账户信息："
        echo "   管理员 - 用户名: admin, 密码: admin123"
        echo "   测试用户 - 用户名: zhangsan/lisi/wangwu, 密码: 123456"
        echo ""
        echo "⚠️  请登录后立即修改默认密码！"
        echo "=========================================="
        echo ""
    else
        echo "❌ 数据库初始化失败！"
        exit 1
    fi
else
    echo "✅ 数据库已存在，跳过初始化"
fi

echo ""
echo "🌟 启动Flask应用..."
echo "=========================================="
echo ""

# 设置数据库路径环境变量并启动Flask
export SQLALCHEMY_DATABASE_URI="sqlite:///$DATABASE_PATH"

# 启动应用
exec python3 app.py
