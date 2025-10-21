# Docker快速启动指南 🚀

> 最快5分钟完成部署！

## 📋 前置条件

✅ Mac电脑（支持M1/M2/Intel芯片）  
✅ 安装Docker Desktop

## 🎯 三步部署

### 第一步：安装Docker

```bash
# 使用Homebrew安装（推荐）
brew install --cask docker

# 启动Docker Desktop
open -a Docker
```

等待Docker Desktop启动完成（顶部菜单栏出现Docker图标）。

### 第二步：部署项目

```bash
# 进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 运行部署脚本
./deploy-docker.sh
```

选择选项 `1` 进行完整部署，等待3-5分钟。

### 第三步：访问系统

在浏览器打开：**http://localhost:5001**

使用以下账户登录：
- 用户名：`admin`
- 密码：`admin123`

## ✅ 完成！

就这么简单！系统已经运行了。

---

## 🔧 常用命令

```bash
# 查看运行状态
docker ps

# 查看日志
docker logs -f project-management-app

# 停止服务
./stop-docker.sh

# 重启服务
docker compose restart
```

---

## 🌐 局域网访问

### 获取本机IP

```bash
# Mac
ipconfig getifaddr en0
```

### 访问地址

假设IP是 `192.168.1.100`，则访问：

```
http://192.168.1.100:5001
```

局域网内的其他设备都可以通过这个地址访问！

---

## ❓ 遇到问题？

### Docker未启动

**症状**：提示 "Cannot connect to Docker daemon"

**解决**：
```bash
# 启动Docker Desktop
open -a Docker

# 等待几秒钟后重试
./deploy-docker.sh
```

### 端口被占用

**症状**：提示 "port 5001 is already allocated"

**解决**：
```bash
# 查看占用端口的进程
lsof -i :5001

# 停止该进程或修改端口
# 编辑 docker-compose.yml，改为其他端口如 "8080:5001"
```

### 无法访问

**症状**：浏览器显示无法连接

**解决**：
```bash
# 1. 检查容器是否运行
docker ps

# 2. 查看容器日志
docker logs project-management-app

# 3. 检查健康状态
curl http://localhost:5001/api/health
```

---

## 📚 更多帮助

- 📖 完整文档：[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)
- 📖 项目说明：[README.md](./README.md)

---

## 🎉 享受使用！

系统特性：
- ✨ 美观的苹果风格界面
- 📊 项目进度可视化
- 👥 团队协作管理
- 💾 数据自动保存

**登录后记得修改默认密码哦！** 🔐


