<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑项目' : '创建项目'"
    width="600px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <!-- 项目名称 -->
      <el-form-item label="项目名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入项目名称" />
      </el-form-item>
      
      <!-- 项目描述 -->
      <el-form-item label="项目描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="3" 
          placeholder="请输入项目描述" 
        />
      </el-form-item>
      
      <!-- 项目类型 -->
      <el-form-item label="项目类型" prop="project_source">
        <el-select v-model="form.project_source" placeholder="选择项目类型" style="width: 100%;" @change="handleProjectSourceChange">
          <el-option label="横向" value="horizontal" />
          <el-option label="纵向" value="vertical" />
          <el-option label="自研" value="self_developed" />
        </el-select>
      </el-form-item>
      
      <!-- 合作方（横向和纵向项目显示） -->
      <el-form-item v-if="form.project_source === 'horizontal' || form.project_source === 'vertical'" label="合作方" prop="partner">
        <el-input
          v-model="form.partner"
          placeholder="请输入合作方名称（选填）"
          maxlength="100"
          show-word-limit
        />
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
              <template #append>万元</template>
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
              <template #append>万元</template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 项目状态 - 根据项目类型动态显示 -->
      <el-form-item label="项目状态" prop="status">
        <el-select v-model="form.status" placeholder="选择项目状态" style="width: 100%;">
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
      
      <!-- 项目日期 -->
      <el-form-item label="项目时间">
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
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          {{ isEdit ? '保存修改' : '创建项目' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { projectApi, userApi } from '@/utils/api'

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
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref(null)
const availableUsers = ref([])

// 表单数据
const form = reactive({
  name: '',
  description: '',
  project_source: 'horizontal',
  partner: '',
  status: 'initial_contact',
  contract_amount: null,
  received_amount: null,
  start_date: '',
  end_date: '',
  leader: ''
})

// 日期范围
const dateRange = ref([])

// 计算属性
const isEdit = computed(() => !!props.project)

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '项目描述不能超过 500 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ],
  leader: [
    { required: true, message: '请选择项目负责人', trigger: 'change' }
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

// 项目类型切换处理
const handleProjectSourceChange = (source) => {
  // 切换项目类型时，重置状态为适合的默认值
  if (source === 'self_developed') {
    // 自研项目默认为进行中
    form.status = 'project_implementation'
    // 清空合作方（自研不需要合作方）
    form.partner = ''
  } else if (source === 'vertical') {
    // 纵向项目
    // 检查当前状态是否是纵向专用状态
    const verticalStatuses = ['vertical_declaration', 'vertical_review', 'vertical_approved', 'vertical_rejected']
    if (!verticalStatuses.includes(form.status)) {
      // 如果不是纵向状态，设置默认值
      form.status = 'vertical_declaration'
    }
    // 纵向项目可以有合作方，不清空
  } else if (source === 'horizontal') {
    // 横向项目
    // 检查当前状态是否是横向有效状态
    const horizontalStatuses = ['initial_contact', 'proposal_submitted', 'quotation_submitted', 
                               'user_confirmation', 'contract_signed', 'project_implementation',
                               'project_acceptance', 'warranty_period', 'post_warranty', 'no_follow_up']
    if (!horizontalStatuses.includes(form.status)) {
      // 如果不是横向状态，设置默认值
      form.status = 'initial_contact'
    }
    // 横向项目可以有合作方，不清空
  }
}

// 初始化对话框
const initDialog = async () => {
  await loadUsers()
  
  if (isEdit.value && props.project) {
    // 编辑模式，填充现有数据
    Object.assign(form, {
      name: props.project.name || '',
      description: props.project.description || '',
      status: props.project.status || 'initial_contact',
      project_source: props.project.project_source || 'horizontal',
      partner: props.project.partner || '',
      contract_amount: props.project.contract_amount || null,
      received_amount: props.project.received_amount || null,
      start_date: props.project.start_date || '',
      end_date: props.project.end_date || '',
      leader: ''
    })
    
    // 从项目成员中找到负责人
    if (props.project.members && props.project.members.length > 0) {
      const leader = props.project.members.find(m => m.role === 'leader')
      if (leader) {
        form.leader = leader.user_id || leader.user?.id || ''
      }
    }
    
    // 设置日期范围
    if (form.start_date && form.end_date) {
      dateRange.value = [form.start_date, form.end_date]
    }
  } else {
    // 创建模式，重置表单
    resetForm()
  }
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
    status: 'initial_contact',
    project_source: 'horizontal',
    partner: '',
    contract_amount: null,
    received_amount: null,
    start_date: '',
    end_date: '',
    leader: ''
  })
  dateRange.value = []
  
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}


// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    // 准备提交的数据
    const submitData = { ...form }
    
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
    
    let response
    if (isEdit.value) {
      response = await projectApi.updateProject(props.project.id, submitData)
    } else {
      response = await projectApi.createProject(submitData)
    }
    
    if (response.success) {
      ElMessage.success(response.message || (isEdit.value ? '项目更新成功' : '项目创建成功'))
      emit('success', response.data)
      handleClose()
    } else {
      ElMessage.error(response.message || (isEdit.value ? '项目更新失败' : '项目创建失败'))
    }
  } catch (error) {
    console.error('提交表单失败:', error)
    ElMessage.error('操作失败，请重试')
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
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
