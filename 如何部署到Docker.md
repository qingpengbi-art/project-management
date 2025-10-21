# 🐳 如何部署到Docker - 完整指南

> 本文档专门为您准备，包含从零开始的完整部署步骤

## 📖 目录

1. [为什么选择Docker](#为什么选择docker)
2. [准备工作](#准备工作)
3. [部署步骤](#部署步骤)
4. [验证部署](#验证部署)
5. [日常使用](#日常使用)
6. [常见问题](#常见问题)

---

## 🎯 为什么选择Docker

### 优势对比

| 特点 | Docker部署 | 传统部署 |
|------|-----------|---------|
| 环境配置 | ✅ 无需配置 | ❌ 需要安装Python、Node.js等 |
| 部署时间 | ✅ 3-5分钟 | ❌ 30分钟以上 |
| 一致性 | ✅ 所有环境完全一致 | ❌ 可能出现"在我机器上能跑" |
| 数据管理 | ✅ 自动持久化 | ⚠️ 需要手动配置 |
| 局域网访问 | ✅ 开箱即用 | ⚠️ 需要配置CORS |
| 更新升级 | ✅ 一条命令 | ❌ 多个步骤 |

### 您的Mac M1完美支持Docker！

---

## 📋 准备工作

### 第一步：安装Docker Desktop

**方法1：使用Homebrew（推荐）**

```bash
# 打开终端，执行：
brew install --cask docker
```

**方法2：手动下载**

1. 访问：https://www.docker.com/products/docker-desktop/
2. 点击 "Download for Mac - Apple Chip"
3. 下载后双击安装

### 第二步：启动Docker

```bash
# 在终端执行：
open -a Docker
```

等待Docker启动完成（顶部菜单栏会出现Docker鲸鱼图标）。

### 第三步：验证Docker安装

```bash
# 检查Docker版本
docker --version

# 应该看到类似输出：
# Docker version 24.x.x, build xxxxx
```

---

## 🚀 部署步骤

### 方法一：自动化部署（强烈推荐！）

这是最简单的方式，只需要两个命令：

```bash
# 1. 进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 2. 运行测试（可选，确保环境正常）
./test-docker.sh

# 3. 执行部署
./deploy-docker.sh
```

**操作说明：**
1. 运行 `./deploy-docker.sh` 后会出现菜单
2. 输入 `1` 选择"完整部署"
3. 等待3-5分钟（首次会下载镜像和构建）
4. 看到"部署完成"提示后即可使用

### 方法二：命令行部署

```bash
# 一键完整部署
./deploy-docker.sh deploy
```

### 方法三：手动执行（了解细节）

```bash
# 1. 创建数据目录
mkdir -p data logs

# 2. 构建Docker镜像
docker compose build

# 3. 启动容器
docker compose up -d

# 4. 查看状态
docker compose ps
```

---

## ✅ 验证部署

### 1. 检查容器状态

```bash
docker compose ps
```

应该看到：
```
NAME                        STATUS
project-management-app      Up (healthy)
```

### 2. 查看日志

```bash
docker logs project-management-app
```

应该看到：
```
✅ 数据库初始化完成！
🌟 启动Flask应用...
```

### 3. 访问系统

**本地访问：**
```
http://localhost:5001
```

**局域网访问：**

1. 获取你的Mac IP地址：
```bash
ipconfig getifaddr en0
```

2. 在浏览器访问（假设IP是192.168.1.100）：
```
http://192.168.1.100:5001
```

### 4. 登录测试

使用默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

---

## 💡 日常使用

### 启动服务

```bash
# 方法1：使用脚本
./deploy-docker.sh start

# 方法2：使用docker命令
docker compose up -d
```

### 停止服务

```bash
# 方法1：使用脚本
./stop-docker.sh

# 方法2：使用docker命令
docker compose down
```

### 重启服务

```bash
docker compose restart
```

### 查看日志

```bash
# 实时查看日志
docker logs -f project-management-app

# 查看最近100行
docker logs --tail 100 project-management-app

# 按Ctrl+C退出日志查看
```

### 查看状态

```bash
# 查看容器状态
docker compose ps

# 查看详细信息
docker inspect project-management-app

# 查看资源使用
docker stats project-management-app
```

### 进入容器调试

```bash
# 进入容器shell
docker exec -it project-management-app bash

# 在容器内可以执行：
ls /app/data          # 查看数据文件
cat /app/logs/*.log   # 查看日志
python3 --version     # 检查Python版本

# 输入exit退出容器
```

---

## 🔧 常见问题解决

### 问题1：Docker未启动

**症状：**
```
Cannot connect to the Docker daemon
```

**解决：**
```bash
# 启动Docker Desktop
open -a Docker

# 等待30秒后重试
./deploy-docker.sh
```

### 问题2：端口被占用

**症状：**
```
Bind for 0.0.0.0:5001 failed: port is already allocated
```

**解决方法1：停止占用端口的程序**
```bash
# 查看占用端口的进程
lsof -i :5001

# 记下PID，然后杀死进程（假设PID是1234）
kill -9 1234
```

**解决方法2：修改端口**
```bash
# 编辑docker-compose.yml
vi docker-compose.yml

# 找到ports配置，改为：
ports:
  - "8080:5001"  # 使用8080端口

# 重新部署
docker compose up -d
```

### 问题3：构建失败

**症状：**
```
ERROR: failed to solve...
```

**解决：**
```bash
# 清理Docker缓存
docker builder prune -a

# 确认后输入 y

# 重新构建（不使用缓存）
docker compose build --no-cache
docker compose up -d
```

### 问题4：容器启动后立即退出

**解决：**
```bash
# 查看容器日志找到错误原因
docker logs project-management-app

# 常见原因：
# 1. 数据库初始化失败
# 2. 端口冲突
# 3. 权限问题

# 重置并重新部署
docker compose down
rm -rf data/*  # 删除旧数据
docker compose up -d
```

### 问题5：无法访问网页

**检查清单：**

```bash
# 1. 确认容器运行
docker compose ps
# 应该显示 "Up (healthy)"

# 2. 检查端口映射
docker port project-management-app
# 应该显示 5001/tcp -> 0.0.0.0:5001

# 3. 测试健康检查
curl http://localhost:5001/api/health
# 应该返回 {"status":"healthy",...}

# 4. 查看日志
docker logs --tail 50 project-management-app

# 5. 重启容器
docker compose restart
```

### 问题6：前端页面空白

**解决：**
```bash
# 1. 检查前端构建
docker exec project-management-app ls -la /app/frontend/dist

# 2. 如果文件不存在，重新构建
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 问题7：局域网无法访问

**解决：**
```bash
# 1. 确认Mac防火墙设置
# 系统偏好设置 -> 安全性与隐私 -> 防火墙
# 确保允许Docker接收连接

# 2. 确认IP地址正确
ipconfig getifaddr en0

# 3. 确认同一网络
# 访问设备需要在同一WiFi/网络下

# 4. 测试连接（在Mac上）
curl http://192.168.x.x:5001/api/health
```

---

## 📊 数据管理

### 数据位置

所有数据保存在：
```
./data/project_management.db   # 数据库文件
./logs/                         # 日志文件
```

### 备份数据

```bash
# 快速备份
cp data/project_management.db data/backup_$(date +%Y%m%d).db

# 或完整备份
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/
```

### 恢复数据

```bash
# 1. 停止容器
docker compose down

# 2. 恢复数据库
cp data/backup_20241020.db data/project_management.db

# 3. 启动容器
docker compose up -d
```

### 查看数据库

```bash
# 进入容器
docker exec -it project-management-app bash

# 使用Python查看
python3 << EOF
import sqlite3
conn = sqlite3.connect('/app/data/project_management.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
EOF

# 退出容器
exit
```

---

## 🎓 进阶使用

### 自定义配置

创建 `.env` 文件：
```bash
cp .env.example .env
vi .env
```

编辑配置：
```env
SECRET_KEY=你的随机密钥
DATABASE_PATH=/app/data/project_management.db
FLASK_ENV=production
```

重新部署：
```bash
docker compose down
docker compose up -d
```

### 使用Nginx（可选）

如果需要使用80端口或HTTPS：

```bash
# 启动带Nginx的版本
docker compose --profile production up -d

# 通过80端口访问
http://localhost
```

### 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建
docker compose build

# 3. 重启容器
docker compose up -d
```

### 清理Docker资源

```bash
# 停止并删除容器
docker compose down

# 删除镜像
docker rmi $(docker images -q 项目推荐表设计*)

# 清理未使用的资源
docker system prune -a
```

---

## 📚 相关文档

- 📖 **[DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md)** - 快速开始指南
- 📖 **[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)** - 完整部署文档
- 📖 **[DOCKER使用总结.md](./DOCKER使用总结.md)** - 技术总结
- 📖 **[README.md](./README.md)** - 项目说明

---

## 🆘 获取帮助

### 快速诊断

运行测试脚本：
```bash
./test-docker.sh
```

会自动检查所有配置并给出建议。

### 命令速查表

```bash
# 部署
./deploy-docker.sh deploy

# 停止
./stop-docker.sh

# 查看状态
docker compose ps

# 查看日志
docker logs -f project-management-app

# 重启
docker compose restart

# 测试
./test-docker.sh

# 健康检查
curl http://localhost:5001/api/health
```

---

## 🎉 恭喜！

如果您已经成功部署，现在可以：

1. ✅ 在浏览器访问 http://localhost:5001
2. ✅ 使用 admin/admin123 登录
3. ✅ 修改默认密码
4. ✅ 开始管理项目
5. ✅ 分享给团队使用（局域网访问）

---

**部署愉快！** 🚀

如有任何问题，请查看上面的"常见问题解决"部分，或运行 `./test-docker.sh` 进行诊断。


