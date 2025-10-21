#!/bin/bash

###############################################################################
# Docker停止脚本
# 用于停止和清理Docker容器
###############################################################################

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "=========================================="
echo -e "${BLUE}停止项目管理系统Docker容器${NC}"
echo "=========================================="
echo ""

# 停止容器
if command -v docker-compose &> /dev/null; then
    docker-compose down
else
    docker compose down
fi

echo ""
echo -e "${GREEN}✅ 容器已停止${NC}"
echo ""
echo "数据已保存在 ./data 目录"
echo "日志已保存在 ./logs 目录"
echo ""
echo "重新启动: ./deploy-docker.sh start"
echo ""


