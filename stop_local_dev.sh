#!/bin/bash

# 本地开发环境停止脚本
echo "🛑 停止本地开发环境..."

# 停止后端服务
echo "🔧 停止后端服务..."
pkill -f "python.*app.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端服务已停止"
else
    echo "ℹ️  后端服务未运行"
fi

# 停止前端服务
echo "🎨 停止前端开发服务..."
pkill -f "node.*vite" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 前端服务已停止"
else
    echo "ℹ️  前端服务未运行"
fi

# 等待进程完全停止
sleep 2

# 检查端口是否释放
echo "🔍 检查端口状态..."
if ! lsof -i :5001 > /dev/null 2>&1; then
    echo "✅ 端口 5001 已释放"
else
    echo "⚠️  端口 5001 仍被占用"
fi

if ! lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ 端口 3000 已释放"
else
    echo "⚠️  端口 3000 仍被占用"
fi

echo ""
echo "🎉 本地开发环境已停止!"
