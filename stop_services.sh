#!/bin/bash

# 停止项目推进表管理系统服务

echo "🛑 正在停止项目推进表管理系统服务..."

# 读取进程ID
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        # 强制杀死进程（如果还在运行）
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
        echo "✅ 后端服务已停止"
    else
        echo "ℹ️  后端服务未运行"
    fi
    rm -f .backend_pid
else
    echo "ℹ️  未找到后端进程ID文件"
fi

if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🌐 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        # 强制杀死进程（如果还在运行）
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill -9 $FRONTEND_PID 2>/dev/null
        fi
        echo "✅ 前端服务已停止"
    else
        echo "ℹ️  前端服务未运行"
    fi
    rm -f .frontend_pid
else
    echo "ℹ️  未找到前端进程ID文件"
fi

# 清理其他可能的Python HTTP服务器进程
echo "🧹 清理残留进程..."
pkill -f "python.*http.server.*3001" 2>/dev/null
pkill -f "python.*app.py" 2>/dev/null

echo ""
echo "✅ 所有服务已停止"
echo "📝 日志文件保留在:"
echo "   - backend/backend.log"
echo "   - frontend/server.log"
