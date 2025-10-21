import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)

  // 计算属性
  const userRole = computed(() => user.value?.role || null)
  const userName = computed(() => user.value?.name || '')
  const isManager = computed(() => user.value?.role === 'department_manager')
  const isProjectLeader = computed(() => false) // 项目负责人现在是项目级角色，不是系统角色
  const isMember = computed(() => user.value?.role === 'member')

  // 权限检查
  const hasPermission = (permission) => {
    if (!user.value || !user.value.role) return false
    
    // 部门主管拥有所有权限
    if (user.value.role === 'department_manager') return true
    
    // 权限映射
    const permissions = {
      // 项目权限
      'view_all_projects': ['department_manager'],
      'create_project': ['department_manager'],
      'edit_all_projects': ['department_manager'],
      'delete_project': ['department_manager'],
      'view_own_projects': ['department_manager', 'member'],
      'edit_own_projects': ['department_manager', 'member'],
      
      // 模块权限
      'update_all_modules': ['department_manager'],
      'update_project_modules': ['department_manager', 'member'],
      'update_own_modules': ['department_manager', 'member'],
      'view_all_modules': ['department_manager', 'member'],
      
      // 用户管理权限
      'manage_users': ['department_manager'],
      'view_users': ['department_manager'],
      
      // 系统权限
      'access_dashboard': ['department_manager', 'member'],
      'access_user_management': ['department_manager'],
    }
    
    const allowedRoles = permissions[permission] || []
    return allowedRoles.includes(user.value.role)
  }

  // 检查用户在特定项目中的权限
  const hasProjectPermission = (project, permission) => {
    if (!user.value || !project) {
      return false
    }

    // 部门主管拥有所有权限
    if (user.value.role === 'department_manager') {
      return true
    }

    // 检查用户是否是项目成员
    const isMember = project.members?.some(member => member.user_id === user.value.id)
    if (!isMember) {
      return false
    }

    // 检查用户在项目中的角色
    const memberInfo = project.members.find(member => member.user_id === user.value.id)
    const projectRole = memberInfo?.role

    if (permission === 'edit_project') {
      // 只有项目负责人可以编辑项目
      return projectRole === 'leader'
    } else if (permission === 'view_project') {
      // 所有项目成员都可以查看项目
      return true
    }

    return false
  }

  // 检查用户是否可以更新特定模块
  const canUpdateModule = (module, project) => {
    if (!user.value || !module) {
      return false
    }

    // 部门主管拥有所有权限
    if (user.value.role === 'department_manager') {
      return true
    }

    // 检查用户是否是项目成员
    if (!project?.members?.some(member => member.user_id === user.value.id)) {
      return false
    }

    // 检查用户在项目中的角色
    const memberInfo = project.members.find(member => member.user_id === user.value.id)
    const projectRole = memberInfo?.role

    // 项目负责人可以更新所有模块
    if (projectRole === 'leader') {
      return true
    }

    // 普通成员只能更新分配给自己的模块
    return module.assigned_to?.id === user.value.id
  }

  // 方法
  const login = async (username, password) => {
    try {
      loading.value = true
      
      const response = await api.post('/auth/login', {
        username,
        password
      })
      
      if (response.success) {
        user.value = response.data.user
        isAuthenticated.value = true
        
        // 保存到localStorage
        localStorage.setItem('user', JSON.stringify(user.value))
        localStorage.setItem('isAuthenticated', 'true')
        
        return true
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error) {
      console.error('登录失败:', error)
      if (error.response?.data?.message) {
        throw new Error(error.response.data.message)
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 无论请求是否成功都清除本地状态
      user.value = null
      isAuthenticated.value = false
      
      // 清除localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
      localStorage.removeItem('rememberLogin')
    }
  }

  const checkAuth = async () => {
    try {
      loading.value = true
      
      const response = await api.get('/auth/check')
      
      if (response.success && response.authenticated) {
        user.value = response.data.user
        isAuthenticated.value = true
        return true
      } else {
        // 清除本地状态
        user.value = null
        isAuthenticated.value = false
        localStorage.removeItem('user')
        localStorage.removeItem('isAuthenticated')
        return false
      }
    } catch (error) {
      console.error('验证登录状态失败:', error)
      // 清除本地状态
      user.value = null
      isAuthenticated.value = false
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
      return false
    } finally {
      loading.value = false
    }
  }

  const initAuth = () => {
    // 从localStorage恢复登录状态
    const savedUser = localStorage.getItem('user')
    const savedAuth = localStorage.getItem('isAuthenticated')
    
    if (savedUser && savedAuth === 'true') {
      try {
        user.value = JSON.parse(savedUser)
        isAuthenticated.value = true
      } catch (error) {
        console.error('恢复用户状态失败:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('isAuthenticated')
      }
    }
  }

  const updateProfile = (userData) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  return {
    // 状态
    user,
    isAuthenticated,
    loading,
    
    // 计算属性
    userRole,
    userName,
    isManager,
    isProjectLeader,
    isMember,
    
    // 方法
    hasPermission,
    hasProjectPermission,
    canUpdateModule,
    login,
    logout,
    checkAuth,
    initAuth,
    updateProfile
  }
})
