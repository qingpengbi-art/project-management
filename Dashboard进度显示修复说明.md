# Dashboard 进度显示修复说明

## 问题描述
用户发现：项目模块进度一览表（Dashboard）里面的项目进度和项目管理的项目进度不一样。

## 问题原因

### 根本原因
`get_department_overview()` 方法直接读取数据库中的 `project.progress` 字段（旧值），而没有使用新的 `calculate_project_progress()` 方法计算实时进度。

### 代码对比

#### 修复前 ❌
```python
project_info = {
    'id': project.id,
    'name': project.name,
    'status': project.status.value,
    'progress': project.progress,  # ← 直接读取数据库旧值
    'leaders': leaders,
    # ...
}
```

**问题**：
- 数据库中的 `progress` 字段可能是旧的
- 不会根据模块进度实时计算
- 不会应用新的进度映射规则

#### 修复后 ✅
```python
# 使用新的进度计算逻辑
progress_info = ProjectService.calculate_project_progress(project)
current_progress = progress_info['progress']

project_info = {
    'id': project.id,
    'name': project.name,
    'status': project.status.value,
    'progress': current_progress,  # ← 使用计算后的进度
    'progress_type': progress_info.get('type', 'unknown'),
    'progress_info': progress_info.get('info', ''),
    'leaders': leaders,
    # ...
}
```

**改进**：
- ✅ 实时计算进度
- ✅ 应用新的进度规则
- ✅ 包含进度类型和说明信息

---

## 修复内容

### 文件
`backend/services/project_service.py`

### 方法
`get_department_overview()`

### 修改行数
第771-802行

### 主要变更
1. 添加进度计算：`progress_info = ProjectService.calculate_project_progress(project)`
2. 使用计算后的进度：`current_progress = progress_info['progress']`
3. 添加额外字段：`progress_type` 和 `progress_info`

---

## 影响范围

### 后端 API
- ✅ `GET /api/projects/overview` - 返回实时计算的进度

### 前端页面
- ✅ Dashboard（项目模块进度一览表）- 显示正确的实时进度

---

## 测试验证

### 测试场景1：前期项目有模块
```
项目：测试项目A
状态：提交方案（5-15%）
模块：3个（80%, 60%, 40%）

预期：
- Dashboard显示：11%
- 项目管理显示：11%
- 两者一致 ✓
```

### 测试场景2：项目实施阶段
```
项目：测试项目B
状态：项目实施
模块：3个（100%, 60%, 30%）

预期：
- Dashboard显示：76%（35% + 63.3% × 65%）
- 项目管理显示：76%
- 两者一致 ✓
```

### 测试场景3：前期项目无模块
```
项目：测试项目C
状态：用户确认
模块：无
手动进度：23%

预期：
- Dashboard显示：23%
- 项目管理显示：23%
- 两者一致 ✓
```

---

## 部署说明

### 需要重启
✅ **仅需重启后端服务**

```bash
# 停止后端服务
# Ctrl+C 或 kill process

# 重新启动
cd backend
python app.py
```

### 无需其他操作
- ❌ 不需要数据库迁移
- ❌ 不需要前端重新编译
- ❌ 不需要清除缓存

### 立即生效
重启后端后，刷新 Dashboard 页面即可看到正确的进度。

---

## 数据一致性

### 现在的数据流

```
┌─────────────────────────────────────────┐
│ 数据库                                   │
│ - projects.progress (可能是旧值)        │
│ - projects.manual_progress              │
│ - project_modules.progress              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ ProjectService.calculate_project_progress()
│ - 读取模块进度                           │
│ - 读取手动进度                           │
│ - 应用计算规则                           │
│ - 返回实时进度                           │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ API返回                                  │
│ - progress: 实时计算的进度               │
│ - progress_type: 进度类型                │
│ - progress_info: 进度说明                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 前端显示                                 │
│ - Dashboard: {{ project.progress }}%     │
│ - Projects: {{ project.progress }}%      │
│ - ProjectDetail: {{ project.progress }}% │
│ ✅ 所有地方显示一致                      │
└─────────────────────────────────────────┘
```

---

## 相关API

### 已更新使用新进度计算的API
1. ✅ `GET /api/projects` - 项目列表
2. ✅ `GET /api/projects/{id}` - 项目详情
3. ✅ `GET /api/projects/overview` - **部门总览（本次修复）**

### 进度计算统一
所有返回项目数据的API现在都使用 `calculate_project_progress()` 方法，确保数据一致性。

---

## 额外改进

### 新增返回字段
Dashboard API 现在额外返回：

1. **progress_type** - 进度类型
   - `stage`: 阶段进度（前期阶段默认值）
   - `stage_manual`: 手动设置的阶段进度
   - `stage_with_modules`: 基于模块映射的阶段进度
   - `implementation`: 项目实施进度
   - `completed`: 完成状态
   - `warranty`: 维保期
   - `terminated`: 已终止

2. **progress_info** - 进度说明
   - 示例："基于 3 个模块，映射到阶段范围 5-15%"
   - 示例："基于 3 个模块计算"
   - 示例："手动设置"
   - 示例："阶段默认进度"

### 前端可以使用（可选）
```vue
<template>
  <el-tooltip :content="project.progress_info">
    <span>{{ project.progress }}%</span>
  </el-tooltip>
</template>
```

---

## 总结

### 问题
Dashboard 显示的进度与项目管理页面不一致。

### 原因
Dashboard API 读取数据库旧值，而不是实时计算。

### 解决
在 `get_department_overview()` 方法中使用 `calculate_project_progress()` 实时计算进度。

### 影响
- ✅ Dashboard 显示正确的实时进度
- ✅ 与项目管理页面保持一致
- ✅ 自动应用所有新的进度规则

### 部署
重启后端服务即可，无需其他操作。

---

*修复完成于 2025年11月4日*

