# 🐳 Docker部署 - 一键启动指南

## ⚡ 快速开始（只需2步）

```bash
# 第1步：运行部署脚本
./deploy-docker.sh

# 第2步：选择 1（完整部署）
# 等待3-5分钟...

# 完成！访问 http://localhost:5001
```

---

## 📚 文档导航

根据您的需求选择合适的文档：

### 🚀 我想快速部署
➡️ 阅读：[DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md)  
⏱️ 用时：5分钟

### 📖 我想了解详细步骤
➡️ 阅读：[如何部署到Docker.md](./如何部署到Docker.md)  
⏱️ 用时：15分钟

### 🔧 我想深入了解技术细节
➡️ 阅读：[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)  
⏱️ 用时：30分钟

### 📊 我想了解整体架构
➡️ 阅读：[DOCKER使用总结.md](./DOCKER使用总结.md)  
⏱️ 用时：20分钟

### ✅ 查看完成情况
➡️ 阅读：[Docker部署完成说明.md](./Docker部署完成说明.md)

---

## 🎯 一键命令

```bash
# 🚀 部署（首次或更新）
./deploy-docker.sh deploy

# 🛑 停止服务
./stop-docker.sh

# 🔄 重启服务
docker compose restart

# 📊 查看状态
docker compose ps

# 📝 查看日志
docker logs -f project-management-app

# 🧪 环境测试
./test-docker.sh

# 💚 健康检查
curl http://localhost:5001/api/health
```

---

## 📋 前置要求

- ✅ Mac电脑（M1/M2/Intel都支持）
- ✅ 安装Docker Desktop
- ✅ 磁盘空间 > 2GB
- ✅ 端口5001未被占用

### 安装Docker

```bash
# 使用Homebrew安装
brew install --cask docker

# 启动Docker
open -a Docker
```

---

## 🌐 访问地址

**本地访问：**
```
http://localhost:5001
```

**局域网访问：**
```bash
# 获取IP地址
ipconfig getifaddr en0

# 访问地址（假设IP是192.168.1.100）
http://192.168.1.100:5001
```

---

## 👤 默认账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| zhangsan | 123456 | 测试用户 |
| lisi | 123456 | 测试用户 |
| wangwu | 123456 | 测试用户 |

⚠️ **重要**：首次登录后请立即修改密码！

---

## 🎁 Docker部署优势

| 特点 | 说明 |
|------|------|
| ⚡ 超级简单 | 一条命令完成部署 |
| 🎯 环境干净 | 无需安装Python、Node.js |
| 💾 数据安全 | 自动持久化，不会丢失 |
| 🌐 局域网访问 | 开箱即用 |
| 🔄 易于更新 | 一键更新代码 |
| 🍎 M1完美支持 | 原生适配 |

---

## 🐛 遇到问题？

### 快速诊断
```bash
./test-docker.sh
```

### 常见问题

**1. Docker未启动**
```bash
open -a Docker
```

**2. 端口被占用**
```bash
lsof -i :5001
```

**3. 查看错误日志**
```bash
docker logs project-management-app
```

**4. 重新初始化**
```bash
docker compose down
rm -rf data/*
./deploy-docker.sh deploy
```

更多问题请查看：[如何部署到Docker.md - 常见问题](./如何部署到Docker.md#常见问题解决)

---

## 📂 项目结构

```
项目推荐表设计/
├── 📜 Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── 🚀 部署脚本
│   ├── deploy-docker.sh      ⭐ 一键部署
│   ├── stop-docker.sh
│   ├── docker-start.sh
│   └── test-docker.sh
│
├── 📖 文档
│   ├── README_DOCKER.md      ⭐ 本文档
│   ├── DOCKER_QUICKSTART.md  ⭐ 快速入门
│   ├── 如何部署到Docker.md   ⭐ 详细指南
│   ├── DOCKER_DEPLOY.md
│   └── DOCKER使用总结.md
│
└── 💾 数据（运行时创建）
    ├── data/   # 数据库
    └── logs/   # 日志
```

---

## 🎓 学习路径

### 初学者
1. 看这个文档（你正在看）
2. 运行 `./deploy-docker.sh`
3. 访问 http://localhost:5001
4. 开始使用 ✨

### 想了解更多
1. [DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md) - 快速入门
2. [如何部署到Docker.md](./如何部署到Docker.md) - 详细步骤
3. [DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md) - 完整文档

---

## 💡 使用技巧

### 备份数据
```bash
cp data/project_management.db backup_$(date +%Y%m%d).db
```

### 查看实时日志
```bash
docker logs -f project-management-app
```

### 进入容器调试
```bash
docker exec -it project-management-app bash
```

### 监控资源
```bash
docker stats project-management-app
```

---

## 🎉 开始使用

现在就试试吧！

```bash
cd /Users/bizai/Desktop/项目推荐表设计
./deploy-docker.sh
```

3-5分钟后，您的项目管理系统就可以使用了！

**祝您使用愉快！** 🚀

---

## 🔗 相关链接

- 📖 [主README](./README.md) - 项目说明
- 📖 [快速入门](./DOCKER_QUICKSTART.md) - 5分钟部署
- 📖 [详细指南](./如何部署到Docker.md) - 完整步骤
- 📖 [技术文档](./DOCKER_DEPLOY.md) - 深入了解
- 📖 [使用总结](./DOCKER使用总结.md) - 架构说明

---

*最后更新：2024年10月20日*

