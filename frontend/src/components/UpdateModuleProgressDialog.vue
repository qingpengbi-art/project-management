<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`更新模块进度 - ${module?.name || ''}`"
    width="600px"
    :before-close="handleClose"
  >
    <div class="update-form">
      <!-- 模块信息 -->
      <div class="module-info">
        <div class="info-row">
          <span class="label">所属项目:</span>
          <span class="value">{{ module?.project?.name || projectName }}</span>
        </div>
        <div class="info-row">
          <span class="label">当前负责人:</span>
          <div class="assignees">
            <span
              v-if="module?.assigned_to"
              class="assignee-tag"
            >
              {{ module.assigned_to.name }}
            </span>
            <span v-else class="no-assignee">
              未分配
            </span>
          </div>
        </div>
        <div class="info-row">
          <span class="label">当前进度:</span>
          <span class="value">{{ module?.progress || 0 }}%</span>
        </div>
      </div>

      <!-- 进度更新表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
      >
        <!-- 新进度 -->
        <el-form-item label="新进度" prop="progress">
          <div class="progress-input">
            <el-slider
              v-model="form.progress"
              :min="0"
              :max="100"
              :step="5"
              show-input
              :show-input-controls="false"
            />
          </div>
        </el-form-item>

        <!-- 工作周期 -->
        <el-form-item label="工作周期" prop="workPeriod">
          <el-radio-group v-model="form.workPeriod">
            <el-radio value="current">本周 ({{ currentWeekLabel }})</el-radio>
            <el-radio value="custom">自定义</el-radio>
          </el-radio-group>
          <div v-if="form.workPeriod === 'custom'" class="custom-period">
            <el-date-picker
              v-model="customDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleCustomDateRangeChange"
              :clearable="false"
            />
          </div>
        </el-form-item>

        <!-- 工作内容（可选） -->
        <el-form-item label="工作内容" prop="workContent">
          <el-input
            v-model="form.workContent"
            type="textarea"
            :rows="3"
            placeholder="请描述本周具体完成的工作内容（可选）..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 工作成果（可选） -->
        <el-form-item label="工作成果" prop="achievements">
          <el-input
            v-model="form.achievements"
            type="textarea"
            :rows="2"
            placeholder="请描述取得的成果和收获（可选）..."
            maxlength="300"
            show-word-limit
          />
        </el-form-item>

        <!-- 遇到的问题（可选） -->
        <el-form-item label="遇到问题" prop="issues">
          <el-input
            v-model="form.issues"
            type="textarea"
            :rows="2"
            placeholder="请描述遇到的问题和困难（可选）..."
            maxlength="300"
            show-word-limit
          />
        </el-form-item>

        <!-- 下周计划（可选） -->
        <el-form-item label="下周计划" prop="nextWeekPlan">
          <el-input
            v-model="form.nextWeekPlan"
            type="textarea"
            :rows="2"
            placeholder="请描述下周的工作计划（可选）..."
            maxlength="300"
            show-word-limit
          />
        </el-form-item>

        <!-- 更新说明（可选） -->
        <el-form-item label="更新说明" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="2"
            placeholder="请简要说明本次进度更新的原因（可选）..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确认更新
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { moduleApi } from '@/utils/api'
import { useUserStore } from '@/stores/user'
import { useAuthStore } from '@/stores/auth'

const userStore = useUserStore()
const authStore = useAuthStore()

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  module: {
    type: Object,
    default: null
  },
  projectName: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const dialogVisible = ref(false)
const formRef = ref()
const submitting = ref(false)
const currentWeekData = ref(null)
const customDateRange = ref([])

// 表单数据
const form = reactive({
  progress: 0,
  workPeriod: 'current',
  workContent: '',
  achievements: '',
  issues: '',
  nextWeekPlan: '',
  notes: ''
})

// 表单验证规则
const rules = {
  progress: [
    { required: true, message: '请设置进度', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '进度必须在0-100之间', trigger: 'blur' }
  ]
  // 所有文本字段改为非必填：workContent、achievements、nextWeekPlan、notes
}

// 计算属性
const currentWeekLabel = computed(() => {
  if (!currentWeekData.value) return ''
  return currentWeekData.value.week_label
})

// 监听器
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    initDialog()
  }
})

watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
  }
})

// 方法
const initDialog = async () => {
  // 重置表单
  resetForm()
  
  // 设置当前进度
  if (props.module) {
    form.progress = props.module.progress || 0
  }
  
  // 获取当前周信息
  try {
    const response = await moduleApi.getCurrentWeek()
    if (response.success) {
      currentWeekData.value = response.data
    }
  } catch (error) {
    console.error('获取当前周信息失败:', error)
  }
}

const resetForm = () => {
  Object.assign(form, {
    progress: 0,
    workPeriod: 'current',
    workContent: '',
    achievements: '',
    issues: '',
    nextWeekPlan: '',
    notes: ''
  })
  customDateRange.value = []
  
  // 清除表单验证
  nextTick(() => {
    if (formRef.value) {
      formRef.value.clearValidate()
    }
  })
}

const handleCustomDateRangeChange = (value) => {
  // 处理自定义日期范围的逻辑
  if (value && value.length === 2) {
    form.weekStart = value[0]
    form.weekEnd = value[1]
    console.log('Custom date range selected:', value)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  // 表单验证
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  if (!props.module) {
    ElMessage.error('模块信息不存在')
    return
  }
  
  try {
    submitting.value = true
    
    // 获取当前用户ID
    const currentUserId = authStore.user?.id
    if (!currentUserId) {
      ElMessage.error('用户未登录')
      submitting.value = false
      return
    }
    
    // 准备工作记录数据
    let weekStart, weekEnd
    
    if (form.workPeriod === 'custom' && customDateRange.value && customDateRange.value.length === 2) {
      // 使用自定义日期范围
      weekStart = customDateRange.value[0]
      weekEnd = customDateRange.value[1]
    } else {
      // 使用当前周
      weekStart = currentWeekData.value?.week_start || new Date().toISOString().split('T')[0]
      weekEnd = currentWeekData.value?.week_end || new Date().toISOString().split('T')[0]
    }
    
    const workRecordData = {
      week_start: weekStart,
      week_end: weekEnd,
      work_content: form.workContent,
      achievements: form.achievements,
      issues: form.issues || null,
      next_week_plan: form.nextWeekPlan,
      created_by_id: currentUserId
    }
    
    // 准备进度更新数据
    const progressData = {
      progress: form.progress,
      notes: form.notes,
      updated_by_id: currentUserId
    }
    
    // 同时更新进度和添加工作记录
    const [progressResult, workResult] = await Promise.all([
      moduleApi.updateModuleProgress(props.module.id, progressData),
      moduleApi.addWorkRecord(props.module.id, workRecordData)
    ])
    
    if (progressResult.success && workResult.success) {
      ElMessage.success('模块进度和工作记录更新成功')
      emit('success')
      handleClose()
    } else {
      const errorMsg = !progressResult.success ? progressResult.message : workResult.message
      ElMessage.error(errorMsg || '更新失败')
    }
    
  } catch (error) {
    console.error('更新模块进度失败:', error)
    ElMessage.error('更新失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}
</script>

<style scoped lang="scss">
.update-form {
  max-height: 70vh;
  overflow-y: auto;
}

.module-info {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: var(--border-radius-small);
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.label {
  font-weight: 500;
  color: var(--text-secondary);
  width: 80px;
  flex-shrink: 0;
}

.value {
  color: var(--text-primary);
  font-weight: 500;
}

.assignees {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.assignee-tag {
  background: rgba(0, 122, 255, 0.1);
  color: var(--apple-blue);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.no-assignee {
  color: var(--text-secondary);
  font-size: 12px;
  font-style: italic;
}

.progress-input {
  width: 100%;
}

.custom-period {
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// Element Plus 样式覆盖
:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

:deep(.el-slider) {
  margin-right: 16px;
}

:deep(.el-textarea__inner) {
  resize: none;
}
</style>
