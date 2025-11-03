# Dashboard模块显示修复说明

## 问题描述

在项目模块进度一览表（Dashboard页面）中，每个模块显示的还是"负责人:"标签，并且使用的是旧的单一负责人数据结构 `module.assigned_to`，与我们之前的改动不一致。

## 问题定位

**文件**：`frontend/src/views/Dashboard.vue`

**位置**：第151-170行的模块卡片显示区域

## 修复内容

### 1. 修改标签文字
```vue
<!-- 修改前 -->
<div class="assignees-label">负责人:</div>

<!-- 修改后 -->
<div class="assignees-label">成员:</div>
```

### 2. 更新数据结构
从单一负责人改为多成员列表：

```vue
<!-- 修改前：显示单个负责人 -->
<div
  v-if="module.assigned_to"
  class="assignee-tag"
  :title="`${module.assigned_to.name} - ${module.assigned_to.position}`"
>
  {{ module.assigned_to.name }}
</div>

<!-- 修改后：显示所有成员 -->
<div
  v-if="module.assigned_users && module.assigned_users.length > 0"
  v-for="user in module.assigned_users"
  :key="user.id"
  class="assignee-tag"
  :title="`${user.name} - ${user.position || ''}`"
>
  {{ user.name }}
</div>
```

### 3. 移除优先级显示
同时移除了模块卡片中的"优先级"显示：

```vue
<!-- 修改前 -->
<div class="progress-info">
  <span class="progress-text">{{ module.progress }}%</span>
  <span class="priority">优先级: {{ getPriorityText(module.priority) }}</span>
</div>

<!-- 修改后 -->
<div class="progress-info">
  <span class="progress-text">{{ module.progress }}%</span>
</div>
```

## 修改范围

### 已修改的文件
- ✅ `frontend/src/views/Dashboard.vue` - 项目模块进度一览表

### 不需要修改的地方
- ❌ `frontend/src/views/Projects.vue` 第154行的"负责人:" - 这是**项目负责人**，不是模块负责人，保持不变
- ❌ `frontend/src/views/Dashboard.vue` 第281行的"项目负责人" - 这也是**项目负责人**，保持不变

## 数据来源

模块的 `assigned_users` 数据由后端API提供：
- **API端点**：`GET /api/projects/<project_id>/modules`
- **Service方法**：`ModuleService.get_project_modules()`
- **数据字段**：`module_dict['assigned_users']` - 包含所有分配的成员列表

## 显示效果

### 修改前
```
模块名称          [进行中]
负责人: 张三
进度: 50%  优先级: 高
```

### 修改后
```
模块名称          [进行中]
成员: 张三 李四 王五
进度: 50%
```

## 生效方式

这是前端修改，需要重新构建前端：

### 开发环境
前端热重载会自动刷新，直接刷新浏览器页面即可看到效果。

### Docker环境
```bash
# 需要重新构建前端并重启容器
docker-compose down
docker-compose up --build
```

### Render云端部署
推送到GitHub后，Render会自动重新构建部署。

## 验证方式

1. 打开系统首页（Dashboard）
2. 查看"项目模块进度一览表"区域
3. 检查每个模块卡片：
   - 标签应显示"成员:"而不是"负责人:"
   - 应显示所有模块成员（可能有多个）
   - 不再显示"优先级"字段

## 相关修改记录

这个修改与之前的模块简化优化保持一致：
- ✅ 创建模块对话框 - 已改为"成员"
- ✅ 编辑模块对话框 - 已改为"成员"
- ✅ 项目详情页模块卡片 - 已改为"成员"
- ✅ Dashboard模块进度一览表 - 本次修复

现在所有页面的模块显示都统一了！

---

**修复时间**：2025-11-03  
**修复人**：AI Assistant

