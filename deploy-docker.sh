#!/bin/bash

###############################################################################
# Docker一键部署脚本
# 用于快速部署项目管理系统到Docker环境
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}$1${NC}"
    echo "=========================================="
    echo ""
}

# 检查Docker是否安装
check_docker() {
    print_header "检查Docker环境"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        echo ""
        echo "Mac安装Docker: https://docs.docker.com/desktop/install/mac-install/"
        echo "或使用Homebrew: brew install --cask docker"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker未启动，请启动Docker Desktop"
        exit 1
    fi
    
    print_success "Docker已安装并运行"
    docker --version
    
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose已安装"
        docker-compose --version
    else
        print_warning "未找到docker-compose命令，将使用docker compose"
    fi
}

# 创建必要的目录
create_directories() {
    print_header "创建数据目录"
    
    mkdir -p data
    mkdir -p logs
    
    print_success "数据目录创建完成"
    ls -la data logs
}

# 构建Docker镜像
build_image() {
    print_header "构建Docker镜像"
    
    print_info "开始构建镜像，这可能需要几分钟..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose build
    else
        docker compose build
    fi
    
    print_success "Docker镜像构建完成"
}

# 启动容器
start_containers() {
    print_header "启动Docker容器"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "容器启动成功"
}

# 检查容器状态
check_status() {
    print_header "检查容器状态"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo ""
    print_info "等待应用启动..."
    sleep 5
    
    # 检查健康状态
    if curl -f http://localhost:5001/api/health &> /dev/null; then
        print_success "应用健康检查通过"
    else
        print_warning "应用可能还在启动中，请稍后访问"
    fi
}

# 显示访问信息
show_access_info() {
    print_header "部署完成"
    
    echo "🎉 项目管理系统已成功部署！"
    echo ""
    echo "📱 访问地址："
    echo "   本地访问: http://localhost:5001"
    echo "   API地址:  http://localhost:5001/api"
    echo "   健康检查: http://localhost:5001/api/health"
    echo ""
    
    # 获取本机IP
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "未获取到IP")
    else
        # Linux
        LOCAL_IP=$(hostname -I | awk '{print $1}')
    fi
    
    if [ "$LOCAL_IP" != "未获取到IP" ]; then
        echo "   局域网访问: http://${LOCAL_IP}:5001"
        echo ""
    fi
    
    echo "👤 默认账户："
    echo "   管理员 - 用户名: admin, 密码: admin123"
    echo "   测试账户 - 用户名: zhangsan/lisi/wangwu, 密码: 123456"
    echo ""
    echo "⚠️  重要提示："
    echo "   1. 请登录后立即修改默认密码"
    echo "   2. 数据保存在 ./data 目录"
    echo "   3. 日志保存在 ./logs 目录"
    echo ""
    echo "📋 常用命令："
    echo "   查看日志: docker logs -f project-management-app"
    echo "   停止服务: docker-compose down 或 ./stop-docker.sh"
    echo "   重启服务: docker-compose restart"
    echo "   进入容器: docker exec -it project-management-app bash"
    echo ""
}

# 显示菜单
show_menu() {
    echo ""
    echo "=========================================="
    echo "   Docker部署脚本 - 项目管理系统"
    echo "=========================================="
    echo ""
    echo "请选择操作："
    echo "  1) 完整部署（构建+启动）"
    echo "  2) 仅构建镜像"
    echo "  3) 仅启动容器"
    echo "  4) 停止容器"
    echo "  5) 查看日志"
    echo "  6) 查看状态"
    echo "  0) 退出"
    echo ""
    read -p "请输入选项 [0-6]: " choice
    
    case $choice in
        1)
            check_docker
            create_directories
            build_image
            start_containers
            check_status
            show_access_info
            ;;
        2)
            check_docker
            build_image
            ;;
        3)
            check_docker
            start_containers
            check_status
            show_access_info
            ;;
        4)
            print_info "停止容器..."
            if command -v docker-compose &> /dev/null; then
                docker-compose down
            else
                docker compose down
            fi
            print_success "容器已停止"
            ;;
        5)
            print_info "显示应用日志（Ctrl+C退出）..."
            docker logs -f project-management-app
            ;;
        6)
            check_status
            ;;
        0)
            print_info "退出"
            exit 0
            ;;
        *)
            print_error "无效选项"
            show_menu
            ;;
    esac
}

# 主函数
main() {
    # 检查是否在项目根目录
    if [ ! -f "docker-compose.yml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 如果没有参数，显示菜单
    if [ $# -eq 0 ]; then
        show_menu
    else
        # 支持命令行参数
        case $1 in
            deploy|start)
                check_docker
                create_directories
                build_image
                start_containers
                check_status
                show_access_info
                ;;
            build)
                check_docker
                build_image
                ;;
            stop)
                if command -v docker-compose &> /dev/null; then
                    docker-compose down
                else
                    docker compose down
                fi
                print_success "容器已停止"
                ;;
            restart)
                if command -v docker-compose &> /dev/null; then
                    docker-compose restart
                else
                    docker compose restart
                fi
                print_success "容器已重启"
                ;;
            logs)
                docker logs -f project-management-app
                ;;
            status)
                check_status
                ;;
            *)
                echo "用法: $0 [deploy|build|start|stop|restart|logs|status]"
                exit 1
                ;;
        esac
    fi
}

# 执行主函数
main "$@"


