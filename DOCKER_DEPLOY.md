# Docker部署指南

本文档详细说明如何使用Docker部署项目管理系统。

## 📋 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [维护操作](#维护操作)

---

## 🔧 前置要求

### 1. 安装Docker

**macOS (推荐使用Docker Desktop):**

```bash
# 方法1: 使用Homebrew安装
brew install --cask docker

# 方法2: 从官网下载
# 访问 https://docs.docker.com/desktop/install/mac-install/
# 下载Docker Desktop for Mac (Apple Silicon 或 Intel芯片)
```

**Linux (Ubuntu/Debian):**

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt-get install docker-compose-plugin
```

### 2. 验证安装

```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker compose version
# 或
docker-compose --version

# 检查Docker是否运行
docker info
```

---

## 🚀 快速开始

### 一键部署（推荐）

```bash
# 1. 进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 2. 赋予脚本执行权限
chmod +x deploy-docker.sh stop-docker.sh

# 3. 运行部署脚本（交互式菜单）
./deploy-docker.sh

# 或直接执行完整部署
./deploy-docker.sh deploy
```

### 手动部署

```bash
# 1. 创建必要目录
mkdir -p data logs

# 2. 构建Docker镜像
docker compose build

# 3. 启动容器
docker compose up -d

# 4. 查看容器状态
docker compose ps

# 5. 查看日志
docker logs -f project-management-app
```

---

## 📝 详细步骤

### 步骤1: 准备环境

```bash
# 克隆或进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 确保Docker正在运行
docker info
```

### 步骤2: 配置环境变量（可选）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（可选）
vi .env
```

**.env 配置示例：**

```env
SECRET_KEY=your-production-secret-key-here
DATABASE_PATH=/app/data/project_management.db
FLASK_ENV=production
```

### 步骤3: 构建镜像

```bash
# 使用docker-compose构建
docker-compose build

# 或使用docker compose（新版本）
docker compose build

# 查看构建的镜像
docker images | grep project-management
```

### 步骤4: 启动服务

```bash
# 启动所有服务
docker compose up -d

# 查看启动的容器
docker compose ps

# 查看容器日志
docker logs -f project-management-app
```

### 步骤5: 验证部署

```bash
# 检查健康状态
curl http://localhost:5001/api/health

# 访问系统信息
curl http://localhost:5001/

# 在浏览器中访问
# http://localhost:5001
```

---

## ⚙️ 配置说明

### Docker Compose配置

`docker-compose.yml` 文件包含以下配置：

```yaml
services:
  app:
    ports:
      - "5001:5001"  # 后端API端口
    volumes:
      - ./data:/app/data      # 数据持久化
      - ./logs:/app/logs      # 日志持久化
    environment:
      - SECRET_KEY=your-secret-key
      - DATABASE_PATH=/app/data/project_management.db
```

### 端口配置

- **5001**: 后端API和前端服务端口

如需修改端口，编辑 `docker-compose.yml`:

```yaml
ports:
  - "8080:5001"  # 将本地8080端口映射到容器5001端口
```

### 数据持久化

- **./data**: 数据库文件存储目录
- **./logs**: 应用日志存储目录

数据会自动保存在这些目录中，即使容器删除也不会丢失。

---

## 🌐 访问系统

### 本地访问

```
http://localhost:5001
```

### 局域网访问

1. **获取本机IP地址：**

```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'
```

2. **使用IP访问：**

```
http://192.168.x.x:5001
```

### 默认账户

- **管理员账户**
  - 用户名: `admin`
  - 密码: `admin123`

- **测试账户**
  - 用户名: `zhangsan` / `lisi` / `wangwu`
  - 密码: `123456`

⚠️ **重要**: 首次登录后请立即修改默认密码！

---

## 🔍 常见问题

### 1. Docker未启动

**问题**: `Cannot connect to the Docker daemon`

**解决**:
```bash
# macOS: 启动Docker Desktop应用
open -a Docker

# Linux: 启动Docker服务
sudo systemctl start docker
```

### 2. 端口被占用

**问题**: `Bind for 0.0.0.0:5001 failed: port is already allocated`

**解决**:
```bash
# 查看占用5001端口的进程
lsof -i :5001

# 杀死进程或修改docker-compose.yml中的端口映射
```

### 3. 权限问题

**问题**: `Permission denied`

**解决**:
```bash
# 给予脚本执行权限
chmod +x deploy-docker.sh stop-docker.sh docker-start.sh

# 或使用sudo运行Docker命令（不推荐）
sudo docker compose up -d
```

### 4. 镜像构建失败

**问题**: 构建时出现网络或依赖错误

**解决**:
```bash
# 清理Docker缓存
docker builder prune -a

# 重新构建（不使用缓存）
docker compose build --no-cache

# 如果是网络问题，配置Docker代理
```

### 5. 数据库初始化失败

**问题**: 容器启动后数据库未正确创建

**解决**:
```bash
# 删除旧数据库
rm -rf data/*

# 重启容器
docker compose restart

# 查看初始化日志
docker logs project-management-app
```

### 6. 前端资源404

**问题**: 前端页面无法加载静态资源

**解决**:
```bash
# 重新构建前端
cd frontend
npm install
npm run build

# 重新构建Docker镜像
docker compose build --no-cache
docker compose up -d
```

---

## 🛠 维护操作

### 查看日志

```bash
# 查看应用日志
docker logs -f project-management-app

# 查看最近100行日志
docker logs --tail 100 project-management-app

# 查看持久化的日志文件
tail -f logs/backend.log
```

### 停止服务

```bash
# 使用脚本停止
./stop-docker.sh

# 或手动停止
docker compose down

# 停止但不删除容器
docker compose stop
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启单个容器
docker restart project-management-app
```

### 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker compose build

# 3. 重启容器
docker compose up -d
```

### 备份数据

```bash
# 备份数据库
cp data/project_management.db data/project_management_backup_$(date +%Y%m%d).db

# 或打包整个data目录
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# 备份到其他位置
cp data/project_management.db ~/Backups/
```

### 恢复数据

```bash
# 1. 停止容器
docker compose down

# 2. 恢复数据库文件
cp data/project_management_backup_20241020.db data/project_management.db

# 3. 重启容器
docker compose up -d
```

### 清理容器和镜像

```bash
# 停止并删除容器（保留数据）
docker compose down

# 删除容器和匿名卷
docker compose down -v

# 删除所有相关镜像
docker rmi project-management-app

# 清理未使用的Docker资源
docker system prune -a
```

### 进入容器调试

```bash
# 进入容器bash
docker exec -it project-management-app bash

# 在容器中执行命令
docker exec project-management-app ls -la /app/data

# 查看容器内进程
docker exec project-management-app ps aux
```

### 监控容器资源

```bash
# 查看容器资源使用情况
docker stats project-management-app

# 查看容器详细信息
docker inspect project-management-app
```

---

## 📊 生产环境建议

### 1. 安全配置

```bash
# 修改默认密钥
vi .env
# 设置强密码: SECRET_KEY=随机生成的长字符串

# 修改所有默认账户密码
# 登录系统后在用户管理中修改
```

### 2. 使用Nginx反向代理（可选）

```bash
# 启动Nginx服务
docker compose --profile production up -d

# 这将同时启动app和nginx容器
# 通过80端口访问: http://localhost
```

### 3. 定期备份

```bash
# 创建定时备份任务
crontab -e

# 添加每天凌晨2点自动备份
0 2 * * * cd /Users/bizai/Desktop/项目推荐表设计 && cp data/project_management.db data/backup_$(date +\%Y\%m\%d).db
```

### 4. 日志轮转

```bash
# 定期清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 📞 支持与帮助

### 有用的命令速查

```bash
# 快速启动
./deploy-docker.sh deploy

# 查看状态
docker compose ps

# 查看日志
docker logs -f project-management-app

# 停止服务
./stop-docker.sh

# 重启服务
docker compose restart

# 进入容器
docker exec -it project-management-app bash

# 健康检查
curl http://localhost:5001/api/health
```

### 调试技巧

1. **查看详细日志**
   ```bash
   docker logs --tail 200 project-management-app
   ```

2. **检查网络连接**
   ```bash
   docker network inspect 项目推荐表设计_app-network
   ```

3. **验证数据库**
   ```bash
   docker exec -it project-management-app ls -la /app/data
   ```

4. **测试API**
   ```bash
   curl -X POST http://localhost:5001/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

---

## 🎯 下一步

部署完成后，你可以：

1. ✅ 访问系统并登录
2. ✅ 修改默认密码
3. ✅ 创建新用户
4. ✅ 开始管理项目
5. ✅ 配置定期备份

---

**祝使用愉快！** 🎉


