# 🔄 重新部署Docker - 快速指南

## 📋 所有问题已修复！

已修复的问题：
1. ✅ 添加了缺少的 `pypinyin` 依赖
2. ✅ 修复了 `Module` 导入错误（改为 `ProjectModule`）
3. ✅ 修复了 `User` 模型字段错误（`chinese_name` → `name`）
4. ✅ 添加了 `UserRole` 枚举导入
5. ✅ 修复了用户角色配置

---

## 🚀 重新部署步骤

### 方法一：完全清理后重新部署（推荐）

```bash
# 1. 停止并删除旧容器
docker compose down

# 2. 清理旧数据（如果需要全新开始）
rm -rf data/*

# 3. 重新构建镜像（使用最新代码）
docker compose build --no-cache

# 4. 启动容器
docker compose up -d

# 5. 查看启动日志
docker logs -f project-management-app
```

### 方法二：使用部署脚本

```bash
# 停止旧容器
docker compose down

# 清理数据
rm -rf data/*

# 使用脚本重新部署
./deploy-docker.sh deploy
```

---

## ✅ 预期输出

部署成功后，应该看到：

```
==========================================
🚀 启动IDIM项目管理系统 (Docker版)
==========================================

📁 数据目录: /app/data
📝 日志目录: /app/logs
💾 数据库路径: /app/data/project_management.db

📊 数据库不存在，开始初始化...
✅ 数据库表创建完成
✅ 默认管理员用户创建成功
   用户名: admin
   密码: admin123
   请登录后立即修改密码！
✅ 测试用户创建完成
✅ 数据库初始化完成！

==========================================
✅ 数据库初始化成功！
==========================================

📋 默认账户信息：
   管理员 - 用户名: admin, 密码: admin123
   测试用户 - 用户名: zhangsan/lisi/wangwu, 密码: 123456

⚠️  请登录后立即修改默认密码！
==========================================

🌟 启动Flask应用...
==========================================

📊 数据库路径: sqlite:////app/data/project_management.db
🌐 CORS配置: 允许所有来源访问（Docker模式）
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://172.x.x.x:5001
```

---

## 🧪 验证部署

### 1. 检查容器状态

```bash
docker compose ps
```

应该显示：
```
NAME                        STATUS
project-management-app      Up (healthy)
```

### 2. 测试健康检查

```bash
curl http://localhost:5001/api/health
```

应该返回：
```json
{
  "status": "healthy",
  "message": "系统运行正常",
  "environment": "docker"
}
```

### 3. 访问前端

在浏览器打开：
```
http://localhost:5001
```

### 4. 测试登录

使用默认账户登录：
- 用户名：`admin`
- 密码：`admin123`

---

## 🎯 如果还有问题

### 查看详细日志

```bash
# 查看完整日志
docker logs project-management-app

# 实时查看日志
docker logs -f project-management-app

# 查看最近100行
docker logs --tail 100 project-management-app
```

### 进入容器调试

```bash
# 进入容器
docker exec -it project-management-app bash

# 检查Python包
pip list | grep pypinyin

# 检查文件
ls -la /app/backend/
ls -la /app/data/

# 退出容器
exit
```

### 完全重置

```bash
# 停止容器
docker compose down

# 删除所有相关镜像
docker rmi $(docker images | grep project-management | awk '{print $3}')

# 清理数据
rm -rf data/* logs/*

# 清理Docker缓存
docker builder prune -a

# 重新开始
./deploy-docker.sh deploy
```

---

## 📊 修复内容总结

### 修改的文件

1. **backend/requirements.txt**
   - ✅ 添加 `pypinyin==0.51.0`

2. **docker-start.sh**
   - ✅ 修复导入：`Module` → `ProjectModule`
   - ✅ 添加导入：`UserRole`
   - ✅ 修复字段：`chinese_name` → `name`
   - ✅ 修复角色：使用 `UserRole` 枚举
   - ✅ 添加 `email` 字段

3. **docker-compose.yml**
   - ✅ 添加项目名称配置

4. **backend/app.py**
   - ✅ 支持Docker环境检测
   - ✅ 自动配置CORS
   - ✅ 静态文件服务

---

## 🎉 部署成功标志

当你看到以下内容时，说明部署成功：

1. ✅ 容器状态显示 `Up (healthy)`
2. ✅ 健康检查返回 `{"status": "healthy"}`
3. ✅ 可以访问 http://localhost:5001
4. ✅ 可以使用 admin/admin123 登录
5. ✅ 日志没有错误信息

---

## 📱 访问方式

### 本地访问
```
http://localhost:5001
```

### 局域网访问

1. 获取IP：
```bash
ipconfig getifaddr en0
```

2. 访问（假设IP是192.168.1.100）：
```
http://192.168.1.100:5001
```

---

## 🎓 后续操作

1. ✅ 登录系统
2. ✅ 修改默认密码
3. ✅ 创建新用户
4. ✅ 开始使用
5. ✅ 配置定期备份

---

## 💾 数据备份

部署成功后，建议立即配置备份：

```bash
# 手动备份
cp data/project_management.db backup_$(date +%Y%m%d_%H%M%S).db

# 或使用脚本
echo '#!/bin/bash' > backup.sh
echo 'cp data/project_management.db backup_$(date +%Y%m%d_%H%M%S).db' >> backup.sh
chmod +x backup.sh
```

---

## 📞 需要帮助？

如果重新部署后仍有问题：

1. 📖 查看 [Docker修复说明.md](./Docker修复说明.md)
2. 📖 查看 [如何部署到Docker.md](./如何部署到Docker.md)
3. 🧪 运行 `./test-docker.sh` 进行诊断
4. 📝 查看日志 `docker logs project-management-app`

---

**祝重新部署成功！** 🚀

现在所有依赖都已完整，应该可以正常启动了！

