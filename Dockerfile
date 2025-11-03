# 多阶段构建 - 前端构建阶段
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# 复制前端package文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# 最终镜像 - 使用Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    FLASK_APP=backend/app.py

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# 复制后端requirements
COPY backend/requirements.txt /app/backend/

# 安装Python依赖
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 复制后端代码
COPY --chown=appuser:appuser backend/ /app/backend/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder --chown=appuser:appuser /frontend/dist /app/frontend/dist

# 复制启动脚本
COPY --chown=appuser:appuser docker-start.sh /app/
COPY --chown=appuser:appuser smart_start.sh /app/
RUN chmod +x /app/docker-start.sh /app/smart_start.sh

# 复制数据导出文件和导入脚本
COPY --chown=appuser:appuser database_export.json /app/
COPY --chown=appuser:appuser import_database.py /app/
COPY --chown=appuser:appuser export_database.py /app/

# 复制初始化脚本
COPY --chown=appuser:appuser backend/models/database.py /app/backend/models/

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# 数据卷
VOLUME ["/app/data"]

# 启动应用（使用智能启动脚本，自动导入数据）
CMD ["/app/smart_start.sh"]
