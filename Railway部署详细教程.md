# Railway 部署详细教程

## 📋 完整部署流程（10分钟搞定）

---

## 🎯 第一步：注册Railway账号

### 1. 访问Railway官网

浏览器打开：**https://railway.app/**

### 2. 使用GitHub登录（推荐）

```
1. 点击 "Login" 或 "Start a New Project"
2. 选择 "Login with GitHub"
3. 授权Railway访问GitHub
4. 完成登录
```

**为什么用GitHub？**
- ✅ 最简单，一键连接代码仓库
- ✅ 自动同步代码更新
- ✅ 支持CI/CD

---

## 📦 第二步：准备项目

### 方法A：使用GitHub（强烈推荐）

#### 1. 将项目上传到GitHub

```bash
# 在项目目录执行
cd /Users/bizai/Desktop/项目推荐表设计

# 初始化Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "准备部署到Railway"

# 创建GitHub仓库
# 访问 https://github.com/new
# 创建新仓库，比如：project-management

# 关联远程仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/project-management.git

# 推送代码
git branch -M main
git push -u origin main
```

#### 2. 优化Railway配置（可选）

创建 `railway.json`（Railway会自动识别Dockerfile）：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

```bash
# 添加配置文件
git add railway.json
git commit -m "添加Railway配置"
git push
```

### 方法B：使用Railway CLI（备选）

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
flyctl auth login

# 初始化项目
railway init

# 部署
railway up
```

---

## 🚀 第三步：在Railway上部署

### 1. 创建新项目

```
1. 登录Railway后，进入Dashboard
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
```

### 2. 连接GitHub仓库

```
1. 授权Railway访问GitHub（首次需要）
2. 在仓库列表中找到 "project-management"
3. 点击仓库名称
```

### 3. 配置项目

Railway会自动检测到Dockerfile并开始构建。

#### 配置环境变量

```
1. 点击项目
2. 进入 "Variables" 标签
3. 添加以下变量：
```

| 变量名 | 值 | 说明 |
|--------|----|----|
| `DATABASE_PATH` | `/app/data/project_management.db` | 数据库路径 |
| `SECRET_KEY` | `随机字符串` | 应用密钥 |
| `FLASK_ENV` | `production` | 运行环境 |

**生成随机SECRET_KEY：**
```bash
# Mac/Linux
openssl rand -hex 32

# 或使用Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 部署设置

```
1. Railway会自动开始构建
2. 在 "Deployments" 标签查看构建进度
3. 等待5-10分钟（首次构建较慢）
```

### 5. 获取访问地址

```
1. 构建完成后，点击 "Settings"
2. 找到 "Domains" 部分
3. 点击 "Generate Domain"
4. Railway会生成一个域名，如：
   https://project-management-production-xxxx.up.railway.app
```

---

## ✅ 第四步：验证部署

### 1. 访问应用

浏览器打开Railway生成的域名：
```
https://your-app-name.up.railway.app
```

### 2. 检查健康状态

```
https://your-app-name.up.railway.app/api/health
```

应该返回：
```json
{
  "status": "healthy",
  "message": "系统运行正常",
  "environment": "docker"
}
```

### 3. 测试登录

- 用户名：`admin`
- 密码：`admin123`

### 4. 查看日志

```
Railway控制台 → Deployments → 点击最新部署 → View Logs
```

---

## 🔧 第五步：配置优化

### 1. 持久化存储（重要！）

Railway默认不持久化数据，需要配置Volume：

```
1. 项目页面 → Settings → Volumes
2. 点击 "New Volume"
3. 配置：
   - Mount Path: /app/data
   - Size: 1GB
4. Save
```

**注意：** 免费版可能不支持Volume，数据会在重启后丢失。解决方案：
- 使用外部数据库（如Railway的PostgreSQL插件）
- 或考虑使用付费版

### 2. 配置自定义域名（可选）

如果你有自己的域名：

```
1. Settings → Domains
2. 点击 "Custom Domain"
3. 输入域名：app.yourdomain.com
4. 按提示配置DNS记录
```

### 3. 设置健康检查

在 `railway.json` 中添加：

```json
{
  "deploy": {
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100
  }
}
```

### 4. 配置自动部署

```
1. Settings → Service
2. 找到 "Deploy Triggers"
3. 确保 "Enable automatic deployments" 开启
4. 每次push代码到GitHub，Railway会自动重新部署
```

---

## 📊 监控和管理

### 查看日志

```
1. Deployments → 选择部署
2. 点击 "View Logs"
3. 实时查看应用日志
```

### 查看资源使用

```
1. 项目页面查看：
   - CPU使用率
   - 内存使用
   - 网络流量
   - 运行时间
```

### 重启应用

```
Settings → Service → Restart
```

### 回滚版本

```
Deployments → 选择历史版本 → Redeploy
```

---

## 💡 常见问题解决

### 问题1：构建失败

**症状：** Build Failed

**解决：**
```
1. 查看构建日志
2. 常见原因：
   - Dockerfile路径错误
   - 依赖安装失败
   - 内存不足

3. 解决方法：
   - 检查Dockerfile语法
   - 优化依赖安装
   - 清理Docker缓存
```

### 问题2：应用启动失败

**症状：** Application Error

**解决：**
```
1. 查看应用日志
2. 检查环境变量是否正确
3. 确认端口配置（Railway需要使用PORT环境变量）
```

修改 `backend/app.py` 末尾：
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # 生产环境关闭debug
    )
```

### 问题3：数据丢失

**症状：** 重启后数据没了

**原因：** Railway免费版不持久化

**解决方案：**

#### 方案A：使用Railway的PostgreSQL（推荐）

```
1. 项目页面 → New → Database → PostgreSQL
2. Railway会自动创建数据库
3. 修改代码使用PostgreSQL
```

修改 `backend/requirements.txt`：
```
psycopg2-binary==2.9.9
```

修改 `backend/app.py`：
```python
# 如果有DATABASE_URL环境变量，使用PostgreSQL
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # 否则使用SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = '...'
```

#### 方案B：外部备份

定期导出数据：
```bash
# 本地备份
docker exec project-management-app sqlite3 /app/data/project_management.db .dump > backup.sql
```

### 问题4：访问超时

**症状：** 504 Gateway Timeout

**解决：**
```
1. 检查应用是否正常运行
2. 查看日志是否有错误
3. 增加启动等待时间
```

### 问题5：超出免费额度

**症状：** Service suspended

**解决方案：**
```
选项1：升级到付费版（$5/月）
选项2：使用多个Railway账号轮换
选项3：配合Render等其他免费平台使用
```

---

## 📈 Railway使用技巧

### 1. 多环境部署

```
1. 创建多个分支：main, staging, dev
2. 在Railway创建对应项目
3. 连接不同分支
4. 实现：
   - main → 生产环境
   - staging → 测试环境
```

### 2. 团队协作

```
Settings → Members → Invite team members
```

### 3. 查看使用量

```
Account → Usage
查看当前月使用时长
```

### 4. 设置告警

```
Settings → Notifications
配置部署失败通知
```

---

## 🎯 完整流程总结

```bash
# 第1步：准备代码
git init
git add .
git commit -m "Initial commit"
git push

# 第2步：Railway部署
1. 访问 railway.app
2. GitHub登录
3. 选择仓库
4. 等待构建

# 第3步：配置
1. 添加环境变量
2. 生成域名
3. 配置Volume（如需要）

# 第4步：访问
https://your-app.railway.app
```

**总耗时：10-15分钟**

---

## 📝 检查清单

部署前：
- [ ] 代码已推送到GitHub
- [ ] Dockerfile存在且正确
- [ ] docker-compose.yml配置正确
- [ ] Railway账号已注册

部署后：
- [ ] 构建成功
- [ ] 应用正常运行
- [ ] 可以访问域名
- [ ] 登录功能正常
- [ ] 环境变量已配置
- [ ] 日志无错误

---

## 🎓 进阶优化

### 1. 使用Railway CLI管理

```bash
# 安装CLI
npm install -g @railway/cli

# 登录
railway login

# 查看项目
railway list

# 查看日志
railway logs

# 打开控制台
railway open
```

### 2. 配置CI/CD

创建 `.github/workflows/railway.yml`：

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railwayapp/railway-deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
```

### 3. 环境变量管理

```bash
# 本地测试时使用.env文件
# Railway上使用Web界面配置

# .env.example 示例
DATABASE_PATH=/app/data/project_management.db
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

---

## 💰 费用说明

### 免费版

- ✅ 500小时/月（约21天）
- ✅ 512MB内存
- ✅ 1GB磁盘
- ✅ 无限项目数
- ✅ 自动HTTPS

### 付费版（$5/月）

- ✅ 无限制运行时间
- ✅ 8GB内存
- ✅ 100GB磁盘
- ✅ 优先支持

### 节省技巧

1. **使用多个免费账号**（轮换使用）
2. **配合其他免费平台**（如Render）
3. **只在需要时开启**（停止不用的项目）

---

## 🔗 有用的链接

- 📖 Railway官方文档：https://docs.railway.app/
- 💬 Railway Discord社区：https://discord.gg/railway
- 🐛 问题反馈：https://github.com/railwayapp/railway-cli/issues
- 📊 状态页面：https://status.railway.app/

---

## 🎉 部署成功！

如果一切顺利，您现在应该有：

✅ 一个公网可访问的应用  
✅ 自动HTTPS域名  
✅ 自动部署配置  
✅ 免费使用500小时/月  

**访问地址示例：**
```
https://project-management-production-xxxx.up.railway.app
```

**下一步：**
1. 修改默认密码
2. 添加其他用户
3. 开始使用系统
4. 定期备份数据

---

**需要帮助？** 

遇到问题可以：
1. 查看Railway日志
2. 检查本教程的"常见问题"部分
3. 访问Railway Discord社区
4. 或者告诉我具体错误信息

**祝部署成功！** 🚀

