# Windows Docker部署指南

## 📋 目录
1. [准备工作](#准备工作)
2. [迁移文件](#迁移文件)
3. [安装Docker](#安装docker)
4. [部署步骤](#部署步骤)
5. [常见问题](#常见问题)

---

## 🔧 准备工作

### 在Mac上打包项目

```bash
# 1. 进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 2. 清理不需要的文件
rm -rf backend/__pycache__ backend/*/__pycache__
rm -rf backend/venv venv
rm -rf frontend/node_modules
rm -rf .DS_Store

# 3. 打包项目（保留数据）
tar -czf project-management.tar.gz \
  --exclude='*.log' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  .

# 或者不保留数据（全新开始）
tar -czf project-management-clean.tar.gz \
  --exclude='*.log' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='data' \
  .
```

打包完成后，会生成 `project-management.tar.gz` 文件。

---

## 📦 迁移文件

### 方法1：使用U盘或移动硬盘

1. 将 `project-management.tar.gz` 复制到U盘
2. 插入Windows电脑
3. 复制到 `D:\Projects\` 或任何你喜欢的位置

### 方法2：使用局域网共享

1. Mac上开启文件共享
2. Windows上访问Mac共享文件夹
3. 直接复制文件

### 方法3：使用云盘

1. 上传到百度云盘/OneDrive/Google Drive
2. 在Windows上下载

### 方法4：使用Git（推荐）

```bash
# 在Mac上
git add .
git commit -m "准备迁移到Windows"
git push

# 在Windows上
git clone <你的仓库地址>
```

---

## 🪟 安装Docker Desktop (Windows)

### 系统要求

- Windows 10/11 专业版、企业版或教育版（64位）
- 或 Windows 10/11 家庭版（需要WSL 2）
- 至少4GB内存（推荐8GB）

### 安装步骤

1. **下载Docker Desktop**
   - 访问：https://www.docker.com/products/docker-desktop/
   - 点击"Download for Windows"
   - 下载 `Docker Desktop Installer.exe`

2. **安装Docker Desktop**
   ```
   1. 双击运行安装程序
   2. 勾选 "Use WSL 2 instead of Hyper-V"（推荐）
   3. 点击 "Ok" 开始安装
   4. 安装完成后重启电脑
   ```

3. **启动Docker Desktop**
   ```
   1. 从开始菜单启动 "Docker Desktop"
   2. 等待Docker引擎启动（可能需要几分钟）
   3. 看到Docker图标变绿色表示启动成功
   ```

4. **验证安装**
   
   打开PowerShell或CMD：
   ```powershell
   docker --version
   docker compose version
   ```

   应该看到类似输出：
   ```
   Docker version 24.x.x
   Docker Compose version v2.x.x
   ```

---

## 🚀 部署步骤

### 1. 解压项目

打开PowerShell：

```powershell
# 切换到项目目录（根据实际情况修改）
cd D:\Projects

# 解压文件
tar -xzf project-management.tar.gz -C project-management

# 进入项目目录
cd project-management
```

### 2. 检查文件

```powershell
# 查看项目文件
dir

# 应该看到：
# - Dockerfile
# - docker-compose.yml
# - backend/
# - frontend/
# 等文件
```

### 3. 一键部署

**方法A：使用PowerShell脚本**

```powershell
# 创建数据目录
mkdir data, logs -Force

# 构建镜像
docker compose build

# 启动容器
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker logs -f project-management-app
```

**方法B：使用批处理脚本**

创建 `deploy.bat`：

```batch
@echo off
echo ==========================================
echo   项目管理系统 - Windows Docker部署
echo ==========================================
echo.

echo [1/4] 创建数据目录...
if not exist data mkdir data
if not exist logs mkdir logs

echo [2/4] 构建Docker镜像...
docker compose build

echo [3/4] 启动容器...
docker compose up -d

echo [4/4] 检查状态...
timeout /t 3 >nul
docker compose ps

echo.
echo ==========================================
echo   部署完成！
echo ==========================================
echo.
echo 访问地址：http://localhost:5001
echo.
echo 查看日志：docker logs -f project-management-app
echo.
pause
```

然后双击运行 `deploy.bat`

### 4. 访问系统

浏览器打开：
```
http://localhost:5001
```

使用默认账户登录：
- 用户名：`admin`
- 密码：`admin123`

---

## 🌐 Windows局域网访问

### 获取Windows IP地址

```powershell
# PowerShell
ipconfig | findstr IPv4
```

或在CMD中：
```cmd
ipconfig | find "IPv4"
```

假设IP是 `192.168.31.10`

### 局域网访问地址

```
http://192.168.31.10:5001
```

### 配置防火墙

如果局域网无法访问，需要允许端口：

```powershell
# 以管理员身份运行PowerShell

# 允许5001端口
netsh advfirewall firewall add rule name="项目管理系统" dir=in action=allow protocol=TCP localport=5001

# 查看规则
netsh advfirewall firewall show rule name="项目管理系统"
```

或通过图形界面：
1. 控制面板 → Windows Defender 防火墙
2. 高级设置 → 入站规则
3. 新建规则 → 端口 → TCP → 5001
4. 允许连接 → 完成

---

## 📝 Windows常用命令

### PowerShell命令对照

| 功能 | Mac命令 | Windows PowerShell |
|------|---------|-------------------|
| 查看文件 | `ls` | `dir` 或 `ls` |
| 切换目录 | `cd` | `cd` |
| 创建目录 | `mkdir` | `mkdir` 或 `New-Item -ItemType Directory` |
| 删除文件 | `rm` | `del` 或 `Remove-Item` |
| 查看IP | `ifconfig` | `ipconfig` |
| 查看进程 | `ps` | `Get-Process` |

### Docker命令（完全相同）

```powershell
# 启动
docker compose up -d

# 停止
docker compose down

# 重启
docker compose restart

# 查看日志
docker logs -f project-management-app

# 查看状态
docker compose ps

# 进入容器
docker exec -it project-management-app bash

# 重新构建
docker compose build --no-cache
```

---

## 🔧 常见问题

### 1. Docker Desktop无法启动

**症状：** Docker Desktop一直显示"Starting..."

**解决：**
```powershell
# 1. 重启Docker Desktop
# 右键Docker图标 → Restart

# 2. 检查WSL 2
wsl --list --verbose

# 3. 更新WSL 2
wsl --update

# 4. 重启电脑
```

### 2. 端口被占用

**症状：** `Bind for 0.0.0.0:5001 failed`

**解决：**
```powershell
# 查看占用5001端口的进程
netstat -ano | findstr :5001

# 结束进程（替换PID）
taskkill /F /PID <PID号>
```

### 3. 构建速度慢

**原因：** 网络问题，下载镜像慢

**解决：** 配置Docker镜像加速

1. Docker Desktop → Settings → Docker Engine
2. 添加镜像源：
```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```
3. Apply & Restart

### 4. 数据持久化

**数据位置：**
```
Windows: D:\Projects\project-management\data\
容器内: /app/data/
```

**备份数据：**
```powershell
# 备份数据库
copy data\project_management.db data\backup_%date:~0,4%%date:~5,2%%date:~8,2%.db
```

### 5. 权限问题

**症状：** 容器内无法写入文件

**解决：**
```powershell
# 确保data和logs目录存在且有写入权限
icacls data /grant Everyone:F
icacls logs /grant Everyone:F
```

### 6. 网络问题

**症状：** 容器无法访问网络

**解决：**
```powershell
# 重置Docker网络
docker network prune

# 重启Docker Desktop
```

---

## 📊 性能优化

### WSL 2资源限制

创建 `%USERPROFILE%\.wslconfig`：

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
```

### Docker Desktop资源配置

1. Docker Desktop → Settings → Resources
2. 调整：
   - CPUs: 2-4核
   - Memory: 4-8GB
   - Disk image size: 60GB

---

## 🎯 快速命令速查

### 部署相关
```powershell
# 完整部署
docker compose down && docker compose build && docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker logs --tail 100 project-management-app

# 重启
docker compose restart
```

### 数据管理
```powershell
# 备份数据
copy data\project_management.db backup\backup_%date%.db

# 清理重置
docker compose down
rmdir /s /q data
docker compose up -d
```

### 故障排查
```powershell
# 查看Docker信息
docker info

# 查看容器详情
docker inspect project-management-app

# 查看网络
docker network ls

# 查看资源使用
docker stats project-management-app
```

---

## 📱 移动设备访问

### 获取Windows IP
```powershell
ipconfig | findstr IPv4
```

### 手机/平板访问
1. 连接同一WiFi
2. 浏览器打开：`http://192.168.31.10:5001`
3. 使用账户登录

---

## ✅ 部署检查清单

- [ ] Docker Desktop已安装并运行
- [ ] 项目文件已解压
- [ ] 运行 `docker compose build` 成功
- [ ] 运行 `docker compose up -d` 成功
- [ ] 访问 http://localhost:5001 正常
- [ ] 可以登录系统
- [ ] 局域网访问正常（如需要）
- [ ] 防火墙已配置（如需要）
- [ ] 数据已备份（如有旧数据）

---

## 🎓 进阶配置

### 开机自启动

1. Docker Desktop → Settings → General
2. 勾选 "Start Docker Desktop when you log in"

### 使用Windows服务

创建服务（管理员权限）：
```powershell
sc create ProjectManagement binPath= "docker compose -f D:\Projects\project-management\docker-compose.yml up" start= auto
```

---

## 📞 需要帮助？

### 查看文档
- 📖 [DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md) - 完整Docker文档
- 📖 [README_DOCKER.md](./README_DOCKER.md) - Docker快速指南

### 常用命令
```powershell
# 完整日志
docker logs project-management-app

# 进入容器调试
docker exec -it project-management-app bash

# 健康检查
curl http://localhost:5001/api/health
```

---

## 🎉 部署成功！

Windows部署完成后，您将拥有：

✅ 独立运行的项目管理系统  
✅ 本地和局域网都可访问  
✅ 数据自动持久化  
✅ 与Mac版本功能完全一致  

**祝使用愉快！** 🚀

---

*最后更新：2024年10月20日*

