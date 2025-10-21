#!/bin/bash

echo "🔄 快速更新Docker容器..."
echo ""

# 停止容器
echo "1️⃣ 停止现有容器..."
docker compose down

# 重新构建（使用缓存加快速度）
echo ""
echo "2️⃣ 重新构建镜像..."
docker compose build

# 启动容器
echo ""
echo "3️⃣ 启动容器..."
docker compose up -d

# 等待启动
echo ""
echo "⏳ 等待应用启动..."
sleep 3

# 显示状态
echo ""
echo "📊 容器状态："
docker compose ps

echo ""
echo "✅ 更新完成！"
echo ""
echo "📱 访问地址："
echo "   http://localhost:5001"
echo ""
echo "📝 查看日志："
echo "   docker logs -f project-management-app"
echo ""

