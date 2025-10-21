<template>
  <div class="users-page">
    <!-- 页面头部 -->
    <div class="page-header apple-card">
      <div class="header-content">
        <div class="header-left">
          <h2 class="page-title">人员管理</h2>
          <p class="page-subtitle">管理部门成员信息和项目参与情况</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><UserFilled /></el-icon>
            添加成员
          </el-button>
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-container apple-card">
      <el-table
        v-loading="userStore.loading"
        :data="userStore.users"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="name" label="姓名" width="120">
          <template #default="{ row }">
            <div class="user-info">
              <div class="user-avatar">
                {{ row.name.charAt(0) }}
              </div>
              <span class="user-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="position" label="职位" width="150">
          <template #default="{ row }">
            <span class="position-text">{{ row.position || '未设置' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="email" label="邮箱" width="200">
          <template #default="{ row }">
            <span class="email-text">{{ row.email || '未设置' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="role" label="系统角色" width="120">
          <template #default="{ row }">
            <span class="role-badge" :class="row.role">
              {{ userStore.getRoleText(row.role) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="project_count" label="参与项目" width="100" align="center">
          <template #default="{ row }">
            <span class="project-count">{{ row.project_count || 0 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="leader_count" label="负责项目" width="100" align="center">
          <template #default="{ row }">
            <span class="leader-count">{{ row.leader_count || 0 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="加入时间" width="150">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                plain
                size="small"
                @click="viewUserDetail(row)"
              >
                查看详情
              </el-button>
              <el-button
                type="warning"
                plain
                size="small"
                @click="showEditDialog(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                plain
                size="small"
                @click="confirmDelete(row)"
                :disabled="row.project_count > 0"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="添加新成员"
      width="500px"
      :before-close="handleCloseCreate"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="createForm.name"
            placeholder="请输入姓名"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="职位" prop="position">
          <el-input
            v-model="createForm.position"
            placeholder="请输入职位"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="createForm.email"
            placeholder="请输入邮箱"
            maxlength="100"
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" placeholder="选择角色" style="width: 100%">
            <el-option label="普通成员" value="member" />
            <el-option label="部门主管" value="department_manager" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseCreate">取消</el-button>
          <el-button
            type="primary"
            :loading="createLoading"
            @click="handleCreateUser"
          >
            添加成员
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑成员信息"
      width="500px"
      :before-close="handleCloseEdit"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="editForm.name"
            placeholder="请输入姓名"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="职位" prop="position">
          <el-input
            v-model="editForm.position"
            placeholder="请输入职位"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="editForm.email"
            placeholder="请输入邮箱"
            maxlength="100"
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="选择角色" style="width: 100%">
            <el-option label="普通成员" value="member" />
            <el-option label="部门主管" value="department_manager" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseEdit">取消</el-button>
          <el-button
            type="primary"
            :loading="editLoading"
            @click="handleUpdateUser"
          >
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`${selectedUser?.name || ''} - 详细信息`"
      width="600px"
    >
      <div v-if="selectedUser" class="user-detail">
        <div class="detail-section">
          <h4 class="section-title">基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">姓名:</span>
              <span class="detail-value">{{ selectedUser.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">职位:</span>
              <span class="detail-value">{{ selectedUser.position || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">邮箱:</span>
              <span class="detail-value">{{ selectedUser.email || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">角色:</span>
              <span class="detail-value">{{ userStore.getRoleText(selectedUser.role) }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4 class="section-title">项目参与情况</h4>
          <div class="project-stats">
            <div class="stat-item">
              <div class="stat-number">{{ selectedUser.project_count || 0 }}</div>
              <div class="stat-label">参与项目</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ selectedUser.leader_count || 0 }}</div>
              <div class="stat-label">负责项目</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 响应式数据
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const createLoading = ref(false)
const editLoading = ref(false)
const selectedUser = ref(null)
const createFormRef = ref()
const editFormRef = ref()

// 创建用户表单
const createForm = ref({
  name: '',
  position: '',
  email: '',
  role: 'member'
})

// 编辑用户表单
const editForm = ref({
  id: null,
  name: '',
  position: '',
  email: '',
  role: 'member'
})

// 表单验证规则
const createRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2到50个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const editRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2到50个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const showCreateDialog = () => {
  createDialogVisible.value = true
}

const handleCloseCreate = () => {
  if (createLoading.value) return
  
  createForm.value = {
    name: '',
    position: '',
    email: '',
    role: 'member'
  }
  
  if (createFormRef.value) {
    createFormRef.value.resetFields()
  }
  
  createDialogVisible.value = false
}

const handleCreateUser = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    
    createLoading.value = true
    
    const result = await userStore.createUser(createForm.value)
    
    if (result.success) {
      // 显示用户创建成功信息和登录凭据
      const userData = result.data
      ElMessageBox.alert(
        `用户创建成功！\n\n用户名: ${userData.username}\n密码: ${userData.password}\n\n请妥善保管登录信息并告知用户。`,
        '用户创建成功',
        {
          confirmButtonText: '确定',
          type: 'success',
          showClose: false
        }
      )
      handleCloseCreate()
    }
  } catch (error) {
    console.error('添加成员失败:', error)
  } finally {
    createLoading.value = false
  }
}

const viewUserDetail = async (user) => {
  try {
    await userStore.fetchUserDetail(user.id)
    selectedUser.value = userStore.currentUser
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  }
}

const showEditDialog = (user) => {
  editForm.value = {
    id: user.id,
    name: user.name,
    position: user.position || '',
    email: user.email || '',
    role: user.role
  }
  editDialogVisible.value = true
}

const handleCloseEdit = () => {
  if (editLoading.value) return
  
  editForm.value = {
    id: null,
    name: '',
    position: '',
    email: '',
    role: 'member'
  }
  
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
  
  editDialogVisible.value = false
}

const handleUpdateUser = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    editLoading.value = true
    
    const result = await userStore.updateUser(editForm.value.id, editForm.value)
    
    if (result.success) {
      ElMessage.success('用户信息更新成功')
      handleCloseEdit()
      await loadData() // 重新加载数据
    }
  } catch (error) {
    console.error('更新用户失败:', error)
  } finally {
    editLoading.value = false
  }
}

const confirmDelete = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${user.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          instance.confirmButtonLoading = true
          handleDeleteUser(user.id)
            .then(() => {
              done()
              instance.confirmButtonLoading = false
            })
            .catch(() => {
              instance.confirmButtonLoading = false
            })
        } else {
          done()
        }
      }
    }
  ).catch(() => {
    // 用户取消删除
  })
}

const handleDeleteUser = async (userId) => {
  try {
    const result = await userStore.deleteUser(userId)
    
    if (result.success) {
      ElMessage.success('用户删除成功')
      await loadData() // 重新加载数据
    }
  } catch (error) {
    console.error('删除用户失败:', error)
    throw error
  }
}

const loadData = async () => {
  try {
    await userStore.fetchUsers()
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.users-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  padding: 24px;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-subtitle {
  color: var(--text-secondary);
  margin: 0;
}

.users-container {
  padding: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--apple-blue);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
}

.position-text, .email-text {
  color: var(--text-secondary);
}

.role-badge {
  padding: 4px 8px;
  border-radius: var(--border-radius-small);
  font-size: 12px;
  font-weight: 500;
  
  &.admin {
    background: rgba(0, 122, 255, 0.1);
    color: var(--apple-blue);
  }
  
  &.member {
    background: rgba(142, 142, 147, 0.1);
    color: var(--apple-gray);
  }
}

.project-count, .leader-count {
  font-weight: 600;
  color: var(--text-primary);
}

.date-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.user-detail {
  padding: 0;
}

.detail-section {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.project-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--apple-blue);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

// Element Plus 表格样式覆盖
:deep(.el-table) {
  border-radius: var(--border-radius-small);
  overflow: hidden;
}

:deep(.el-table th) {
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-weight: 600;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table__body tr:hover > td) {
  background: var(--apple-gray-light);
}

// 响应式设计
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .project-stats {
    justify-content: center;
    gap: 60px;
  }
}

// 操作按钮样式
.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-buttons .el-button {
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-buttons .el-button--primary.is-plain {
  color: #409eff;
  border-color: #409eff;
  background-color: #ecf5ff;
}

.action-buttons .el-button--primary.is-plain:hover {
  color: #ffffff;
  background-color: #409eff;
  border-color: #409eff;
}

.action-buttons .el-button--warning.is-plain {
  color: #e6a23c;
  border-color: #e6a23c;
  background-color: #fdf6ec;
}

.action-buttons .el-button--warning.is-plain:hover {
  color: #ffffff;
  background-color: #e6a23c;
  border-color: #e6a23c;
}

.action-buttons .el-button--danger.is-plain {
  color: #f56c6c;
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.action-buttons .el-button--danger.is-plain:hover {
  color: #ffffff;
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.action-buttons .el-button.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-buttons .el-button.is-disabled:hover {
  transform: none;
  box-shadow: none;
}
</style>
