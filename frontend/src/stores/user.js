import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref([])
  const currentUser = ref(null)
  const loading = ref(false)

  // 计算属性
  const adminUsers = computed(() => 
    users.value.filter(u => u.role === 'admin')
  )

  const memberUsers = computed(() => 
    users.value.filter(u => u.role === 'member')
  )

  const userOptions = computed(() => 
    users.value.map(u => ({
      label: u.name,
      value: u.id,
      position: u.position
    }))
  )

  // 方法
  const fetchUsers = async (filters = {}) => {
    try {
      loading.value = true
      const response = await userApi.getUsers(filters)
      if (response.success) {
        users.value = response.data
      }
      return response
    } catch (error) {
      console.error('获取用户列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchUserDetail = async (id) => {
    try {
      loading.value = true
      const response = await userApi.getUserDetail(id)
      if (response.success) {
        currentUser.value = response.data
      }
      return response
    } catch (error) {
      console.error('获取用户详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData) => {
    try {
      loading.value = true
      const response = await userApi.createUser(userData)
      if (response.success) {
        // 刷新用户列表
        await fetchUsers()
      }
      return response
    } catch (error) {
      console.error('创建用户失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (userId, userData) => {
    try {
      loading.value = true
      const response = await userApi.updateUser(userId, userData)
      if (response.success) {
        // 刷新用户列表
        await fetchUsers()
      }
      return response
    } catch (error) {
      console.error('更新用户失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteUser = async (userId) => {
    try {
      loading.value = true
      const response = await userApi.deleteUser(userId)
      if (response.success) {
        // 刷新用户列表
        await fetchUsers()
      }
      return response
    } catch (error) {
      console.error('删除用户失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const addProjectMember = async (projectId, memberData) => {
    try {
      loading.value = true
      const response = await userApi.addProjectMember(projectId, memberData)
      return response
    } catch (error) {
      console.error('添加项目成员失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const removeProjectMember = async (projectId, userId) => {
    try {
      loading.value = true
      const response = await userApi.removeProjectMember(projectId, userId)
      return response
    } catch (error) {
      console.error('移除项目成员失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateMemberRole = async (projectId, userId, role) => {
    try {
      loading.value = true
      const response = await userApi.updateMemberRole(projectId, userId, { role })
      return response
    } catch (error) {
      console.error('更新成员角色失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getUserById = (id) => {
    return users.value.find(u => u.id === parseInt(id))
  }

  const getUsersByIds = (ids) => {
    return users.value.filter(u => ids.includes(u.id))
  }

  const getRoleText = (role) => {
    const roleMap = {
      'department_manager': '部门主管',
      'member': '普通成员'
    }
    return roleMap[role] || role
  }

  const getProjectRoleText = (role) => {
    const roleMap = {
      'leader': '负责人',
      'member': '成员'
    }
    return roleMap[role] || role
  }

  return {
    // 状态
    users,
    currentUser,
    loading,
    
    // 计算属性
    adminUsers,
    memberUsers,
    userOptions,
    
    // 方法
    fetchUsers,
    fetchUserDetail,
    createUser,
    updateUser,
    deleteUser,
    addProjectMember,
    removeProjectMember,
    updateMemberRole,
    getUserById,
    getUsersByIds,
    getRoleText,
    getProjectRoleText
  }
})
