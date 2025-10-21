<template>
  <div class="projects-page">
    <!-- 筛选和搜索栏 -->
    <div class="filter-section apple-card">
      <div class="filter-row">
        <div class="filter-group">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索项目名称或描述"
            style="width: 300px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <!-- 项目类型筛选 -->
          <el-select
            v-model="sourceFilter"
            placeholder="项目类型"
            style="width: 130px"
            clearable
            @change="handleSourceChange"
          >
            <el-option label="全部类型" value="" />
            <el-option label="横向" value="horizontal" />
            <el-option label="纵向" value="vertical" />
            <el-option label="自研" value="self_developed" />
          </el-select>
          
          <!-- 项目状态筛选 - 根据项目类型动态显示 -->
          <el-select
            v-model="statusFilter"
            placeholder="项目状态"
            style="width: 150px"
            clearable
            @change="handleFilter"
          >
            <el-option label="全部状态" value="" />
            <!-- 横向和纵向项目的状态 -->
            <template v-if="!sourceFilter || sourceFilter === 'horizontal' || sourceFilter === 'vertical'">
              <el-option label="初步接触" value="initial_contact" />
              <el-option label="提交方案" value="proposal_submitted" />
              <el-option label="提交报价" value="quotation_submitted" />
              <el-option label="用户确认" value="user_confirmation" />
              <el-option label="合同签订" value="contract_signed" />
              <el-option label="项目实施" value="project_implementation" />
              <el-option label="项目验收" value="project_acceptance" />
              <el-option label="维保期内" value="warranty_period" />
              <el-option label="维保期外" value="post_warranty" />
              <el-option label="不再跟进" value="no_follow_up" />
            </template>
            <!-- 自研项目的状态 -->
            <template v-else-if="sourceFilter === 'self_developed'">
              <el-option label="进行中" value="project_implementation" />
              <el-option label="已完成" value="project_acceptance" />
            </template>
          </el-select>
          
          <el-select
            v-if="authStore.hasPermission('view_users')"
            v-model="userFilter"
            placeholder="参与人员"
            style="width: 200px"
            clearable
            filterable
            @change="handleFilter"
          >
            <el-option label="全部人员" value="" />
            <el-option
              v-for="user in userStore.users"
              :key="user.id"
              :label="user.name"
              :value="user.id"
            />
          </el-select>
        </div>
        
        <div class="action-group">
          <el-button 
            v-if="authStore.hasPermission('create_project')"
            type="primary" 
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
          
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </div>

    <!-- 项目列表 -->
    <div class="projects-container">
      <div v-loading="projectStore.loading" class="projects-grid">
        <div
          v-for="project in filteredProjects"
          :key="project.id"
          class="project-card apple-card"
          @click="goToProject(project.id)"
        >
          <!-- 项目头部 -->
          <div class="project-header">
            <div class="project-title">
              <h3 class="project-name">{{ project.name }}</h3>
              <div class="project-meta">
                <!-- 项目类型标签 -->
                <span class="source-tag" :class="`source-${project.project_source || 'horizontal'}`">
                  {{ getSourceText(project.project_source) }}
                </span>
                <span class="status-badge" :class="project.status">
                  {{ projectStore.getStatusText(project.status) }}
                </span>
                <div class="priority-indicator" :class="`priority-${project.priority}`"></div>
              </div>
            </div>
          </div>

          <!-- 项目描述 -->
          <div class="project-description">
            <p>{{ project.description || '暂无描述' }}</p>
          </div>

          <!-- 项目进度 -->
          <div class="project-progress">
            <div class="progress-header">
              <span class="progress-label">进度</span>
            </div>
            <div class="progress-circular">
              <el-progress 
                type="circle" 
                :percentage="project.progress || 0"
                :width="70"
                :stroke-width="6"
                :color="getProgressColor(project.progress)"
                :show-text="true"
              >
                <template #default="{ percentage }">
                  <span class="progress-text">{{ percentage }}%</span>
                </template>
              </el-progress>
            </div>
          </div>

          <!-- 项目信息 -->
          <div class="project-info">
            <div class="info-row">
              <span class="info-label">负责人:</span>
              <span class="info-value">{{ project.leaders?.map(leader => leader.name).join(', ') || '未分配' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">项目类型:</span>
              <span class="info-value">{{ getSourceText(project.project_source) }}</span>
            </div>
            <div class="info-row" v-if="project.project_source === 'horizontal' && project.partner">
              <span class="info-label">合作方:</span>
              <span class="info-value">{{ project.partner }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">成员数:</span>
              <span class="info-value">{{ project.member_count || 0 }}人</span>
            </div>
            <div class="info-row">
              <span class="info-label">更新时间:</span>
              <span class="info-value">{{ formatDate(project.updated_at) }}</span>
            </div>
          </div>

          <!-- 项目操作 -->
          <div class="project-actions">
            <el-button
              v-if="canEditProject(project)"
              size="small"
              plain
              @click.stop="showEditProject(project)"
            >
              编辑项目
            </el-button>
            <el-button
              v-if="canDeleteProject()"
              size="small"
              plain
              @click.stop="handleDeleteProject(project)"
            >
              删除项目
            </el-button>
            <el-button
              size="small"
              plain
              @click.stop="goToProject(project.id)"
            >
              查看详情
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!projectStore.loading && filteredProjects.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><FolderOpened /></el-icon>
        </div>
        <div class="empty-text">
          <h3>暂无项目</h3>
          <p>{{ hasFilters ? '没有符合条件的项目' : '开始创建您的第一个项目吧' }}</p>
        </div>
        <el-button v-if="!hasFilters" type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建项目
        </el-button>
      </div>
    </div>

    <!-- 创建项目对话框 -->
    <CreateProjectDialog 
      v-model="createDialogVisible"
      @success="handleCreateSuccess"
    />

    <!-- 编辑项目对话框 -->
    <EditProjectDialog 
      v-model:visible="editDialogVisible"
      :project="selectedProject"
      @success="handleEditSuccess"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  Plus, 
  Refresh,
  FolderOpened
} from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'
import { useAuthStore } from '@/stores/auth'
import { projectApi } from '@/utils/api'
import CreateProjectDialog from '@/components/CreateProjectDialog.vue'
import EditProjectDialog from '@/components/EditProjectDialog.vue'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()
const userStore = useUserStore()
const authStore = useAuthStore()

// 响应式数据
const searchKeyword = ref('')
const sourceFilter = ref('') // 项目类型筛选
const statusFilter = ref('')
const userFilter = ref('')
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const selectedProject = ref(null)

// 计算属性
const filteredProjects = computed(() => {
  let projects = [...projectStore.projects]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    projects = projects.filter(project => 
      project.name.toLowerCase().includes(keyword) ||
      (project.description && project.description.toLowerCase().includes(keyword))
    )
  }
  
  // 项目类型过滤
  if (sourceFilter.value) {
    projects = projects.filter(project => 
      (project.project_source || 'horizontal') === sourceFilter.value
    )
  }
  
  // 状态过滤
  if (statusFilter.value) {
    projects = projects.filter(project => project.status === statusFilter.value)
  }
  
  // 用户过滤
  if (userFilter.value) {
    projects = projects.filter(project => {
      if (!project.members || project.members.length === 0) {
        return false
      }
      
      const targetUserId = parseInt(userFilter.value)
      return project.members.some(member => member.id === targetUserId)
    })
  }
  
  return projects
})

const hasFilters = computed(() => 
  searchKeyword.value || sourceFilter.value || statusFilter.value || userFilter.value
)

// 权限检查方法
const canEditProject = (project) => {
  return authStore.hasProjectPermission(project, 'edit_project')
}

// 检查是否可以删除项目（只有部门主管）
const canDeleteProject = () => {
  return authStore.hasPermission('manage_all_projects')
}

// 方法
const getSourceText = (source) => {
  const sourceMap = {
    'horizontal': '横向',
    'vertical': '纵向',
    'self_developed': '自研'
  }
  return sourceMap[source] || '横向'
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

const handleSearch = () => {
  // 搜索是实时的，通过计算属性自动更新
}

const handleFilter = () => {
  // 过滤是实时的，通过计算属性自动更新
}

// 项目类型切换处理
const handleSourceChange = () => {
  // 当项目类型改变时，如果当前选中的状态不适用于新的项目类型，清空状态筛选
  if (sourceFilter.value === 'self_developed') {
    // 自研项目只有进行中和已完成两个状态
    if (statusFilter.value !== 'project_implementation' && 
        statusFilter.value !== 'project_acceptance' &&
        statusFilter.value !== '') {
      statusFilter.value = ''
    }
  }
  // 横向和纵向的状态相同，不需要特殊处理
}

const showCreateDialog = () => {
  createDialogVisible.value = true
}

const showEditProject = (project) => {
  selectedProject.value = project
  editDialogVisible.value = true
}


const goToProject = (id) => {
  router.push(`/projects/${id}`)
}

const getProgressColor = (progress) => {
  if (!progress || progress === 0) {
    return '#e4e7ed'
  } else if (progress < 30) {
    return '#f56c6c'
  } else if (progress < 70) {
    return '#e6a23c'
  } else if (progress < 100) {
    return '#409eff'
  } else {
    return '#67c23a'
  }
}

const handleCreateSuccess = () => {
  ElMessage.success('项目创建成功')
  refreshData()
}

const handleUpdateSuccess = () => {
  ElMessage.success('进度更新成功')
  refreshData()
}

const handleEditSuccess = () => {
  ElMessage.success('项目修改成功')
  refreshData()
}

// 删除项目
const handleDeleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？删除后将无法恢复，该项目下的所有模块和记录也会被删除。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    const response = await projectApi.deleteProject(project.id)
    
    if (response.success) {
      ElMessage.success(response.message || '项目删除成功')
      refreshData()
    } else {
      ElMessage.error(response.message || '删除项目失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除项目失败:', error)
      ElMessage.error('删除项目失败')
    }
  }
}

const refreshData = async () => {
  try {
    const promises = [projectStore.fetchProjects()]
    
    // 只有部门主管才需要获取用户列表（用于筛选功能）
    if (authStore.hasPermission('view_users')) {
      promises.push(userStore.fetchUsers())
    }
    
    await Promise.all(promises)
  } catch (error) {
    ElMessage.error('刷新数据失败')
  }
}

// 生命周期
onMounted(() => {
  // 从路由查询参数中获取筛选条件
  if (route.query.project_source) {
    sourceFilter.value = route.query.project_source
  }
  if (route.query.status) {
    statusFilter.value = route.query.status
  }
  refreshData()
})

// 监听路由变化
watch(() => route.query, (newQuery) => {
  // 监听项目类型变化
  if (newQuery.project_source !== undefined && newQuery.project_source !== sourceFilter.value) {
    sourceFilter.value = newQuery.project_source || ''
  }
  // 监听状态变化
  if (newQuery.status !== undefined && newQuery.status !== statusFilter.value) {
    statusFilter.value = newQuery.status || ''
    handleFilter()
  }
})
</script>

<style scoped lang="scss">
.projects-page {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-section {
  padding: 20px;
  margin-bottom: 24px;
}

.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.projects-container {
  min-height: 400px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

.project-card {
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  min-height: 320px;
  height: auto;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
  }
}

.project-header {
  margin-bottom: 16px;
}

.project-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.project-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
  flex: 1;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

// 项目类型标签
.source-tag {
  padding: 4px 10px;
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
  padding: 4px 10px;
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

.project-description {
  flex: 1;
  margin-bottom: 16px;
  
  p {
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.project-progress {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.progress-circular {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 12px;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.progress-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
}

.project-info {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.project-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.project-actions .el-button {
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.project-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.project-actions .el-button--primary.is-plain {
  color: #409eff;
  border-color: #409eff;
  background-color: #ecf5ff;
}

.project-actions .el-button--primary.is-plain:hover {
  color: #ffffff;
  background-color: #409eff;
  border-color: #409eff;
}

.project-actions .el-button--warning.is-plain {
  color: #e6a23c;
  border-color: #e6a23c;
  background-color: #fdf6ec;
}

.project-actions .el-button--warning.is-plain:hover {
  color: #ffffff;
  background-color: #e6a23c;
  border-color: #e6a23c;
}

.project-actions .el-button--info.is-plain {
  color: #909399;
  border-color: #909399;
  background-color: #f4f4f5;
}

.project-actions .el-button--info.is-plain:hover {
  color: #ffffff;
  background-color: #909399;
  border-color: #909399;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--apple-gray);
  margin-bottom: 20px;
}

.empty-text {
  margin-bottom: 24px;
  
  h3 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px 0;
  }
  
  p {
    color: var(--text-secondary);
    margin: 0;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-group {
    justify-content: center;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .project-card {
    height: auto;
  }
  
  .project-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .project-meta {
    align-self: flex-end;
  }
}
</style>
