import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi } from '@/utils/api'

export const useProjectStore = defineStore('project', () => {
  // 按业务流程顺序排列的状态列表
  const orderedStatusList = [
    'initial_contact',      // 初步接触
    'proposal_submitted',   // 提交方案
    'quotation_submitted',  // 提交报价
    'user_confirmation',    // 用户确认
    'contract_signed',      // 合同签订
    'project_implementation', // 项目实施
    'project_acceptance',   // 项目验收
    'warranty_period',      // 维保期内
    'post_warranty',        // 维保期外
    'no_follow_up'          // 不再跟进
  ]

  // 状态
  const projects = ref([])
  const currentProject = ref(null)
  const loading = ref(false)
  const overview = ref({
    summary: {
      total_projects: 0,
      active_projects: 0,
      avg_progress: 0,
      status_distribution: {}
    },
    projects: [],
    user_stats: []
  })

  // 计算属性
  const activeProjects = computed(() => 
    projects.value.filter(p => p.status === 'project_implementation')
  )

  const completedProjects = computed(() => 
    projects.value.filter(p => ['project_acceptance', 'warranty_period', 'post_warranty'].includes(p.status))
  )

  const projectsByStatus = computed(() => {
    const grouped = {}
    projects.value.forEach(project => {
      if (!grouped[project.status]) {
        grouped[project.status] = []
      }
      grouped[project.status].push(project)
    })
    return grouped
  })

  // 方法
  const fetchProjects = async (filters = {}) => {
    try {
      loading.value = true
      const response = await projectApi.getProjects(filters)
      if (response.success) {
        // 按照业务流程顺序对项目进行排序
        const sortedProjects = response.data.sort((a, b) => {
          const aIndex = orderedStatusList.indexOf(a.status)
          const bIndex = orderedStatusList.indexOf(b.status)
          
          // 如果状态不在有序列表中，放到最后
          if (aIndex === -1 && bIndex === -1) return 0
          if (aIndex === -1) return 1
          if (bIndex === -1) return -1
          
          return aIndex - bIndex
        })
        
        projects.value = sortedProjects
      }
      return response
    } catch (error) {
      console.error('获取项目列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchProjectDetail = async (id) => {
    try {
      loading.value = true
      const response = await projectApi.getProjectDetail(id)
      if (response.success) {
        currentProject.value = response.data
      }
      return response
    } catch (error) {
      console.error('获取项目详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createProject = async (projectData) => {
    try {
      loading.value = true
      const response = await projectApi.createProject(projectData)
      if (response.success) {
        // 刷新项目列表
        await fetchProjects()
      }
      return response
    } catch (error) {
      console.error('创建项目失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateProjectProgress = async (id, progressData) => {
    try {
      loading.value = true
      const response = await projectApi.updateProgress(id, progressData)
      if (response.success) {
        // 更新本地项目数据
        const index = projects.value.findIndex(p => p.id === id)
        if (index !== -1) {
          projects.value[index] = { ...projects.value[index], ...response.data }
        }
        
        // 如果当前查看的是这个项目，也更新详情
        if (currentProject.value && currentProject.value.id === id) {
          currentProject.value = { ...currentProject.value, ...response.data }
        }
      }
      return response
    } catch (error) {
      console.error('更新项目进度失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchDepartmentOverview = async () => {
    try {
      loading.value = true
      const response = await projectApi.getDepartmentOverview()
      
      if (response.success) {
        // 对overview中的projects也进行排序
        const sortedOverview = {
          ...response.data,
          projects: response.data.projects.sort((a, b) => {
            const aIndex = orderedStatusList.indexOf(a.status)
            const bIndex = orderedStatusList.indexOf(b.status)
            
            // 如果状态不在有序列表中，放到最后
            if (aIndex === -1 && bIndex === -1) return 0
            if (aIndex === -1) return 1
            if (bIndex === -1) return -1
            
            return aIndex - bIndex
          })
        }
        
        overview.value = sortedOverview
      }
      return response
    } catch (error) {
      console.error('获取部门总览失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getProjectById = (id) => {
    return projects.value.find(p => p.id === parseInt(id))
  }

  const getStatusText = (status) => {
    const statusMap = {
      // 横向项目状态
      'initial_contact': '初步接触',
      'proposal_submitted': '提交方案',
      'quotation_submitted': '提交报价',
      'user_confirmation': '用户确认',
      'contract_signed': '合同签订',
      'project_implementation': '项目实施',
      'project_acceptance': '项目验收',
      'warranty_period': '维保期内',
      'post_warranty': '维保期外',
      'no_follow_up': '不再跟进',
      // 纵向项目专用状态
      'vertical_declaration': '申报阶段',
      'vertical_review': '审核阶段',
      'vertical_approved': '审核通过',
      'vertical_rejected': '审核未通过'
    }
    return statusMap[status] || status
  }

  const getStatusColor = (status) => {
    const colorMap = {
      // 横向项目状态颜色
      'initial_contact': '#8E8E93',        // 浅灰色 - 初步接触
      'proposal_submitted': '#5AC8FA',     // 天蓝色 - 提交方案
      'quotation_submitted': '#007AFF',    // 蓝色 - 提交报价
      'user_confirmation': '#AF52DE',      // 紫色 - 用户确认
      'contract_signed': '#FF9500',        // 橙色 - 合同签订
      'project_implementation': '#34C759', // 绿色 - 项目实施
      'project_acceptance': '#32D74B',     // 深绿色 - 项目验收
      'warranty_period': '#FFD60A',        // 黄色 - 维保期内
      'post_warranty': '#A2845E',          // 棕色 - 维保期外
      'no_follow_up': '#FF3B30',           // 红色 - 不再跟进
      // 纵向项目状态颜色
      'vertical_declaration': '#5AC8FA',   // 天蓝色 - 申报阶段
      'vertical_review': '#FF9500',        // 橙色 - 审核阶段
      'vertical_approved': '#34C759',      // 绿色 - 审核通过
      'vertical_rejected': '#FF3B30'       // 红色 - 审核未通过
    }
    return colorMap[status] || '#8e8e93'
  }

  const getPriorityText = (priority) => {
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
    // 常量
    orderedStatusList,
    
    // 状态
    projects,
    currentProject,
    loading,
    overview,
    
    // 计算属性
    activeProjects,
    completedProjects,
    projectsByStatus,
    
    // 方法
    fetchProjects,
    fetchProjectDetail,
    createProject,
    updateProjectProgress,
    fetchDepartmentOverview,
    getProjectById,
    getStatusText,
    getStatusColor,
    getPriorityText
  }
})
