<template>
  <el-dialog
    v-model="dialogVisible"
    title="项目进度详情"
    width="700px"
    :before-close="handleClose"
  >
    <div v-if="project" class="progress-dialog">
      <!-- 项目基本信息 -->
      <div class="project-info">
        <h3 class="project-name">{{ project.name }}</h3>
        <p class="project-desc">{{ project.description || '暂无描述' }}</p>
      </div>

      <!-- 总体进度 -->
      <div class="overall-progress">
        <div class="progress-header">
          <h4 class="section-title">总体进度</h4>
          <span class="progress-value">{{ project.progress }}%</span>
        </div>
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
        <div class="progress-note">
          <el-icon><InfoFilled /></el-icon>
          <span>项目进度由所有模块进度自动计算得出</span>
        </div>
      </div>

      <!-- 模块进度分布 -->
      <div class="modules-progress" v-loading="modulesLoading">
        <h4 class="section-title">模块进度分布</h4>
        <div v-if="!projectModules || projectModules.length === 0" class="empty-modules">
          <p>该项目暂无模块</p>
          <el-button size="small" type="primary" @click="goToProjectDetail">
            添加模块
          </el-button>
        </div>
        <div v-else class="modules-list">
          <div 
            v-for="module in (projectModules || [])" 
            :key="module.id"
            class="module-item"
          >
            <div class="module-header">
              <span class="module-name">{{ module?.name || '未知模块' }}</span>
              <span class="module-progress">{{ module?.progress || 0 }}%</span>
            </div>
            <div class="module-progress-bar">
              <div 
                class="progress-fill"
                :class="getProgressClass(module?.progress || 0)"
                :style="{ width: (module?.progress || 0) + '%' }"
              ></div>
            </div>
            <div class="module-meta">
              <span class="module-status" :class="module?.status">
                {{ getModuleStatusText(module?.status) }}
              </span>
              <span class="module-assignees">
                {{ module?.assigned_to?.name || '未分配' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 进度统计 -->
      <div class="progress-stats">
        <h4 class="section-title">进度统计</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ moduleStats.total }}</div>
            <div class="stat-label">总模块数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ moduleStats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ moduleStats.inProgress }}</div>
            <div class="stat-label">进行中</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ moduleStats.notStarted }}</div>
            <div class="stat-label">未开始</div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="goToProjectDetail">
          管理模块
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { InfoFilled } from '@element-plus/icons-vue'
import { useModuleStore } from '@/stores/module'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  project: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const router = useRouter()
const moduleStore = useModuleStore()

// 响应式数据
const modulesLoading = ref(false)
const projectModules = ref([])

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const moduleStats = computed(() => {
  const modules = projectModules.value || []
  return {
    total: modules.length,
    completed: modules.filter(m => m.status === 'COMPLETED').length,
    inProgress: modules.filter(m => m.status === 'IN_PROGRESS').length,
    notStarted: modules.filter(m => m.status === 'NOT_STARTED').length
  }
})

// 方法
const handleClose = () => {
  emit('update:modelValue', false)
}

const goToProjectDetail = () => {
  handleClose()
  router.push(`/projects/${props.project.id}`)
}

const getProgressClass = (progress) => {
  if (progress >= 80) return 'success'
  if (progress < 40) return 'warning'
  return ''
}

const getModuleStatusText = (status) => {
  const statusMap = {
    'NOT_STARTED': '未开始',
    'IN_PROGRESS': '进行中',
    'COMPLETED': '已完成',
    'PAUSED': '暂停'
  }
  return statusMap[status] || status
}

const fetchProjectModules = async (projectId) => {
  try {
    modulesLoading.value = true
    await moduleStore.fetchProjectModules(projectId)
    // 从 moduleStore.modules 中获取当前项目的模块
    projectModules.value = moduleStore.modules || []
  } catch (error) {
    console.error('获取项目模块失败:', error)
    projectModules.value = []
  } finally {
    modulesLoading.value = false
  }
}

// 监听对话框显示状态
watch(
  [() => props.modelValue, () => props.project],
  ([visible, project]) => {
    if (visible && project) {
      fetchProjectModules(project.id)
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.progress-dialog {
  padding: 0;
}

.project-info {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--border-radius-small);
  margin-bottom: 24px;
}

.project-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.project-desc {
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.overall-progress {
  margin-bottom: 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.progress-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--apple-blue);
}

.progress-bar {
  height: 12px;
  background-color: var(--border-color);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background-color: var(--apple-blue);
  transition: width 0.3s ease;
  
  &.success {
    background-color: var(--apple-green);
  }
  
  &.warning {
    background-color: var(--apple-orange);
  }
}

.progress-note {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.modules-progress {
  margin-bottom: 24px;
}

.empty-modules {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-item {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: var(--border-radius-small);
  border: 1px solid var(--border-color);
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.module-name {
  font-weight: 500;
  color: var(--text-primary);
}

.module-progress {
  font-weight: 600;
  color: var(--apple-blue);
}

.module-progress-bar {
  height: 8px;
  background-color: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.module-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.module-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
  
  &.NOT_STARTED {
    background-color: #f5f5f7;
    color: #8e8e93;
  }
  
  &.IN_PROGRESS {
    background-color: #e3f2fd;
    color: #1976d2;
  }
  
  &.COMPLETED {
    background-color: #e8f5e8;
    color: #2e7d32;
  }
  
  &.PAUSED {
    background-color: #fff3e0;
    color: #f57c00;
  }
}

.module-assignees {
  color: var(--text-secondary);
}

.progress-stats {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--border-radius-small);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--apple-blue);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .module-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .module-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
