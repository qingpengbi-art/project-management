<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`工作历史 - ${props.projectName} / ${props.module?.name}`"
    width="800px"
    :before-close="handleClose"
  >
    <div class="history-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="workRecords.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <p>暂无工作记录</p>
      </div>
      
      <!-- 工作记录列表 -->
      <div v-else class="work-records">
        <div 
          v-for="(record, index) in workRecords" 
          :key="record.id"
          class="record-item"
          :class="{ 'latest': index === 0 }"
        >
          <!-- 记录头部 -->
          <div class="record-header">
            <div class="record-info">
              <div class="week-info">
                <el-tag :type="index === 0 ? 'success' : 'info'" size="small">
                  {{ record.week_label }}
                </el-tag>
                <span v-if="index === 0" class="latest-badge">最新</span>
              </div>
              <div class="record-meta">
                <span class="author">{{ record.created_by?.name }}</span>
                <span class="date">{{ formatDateTime(record.updated_at) }}</span>
              </div>
            </div>
            <!-- 部门主管操作按钮 -->
            <div v-if="isDepartmentManager" class="record-actions">
              <el-button 
                size="small" 
                type="primary" 
                plain
                @click="handleEdit(record)"
                class="action-btn"
              >
                编辑
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                plain
                @click="handleDelete(record)"
                class="action-btn"
              >
                删除
              </el-button>
            </div>
          </div>
          
          <!-- 记录内容 -->
          <div class="record-content">
            <!-- 工作内容 -->
            <div class="content-section">
              <div class="section-title">
                <el-icon><Edit /></el-icon>
                <span>工作内容</span>
              </div>
              <div class="section-content">
                {{ record.work_content }}
              </div>
            </div>
            
            <!-- 本周成果 -->
            <div v-if="record.achievements" class="content-section">
              <div class="section-title">
                <el-icon><Trophy /></el-icon>
                <span>本周成果</span>
              </div>
              <div class="section-content">
                {{ record.achievements }}
              </div>
            </div>
            
            <!-- 遇到的问题 -->
            <div v-if="record.issues" class="content-section">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>遇到的问题</span>
              </div>
              <div class="section-content">
                {{ record.issues }}
              </div>
            </div>
            
            <!-- 下周计划 -->
            <div v-if="record.next_week_plan" class="content-section">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>下周计划</span>
              </div>
              <div class="section-content">
                {{ record.next_week_plan }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载更多按钮 -->
      <div v-if="!loading && workRecords.length > 0 && hasMore" class="load-more">
        <el-button @click="loadMoreRecords" :loading="loadingMore">
          加载更多
        </el-button>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
  
  <!-- 编辑工作记录对话框 -->
  <EditWorkRecordDialog
    v-model:visible="editDialogVisible"
    :record="editingRecord"
    @success="handleEditSuccess"
  />
</template>

<script setup>
import { ref, reactive, watch, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  DocumentCopy, 
  Edit, 
  Trophy, 
  Warning, 
  Calendar,
  Delete
} from '@element-plus/icons-vue'
import { moduleApi } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import EditWorkRecordDialog from './EditWorkRecordDialog.vue'

const authStore = useAuthStore()

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

const emit = defineEmits(['update:visible', 'recordUpdated'])

// 响应式数据
const dialogVisible = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const workRecords = ref([])
const hasMore = ref(true)
const currentLimit = ref(10)
const editDialogVisible = ref(false)
const editingRecord = ref(null)

// 计算属性 - 判断是否为部门主管
const isDepartmentManager = computed(() => {
  return authStore.user?.role === 'department_manager'
})

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.module) {
    loadWorkRecords()
  }
})

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
    resetData()
  }
})

// 重置数据
const resetData = () => {
  workRecords.value = []
  hasMore.value = true
  currentLimit.value = 10
}

// 加载工作记录
const loadWorkRecords = async (isLoadMore = false) => {
  if (!props.module?.id) return
  
  try {
    if (isLoadMore) {
      loadingMore.value = true
    } else {
      loading.value = true
      resetData()
    }
    
    const response = await moduleApi.getModuleWorkRecords(
      props.module.id, 
      isLoadMore ? currentLimit.value + 10 : currentLimit.value
    )
    
    if (response.success) {
      const records = response.data || []
      
      if (isLoadMore) {
        // 检查是否有新记录
        if (records.length <= workRecords.value.length) {
          hasMore.value = false
          ElMessage.info('没有更多记录了')
        } else {
          workRecords.value = records
          currentLimit.value += 10
        }
      } else {
        workRecords.value = records
        hasMore.value = records.length >= currentLimit.value
      }
    } else {
      ElMessage.error(response.message || '获取工作记录失败')
    }
  } catch (error) {
    console.error('获取工作记录失败:', error)
    ElMessage.error('获取工作记录失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载更多记录
const loadMoreRecords = () => {
  loadWorkRecords(true)
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateStr
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}

// 编辑工作记录
const handleEdit = (record) => {
  editingRecord.value = record
  editDialogVisible.value = true
}

// 删除工作记录
const handleDelete = async (record) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条工作记录吗？（${record.week_label}）`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 执行删除
    const response = await moduleApi.deleteWorkRecord(record.id)
    if (response.success) {
      ElMessage.success('工作记录删除成功')
      // 重新加载记录
      await loadWorkRecords()
      // 通知父组件刷新
      emit('recordUpdated')
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工作记录失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 处理编辑成功
const handleEditSuccess = async () => {
  editDialogVisible.value = false
  ElMessage.success('工作记录更新成功')
  // 重新加载记录
  await loadWorkRecords()
  // 通知父组件刷新
  emit('recordUpdated')
}
</script>

<style scoped>
.history-content {
  max-height: 600px;
  overflow-y: auto;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.empty-state .empty-icon {
  font-size: 48px;
  color: var(--el-text-color-placeholder);
  margin-bottom: 16px;
}

.work-records {
  padding: 0;
}

.record-item {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.record-item:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.record-item.latest {
  border-color: var(--el-color-success);
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f7fa 100%);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--el-bg-color-page);
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.record-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 按钮样式优化 - 参考Dashboard的按钮样式 */
.action-btn {
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Primary按钮 - 编辑 */
.action-btn.el-button--primary.is-plain {
  color: #409eff;
  border-color: #409eff;
  background-color: #ecf5ff;
}

.action-btn.el-button--primary.is-plain:hover {
  color: #ffffff;
  background-color: #409eff;
  border-color: #409eff;
}

/* Danger按钮 - 删除 */
.action-btn.el-button--danger.is-plain {
  color: #f56c6c;
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.action-btn.el-button--danger.is-plain:hover {
  color: #ffffff;
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.record-item.latest .record-header {
  background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
}

.record-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.week-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.latest-badge {
  background: var(--el-color-success);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.record-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.author {
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.record-content {
  padding: 16px;
}

.content-section {
  margin-bottom: 16px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  font-size: 14px;
}

.section-title .el-icon {
  font-size: 16px;
}

.section-content {
  background: var(--el-fill-color-lighter);
  padding: 12px;
  border-radius: 6px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  white-space: pre-wrap;
  word-break: break-word;
}

.load-more {
  text-align: center;
  padding: 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

/* 滚动条样式 */
.history-content::-webkit-scrollbar {
  width: 6px;
}

.history-content::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.history-content::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.history-content::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-dark);
}
</style>
