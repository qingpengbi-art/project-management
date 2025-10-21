#!/bin/bash

# 项目推进表管理系统 - 局域网访问启动脚本

echo "🌐 启动项目推进表管理系统（局域网访问模式）..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 获取本机局域网IP地址
LOCAL_IP=$(ifconfig | grep "inet " | grep -v "127.0.0.1" | head -n1 | awk '{print $2}')
if [ -z "$LOCAL_IP" ]; then
    echo "❌ 错误: 无法获取本机IP地址"
    exit 1
fi

echo "📍 检测到本机IP地址: $LOCAL_IP"

# 创建Python虚拟环境（如果不存在）
if [ ! -d "backend/venv" ]; then
    echo "📦 创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# 激活虚拟环境并启动后端
echo "⚙️  启动后端服务..."
cd backend
source venv/bin/activate

# 安装Python依赖
if [ ! -f "venv/.deps_installed" ]; then
    echo "📥 安装Python依赖..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# 后台启动后端服务
nohup python app.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务是否启动成功
if curl -s "http://$LOCAL_IP:5001/health" > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败，请检查日志"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 构建前端
echo "🔨 构建前端项目..."
cd frontend

# 安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi

# 构建前端项目
echo "📦 构建前端..."
npm run build

# 启动静态文件服务器
echo "🌐 启动前端服务..."
cd dist
nohup python3 -m http.server 3001 --bind 0.0.0.0 > ../server.log 2>&1 &
FRONTEND_PID=$!
cd ../..

# 等待前端服务启动
sleep 3

# 检查前端服务
if curl -s -I "http://$LOCAL_IP:3001/" | grep -q "200 OK"; then
    echo "✅ 前端服务启动成功"
else
    echo "❌ 前端服务启动失败"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 系统启动完成！"
echo ""
echo "📱 局域网访问地址:"
echo "   前端: http://$LOCAL_IP:3001"
echo "   后端API: http://$LOCAL_IP:5001"
echo ""
echo "🖥️  本机访问地址:"
echo "   前端: http://localhost:3001"
echo "   后端API: http://localhost:5001"
echo ""
echo "📋 其他设备访问步骤:"
echo "   1. 确保设备连接到同一WiFi网络"
echo "   2. 在浏览器中输入: http://$LOCAL_IP:3001"
echo "   3. 开始使用项目管理系统"
echo ""
echo "📝 服务状态:"
echo "   后端日志: backend/backend.log"
echo "   前端日志: frontend/server.log"
echo ""
echo "🛑 停止服务请运行: ./stop_services.sh"
echo "   或手动停止进程ID: $BACKEND_PID (后端), $FRONTEND_PID (前端)"

# 保存进程ID到文件
echo "$BACKEND_PID" > .backend_pid
echo "$FRONTEND_PID" > .frontend_pid

echo ""
echo "按 Ctrl+C 退出脚本（服务将继续在后台运行）"

# 等待用户中断
trap "echo ''; echo '📋 服务继续在后台运行...'; echo '🛑 要停止服务请运行: ./stop_services.sh'; exit 0" INT

# 监控服务状态
while true; do
    sleep 10
    # 检查后端服务
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ 后端服务已停止"
        break
    fi
    # 检查前端服务
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ 前端服务已停止"
        break
    fi
done

echo "⚠️  有服务已停止，请检查日志文件"
