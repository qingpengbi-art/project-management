# Docker部署脚本修复说明

## 🔧 修复的问题

### 问题1：缺少pypinyin依赖
**错误信息：**
```
ModuleNotFoundError: No module named 'pypinyin'
```

**原因：** `backend/requirements.txt` 中缺少 `pypinyin` 包

**修复：** 在 `backend/requirements.txt` 中添加：
```
pypinyin==0.51.0
```

---

### 问题2：导入错误
**错误信息：**
```
ImportError: cannot import name 'Module' from 'models.database'
```

**原因：** `docker-start.sh` 中导入了不存在的 `Module`，应该是 `ProjectModule`

**修复：**
```python
# 修复前
from models.database import db, User, Project, Module

# 修复后
from models.database import db, User, Project, ProjectModule, UserRole
```

---

### 问题3：User模型字段错误
**错误信息：**
```
TypeError: 'chinese_name' is an invalid keyword argument for User
```

**原因：** User模型中没有 `chinese_name` 字段，正确的字段名是 `name`

**修复：**
```python
# 修复前
admin = User(
    username='admin',
    chinese_name='系统管理员',  # ❌ 错误字段
    password_hash=generate_password_hash('admin123'),
    role='admin',  # ❌ 错误：应该是枚举
    is_active=True  # ❌ 错误：User模型中没有此字段
)

# 修复后
admin = User(
    name='系统管理员',  # ✅ 正确字段
    username='admin',
    password_hash=generate_password_hash('admin123'),
    role=UserRole.DEPARTMENT_MANAGER,  # ✅ 使用枚举
    email='admin@example.com'  # ✅ 添加email字段
)
```

---

## ✅ User模型的正确字段

根据 `backend/models/database.py` 中的定义：

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)           # ✅ 姓名（中文名）
    username = db.Column(db.String(50), unique=True, nullable=False)  # ✅ 用户名
    password_hash = db.Column(db.String(128), nullable=False)  # ✅ 密码哈希
    email = db.Column(db.String(100), unique=True, nullable=True)  # ✅ 邮箱
    position = db.Column(db.String(50), nullable=True)        # ✅ 职位
    role = db.Column(db.Enum(UserRole), default=UserRole.MEMBER)  # ✅ 角色（枚举）
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
```

**注意：**
- ✅ 使用 `name` 字段存储中文姓名
- ✅ `role` 必须使用 `UserRole` 枚举
- ❌ 没有 `chinese_name` 字段
- ❌ 没有 `is_active` 字段

---

## ✅ UserRole枚举值

```python
class UserRole(Enum):
    DEPARTMENT_MANAGER = "department_manager"  # 部门主管
    MEMBER = "member"                          # 普通成员
```

---

## 📝 修复后的用户创建代码

### 创建管理员
```python
admin = User(
    name='系统管理员',
    username='admin',
    password_hash=generate_password_hash('admin123'),
    role=UserRole.DEPARTMENT_MANAGER,
    email='admin@example.com'
)
```

### 创建普通用户
```python
test_users = [
    {'username': 'zhangsan', 'name': '张三', 'email': 'zhangsan@example.com'},
    {'username': 'lisi', 'name': '李四', 'email': 'lisi@example.com'},
    {'username': 'wangwu', 'name': '王五', 'email': 'wangwu@example.com'},
]

for user_data in test_users:
    user = User(
        name=user_data['name'],
        username=user_data['username'],
        password_hash=generate_password_hash('123456'),
        role=UserRole.MEMBER,
        email=user_data['email']
    )
    db.session.add(user)
```

---

## 🧪 验证修复

修复后，重新构建并启动Docker：

```bash
# 停止现有容器
docker compose down

# 清理旧数据
rm -rf data/*

# 重新构建（确保使用最新的docker-start.sh）
docker compose build --no-cache

# 启动容器
docker compose up -d

# 查看日志验证
docker logs -f project-management-app
```

预期输出：
```
✅ 数据库表创建完成
✅ 默认管理员用户创建成功
   用户名: admin
   密码: admin123
   请登录后立即修改密码！
✅ 测试用户创建完成
✅ 数据库初始化完成！
🌟 启动Flask应用...
```

---

## 🎉 修复完成

现在 `docker-start.sh` 已经完全修复，可以正常：
1. ✅ 初始化数据库
2. ✅ 创建默认管理员账户
3. ✅ 创建测试用户
4. ✅ 启动Flask应用

---

## 📋 默认账户（修复后）

| 用户名 | 密码 | 姓名 | 角色 | 邮箱 |
|--------|------|------|------|------|
| admin | admin123 | 系统管理员 | 部门主管 | admin@example.com |
| zhangsan | 123456 | 张三 | 普通成员 | zhangsan@example.com |
| lisi | 123456 | 李四 | 普通成员 | lisi@example.com |
| wangwu | 123456 | 王五 | 普通成员 | wangwu@example.com |

---

## 🚀 现在可以部署了

```bash
# 进入项目目录
cd /Users/bizai/Desktop/项目推荐表设计

# 一键部署
./deploy-docker.sh deploy

# 访问系统
http://localhost:5001
```

**祝部署成功！** 🎉

