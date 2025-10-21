# Docker部署完整总结

## 📦 已创建的文件

### 核心配置文件
1. **Dockerfile** - Docker镜像构建配置
2. **docker-compose.yml** - Docker编排配置
3. **.dockerignore** - Docker构建时忽略的文件
4. **.env.example** - 环境变量配置示例

### 脚本文件
1. **docker-start.sh** - 容器启动脚本（容器内使用）
2. **deploy-docker.sh** - 一键部署脚本（交互式菜单）
3. **stop-docker.sh** - 停止容器脚本

### 文档文件
1. **DOCKER_DEPLOY.md** - 完整的Docker部署文档
2. **DOCKER_QUICKSTART.md** - 快速启动指南
3. **DOCKER使用总结.md** - 本文档

### 代码修改
1. **backend/app.py** - 支持Docker环境配置
2. **backend/config.py** - 配置管理（新增）

---

## 🚀 快速使用指南

### 方式1：使用部署脚本（推荐）

```bash
# 进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 运行部署脚本
./deploy-docker.sh

# 选择 1 - 完整部署
```

### 方式2：使用命令行

```bash
# 完整部署
./deploy-docker.sh deploy

# 或手动执行
docker compose build
docker compose up -d
```

### 方式3：Docker命令

```bash
# 构建镜像
docker compose build

# 启动容器
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker logs -f project-management-app

# 停止容器
docker compose down
```

---

## 📝 关键特性

### 1. 环境自适应
- ✅ 自动检测Docker环境
- ✅ 本地开发和Docker环境共存
- ✅ 数据库路径自动配置

### 2. 数据持久化
```yaml
volumes:
  - ./data:/app/data      # 数据库文件
  - ./logs:/app/logs      # 日志文件
```

数据保存在宿主机，容器删除也不会丢失。

### 3. 网络配置
```yaml
ports:
  - "5001:5001"  # 主应用端口
```

支持：
- 本地访问：`http://localhost:5001`
- 局域网访问：`http://192.168.x.x:5001`

### 4. 健康检查
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
  interval: 30s
  timeout: 10s
```

Docker会自动监控应用健康状态。

### 5. 多阶段构建
```dockerfile
# 阶段1：构建前端
FROM node:18-alpine AS frontend-builder
...

# 阶段2：运行应用
FROM python:3.9-slim
...
```

减小最终镜像体积，提高构建效率。

---

## 🔧 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| SECRET_KEY | your-secret-key... | 应用密钥（生产环境必改） |
| DATABASE_PATH | /app/data/project_management.db | 数据库路径 |
| FLASK_ENV | production | Flask环境 |
| LOG_PATH | /app/logs | 日志路径 |

### 端口配置

修改 `docker-compose.yml`:
```yaml
ports:
  - "8080:5001"  # 改为8080端口
```

### 存储配置

修改 `docker-compose.yml`:
```yaml
volumes:
  - /path/to/your/data:/app/data  # 自定义数据目录
  - /path/to/your/logs:/app/logs  # 自定义日志目录
```

---

## 📊 目录结构

```
项目推荐表设计/
├── Dockerfile              # Docker镜像配置
├── docker-compose.yml      # Docker编排
├── .dockerignore          # 构建忽略文件
├── .env.example           # 环境变量示例
├── deploy-docker.sh       # 部署脚本 ⭐
├── stop-docker.sh         # 停止脚本
├── docker-start.sh        # 容器启动脚本
├── DOCKER_DEPLOY.md       # 完整文档 📖
├── DOCKER_QUICKSTART.md   # 快速指南 🚀
│
├── data/                  # 数据目录（自动创建）
│   └── project_management.db
│
├── logs/                  # 日志目录（自动创建）
│   └── backend.log
│
├── backend/               # 后端代码
│   ├── app.py            # 支持Docker环境 ✨
│   ├── config.py         # 配置管理 ✨
│   └── ...
│
└── frontend/             # 前端代码
    ├── dist/             # 构建产物（Docker使用）
    └── ...
```

---

## 🎯 使用场景

### 场景1：快速演示
```bash
./deploy-docker.sh deploy
# 等待3-5分钟
# 打开 http://localhost:5001
```

### 场景2：局域网分享
```bash
# 1. 部署
./deploy-docker.sh deploy

# 2. 获取IP
ipconfig getifaddr en0

# 3. 分享给同事
# http://192.168.x.x:5001
```

### 场景3：服务器部署
```bash
# 1. 上传项目到服务器
scp -r . user@server:/path/to/project

# 2. SSH连接服务器
ssh user@server

# 3. 部署
cd /path/to/project
./deploy-docker.sh deploy

# 4. 配置防火墙
sudo ufw allow 5001
```

### 场景4：开发调试
```bash
# 进入容器
docker exec -it project-management-app bash

# 查看日志
docker logs -f project-management-app

# 重启服务
docker compose restart
```

---

## 🔍 故障排查

### 问题1：容器无法启动

**检查步骤：**
```bash
# 1. 查看容器状态
docker compose ps

# 2. 查看详细日志
docker logs project-management-app

# 3. 检查端口占用
lsof -i :5001

# 4. 重新构建
docker compose build --no-cache
docker compose up -d
```

### 问题2：数据库初始化失败

**解决方案：**
```bash
# 1. 停止容器
docker compose down

# 2. 清理数据
rm -rf data/*

# 3. 重启容器
docker compose up -d

# 4. 查看初始化日志
docker logs -f project-management-app
```

### 问题3：前端页面404

**解决方案：**
```bash
# 1. 检查前端构建
ls -la frontend/dist/

# 2. 如果dist为空，重新构建
cd frontend
npm install
npm run build

# 3. 重新构建Docker镜像
cd ..
docker compose build --no-cache
docker compose up -d
```

### 问题4：CORS错误

Docker环境已配置允许所有来源，如需限制，修改 `backend/app.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://your-domain.com"],  # 指定域名
        ...
    }
})
```

---

## 📈 性能优化

### 1. 构建缓存
```bash
# 使用构建缓存
docker compose build

# 不使用缓存（完全重建）
docker compose build --no-cache
```

### 2. 镜像体积
当前镜像使用多阶段构建，已经优化：
- 前端构建阶段：仅保留构建产物
- 运行阶段：使用slim镜像，最小化体积

### 3. 容器资源限制
编辑 `docker-compose.yml`:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          memory: 512M
```

---

## 🔐 安全建议

### 1. 修改默认密钥
```bash
# 创建 .env 文件
cp .env.example .env

# 生成随机密钥
python3 -c "import secrets; print(secrets.token_hex(32))"

# 修改 .env
SECRET_KEY=生成的随机密钥
```

### 2. 修改默认密码
登录后在用户管理中修改所有默认账户密码。

### 3. 配置防火墙
```bash
# macOS防火墙会自动提示
# Linux使用ufw
sudo ufw allow 5001
sudo ufw enable
```

### 4. 使用HTTPS（生产环境）
配合Nginx反向代理：
```bash
# 启动Nginx
docker compose --profile production up -d
```

---

## 📦 数据备份与恢复

### 备份数据
```bash
# 方法1：复制数据库文件
cp data/project_management.db backup_$(date +%Y%m%d).db

# 方法2：打包整个data目录
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 方法3：Docker卷备份
docker run --rm \
  -v 项目推荐表设计_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/data_backup.tar.gz /data
```

### 恢复数据
```bash
# 1. 停止容器
docker compose down

# 2. 恢复数据库
cp backup_20241020.db data/project_management.db

# 3. 重启容器
docker compose up -d
```

### 自动备份（定时任务）
```bash
# 编辑crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * cd /Users/bizai/Desktop/项目推荐表设计 && cp data/project_management.db data/backup_$(date +\%Y\%m\%d).db

# 每周日清理30天前的备份
0 3 * * 0 find /Users/bizai/Desktop/项目推荐表设计/data -name "backup_*.db" -mtime +30 -delete
```

---

## 🎉 总结

### 优势
✅ **简单**：一键部署，无需配置环境  
✅ **可靠**：数据持久化，自动健康检查  
✅ **灵活**：支持本地和局域网访问  
✅ **专业**：DDD架构，生产级配置  
✅ **完美支持Mac M1**：原生适配  

### 适用场景
🎯 快速演示  
🎯 团队协作  
🎯 服务器部署  
🎯 生产环境  

### 下一步建议
1. ✅ 修改默认密码
2. ✅ 配置定期备份
3. ✅ 根据需求调整端口
4. ✅ 生产环境配置HTTPS
5. ✅ 监控容器资源使用

---

**祝使用愉快！** 🚀

如有问题，请查看：
- 📖 [完整部署文档](./DOCKER_DEPLOY.md)
- 🚀 [快速启动指南](./DOCKER_QUICKSTART.md)
- 📋 [项目说明](./README.md)


