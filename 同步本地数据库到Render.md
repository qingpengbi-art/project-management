# 🔄 同步本地数据库到 Render

## 📋 目标

将本地的 SQLite 数据库同步到 Render 上的生产环境。

---

## ⚠️ 重要提示

**操作前必读：**
- ✅ 这个操作会**替换** Render 上的所有数据
- ⚠️ 建议先备份 Render 上的现有数据
- 📊 确保本地数据库是最新的、完整的

---

## 🎯 方法一：导出本地数据，通过 API 导入（推荐）⭐

这是最安全、最灵活的方法。

### 第1步：导出本地数据

创建导出脚本 `export_database.py`：

```python
"""
导出数据库数据为 JSON 格式
"""
import json
import sys
sys.path.insert(0, './backend')

from backend.models.database import db, User, Project, ProjectModule, ModuleAssignment, ModuleWorkRecord, ProjectMember
from backend.app import create_app

def export_data():
    """导出所有数据"""
    app = create_app()
    
    with app.app_context():
        data = {
            'users': [],
            'projects': [],
            'project_members': [],
            'modules': [],
            'module_assignments': [],
            'work_records': []
        }
        
        # 导出用户
        print("导出用户...")
        users = User.query.all()
        for user in users:
            data['users'].append({
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'password_hash': user.password_hash,  # 直接导出加密后的密码
                'email': user.email,
                'position': user.position,
                'role': user.role.value if user.role else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        print(f"✅ 导出 {len(data['users'])} 个用户")
        
        # 导出项目
        print("导出项目...")
        projects = Project.query.all()
        for project in projects:
            data['projects'].append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'status': project.status.value if project.status else None,
                'progress': project.progress,
                'project_source': project.project_source,
                'partner': project.partner,
                'amount': project.amount,
                'created_at': project.created_at.isoformat() if project.created_at else None
            })
        print(f"✅ 导出 {len(data['projects'])} 个项目")
        
        # 导出项目成员
        print("导出项目成员...")
        members = ProjectMember.query.all()
        for member in members:
            data['project_members'].append({
                'id': member.id,
                'project_id': member.project_id,
                'user_id': member.user_id,
                'role': member.role.value if member.role else None,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None
            })
        print(f"✅ 导出 {len(data['project_members'])} 条项目成员记录")
        
        # 导出模块
        print("导出模块...")
        modules = ProjectModule.query.all()
        for module in modules:
            data['modules'].append({
                'id': module.id,
                'project_id': module.project_id,
                'name': module.name,
                'description': module.description,
                'assigned_to_id': module.assigned_to_id,
                'progress': module.progress,
                'start_date': module.start_date.isoformat() if module.start_date else None,
                'end_date': module.end_date.isoformat() if module.end_date else None,
                'status': module.status.value if module.status else None,
                'created_at': module.created_at.isoformat() if module.created_at else None
            })
        print(f"✅ 导出 {len(data['modules'])} 个模块")
        
        # 导出模块分配
        print("导出模块分配...")
        assignments = ModuleAssignment.query.all()
        for assignment in assignments:
            data['module_assignments'].append({
                'id': assignment.id,
                'module_id': assignment.module_id,
                'user_id': assignment.user_id,
                'role': assignment.role,
                'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None
            })
        print(f"✅ 导出 {len(data['module_assignments'])} 条模块分配记录")
        
        # 导出工作记录
        print("导出工作记录...")
        records = ModuleWorkRecord.query.all()
        for record in records:
            data['work_records'].append({
                'id': record.id,
                'module_id': record.module_id,
                'week_start': record.week_start.isoformat() if record.week_start else None,
                'week_end': record.week_end.isoformat() if record.week_end else None,
                'work_content': record.work_content,
                'achievements': record.achievements,
                'issues': record.issues,
                'next_week_plan': record.next_week_plan,
                'created_by_id': record.created_by_id,
                'created_at': record.created_at.isoformat() if record.created_at else None
            })
        print(f"✅ 导出 {len(data['work_records'])} 条工作记录")
        
        # 保存为 JSON 文件
        with open('database_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print("✅ 数据导出完成！")
        print(f"📁 文件位置：database_export.json")
        print("="*50)
        
        return data

if __name__ == '__main__':
    export_data()
```

### 第2步：执行导出

```bash
cd /Users/bizai/Desktop/项目推荐表设计
python3 export_database.py
```

这会生成 `database_export.json` 文件。

### 第3步：创建导入脚本

创建 `import_database.py`：

```python
"""
从 JSON 文件导入数据到数据库
警告：这会清空现有数据！
"""
import json
import sys
from datetime import datetime
sys.path.insert(0, './backend')

from backend.models.database import db, User, Project, ProjectModule, ModuleAssignment, ModuleWorkRecord, ProjectMember, UserRole, ProjectStatus, ModuleStatus, ProjectMemberRole
from backend.app import create_app

def import_data(json_file='database_export.json'):
    """从 JSON 文件导入数据"""
    app = create_app()
    
    with app.app_context():
        # 读取 JSON 文件
        print("📖 读取数据文件...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 确认操作
        print("\n" + "⚠️ "*20)
        print("⚠️  警告：此操作将清空现有数据库并导入新数据！")
        print("⚠️ "*20)
        response = input("\n确认继续？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 操作已取消")
            return
        
        # 清空现有数据（按照外键依赖顺序）
        print("\n🗑️  清空现有数据...")
        ModuleWorkRecord.query.delete()
        ModuleAssignment.query.delete()
        ProjectModule.query.delete()
        ProjectMember.query.delete()
        Project.query.delete()
        User.query.delete()
        db.session.commit()
        print("✅ 现有数据已清空")
        
        # 导入用户
        print("\n👥 导入用户...")
        for user_data in data['users']:
            user = User(
                id=user_data['id'],
                name=user_data['name'],
                username=user_data['username'],
                email=user_data['email'],
                position=user_data['position'],
                role=UserRole(user_data['role']) if user_data['role'] else UserRole.MEMBER,
                created_at=datetime.fromisoformat(user_data['created_at']) if user_data['created_at'] else None
            )
            user.password_hash = user_data['password_hash']  # 直接设置加密后的密码
            db.session.add(user)
        db.session.commit()
        print(f"✅ 导入 {len(data['users'])} 个用户")
        
        # 导入项目
        print("\n📁 导入项目...")
        for project_data in data['projects']:
            project = Project(
                id=project_data['id'],
                name=project_data['name'],
                description=project_data['description'],
                start_date=datetime.fromisoformat(project_data['start_date']).date() if project_data['start_date'] else None,
                end_date=datetime.fromisoformat(project_data['end_date']).date() if project_data['end_date'] else None,
                status=ProjectStatus(project_data['status']) if project_data['status'] else ProjectStatus.INITIAL_CONTACT,
                progress=project_data['progress'],
                project_source=project_data['project_source'],
                partner=project_data['partner'],
                amount=project_data['amount'],
                created_at=datetime.fromisoformat(project_data['created_at']) if project_data['created_at'] else None
            )
            db.session.add(project)
        db.session.commit()
        print(f"✅ 导入 {len(data['projects'])} 个项目")
        
        # 导入项目成员
        print("\n👤 导入项目成员...")
        for member_data in data['project_members']:
            member = ProjectMember(
                id=member_data['id'],
                project_id=member_data['project_id'],
                user_id=member_data['user_id'],
                role=ProjectMemberRole(member_data['role']) if member_data['role'] else ProjectMemberRole.MEMBER,
                joined_at=datetime.fromisoformat(member_data['joined_at']) if member_data['joined_at'] else None
            )
            db.session.add(member)
        db.session.commit()
        print(f"✅ 导入 {len(data['project_members'])} 条项目成员记录")
        
        # 导入模块
        print("\n📦 导入模块...")
        for module_data in data['modules']:
            module = ProjectModule(
                id=module_data['id'],
                project_id=module_data['project_id'],
                name=module_data['name'],
                description=module_data['description'],
                assigned_to_id=module_data['assigned_to_id'],
                progress=module_data['progress'],
                start_date=datetime.fromisoformat(module_data['start_date']).date() if module_data['start_date'] else None,
                end_date=datetime.fromisoformat(module_data['end_date']).date() if module_data['end_date'] else None,
                status=ModuleStatus(module_data['status']) if module_data['status'] else ModuleStatus.NOT_STARTED,
                created_at=datetime.fromisoformat(module_data['created_at']) if module_data['created_at'] else None
            )
            db.session.add(module)
        db.session.commit()
        print(f"✅ 导入 {len(data['modules'])} 个模块")
        
        # 导入模块分配
        print("\n🔗 导入模块分配...")
        for assignment_data in data['module_assignments']:
            assignment = ModuleAssignment(
                id=assignment_data['id'],
                module_id=assignment_data['module_id'],
                user_id=assignment_data['user_id'],
                role=assignment_data['role'],
                assigned_at=datetime.fromisoformat(assignment_data['assigned_at']) if assignment_data['assigned_at'] else None
            )
            db.session.add(assignment)
        db.session.commit()
        print(f"✅ 导入 {len(data['module_assignments'])} 条模块分配记录")
        
        # 导入工作记录
        print("\n📝 导入工作记录...")
        for record_data in data['work_records']:
            record = ModuleWorkRecord(
                id=record_data['id'],
                module_id=record_data['module_id'],
                week_start=datetime.fromisoformat(record_data['week_start']).date() if record_data['week_start'] else None,
                week_end=datetime.fromisoformat(record_data['week_end']).date() if record_data['week_end'] else None,
                work_content=record_data['work_content'],
                achievements=record_data['achievements'],
                issues=record_data['issues'],
                next_week_plan=record_data['next_week_plan'],
                created_by_id=record_data['created_by_id'],
                created_at=datetime.fromisoformat(record_data['created_at']) if record_data['created_at'] else None
            )
            db.session.add(record)
        db.session.commit()
        print(f"✅ 导入 {len(data['work_records'])} 条工作记录")
        
        print("\n" + "="*50)
        print("🎉 数据导入完成！")
        print("="*50)

if __name__ == '__main__':
    import_data()
```

### 第4步：在 Render 上执行导入

有两种方式：

#### 方式A：使用 Render Shell（推荐）

1. **访问 Render Dashboard**
2. 选择你的服务
3. 点击 **"Shell"** 标签（右上角）
4. 上传 `database_export.json` 文件到服务器
5. 执行导入命令：
```bash
python3 import_database.py
```

#### 方式B：通过部署脚本

创建 `deploy_with_data.sh`：

```bash
#!/bin/bash
# 部署并导入数据

echo "📦 构建 Docker 镜像..."
docker build -t project-management .

echo "🚀 启动容器..."
docker run -d -p 5001:5001 \
  -v $(pwd)/database_export.json:/app/database_export.json \
  -v $(pwd)/data:/app/data \
  --name project-management \
  project-management

echo "⏳ 等待服务启动..."
sleep 5

echo "📥 导入数据..."
docker exec -it project-management python3 import_database.py

echo "✅ 完成！"
```

---

## 🎯 方法二：直接替换数据库文件

这个方法更简单但需要小心操作。

### 第1步：找到本地数据库文件

```bash
# 通常在以下位置之一：
/Users/bizai/Desktop/项目推荐表设计/backend/project_management.db
/Users/bizai/Desktop/项目推荐表设计/data/project_management.db
```

### 第2步：备份 Render 上的数据库

首先备份现有数据：

```bash
# 在 Render Shell 中
cp /app/data/project_management.db /app/data/project_management.db.backup
```

### 第3步：使用 Render Disk

Render 提供持久化存储，你需要：

1. **创建 Render Disk**（如果还没有）
   - Dashboard → 你的服务 → Disks
   - 点击 "Add Disk"
   - Mount Path: `/app/data`
   - Size: 1GB（免费）

2. **通过 SSH 上传数据库**

创建上传脚本 `upload_database.sh`：

```bash
#!/bin/bash
# 上传本地数据库到 Render

# Render 服务信息
RENDER_SERVICE="your-service-name"
RENDER_REGION="singapore"

# 本地数据库路径
LOCAL_DB="/Users/bizai/Desktop/项目推荐表设计/backend/project_management.db"

# 使用 Render Shell API 上传
echo "📤 上传数据库文件..."
# 注意：这需要 Render CLI 工具

# 或者使用 SCP（如果配置了 SSH）
# scp $LOCAL_DB render:/app/data/project_management.db

echo "✅ 上传完成！"
```

---

## 🎯 方法三：使用 Git（最简单但有限制）⭐⭐

如果数据库文件不大（< 100MB），可以直接通过 Git：

### 第1步：复制数据库到项目目录

```bash
cd /Users/bizai/Desktop/项目推荐表设计

# 创建 data 目录（如果不存在）
mkdir -p data

# 复制数据库文件
cp backend/project_management.db data/project_management.db
```

### 第2步：更新 .gitignore

确保 `data/project_management.db` 不在 `.gitignore` 中：

```bash
# 检查 .gitignore
cat .gitignore | grep project_management.db

# 如果存在，移除该行
```

### 第3步：提交并推送

```bash
git add data/project_management.db
git commit -m "更新数据库文件"
git push origin main
```

### ⚠️ 限制

- 数据库文件必须 < 100MB
- 每次更新都会提交到 Git 历史
- 不适合频繁更新

---

## 📋 推荐流程（完整步骤）

### 准备工作

1. ✅ 确保本地数据库是最新的
2. ✅ 导出本地数据为 JSON
3. ✅ 备份 Render 上的数据（以防万一）

### 执行同步

```bash
# 1. 导出本地数据
cd /Users/bizai/Desktop/项目推荐表设计
python3 export_database.py

# 2. 提交导出文件到 Git
git add database_export.json import_database.py
git commit -m "添加数据导入导出脚本"
git push origin main

# 3. 等待 Render 自动部署完成

# 4. 在 Render Shell 中执行导入
# Dashboard → Shell → 运行：
python3 import_database.py
```

### 验证结果

1. 访问你的 Render 应用
2. 登录检查数据
3. 确认所有项目、用户、模块都已同步

---

## 🐛 常见问题

### 问题1：数据库文件太大

**解决方案：**
- 使用方法一（JSON 导出导入）
- 清理不必要的历史记录
- 使用数据压缩

### 问题2：导入失败（外键约束）

**解决方案：**
```python
# 在导入前禁用外键检查
db.session.execute('PRAGMA foreign_keys=OFF')
# 导入数据...
db.session.execute('PRAGMA foreign_keys=ON')
```

### 问题3：Render Disk 配置问题

**检查配置：**
```bash
# 在 Render Dashboard
Settings → Disks
确认：
- Mount Path: /app/data
- Size: 至少 1GB
```

### 问题4：数据库版本不兼容

**解决方案：**
```bash
# 升级数据库结构
flask db upgrade
```

---

## 💡 最佳实践

### 1. 定期备份

创建自动备份脚本：

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/app/backups"
DB_FILE="/app/data/project_management.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/db_backup_$DATE.db"

# 只保留最近7天的备份
find $BACKUP_DIR -name "db_backup_*.db" -mtime +7 -delete

echo "✅ 备份完成: db_backup_$DATE.db"
```

### 2. 使用环境变量

```python
# 区分本地和生产环境
import os

if os.getenv('FLASK_ENV') == 'production':
    DB_PATH = '/app/data/project_management.db'
else:
    DB_PATH = './backend/project_management.db'
```

### 3. 数据验证

导入后验证数据完整性：

```python
def validate_data():
    """验证数据完整性"""
    checks = [
        ('用户数量', User.query.count()),
        ('项目数量', Project.query.count()),
        ('模块数量', ProjectModule.query.count()),
        ('工作记录', ModuleWorkRecord.query.count())
    ]
    
    for name, count in checks:
        print(f"✅ {name}: {count}")
```

---

## 🎉 完成！

选择最适合你的方法：

- **方法一（推荐）**：JSON 导出导入 - 最安全、最灵活
- **方法二**：直接替换 - 最快但需要配置 Disk
- **方法三**：通过 Git - 最简单但有大小限制

---

**最后更新：** 2025-11-03

