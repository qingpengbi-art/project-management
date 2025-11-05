<template>
  <el-dialog
    v-model="dialogVisible"
    title="更新项目进度"
    width="600px"
    :before-close="handleClose"
  >
    <div v-if="project" class="progress-editor">
      <!-- 当前状态信息 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">项目名称：</span>
          <span class="value">{{ project.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">当前状态：</span>
          <el-tag :type="getStatusTagType(project.status)">
            {{ getStatusLabel(project.status) }}
          </el-tag>
        </div>
        <div class="info-row">
          <span class="label">当前进度：</span>
          <span class="value">{{ project.progress }}%</span>
        </div>
      </div>

      <!-- 进度来源说明 -->
      <div class="source-info">
        <div class="source-label">
          <el-icon><InfoFilled /></el-icon>
          <span>进度来源</span>
        </div>
        
        <!-- 如果有模块 -->
        <el-alert
          v-if="hasModules"
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            项目进度将基于模块进度自动计算
          </template>
          <div class="module-info">
            <p>模块数量：{{ moduleCount }} 个</p>
            <p>模块平均进度：{{ avgModuleProgress }}%</p>
            <p v-if="isEarlyStage">
              映射到阶段范围：{{ progressLimits.min }}% - {{ progressLimits.max }}%
            </p>
            <p class="calculated">
              <strong>计算后的项目进度：{{ calculatedProgress }}%</strong>
            </p>
          </div>
          <div class="tip">
            💡 要更改项目进度，请更新各模块的进度
          </div>
        </el-alert>
        
        <!-- 如果没有模块 -->
        <div v-else class="manual-section">
          <!-- 前期阶段可以手动设置 -->
          <div v-if="isEarlyStage">
            <el-alert
              type="warning"
              :closable="false"
              show-icon
              class="range-alert"
            >
              <template #title>
                手动设置进度
              </template>
              <p>当前阶段允许范围：{{ progressLimits.min }}% - {{ progressLimits.max }}%</p>
            </el-alert>
            
            <div class="progress-input">
              <div class="slider-container">
                <el-slider
                  v-model="manualProgress"
                  :min="progressLimits.min"
                  :max="progressLimits.max"
                  :marks="marks"
                  show-stops
                  :step="1"
                />
              </div>
              
              <div class="progress-display">
                <el-input-number
                  v-model="manualProgress"
                  :min="progressLimits.min"
                  :max="progressLimits.max"
                  :step="1"
                  controls-position="right"
                />
                <span class="unit">%</span>
              </div>
            </div>
            
            <div class="tip-box">
              <el-icon><WarnTriangleFilled /></el-icon>
              <span>进度范围受当前状态限制。如需更大范围，请先更新项目状态。</span>
            </div>
          </div>
          
          <!-- 项目实施阶段不能手动设置 -->
          <el-alert
            v-else-if="project.status === 'project_implementation'"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #title>
              项目实施阶段不支持手动设置进度
            </template>
            <p>请通过创建和更新项目模块来反映实际进度。</p>
            <p class="tip">💡 当前显示的进度为默认值，建议创建模块来准确追踪进度。</p>
          </el-alert>
          
          <!-- 其他状态 -->
          <el-alert
            v-else
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              当前状态不支持手动设置进度
            </template>
            <p>当前进度：{{ project.progress }}%</p>
          </el-alert>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="canUpdate"
          type="primary"
          @click="handleSubmit"
          :loading="loading"
        >
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, WarnTriangleFilled } from '@element-plus/icons-vue'
import { projectApi } from '@/utils/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  project: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const loading = ref(false)
const manualProgress = ref(0)

// 计算属性
const hasModules = computed(() => {
  return props.project?.modules?.length > 0
})

const moduleCount = computed(() => {
  return props.project?.modules?.length || 0
})

const avgModuleProgress = computed(() => {
  if (!hasModules.value) return 0
  const total = props.project.modules.reduce((sum, m) => sum + (m.progress || 0), 0)
  return Math.round(total / props.project.modules.length)
})

const isEarlyStage = computed(() => {
  const earlyStatuses = [
    'initial_contact',
    'proposal_submitted',
    'quotation_submitted',
    'user_confirmation',
    'contract_signed'
  ]
  return earlyStatuses.includes(props.project?.status)
})

const progressLimits = computed(() => {
  const status = props.project?.status
  return getProgressLimitsByStatus(status)
})

const calculatedProgress = computed(() => {
  if (!hasModules.value) return manualProgress.value
  
  const limits = progressLimits.value
  
  // 前期阶段：映射到范围
  if (isEarlyStage.value) {
    const rangeSize = limits.max - limits.min
    return Math.round(limits.min + (avgModuleProgress.value / 100 * rangeSize))
  }
  
  // 项目实施：35% + 模块平均 × 65%
  if (props.project?.status === 'project_implementation') {
    return Math.round(35 + (avgModuleProgress.value * 0.65))
  }
  
  return props.project?.progress || 0
})

const marks = computed(() => {
  const limits = progressLimits.value
  return {
    [limits.min]: {
      style: { color: '#909399' },
      label: `${limits.min}%`
    },
    [limits.max]: {
      style: { color: '#909399' },
      label: `${limits.max}%`
    }
  }
})

const canUpdate = computed(() => {
  // 只有前期阶段且没有模块时才能手动更新
  return isEarlyStage.value && !hasModules.value
})

// 方法
function getProgressLimitsByStatus(status) {
  const LIMITS = {
    'initial_contact': { min: 0, max: 5, default: 5 },
    'proposal_submitted': { min: 5, max: 15, default: 15 },
    'quotation_submitted': { min: 15, max: 20, default: 20 },
    'user_confirmation': { min: 20, max: 25, default: 25 },
    'contract_signed': { min: 25, max: 35, default: 35 }
  }
  return LIMITS[status] || { min: 0, max: 100, default: 0 }
}

function getStatusLabel(status) {
  const labels = {
    'initial_contact': '初步接触',
    'proposal_submitted': '提交方案',
    'quotation_submitted': '提交报价',
    'user_confirmation': '用户确认',
    'contract_signed': '合同签订',
    'project_implementation': '项目实施',
    'project_acceptance': '项目验收',
    'warranty_period': '维保期内',
    'post_warranty': '维保期外',
    'no_follow_up': '不再跟进'
  }
  return labels[status] || status
}

function getStatusTagType(status) {
  const types = {
    'initial_contact': 'info',
    'proposal_submitted': 'warning',
    'quotation_submitted': 'warning',
    'user_confirmation': 'warning',
    'contract_signed': 'success',
    'project_implementation': 'primary',
    'project_acceptance': 'success',
    'warranty_period': 'success',
    'post_warranty': 'info',
    'no_follow_up': 'danger'
  }
  return types[status] || ''
}

async function handleSubmit() {
  if (!canUpdate.value) {
    ElMessage.warning('当前状态不支持手动更新进度')
    return
  }
  
  try {
    loading.value = true
    
    const response = await projectApi.updateManualProgress(
      props.project.id,
      manualProgress.value
    )
    
    if (response.success) {
      ElMessage.success(response.message || '进度更新成功')
      emit('success')
      handleClose()
    } else {
      ElMessage.error(response.message || '进度更新失败')
    }
  } catch (error) {
    console.error('更新进度失败:', error)
    ElMessage.error(error.response?.data?.message || '进度更新失败')
  } finally {
    loading.value = false
  }
}

function handleClose() {
  dialogVisible.value = false
}

// 监听对话框打开
watch(() => props.visible, (newVal) => {
  if (newVal && props.project) {
    // 初始化手动进度值
    manualProgress.value = props.project.manual_progress || 
                          props.project.progress || 
                          progressLimits.value.default
  }
})
</script>

<style scoped>
.progress-editor {
  padding: 10px 0;
}

.info-section {
  margin-bottom: 24px;
  padding: 16px;
  background-color: var(--bg-secondary, #f5f7fa);
  border-radius: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-size: 14px;
  color: var(--text-secondary, #606266);
  min-width: 80px;
}

.info-row .value {
  font-size: 14px;
  color: var(--text-primary, #303133);
  font-weight: 500;
}

.source-info {
  margin-bottom: 24px;
}

.source-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #303133);
}

.module-info {
  margin-top: 12px;
  padding-left: 8px;
}

.module-info p {
  margin: 8px 0;
  font-size: 14px;
  color: var(--text-regular, #606266);
}

.module-info .calculated {
  margin-top: 12px;
  padding: 8px;
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 4px;
  color: var(--el-color-primary);
}

.tip {
  margin-top: 12px;
  padding: 8px;
  background-color: rgba(230, 162, 60, 0.1);
  border-radius: 4px;
  font-size: 13px;
  color: #e6a23c;
}

.manual-section {
  margin-top: 16px;
}

.range-alert {
  margin-bottom: 20px;
}

.progress-input {
  margin: 24px 0;
}

.slider-container {
  padding: 0 12px;
  margin-bottom: 24px;
}

.progress-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.progress-display .unit {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #303133);
}

.tip-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background-color: #fff7e6;
  border-left: 3px solid #e6a23c;
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-regular, #606266);
  margin-top: 16px;
}

.tip-box .el-icon {
  color: #e6a23c;
  margin-top: 2px;
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-alert__title) {
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-alert__description) {
  font-size: 13px;
  margin-top: 8px;
}

:deep(.el-slider__marks-text) {
  font-size: 12px;
}

:deep(.el-input-number) {
  width: 120px;
}
</style>
