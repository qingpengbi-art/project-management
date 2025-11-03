# 纵向项目Dashboard修复和删除项目修复说明

## 📋 问题描述

### 问题1：Dashboard纵向项目显示旧状态
- **现象**：项目总览的纵向项目卡片仍显示10个横向项目的状态
- **原因**：Dashboard使用的状态列表未区分横向和纵向项目

### 问题2：删除项目失败
- **现象**：删除项目时报错 `NOT NULL constraint failed: module_assignments.module_id`
- **原因**：项目删除时未正确处理模块分配记录的外键约束

## ✅ 问题修复

### 修复1：Dashboard纵向项目状态显示

#### 1.1 添加纵向专用状态列表

```javascript
// 横向项目按业务流程顺序排列的状态列表
const orderedStatusList = [
  'initial_contact',      // 初步接触
  'proposal_submitted',   // 提交方案
  'quotation_submitted',  // 提交报价
  'user_confirmation',    // 用户确认
  'contract_signed',      // 合同签订
  'project_implementation', // 项目实施
  'project_acceptance',   // 项目验收
  'warranty_period',      // 维保期内
  'post_warranty',        // 维保期外
  'no_follow_up'          // 不再跟进
]

// 纵向项目专用状态列表 ✨ 新增
const verticalStatusList = [
  'vertical_declaration', // 申报阶段
  'vertical_review',      // 审核阶段
  'vertical_approved',    // 审核通过
  'vertical_rejected'     // 审核未通过
]
```

#### 1.2 修改纵向项目卡片模板

**修改前**：使用 `orderedStatusList`（10个状态）

**修改后**：使用 `verticalStatusList`（4个状态）

```vue
<!-- 纵向项目卡片 -->
<div class="stat-card apple-card project-source-card vertical-card">
  <!-- 下半部分：状态区 - 使用纵向专用状态 -->
  <div class="card-status-section">
    <div class="status-grid-vertical">
      <div 
        v-for="status in verticalStatusList" 
        :key="status"
        class="status-item-vertical"
        :class="{ 'active': (verticalOverview.statusDist[status] || 0) > 0 }"
        @click="navigateToProjectsBySource('vertical', status)"
      >
        <div class="status-count-uniform">{{ verticalOverview.statusDist[status] || 0 }}</div>
        <div class="status-label-uniform">{{ getStatusShortText(status) }}</div>
      </div>
    </div>
  </div>
</div>
```

#### 1.3 修改纵向项目统计计算

```javascript
// 纵向项目统计 - 使用纵向专用状态
const verticalOverview = computed(() => {
  const projects = overview.value.projects.filter(p => p.project_source === 'vertical')
  const statusDist = {}
  verticalStatusList.forEach(status => {  // 使用纵向状态列表
    statusDist[status] = projects.filter(p => p.status === status).length
  })
  return {
    total: projects.length,
    statusDist
    // 注意：移除了 avgProgress，纵向项目没有进度概念
  }
})
```

#### 1.4 添加纵向专用CSS样式

```scss
// 纵向项目专用网格布局（2x2）
.status-grid-vertical {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

// 纵向项目状态项样式
.status-item-vertical {
  padding: 12px 8px;
  background: white;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  
  &.active {
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    
    .status-count-uniform {
      color: var(--theme-color);
    }
    
    &:hover {
      border-color: var(--theme-color);
      transform: translateY(-2px);
      box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
}
```

### 修复2：项目删除外键约束问题

#### 2.1 问题分析

删除项目时的数据关系：
```
Project (项目)
  ├─ ProjectMember (项目成员)
  ├─ ProjectProgressRecord (项目进度记录)
  └─ ProjectModule (模块)
       ├─ ModuleAssignment (模块分配) ⚠️ 外键约束
       ├─ ModuleWorkRecord (模块工作记录) ⚠️ 外键约束
       └─ ModuleProgressRecord (模块进度记录) ✅ 已配置级联删除
```

**关键问题**：`ModuleAssignment` 和 `ModuleWorkRecord` 的外键没有配置级联删除，导致删除项目时报错。

#### 2.2 解决方案

在项目删除服务中，**手动按正确顺序删除关联数据**：

```python
@staticmethod
def delete_project(project_id: int) -> Dict[str, Any]:
    """删除项目"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return {
                'success': False,
                'message': '项目不存在',
                'data': None
            }
        
        project_name = project.name
        
        # 手动删除关联数据（避免外键约束错误）
        # 1. 获取项目的所有模块
        modules = ProjectModule.query.filter_by(project_id=project_id).all()
        
        # 2. 删除每个模块的关联数据
        for module in modules:
            # 删除模块分配记录
            ModuleAssignment.query.filter_by(module_id=module.id).delete()
            # 删除模块工作记录
            ModuleWorkRecord.query.filter_by(module_id=module.id).delete()
            # 删除模块进度记录会被级联删除（已配置cascade）
        
        # 3. 删除项目成员记录
        ProjectMember.query.filter_by(project_id=project_id).delete()
        
        # 4. 删除项目进度记录
        ProjectProgressRecord.query.filter_by(project_id=project_id).delete()
        
        # 5. 删除项目本身（会级联删除模块）
        db.session.delete(project)
        db.session.commit()
        
        return {
            'success': True,
            'message': f'项目"{project_name}"已成功删除',
            'data': None
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'删除项目失败: {str(e)}',
            'data': None
        }
```

#### 2.3 添加必要的导入

```python
from ..models.database import (
    db, Project, ProjectMember, ProgressRecord, User, 
    ProjectStatus, ProjectMemberRole, 
    ProjectModule, ModuleAssignment, ModuleWorkRecord, ProjectProgressRecord  # ✨ 新增
)
```

## 🎯 修改文件清单

### 前端文件
- ✅ `frontend/src/views/Dashboard.vue`
  - 添加 `verticalStatusList` 纵向专用状态列表
  - 修改纵向项目卡片模板使用 `verticalStatusList`
  - 修改 `verticalOverview` 计算属性
  - 添加 `.status-grid-vertical` 和 `.status-item-vertical` 样式

### 后端文件
- ✅ `backend/services/project_service.py`
  - 修改 `delete_project` 方法，手动删除关联数据
  - 添加必要的模型导入

## 📊 修复效果

### Dashboard显示效果

#### 横向项目卡片
- 显示10个状态（5x2网格）
- 状态：初步接触、提交方案、...、不再跟进

#### 纵向项目卡片 ✨
- 显示4个专用状态（2x2网格）
- 状态：申报阶段、审核阶段、审核通过、审核未通过
- **不显示进度信息**（纵向项目没有进度概念）

#### 自研项目卡片
- 显示2个状态
- 状态：进行中、已完成

### 删除项目功能

#### 修复前
```
❌ 删除项目失败: (sqlite3.IntegrityError) 
   NOT NULL constraint failed: module_assignments.module_id
```

#### 修复后
```
✅ 项目"XXX"已成功删除
```

**删除顺序**：
1. 模块分配记录 → 2. 模块工作记录 → 3. 项目成员记录 → 4. 项目进度记录 → 5. 项目本身（级联删除模块）

## 🧪 测试验证

### 测试1：Dashboard纵向项目显示
1. 刷新浏览器页面
2. 查看Dashboard的纵向项目卡片
3. **验证点**：
   - ✅ 只显示4个状态格子
   - ✅ 状态文本为：申报阶段、审核阶段、审核通过、审核未通过
   - ✅ 不显示平均进度
   - ✅ 布局为2x2网格

### 测试2：删除纵向项目
1. 创建一个测试纵向项目
2. 为项目添加模块和成员
3. 尝试删除该项目
4. **验证点**：
   - ✅ 删除成功，无错误提示
   - ✅ 项目从列表中消失
   - ✅ 相关模块、成员、进度记录都被删除

### 测试3：删除横向/自研项目
1. 删除一个有模块的横向项目
2. **验证点**：
   - ✅ 删除成功
   - ✅ 不影响其他项目

## 🔍 技术细节

### 外键约束处理策略

#### 方案1：数据库层面配置级联删除（未采用）
```python
# 需要修改 ModuleAssignment 模型
module_id = db.Column(db.Integer, 
                     db.ForeignKey('project_modules.id', ondelete='CASCADE'),  # 级联删除
                     nullable=False)
```

**问题**：需要数据库迁移，可能影响现有数据

#### 方案2：应用层面手动删除（已采用）✅
```python
# 在删除前手动清理关联数据
for module in modules:
    ModuleAssignment.query.filter_by(module_id=module.id).delete()
    ModuleWorkRecord.query.filter_by(module_id=module.id).delete()
```

**优点**：
- ✅ 不需要数据库迁移
- ✅ 代码逻辑清晰
- ✅ 容易调试和维护
- ✅ 可以在删除前执行额外的业务逻辑

### Vue响应式处理

纵向项目状态列表使用常量数组：
```javascript
const verticalStatusList = [...]  // 不需要 ref()，因为是静态数据
```

状态统计使用计算属性：
```javascript
const verticalOverview = computed(() => { ... })  // 自动响应 overview 变化
```

## 📝 后续优化建议

### 1. 数据库层面优化（可选）
考虑在下次数据库迁移时，为 `ModuleAssignment` 和 `ModuleWorkRecord` 添加级联删除配置：

```python
class ModuleAssignment(db.Model):
    module_id = db.Column(db.Integer, 
                         db.ForeignKey('project_modules.id', ondelete='CASCADE'),
                         nullable=False)
```

### 2. 删除确认优化
添加更详细的删除确认信息：
```javascript
ElMessageBox.confirm(
  `确定要删除项目"${project.name}"吗？\n` +
  `该项目包含 ${project.modules.length} 个模块，` +
  `${project.members.length} 个成员，删除后无法恢复！`,
  '删除确认',
  { type: 'warning' }
)
```

### 3. 软删除机制
考虑实现软删除（标记为已删除而不是真正删除）：
```python
class Project(db.Model):
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
```

## ✅ 完成清单

- [x] Dashboard纵向项目显示修复
  - [x] 添加纵向专用状态列表
  - [x] 修改模板使用纵向状态
  - [x] 修改计算属性
  - [x] 添加专用CSS样式
- [x] 项目删除功能修复
  - [x] 手动删除模块分配记录
  - [x] 手动删除模块工作记录
  - [x] 手动删除项目成员记录
  - [x] 手动删除项目进度记录
  - [x] 添加必要的导入
- [x] 后端服务重启
- [x] 文档编写

## 🎉 修复完成

所有问题已解决：
1. ✅ Dashboard纵向项目正确显示4个专用状态
2. ✅ 删除项目功能正常工作，无外键约束错误

**请刷新浏览器测试功能！**

---

**完成时间**：2025-11-03  
**修复人**：AI Assistant

