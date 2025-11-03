<template>
  <el-dialog
    v-model="dialogVisible"
    title="编辑工作记录"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="top"
    >
      <!-- 工作周期 -->
      <el-form-item label="工作周期" prop="dateRange">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :disabled-date="disabledDate"
          style="width: 100%"
        />
      </el-form-item>

      <!-- 工作内容 -->
      <el-form-item label="工作内容" prop="work_content">
        <el-input
          v-model="form.work_content"
          type="textarea"
          :rows="4"
          placeholder="请描述本周具体完成的工作内容（可选）..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <!-- 工作成果 -->
      <el-form-item label="工作成果" prop="achievements">
        <el-input
          v-model="form.achievements"
          type="textarea"
          :rows="3"
          placeholder="请描述本周取得的主要成果（可选）..."
          maxlength="300"
          show-word-limit
        />
      </el-form-item>

      <!-- 遇到的问题 -->
      <el-form-item label="遇到的问题" prop="issues">
        <el-input
          v-model="form.issues"
          type="textarea"
          :rows="3"
          placeholder="请描述遇到的问题或困难（可选）..."
          maxlength="300"
          show-word-limit
        />
      </el-form-item>

      <!-- 下周计划 -->
      <el-form-item label="下周计划" prop="next_week_plan">
        <el-input
          v-model="form.next_week_plan"
          type="textarea"
          :rows="3"
          placeholder="请描述下周的工作计划（可选）..."
          maxlength="300"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存修改
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { moduleApi } from '@/utils/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  record: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const dialogVisible = ref(false)
const formRef = ref(null)
const submitting = ref(false)

// 表单数据
const form = reactive({
  dateRange: [],
  work_content: '',
  achievements: '',
  issues: '',
  next_week_plan: ''
})

// 表单验证规则
const rules = {
  dateRange: [
    { required: true, message: '请选择工作周期', trigger: 'change' }
  ]
}

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.record) {
    // 初始化表单数据
    nextTick(() => {
      form.dateRange = [props.record.week_start, props.record.week_end]
      form.work_content = props.record.work_content || ''
      form.achievements = props.record.achievements || ''
      form.issues = props.record.issues || ''
      form.next_week_plan = props.record.next_week_plan || ''
    })
  }
})

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
    resetForm()
  }
})

// 禁用未来日期
const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  form.dateRange = []
  form.work_content = ''
  form.achievements = ''
  form.issues = ''
  form.next_week_plan = ''
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    // 准备提交数据
    const submitData = {
      week_start: form.dateRange[0],
      week_end: form.dateRange[1],
      work_content: form.work_content || null,
      achievements: form.achievements || null,
      issues: form.issues || null,
      next_week_plan: form.next_week_plan || null
    }
    
    // 调用更新API
    const response = await moduleApi.updateWorkRecord(props.record.id, submitData)
    
    if (response.success) {
      emit('success')
      dialogVisible.value = false
    } else {
      ElMessage.error(response.message || '更新失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('更新工作记录失败:', error)
      ElMessage.error('更新失败')
    }
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

