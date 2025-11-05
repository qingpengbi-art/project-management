<template>
  <div class="project-detail-page">
    <div v-if="projectStore.currentProject" class="project-detail">
      <!-- 项目基本信息 -->
      <div class="project-header apple-card">
        <div class="header-content">
          <div class="header-left">
            <h1 class="project-title">{{ project.name }}</h1>
            <p class="project-description">{{ project.description || '暂无描述' }}</p>
            <div class="project-meta">
              <span class="status-badge" :class="project.status">
                {{ projectStore.getStatusText(project.status) }}
              </span>
            </div>
            <!-- 项目类型和合作方信息 -->
            <div class="project-source-info">
              <div class="info-item">
                <span class="info-label">项目类型:</span>
                <span class="source-tag" :class="`source-${project.project_source || 'horizontal'}`">
                  {{ getSourceText(project.project_source) }}
                </span>
              </div>
              <div class="info-item" v-if="project.project_source === 'horizontal' && project.partner">
                <span class="info-label">合作方:</span>
                <span class="info-value">{{ project.partner }}</span>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-button @click="goBack">
              返回列表
            </el-button>
          </div>
        </div>
      </div>

      <!-- 项目进度 - 只在横向和自研项目显示，不再跟进项目不显示 -->
      <div v-if="project.project_source !== 'vertical' && project.status !== 'no_follow_up'" class="progress-section apple-card">
        <div class="section-header">
          <h3 class="section-title">项目进度</h3>
          <el-button
            v-if="canUpdateProgress"
            type="primary"
            size="small"
            @click="showUpdateProgressDialog"
          >
            更新进度
          </el-button>
        </div>
        <div class="progress-content">
          <div class="progress-display">
            <div class="progress-circle">
              <div class="progress-text">{{ project.progress }}%</div>
            </div>
            <div class="progress-info">
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :class="{ 
                    success: project.progress === 100,
                    warning: project.progress < 30 
                  }"
                  :style="{ width: project.progress + '%' }"
                ></div>
              </div>
              <div class="progress-details">
                <span>开始日期: {{ formatDate(project.start_date) }}</span>
                <span>预计完成: {{ formatDate(project.end_date) }}</span>
                <span v-if="project.actual_end_date">实际完成: {{ formatDate(project.actual_end_date) }}</span>
              </div>
              <div class="project-duration-wrapper">
                <span class="project-duration">
                  项目总时间: {{ calculateProjectDuration(project.start_date, project.end_date) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 项目模块 -->
      <div class="modules-section apple-card">
        <div class="section-header">
          <h3 class="section-title">项目模块</h3>
          <div class="section-actions">
            <el-button size="small" type="primary" @click="showCreateModuleDialog">
              <el-icon><Plus /></el-icon>
              添加模块
            </el-button>
          </div>
        </div>
        
        <div v-if="moduleStore.loading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="modules.length === 0" class="empty-modules">
          <div class="empty-icon">
            <el-icon><Box /></el-icon>
          </div>
          <p>暂无项目模块</p>
          <el-button type="primary" @click="showCreateModuleDialog">
            创建第一个模块
          </el-button>
        </div>
        
        <div v-else class="modules-list">
          <div
            v-for="module in modules"
            :key="module.id"
            class="module-card"
          >
            <div class="module-header">
              <div class="module-title">
                <h4 class="module-name">{{ module.name }}</h4>
                <div class="module-meta">
                  <span class="status-badge" :class="module.status">
                    {{ moduleStore.getStatusText(module.status) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="module-description">
              <p>{{ module.description || '暂无描述' }}</p>
            </div>
            
            <div class="module-progress">
              <div class="progress-header">
                <span class="progress-label">进度</span>
                <span class="progress-value">{{ module.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :class="{ 
                    success: module.progress === 100,
                    warning: module.progress < 30 
                  }"
                  :style="{ width: module.progress + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="module-info">
              <div class="info-row members-row">
                <span class="info-label">成员:</span>
                <div class="members-list-inline">
                  <span 
                    v-if="module.assigned_users && module.assigned_users.length > 0"
                    v-for="user in module.assigned_users"
                    :key="user.id"
                    class="member-tag"
                  >
                    {{ user.name }}
                  </span>
                  <span v-else class="no-members">未分配</span>
                </div>
              </div>
              <div class="info-row">
                <span class="info-label">更新时间:</span>
                <span class="info-value">{{ formatDateTime(module.updated_at) }}</span>
              </div>
            </div>
            
            <div class="module-actions">
              <el-button
                v-if="canUpdateModule(module)"
                size="small"
                type="primary"
                plain
                @click="showUpdateModuleProgress(module)"
              >
                更新进度
              </el-button>
              <el-button
                v-if="canEditModule(module)"
                size="small"
                type="info"
                plain
                @click="showEditModule(module)"
              >
                <el-icon><Edit /></el-icon>
                编辑模块
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 项目成员 -->
      <div class="members-section apple-card">
        <div class="section-header">
          <h3 class="section-title">项目成员</h3>
        </div>
        
        <div v-if="allProjectMembers.length === 0" class="empty-members">
          <p>暂无项目成员</p>
          <p class="empty-tip">请在项目模块中分配成员</p>
        </div>
        
        <div v-else class="members-grid">
          <div
            v-for="member in allProjectMembers"
            :key="member.id"
            class="member-card"
          >
            <div class="member-avatar">
              {{ member.name.charAt(0) }}
            </div>
            <div class="member-info">
              <div class="member-name">{{ member.name }}</div>
              <div class="member-position">{{ member.position || '未知职位' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else-if="projectStore.loading" class="loading-state">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-state">
      <div class="error-icon">
        <el-icon><Warning /></el-icon>
      </div>
      <h3>项目不存在</h3>
      <p>请检查项目ID是否正确</p>
      <el-button type="primary" @click="goBack">返回列表</el-button>
    </div>

    
    <!-- 创建模块对话框 -->
    <CreateModuleDialog 
      v-model:visible="createModuleDialogVisible"
      :project-id="parseInt(route.params.id)"
      @success="handleModuleCreateSuccess"
    />
    
    <!-- 模块进度更新对话框 -->
    <UpdateModuleProgressDialog
      v-model:visible="updateModuleProgressDialogVisible"
      :module="selectedModule"
      :project-name="project?.name"
      @success="handleModuleUpdateSuccess"
    />
    
    <!-- 更新项目进度对话框 -->
    <UpdateProgressDialog
      v-model:visible="updateProgressDialogVisible"
      :project="project"
      @success="handleProgressUpdateSuccess"
    />

    <!-- 编辑模块对话框 -->
    <EditModuleDialog
      v-model="editModuleDialogVisible"
      :module="selectedModule"
      :project-id="parseInt(route.params.id)"
      @success="handleModuleEditSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Warning, Plus, Box, Edit } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'
import { useModuleStore } from '@/stores/module'
import { useAuthStore } from '@/stores/auth'
import CreateModuleDialog from '@/components/CreateModuleDialog.vue'
import UpdateModuleProgressDialog from '@/components/UpdateModuleProgressDialog.vue'
import UpdateProgressDialog from '@/components/UpdateProgressDialog.vue'
import EditModuleDialog from '@/components/EditModuleDialog.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const userStore = useUserStore()
const moduleStore = useModuleStore()
const authStore = useAuthStore()

// 响应式数据
const createModuleDialogVisible = ref(false)
const updateModuleProgressDialogVisible = ref(false)
const editModuleDialogVisible = ref(false)
const updateProgressDialogVisible = ref(false)
const selectedModule = ref(null)

// 计算属性
const project = computed(() => projectStore.currentProject)
const modules = computed(() => moduleStore.modules)

// 获取所有项目成员（从模块中收集）
const allProjectMembers = computed(() => {
  if (!modules.value || modules.value.length === 0) {
    return []
  }
  
  const memberMap = new Map()
  
  modules.value.forEach(module => {
    // 使用 assigned_users 而不是 assignments
    if (module.assigned_users && module.assigned_users.length > 0) {
      module.assigned_users.forEach(user => {
        if (user) {
          if (!memberMap.has(user.id)) {
            memberMap.set(user.id, {
              id: user.id,
              name: user.name,
              position: user.position,
              modules: []
            })
          }
          memberMap.get(user.id).modules.push(module.name)
        }
      })
    }
  })
  
  return Array.from(memberMap.values())
})

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '未设置'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 计算项目总时间
const calculateProjectDuration = (startDate, endDate) => {
  // 如果日期不完整，返回 "-"
  if (!startDate || !endDate) {
    return '-'
  }
  
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  // 0天的情况
  if (diffDays === 0) {
    return '当天完成'
  }
  
  if (diffDays < 30) {
    return `${diffDays}天`
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    const days = diffDays % 30
    return days > 0 ? `${months}个月${days}天` : `${months}个月`
  } else {
    const years = Math.floor(diffDays / 365)
    const months = Math.floor((diffDays % 365) / 30)
    if (months > 0) {
      return `${years}年${months}个月`
    }
    return `${years}年`
  }
}

// 获取项目类型文本
const getSourceText = (source) => {
  const sourceMap = {
    'horizontal': '横向',
    'vertical': '纵向',
    'self_developed': '自研'
  }
  return sourceMap[source] || '横向'
}

// 权限检查方法
const canUpdateModule = (module) => {
  return authStore.canUpdateModule(module, project.value)
}

const formatDateTime = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}


const handleUpdateSuccess = () => {
  ElMessage.success('进度更新成功')
  // 重新加载项目详情
  loadProjectDetail()
}

const handleModuleCreateSuccess = () => {
  ElMessage.success('模块创建成功')
  // 重新加载项目模块
  const projectId = route.params.id
  if (projectId) {
    moduleStore.fetchProjectModules(parseInt(projectId))
  }
}

const handleModuleUpdateSuccess = () => {
  ElMessage.success('模块进度更新成功')
  // 重新加载项目详情和模块数据
  loadProjectDetail()
  const projectId = route.params.id
  if (projectId) {
    moduleStore.fetchProjectModules(parseInt(projectId))
  }
}

const goBack = () => {
  router.push('/projects')
}

const showCreateModuleDialog = () => {
  createModuleDialogVisible.value = true
}

const showUpdateModuleProgress = (module) => {
  selectedModule.value = module
  updateModuleProgressDialogVisible.value = true
}


const showEditModule = (module) => {
  selectedModule.value = module
  editModuleDialogVisible.value = true
}

const canEditModule = (module) => {
  return authStore.hasProjectPermission(project.value, 'edit_project')
}

const handleModuleEditSuccess = () => {
  // 刷新模块数据
  moduleStore.fetchProjectModules(parseInt(route.params.id))
  ElMessage.success('模块编辑成功')
}

// 更新项目进度相关
const canUpdateProgress = computed(() => {
  // 只有前期阶段才显示更新进度按钮
  const earlyStatuses = [
    'initial_contact',
    'proposal_submitted',
    'quotation_submitted',
    'user_confirmation',
    'contract_signed'
  ]
  return project.value && earlyStatuses.includes(project.value.status)
})

const showUpdateProgressDialog = () => {
  updateProgressDialogVisible.value = true
}

const handleProgressUpdateSuccess = () => {
  // 刷新项目数据
  projectStore.fetchProjectDetail(parseInt(route.params.id))
  ElMessage.success('项目进度更新成功')
}

const loadProjectDetail = async () => {
  const projectId = route.params.id
  if (!projectId) {
    goBack()
    return
  }

  try {
    // 同时加载项目详情和模块列表
    await Promise.all([
      projectStore.fetchProjectDetail(parseInt(projectId)),
      moduleStore.fetchProjectModules(parseInt(projectId))
    ])
  } catch (error) {
    ElMessage.error('加载项目详情失败')
  }
}

// 生命周期
onMounted(() => {
  loadProjectDetail()
})
</script>

<style scoped lang="scss">
.project-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.project-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.project-header {
  padding: 32px;
}

.header-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.header-left {
  flex: 1;
}

.project-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  line-height: 1.2;
}

.project-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}


// 项目类型信息
.project-source-info {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 12px;
  
  .info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .info-label {
      font-size: 14px;
      color: var(--text-secondary);
      font-weight: 500;
    }
    
    .info-value {
      font-size: 14px;
      color: var(--text-primary);
      font-weight: 600;
    }
  }
}

// 项目类型标签
.source-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  
  &.source-horizontal {
    background: #4B7BF5; // 与 Dashboard 横向项目卡片一致
    color: white;
  }
  
  &.source-vertical {
    background: #F59D52; // 与 Dashboard 纵向项目卡片一致
    color: white;
  }
  
  &.source-self_developed {
    background: #5FD068; // 与 Dashboard 自研项目卡片一致
    color: white;
  }
}

// 项目状态标签 - 使用与Dashboard卡片一致的颜色
.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  
  // 初步接触 - 浅灰色
  &.initial_contact {
    background: rgba(142, 142, 147, 0.15);
    color: #8E8E93;
  }
  
  // 提交方案 - 天蓝色
  &.proposal_submitted {
    background: rgba(90, 200, 250, 0.15);
    color: #5AC8FA;
  }
  
  // 提交报价 - 蓝色
  &.quotation_submitted {
    background: rgba(0, 122, 255, 0.15);
    color: #007AFF;
  }
  
  // 用户确认 - 紫色
  &.user_confirmation {
    background: rgba(175, 82, 222, 0.15);
    color: #AF52DE;
  }
  
  // 合同签订 - 橙色
  &.contract_signed {
    background: rgba(255, 149, 0, 0.15);
    color: #FF9500;
  }
  
  // 项目实施 - 绿色
  &.project_implementation {
    background: rgba(52, 199, 89, 0.15);
    color: #34C759;
  }
  
  // 项目验收 - 深绿色
  &.project_acceptance {
    background: rgba(50, 215, 75, 0.15);
    color: #32D74B;
  }
  
  // 维保期内 - 黄色
  &.warranty_period {
    background: rgba(255, 214, 10, 0.15);
    color: #FFD60A;
  }
  
  // 维保期外 - 棕色
  &.post_warranty {
    background: rgba(162, 132, 94, 0.15);
    color: #A2845E;
  }
  
  // 不再跟进 - 红色
  &.no_follow_up {
    background: rgba(255, 59, 48, 0.15);
    color: #FF3B30;
  }
}

.header-right {
  display: flex;
  gap: 12px;
}

.progress-section {
  padding: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.progress-display {
  display: flex;
  align-items: center;
  gap: 40px;
}

.progress-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    var(--apple-blue) 0deg,
    var(--apple-blue) calc(var(--progress, 0) * 3.6deg),
    var(--apple-gray-light) calc(var(--progress, 0) * 3.6deg),
    var(--apple-gray-light) 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  
  &::before {
    content: '';
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--bg-primary);
    position: absolute;
  }
}

.progress-text {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  position: relative;
  z-index: 1;
}

.progress-info {
  flex: 1;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: var(--apple-gray-light);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 16px;
  
  .progress-fill {
    height: 100%;
    background: var(--apple-blue);
    border-radius: 6px;
    transition: width 0.3s ease;
    
    &.success {
      background: var(--apple-green);
    }
    
    &.warning {
      background: var(--apple-orange);
    }
  }
}

.progress-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  span {
    color: var(--text-secondary);
    font-size: 14px;
  }
}

.project-duration-wrapper {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  
  .project-duration {
    color: var(--apple-blue);
    font-weight: 600;
    font-size: 16px;
    display: block;
  }
}

.modules-section {
  padding: 24px;
  margin-bottom: 24px;
}

.empty-modules {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: var(--apple-gray);
  margin-bottom: 16px;
}

.modules-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.module-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--border-radius-small);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
  }
}

.module-header {
  margin-bottom: 12px;
}

.module-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.module-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
  flex: 1;
}

.module-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.module-description {
  margin-bottom: 16px;
  
  p {
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0;
    font-size: 14px;
  }
}

.module-progress {
  margin-bottom: 16px;
}

.module-info {
  margin-bottom: 16px;
  
  .info-row {
    display: flex;
    align-items: flex-start;
    margin-bottom: 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    &.members-row {
      align-items: flex-start;
    }
  }
  
  .info-label {
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    min-width: 80px;
    flex-shrink: 0;
  }
  
  .info-value {
    color: var(--text-primary);
    font-size: 14px;
  }
  
  .members-list-inline {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    flex: 1;
  }
  
  .member-tag {
    padding: 2px 10px;
    background: rgba(0, 122, 255, 0.1);
    color: var(--apple-blue);
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
  }
  
  .no-members {
    color: var(--text-secondary);
    font-size: 14px;
    font-style: italic;
  }
}

.module-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 7px;
  border-top: 1px solid var(--border-color);
}

.module-actions .el-button {
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.module-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.module-actions .el-button--primary.is-plain {
  color: #409eff;
  border-color: #409eff;
  background-color: #ecf5ff;
}

.module-actions .el-button--primary.is-plain:hover {
  color: #ffffff;
  background-color: #409eff;
  border-color: #409eff;
}

.module-actions .el-button--info.is-plain {
  color: #909399;
  border-color: #909399;
  background-color: #f4f4f5;
}

.module-actions .el-button--info.is-plain:hover {
  color: #ffffff;
  background-color: #909399;
  border-color: #909399;
}

.members-section {
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.empty-members {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  
  p {
    margin: 8px 0;
    font-size: 14px;
  }
  
  .empty-tip {
    font-size: 13px;
    color: var(--text-tertiary);
  }
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.member-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--border-radius-small);
  display: flex;
  align-items: center;
  gap: 16px;
}

.member-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--apple-blue);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
}

.member-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.member-position {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}


.member-role {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
  
  &.leader {
    background: rgba(0, 122, 255, 0.1);
    color: var(--apple-blue);
  }
  
  &.member {
    background: rgba(142, 142, 147, 0.1);
    color: var(--apple-gray);
  }
}


.loading-state {
  padding: 40px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.error-icon {
  font-size: 64px;
  color: var(--apple-orange);
  margin-bottom: 20px;
}

// 响应式设计
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }
  
  .header-right {
    justify-content: center;
  }
  
  .progress-display {
    flex-direction: column;
    align-items: center;
    gap: 24px;
  }
  
  .members-grid {
    grid-template-columns: 1fr;
  }
}
</style>
