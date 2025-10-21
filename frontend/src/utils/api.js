import axios from 'axios'
import { ElMessage } from 'element-plus'

// 动态获取API基础URL
const getBaseURL = () => {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    console.log('开发环境使用代理: /api')
    return '/api'
  }
  
  // 生产环境：动态检测当前访问地址并设置对应的API地址
  const currentHost = window.location.hostname
  const currentPort = window.location.port
  
  console.log('当前访问地址:', currentHost, '端口:', currentPort)
  
  // 构建API URL：使用当前主机的5001端口
  const apiUrl = `http://${currentHost}:5001/api`
  console.log('API地址:', apiUrl)
  
  return apiUrl
}

// 创建axios实例
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  withCredentials: true, // 支持会话Cookie
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 在请求发送之前做一些处理
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { data } = response
    
    // 如果返回的状态码为200，说明接口请求成功
    if (response.status === 200 || response.status === 201) {
      return data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  error => {
    console.error('响应错误:', error)
    
    let message = '网络错误'
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message = data.message || '请求参数错误'
          break
        case 401:
          message = data.message || '未授权，请重新登录'
          // 处理认证失效，重定向到登录页
          if (window.location.pathname !== '/login') {
            import('@/stores/auth').then(({ useAuthStore }) => {
              const authStore = useAuthStore()
              authStore.logout()
              window.location.href = '/login'
            })
          }
          break
        case 403:
          message = data.message || '权限不足，无法执行此操作'
          // 显示友好的权限提示
          import('element-plus').then(({ ElMessageBox }) => {
            ElMessageBox.alert(
              '您没有执行此操作的权限。如需帮助，请联系系统管理员。',
              '权限不足',
              {
                confirmButtonText: '我知道了',
                type: 'warning',
                showClose: false
              }
            )
          })
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API方法封装
export const projectApi = {
  // 获取项目列表
  getProjects(params = {}) {
    return api.get('/projects', { params })
  },
  
  // 获取项目详情
  getProjectDetail(id) {
    return api.get(`/projects/${id}`)
  },
  
  // 创建项目
  createProject(data) {
    return api.post('/projects', data)
  },
  
  // 更新项目
  updateProject(id, data) {
    return api.put(`/projects/${id}`, data)
  },
  
  // 删除项目
  deleteProject(id) {
    return api.delete(`/projects/${id}`)
  },
  
  // 更新项目进度
  updateProgress(id, data) {
    return api.put(`/projects/${id}/progress`, data)
  },
  
  // 获取部门总览
  getDepartmentOverview() {
    return api.get('/projects/overview')
  }
}

export const moduleApi = {
  // 获取项目模块列表
  getProjectModules(projectId) {
    return api.get(`/modules/projects/${projectId}`)
  },
  
  // 获取模块详情
  getModuleDetail(moduleId) {
    return api.get(`/modules/${moduleId}`)
  },
  
  // 创建模块
  createModule(projectId, data) {
    return api.post(`/modules/projects/${projectId}`, data)
  },
  
  // 更新模块进度
  updateModuleProgress(moduleId, data) {
    return api.put(`/modules/${moduleId}/progress`, data)
  },
  
  // 分配模块给用户
  assignModule(moduleId, userId) {
    return api.put(`/modules/${moduleId}/assign`, { user_id: userId })
  },

  // 更新模块负责人（支持移除）
  updateModuleAssignee(moduleId, userId) {
    return api.put(`/modules/${moduleId}/assignee`, { 
      assigned_to_id: userId // null表示移除负责人
    })
  },

  // 获取模块成员列表
  getModuleMembers(moduleId) {
    return api.get(`/modules/${moduleId}/members`)
  },

  // 添加模块成员
  addModuleMember(moduleId, userId, role = 'member') {
    return api.post(`/modules/${moduleId}/members`, {
      user_id: userId,
      role: role
    })
  },

  // 移除模块成员
  removeModuleMember(assignmentId) {
    return api.delete(`/modules/members/${assignmentId}`)
  },
  
  // 获取用户负责的模块
  getUserModules(userId) {
    return api.get(`/modules/users/${userId}`)
  },
  
  // 获取所有项目的模块概览
  getModulesOverview() {
    return api.get('/modules/overview')
  },
  
  // 添加模块工作记录
  addWorkRecord(moduleId, data) {
    return api.post(`/modules/${moduleId}/work-records`, data)
  },
  
  // 获取模块工作记录
  getModuleWorkRecords(moduleId, limit = 10) {
    return api.get(`/modules/${moduleId}/work-records`, { params: { limit } })
  },
  
  // 获取模块最新工作内容
  getLatestWorkContent(moduleId) {
    return api.get(`/modules/${moduleId}/latest-work`)
  },
  
  // 为模块分配多个用户
  assignUsersToModule(moduleId, userIds) {
    return api.put(`/modules/${moduleId}/assign-users`, { user_ids: userIds })
  },
  
  // 获取当前周日期
  getCurrentWeek() {
    return api.get('/modules/current-week')
  },
  
  // 删除模块
  deleteModule(moduleId) {
    return api.delete(`/modules/${moduleId}`)
  }
}

export const userApi = {
  // 获取用户列表
  getUsers(params = {}) {
    return api.get('/users', { params })
  },
  
  // 获取用户详情
  getUserDetail(id) {
    return api.get(`/users/${id}`)
  },
  
  // 创建用户
  createUser(data) {
    return api.post('/users', data)
  },
  
  // 更新用户
  updateUser(id, data) {
    return api.put(`/users/${id}`, data)
  },
  
  // 删除用户
  deleteUser(id) {
    return api.delete(`/users/${id}`)
  },
  
  // 添加项目成员
  addProjectMember(projectId, data) {
    return api.post(`/users/projects/${projectId}/members`, data)
  },
  
  // 移除项目成员
  removeProjectMember(projectId, userId) {
    return api.delete(`/users/projects/${projectId}/members/${userId}`)
  },
  
  // 更新成员角色
  updateMemberRole(projectId, userId, data) {
    return api.put(`/users/projects/${projectId}/members/${userId}/role`, data)
  }
}

export default api
