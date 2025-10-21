# 部门项目推进表管理系统

## 项目概述
一个简洁高效的部门项目推进表管理系统，支持多人协作，方便主管汇总所有项目进度向领导汇报。

## 功能特点
- 📊 **项目进度可视化**：清晰展示每个项目的完成进度
- 👥 **人员分工管理**：明确显示项目负责人和参与人员
- 🔄 **协作更新**：团队成员可独立更新自己负责的项目内容
- 📈 **进度汇总**：主管可一键查看所有项目整体情况
- 💾 **数据持久化**：自动保存，支持历史记录查看

## 系统架构
- **前端**：Vue3 + Element Plus（简洁美观的苹果风格设计）
- **后端**：Python Flask（DDD分层架构）
- **数据库**：SQLite（轻量级，无需额外安装）
- **部署**：本地运行，支持局域网访问

## 使用场景
- 部门约20个项目同时管理
- 每个项目1-8人参与
- 项目周期：几个月到2年不等
- 每周更新一次进度
- 主管向领导汇报使用

## 快速开始

### 🐳 Docker部署（强烈推荐）

**最简单的部署方式，一键启动，无需配置环境！**

```bash
# 1. 确保已安装Docker
docker --version

# 2. 一键部署
chmod +x deploy-docker.sh
./deploy-docker.sh

# 3. 访问系统
# http://localhost:5001
```

> 📖 详细的Docker部署文档请查看：[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)

**优势：**
- ✅ 无需安装Python、Node.js等环境
- ✅ 一条命令完成所有配置
- ✅ 数据自动持久化
- ✅ 支持局域网访问
- ✅ 适合Mac M1芯片

---

### 💻 本地开发部署

#### 方法1：一键启动脚本
```bash
# 本地开发环境
./start_local_dev.sh

# 局域网访问模式
./start_lan.sh
```

#### 方法2：手动启动
```bash
# 1. 安装Python依赖
pip3 install -r backend/requirements.txt

# 2. 启动后端服务
cd backend
python3 app.py

# 3. 在新终端窗口中，进入前端目录并安装依赖
cd frontend
npm install

# 4. 启动前端服务
npm run dev
```

### 🌐 访问系统

**Docker部署：**
- 完整系统: http://localhost:5001
- API接口: http://localhost:5001/api
- 健康检查: http://localhost:5001/api/health

**本地开发：**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:5001

**局域网访问：**
- http://你的IP地址:5001 (Docker)
- http://你的IP地址:3000 (本地开发)

## 👤 默认账户

系统首次启动会自动创建以下账户：

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 拥有所有权限 |
| 测试用户 | zhangsan | 123456 | 项目负责人 |
| 测试用户 | lisi | 123456 | 普通成员 |
| 测试用户 | wangwu | 123456 | 普通成员 |

⚠️ **重要提示**：首次登录后请立即修改默认密码！

---

## 📂 目录结构

```
项目推荐表设计/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask应用入口
│   ├── config.py              # 配置文件
│   ├── models/                # 数据模型层
│   ├── services/              # 业务逻辑层
│   ├── controllers/           # 控制器层
│   └── utils/                 # 工具函数
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia状态管理
│   │   ├── router/            # 路由配置
│   │   └── utils/             # 工具函数
│   └── dist/                  # 构建产物
├── data/                      # 数据目录（Docker）
├── logs/                      # 日志目录（Docker）
├── Dockerfile                 # Docker镜像配置
├── docker-compose.yml         # Docker编排配置
├── deploy-docker.sh          # Docker部署脚本
└── DOCKER_DEPLOY.md          # Docker部署文档
```

---

## 🚀 部署方式对比

| 特性 | Docker部署 | 本地开发 | 说明 |
|------|-----------|---------|------|
| 环境依赖 | ✅ 只需Docker | ❌ 需要Python + Node.js | Docker更简单 |
| 一键启动 | ✅ 是 | ⚠️ 需要两个终端 | Docker一个命令搞定 |
| 数据持久化 | ✅ 自动 | ⚠️ 手动配置 | Docker自动管理 |
| 局域网访问 | ✅ 开箱即用 | ⚠️ 需要配置 | Docker默认支持 |
| 适合场景 | 生产、演示、分享 | 开发调试 | 根据需求选择 |
| Mac M1支持 | ✅ 完美 | ✅ 完美 | 都支持 |

**推荐使用Docker部署！** 特别是在以下场景：
- 🎯 快速演示给他人
- 🎯 部署到服务器
- 🎯 不想折腾环境配置
- 🎯 需要局域网访问
