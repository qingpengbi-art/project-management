# 🐳 IDIM项目管理系统 - Docker一键部署指南

## 🎯 为什么选择Docker部署？

### ✅ 超级简单
- **一条命令**：`docker-compose up -d` 即可完成部署
- **环境隔离**：不会污染您的系统环境
- **跨平台**：Windows、Mac、Linux都支持

### 💰 成本极低
- **本地使用**：完全免费
- **VPS部署**：最低5元/月的VPS即可

### 🚀 功能完整
- **自动初始化**：数据库和测试用户自动创建
- **数据持久化**：重启容器数据不丢失
- **健康检查**：服务异常自动重启

---

## 📋 部署前准备

### 1. 安装Docker
根据您的操作系统选择：

#### Windows/Mac
1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 安装并启动Docker Desktop
3. 验证安装：打开终端运行 `docker --version`

#### Linux (Ubuntu/Debian)
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install docker-compose

# 将用户添加到docker组（避免使用sudo）
sudo usermod -aG docker $USER
# 重新登录或运行：newgrp docker
```

### 2. 验证Docker安装
```bash
docker --version
docker-compose --version
```

---

## 🚀 一键部署步骤

### 方法1：简单部署（推荐新手）
```bash
# 1. 进入项目目录
cd "/Users/bizai/Desktop/项目推荐表设计"

# 2. 构建并启动服务（一条命令搞定！）
docker-compose up -d

# 3. 查看启动状态
docker-compose ps

# 4. 查看日志（可选）
docker-compose logs -f idim-app
```

### 方法2：仅后端服务（更轻量）
```bash
# 1. 构建镜像
docker build -t idim-app .

# 2. 运行容器
docker run -d \
  --name idim-system \
  -p 3001:5001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/backend/database.db:/app/backend/database.db \
  idim-app

# 3. 检查运行状态
docker ps
```

---

## 🌐 访问系统

### 本地访问
- **地址**：http://localhost:3001 或 http://localhost
- **测试账号**：
  - 管理员：`admin` / `td123456`
  - 项目负责人：`王开发` / `td123456`
  - 普通成员：`李项目` / `td123456`

### 局域网访问
其他设备访问：`http://您的电脑IP:3001`

---

## 🔧 常用管理命令

### 服务管理
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f idim-app
```

### 数据管理
```bash
# 备份数据库
docker cp idim-system:/app/backend/database.db ./backup-$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backup-20231201.db idim-system:/app/backend/database.db
docker-compose restart idim-app

# 清空数据（重新初始化）
docker-compose down
rm -f backend/database.db
docker-compose up -d
```

### 更新应用
```bash
# 1. 停止服务
docker-compose down

# 2. 重新构建镜像
docker-compose build --no-cache

# 3. 启动服务
docker-compose up -d
```

---

## 🌍 VPS部署（外网访问）

### 推荐VPS服务商
| 服务商 | 价格 | 配置 | 特点 |
|--------|------|------|------|
| **腾讯云轻量** | 24元/月 | 1核2G | 国内访问快 |
| **阿里云ECS** | 30元/月 | 1核2G | 稳定可靠 |
| **DigitalOcean** | $5/月 | 1核1G | 国际访问好 |
| **Vultr** | $2.5/月 | 1核512M | 最便宜 |

### VPS部署步骤
```bash
# 1. 连接VPS
ssh root@您的VPS_IP

# 2. 安装Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose -y

# 3. 上传项目文件
scp -r "/Users/bizai/Desktop/项目推荐表设计" root@VPS_IP:/root/

# 4. 部署
cd "/root/项目推荐表设计"
docker-compose up -d

# 5. 配置防火墙
ufw allow 80
ufw allow 443
ufw enable
```

### 域名配置（可选）
```bash
# 修改docker-compose.yml中的nginx配置
# 将server_name改为您的域名

# 申请SSL证书（免费）
apt install certbot
certbot --standalone -d yourdomain.com

# 配置HTTPS（修改nginx.conf添加SSL配置）
```

---

## 📊 资源监控

### 查看资源使用情况
```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df

# 查看容器详细信息
docker inspect idim-system
```

### 性能优化
```bash
# 清理无用镜像和容器
docker system prune -a

# 限制容器内存使用（修改docker-compose.yml）
# 添加：
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

---

## 🔒 安全配置

### 基础安全
```bash
# 1. 修改默认密码
# 登录系统后在人员管理中修改admin密码

# 2. 配置防火墙（VPS环境）
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# 3. 定期备份
# 设置定时任务备份数据库
crontab -e
# 添加：0 2 * * * docker cp idim-system:/app/backend/database.db /backup/db-$(date +\%Y\%m\%d).db
```

### 高级安全（可选）
```bash
# 1. 使用非root用户运行
# 在Dockerfile中添加：
# RUN useradd -m -u 1001 appuser
# USER appuser

# 2. 启用HTTPS
# 配置SSL证书和HTTPS重定向

# 3. 限制访问IP
# 在nginx.conf中添加IP白名单
```

---

## 🚨 故障排除

### 常见问题

#### Q1: 容器启动失败
```bash
# 查看详细错误日志
docker-compose logs idim-app

# 检查端口占用
netstat -tlnp | grep 3001

# 重新构建镜像
docker-compose build --no-cache
```

#### Q2: 无法访问网站
```bash
# 检查容器是否运行
docker-compose ps

# 检查端口映射
docker port idim-system

# 测试本地连接
curl http://localhost:3001
```

#### Q3: 数据库错误
```bash
# 重新初始化数据库
docker-compose down
rm -f backend/database.db
docker-compose up -d

# 查看数据库文件权限
ls -la backend/database.db
```

#### Q4: 前端资源无法加载
```bash
# 重新构建前端
docker exec -it idim-system bash
cd /app/frontend
npm run build
exit
docker-compose restart
```

### 获取帮助
```bash
# 进入容器调试
docker exec -it idim-system bash

# 查看系统资源
docker stats idim-system

# 导出容器日志
docker logs idim-system > debug.log
```

---

## 🎯 部署场景推荐

### 场景1：本地开发测试
```bash
# 简单启动，用于开发和测试
docker-compose up -d
```
- **适合**：开发人员本地测试
- **访问**：http://localhost:3001

### 场景2：团队内部使用
```bash
# 局域网部署，团队成员访问
docker run -d --name idim -p 3001:5001 idim-app
```
- **适合**：小团队内部项目管理
- **访问**：http://内网IP:3001

### 场景3：正式生产环境
```bash
# 完整部署，包含Nginx反向代理
docker-compose up -d
```
- **适合**：正式对外提供服务
- **访问**：http://域名 或 http://公网IP

---

## 💡 进阶配置

### 自定义配置
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  idim-app:
    environment:
      - CUSTOM_CONFIG=value
    volumes:
      - ./custom-config:/app/config
```

### 多环境部署
```bash
# 开发环境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 生产环境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 集群部署
```yaml
# docker-compose.cluster.yml
version: '3.8'
services:
  idim-app:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
```

---

## 🎉 部署成功验证

### ✅ 检查清单
- [ ] Docker容器正常运行：`docker-compose ps`
- [ ] 网站可以正常访问：http://localhost:3001
- [ ] 登录功能正常：使用测试账号登录
- [ ] 数据持久化正常：重启容器后数据不丢失
- [ ] 所有功能模块正常：项目管理、人员管理、进度更新

### 🌟 恭喜！
您的IDIM项目管理系统已经成功部署！

**访问地址**：http://localhost:3001  
**管理员账号**：admin / td123456

---

## 📞 技术支持

### 社区支持
- **Docker官方文档**：https://docs.docker.com/
- **Docker Hub**：https://hub.docker.com/
- **GitHub Issues**：项目相关问题

### 快速联系
如有问题，请提供以下信息：
- 操作系统版本
- Docker版本：`docker --version`
- 错误日志：`docker-compose logs`
- 部署环境：本地/VPS

---

**🚀 Docker部署 - 让部署变得简单！**
