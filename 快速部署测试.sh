#!/bin/bash

# IDIM项目管理系统 - 快速部署测试脚本

echo "🚀 IDIM项目管理系统 - 快速部署测试"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查Docker是否安装
print_status "检查Docker环境..."
if command -v docker &> /dev/null; then
    print_success "Docker已安装: $(docker --version)"
else
    print_error "Docker未安装，请先安装Docker Desktop"
    echo "下载地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查Docker是否运行
if docker info &> /dev/null; then
    print_success "Docker服务正在运行"
else
    print_error "Docker服务未运行，请启动Docker Desktop"
    exit 1
fi

# 检查docker-compose是否可用
if command -v docker-compose &> /dev/null; then
    print_success "docker-compose可用: $(docker-compose --version)"
else
    print_warning "docker-compose未找到，尝试使用docker compose"
fi

echo ""
print_status "选择部署方式："
echo "1. 🐳 Docker Compose部署 (推荐)"
echo "2. 🚀 单容器部署 (简单)"
echo "3. 🌐 ngrok内网穿透 (外网访问)"
echo "4. 📊 查看当前服务状态"
echo "5. 🛑 停止所有服务"

read -p "请选择 (1-5): " choice

case $choice in
    1)
        print_status "开始Docker Compose部署..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose down 2>/dev/null
            docker-compose up -d
            if [ $? -eq 0 ]; then
                print_success "部署成功！"
                echo ""
                echo "访问地址："
                echo "- 前端: http://localhost"
                echo "- API: http://localhost/api/"
                echo ""
                echo "测试账号："
                echo "- 管理员: admin / td123456"
                echo "- 项目负责人: 王开发 / td123456"
                echo "- 普通成员: 李项目 / td123456"
            else
                print_error "部署失败，请检查错误信息"
            fi
        else
            print_error "docker-compose.yml文件不存在"
        fi
        ;;
    2)
        print_status "开始单容器部署..."
        
        # 停止可能存在的容器
        docker stop idim-system 2>/dev/null
        docker rm idim-system 2>/dev/null
        
        # 构建镜像
        print_status "构建Docker镜像..."
        docker build -t idim-app .
        
        if [ $? -eq 0 ]; then
            # 运行容器
            print_status "启动容器..."
            docker run -d \
              --name idim-system \
              -p 3001:5001 \
              -v "$(pwd)/data:/app/data" \
              idim-app
            
            if [ $? -eq 0 ]; then
                print_success "部署成功！"
                echo ""
                echo "访问地址: http://localhost:3001"
                echo ""
                echo "测试账号："
                echo "- 管理员: admin / td123456"
                echo "- 项目负责人: 王开发 / td123456"
                echo "- 普通成员: 李项目 / td123456"
            else
                print_error "容器启动失败"
            fi
        else
            print_error "镜像构建失败"
        fi
        ;;
    3)
        print_status "启动ngrok内网穿透..."
        
        if ! command -v ngrok &> /dev/null; then
            print_error "ngrok未安装"
            echo "安装方法："
            echo "Mac: brew install ngrok/ngrok/ngrok"
            echo "或访问: https://ngrok.com/download"
            exit 1
        fi
        
        # 检查本地服务是否运行
        if curl -s http://localhost:3001 > /dev/null; then
            print_success "检测到本地服务运行中"
            print_status "启动ngrok隧道..."
            ngrok http 3001
        else
            print_warning "本地服务未运行，请先选择选项1或2部署服务"
        fi
        ;;
    4)
        print_status "检查服务状态..."
        
        echo ""
        echo "Docker容器状态："
        docker ps -a --filter "name=idim"
        
        echo ""
        echo "Docker Compose服务状态："
        if [ -f "docker-compose.yml" ]; then
            docker-compose ps
        else
            echo "docker-compose.yml不存在"
        fi
        
        echo ""
        echo "端口占用情况："
        netstat -an | grep -E ':(80|3001|5001)' || echo "未发现相关端口占用"
        
        echo ""
        echo "本地服务测试："
        if curl -s http://localhost:3001 > /dev/null; then
            print_success "本地服务 (3001端口) 正常"
        else
            print_warning "本地服务 (3001端口) 无响应"
        fi
        
        if curl -s http://localhost > /dev/null; then
            print_success "Nginx服务 (80端口) 正常"
        else
            print_warning "Nginx服务 (80端口) 无响应"
        fi
        ;;
    5)
        print_status "停止所有服务..."
        
        # 停止docker-compose服务
        if [ -f "docker-compose.yml" ]; then
            docker-compose down
        fi
        
        # 停止单独的容器
        docker stop idim-system 2>/dev/null
        docker rm idim-system 2>/dev/null
        
        print_success "所有服务已停止"
        ;;
    *)
        print_error "无效选择，请输入1-5"
        exit 1
        ;;
esac

echo ""
print_status "脚本执行完成！"

# 显示有用的命令
echo ""
echo "常用命令："
echo "- 查看日志: docker-compose logs -f idim-app"
echo "- 重启服务: docker-compose restart"
echo "- 停止服务: docker-compose down"
echo "- 查看状态: docker-compose ps"
