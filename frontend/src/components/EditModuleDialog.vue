<template>
  <el-dialog
    v-model="visible"
    title="编辑模块"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
    class="edit-module-dialog"
  >
    <div v-if="module" class="edit-module-form">
      <!-- 模块基本信息编辑 -->
      <div class="module-info-section">
        <h4 class="section-title">模块信息</h4>
        
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <!-- 模块名称 -->
          <el-form-item label="模块名称" prop="name">
            <el-input 
              v-model="form.name" 
              placeholder="请输入模块名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <!-- 模块描述 -->
          <el-form-item label="模块描述" prop="description">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入模块描述"
              maxlength="500"
              show-word-limit
            />
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
          
          <!-- 当前进度（只读显示） -->
          <el-form-item label="当前进度">
            <div class="progress-display">
              <el-progress 
                :percentage="module.progress" 
                :stroke-width="20"
                :color="getProgressColor(module.progress)"
              />
              <span class="progress-tip">💡 进度修改请使用"更新进度"功能</span>
            </div>
          </el-form-item>
          
          <!-- 开始时间 -->
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="form.start_date"
              type="date"
              placeholder="选择开始日期（非必填）"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              clearable
              style="width: 100%;"
            />
          </el-form-item>
          
          <!-- 结束时间 -->
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="form.end_date"
              type="date"
              placeholder="选择结束日期（非必填）"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              clearable
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 模块成员管理 -->
      <div class="members-section">
        <div class="members-header">
          <h4 class="section-title">模块成员</h4>
          <el-button
            type="primary"
            size="small"
            @click="showAddMember = true"
          >
            <el-icon><Plus /></el-icon>
            添加成员
          </el-button>
        </div>
        
        <!-- 当前成员列表 -->
        <div class="current-members">
          
          <div v-if="currentMembers.length > 0" class="members-list">
            <div
              v-for="member in currentMembers"
              :key="member.id"
              class="member-card"
              :class="{ 'member-deleted': member._isDeleted }"
            >
              <div class="member-avatar">
                {{ member.user.name.charAt(0) }}
              </div>
              <div class="member-info">
                <div class="member-name">{{ member.user.name }}</div>
                <div class="member-position">{{ member.user.position || '职位未设置' }}</div>
              </div>
              <div class="member-actions">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeMember(member.id)"
                  class="remove-member-btn"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
          
          <div v-else class="no-members">
            <el-empty 
              :image-size="100" 
              description="暂无团队成员"
            >
              <template #image>
                <el-icon class="empty-icon"><UserFilled /></el-icon>
              </template>
              <el-button 
                type="primary" 
                @click="showAddMember = true"
                class="empty-action-btn"
              >
                <el-icon><Plus /></el-icon>
                添加第一个成员
              </el-button>
            </el-empty>
          </div>
        </div>

        <!-- 添加成员表单 -->
        <el-collapse-transition>
          <div v-if="showAddMember" class="add-member-panel">
            <div class="panel-header">
              <span class="panel-title">添加成员</span>
              <el-button
                size="small"
                @click="showAddMember = false"
              >
                取消
              </el-button>
            </div>
            
            <div class="add-member-form">
              <el-select
                v-model="selectedNewMember"
                placeholder="搜索并选择团队成员"
                clearable
                filterable
                style="width: 100%; margin-bottom: 12px;"
              >
                <el-option
                  v-for="user in availableMembersToAdd"
                  :key="user.id"
                  :label="`${user.name} - ${user.position || '职位未设置'}`"
                  :value="user.id"
                >
                  <div class="user-option">
                    <div class="user-avatar">{{ user.name.charAt(0) }}</div>
                    <div class="user-info">
                      <div class="user-name">{{ user.name }}</div>
                      <div class="user-position">{{ user.position || '职位未设置' }}</div>
                    </div>
                  </div>
                </el-option>
              </el-select>
              
              
              <el-button
                type="primary"
                @click="addMember"
                :disabled="!selectedNewMember"
                style="width: 100%;"
              >
                确认添加
              </el-button>
            </div>
          </div>
        </el-collapse-transition>
      </div>

    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <el-button 
            type="danger" 
            @click="handleDelete"
            :loading="deleting"
          >
            <el-icon><Delete /></el-icon>
            删除模块
          </el-button>
        </div>
        <div class="footer-right">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            type="primary"
            @click="handleSave"
            :loading="saving"
            :disabled="!hasChanges"
          >
            {{ saving ? '保存中...' : '保存更改' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, UserFilled, Plus, Delete 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useModuleStore } from '@/stores/module'
import { moduleApi } from '@/utils/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  module: {
    type: Object,
    default: null
  },
  projectId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const userStore = useUserStore()
const moduleStore = useModuleStore()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref(null)
const selectedNewMember = ref(null)
const showAddMember = ref(false)
const saving = ref(false)
const deleting = ref(false)

// 表单数据
const form = reactive({
  name: '',
  description: '',
  status: '',
  start_date: null,
  end_date: null
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' },
    { min: 2, max: 100, message: '模块名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '模块描述不能超过 500 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择模块状态', trigger: 'change' }
  ]
}

// 模块成员数据
const currentMembers = ref([])

// 计算属性
const availableMembersToAdd = computed(() => {
  const existingMemberIds = currentMembers.value.map(m => m.user_id)
  
  return userStore.users.filter(user => 
    !existingMemberIds.includes(user.id)
  )
})

const hasChanges = computed(() => {
  if (!props.module) return false
  
  // 检查基本信息是否有变化
  const basicInfoChanged = 
    form.name !== props.module.name ||
    form.description !== (props.module.description || '') ||
    form.status !== props.module.status ||
    form.start_date !== (props.module.start_date || '') ||
    form.end_date !== (props.module.end_date || '')
  
  // 检查成员是否有变化
  const membersChanged = currentMembers.value.some(m => m._isNew || m._isDeleted)
  
  return basicInfoChanged || membersChanged
})

// 方法
const getModuleStatusText = (status) => {
  const statusMap = {
    'not_started': '待开始',
    'in_progress': '进行中', 
    'completed': '已完成',
    'paused': '暂停'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const statusTypeMap = {
    'not_started': '',
    'in_progress': 'warning',
    'completed': 'success',
    'paused': 'info'
  }
  return statusTypeMap[status] || ''
}

const getProgressColor = (progress) => {
  if (progress < 30) return '#f56c6c'
  if (progress < 70) return '#e6a23c'
  return '#67c23a'
}



const addMember = () => {
  if (!selectedNewMember.value) {
    return
  }
  
  const user = userStore.users.find(u => u.id === selectedNewMember.value)
  if (!user) return
  
  // 添加新成员到列表
  const newMember = {
    id: `temp_${Date.now()}`, // 临时ID
    user_id: user.id,
    user: user,
    role: 'member', // 固定为member
    _isNew: true // 标记为新添加
  }
  
  currentMembers.value.push(newMember)
  
  // 重置表单
  selectedNewMember.value = null
  showAddMember.value = false
  
  ElMessage.success('成员已添加到列表，请保存更改')
}

const removeMember = (memberId) => {
  const memberIndex = currentMembers.value.findIndex(m => m.id === memberId)
  if (memberIndex === -1) return
  
  const member = currentMembers.value[memberIndex]
  
  if (member._isNew) {
    // 如果是新添加的成员，直接从列表中移除
    currentMembers.value.splice(memberIndex, 1)
  } else {
    // 如果是已存在的成员，标记为删除
    member._isDeleted = true
  }
  
  ElMessage.success('成员已从列表中移除，请保存更改')
}

const loadModuleMembers = async () => {
  if (!props.module?.id) return
  
  try {
    const response = await moduleStore.getModuleMembers(props.module.id)
    if (response.success) {
      currentMembers.value = response.data.map(member => ({
        ...member,
        _isNew: false,
        _isDeleted: false
      }))
    }
  } catch (error) {
    console.error('加载模块成员失败:', error)
  }
}

const handleSave = async () => {
  if (!hasChanges.value) {
    ElMessage.warning('没有需要保存的更改')
    return
  }

  // 验证表单
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.error('请检查表单填写是否正确')
    return
  }

  saving.value = true

  try {
    const updates = []
    
    // 1. 更新模块基本信息
    const basicInfoChanged = 
      form.name !== props.module.name ||
      form.description !== (props.module.description || '') ||
      form.status !== props.module.status ||
      form.start_date !== (props.module.start_date || '') ||
      form.end_date !== (props.module.end_date || '')
    
    if (basicInfoChanged) {
      const updateData = {
        name: form.name,
        description: form.description,
        status: form.status,
        start_date: form.start_date || null,
        end_date: form.end_date || null
      }
      updates.push(
        moduleApi.updateModule(props.module.id, updateData)
      )
    }
    
    // 2. 处理成员更新
    const memberUpdates = []
    
    // 添加新成员
    const newMembers = currentMembers.value.filter(m => m._isNew && !m._isDeleted)
    for (const member of newMembers) {
      memberUpdates.push(
        moduleStore.addModuleMember(props.module.id, member.user_id, 'member')
      )
    }
    
    // 移除成员
    const deletedMembers = currentMembers.value.filter(m => m._isDeleted && !m._isNew)
    for (const member of deletedMembers) {
      memberUpdates.push(
        moduleStore.removeModuleMember(member.id)
      )
    }
    
    // 执行所有更新
    await Promise.all([...updates, ...memberUpdates])
    
    ElMessage.success('模块更新成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  if (!props.module?.id) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除模块"${props.module.name}"吗？\n\n删除后将无法恢复，相关的进度记录和工作记录也将被删除。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        dangerouslyUseHTMLString: true
      }
    )
    
    deleting.value = true
    
    const response = await moduleApi.deleteModule(props.module.id)
    if (response.success) {
      ElMessage.success('模块删除成功')
      emit('success')
      handleClose()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模块失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  } finally {
    deleting.value = false
  }
}

const handleClose = () => {
  // 重置所有状态
  selectedNewMember.value = null
  showAddMember.value = false
  currentMembers.value = []
  deleting.value = false
  visible.value = false
}

// 监听对话框打开
watch(() => props.modelValue, async (newVal) => {
  if (newVal && props.module) {
    // 初始化表单数据
    Object.assign(form, {
      name: props.module.name || '',
      description: props.module.description || '',
      status: props.module.status || 'not_started',
      start_date: props.module.start_date || null,
      end_date: props.module.end_date || null
    })
    
    // 确保有用户数据
    if (userStore.users.length === 0) {
      await userStore.fetchUsers()
    }
    
    // 加载模块成员数据
    await loadModuleMembers()
    
    // 清除验证
    nextTick(() => {
      formRef.value?.clearValidate()
    })
  }
})
</script>

<style scoped lang="scss">
.edit-module-form {
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .module-info-section,
  .members-section {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  // 进度显示样式
  .progress-display {
    width: 100%;
    
    .el-progress {
      margin-bottom: 8px;
    }
    
    .progress-tip {
      display: block;
      font-size: 12px;
      color: #909399;
      font-style: italic;
      margin-top: 4px;
    }
  }
  
  // 表单样式优化
  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #333;
  }
  
  :deep(.el-textarea__inner),
  :deep(.el-input__inner) {
    border-radius: 6px;
  }

  // 模块信息卡片
  .module-info-card {
    background: #f8fafc;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #e2e8f0;
    
    .module-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      
      .module-title {
        h3 {
          margin: 0 0 8px 0;
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }
        
        .module-badges {
          display: flex;
          gap: 8px;
        }
      }
    }
    
    .module-description {
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid #e2e8f0;
      
      p {
        margin: 0;
        color: #666;
        font-size: 14px;
      }
    }
  }

  // 模块成员管理
  .members-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .members-list {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .member-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: #f8fafc;
      border-radius: 8px;
      border: 1px solid #e2e8f0;

      &.member-deleted {
        opacity: 0.5;
      }

      .member-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #409eff;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 12px;
      }

      .member-info {
        flex: 1;

        .member-name {
          font-weight: 500;
          color: #333;
          margin-bottom: 2px;
        }

        .member-position {
          font-size: 12px;
          color: #666;
        }
      }
    }
  }

  // 添加成员面板
  .add-member-panel {
    margin-top: 16px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .panel-title {
        font-weight: 600;
        color: #333;
      }
    }
  }
}

.user-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;

  .user-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #409eff;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
  }

  .user-info {
    .user-name {
      font-size: 14px;
      font-weight: 500;
    }

    .user-position {
      font-size: 12px;
      color: #666;
    }
  }
}

// 彻底解决按钮颜色问题
.remove-btn,
.remove-member-btn {
  &.el-button--danger {
    background-color: #f56c6c !important;
    border-color: #f56c6c !important;
    color: #ffffff !important;
    
    &:hover,
    &:focus {
      background-color: #f78989 !important;
      border-color: #f78989 !important;
      color: #ffffff !important;
    }
    
    &:active {
      background-color: #dd6161 !important;
      border-color: #dd6161 !important;
      color: #ffffff !important;
    }
    
    // 确保图标也是白色
    .el-icon {
      color: #ffffff !important;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.footer-left {
  display: flex;
  align-items: center;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 删除按钮样式 */
.footer-left .el-button--danger {
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: #ffffff !important;
}

.footer-left .el-button--danger:hover {
  background-color: #f78989 !important;
  border-color: #f78989 !important;
  color: #ffffff !important;
}

.footer-left .el-button--danger:focus {
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: #ffffff !important;
}

.footer-left .el-button--danger .el-icon {
  color: #ffffff !important;
}
</style>
