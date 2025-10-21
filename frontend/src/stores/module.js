import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { moduleApi } from '@/utils/api'

export const useModuleStore = defineStore('module', () => {
  // 状态
  const modules = ref([])
  const currentModule = ref(null)
  const loading = ref(false)

  // 计算属性
  const modulesByProject = computed(() => {
    const grouped = {}
    modules.value.forEach(module => {
      if (!grouped[module.project_id]) {
        grouped[module.project_id] = []
      }
      grouped[module.project_id].push(module)
    })
    return grouped
  })

  const completedModules = computed(() => 
    modules.value.filter(m => m.progress === 100)
  )

  const inProgressModules = computed(() => 
    modules.value.filter(m => m.progress > 0 && m.progress < 100)
  )

  const pendingModules = computed(() => 
    modules.value.filter(m => m.progress === 0)
  )

  // 方法
  const fetchProjectModules = async (projectId) => {
    try {
      loading.value = true
      const response = await moduleApi.getProjectModules(projectId)
      if (response.success) {
        modules.value = response.data
      }
      return response
    } catch (error) {
      console.error('获取项目模块失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchModuleDetail = async (moduleId) => {
    try {
      loading.value = true
      const response = await moduleApi.getModuleDetail(moduleId)
      if (response.success) {
        currentModule.value = response.data
      }
      return response
    } catch (error) {
      console.error('获取模块详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createModule = async (projectId, moduleData) => {
    try {
      loading.value = true
      const response = await moduleApi.createModule(projectId, moduleData)
      if (response.success) {
        // 刷新项目模块列表
        await fetchProjectModules(projectId)
      }
      return response
    } catch (error) {
      console.error('创建模块失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateModuleProgress = async (moduleId, progressData) => {
    try {
      loading.value = true
      const response = await moduleApi.updateModuleProgress(moduleId, progressData)
      if (response.success) {
        // 更新本地模块数据
        const index = modules.value.findIndex(m => m.id === moduleId)
        if (index !== -1) {
          modules.value[index] = { ...modules.value[index], ...response.data }
        }
        
        // 如果当前查看的是这个模块，也更新详情
        if (currentModule.value && currentModule.value.id === moduleId) {
          currentModule.value = { ...currentModule.value, ...response.data }
        }
      }
      return response
    } catch (error) {
      console.error('更新模块进度失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const assignModule = async (moduleId, userId) => {
    try {
      loading.value = true
      const response = await moduleApi.assignModule(moduleId, userId)
      if (response.success) {
        // 更新本地模块数据
        const index = modules.value.findIndex(m => m.id === moduleId)
        if (index !== -1) {
          modules.value[index] = { ...modules.value[index], ...response.data }
        }
      }
      return response
    } catch (error) {
      console.error('分配模块失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateModuleAssignee = async (moduleId, userId) => {
    try {
      loading.value = true
      const response = await moduleApi.updateModuleAssignee(moduleId, userId)
      if (response.success) {
        // 更新本地模块数据
        const index = modules.value.findIndex(m => m.id === moduleId)
        if (index !== -1) {
          modules.value[index] = { ...modules.value[index], ...response.data }
        }
      }
      return response
    } catch (error) {
      console.error('更新模块负责人失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getModuleMembers = async (moduleId) => {
    try {
      loading.value = true
      const response = await moduleApi.getModuleMembers(moduleId)
      return response
    } catch (error) {
      console.error('获取模块成员失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const addModuleMember = async (moduleId, userId, role = 'member') => {
    try {
      loading.value = true
      const response = await moduleApi.addModuleMember(moduleId, userId, role)
      return response
    } catch (error) {
      console.error('添加模块成员失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const removeModuleMember = async (assignmentId) => {
    try {
      loading.value = true
      const response = await moduleApi.removeModuleMember(assignmentId)
      return response
    } catch (error) {
      console.error('移除模块成员失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteModule = async (moduleId) => {
    try {
      loading.value = true
      const response = await moduleApi.deleteModule(moduleId)
      if (response.success) {
        // 从本地状态中移除已删除的模块
        const index = modules.value.findIndex(m => m.id === moduleId)
        if (index > -1) {
          modules.value.splice(index, 1)
        }
      }
      return response
    } catch (error) {
      console.error('删除模块失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchUserModules = async (userId) => {
    try {
      loading.value = true
      const response = await moduleApi.getUserModules(userId)
      if (response.success) {
        modules.value = response.data
      }
      return response
    } catch (error) {
      console.error('获取用户模块失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getModuleById = (id) => {
    return modules.value.find(m => m.id === parseInt(id))
  }

  const getStatusText = (status) => {
    if (!status) return '未知状态'
    const statusMap = {
      'planning': '计划中',
      'in_progress': '进行中',
      'completed': '已完成',
      'paused': '暂停',
      'cancelled': '已取消'
    }
    return statusMap[status] || status
  }

  const getStatusColor = (status) => {
    if (!status) return '#8e8e93'
    const colorMap = {
      'planning': '#8e8e93',
      'in_progress': '#007aff',
      'completed': '#34c759',
      'paused': '#ff9500',
      'cancelled': '#ff3b30'
    }
    return colorMap[status] || '#8e8e93'
  }

  const getPriorityText = (priority) => {
    if (priority === null || priority === undefined) return '未设置'
    const priorityMap = {
      1: '低',
      2: '中低',
      3: '中',
      4: '中高',
      5: '高'
    }
    return priorityMap[priority] || '未知'
  }

  return {
    // 状态
    modules,
    currentModule,
    loading,
    
    // 计算属性
    modulesByProject,
    completedModules,
    inProgressModules,
    pendingModules,
    
    // 方法
    fetchProjectModules,
    fetchModuleDetail,
    createModule,
    updateModuleProgress,
    assignModule,
    updateModuleAssignee,
    getModuleMembers,
    addModuleMember,
    removeModuleMember,
    deleteModule,
    fetchUserModules,
    getModuleById,
    getStatusText,
    getStatusColor,
    getPriorityText
  }
})
