# 推送代码到GitHub

## 📋 您的GitHub仓库

**仓库地址：** https://github.com/qingpengbi-art/project-management

---

## 🔐 方法1：使用GitHub Desktop（最简单）

### 1. 安装GitHub Desktop

下载：https://desktop.github.com/

### 2. 登录GitHub账号

打开GitHub Desktop → 登录您的GitHub账号

### 3. 添加项目

```
File → Add Local Repository
选择：/Users/bizai/Desktop/项目推荐表设计
```

### 4. 推送

```
1. 确认所有文件已添加
2. 点击 "Commit to main"
3. 点击 "Push origin"
```

**完成！** ✅

---

## 🔐 方法2：使用Personal Access Token（推荐）

### 1. 生成GitHub Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选权限：
   - ✅ repo (所有子选项)
   - ✅ workflow
4. 点击 "Generate token"
5. **复制token（只显示一次！）**

### 2. 推送代码

```bash
cd /Users/bizai/Desktop/项目推荐表设计

# 使用token推送（将TOKEN替换为你的token）
git push https://TOKEN@github.com/qingpengbi-art/project-management.git main
```

**示例：**
```bash
git push https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/qingpengbi-art/project-management.git main
```

### 3. 保存凭证（可选）

```bash
# 保存token，以后不用每次输入
git config credential.helper store
git push -u origin main
# 输入用户名和token后会保存
```

---

## 🔐 方法3：使用SSH密钥

### 1. 生成SSH密钥

```bash
# 生成新密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 按Enter使用默认位置
# 可以设置密码或直接Enter跳过
```

### 2. 添加SSH密钥到GitHub

```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 或使用pbcopy直接复制到剪贴板
pbcopy < ~/.ssh/id_ed25519.pub
```

访问：https://github.com/settings/keys
- 点击 "New SSH key"
- 粘贴公钥
- 保存

### 3. 更换为SSH地址

```bash
cd /Users/bizai/Desktop/项目推荐表设计

# 更换为SSH地址
git remote set-url origin git@github.com:qingpengbi-art/project-management.git

# 推送
git push -u origin main
```

---

## ⚡ 快速推送（选择一个方法）

### 使用Token推送
```bash
cd /Users/bizai/Desktop/项目推荐表设计

# 替换YOUR_TOKEN为你的GitHub Token
git push https://YOUR_TOKEN@github.com/qingpengbi-art/project-management.git main
```

### 或使用SSH推送
```bash
cd /Users/bizai/Desktop/项目推荐表设计

# 先配置SSH密钥（见上面方法3）
git remote set-url origin git@github.com:qingpengbi-art/project-management.git
git push -u origin main
```

---

## ✅ 验证推送成功

推送后，访问：https://github.com/qingpengbi-art/project-management

应该看到：
- ✅ 所有项目文件
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ railway.json
- ✅ backend/ 和 frontend/ 目录

---

## 🚀 推送成功后 → 部署到Railway

### 1. 访问Railway

https://railway.app/

### 2. 登录

使用GitHub账号登录

### 3. 创建项目

```
Dashboard → New Project
→ Deploy from GitHub repo
→ 选择 "qingpengbi-art/project-management"
→ Deploy
```

### 4. 配置环境变量

在Railway控制台添加：

```
DATABASE_PATH = /app/data/project_management.db
FLASK_ENV = production
```

生成SECRET_KEY：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

添加到Railway：
```
SECRET_KEY = <生成的密钥>
```

### 5. 等待构建

大约5-10分钟后，Railway会提供访问地址：
```
https://project-management-production-xxxx.up.railway.app
```

---

## 🎯 推荐流程

**最简单的方式：**

1. **使用GitHub Desktop**
   - 图形界面，最简单
   - 无需配置token或SSH
   - 适合新手

2. **或使用Token（命令行）**
   ```bash
   # 生成token: https://github.com/settings/tokens
   # 推送
   git push https://YOUR_TOKEN@github.com/qingpengbi-art/project-management.git main
   ```

---

## 📞 需要帮助？

### 如果遇到错误

**错误1：认证失败**
```
解决：使用GitHub Desktop 或 重新生成Token
```

**错误2：权限被拒绝**
```
解决：确认仓库是你自己的，或配置SSH密钥
```

**错误3：网络问题**
```
解决：检查网络，或使用GitHub Desktop重试
```

---

## 📝 下一步

推送成功后：

1. ✅ 验证GitHub上有代码
2. ✅ 访问 https://railway.app/
3. ✅ 部署项目
4. ✅ 配置环境变量
5. ✅ 获得公网地址

**详细Railway部署教程：**
- [Railway部署详细教程.md](./Railway部署详细教程.md)
- [README_RAILWAY.md](./README_RAILWAY.md)

---

**选择最适合您的方法，开始推送吧！** 🚀

