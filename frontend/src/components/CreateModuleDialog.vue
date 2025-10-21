<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建项目模块"
    width="600px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <!-- 模块名称 -->
      <el-form-item label="模块名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入模块名称" />
      </el-form-item>
      
      <!-- 模块描述 -->
      <el-form-item label="模块描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="3" 
          placeholder="请输入模块描述" 
        />
      </el-form-item>
      
      <!-- 模块优先级 -->
      <el-form-item label="优先级" prop="priority">
        <el-select v-model="form.priority" placeholder="选择优先级" style="width: 100%;">
          <el-option label="低" :value="1" />
          <el-option label="中" :value="2" />
          <el-option label="高" :value="3" />
          <el-option label="紧急" :value="4" />
        </el-select>
      </el-form-item>
      
      <!-- 模块状态 -->
      <el-form-item label="模块状态" prop="status">
        <el-select v-model="form.status" placeholder="选择模块状态" style="width: 100%;">
          <el-option label="未开始" value="not_started" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="暂停" value="paused" />
        </el-select>
      </el-form-item>
      
      <!-- 初始进度 -->
      <el-form-item label="初始进度" prop="progress">
        <el-slider 
          v-model="form.progress" 
          show-input 
          :max="100" 
          style="margin-right: 20px;"
        />
      </el-form-item>
      
      <!-- 模块负责人 -->
      <el-form-item label="负责人">
        <div class="assignee-section">
          <div class="assignee-list">
            <div 
              v-for="(assignee, index) in form.assignees" 
              :key="index"
              class="assignee-item"
            >
              <el-select 
                v-model="assignee.user_id" 
                placeholder="选择负责人" 
                style="flex: 1; margin-right: 8px;"
                filterable
              >
                <el-option
                  v-for="user in availableUsers"
                  :key="user.id"
                  :label="`${user.name} - ${user.position}`"
                  :value="user.id"
                />
              </el-select>
              
              <el-select 
                v-model="assignee.role" 
                placeholder="角色" 
                style="width: 120px; margin-right: 8px;"
              >
                <el-option label="负责人" value="leader" />
                <el-option label="成员" value="member" />
              </el-select>
              
              <el-button 
                type="danger" 
                size="small" 
                icon="Delete"
                @click="removeAssignee(index)"
                :disabled="form.assignees.length <= 1"
              />
            </div>
          </div>
          
          <el-button 
            type="primary" 
            size="small" 
            icon="Plus"
            @click="addAssignee"
            style="margin-top: 8px;"
          >
            添加负责人
          </el-button>
        </div>
      </el-form-item>
      
      <!-- 预计开始时间 -->
      <el-form-item label="预计时间">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%;"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          创建模块
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { moduleApi, userApi } from '@/utils/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref(null)
const availableUsers = ref([])

// 表单数据
const form = reactive({
  name: '',
  description: '',
  priority: 2,
  status: 'not_started',
  progress: 0,
  start_date: '',
  end_date: '',
  assignees: [
    { user_id: '', role: 'leader' }
  ]
})

// 日期范围
const dateRange = ref([])

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' },
    { min: 2, max: 100, message: '模块名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '模块描述不能超过 500 个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择模块状态', trigger: 'change' }
  ],
  progress: [
    { type: 'number', min: 0, max: 100, message: '进度必须在 0-100 之间', trigger: 'blur' }
  ]
}

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    initDialog()
  }
})

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
  }
})

// 监听日期范围变化
watch(dateRange, (newVal) => {
  if (newVal && newVal.length === 2) {
    form.start_date = newVal[0]
    form.end_date = newVal[1]
  } else {
    form.start_date = ''
    form.end_date = ''
  }
})

// 监听状态变化，自动调整进度
watch(() => form.status, (newStatus) => {
  if (newStatus === 'completed') {
    // 选择已完成时，自动设置进度为100%
    form.progress = 100
  } else if (newStatus === 'not_started') {
    // 选择未开始时，自动设置进度为0%
    form.progress = 0
  } else if (newStatus === 'in_progress' && form.progress === 0) {
    // 选择进行中且当前进度为0时，设置为一个合理的初始值
    form.progress = 10
  }
})

// 监听进度变化，自动调整状态
watch(() => form.progress, (newProgress) => {
  if (newProgress === 0 && form.status !== 'not_started') {
    form.status = 'not_started'
  } else if (newProgress === 100 && form.status !== 'completed') {
    form.status = 'completed'
  } else if (newProgress > 0 && newProgress < 100 && form.status === 'not_started') {
    form.status = 'in_progress'
  }
})

// 初始化对话框
const initDialog = async () => {
  await loadUsers()
  resetForm()
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await userApi.getUsers()
    if (response.success) {
      availableUsers.value = response.data || []
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    name: '',
    description: '',
    priority: 2,
    status: 'not_started',
    progress: 0,
    start_date: '',
    end_date: '',
    assignees: [{ user_id: '', role: 'leader' }]
  })
  dateRange.value = []
  
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

// 添加负责人
const addAssignee = () => {
  form.assignees.push({ user_id: '', role: 'member' })
}

// 移除负责人
const removeAssignee = (index) => {
  if (form.assignees.length > 1) {
    form.assignees.splice(index, 1)
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    // 过滤掉没有选择用户的负责人
    const validAssignees = form.assignees.filter(assignee => assignee.user_id)
    
    if (validAssignees.length === 0) {
      ElMessage.warning('请至少选择一个负责人')
      loading.value = false
      return
    }
    
    const submitData = {
      name: form.name,
      description: form.description,
      priority: form.priority,
      status: form.status,
      progress: form.progress,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
      assigned_users: validAssignees.map(a => a.user_id) // 转换为用户ID数组
    }
    
    const response = await moduleApi.createModule(props.projectId, submitData)
    
    if (response.success) {
      ElMessage.success(response.message || '模块创建成功')
      
      // 如果有负责人，分配给模块
      if (validAssignees.length > 0 && response.data?.id) {
        try {
          await moduleApi.assignUsersToModule(response.data.id, validAssignees.map(a => a.user_id))
        } catch (assignError) {
          console.error('分配负责人失败:', assignError)
          // 不阻塞主流程，只是警告
          ElMessage.warning('模块创建成功，但分配负责人失败')
        }
      }
      
      emit('success', response.data)
      handleClose()
    } else {
      ElMessage.error(response.message || '模块创建失败')
    }
  } catch (error) {
    console.error('提交表单失败:', error)
    ElMessage.error('创建失败，请重试')
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}
</script>

<style scoped>
.assignee-section {
  width: 100%;
}

.assignee-list {
  max-height: 200px;
  overflow-y: auto;
}

.assignee-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.assignee-item:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
