#!/bin/bash

# 本地开发环境启动脚本
echo "🚀 启动本地开发环境..."

# 检查并停止可能运行的服务
echo "📋 检查现有服务..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
sleep 2

# 启动后端服务
echo "🔧 启动后端服务 (Flask)..."
cd backend
source venv/bin/activate
nohup python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 启动前端开发服务
echo "🎨 启动前端开发服务 (Vite)..."
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务 PID: $FRONTEND_PID"
cd ..

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if lsof -i :5001 > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常 (端口 5001)"
else
    echo "❌ 后端服务启动失败"
fi

if lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ 前端服务运行正常 (端口 3000)"
else
    echo "❌ 前端服务启动失败"
fi

echo ""
echo "🎉 本地开发环境启动完成!"
echo ""
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:5001"
echo ""
echo "📋 日志文件:"
echo "   - 后端日志: backend.log"
echo "   - 前端日志: frontend.log"
echo ""
echo "🛑 停止服务请运行: ./stop_local_dev.sh"
