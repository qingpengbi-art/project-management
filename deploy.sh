#!/bin/bash

# IDIM项目管理系统部署脚本
# 使用方法: ./deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 开始部署IDIM项目管理系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/home/idim/项目推荐表设计"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 函数：打印状态信息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    print_error "请不要使用root用户运行此脚本"
    exit 1
fi

# 步骤1: 更新代码（如果使用git）
if [ -d "$PROJECT_DIR/.git" ]; then
    print_status "更新代码..."
    cd $PROJECT_DIR
    git pull origin main || print_warning "Git pull失败，继续部署..."
fi

# 步骤2: 部署后端
print_status "部署后端服务..."
cd $BACKEND_DIR

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    print_status "创建Python虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 安装/更新依赖
print_status "安装Python依赖..."
pip install -r requirements.txt

# 初始化数据库（如果需要）
if [ ! -f "database.db" ]; then
    print_status "初始化数据库..."
    python3 -c "
from models.database import init_database, create_test_users
from app import app
with app.app_context():
    init_database(app)
    create_test_users()
print('数据库初始化完成')
"
fi

# 步骤3: 部署前端
print_status "构建前端应用..."
cd $FRONTEND_DIR

# 安装依赖
print_status "安装Node.js依赖..."
npm install

# 构建生产版本
print_status "构建前端生产版本..."
npm run build

# 设置文件权限
print_status "设置文件权限..."
sudo chown -R www-data:www-data $FRONTEND_DIR/dist

# 步骤4: 重启服务
print_status "重启后端服务..."
sudo systemctl restart idim-backend

# 检查服务状态
sleep 3
if sudo systemctl is-active --quiet idim-backend; then
    print_success "后端服务启动成功"
else
    print_error "后端服务启动失败"
    sudo systemctl status idim-backend
    exit 1
fi

# 重启Nginx
print_status "重启Nginx..."
sudo systemctl restart nginx

if sudo systemctl is-active --quiet nginx; then
    print_success "Nginx重启成功"
else
    print_error "Nginx重启失败"
    sudo systemctl status nginx
    exit 1
fi

# 步骤5: 验证部署
print_status "验证部署..."

# 检查后端API
if curl -f -s http://localhost:5001/api/projects > /dev/null; then
    print_success "后端API正常"
else
    print_warning "后端API检查失败，可能需要登录"
fi

# 检查前端
if curl -f -s http://localhost > /dev/null; then
    print_success "前端服务正常"
else
    print_error "前端服务检查失败"
fi

# 步骤6: 显示状态信息
print_status "服务状态："
echo "================================"
echo "后端服务: $(sudo systemctl is-active idim-backend)"
echo "Nginx服务: $(sudo systemctl is-active nginx)"
echo "================================"

print_success "🎉 部署完成！"
echo ""
echo "访问地址："
echo "- 本地: http://localhost"
echo "- 外网: http://$(curl -s ifconfig.me 2>/dev/null || echo '您的服务器IP')"
echo ""
echo "测试账号："
echo "- 管理员: admin / td123456"
echo "- 项目负责人: 王开发 / td123456"
echo "- 普通成员: 李项目 / td123456"
echo ""
print_status "部署日志已保存，如有问题请检查："
echo "- 后端日志: sudo journalctl -u idim-backend -f"
echo "- Nginx日志: sudo tail -f /var/log/nginx/error.log"
