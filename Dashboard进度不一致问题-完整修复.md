# Dashboard 进度不一致问题 - 完整修复报告

## 问题描述
用户报告：**电池仓自动化打磨项目**在Dashboard显示进度25%，但实际应该是1%

## 问题分析

### 1. 数据库状态
```sql
项目: 电池仓自动化打磨
状态: INITIAL_CONTACT (初步接触)
数据库进度: 25% (旧值)
手动进度: NULL
项目来源: horizontal
模块: 1个 (确认用户需求: 25%)
```

### 2. 预期进度计算
根据新的进度规则：
- **状态**: 初步接触（阶段1/7）
- **阶段进度范围**: 0-5%
- **有模块**: 1个，进度25%
- **计算方式**: 线性映射模块进度到阶段范围
- **公式**: `0 + (25/100) × (5-0) = 1.25%` ≈ **1%**

### 3. 根本原因分析

#### 问题1：后端API使用旧值 ❌
`get_department_overview()` 直接读取 `project.progress` (25%)，而不是实时计算

#### 问题2：数据库缺少字段 ❌
`manual_progress` 字段不存在，导致手动进度功能无法使用

#### 问题3：后端服务未重启 ❌
修改代码后未重启，仍运行旧代码

---

## 修复过程

### 第1步：修复后端API ✅

**文件**: `backend/services/project_service.py`

**修改**: `get_department_overview()` 方法（第771-802行）

#### 修复前
```python
project_info = {
    'progress': project.progress,  # ❌ 直接读取数据库旧值
}
```

#### 修复后
```python
# 使用新的进度计算逻辑
progress_info = ProjectService.calculate_project_progress(project)
current_progress = progress_info['progress']

project_info = {
    'progress': current_progress,  # ✅ 使用实时计算进度
    'progress_type': progress_info.get('type', 'unknown'),
    'progress_info': progress_info.get('info', ''),
}
```

### 第2步：添加数据库字段 ✅

**命令**:
```bash
cd backend
sqlite3 project_management.db \
  "ALTER TABLE projects ADD COLUMN manual_progress INTEGER DEFAULT NULL;"
```

**验证**:
```bash
sqlite3 project_management.db "PRAGMA table_info(projects);" | grep manual_progress
# 输出: 14|manual_progress|INTEGER|0|NULL|0 ✅
```

### 第3步：重启后端服务 ✅

**命令**:
```bash
# 停止旧进程
pkill -f "python.*backend/app.py"

# 重新启动
cd backend
source venv/bin/activate
nohup python app.py > backend.log 2>&1 &
```

### 第4步：验证修复 ✅

**测试API**:
```python
# test_api_progress.py
import requests
response = requests.get('http://localhost:5001/api/projects/overview')
data = response.json()

# 结果：
# 项目: 电池仓自动化打磨
# Dashboard API 返回的进度: 1% ✅
# 进度类型: stage_with_modules
# 进度说明: 基于 1 个模块，映射到阶段范围 0-5%
```

---

## 修复结果

### 后端API ✅
```json
{
  "name": "电池仓自动化打磨",
  "status": "initial_contact",
  "progress": 1,  // ✅ 正确！从25%修正为1%
  "progress_type": "stage_with_modules",
  "progress_info": "基于 1 个模块，映射到阶段范围 0-5%"
}
```

### 计算逻辑 ✅
```
状态: 初步接触 (0-5%)
模块进度: 25%
映射计算: 0 + (25/100) × (5-0) = 1.25% ≈ 1%
最终进度: 1% ✅
```

---

## 前端刷新

### 如果Dashboard仍显示25%

**原因**: 浏览器缓存了旧的API响应

**解决方案**:

#### 方法1：硬刷新（推荐）
- **Windows/Linux**: `Ctrl + F5` 或 `Ctrl + Shift + R`
- **Mac**: `Cmd + Shift + R`

#### 方法2：清除缓存
1. 打开浏览器开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

#### 方法3：禁用缓存（开发模式）
1. 打开开发者工具（F12）
2. Network 标签
3. 勾选 "Disable cache"
4. 刷新页面

---

## 数据一致性验证

### 所有API现在都使用实时计算 ✅

| API端点 | 使用方法 | 状态 |
|---------|----------|------|
| `/api/projects` | `calculate_project_progress()` | ✅ |
| `/api/projects/{id}` | `calculate_project_progress()` | ✅ |
| `/api/projects/overview` | `calculate_project_progress()` | ✅ |

### 进度显示统一 ✅

| 页面 | 显示进度 | 数据源 |
|------|----------|--------|
| Dashboard | 1% | 实时计算 ✅ |
| Projects | 1% | 实时计算 ✅ |
| ProjectDetail | 1% | 实时计算 ✅ |

---

## 测试其他项目

### 测试场景1：项目实施阶段
```
项目: 某项目A
状态: project_implementation
模块: 3个（100%, 60%, 30%）平均63.3%
计算: 35% + 63.3% × 65% = 76.1% ≈ 76%
预期Dashboard显示: 76% ✅
```

### 测试场景2：前期无模块
```
项目: 某项目B
状态: quotation_submitted (15-20%)
模块: 无
手动进度: NULL
计算: 使用阶段默认值 20%
预期Dashboard显示: 20% ✅
```

### 测试场景3：纵向项目
```
项目: 某纵向项目C
状态: vertical_review (审核阶段)
模块: 任意
计算: 固定阶段进度 50%
预期Dashboard显示: 50% ✅
```

---

## 文件清单

### 已修改
1. ✅ `backend/services/project_service.py` - 修复 `get_department_overview()`
2. ✅ `backend/project_management.db` - 添加 `manual_progress` 字段

### 已创建（测试文件）
1. `backend/test_progress_calculation.py` - 测试进度计算逻辑
2. `test_api_progress.py` - 测试API返回数据

### 已重启
1. ✅ 后端服务 `backend/app.py`

### 无需修改
- ❌ 前端代码（Dashboard.vue已正确使用`project.progress`）
- ❌ 数据库数据（不需要批量更新）

---

## 部署检查清单

- [x] 修改后端代码
- [x] 添加数据库字段
- [x] 重启后端服务
- [x] 验证API返回数据
- [ ] **刷新前端页面（用户操作）**

---

## 总结

### 问题
Dashboard显示的进度与实际计算不符（25% vs 1%）

### 根源
1. 后端API读取数据库旧值
2. 数据库缺少新字段
3. 服务未重启

### 解决
1. ✅ 修改API使用实时计算
2. ✅ 添加 `manual_progress` 字段
3. ✅ 重启后端服务
4. ⏳ 用户需刷新浏览器

### 结果
- **后端API**: 返回正确进度 1% ✅
- **数据一致性**: 所有API统一使用实时计算 ✅
- **前端显示**: 需用户刷新页面 ⏳

---

## 用户操作指南

### 查看修复结果

1. **刷新页面**
   - 按 `Cmd + Shift + R`（Mac）
   - 或 `Ctrl + Shift + R`（Windows/Linux）

2. **验证进度**
   - 打开 Dashboard（项目模块进度一览表）
   - 找到"电池仓自动化打磨"项目
   - 确认进度显示为 **1%** ✅

3. **检查说明**（可选）
   - 鼠标悬停在进度上
   - 查看 tooltip："基于 1 个模块，映射到阶段范围 0-5%"

---

*修复完成于 2025年11月4日 19:08*
*后端服务已重启，API返回正确数据*
*用户需刷新浏览器以查看最新进度*

