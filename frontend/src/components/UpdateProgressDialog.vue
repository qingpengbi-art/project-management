<template>
  <el-dialog
    v-model="dialogVisible"
    title="项目进度详情"
    width="600px"
    :before-close="handleClose"
  >
    <div v-if="project" class="progress-dialog">
      <div class="project-info">
        <h3 class="project-name">{{ project.name }}</h3>
        <p class="project-desc">{{ project.description }}</p>
        <div class="current-progress">
          <span class="label">当前进度:</span>
          <span class="progress-value">{{ project.progress }}%</span>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        label-position="left"
      >
        <el-form-item label="新进度" prop="progress">
          <div class="progress-input">
            <el-slider
              v-model="form.progress"
              :min="0"
              :max="100"
              :step="5"
              show-stops
              show-input
              :show-input-controls="false"
            />
          </div>
        </el-form-item>

        <el-form-item label="进度说明" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入本次进度更新的说明（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="更新人" prop="updated_by_id">
          <el-select
            v-model="form.updated_by_id"
            placeholder="选择更新人"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="member in projectMembers"
              :key="member.id"
              :label="`${member.name} (${member.position || '未知职位'})`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <div class="progress-preview">
        <div class="preview-label">进度预览:</div>
        <div class="progress-bar">
          <div 
            class="progress-fill"
            :class="{ 
              success: form.progress === 100,
              warning: form.progress < 30 
            }"
            :style="{ width: form.progress + '%' }"
          ></div>
        </div>
        <div class="progress-text">{{ form.progress }}%</div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          更新进度
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import { useUserStore } from '@/stores/user'

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

const emit = defineEmits(['update:modelValue', 'success'])

const projectStore = useProjectStore()
const userStore = useUserStore()

// 响应式数据
const formRef = ref()
const loading = ref(false)

// 表单数据
const form = ref({
  progress: 0,
  notes: '',
  updated_by_id: ''
})

// 表单验证规则
const rules = {
  progress: [
    { required: true, message: '请设置进度', trigger: 'change' },
    { type: 'number', min: 0, max: 100, message: '进度必须在0-100之间', trigger: 'change' }
  ],
  updated_by_id: [
    { required: true, message: '请选择更新人', trigger: 'change' }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const projectMembers = computed(() => {
  if (!props.project || !props.project.members) return []
  
  return props.project.members.map(member => {
    const user = userStore.users.find(u => u.id === member.user_id)
    return user || { id: member.user_id, name: '未知用户', position: '未知职位' }
  })
})

// 方法
const resetForm = () => {
  if (props.project) {
    form.value = {
      progress: props.project.progress || 0,
      notes: '',
      updated_by_id: ''
    }
  }
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleClose = () => {
  if (loading.value) return
  resetForm()
  emit('update:modelValue', false)
}

const handleSubmit = async () => {
  if (!formRef.value || !props.project) return
  
  try {
    await formRef.value.validate()
    
    // 检查进度是否有变化
    if (form.value.progress === props.project.progress) {
      ElMessage.warning('进度没有变化')
      return
    }
    
    loading.value = true
    
    const result = await projectStore.updateProjectProgress(props.project.id, form.value)
    
    if (result.success) {
      ElMessage.success('进度更新成功')
      emit('success', result.data)
      handleClose()
    }
  } catch (error) {
    console.error('更新进度失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听对话框显示状态和项目变化
watch(
  [() => props.modelValue, () => props.project],
  ([visible, project]) => {
    if (visible && project) {
      resetForm()
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
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.current-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .label {
    color: var(--text-secondary);
    font-weight: 500;
  }
  
  .progress-value {
    color: var(--apple-blue);
    font-weight: 600;
    font-size: 16px;
  }
}

.progress-input {
  width: 100%;
  
  :deep(.el-slider) {
    margin: 12px 0;
  }
}

.progress-preview {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: var(--border-radius-small);
  margin-top: 20px;
}

.preview-label {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--apple-gray-light);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
  
  .progress-fill {
    height: 100%;
    background: var(--apple-blue);
    border-radius: 4px;
    transition: width 0.3s ease;
    
    &.success {
      background: var(--apple-green);
    }
    
    &.warning {
      background: var(--apple-orange);
    }
  }
}

.progress-text {
  text-align: center;
  font-weight: 600;
  color: var(--text-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

:deep(.el-slider__runway) {
  background: var(--apple-gray-light);
}

:deep(.el-slider__bar) {
  background: var(--apple-blue);
}

:deep(.el-slider__button) {
  border: 2px solid var(--apple-blue);
}

:deep(.el-input__wrapper) {
  border-radius: var(--border-radius-small);
}

:deep(.el-textarea__inner) {
  border-radius: var(--border-radius-small);
}
</style>
