#!/bin/bash

# 项目推进表管理系统启动脚本

echo "🚀 启动项目推进表管理系统..."

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

# 创建Python虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活Python虚拟环境..."
source venv/bin/activate

# 安装Python依赖
echo "📥 安装Python依赖..."
pip install -r requirements.txt

# 进入前端目录并安装依赖
echo "📥 安装前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# 启动前端开发服务器（后台运行）
echo "🌐 启动前端服务..."
npm run dev &
FRONTEND_PID=$!

# 返回根目录
cd ..

# 等待前端服务启动
sleep 3

# 启动后端服务
echo "⚙️  启动后端服务..."
python backend/app.py &
BACKEND_PID=$!

# 等待服务启动
sleep 5

echo ""
echo "✅ 系统启动完成！"
echo ""
echo "🌐 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:5001"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit 0" INT

# 保持脚本运行
wait
