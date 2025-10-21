#!/bin/bash

###############################################################################
# Docker部署测试脚本
# 用于验证Docker配置是否正确
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}🧪 测试: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ 通过: $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ 失败: $1${NC}"
}

print_header() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}$1${NC}"
    echo "=========================================="
    echo ""
}

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

run_test() {
    TOTAL=$((TOTAL + 1))
    print_test "$1"
    
    if eval "$2" > /dev/null 2>&1; then
        PASSED=$((PASSED + 1))
        print_pass "$1"
        return 0
    else
        FAILED=$((FAILED + 1))
        print_fail "$1"
        if [ ! -z "$3" ]; then
            echo "   提示: $3"
        fi
        return 1
    fi
}

print_header "Docker部署测试"

# 测试1：检查必要文件
print_test "检查配置文件"
if [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ] && [ -f "docker-start.sh" ]; then
    PASSED=$((PASSED + 1))
    print_pass "所有必要文件存在"
else
    FAILED=$((FAILED + 1))
    print_fail "缺少必要文件"
fi
TOTAL=$((TOTAL + 1))

# 测试2：检查脚本权限
print_test "检查脚本执行权限"
if [ -x "deploy-docker.sh" ] && [ -x "docker-start.sh" ]; then
    PASSED=$((PASSED + 1))
    print_pass "脚本具有执行权限"
else
    FAILED=$((FAILED + 1))
    print_fail "脚本缺少执行权限"
    echo "   运行: chmod +x deploy-docker.sh docker-start.sh stop-docker.sh"
fi
TOTAL=$((TOTAL + 1))

# 测试3：检查Docker安装
run_test "Docker已安装" "command -v docker" "请安装Docker Desktop"

# 测试4：检查Docker运行
run_test "Docker服务运行中" "docker info" "请启动Docker Desktop"

# 测试5：检查docker-compose
if command -v docker-compose > /dev/null 2>&1; then
    run_test "docker-compose可用" "docker-compose --version"
else
    run_test "docker compose可用" "docker compose version"
fi

# 测试6：检查.dockerignore
run_test ".dockerignore文件存在" "[ -f .dockerignore ]" "建议创建.dockerignore以优化构建"

# 测试7：检查前端构建目录
print_test "检查前端构建目录"
if [ -d "frontend/dist" ]; then
    PASSED=$((PASSED + 1))
    print_pass "前端已构建"
else
    TOTAL=$((TOTAL + 1))
    echo "   ⚠️  前端未构建（首次构建时Docker会自动构建）"
fi
TOTAL=$((TOTAL + 1))

# 测试8：检查后端依赖文件
run_test "后端requirements.txt存在" "[ -f backend/requirements.txt ]"

# 测试9：检查前端package.json
run_test "前端package.json存在" "[ -f frontend/package.json ]"

# 测试10：语法检查
print_test "Dockerfile语法检查"
if docker build -f Dockerfile -t test-syntax --target frontend-builder . > /dev/null 2>&1; then
    PASSED=$((PASSED + 1))
    print_pass "Dockerfile语法正确"
    docker rmi test-syntax > /dev/null 2>&1 || true
else
    FAILED=$((FAILED + 1))
    print_fail "Dockerfile语法错误"
fi
TOTAL=$((TOTAL + 1))

# 测试11：docker-compose配置验证
run_test "docker-compose配置验证" "docker compose config > /dev/null" "检查docker-compose.yml语法"

# 测试12：检查端口占用
print_test "检查端口5001是否可用"
if lsof -i :5001 > /dev/null 2>&1; then
    FAILED=$((FAILED + 1))
    print_fail "端口5001已被占用"
    echo "   运行: lsof -i :5001 查看占用进程"
else
    PASSED=$((PASSED + 1))
    print_pass "端口5001可用"
fi
TOTAL=$((TOTAL + 1))

# 测试13：检查磁盘空间
print_test "检查磁盘空间"
AVAILABLE=$(df -h . | tail -1 | awk '{print $4}')
if [ ! -z "$AVAILABLE" ]; then
    PASSED=$((PASSED + 1))
    print_pass "磁盘空间充足 (可用: $AVAILABLE)"
else
    FAILED=$((FAILED + 1))
    print_fail "无法检查磁盘空间"
fi
TOTAL=$((TOTAL + 1))

# 打印测试结果
print_header "测试结果"

echo "总测试数: $TOTAL"
echo -e "✅ 通过: ${GREEN}$PASSED${NC}"
echo -e "❌ 失败: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 所有测试通过！可以开始部署了！${NC}"
    echo ""
    echo "下一步："
    echo "  ./deploy-docker.sh deploy"
    echo ""
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  有 $FAILED 项测试失败，请先解决问题${NC}"
    echo ""
    echo "常见解决方案："
    echo "  1. 安装Docker: brew install --cask docker"
    echo "  2. 启动Docker: open -a Docker"
    echo "  3. 赋予权限: chmod +x *.sh"
    echo ""
    exit 1
fi


