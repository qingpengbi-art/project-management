<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建新项目"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="left"
    >
      <el-form-item label="项目名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入项目名称"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="项目描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入项目描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="开始日期" prop="start_date">
            <el-date-picker
              v-model="form.start_date"
              type="date"
              placeholder="选择开始日期"
              style="width: 100%"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="预计完成" prop="end_date">
            <el-date-picker
              v-model="form.end_date"
              type="date"
              placeholder="选择预计完成日期"
              style="width: 100%"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="项目类型" prop="project_source">
        <el-select v-model="form.project_source" placeholder="选择项目类型" style="width: 100%" @change="handleProjectSourceChange">
          <el-option label="横向" value="horizontal" />
          <el-option label="纵向" value="vertical" />
          <el-option label="自研" value="self_developed" />
        </el-select>
      </el-form-item>

      <!-- 金额字段 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="合同金额(万元)" prop="contract_amount">
            <el-input
              v-model.number="form.contract_amount"
              type="number"
              placeholder="请输入合同金额（选填）"
              :min="0"
              :step="0.01"
            >
              <template #prepend>¥</template>
            </el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="到账金额(万元)" prop="received_amount">
            <el-input
              v-model.number="form.received_amount"
              type="number"
              placeholder="请输入到账金额（选填）"
              :min="0"
              :step="0.01"
            >
              <template #prepend>¥</template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 合作方（横向和纵向项目显示） -->
      <el-form-item v-if="form.project_source === 'horizontal' || form.project_source === 'vertical'" label="合作方" prop="partner">
        <el-input
          v-model="form.partner"
          placeholder="请输入合作方名称（选填）"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <!-- 项目状态 - 根据项目类型动态显示 -->
      <el-form-item label="项目状态" prop="status">
        <el-select v-model="form.status" placeholder="选择项目状态" style="width: 100%">
          <!-- 横向项目的状态 -->
          <template v-if="form.project_source === 'horizontal'">
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
          <!-- 纵向项目专用状态 -->
          <template v-else-if="form.project_source === 'vertical'">
            <el-option label="申报阶段" value="vertical_declaration" />
            <el-option label="审核阶段" value="vertical_review" />
            <el-option label="审核通过" value="vertical_approved" />
            <el-option label="审核未通过" value="vertical_rejected" />
          </template>
          <!-- 自研项目的状态 -->
          <template v-else-if="form.project_source === 'self_developed'">
            <el-option label="进行中" value="project_implementation" />
            <el-option label="已完成" value="project_acceptance" />
          </template>
        </el-select>
      </el-form-item>

      <!-- 项目负责人 -->
      <el-form-item label="项目负责人" prop="leader" required>
        <el-select
          v-model="form.leader"
          placeholder="请选择项目负责人"
          style="width: 100%"
          filterable
        >
          <el-option
            v-for="user in availableUsers"
            :key="user.id"
            :label="`${user.name} (${user.position})`"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          创建项目
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
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'initial_contact',
  project_source: 'horizontal', // 默认横向
  partner: '', // 合作方
  contract_amount: null, // 合同金额
  received_amount: null, // 到账金额
  leader: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 200, message: '项目名称长度在2到200个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '项目描述不能超过500个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ],
  project_source: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  partner: [
    { max: 100, message: '合作方名称不能超过100个字符', trigger: 'blur' }
  ],
  leader: [
    { required: true, message: '请选择项目负责人', trigger: 'change' }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const availableUsers = computed(() => {
  return userStore.users
})

// 方法

// 项目类型切换处理
const handleProjectSourceChange = (source) => {
  // 切换项目类型时，重置状态为适合的默认值
  if (source === 'self_developed') {
    // 自研项目默认为进行中
    form.value.status = 'project_implementation'
    // 清空合作方（自研项目不需要合作方）
    form.value.partner = ''
  } else if (source === 'vertical') {
    // 纵向项目默认为申报阶段
    form.value.status = 'vertical_declaration'
    // 纵向项目可以有合作方，不清空
  } else {
    // 横向项目默认为初步接触
    form.value.status = 'initial_contact'
    // 横向项目可以有合作方，不清空
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 'initial_contact',
    project_source: 'horizontal',
    partner: '',
    contract_amount: null,
    received_amount: null,
    leader: ''
  }
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleClose = () => {
  if (loading.value) return
  resetForm()
  emit('update:modelValue', false)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    // 准备提交的数据
    const submitData = { ...form.value }
    
    // 添加项目负责人到成员列表
    const leaderUser = availableUsers.value.find(u => u.id === submitData.leader)
    if (leaderUser) {
      submitData.members = [{
        user_id: submitData.leader,
        name: leaderUser.name,
        position: leaderUser.position,
        role: 'leader'
      }]
    } else {
      submitData.members = []
    }
    
    const result = await projectStore.createProject(submitData)
    
    if (result.success) {
      ElMessage.success('项目创建成功')
      emit('success', result.data)
      handleClose()
    }
  } catch (error) {
    console.error('创建项目失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听对话框显示状态
watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      resetForm()
    }
  }
)
</script>

<style scoped lang="scss">
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

:deep(.el-input__wrapper) {
  border-radius: var(--border-radius-small);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: var(--border-radius-small);
}

:deep(.el-textarea__inner) {
  border-radius: var(--border-radius-small);
}
</style>
