#!/bin/bash

echo "🔄 重启项目管理系统服务..."

# 获取本机IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
echo "📍 检测到本机IP地址: $LOCAL_IP"

# 停止所有相关服务
echo "🛑 停止现有服务..."
pkill -f "python.*app.py"
pkill -f "spa_server.py"
pkill -f "python3 -m http.server"
sleep 3

# 启动后端服务
echo "⚙️  启动后端服务..."
cd backend
source venv/bin/activate
nohup python app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../.backend_pid
cd ..

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务
if curl -s -f "http://$LOCAL_IP:5001/health" > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 构建前端项目
echo "🔨 构建前端项目..."
cd frontend
npm run build

# 启动SPA前端服务
echo "🌐 启动前端SPA服务..."
nohup python3 spa_server.py > spa_server.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend_pid
cd ..

# 等待前端服务启动
sleep 3

# 检查前端服务
if curl -s -f "http://$LOCAL_IP:3001/" > /dev/null; then
    echo "✅ 前端服务启动成功"
else
    echo "❌ 前端服务启动失败"
    exit 1
fi

echo ""
echo "🎉 系统重启完成！"
echo ""
echo "📱 局域网访问地址:"
echo "   前端: http://$LOCAL_IP:3001"
echo "   后端API: http://$LOCAL_IP:5001"
echo ""
echo "🖥️  本机访问地址:"
echo "   前端: http://localhost:3001"
echo "   后端API: http://localhost:5001"
echo ""
echo "📋 测试账号:"
echo "   管理员: gaojimin / td123456"
echo "   普通用户: yangjitong / td123456"
echo ""
echo "🛑 停止服务请运行: ./stop_services.sh"
echo "   或手动停止进程ID: $BACKEND_PID (后端), $FRONTEND_PID (前端)"
